# Simulador de Control de Cargador

Simulación en Python de un submódulo de cargador con máquina de estados no bloqueante, debounce de botón y CLI para inspección/forzado.

## Características

### Estados
- **IDLE**: Contactor OFF, LED parpadeo lento (1 Hz)
- **READY**: Pilot OK, esperando usuario (LED fijo encendido)
- **CHARGING**: Contactor ON (si no hay fallo), LED parpadeo rápido (4 Hz)
- **FAULT**: Contactor OFF, LED doble destello cada segundo

### Entradas/Salidas
- **Entradas**: PILOT_OK, FAULT, BTN (botón con debounce ≥20 ms)
- **Salidas**: CONTACTOR, LED

### Reglas de Transición
1. **Arranque** → IDLE
2. **IDLE** → READY cuando PILOT_OK=1
3. **READY** → CHARGING al pulsar BTN (borde ascendente, debounce ≥20 ms)
4. **Cualquier estado** → FAULT si FAULT=1
5. **CHARGING** → IDLE si PILOT_OK=0
6. **FAULT** → IDLE al despejarse FAULT y pulsar BTN

## Uso

### Ejecutar el simulador
```bash
cd /Users/santiago/Desktop/V2C
python3 -m src.main
```

### Comandos CLI
- `GET STATE` - Muestra estado actual de la máquina
- `GET IO` - Muestra estado de todas las entradas/salidas
- `SET LED <OFF|SLOW|FAST|FAULT|ON>` - Fuerza patrón del LED
- `SET IN <PILOT_OK|FAULT|BTN> <0|1>` - Simula cambio en entradas
- `CLEAR LED` - Libera forzado del LED
- `HELP` - Muestra ayuda completa
- `exit` o `quit` - Salir del simulador

### Ejemplos de Uso

#### Secuencia normal de carga:
1. `SET IN PILOT_OK 1` - Simula conexión del piloto → Estado READY
2. `SET IN BTN 1` - Simula pulsación de botón → Estado CHARGING
3. `SET IN BTN 0` - Libera botón
4. `SET IN PILOT_OK 0` - Simula desconexión → Estado IDLE

#### Simulación de fallo:
1. `SET IN FAULT 1` - Simula fallo → Estado FAULT
2. `SET IN FAULT 0` - Despeja fallo
3. `SET IN BTN 1` - Pulsa botón → Estado IDLE

#### Control manual de LED:
1. `SET LED FAST` - Fuerza LED a parpadeo rápido
2. `CLEAR LED` - Libera control manual

## Arquitectura

```
src/
├── main.py                 # Bucle principal y orquestación
├── app/
│   ├── state_machine.py   # Máquina de estados con debounce
│   ├── led.py             # Control de patrones de LED
│   └── cli.py             # Interfaz de comandos
└── drivers/
    ├── gpio.py            # Simulador de entradas/salidas
    ├── clock.py           # Sistema de tiempo no bloqueante
    └── uart.py            # Simulador de comunicación serie
```

## Requisitos Técnicos

- Python 3.10+
- Solo bibliotecas estándar (no dependencias externas)
- Arquitectura por capas (drivers/app/main)
- Sistema no bloqueante (ticks cada ~10 ms)
- Debounce por tiempo (≥20 ms)
- Patrones de LED temporizados
- Logs claros de cambios de estado# V2c_test
