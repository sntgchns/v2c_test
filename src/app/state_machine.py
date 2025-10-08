from enum import Enum
import asyncio
from src.drivers.clock import tick_ms
from src.app.led import LedMode

class State(Enum):
    IDLE = 0      # Contactor OFF, LED parpadeo lento (1 Hz)
    READY = 1     # Pilot OK, esperando usuario (LED fijo)
    CHARGING = 2  # Contactor ON, LED parpadeo rápido (4 Hz)
    FAULT = 3     # Contactor OFF, LED doble destello cada segundo

class StateMachine:
    
    def __init__(self, gpio, led_controller, clock=tick_ms):
        self.gpio = gpio
        self.led_controller = led_controller
        self.clock = clock
        
        # Estado actual
        self.state = None
        self.previous_state = None
        
        # Debounce del botón
        self.btn_last_state = 0
        self.btn_last_change_time = 0
        self.btn_debounced = 0
        self.btn_previous_debounced = 0
        self.debounce_time_ms = 20
        
        # Estado anterior de entradas para detectar bordes
        self.pilot_ok_prev = 0
        self.fault_prev = 0
        
        # Configurar estado inicial
        self._enter_state(State.IDLE)
        
    def _enter_state(self, new_state: State):
        if new_state != self.state:
            prev_state_name = "Arranque" if self.state is None else self.state.name
            self.previous_state = self.state
            self.state = new_state
            print(f"Estado: {prev_state_name} -> {self.state.name}")
            
            # Configurar salidas según el estado
            if self.state == State.IDLE:
                self.gpio.write_contactor(0)
                if not self.led_controller.forced_mode:
                    self.led_controller.set_mode(LedMode.SLOW)
                    
            elif self.state == State.READY:
                self.gpio.write_contactor(0)
                if not self.led_controller.forced_mode:
                    self.led_controller.set_mode(LedMode.ON)
                    
            elif self.state == State.CHARGING:
                # Solo activar contactor si no hay fallo
                if not self.gpio.read_fault():
                    self.gpio.write_contactor(1)
                    print("Contactor activado - Iniciando carga")
                else:
                    self.gpio.write_contactor(0)
                    print("Contactor desactivado - Fallo detectado")
                    
                if not self.led_controller.forced_mode:
                    self.led_controller.set_mode(LedMode.FAST)
                    
            elif self.state == State.FAULT:
                self.gpio.write_contactor(0)
                print("Contactor desactivado - Estado de fallo")
                if not self.led_controller.forced_mode:
                    self.led_controller.set_mode(LedMode.FAULT)
    
    def _update_button_debounce(self):
        current_time = self.clock()
        btn_raw = self.gpio.read_btn_raw()
        
        # Si el botón cambió de estado
        if btn_raw != self.btn_last_state:
            self.btn_last_state = btn_raw
            self.btn_last_change_time = current_time
        
        # Si ha pasado suficiente tiempo desde el último cambio
        if current_time - self.btn_last_change_time >= self.debounce_time_ms:
            self.btn_previous_debounced = self.btn_debounced
            self.btn_debounced = btn_raw
    
    def _button_pressed(self) -> bool:
        return self.btn_debounced == 1 and self.btn_previous_debounced == 0
    
    def step(self):
        # Actualizar debounce del botón
        self._update_button_debounce()
        
        # Leer entradas actuales
        pilot_ok = self.gpio.read_pilot_ok()
        fault = self.gpio.read_fault()
        
        # Regla 4: En cualquier estado, si FAULT=1 → FAULT
        if fault and not self.fault_prev:  # Borde ascendente de FAULT
            self._enter_state(State.FAULT)
        
        # Transiciones específicas por estado
        elif self.state == State.IDLE:
            # Regla 2: IDLE → READY cuando PILOT_OK=1
            if pilot_ok and not self.pilot_ok_prev:  # Borde ascendente
                self._enter_state(State.READY)
                
        elif self.state == State.READY:
            # Regla 3: READY → CHARGING al pulsar BTN
            if self._button_pressed():
                self._enter_state(State.CHARGING)
            # Si se pierde PILOT_OK, volver a IDLE
            elif not pilot_ok and self.pilot_ok_prev:  # Borde descendente
                self._enter_state(State.IDLE)
                
        elif self.state == State.CHARGING:
            # Regla 5: CHARGING → IDLE si PILOT_OK=0
            if not pilot_ok and self.pilot_ok_prev:  # Borde descendente
                self._enter_state(State.IDLE)
            # Si aparece fallo durante carga, desactivar contactor
            elif fault:
                self.gpio.write_contactor(0)
                print("Contactor desactivado durante carga - Fallo detectado")
                
        elif self.state == State.FAULT:
            # Regla 4 (continuación): Desde FAULT, al despejarse FAULT y con BTN → IDLE
            if not fault:  # FAULT se despejó
                if self._button_pressed():
                    self._enter_state(State.IDLE)
        
        # Guardar estados anteriores para detectar bordes
        self.pilot_ok_prev = pilot_ok
        self.fault_prev = fault

    async def run(self):
        while True:
            self.step()
            await asyncio.sleep(0.01)  # Ejecutar cada 10ms
    
    def get_state(self) -> State:
        return self.state
    
    def set_input(self, name: str, val: int):
        self.gpio.set_input(name, val)
        print(f"Entrada {name} establecida a {val}")