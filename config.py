import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', 0))
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))

GAME_INTERVAL = 5400  # 1 hora y media en segundos (90 minutos * 60)
ROUND_DURATION = 60
POINTS_CORRECT = 15
POINTS_WRONG = -5

ENGLISH_WORDS = [
    "apple", "house", "car", "book", "computer", "phone", "table", "chair",
    "window", "door", "tree", "flower", "sun", "moon", "star", "water",
    "fire", "earth", "air", "food", "drink", "sleep", "work", "play",
    "happy", "sad", "angry", "tired", "excited", "bored", "hungry", "thirsty",
    "hot", "cold", "warm", "cool", "big", "small", "tall", "short",
    "fast", "slow", "loud", "quiet", "bright", "dark", "clean", "dirty",
    "new", "old", "young", "beautiful", "ugly", "good", "bad", "easy", "hard"
]

CORRECT_TRANSLATIONS = {
    "apple": "manzana",
    "house": "casa",
    "car": "coche",
    "book": "libro",
    "computer": "computadora",
    "phone": "teléfono",
    "table": "mesa",
    "chair": "silla",
    "window": "ventana",
    "door": "puerta",
    "tree": "árbol",
    "flower": "flor",
    "sun": "sol",
    "moon": "luna",
    "star": "estrella",
    "water": "agua",
    "fire": "fuego",
    "earth": "tierra",
    "air": "aire",
    "food": "comida",
    "drink": "bebida",
    "sleep": "dormir",
    "work": "trabajar",
    "play": "jugar",
    "happy": "feliz",
    "sad": "triste",
    "angry": "enojado",
    "tired": "cansado",
    "excited": "emocionado",
    "bored": "aburrido",
    "hungry": "hambriento",
    "thirsty": "sediento",
    "hot": "caliente",
    "cold": "frío",
    "warm": "templado",
    "cool": "fresco",
    "big": "grande",
    "small": "pequeño",
    "tall": "alto",
    "short": "bajo",
    "fast": "rápido",
    "slow": "lento",
    "loud": "ruidoso",
    "quiet": "silencioso",
    "bright": "brillante",
    "dark": "oscuro",
    "clean": "limpio",
    "dirty": "sucio",
    "new": "nuevo",
    "old": "viejo",
    "young": "joven",
    "beautiful": "hermoso",
    "ugly": "feo",
    "good": "bueno",
    "bad": "malo",
    "easy": "fácil",
    "hard": "difícil"
} 