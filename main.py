import sys
import asyncio
from src.drivers.gpio import GPIO
from src.drivers.clock import tick_ms
from src.drivers.uart import UART
from src.app.state_machine import StateMachine
from src.app.led import LedController
from src.app.cli import CLI

async def main():
    print("=== Simulador de Control de Cargador ===")
    print("Escriba 'help' para ver comandos disponibles")
    print("Presione Ctrl+C para salir")
    print("-" * 40)
    
    # Inicializar componentes
    gpio = GPIO()
    led_controller = LedController(gpio)
    state_machine = StateMachine(gpio, led_controller)
    

    print("Inicializando sistema...")

    led_task = asyncio.create_task(led_controller.run_led_pattern())
    state_task = asyncio.create_task(state_machine.run())

    await asyncio.gather(led_task, state_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSaliendo...")
        sys.exit(0)