import discord
from discord.ext import commands
import asyncio
import os
from config import TOKEN, GUILD_ID, CHANNEL_ID
from game_manager import GameManager
import json

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
        title="🎮 Comandos del Bot de Traducción v2.0",
        description="Bot mejorado con API propia y palabras de Warframe:",
        color=0x0099ff
    )
    
    embed.add_field(
        name="👑 Comandos de Moderador",
        value="`!iniciar` - Iniciar el juego de traducción\n"
              "`!detener` - Detener el juego\n"
              "`!palabra` - Forzar nueva palabra inmediatamente\n"
              "`!seleccionar @usuario` - Seleccionar jugador manualmente\n"
              "`!reiniciar` - Reiniciar puntuaciones\n"
              "`!tipo [tipo]` - Configurar tipo de palabras",
        inline=False
    )
    
    embed.add_field(
        name="👤 Comandos de Usuario",
        value="`!puntuacion` - Ver tu puntuación\n"
              "`!tabla` - Ver tabla de puntuaciones\n"
              "`!estado` - Ver estado del juego\n"
              "`!estadisticas` - Ver estadísticas de palabras\n"
              "`!ayuda` - Mostrar esta ayuda",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Tipos de Palabras",
        value="`normal` - Palabras cotidianas\n"
              "`warframe` - Solo mods de Warframe\n"
              "`mixto` - Todas mezcladas\n"
              "`auto` - Selección automática (70% normal, 20% warframe, 10% mixto)",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Cómo Jugar",
        value="1. Un moderador inicia el juego con `!iniciar`\n"
              "2. Cada 1.5 horas aparece una palabra en inglés\n"
              "3. Se selecciona un jugador aleatorio\n"
              "4. Tienes 2 minutos para traducir la palabra\n"
              "5. +10 puntos por acierto, -15 por timeout",
        inline=False
    )
    
    embed.set_footer(text="Bot desarrollado con API propia • Versión 2.0")
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

@bot.command(name='tipo')
@commands.has_permissions(manage_messages=True)
async def cambiar_tipo_palabras(ctx, tipo: str = None):
    """Cambiar el tipo de palabras que usa el bot"""
    global game_manager
    
    tipos_validos = ["normal", "warframe", "mixto", "auto"]
    
    if not tipo:
        # Mostrar tipo actual y opciones
        tipo_actual = getattr(game_manager, 'tipo_palabras', 'auto')
        
        embed = discord.Embed(
            title="⚙️ Configuración de Tipos de Palabras",
            description=f"**Tipo actual:** `{tipo_actual.upper()}`\n\n"
                       "**Tipos disponibles:**\n"
                       "• `normal` - Solo palabras cotidianas (animales, comida, colores, etc.)\n"
                       "• `warframe` - Solo mods de Warframe\n"
                       "• `mixto` - Todas las palabras mezcladas\n"
                       "• `auto` - Selección automática con probabilidades\n\n"
                       "**Uso:** `!tipo <tipo>`\n"
                       "**Ejemplo:** `!tipo warframe`",
            color=0x9932cc
        )
        
        if tipo_actual == "auto":
            from config import PROBABILIDADES_AUTO
            probabilidades_texto = "\n".join([
                f"• {k.capitalize()}: {v}%" 
                for k, v in PROBABILIDADES_AUTO.items()
            ])
            embed.add_field(
                name="🎲 Probabilidades en modo AUTO",
                value=probabilidades_texto,
                inline=False
            )
        
        await ctx.send(embed=embed)
        return
    
    tipo = tipo.lower()
    
    if tipo not in tipos_validos:
        await ctx.send(f"❌ Tipo inválido. Usa: `{', '.join(tipos_validos)}`")
        return
    
    # Cambiar tipo en el game_manager
    game_manager.tipo_palabras = tipo
    
    # Guardar en archivo de configuración temporal (opcional)
    try:
        with open('bot_config.json', 'w') as f:
            json.dump({'tipo_palabras': tipo}, f)
    except:
        pass  # Si no se puede guardar, no pasa nada
    
    # Descripción del tipo seleccionado
    descripciones = {
        "normal": "palabras cotidianas (animales, comida, colores, objetos, acciones)",
        "warframe": "mods de Warframe únicamente",
        "mixto": "todas las palabras mezcladas",
        "auto": "selección automática con probabilidades configuradas"
    }
    
    embed = discord.Embed(
        title="✅ Tipo de Palabras Cambiado",
        description=f"**Nuevo tipo:** `{tipo.upper()}`\n"
                   f"**Descripción:** {descripciones[tipo]}\n\n"
                   "El cambio se aplicará en la próxima ronda.",
        color=0x00ff00
    )
    
    await ctx.send(embed=embed)

@bot.command(name='estadisticas', aliases=['stats'])
async def mostrar_estadisticas_api(ctx):
    """Mostrar estadísticas de la API de palabras"""
    try:
        from api_config import API_URL
        import requests
        
        # Obtener estadísticas de cada tipo
        tipos = ["normal", "warframe", "mixto"]
        estadisticas = {}
        
        for tipo in tipos:
            try:
                response = requests.get(f"{API_URL}/estadisticas?tipo={tipo}", timeout=5)
                if response.status_code == 200:
                    estadisticas[tipo] = response.json()["estadisticas"]
            except:
                estadisticas[tipo] = {"total": "Error"}
        
        embed = discord.Embed(
            title="📊 Estadísticas de la Base de Datos",
            description="Cantidad de palabras disponibles por tipo:",
            color=0x1f8b4c
        )
        
        for tipo, stats in estadisticas.items():
            if isinstance(stats.get("total"), int):
                categorias = stats.get("por_categoria", {})
                categorias_texto = ", ".join([f"{k}: {v}" for k, v in categorias.items()])
                
                embed.add_field(
                    name=f"📝 {tipo.capitalize()}",
                    value=f"**Total:** {stats['total']} palabras\n"
                           f"**Categorías:** {categorias_texto}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"❌ {tipo.capitalize()}",
                    value="Error al obtener datos",
                    inline=False
                )
        
        embed.set_footer(text=f"Datos de: {API_URL}")
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error obteniendo estadísticas: {e}")

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