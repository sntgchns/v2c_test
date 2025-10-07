import sys
import time
from src.drivers.gpio import GPIO
from src.drivers.clock import tick_ms
from src.drivers.uart import UART
from src.app.state_machine import StateMachine
from src.app.led import LedController
from src.app.cli import CLI

def main():
    print("=== Simulador de Control de Cargador ===")
    print("Escriba 'help' para ver comandos disponibles")
    print("Presione Ctrl+C para salir")
    print("-" * 40)
    
    # Inicializar componentes
    gpio = GPIO()
    led_controller = LedController(gpio)
    state_machine = StateMachine(gpio, led_controller)
    uart = UART()
    cli = CLI(state_machine, gpio, led_controller)
    
    # Variables para control de tiempo
    last_tick = tick_ms()
    tick_interval = 10  # Ejecutar cada 10ms
    
    # Estado inicial
    print("Sistema iniciado en estado IDLE")
    print("PILOT_OK=0, FAULT=0, BTN=0")
    print("Contactor=OFF, LED=parpadeo lento")
    print()
    
    try:
        while True:
            current_time = tick_ms()
            
            # Ejecutar tick del sistema cada ~10ms
            if current_time - last_tick >= tick_interval:
                # Actualizar máquina de estados
                state_machine.step()
                
                # Actualizar controlador de LED
                led_controller.step()
                
                last_tick = current_time
            
            # Procesar comandos CLI (no bloqueante)
            try:
                line = uart.read_line()
                if line is not None:
                    if line.lower() in ['exit', 'quit']:
                        break
                    
                    response = cli.process_command(line)
                    if response:
                        uart.write_line(response)
            except Exception as e:
                uart.write_line(f"Error en CLI: {e}")
            
            # Pequeña pausa para no consumir 100% CPU
            time.sleep(0.001)  # 1ms
            
    except KeyboardInterrupt:
        print("\n\nSistema detenido por usuario")
        
    except Exception as e:
        print(f"\nError inesperado: {e}")
        return 1
    
    finally:
        # Limpieza al salir
        gpio.write_contactor(0)
        gpio.write_led(0)
        print("Sistema limpiamente detenido")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())