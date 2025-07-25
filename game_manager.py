import asyncio
import random
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import discord
import requests
from config import (
    ENGLISH_WORDS, CORRECT_TRANSLATIONS, GAME_INTERVAL, ROUND_DURATION, 
    POINTS_CORRECT, POINTS_WRONG, PALABRA_TIPO, PROBABILIDADES_AUTO, 
    CATEGORIAS_PREFERIDAS, COMANDOS_TIPO
)
from api_config import API_URL, USE_FALLBACK_APIS

def get_random_word_from_api(tipo_forzado=None):
    """Obtener palabra aleatoria de nuestra propia API según configuración"""
    try:
        print(f"🎯 Obteniendo palabra de nuestra API: {API_URL}")
        
        # Determinar el tipo de palabra a usar
        tipo_actual = tipo_forzado or PALABRA_TIPO
        
        if tipo_actual == "auto":
            # Selección aleatoria basada en probabilidades
            rand = random.randint(1, 100)
            if rand <= PROBABILIDADES_AUTO["normal"]:
                tipo_seleccionado = "normal"
            elif rand <= PROBABILIDADES_AUTO["normal"] + PROBABILIDADES_AUTO["warframe"]:
                tipo_seleccionado = "warframe"
            else:
                tipo_seleccionado = "mixto"
        else:
            tipo_seleccionado = tipo_actual
        
        print(f"📝 Tipo de palabra seleccionado: {tipo_seleccionado}")
        
        # Seleccionar endpoint según el tipo
        if tipo_seleccionado == "normal":
            endpoint = f"{API_URL}/palabra-normal"
            categoria = random.choice(CATEGORIAS_PREFERIDAS["normal"])
        elif tipo_seleccionado == "warframe":
            endpoint = f"{API_URL}/palabra-warframe"
            categoria = None  # Warframe solo tiene una categoría
        else:  # mixto
            endpoint = f"{API_URL}/palabra-mixta"
            categoria = random.choice(CATEGORIAS_PREFERIDAS["mixto"])
        
        # Construir URL con parámetros
        url = endpoint
        if categoria:
            url += f"?categoria={categoria}"
        
        print(f"🌐 Llamando a: {url}")
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            word = data["palabra"]
            print(f"✅ Palabra obtenida: '{word}' (tipo: {tipo_seleccionado}, categoría: {data.get('categoria', 'N/A')})")
            return word
        else:
            print(f"❌ Error HTTP obteniendo palabra: {response.status_code}")
        
        return None
    except Exception as e:
        print(f"❌ Error obteniendo palabra de nuestra API: {e}")
        return None

def translate_word_with_api(word, tipo="mixto"):
    """Obtener traducción de nuestra propia API"""
    try:
        url = f"{API_URL}/traducir/{word}?tipo={tipo}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Traducción obtenida de nuestra API: '{word}' -> '{data['traduccion']}'")
            return data["traduccion"]
        else:
            print(f"❌ Error HTTP obteniendo traducción: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo traducción de nuestra API: {e}")
        return None
    
    
            


class GameManager:
    def __init__(self):
        self.is_game_active = False
        self.current_word = None
        self.current_player = None
        self.scores = {}
        self.channel = None
        self.guild = None
        self.game_task = None
        self.round_task = None
        # Nuevo: tipo de palabras configurado
        self.tipo_palabras = "auto"  # Por defecto usa el modo automático
        self.load_scores()
        self.load_config()
    
    def load_config(self):
        """Cargar configuración guardada"""
        try:
            with open('bot_config.json', 'r') as f:
                config = json.load(f)
                self.tipo_palabras = config.get('tipo_palabras', 'auto')
                print(f"⚙️ Configuración cargada: tipo_palabras = {self.tipo_palabras}")
        except FileNotFoundError:
            print("⚙️ No se encontró archivo de configuración, usando valores por defecto")
        except Exception as e:
            print(f"⚙️ Error cargando configuración: {e}")
    
    def load_scores(self):
        try:
            with open('scores.json', 'r', encoding='utf-8') as f:
                self.scores = json.load(f)
        except FileNotFoundError:
            self.scores = {}
    
    def save_scores(self):
        with open('scores.json', 'w', encoding='utf-8') as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=2)
    
    def get_random_word(self) -> str:
        """Obtener palabra aleatoria según configuración actual"""
        word = get_random_word_from_api(tipo_forzado=self.tipo_palabras)
        if word:
            return word
        else:
            # Fallback a palabras locales
            print("⚠️ API falló, usando palabras de fallback")
            return random.choice(ENGLISH_WORDS)
    
    def get_correct_translation(self, word: str) -> str:
        """Obtener traducción según el tipo actual"""
        translation = translate_word_with_api(word, tipo=self.tipo_palabras if self.tipo_palabras != "auto" else "mixto")
        if translation:
            return translation
        else:
            # Fallback a traducciones locales
            return CORRECT_TRANSLATIONS.get(word.lower(), "traducción no encontrada")
    
    def check_translation(self, word: str, user_translation: str) -> bool:
        """Verificar si la traducción es correcta usando nuestra API"""
        user_translation = user_translation.lower().strip()
        
        # Obtener traducción completa de nuestra API
        try:
            response = requests.get(f"{API_URL}/traducir/{word}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar traducción principal
                correct_translation = data["traduccion"].lower()
                if user_translation == correct_translation:
                    return True
                
                # Verificar alternativas
                alternativas = data.get("alternativas", [])
                for alt in alternativas:
                    if user_translation == alt.lower():
                        return True
                
                # Verificar errores de tipeo menores (máximo 1 carácter de diferencia)
                if len(user_translation) >= 3 and len(correct_translation) >= 3:
                    # Solo acepta si las palabras son muy similares en longitud
                    if abs(len(user_translation) - len(correct_translation)) <= 1:
                        # Verificar si es un error de tipeo menor
                        if self.are_similar_words(user_translation, correct_translation):
                            return True
                    
                return False
        except Exception as e:
            print(f"❌ Error verificando traducción con API: {e}")
            # Fallback al método original (también más estricto)
            correct = self.get_correct_translation(word).lower()
            
            if user_translation == correct:
                return True
            
            # Verificar errores de tipeo menores en fallback también
            if len(user_translation) >= 3 and len(correct) >= 3:
                if abs(len(user_translation) - len(correct)) <= 1:
                    if self.are_similar_words(user_translation, correct):
                        return True
                
            return False
    
    def are_similar_words(self, word1: str, word2: str) -> bool:
        """Verificar si dos palabras son muy similares (máximo 1 diferencia)"""
        if len(word1) == len(word2):
            # Misma longitud: verificar cuántos caracteres difieren
            differences = sum(c1 != c2 for c1, c2 in zip(word1, word2))
            return differences <= 1  # Solo 1 carácter diferente máximo
        elif abs(len(word1) - len(word2)) == 1:
            # Diferencia de 1 carácter: verificar si uno está contenido en el otro
            shorter, longer = (word1, word2) if len(word1) < len(word2) else (word2, word1)
            # Verificar si al eliminar 1 carácter del más largo obtenemos el más corto
            for i in range(len(longer)):
                if longer[:i] + longer[i+1:] == shorter:
                    return True
            return False
        return False
    
    def update_score(self, user_id: int, points: int):
        if str(user_id) not in self.scores:
            self.scores[str(user_id)] = 0
        self.scores[str(user_id)] += points
        self.save_scores()
    
    def get_top_scores(self, limit: int = 10) -> List[tuple]:
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:limit]
    
    async def select_random_player(self) -> Optional[discord.Member]:
        if not self.guild:
            print("❌ No hay guild configurado")
            return None
        
        try:
            print("🔄 Obteniendo todos los miembros del servidor...")
            all_members = []
            async for member in self.guild.fetch_members():
                all_members.append(member)
            print(f"📊 Total de miembros en el servidor: {len(all_members)}")
            
            print("🔍 Lista completa de miembros:")
            for i, member in enumerate(all_members):
                print(f"   {i+1}. {member.display_name} (Bot: {member.bot}, ID: {member.id})")
            
            human_members = []
            for member in all_members:
                print(f"\n🔍 Analizando: {member.display_name}")
                print(f"   - Bot: {member.bot}")
                print(f"   - ID: {member.id}")
                print(f"   - Nombre: {member.name}")
                print(f"   - Display: {member.display_name}")
                
                is_real_bot = member.bot
                print(f"   - Es bot real: {is_real_bot}")
                
                is_this_bot = member.id == self.guild.me.id
                print(f"   - Es este bot: {is_this_bot}")
                
                is_application = False
                if hasattr(member, 'flags'):
                    try:
                        is_application = member.flags.verified_bot
                    except:
                        is_application = False
                print(f"   - Es aplicación: {is_application}")
                
                member_name_lower = member.display_name.lower()
                member_username_lower = member.name.lower()
                
                app_indicators = [
                    'bot', 'app', 'application', 'ce', 'english', 'translator',
                    'emoji', 'gg', 'discord', 'server', 'mod', 'admin',
                    'webhook', 'integration', 'api', 'service', 'tool',
                    'helper', 'assistant', 'ai', 'gpt', 'chat'
                ]
                
                has_app_name = any(indicator in member_name_lower or indicator in member_username_lower 
                                 for indicator in app_indicators)
                print(f"   - Tiene nombre de app: {has_app_name}")
                
                has_app_id = member.id < 1000000000000000000
                print(f"   - Tiene ID de app: {has_app_id}")
                
                is_real_human = (
                    not is_real_bot and
                    not is_this_bot
                )
                print(f"   - Es humano real: {is_real_human}")
                
                if is_real_human:
                    human_members.append(member)
                    print(f"✅ Usuario REAL confirmado: {member.display_name}")
                else:
                    reason = []
                    if is_real_bot: reason.append("Bot real")
                    if is_this_bot: reason.append("Este bot")
                    
                    print(f"❌ Excluido: {member.display_name} - Razones: {', '.join(reason)}")
            
            if not human_members:
                print("❌ No se encontraron usuarios REALES en el servidor")
                return None
            
            print(f"✅ Encontrados {len(human_members)} usuarios REALES")
            
            print(f"✅ Usando todos los {len(human_members)} usuarios reales encontrados")
            
            selected_player = random.choice(human_members)
            print(f"🎯 Jugador seleccionado: {selected_player.display_name} (ID: {selected_player.id})")
            
            return selected_player
            
        except Exception as e:
            print(f"❌ Error seleccionando jugador: {e}")
            return None
    
    async def start_game_loop(self, channel: discord.TextChannel, guild: discord.Guild):
        self.channel = channel
        self.guild = guild
        self.is_game_active = True
        self.load_scores()
        
        await self.channel.send("🎮 **¡El juego de traducción ha comenzado!** 🎮\n"
                              f"Cada {GAME_INTERVAL // 60} minutos se seleccionará una palabra en inglés "
                              "y un jugador aleatorio deberá traducirla al español.")
        
        while self.is_game_active:
            try:
                await asyncio.sleep(GAME_INTERVAL)
                if self.is_game_active:
                    await self.start_new_round()
            except asyncio.CancelledError:
                break
    
    async def start_new_round(self):
        if not self.is_game_active:
            return
        
        print("🎮 Iniciando nueva ronda...")
        
        self.current_word = self.get_random_word()
        print(f"📝 Palabra seleccionada: {self.current_word}")
        
        self.current_player = await self.select_random_player()
        
        if not self.current_player:
            print("❌ No se pudo seleccionar un jugador")
            await self.channel.send("❌ No se pudo seleccionar un jugador para esta ronda.")
            return
        
        if self.current_player.bot:
            print(f"❌ Error: Se seleccionó un bot ({self.current_player.display_name})")
            await self.channel.send("❌ Error: Se seleccionó un bot. Reiniciando ronda...")
            await asyncio.sleep(2)
            await self.start_new_round()
            return
        
        print(f"✅ Ronda configurada: {self.current_word} -> {self.current_player.display_name} (Humano: {not self.current_player.bot})")
        
        # Ping al jugador seleccionado
        ping_message = f"🎯 **¡{self.current_player.mention} es tu turno!** 🎯"
        
        embed = discord.Embed(
            title="🎯 Nueva Ronda de Traducción",
            description=f"**Palabra en inglés:** `{self.current_word.upper()}`\n"
                       f"**Jugador seleccionado:** {self.current_player.mention}\n"
                       f"**Tiempo:** {ROUND_DURATION} segundos\n\n"
                       f"¡{self.current_player.display_name}, traduce esta palabra al español!",
            color=0x00ff00
        )
        embed.set_footer(text="Responde con la traducción en español")
        
        # Enviar ping y embed juntos
        await self.channel.send(ping_message)
        await self.channel.send(embed=embed)
        
        print(f"⏰ Iniciando temporizador de {ROUND_DURATION} segundos...")
        
        self.round_task = asyncio.create_task(self.wait_and_check())
        print(f"⏰ Tarea del temporizador creada: {self.round_task}")
        
        print(f"✅ Ronda iniciada completamente - Palabra: {self.current_word}, Jugador: {self.current_player.display_name}")
    
    async def wait_and_check(self):
        print(f"⏰ WAIT_AND_CHECK: Iniciando espera de {ROUND_DURATION} segundos...")
        print(f"⏰ WAIT_AND_CHECK: Palabra actual: {self.current_word}")
        print(f"⏰ WAIT_AND_CHECK: Jugador actual: {self.current_player.display_name if self.current_player else 'None'}")
        
        await asyncio.sleep(ROUND_DURATION)
        
        print(f"⏰ WAIT_AND_CHECK: Tiempo completado después de {ROUND_DURATION} segundos")
        print(f"⏰ WAIT_AND_CHECK: Verificando estado del juego...")
        print(f"⏰ WAIT_AND_CHECK: is_game_active: {self.is_game_active}")
        print(f"⏰ WAIT_AND_CHECK: current_word: {self.current_word}")
        print(f"⏰ WAIT_AND_CHECK: current_player: {self.current_player.display_name if self.current_player else 'None'}")
        
        if self.is_game_active and self.current_word and self.current_player:
            print(f"⏰ WAIT_AND_CHECK: Enviando mensaje de tiempo agotado")
            
            correct_translation = self.get_correct_translation(self.current_word)
            self.update_score(self.current_player.id, POINTS_WRONG)
            
            embed = discord.Embed(
                title="⏰ Tiempo Agotado",
                description=f"**Palabra:** `{self.current_word.upper()}`\n"
                           f"**Traducción correcta:** `{correct_translation}`\n"
                           f"**Jugador:** {self.current_player.mention}\n"
                           f"**Puntos perdidos:** {POINTS_WRONG}\n"
                           f"**Puntuación total:** {self.scores.get(str(self.current_player.id), 0)}\n\n"
                           "¡Nadie respondió correctamente en el tiempo límite!",
                color=0xff0000
            )
            
            await self.channel.send(embed=embed)
            
            self.current_word = None
            self.current_player = None
            print(f"⏰ WAIT_AND_CHECK: Estado limpiado")
        else:
            print(f"⏰ WAIT_AND_CHECK: Juego no activo o ronda ya terminada, NO enviando mensaje")
    
    async def simple_timer(self):
        print(f"⏰ SIMPLE TIMER: Iniciando espera de {ROUND_DURATION} segundos...")
        
        await asyncio.sleep(ROUND_DURATION)
        
        print(f"⏰ SIMPLE TIMER: Tiempo completado, verificando estado...")
        
        if self.is_game_active and self.current_word and self.current_player:
            print(f"⏰ SIMPLE TIMER: Enviando mensaje de tiempo agotado")
            
            correct_translation = self.get_correct_translation(self.current_word)
            
            embed = discord.Embed(
                title="⏰ Tiempo Agotado",
                description=f"**Palabra:** `{self.current_word.upper()}`\n"
                           f"**Traducción correcta:** `{correct_translation}`\n"
                           f"**Jugador:** {self.current_player.mention}\n\n"
                           "¡Nadie respondió correctamente en el tiempo límite!",
                color=0xff0000
            )
            
            await self.channel.send(embed=embed)
            self.update_score(self.current_player.id, POINTS_WRONG)
            
            self.current_word = None
            self.current_player = None
        else:
            print(f"⏰ SIMPLE TIMER: Juego no activo o ronda ya terminada, no enviando mensaje")
    
    async def round_timer(self):
        try:
            print(f"⏰ Temporizador iniciado, esperando {ROUND_DURATION} segundos...")
            print(f"⏰ Palabra actual: {self.current_word}")
            print(f"⏰ Jugador actual: {self.current_player.display_name if self.current_player else 'None'}")
            
            await asyncio.sleep(ROUND_DURATION)
            
            print(f"⏰ Temporizador terminado después de {ROUND_DURATION} segundos")
            print(f"⏰ Verificando si la ronda sigue activa...")
            
            if self.current_player and self.current_word and self.is_game_active:
                print(f"⏰ Enviando mensaje de tiempo agotado para {self.current_player.display_name}")
                correct_translation = self.get_correct_translation(self.current_word)
                
                embed = discord.Embed(
                    title="⏰ Tiempo Agotado",
                    description=f"**Palabra:** `{self.current_word.upper()}`\n"
                               f"**Traducción correcta:** `{correct_translation}`\n"
                               f"**Jugador:** {self.current_player.mention}\n\n"
                               "¡Nadie respondió correctamente en el tiempo límite!",
                    color=0xff0000
                )
                
                await self.channel.send(embed=embed)
                
                self.update_score(self.current_player.id, POINTS_WRONG)
            else:
                print(f"⏰ Ronda ya no está activa, no enviando mensaje de tiempo agotado")
                
        except asyncio.CancelledError:
            print(f"⏰ Temporizador cancelado")
            pass
        except Exception as e:
            print(f"⏰ Error en temporizador: {e}")
        finally:
            print(f"⏰ Limpiando estado de la ronda")
            self.current_word = None
            self.current_player = None
    
    async def handle_translation_attempt(self, message: discord.Message) -> bool:
        print(f"🔍 Procesando mensaje de {message.author.display_name}: '{message.content}'")
        
        if not self.is_game_active or not self.current_word or not self.current_player:
            print("❌ Juego no activo o no hay ronda en curso")
            return False
        
        if message.author.id != self.current_player.id:
            print(f"❌ Mensaje no es del jugador seleccionado (esperado: {self.current_player.id}, recibido: {message.author.id})")
            return False
        
        if message.author.bot:
            print(f"🤖 Ignorando respuesta de bot: {message.author.display_name}")
            return False
        
        user_translation = message.content.strip()
        is_correct = self.check_translation(self.current_word, user_translation)
        
        if is_correct:
            if self.round_task and not self.round_task.done():
                print(f"✅ Cancelando temporizador por respuesta correcta de {message.author.display_name}")
                self.round_task.cancel()
            
            correct_translation = self.get_correct_translation(self.current_word)
            self.update_score(self.current_player.id, POINTS_CORRECT)
            
            embed = discord.Embed(
                title="✅ ¡Respuesta Correcta!",
                description=f"**Palabra:** `{self.current_word.upper()}`\n"
                           f"**Traducción:** `{correct_translation}`\n"
                           f"**Jugador:** {self.current_player.mention}\n"
                           f"**Puntos ganados:** +{POINTS_CORRECT}\n"
                           f"**Puntuación total:** {self.scores.get(str(self.current_player.id), 0)}",
                color=0x00ff00
            )
            
            await self.channel.send(embed=embed)
            
            print(f"🔄 Limpiando estado de la ronda después de respuesta correcta")
            self.current_word = None
            self.current_player = None
            
            return True
        else:
            print(f"🔄 Respuesta incorrecta de {message.author.display_name}: '{user_translation}', pero puede seguir intentando en silencio")
            return True
    
    async def stop_game(self):
        self.is_game_active = False
        
        if self.round_task and not self.round_task.done():
            self.round_task.cancel()
        
        if self.game_task and not self.game_task.done():
            self.game_task.cancel()
        
        await self.channel.send("🛑 **El juego de traducción se ha detenido.**")
    
    async def show_leaderboard(self):
        top_scores = self.get_top_scores(10)
        
        if not top_scores:
            await self.channel.send("📊 No hay puntuaciones registradas aún.")
            return
        
        embed = discord.Embed(
            title="🏆 Tabla de Puntuaciones",
            description="Los mejores traductores del servidor:",
            color=0xffd700
        )
        
        for i, (user_id, score) in enumerate(top_scores, 1):
            user = self.guild.get_member(int(user_id))
            username = user.display_name if user else f"Usuario {user_id}"
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            embed.add_field(
                name=f"{medal} {username}",
                value=f"**{score} puntos**",
                inline=False
            )
        
        await self.channel.send(embed=embed) 