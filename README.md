# Simulador de Control de Cargador v2.0

Simulación asíncrona en Python de un submódulo de cargador con máquina de estados concurrente, debounce de botón y sistema de control visual en tiempo real.

## ✨ Características

### Estados de la Máquina
- **IDLE**: Contactor OFF, LED parpadeo lento (1 Hz)
- **READY**: Pilot OK, esperando usuario (LED fijo encendido)
- **CHARGING**: Contactor ON (si no hay fallo), LED parpadeo rápido (4 Hz)
- **FAULT**: Contactor OFF, LED doble destello cada segundo

### Entradas/Salidas
- **Entradas**: PILOT_OK, FAULT, BTN (botón con debounce ≥20 ms)
- **Salidas**: CONTACTOR, LED (con indicador visual en terminal)

### Reglas de Transición
1. **Arranque** → IDLE
2. **IDLE** → READY cuando PILOT_OK=1
3. **READY** → CHARGING al pulsar BTN (borde ascendente, debounce ≥20 ms)
4. **Cualquier estado** → FAULT si FAULT=1
5. **CHARGING** → IDLE si PILOT_OK=0
6. **FAULT** → IDLE al despejarse FAULT y pulsar BTN

## 🚀 Uso

### Ejecutar el simulador
```bash
cd /Users/santiago/Desktop/v2c_test
python3 main.py
```

### Funcionalidades disponibles

El simulador proporciona:
- ✅ **Visualización en tiempo real** del estado del LED (● encendido / ○ apagado)
- ✅ **Logs automáticos** de todas las transiciones de estado
- ✅ **Sistema concurrente** con máquina de estados y control de LED independientes
- ✅ **API CLI** completa para simulación y testing (ver comandos más abajo)

### Comandos CLI (Programáticos)

La clase `CLI` proporciona una interfaz para testing y simulación:

```python
# Crear instancia CLI
cli = CLI(state_machine, gpio, led_controller)

# Comandos disponibles:
cli.process_command("GET STATE")                   # → "STATE: IDLE"
cli.process_command("GET IO")                      # → "PILOT_OK=0 FAULT=0 BTN=0 CONTACTOR=0 LED=0"
cli.process_command("SET LED FAST")                # Fuerza LED a parpadeo rápido
cli.process_command("SET IN PILOT_OK 1")           # Simula conexión del piloto
cli.process_command("SET IN BTN 1")                # Simula pulsación de botón
cli.process_command("CLEAR LED")                   # Libera forzado del LED
cli.process_command("HELP")                        # Muestra ayuda completa
```

### Ejemplos de Simulación

#### Secuencia normal de carga:
```python
cli.process_command("SET IN PILOT_OK 1")  # → Estado READY
cli.process_command("SET IN BTN 1")       # → Estado CHARGING
cli.process_command("SET IN BTN 0")       # Libera botón
cli.process_command("SET IN PILOT_OK 0")  # → Estado IDLE
```

#### Simulación de fallo:
```python
cli.process_command("SET IN FAULT 1")     # → Estado FAULT
cli.process_command("SET IN FAULT 0")     # Despeja fallo
cli.process_command("SET IN BTN 1")       # → Estado IDLE
```

#### Control manual de LED:
```python
cli.process_command("SET LED FAULT")      # Fuerza patrón de fallo
cli.process_command("CLEAR LED")          # Vuelve al control automático
```

## 🏗️ Arquitectura v2.0

### Estructura del Proyecto
```
main.py                     # Punto de entrada - Sistema asíncrono
src/
├── app/
│   ├── state_machine.py   # Máquina de estados asíncrona con debounce
│   ├── led.py             # Controlador de LED con patrones async
│   └── cli.py             # Interfaz de comandos (API programática)
└── drivers/
    ├── gpio.py            # Simulador de E/S con visualización
    ├── clock.py           # Sistema de tiempo monotónico
    └── uart.py            # Simulador de comunicación serie
```

### Mejoras en v2.0

#### 🔄 Sistema Asíncrono
- **Concurrencia real**: La máquina de estados y el controlador de LED ejecutan en tareas asyncio independientes
- **No bloqueante**: Ambos sistemas corren en paralelo sin interferencias
- **Precisión temporal**: Patrones de LED con timing exacto usando `asyncio.sleep()`

#### 🎯 Control de LED Avanzado
- **Patrones precisos**: 
  - SLOW: 1 Hz (500ms ON/OFF)
  - FAST: 4 Hz (125ms ON/OFF)
  - FAULT: Doble destello con pausa de 700ms
- **Modo forzado**: Control manual desde CLI que sobrescribe el automático
- **Visualización**: Indicador en terminal (● / ○) actualizado en tiempo real

#### 🔧 Máquina de Estados Robusta
- **Debounce por tiempo**: 20ms mínimo para estabilidad
- **Detección de bordes**: Transiciones solo en cambios de estado
- **Logs detallados**: Seguimiento completo de transiciones
- **Manejo de fallos**: Desactivación automática del contactor en caso de fallo

## 📋 Requisitos Técnicos

- **Python 3.10+** (requerido para `asyncio` moderno)
- **Solo bibliotecas estándar** (sin dependencias externas)
- **Arquitectura por capas** (drivers/app/main)
- **Sistema asíncrono** con tareas concurrentes
- **Timing preciso** (10ms para máquina de estados, variable para LED)
- **Debounce temporal** (≥20 ms)
- **Logs estructurados** de cambios de estado

## 🎮 Modo de Operación

1. **Inicio**: El simulador arranca en estado IDLE con LED parpadeando lento
2. **Visualización**: El estado del LED se muestra continuamente en terminal
3. **Simulación**: Utiliza la API CLI para simular entradas y observar comportamiento
4. **Monitoreo**: Los logs muestran todas las transiciones de estado en tiempo real
5. **Salida**: Ctrl+C para terminar limpiamente el simulador

## 🧪 Testing y Desarrollo

El sistema está diseñado para testing fácil mediante la API CLI:

```python
# Ejemplo de test automatizado
def test_charging_sequence():
    # Setup
    cli = CLI(state_machine, gpio, led_controller)
    
    # Test normal charging
    assert "IDLE" in cli.process_command("GET STATE")
    cli.process_command("SET IN PILOT_OK 1")
    assert "READY" in cli.process_command("GET STATE")
    cli.process_command("SET IN BTN 1")
    assert "CHARGING" in cli.process_command("GET STATE")
```

---

## 🔗 Enlaces

- **Repositorio**: v2c_test
- **Versión**: 2.0 (Sistema Asíncrono)
- **Autor**: Santiago
- **Fecha**: 7 de Octubre 2025
