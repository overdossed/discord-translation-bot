import discord
from discord.ext import commands
import asyncio
import os
from config import TOKEN, GUILD_ID, CHANNEL_ID
from game_manager import GameManager

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)
game_manager = GameManager()

@bot.event
async def on_ready():
    print(f'🤖 {bot.user} se ha conectado a Discord!')
    print(f'📊 Servidores conectados: {len(bot.guilds)}')
    
    for guild in bot.guilds:
        print(f'🏠 Servidor: {guild.name} (ID: {guild.id})')
        print(f'   👥 Miembros: {guild.member_count}')
        print(f'   📝 Canales: {len(guild.channels)}')
    
    await bot.change_presence(
        activity=discord.Game(name="!ayuda para comandos")
    )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith('!'):
        await bot.process_commands(message)
        return
    
    if game_manager.is_game_active:
        await game_manager.handle_translation_attempt(message)

@bot.command(name='start')
@commands.has_permissions(manage_messages=True)
async def start_game(ctx):
    if game_manager.is_game_active:
        await ctx.send("❌ El juego ya está activo. Usa `!detener` para pararlo primero.")
        return
    
    await ctx.send("🎮 Iniciando el juego de traducción...")
    
    game_manager.game_task = asyncio.create_task(
        game_manager.start_game_loop(ctx.channel, ctx.guild)
    )

@bot.command(name='stop')
@commands.has_permissions(manage_messages=True)
async def stop_game(ctx):
    if not game_manager.is_game_active:
        await ctx.send("❌ El juego no está activo.")
        return
    
    await game_manager.stop_game()

@bot.command(name='score')
async def show_score(ctx):
    user_id = str(ctx.author.id)
    score = game_manager.scores.get(user_id, 0)
    
    embed = discord.Embed(
        title="📊 Tu Puntuación",
        description=f"**Usuario:** {ctx.author.display_name}\n"
                   f"**Puntos:** {score}",
        color=0x00ff00
    )
    
    await ctx.send(embed=embed)

@bot.command(name='table')
async def show_leaderboard(ctx):
    await game_manager.show_leaderboard()

@bot.command(name='word')
@commands.has_permissions(manage_messages=True)
async def force_new_word(ctx):
    if not game_manager.is_game_active:
        await ctx.send("❌ El juego no está activo. Usa `!iniciar` primero.")
        return
    
    if game_manager.round_task and not game_manager.round_task.done():
        game_manager.round_task.cancel()
    
    await ctx.send("🔄 Forzando nueva palabra...")
    await game_manager.start_new_round()

@bot.command(name='select')
@commands.has_permissions(manage_messages=True)
async def select_player(ctx, member: discord.Member):
    if not game_manager.is_game_active:
        await ctx.send("❌ El juego no está activo. Usa `!iniciar` primero.")
        return
    
    if member.bot:
        await ctx.send("❌ No puedes seleccionar un bot. Selecciona un usuario humano.")
        return
    
    if game_manager.round_task and not game_manager.round_task.done():
        game_manager.round_task.cancel()
    
    word = game_manager.get_random_word()
    game_manager.current_word = word
    game_manager.current_player = member
    
    embed = discord.Embed(
        title="🎯 Jugador Seleccionado",
        description=f"**Palabra en inglés:** `{word.upper()}`\n"
                   f"**Jugador seleccionado:** {member.mention}\n"
                   f"**Tiempo:** 60 segundos\n\n"
                   f"¡{member.display_name}, traduce esta palabra al español!",
        color=0xff6b35
    )
    embed.set_footer(text="Responde con la traducción en español")
    
    await ctx.send(embed=embed)
    
    game_manager.round_task = asyncio.create_task(game_manager.wait_and_check())

@bot.command(name='ayuda')
async def help_command(ctx):
    embed = discord.Embed(
        title="🎮 Comandos del Bot de Traducción",
        description="Aquí tienes todos los comandos disponibles:",
        color=0x0099ff
    )
    
    embed.add_field(
        name="👑 Comandos de Moderador",
        value="`!start` - Iniciar el juego de traducción\n"
              "`!stop` - Detener el juego\n"
              "`!word` - Forzar nueva palabra inmediatamente\n"
              "`!select @usuario` - Seleccionar jugador manualmente\n"
              "`!reset` - Reiniciar puntuaciones",
        inline=False
    )
    
    embed.add_field(
        name="👤 Comandos de Usuario",
        value="`!puntuacion` - Ver tu puntuación\n"
              "`!tabla` - Ver tabla de puntuaciones\n"
              "`!ayuda` - Mostrar esta ayuda",
        inline=False
    )
    
    embed.add_field(
        name="📋 Cómo Jugar",
        value="1. Un administrador inicia el juego con `!iniciar`\n"
              "2. Cada 5 minutos se selecciona una palabra en inglés\n"
              "3. Se elige un jugador aleatorio para traducirla\n"
              "4. El jugador tiene 60 segundos para responder\n"
              "5. Respuestas correctas: +10 puntos\n"
              "6. Respuestas incorrectas: -2 puntos",
        inline=False
    )
    
    embed.set_footer(text="¡Diviértete aprendiendo inglés!")
    
    await ctx.send(embed=embed)

@bot.command(name='status')
async def game_status(ctx):
    if game_manager.is_game_active:
        status = "🟢 Activo"
        if game_manager.current_word and game_manager.current_player:
            status += f"\n🎯 Palabra actual: {game_manager.current_word.upper()}"
            status += f"\n👤 Jugador: {game_manager.current_player.display_name}"
    else:
        status = "🔴 Inactivo"
    
    embed = discord.Embed(
        title="📊 Estado del Juego",
        description=f"**Estado:** {status}",
        color=0x00ff00 if game_manager.is_game_active else 0xff0000
    )
    
    await ctx.send(embed=embed)

@bot.command(name='reset')
@commands.has_permissions(manage_messages=True)
async def reset_scores(ctx):
    game_manager.scores = {}
    game_manager.save_scores()
    
    embed = discord.Embed(
        title="🔄 Puntuaciones Reiniciadas",
        description="Todas las puntuaciones han sido eliminadas.",
        color=0xffa500
    )
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes permisos para usar este comando.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Comando no encontrado. Usa `!ayuda` para ver los comandos disponibles.")
    else:
        await ctx.send(f"❌ Error: {error}")

def main():
    if not TOKEN:
        print("❌ Error: No se encontró el token de Discord.")
        print("Por favor, crea un archivo .env con tu DISCORD_TOKEN")
        return
    
    print("🚀 Iniciando bot de traducción...")
    bot.run(TOKEN)

if __name__ == "__main__":
    main() 