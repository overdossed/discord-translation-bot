# Configuración del Bot de Discord
import os
from dotenv import load_dotenv

load_dotenv()

# Token del bot (requerido)
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = None  # None para todos los servidores
CHANNEL_ID = None  # None para cualquier canal

# Configuración del juego
GAME_INTERVAL = 5400  # 1.5 horas en segundos
ROUND_DURATION = 120  # 2 minutos en segundos
POINTS_CORRECT = 10   # Puntos por respuesta correcta
POINTS_WRONG = -15    # Puntos perdidos por timeout

# ====== NUEVA CONFIGURACIÓN: TIPOS DE PALABRAS ======

# Configuración del tipo de palabras
# Opciones: "normal", "warframe", "mixto", "auto"
PALABRA_TIPO = "auto"  # auto = aleatorio entre todos los tipos

# Probabilidades cuando se usa tipo "auto" (deben sumar 100)
PROBABILIDADES_AUTO = {
    "normal": 70,      # 70% probabilidad de palabras normales
    "warframe": 20,    # 20% probabilidad de mods de Warframe  
    "mixto": 10        # 10% probabilidad de mezcla completa
}

# Categorías preferidas por tipo
CATEGORIAS_PREFERIDAS = {
    "normal": ["animals", "food", "colors", "objects", "actions"],
    "warframe": ["warframe_mods"],
    "mixto": ["animals", "food", "colors", "objects", "actions", "warframe_mods"]
}

# Comandos para cambiar tipo de palabras (solo admins)
COMANDOS_TIPO = {
    "!tipo normal": "normal",
    "!tipo warframe": "warframe", 
    "!tipo mixto": "mixto",
    "!tipo auto": "auto"
}

# ====== PALABRAS DE FALLBACK (si falla la API) ======

# Lista mínima de palabras en inglés como fallback
ENGLISH_WORDS = [
    "cat", "dog", "bird", "house", "car"
]

# Traducciones correspondientes
CORRECT_TRANSLATIONS = {
    "cat": "gato",
    "dog": "perro", 
    "bird": "pájaro",
    "house": "casa",
    "car": "coche"
} 