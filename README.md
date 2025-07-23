# 🎮 Bot de Traducción para Discord

Un bot divertido para Discord que ayuda a aprender inglés jugando. Cada cierto tiempo, el bot selecciona una palabra en inglés y elige a un jugador aleatorio del servidor para que la traduzca al español.

## 🚀 Características

- **Juego automático**: Cada 5 minutos se selecciona una nueva palabra
- **Selección aleatoria**: Elige jugadores aleatoriamente del servidor
- **Sistema de puntuación**: Lleva un registro de aciertos y errores
- **Tabla de puntuaciones**: Muestra los mejores traductores
- **Comandos de administración**: Para controlar el juego
- **Interfaz visual**: Embeds bonitos y coloridos

## 📋 Requisitos

- Python 3.8 o superior
- Una cuenta de Discord
- Un bot de Discord (creado en el Portal de Desarrolladores)

## 🛠️ Instalación

### 1. Clonar o descargar el proyecto
```bash
git clone <tu-repositorio>
cd Bot
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Crear el bot en Discord

1. Ve a [Discord Developer Portal](https://discord.com/developers/applications)
2. Haz clic en "New Application"
3. Dale un nombre a tu aplicación
4. Ve a la sección "Bot"
5. Haz clic en "Add Bot"
6. Copia el token del bot (lo necesitarás después)

### 4. Configurar el bot

1. Crea un archivo `.env` en la carpeta del bot:
```bash
# Token de tu bot de Discord
DISCORD_TOKEN=tu_token_aqui

# ID de tu servidor de Discord (opcional)
GUILD_ID=123456789012345678

# ID del canal donde se jugará (opcional)
CHANNEL_ID=123456789012345678
```

2. Reemplaza `tu_token_aqui` con el token de tu bot
3. (Opcional) Agrega el ID de tu servidor y canal

### 5. Invitar el bot a tu servidor

1. En el Portal de Desarrolladores, ve a "OAuth2" > "URL Generator"
2. Selecciona los scopes: `bot` y `applications.commands`
3. Selecciona los permisos necesarios:
   - Send Messages
   - Embed Links
   - Read Message History
   - Use Slash Commands
4. Copia la URL generada y ábrela en tu navegador
5. Selecciona tu servidor y autoriza el bot

## 🎮 Cómo usar el bot

### Comandos de Administrador

- `!iniciar` - Iniciar el juego de traducción
- `!detener` - Detener el juego
- `!palabra` - Forzar una nueva palabra inmediatamente
- `!reiniciar` - Reiniciar todas las puntuaciones

### Comandos de Usuario

- `!puntuacion` - Ver tu puntuación personal
- `!tabla` - Ver la tabla de puntuaciones
- `!ayuda` - Mostrar todos los comandos
- `!estado` - Ver el estado actual del juego

### Cómo jugar

1. Un administrador inicia el juego con `!iniciar`
2. Cada 5 minutos se selecciona una palabra en inglés
3. Se elige un jugador aleatorio para traducirla
4. El jugador tiene 60 segundos para responder
5. Respuestas correctas: +10 puntos
6. Respuestas incorrectas: -2 puntos

## 🚀 Ejecutar el bot

```bash
python bot.py
```

## ⚙️ Configuración

Puedes modificar la configuración del juego editando `config.py`:

- `GAME_INTERVAL`: Intervalo entre rondas (en segundos)
- `ROUND_DURATION`: Tiempo para responder (en segundos)
- `POINTS_CORRECT`: Puntos por respuesta correcta
- `POINTS_WRONG`: Puntos por respuesta incorrecta
- `ENGLISH_WORDS`: Lista de palabras en inglés
- `CORRECT_TRANSLATIONS`: Diccionario de traducciones correctas

## 📁 Estructura del proyecto

```
Bot/
├── bot.py              # Archivo principal del bot
├── game_manager.py     # Lógica del juego
├── config.py           # Configuración
├── requirements.txt    # Dependencias
├── scores.json         # Puntuaciones (se crea automáticamente)
├── env_example.txt     # Ejemplo de variables de entorno
└── README.md          # Este archivo
```

## 🔧 Solución de problemas

### El bot no responde
- Verifica que el token sea correcto
- Asegúrate de que el bot tenga los permisos necesarios
- Revisa que esté conectado al servidor

### Error de permisos
- Asegúrate de que el bot tenga permisos de administrador o los permisos específicos necesarios

### El juego no inicia
- Verifica que uses el comando en el canal correcto
- Asegúrate de tener permisos de administrador

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Puedes:
- Agregar nuevas palabras al juego
- Mejorar la interfaz visual
- Agregar nuevas funcionalidades
- Reportar bugs

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 🎯 Próximas características

- [ ] Más palabras y categorías
- [ ] Diferentes idiomas
- [ ] Modo competitivo
- [ ] Estadísticas detalladas
- [ ] Integración con APIs de traducción

---

¡Diviértete aprendiendo inglés con tu bot de Discord! 🎉 