class GPIO: 
    def __init__(self):
        # Entradas (sensores/botones)
        self._pilot_ok = 0
        self._fault = 0
        self._btn_raw = 0
        
        # Salidas (actuadores)
        self.contactor = 0
        self.led = 0
    
    # Lectura de entradas
    def read_pilot_ok(self) -> int:
        return self._pilot_ok
    
    def read_fault(self) -> int:
        return self._fault
    
    def read_btn_raw(self) -> int:
        return self._btn_raw
    
    def read_led(self) -> int:
        return self.led
    
    # Escritura de salidas
    def write_contactor(self, on: int):
        self.contactor = 1 if on else 0
    
    def write_led(self, on: int):
        self.led = 1 if on else 0
        # --- Magia de simulación ---
        led_symbol = "●" if self.led else "○"
        # Usamos end='\r' para que el cursor vuelva al inicio de la línea
        # y la siguiente impresión la sobrescriba.
        print(f"ESTADO DEL LED: {led_symbol}", end='\r', flush=True)
    
    # Simulación de entradas (para testing/CLI)
    def set_input(self, name: str, val: int):
        """Simula cambio en entradas para testing"""
        if name.upper() == "PILOT_OK":
            self._pilot_ok = 1 if val else 0
        elif name.upper() == "FAULT":
            self._fault = 1 if val else 0
        elif name.upper() == "BTN":
            self._btn_raw = 1 if val else 0
        else:
            raise ValueError(f"Unknown input: {name}")