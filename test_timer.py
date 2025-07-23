import asyncio
import time

async def test_timer():
    """Prueba simple del temporizador"""
    print(f"⏰ Iniciando prueba de temporizador...")
    start_time = time.time()
    
    # Simular el temporizador del juego
    await asyncio.sleep(10)  # 10 segundos para la prueba
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"⏰ Temporizador terminado después de {elapsed:.2f} segundos")
    print(f"⏰ Tiempo esperado: 10 segundos")

if __name__ == "__main__":
    print("🚀 Probando temporizador...")
    asyncio.run(test_timer())
    print("✅ Prueba completada") 