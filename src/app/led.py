from enum import Enum
from src.drivers.clock import tick_ms
import asyncio

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
    
    async def run_led_pattern(self):
        """Ejecuta el patrón del LED"""
        while True:
            current_mode = self.forced_mode if self.forced_mode is not None else self.mode
            if current_mode == LedMode.OFF:
                self.gpio.write_led(0)
                await asyncio.sleep(1)
            elif current_mode == LedMode.SLOW:
                self.gpio.write_led(1)
                await asyncio.sleep(0.5)
                self.gpio.write_led(0)
                await asyncio.sleep(0.5)
            elif current_mode == LedMode.FAST:
                self.gpio.write_led(1)
                await asyncio.sleep(0.125)
                self.gpio.write_led(0)
                await asyncio.sleep(0.125)
            elif current_mode == LedMode.FAULT:
                self.gpio.write_led(1)
                await asyncio.sleep(0.1)
                self.gpio.write_led(0)
                await asyncio.sleep(0.1)
                self.gpio.write_led(1)
                await asyncio.sleep(0.1)
                self.gpio.write_led(0)
                await asyncio.sleep(0.7)
            elif current_mode == LedMode.ON:
                self.gpio.write_led(1)
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.1)  # Modo desconocido, espera breve