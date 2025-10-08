import sys
import select
from typing import Optional

class UART:
    def __init__(self):
        self._input_buffer = ""
    
    def has_data(self) -> bool:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            return True
        return False
    
    def read_line(self) -> Optional[str]:
        try:
            if self.has_data():
                # Leer datos disponibles
                data = sys.stdin.read(1)
                if data:
                    self._input_buffer += data
                    
                    # Si encontramos un salto de línea, retornamos la línea
                    if '\n' in self._input_buffer:
                        line, self._input_buffer = self._input_buffer.split('\n', 1)
                        return line.strip()
        except (OSError, IOError):
            # Error de lectura, ignoramos
            pass
        
        return None
    
    def write_line(self, text: str):
        print(text)
        sys.stdout.flush()
    
    def write(self, text: str):
        print(text, end='')
        sys.stdout.flush()