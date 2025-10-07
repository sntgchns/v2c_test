from enum import Enum
from src.drivers.clock import tick_ms

class LedMode(Enum):
    OFF = 0      # LED apagado
    SLOW = 1     # Parpadeo lento 1 Hz (500ms ON, 500ms OFF)
    FAST = 2     # Parpadeo rápido 4 Hz (125ms ON, 125ms OFF)  
    FAULT = 3    # Doble destello cada segundo
    ON = 4       # LED fijo encendido

class LedController:
    def __init__(self, gpio, clock=tick_ms):
        self.gpio = gpio
        self.clock = clock
        self.mode = LedMode.OFF
        self.last_tick = 0
        self.pattern_state = 0  # Para patrones complejos como FAULT
        self.forced_mode = None  # Para forzado manual desde CLI
        
    def set_mode(self, mode: LedMode):
        """Establece el modo del LED"""
        self.mode = mode
        self.last_tick = self.clock()
        self.pattern_state = 0
        if mode == LedMode.OFF:
            self.gpio.write_led(0)
        elif mode == LedMode.ON:
            self.gpio.write_led(1)
    
    def force_mode(self, mode: LedMode):
        """Fuerza un modo desde la CLI"""
        self.forced_mode = mode
        self.set_mode(mode)
    
    def clear_force(self):
        """Limpia el forzado manual"""
        self.forced_mode = None
    
    def step(self):
        """Actualiza el estado del LED - debe llamarse en cada tick"""
        current_time = self.clock()
        
        if self.mode == LedMode.OFF:
            # LED apagado
            pass
            
        elif self.mode == LedMode.ON:
            # LED fijo encendido
            pass
            
        elif self.mode == LedMode.SLOW:
            # Parpadeo lento: 1 Hz (periodo 1000ms, 500ms ON, 500ms OFF)
            if current_time - self.last_tick >= 500:
                self.gpio.write_led(not self.gpio.read_led())
                self.last_tick = current_time
                
        elif self.mode == LedMode.FAST:
            # Parpadeo rápido: 4 Hz (periodo 250ms, 125ms ON, 125ms OFF)
            if current_time - self.last_tick >= 125:
                self.gpio.write_led(not self.gpio.read_led())
                self.last_tick = current_time
                
        elif self.mode == LedMode.FAULT:
            # Doble destello cada segundo
            elapsed = current_time - self.last_tick
            
            if self.pattern_state == 0:  # Espera inicial
                if elapsed >= 200:  # 200ms de espera
                    self.gpio.write_led(1)  # Primer destello ON
                    self.pattern_state = 1
                    self.last_tick = current_time
                    
            elif self.pattern_state == 1:  # Primer destello ON
                if elapsed >= 100:  # 100ms encendido
                    self.gpio.write_led(0)  # Primer destello OFF
                    self.pattern_state = 2
                    self.last_tick = current_time
                    
            elif self.pattern_state == 2:  # Pausa entre destellos
                if elapsed >= 100:  # 100ms apagado
                    self.gpio.write_led(1)  # Segundo destello ON
                    self.pattern_state = 3
                    self.last_tick = current_time
                    
            elif self.pattern_state == 3:  # Segundo destello ON
                if elapsed >= 100:  # 100ms encendido
                    self.gpio.write_led(0)  # Segundo destello OFF
                    self.pattern_state = 4
                    self.last_tick = current_time
                    
            elif self.pattern_state == 4:  # Pausa final
                if elapsed >= 500:  # 500ms apagado (total ~1 segundo)
                    self.pattern_state = 0  # Reiniciar patrón
                    self.last_tick = current_time