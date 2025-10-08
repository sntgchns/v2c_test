# +++ CÓDIGO NUEVO Y COMPLETO (main.py) +++
import sys
import asyncio
from src.drivers.gpio import GPIO
from src.app.state_machine import StateMachine
from src.app.led import LedController

async def test_harness(state_machine: StateMachine):
    """
    Esta corutina simula la interacción del usuario y eventos externos.
    Sigue un guion para probar todas las transiciones de estado.
    """
    print("\n--- [TEST] El arnés de pruebas se iniciará en 5 segundos. ---")
    await asyncio.sleep(5)

    # 1. Transición de IDLE -> READY
    print("\n--- [TEST] Simulando conexión del vehículo (PILOT_OK = 1) ---")
    state_machine.gpio.set_input("PILOT_OK", 1)
    await asyncio.sleep(5)

    # 2. Transición de READY -> CHARGING
    print("\n--- [TEST] Simulando pulsación de botón para iniciar carga (BTN = 1) ---")
    state_machine.gpio.set_input("BTN", 1)
    await asyncio.sleep(0.1) # Mantenemos el botón presionado 100ms
    print("\n--- [TEST] Simulando liberación de botón (BTN = 0) ---")
    state_machine.gpio.set_input("BTN", 0)
    await asyncio.sleep(8)

    # 3. Simulación de un fallo (-> FAULT)
    print("\n--- [TEST] ¡Simulando un FALLO! (FAULT = 1) ---")
    state_machine.gpio.set_input("FAULT", 1)
    await asyncio.sleep(5)

    # 4. Recuperación del fallo (FAULT -> IDLE)
    print("\n--- [TEST] Eliminando el fallo (FAULT = 0) ---")
    state_machine.gpio.set_input("FAULT", 0)
    await asyncio.sleep(1)
    print("\n--- [TEST] Pulsando botón para resetear (BTN = 1) ---")
    state_machine.gpio.set_input("BTN", 1)
    await asyncio.sleep(0.1)
    state_machine.gpio.set_input("BTN", 0)
    
    print("\n--- [TEST] Secuencia de prueba completada. ---")


async def main():
    print("=== Simulador de Control de Cargador (Async con Test) ===")
    
    # 1. Inicializar componentes
    gpio = GPIO()
    led_controller = LedController(gpio)
    state_machine = StateMachine(gpio, led_controller)
    
    print("Sistema iniciado...")

    # 2. Crear las tareas que correrán en segundo plano
    led_task = asyncio.create_task(led_controller.run_led_pattern())
    state_machine_task = asyncio.create_task(state_machine.run())
    # ¡Añadimos nuestra nueva tarea de prueba!
    test_task = asyncio.create_task(test_harness(state_machine))
    
    # 3. Ejecutar las tareas para siempre
    await asyncio.gather(led_task, state_machine_task, test_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSistema detenido por el usuario.")