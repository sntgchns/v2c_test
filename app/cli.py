from src.app.led import LedMode

class CLI:
    def __init__(self, state_machine, gpio, led_controller):
        self.state_machine = state_machine
        self.gpio = gpio
        self.led_controller = led_controller
    
    def process_command(self, line: str) -> str:
        """Procesa un comando CLI y retorna la respuesta"""
        parts = line.strip().upper().split()
        
        if not parts:
            return ""
        
        try:
            if parts == ["GET", "STATE"]:
                return f"STATE: {self.state_machine.get_state().name}"
                
            elif parts == ["GET", "IO"]:
                pilot_ok = self.gpio.read_pilot_ok()
                fault = self.gpio.read_fault()
                btn = self.gpio.read_btn_raw()
                contactor = self.gpio.contactor
                led = self.gpio.led
                return f"PILOT_OK={pilot_ok} FAULT={fault} BTN={btn} CONTACTOR={contactor} LED={led}"
                
            elif len(parts) >= 3 and parts[:2] == ["SET", "LED"]:
                if len(parts) < 3:
                    return "Error: Uso: SET LED <OFF|SLOW|FAST|FAULT|ON>"
                
                try:
                    mode_name = parts[2]
                    if mode_name == "ON":
                        mode = LedMode.ON
                    else:
                        mode = LedMode[mode_name]
                    
                    self.led_controller.force_mode(mode)
                    return f"LED forzado a modo {mode.name}"
                    
                except KeyError:
                    return "Error: Modo LED inválido. Opciones: OFF, SLOW, FAST, FAULT, ON"
                    
            elif len(parts) >= 4 and parts[:2] == ["SET", "IN"]:
                if len(parts) < 4:
                    return "Error: Uso: SET IN <PILOT_OK|FAULT|BTN> <0|1>"
                
                try:
                    input_name = parts[2]
                    value = int(parts[3])
                    
                    if input_name not in ["PILOT_OK", "FAULT", "BTN"]:
                        return "Error: Entrada inválida. Opciones: PILOT_OK, FAULT, BTN"
                    
                    if value not in [0, 1]:
                        return "Error: Valor debe ser 0 o 1"
                    
                    self.state_machine.set_input(input_name, value)
                    return f"Entrada {input_name} establecida a {value}"
                    
                except ValueError:
                    return "Error: Valor debe ser 0 o 1"
                    
            elif parts == ["CLEAR", "LED"]:
                self.led_controller.clear_force()
                return "Forzado de LED liberado"
                
            elif parts == ["HELP"]:
                return self._get_help_text()
                
            else:
                return "Comando no reconocido. Escriba HELP para ver comandos disponibles."
                
        except Exception as e:
            return f"Error procesando comando: {e}"
    
    def _get_help_text(self) -> str:
        """Retorna el texto de ayuda con todos los comandos disponibles"""
        return """Comandos disponibles:
GET STATE                          - Muestra estado actual de la máquina
GET IO                            - Muestra estado de todas las entradas/salidas
SET LED <OFF|SLOW|FAST|FAULT|ON>  - Fuerza patrón del LED
SET IN <PILOT_OK|FAULT|BTN> <0|1> - Simula cambio en entradas
CLEAR LED                         - Libera forzado del LED
HELP                              - Muestra esta ayuda

Estados de la máquina:
IDLE     - Contactor OFF, LED parpadeo lento (1 Hz)
READY    - Pilot OK, esperando usuario (LED fijo)
CHARGING - Contactor ON, LED parpadeo rápido (4 Hz)
FAULT    - Contactor OFF, LED doble destello cada segundo

Transiciones:
1. Arranque → IDLE
2. IDLE → READY cuando PILOT_OK=1
3. READY → CHARGING al pulsar BTN (debounce ≥20 ms)
4. Cualquier estado → FAULT si FAULT=1
5. CHARGING → IDLE si PILOT_OK=0
6. FAULT → IDLE al despejarse FAULT y pulsar BTN"""