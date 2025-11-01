# Guía de Desarrollo de Plugins para DGT Centaur Mods

## Índice
1. [Introducción](#introducción)
2. [Estructura Básica](#estructura-básica)
3. [Callbacks Disponibles](#callbacks-disponibles)
4. [API de Centaur](#api-de-centaur)
5. [Ejemplos Completos](#ejemplos-completos)
6. [Mejores Prácticas](#mejores-prácticas)

---

## Introducción

Los plugins para DGT Centaur Mods permiten extender la funcionalidad del tablero de ajedrez DGT Centaur. Cada plugin hereda de la clase base `Plugin` y puede implementar variantes de ajedrez, juegos educativos, bots personalizados, y más.

### Requisitos Previos
- Conocimientos básicos de Python
- Familiaridad con la librería `python-chess`
- Comprensión del sistema DGT Centaur

---

## Estructura Básica

### 1. Estructura de Archivos

Todos los plugins deben ubicarse en el directorio:
```
DGTCentaurMods/opt/DGTCentaurMods/plugins/
```

**Regla importante**: El nombre del archivo debe coincidir exactamente con el nombre de la clase.
- Archivo: `MiPlugin.py`
- Clase: `class MiPlugin(Plugin):`

### 2. Plantilla Básica

```python
# This file is part of the DGTCentaur Mods open source software
# ( https://github.com/Alistair-Crompton/DGTCentaurMods )
# [Licencia GPL v3 - incluir el header completo]

import chess
from DGTCentaurMods.classes.Plugin import Plugin, Centaur
from DGTCentaurMods.consts import Enums, fonts
from typing import Optional

class MiPlugin(Plugin):
    """
    Descripción de lo que hace tu plugin.
    """

    def __init__(self, id: str):
        """Constructor del plugin."""
        super().__init__(id)
        # Inicializar variables del plugin aquí
        self.mi_variable = None

    def start(self):
        """
        Invocado automáticamente cuando el usuario lanza el plugin.
        """
        super().start()
        # Configuración inicial aquí

    def stop(self):
        """
        Invocado automáticamente cuando el usuario detiene el plugin.
        """
        super().stop()
        # Limpieza de recursos aquí

    def splash_screen(self) -> bool:
        """
        Pantalla inicial mostrada al iniciar el plugin.
        Retorna True si quieres activar la splash screen.
        """
        Centaur.clear_screen()
        Centaur.print("MI PLUGIN", font=fonts.DIGITAL_FONT, row=2)
        Centaur.print("Push PLAY", row=5)
        Centaur.print("to start!")
        return True

    def on_start_callback(self, key: Enums.Btn) -> bool:
        """
        Invocado después de la splash screen cuando se presiona un botón.
        Retorna True para indicar que el juego ha comenzado.
        """
        if key == Enums.Btn.PLAY:
            # Iniciar el juego
            return True
        return False
```

---

## Callbacks Disponibles

### 1. `splash_screen() -> bool`

Muestra una pantalla inicial cuando se lanza el plugin.

**Retorno:**
- `True`: Activa la splash screen (el usuario debe presionar un botón para continuar)
- `False`: Salta directo al juego

**Ejemplo:**
```python
def splash_screen(self) -> bool:
    Centaur.clear_screen()
    Centaur.print("RANDOM BOT", row=2)
    Centaur.print("Push PLAY to start", row=5)
    return True
```

---

### 2. `on_start_callback(key: Enums.Btn) -> bool`

Invocado cuando el usuario presiona un botón después de la splash screen.

**Parámetros:**
- `key`: El botón presionado (Enums.Btn.PLAY, UP, DOWN, TICK, etc.)

**Retorno:**
- `True`: El juego ha comenzado
- `False`: Esperar más acciones del usuario

**Ejemplo:**
```python
def on_start_callback(self, key: Enums.Btn) -> bool:
    if key == Enums.Btn.UP:
        self.HUMAN_COLOR = chess.WHITE
    elif key == Enums.Btn.DOWN:
        self.HUMAN_COLOR = chess.BLACK
        Centaur.reverse_board()
    else:
        return False  # Esperar elección de color

    # Iniciar partida
    Centaur.start_game(
        white="You",
        black="Bot",
        event="My Event",
        flags=Enums.BoardOption.CAN_UNDO_MOVES
    )
    return True
```

---

### 3. `key_callback(key: Enums.Btn) -> bool`

Invocado cada vez que el usuario presiona un botón (excepto BACK, que se maneja automáticamente).

**Parámetros:**
- `key`: El botón presionado

**Retorno:**
- `True`: La tecla ha sido manejada por el plugin
- `False`: La tecla puede ser manejada por el motor del juego

**Botones disponibles:**
```python
Enums.Btn.HELP    # Botón de ayuda
Enums.Btn.TICK    # Botón de tick/confirmación
Enums.Btn.UP      # Botón arriba
Enums.Btn.DOWN    # Botón abajo
Enums.Btn.PLAY    # Botón play
```

**Ejemplo:**
```python
def key_callback(self, key: Enums.Btn):
    if key == Enums.Btn.HELP:
        Centaur.hint()  # Mostrar pista usando Stockfish
        return True
    return False
```

---

### 4. `event_callback(event: Enums.Event, outcome: Optional[chess.Outcome])`

Invocado cuando el estado del motor del juego cambia.

**Eventos disponibles:**
```python
Enums.Event.NEW_GAME      # Nueva partida iniciada
Enums.Event.RESUME_GAME   # Partida reanudada
Enums.Event.PLAY          # Turno de juego
Enums.Event.REQUEST_DRAW  # Solicitud de tablas
Enums.Event.RESIGN_GAME   # Rendición
Enums.Event.QUIT          # Salir del plugin
Enums.Event.TERMINATION   # Final de la partida
```

**Ejemplo:**
```python
def event_callback(self, event: Enums.Event, outcome: Optional[chess.Outcome]):
    if event == Enums.Event.QUIT:
        self.stop()

    if event == Enums.Event.TERMINATION:
        if outcome.winner == chess.WHITE:
            Centaur.sound(Enums.Sound.VICTORY)
        else:
            Centaur.sound(Enums.Sound.GAME_LOST)

    if event == Enums.Event.PLAY:
        turn = self.chessboard.turn
        current_player = "You" if turn == chess.WHITE else "Bot"
        Centaur.header(f"{current_player} {'W' if turn == chess.WHITE else 'B'}")

        if turn == (not self.HUMAN_COLOR):
            # Turno de la computadora
            self.computer_move()
```

---

### 5. `move_callback(uci_move: str, san_move: str, color: chess.Color, field_index: chess.Square) -> bool`

Invocado cuando el jugador mueve físicamente una pieza.

**Parámetros:**
- `uci_move`: Movimiento en notación UCI (ej: "e2e4")
- `san_move`: Movimiento en notación SAN (ej: "e4")
- `color`: Color que movió (chess.WHITE o chess.BLACK)
- `field_index`: Índice del cuadro destino (0-63)

**Retorno:**
- `True`: Movimiento aceptado
- `False`: Movimiento rechazado

**Ejemplo:**
```python
def move_callback(self, uci_move: str, san_move: str, color: chess.Color, field_index: chess.Square):
    # Validar movimiento personalizado
    if color == self.HUMAN_COLOR:
        # Evaluar posición después del movimiento
        self.evaluate_position()
    return True  # Aceptar movimiento
```

---

### 6. `undo_callback(uci_move: str, san_move: str, field_index: chess.Square)`

Invocado cuando el jugador retrocede un movimiento.

**Ejemplo:**
```python
def undo_callback(self, uci_move: str, san_move: str, field_index: chess.Square):
    # Re-evaluar la posición
    self.evaluate_position()
```

---

### 7. `field_callback(square: str, field_action: Enums.PieceAction, web_move: bool)`

Invocado cuando el jugador interactúa con una casilla del tablero.

**Parámetros:**
- `square`: Nombre del cuadro (ej: "e4")
- `field_action`: Acción realizada (LIFT o PLACE)
- `web_move`: Si el movimiento viene de la interfaz web

**Acciones disponibles:**
```python
Enums.PieceAction.LIFT   # Pieza levantada
Enums.PieceAction.PLACE  # Pieza colocada
```

**Ejemplo:**
```python
def field_callback(self, square: str, field_action: Enums.PieceAction, web_move: bool):
    if field_action == Enums.PieceAction.PLACE:
        # Verificar si es el cuadro correcto
        if square == self.target_square:
            Centaur.sound(Enums.Sound.CORRECT_MOVE)
        else:
            Centaur.sound(Enums.Sound.WRONG_MOVE)
```

---

## API de Centaur

La clase `Centaur` proporciona una API estática para interactuar con el hardware y el sistema.

### Display (Pantalla)

#### `Centaur.clear_screen()`
Limpia la pantalla e-paper.

```python
Centaur.clear_screen()
```

#### `Centaur.print(text: str, row: float = -1, font=fonts.MAIN_FONT)`
Imprime texto en la pantalla.

**Parámetros:**
- `text`: Texto a mostrar
- `row`: Fila donde mostrar (opcional, auto-incrementa)
- `font`: Fuente a usar

**Fuentes disponibles:**
```python
fonts.MAIN_FONT          # Fuente principal
fonts.DIGITAL_FONT       # Fuente digital grande
fonts.SMALL_DIGITAL_FONT # Fuente digital pequeña
fonts.MEDIUM_MAIN_FONT   # Fuente mediana
fonts.SMALL_MAIN_FONT    # Fuente pequeña
```

**Ejemplo:**
```python
Centaur.print("MI PLUGIN", font=fonts.DIGITAL_FONT, row=2)
Centaur.print("Línea 1")
Centaur.print("Línea 2")  # Se auto-incrementa la fila
```

#### `Centaur.header(text: str, web_text: str = None)`
Muestra un encabezado en la partida.

```python
Centaur.header("You W")
Centaur.header(
    text="You W",
    web_text="turn → You (WHITE)"
)
```

#### `Centaur.messagebox(text_lines: Tuple[str,...], row: float = 8, tick_button: bool = False)`
Muestra un cuadro de mensaje.

```python
Centaur.messagebox(("Game Over!", "White wins"), row=8)
```

#### `Centaur.print_button_label(button: Enums.Btn, x: int, row: float = -1, text: str = "")`
Muestra una etiqueta de botón.

```python
Centaur.print_button_label(Enums.Btn.UP, row=8, x=6, text="Play white")
Centaur.print_button_label(Enums.Btn.DOWN, row=9, x=6, text="Play black")
```

---

### LEDs del Tablero

#### `Centaur.flash(square: str)`
Destella un LED en una casilla.

```python
Centaur.flash("e4")
```

#### `Centaur.light_move(uci_move: str, web: bool = True)`
Ilumina un movimiento (origen → destino).

```python
Centaur.light_move("e2e4")
```

#### `Centaur.light_moves(uci_moves: Tuple[str], web: bool = True)`
Ilumina múltiples movimientos.

```python
Centaur.light_moves(("e2e4", "d2d4", "g1f3"))
```

#### `Centaur.lights_off()`
Apaga todos los LEDs.

```python
Centaur.lights_off()
```

---

### Sonidos

#### `Centaur.sound(sound: Enums.Sound, override: Optional[Enums.Sound] = None)`
Reproduce un sonido.

**Sonidos disponibles:**
```python
Enums.Sound.MUSIC           # Música
Enums.Sound.WRONG_MOVE      # Movimiento incorrecto
Enums.Sound.CORRECT_MOVE    # Movimiento correcto
Enums.Sound.TAKEBACK_MOVE   # Retroceder movimiento
Enums.Sound.COMPUTER_MOVE   # Movimiento de computadora
Enums.Sound.POWER_OFF       # Apagar
Enums.Sound.VICTORY         # Victoria
Enums.Sound.GAME_LOST       # Derrota
Enums.Sound.VERY_GOOD_MOVE  # Muy buen movimiento
Enums.Sound.BAD_MOVE        # Mal movimiento
```

**Ejemplo:**
```python
Centaur.sound(Enums.Sound.CORRECT_MOVE)
Centaur.sound(Enums.Sound.VICTORY)
```

---

### Motor de Ajedrez

#### `Centaur.start_game(...)`
Inicia una nueva partida.

```python
Centaur.start_game(
    white="You",              # Nombre jugador blancas
    black="Bot",              # Nombre jugador negras
    event="My Event 2024",    # Nombre del evento
    site="",                  # Sitio (opcional)
    flags=Enums.BoardOption.CAN_UNDO_MOVES | Enums.BoardOption.CAN_FORCE_MOVES
)
```

**Opciones de tablero (flags):**
```python
Enums.BoardOption.CAN_FORCE_MOVES      # Permitir forzar movimientos
Enums.BoardOption.CAN_UNDO_MOVES       # Permitir deshacer
Enums.BoardOption.DB_RECORD_DISABLED   # Deshabilitar grabación BD
Enums.BoardOption.EVALUATION_DISABLED  # Deshabilitar evaluación
Enums.BoardOption.PARTIAL_PGN_DISABLED # Deshabilitar PGN parcial
Enums.BoardOption.RESUME_DISABLED      # Deshabilitar reanudar
```

Puedes combinar flags usando el operador `|`:
```python
flags = Enums.BoardOption.CAN_UNDO_MOVES | Enums.BoardOption.CAN_FORCE_MOVES
```

#### `Centaur.play_computer_move(uci_move: str)`
Ejecuta un movimiento de la computadora.

```python
Centaur.play_computer_move("e2e4")
```

#### `Centaur.hint()`
Muestra una pista usando el motor de ajedrez.

```python
Centaur.hint()
```

#### `Centaur.set_main_chess_engine(engine_name: str)`
Configura el motor de ajedrez principal.

```python
Centaur.set_main_chess_engine("ct800")     # Motor CT800
Centaur.set_main_chess_engine("stockfish") # Stockfish
```

#### `Centaur.configure_main_chess_engine(options: dict)`
Configura opciones del motor.

```python
Centaur.configure_main_chess_engine({"UCI_Elo": 1800})
```

#### `Centaur.request_chess_engine_move(callback, time: int = 5)`
Solicita al motor que calcule un movimiento (asíncrono).

```python
def on_move_calculated(result: TPlayResult):
    Centaur.play_computer_move(str(result.move))

Centaur.request_chess_engine_move(on_move_calculated, time=3)
```

#### `Centaur.request_chess_engine_evaluation(callback, time: int = 2, multipv: int = 1)`
Solicita evaluación de la posición (asíncrono).

```python
def on_evaluation(results: Tuple[TAnalyseResult, ...]):
    result = results[0]
    score = result.score.pov(chess.WHITE)
    print(f"Evaluación: {score}")

Centaur.request_chess_engine_evaluation(on_evaluation, time=2)
```

---

### Utilidades

#### `Centaur.reverse_board(value: bool = True)`
Invierte la visualización del tablero.

```python
Centaur.reverse_board()  # Invertir
Centaur.reverse_board(False)  # Normal
```

#### `Centaur.delayed_call(call: callable, delay: int)`
Ejecuta una función después de un delay (milisegundos).

```python
def mi_funcion():
    print("Ejecutado después de 2 segundos")

Centaur.delayed_call(mi_funcion, 2000)
```

#### `self.chessboard`
Accede al tablero de ajedrez actual (objeto `chess.Board`).

```python
# Ver turno actual
turn = self.chessboard.turn

# Ver movimientos legales
legal_moves = list(self.chessboard.legal_moves)

# Ver FEN actual
fen = self.chessboard.fen()

# Verificar fin de juego
is_over = self.chessboard.is_game_over()
```

---

## Ejemplos Completos

### Ejemplo 1: Bot Simple que Juega Movimientos Aleatorios

```python
import chess, random
from DGTCentaurMods.classes.Plugin import Plugin, Centaur
from DGTCentaurMods.consts import Enums, fonts
from typing import Optional

HUMAN_COLOR = chess.WHITE

class RandomBot(Plugin):

    def key_callback(self, key: Enums.Btn):
        if key == Enums.Btn.HELP:
            Centaur.hint()
            return True
        return False

    def event_callback(self, event: Enums.Event, outcome: Optional[chess.Outcome]):
        if event == Enums.Event.QUIT:
            self.stop()

        if event == Enums.Event.PLAY:
            turn = self.chessboard.turn
            current_player = "You" if turn == chess.WHITE else "Random bot"
            Centaur.header(f"{current_player} {'W' if turn == chess.WHITE else 'B'}")

            if turn == (not HUMAN_COLOR):
                # Elegir movimiento aleatorio
                uci_move = str(random.choice(list(self.chessboard.legal_moves)))
                Centaur.play_computer_move(uci_move)

    def on_start_callback(self, key: Enums.Btn) -> bool:
        Centaur.start_game(
            white="You",
            black="Random bot",
            event="Random Bot Event",
            flags=Enums.BoardOption.CAN_UNDO_MOVES
        )
        return True

    def splash_screen(self) -> bool:
        Centaur.clear_screen()
        Centaur.print("RANDOM", row=2)
        Centaur.print("BOT", font=fonts.DIGITAL_FONT, row=4)
        Centaur.print("Push PLAY", row=8)
        Centaur.print("to start")
        return True
```

---

### Ejemplo 2: Juego Educativo - Squiz (Encuentra la Casilla)

```python
import chess, random
from DGTCentaurMods.classes.Plugin import Plugin, Centaur
from DGTCentaurMods.consts import Enums, fonts

QUESTIONS_COUNT = 10

class Squiz(Plugin):

    def __init__(self, id: str):
        super().__init__(id)
        self.initialize()

    def initialize(self):
        self._qindex = 0
        self._bonus = QUESTIONS_COUNT * 3
        Centaur.pause_plugin()

    def game_over(self):
        Centaur.clear_screen()
        Centaur.print("GAME OVER", row=2, font=fonts.DIGITAL_FONT)

        score = int(self._bonus * 100 / (QUESTIONS_COUNT * 3))
        Centaur.print(f"SCORE: {score}%", row=5, font=fonts.DIGITAL_FONT)
        Centaur.print("Press PLAY to retry!", row=8)

        self.initialize()

    def generate_question(self):
        self._qindex += 1

        if self._qindex == QUESTIONS_COUNT + 1:
            self.game_over()
            return

        Centaur.clear_screen()

        # Generar casilla aleatoria
        self._random_square = chess.square_name(random.randint(0, 63))

        Centaur.print(f"Question {self._qindex}", row=2)
        Centaur.print("Place a piece on", row=5)
        Centaur.print(self._random_square, font=fonts.DIGITAL_FONT)

    def key_callback(self, key: Enums.Btn):
        if key == Enums.Btn.HELP:
            Centaur.sound(Enums.Sound.TAKEBACK_MOVE)
            Centaur.flash(self._random_square)

    def field_callback(self, square: str, field_action: Enums.PieceAction, web_move: bool):
        if field_action == Enums.PieceAction.PLACE:
            Centaur.flash(square)

            if self._random_square == square:
                Centaur.sound(Enums.Sound.CORRECT_MOVE)
                self.generate_question()
            else:
                Centaur.sound(Enums.Sound.WRONG_MOVE)
                Centaur.print("WRONG!", row=11)
                self._bonus -= 1

                if self._bonus == 0:
                    self.game_over()

    def on_start_callback(self, key: Enums.Btn) -> bool:
        Centaur.sound(Enums.Sound.COMPUTER_MOVE)
        self.generate_question()
        return True

    def splash_screen(self) -> bool:
        Centaur.clear_screen()
        Centaur.print("SQUIZ", font=fonts.DIGITAL_FONT, row=2)
        Centaur.print("Push PLAY to start!", row=5)
        return True
```

---

### Ejemplo 3: Bot Adaptativo con Motor de Ajedrez

```python
import chess
from DGTCentaurMods.classes.Plugin import Plugin, Centaur, TPlayResult, TAnalyseResult
from DGTCentaurMods.consts import Enums, fonts
from typing import Optional, Tuple

class AdaptativeBot(Plugin):

    def __init__(self, id: str):
        super().__init__(id)
        self.HUMAN_COLOR = chess.WHITE
        self._elo = 1500

    def start(self):
        super().start()
        Centaur.set_main_chess_engine("stockfish")
        self._adjust_engine_level(1500)

    def _adjust_engine_level(self, elo: int):
        if self._elo != elo:
            Centaur.configure_main_chess_engine({"UCI_Elo": elo})
            self._elo = elo

    def _evaluate_and_adjust(self):
        def on_evaluation(results: Tuple[TAnalyseResult, ...]):
            result = results[0]
            score = result.score.pov(self.HUMAN_COLOR)

            # Obtener evaluación en centipawns
            cp = score.score()
            if cp:
                # Ajustar nivel según evaluación
                if cp > 200:  # Jugador gana
                    new_elo = min(2400, self._elo + 100)
                elif cp < -200:  # Jugador pierde
                    new_elo = max(1000, self._elo - 100)
                else:
                    new_elo = 1500

                self._adjust_engine_level(new_elo)

        Centaur.request_chess_engine_evaluation(on_evaluation, time=2)

    def event_callback(self, event: Enums.Event, outcome: Optional[chess.Outcome]):
        if event == Enums.Event.QUIT:
            self.stop()

        if event == Enums.Event.TERMINATION:
            if outcome.winner == self.HUMAN_COLOR:
                Centaur.sound(Enums.Sound.VICTORY)
            else:
                Centaur.sound(Enums.Sound.GAME_LOST)

        if event == Enums.Event.PLAY:
            turn = self.chessboard.turn
            current_player = "You" if turn == self.HUMAN_COLOR else "Bot"
            Centaur.header(f"{current_player} {'W' if turn == chess.WHITE else 'B'}")

            if turn == (not self.HUMAN_COLOR):
                def on_move(result: TPlayResult):
                    Centaur.play_computer_move(str(result.move))
                    self._evaluate_and_adjust()

                Centaur.request_chess_engine_move(on_move, time=3)

    def move_callback(self, uci_move: str, san_move: str, color: chess.Color, field_index: chess.Square):
        if color == self.HUMAN_COLOR:
            self._evaluate_and_adjust()
        return True

    def on_start_callback(self, key: Enums.Btn) -> bool:
        if key == Enums.Btn.UP:
            self.HUMAN_COLOR = chess.WHITE
        elif key == Enums.Btn.DOWN:
            self.HUMAN_COLOR = chess.BLACK
            Centaur.reverse_board()
        else:
            return False

        Centaur.start_game(
            white="You" if self.HUMAN_COLOR == chess.WHITE else "Adaptive Bot",
            black="Adaptive Bot" if self.HUMAN_COLOR == chess.WHITE else "You",
            event="Adaptive Bot Challenge",
            flags=Enums.BoardOption.CAN_UNDO_MOVES | Enums.BoardOption.CAN_FORCE_MOVES
        )
        return True

    def splash_screen(self) -> bool:
        Centaur.clear_screen()
        Centaur.print("ADAPTIVE BOT", font=fonts.DIGITAL_FONT, row=2)
        Centaur.print_button_label(Enums.Btn.UP, row=6, x=6, text="Play white")
        Centaur.print_button_label(Enums.Btn.DOWN, row=7, x=6, text="Play black")
        return True
```

---

## Mejores Prácticas

### 1. Nomenclatura
- **Archivo y clase deben coincidir**: `MiPlugin.py` → `class MiPlugin(Plugin):`
- Usar CamelCase para nombres de clases
- Nombres descriptivos que indiquen la funcionalidad

### 2. Gestión de Recursos
- Siempre llamar `super().start()` y `super().stop()`
- Limpiar recursos en `stop()` (motores de ajedrez, timers, etc.)
- No mantener estados entre diferentes instancias del plugin

### 3. Manejo de Eventos
```python
def event_callback(self, event: Enums.Event, outcome: Optional[chess.Outcome]):
    # Siempre manejar QUIT
    if event == Enums.Event.QUIT:
        self.stop()

    # Manejar TERMINATION para fin de juego
    if event == Enums.Event.TERMINATION:
        # Mostrar resultado
        pass
```

### 4. Callbacks Asíncronos
Cuando uses motores de ajedrez, los callbacks son asíncronos:

```python
def event_callback(self, event: Enums.Event, outcome: Optional[chess.Outcome]):
    if event == Enums.Event.PLAY:
        if self.chessboard.turn == computer_turn:
            # Callback será invocado cuando el motor termine
            def on_move_ready(result: TPlayResult):
                Centaur.play_computer_move(str(result.move))

            Centaur.request_chess_engine_move(on_move_ready, time=5)
```

### 5. Feedback al Usuario
- Usar sonidos apropiados para cada acción
- Actualizar el display regularmente con `Centaur.header()`
- Iluminar LEDs para guiar al usuario
- Proporcionar feedback visual y auditivo

### 6. Licencia
Incluir siempre el header de licencia GPL v3 al inicio del archivo:

```python
# This file is part of the DGTCentaur Mods open source software
# ( https://github.com/Alistair-Crompton/DGTCentaurMods )
#
# DGTCentaur Mods is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
# [...]
```

### 7. Testing
- Probar todos los callbacks
- Verificar el comportamiento con movimientos ilegales
- Probar el botón BACK en diferentes estados
- Verificar la limpieza de recursos al salir

### 8. Documentación
- Documentar el propósito del plugin en el docstring de la clase
- Comentar lógica compleja
- Incluir ejemplos de uso si el plugin tiene configuración especial

---

## Recursos Adicionales

- **python-chess**: https://python-chess.readthedocs.io/
- **Repositorio DGTCentaurMods**: https://github.com/Alistair-Crompton/DGTCentaurMods
- **Plugins existentes**: Ver los ejemplos en el directorio `plugins/`

---

## Solución de Problemas

### El plugin no aparece en el menú
- Verificar que el nombre del archivo coincida con la clase
- Asegurar que la clase herede de `Plugin`
- Revisar errores de sintaxis en el código

### Los LEDs no se iluminan
- Usar `Centaur.flash(square)` o `Centaur.light_move(uci_move)`
- Apagar LEDs con `Centaur.lights_off()` cuando sea necesario

### El motor de ajedrez no funciona
- Inicializar con `Centaur.set_main_chess_engine(engine_name)`
- Verificar que el motor esté disponible en el sistema
- Usar callbacks correctamente para operaciones asíncronas

### La pantalla no se actualiza
- Llamar `Centaur.clear_screen()` antes de dibujar
- Usar `row` para posicionar texto correctamente
- Verificar que el texto no sea demasiado largo

---

¡Feliz desarrollo de plugins! 🎉
