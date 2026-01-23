# DGTCentaurMods - Claude Developer Guide

## Projekt-Kontext

**DGT Centaur** ist ein elektronisches Schachbrett mit einem Raspberry Pi Zero 2 W im Inneren. Dieses Projekt erweitert die ursprüngliche Firmware um zusätzliche Features wie Web-Interface, Plugins und verschiedene Spielmodi.

**Hardware-Abhängigkeiten:**
- Raspberry Pi Zero 2 W (oder Zero W)
- Waveshare e-Paper Display (2.9")
- DGT Centaur Schachbrett
- Serielle Kommunikation mit dem Board

**Wichtige Einschränkung:** Das Projekt bricht die Produktgarantie, da der originale Raspberry Pi ersetzt werden muss.

## Architektur-Übersicht

### System-Komponenten
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DGT Centaur   │    │   Raspberry Pi  │    │   Web Browser   │
│     Board       │◄──►│   (main.py)     │◄──►│   (app.py)      │
│                 │    │                 │    │                 │
│ • LED-Steuerung │    │ • Game Engine   │    │ • WebSocket     │
│ • Tasten-Events │    │ • Plugin System │    │ • Vue.js UI     │
│ • Stück-Erkennung│    │ • DB Storage   │    │ • Live Control  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Kommunikationsfluss
1. **Board Events** → `CentaurBoard` → `main.py` → Plugin/Game Engine
2. **Web Requests** → `app.py` → WebSocket → `main.py` → Board
3. **Plugin Actions** → `Plugin` → `Centaur` API → Hardware

### Thread-Modell
- **Main Thread**: UI-Loop, Menü-Navigation
- **Game Thread**: Spiel-Logik, Engine-Kommunikation
- **Evaluation Thread**: Positionsbewertung
- **Web Thread**: Flask-Server mit SocketIO

## Kern-Komponenten Mapping

### Entry Points
- **`main.py`**: Haupteinstiegspunkt, Menü-System, Plugin-Loader
- **`app.py`**: Flask-Webserver, WebSocket-Handler

### Hardware-Abstraktion
- **`CentaurBoard`**: Serielle Kommunikation, LED-Steuerung, Tasten-Events
- **`CentaurScreen`**: e-Paper Display, Text/FEN-Rendering
- **`CentaurConfig`**: Konfiguration (INI-Dateien, Settings)

### Spiel-Logik
- **`GameFactory`**: Standard-Schach Engine
- **`GameFactoryChess960`**: Chess960-spezifische Engine (FRC-Unterstützung)
- **`ChessEngine`**: UCI-Engine Wrapper (Stockfish, etc.)

### Plugin-System
- **`Plugin`**: Basis-Klasse für alle Plugins
- **`Centaur`**: API für Plugin-Entwickler

### Datenhaltung
- **`DAL`**: SQLite Database Access Layer
- **`models.py`**: Datenbank-Schema

## Chess960 Plugin - Detaillierte Analyse

### Übersicht
Das Chess960 Plugin ermöglicht das Spielen von Fischer Random Chess (Chess960/FRC) mit verschiedenen Engines. Es ist das aktuell aktiv entwickelte Feature.

### Dateien
- **`plugins/Chess960.py`**: Plugin-Hauptlogik
- **`classes/GameFactoryChess960.py`**: Chess960-spezifische Game Engine
- **`engines-chess960/`**: FRC-kompatible Engine-Binaries

### Plugin-Architektur
```python
class Chess960(Plugin):
    def __init__(self, id: str):
        # Menu state management
        self._menu_state = None  # 'engine' | 'strength' | None
        self._engines = []       # Available FRC engines
        self._current_index = 0  # Menu navigation
        self._selected_engine = None
        self._strengths = []     # Engine strength levels
        self._chess_engine = None
        self._chess960_fen = None  # Current position FEN
```

### Wichtige Workflows

#### 1. Engine-Scan und FRC-Kompatibilität
```python
def _scan_frc_engines(self):
    """Find engines that support UCI_Chess960"""
    for f in os.scandir(consts.ENGINES_DIRECTORY):
        if f.name.endswith('.uci'):
            try:
                engine = ChessEngine.get(binary_path)
                engine.configure({"UCI_Chess960": True})
                # Test FRC capability
                test_board = chess.Board.from_chess960_pos(0)
                engine.analyse(test_board, chess.engine.Limit(time=0.1))
                engines.append({'name': f.name[:-4], 'path': f.path})
            except:
                # Engine not FRC capable
                pass
```

#### 2. Spiel-Start mit zufälliger Position
```python
def _start_game_with_strength(self):
    # Generate random Chess960 position (0-959)
    chess960_pos = random.randint(0, 959)
    board = chess.Board.from_chess960_pos(chess960_pos)
    self._chess960_fen = board.fen()

    # Initialize Chess960 game engine
    self._start_game(
        event="Chess960 Event",
        white="You",
        black=f"{engine_name} {strength}",
        custom_fen=self._chess960_fen
    )
```

#### 3. Chess960-spezifische GameFactory
```python
class Engine(GameFactory.Engine):
    def __init__(self, ..., custom_fen=None):
        # Initialize with Chess960 FEN
        self._original_fen = custom_fen
        self._chessboard = chess.Board(custom_fen, chess960=True)
        self._chessboard.chess960 = True
```

### Kritische Chess960-spezifische Änderungen

#### Rochade-Handling
- Standard-Rochade funktioniert nicht in FRC
- GameFactoryChess960 behandelt alle Rochaden als normale Züge
- `_last_move_was_castling` Tracking für Takeback

#### Position-Reset
- Board-Erkennung prüft auf `BOARD_START_STATE` für Reset
- Bei Reset wird zur ursprünglichen Chess960-FEN zurückgesetzt

#### Engine-Kommunikation
- Engines müssen `UCI_Chess960: True` unterstützen
- Strength-Konfiguration aus UCI-Dateien

### Häufige Aufgaben für Chess960-Entwicklung

#### Neue Engine hinzufügen
1. UCI-Datei in `engines-chess960/` ablegen
2. FRC-Binary in `engines-chess960/` kopieren
3. Plugin scannt automatisch neue Engines

#### Strength-Level konfigurieren
```ini
# engines-chess960/stockfish.uci
[Beginner]
UCI_Elo = 1000
UCI_LimitStrength = true

[Expert]
UCI_Elo = 2000
UCI_LimitStrength = true
```

#### Debugging Chess960-Spiele
- Log-Ausgaben: `Chess960 Engine: result=...`
- FEN-Validierung: `chess960=True` Parameter
- Rochade-Erkennung: `was_last_move_castling()`

## Wichtige Workflows

### Zug-Verarbeitung
1. **Board Event** → `CentaurBoard.read_keys()`
2. **Field Callback** → `PieceHandler.__call__()`
3. **Move Validation** → `PieceHandler._interpret_actions()`
4. **Engine Response** → `ChessEngine.play()` oder `analyse()`
5. **UI Update** → WebSocket broadcast

### Plugin-Entwicklung
1. Erbe von `Plugin` Klasse
2. Implementiere `key_callback()`, `event_callback()`, etc.
3. Verwende `Centaur` API für Hardware-Zugriff
4. Plugin wird automatisch erkannt (Dateiname = Klassenname)

### Web-Interface Integration
1. **Client Request** → `app.py.on_web_message()`
2. **Socket Forward** → `main.py._on_socket_request()`
3. **Plugin Callback** → `Chess960.on_socket_request()`
4. **Hardware Action** → `CentaurBoard.push_button()`

## Code-Konventionen

### Naming
- **Klassen**: PascalCase (`CentaurBoard`, `Chess960`)
- **Methoden**: snake_case (`get_board_state()`, `_scan_frc_engines()`)
- **Konstanten**: UPPER_CASE (`BOARD_START_STATE`)
- **Dateien**: PascalCase für Klassen, snake_case für Module

### Callbacks
- `key_callback(key: Enums.Btn)`: Tasten-Events
- `event_callback(event: Enums.Event, outcome)`: Spiel-Events
- `move_callback(uci_move, san_move, color, field_index)`: Zug-Events
- `socket_callback(data, socket)`: WebSocket-Events

### Error Handling
- Alle Callbacks in `try/except` wrappen
- Exceptions an Web-UI senden: `SOCKET.send_web_message({"script_output": Log.last_exception()})`
- Plugin bei Fehlern stoppen: `self.stop()`

## Debugging-Hinweise

### Log-Dateien
- **Location**: `/opt/DGTCentaurMods/log/`
- **Levels**: `Log.info()`, `Log.debug()`, `Log.exception()`
- **Web Access**: `app.py` exposes `/log_events` endpoint

### Häufige Fehler
- **Serial Connection**: Board nicht angeschlossen
- **Engine Timeout**: UCI-Engine antwortet nicht
- **FEN Mismatch**: Board-Zustand ≠ Software-Zustand
- **Plugin Import**: Syntax-Fehler in Plugin-Datei

### Testing
- **Unit Tests**: `test/test_chess.py`, `test/test_common.py`
- **Live Scripts**: `scripts/live_script_tests.py`
- **Manual Testing**: Web-UI + physisches Board

## Externe Systeme

### Lichess Integration
- **API**: `berserk` library
- **Auth**: Token in Config
- **Features**: Online-Spiele, Turniere

### External Socket Server
- **Purpose**: Multi-Board Kommunikation (TeamPlay, CentaurDuel)
- **Protocol**: WebSocket mit CUUID-Authentifizierung
- **Config**: `CentaurConfig.get_external_socket_server()`

## Build & Deployment

### Debian Package
- **Structure**: `DGTCentaurMods/` als Debian-Paket
- **Scripts**: `postinst`, `prerm` für Systemd-Services
- **Installation**: `sudo dpkg -i package.deb`

### Systemd Services
- **Main Service**: `DGTCentaurMods.service` (main.py)
- **Web Service**: `DGTCentaurModsWeb.service` (app.py)
- **Update Service**: `DGTCentaurModsUpdate.service`

## Aktuelle Roadmap (Chess960-Fokus)

### TODO für Chess960 Plugin
- [ ] **Engine Strength Tuning**: Bessere Elo-Kalibrierung
- [ ] **Position Database**: Speichere gespielte Chess960-Positionen
- [ ] **Opening Book**: FRC-spezifische Eröffnungsbibliothek
- [ ] **Castling Animation**: Visuelle Rochade-Darstellung
- [ ] **Multi-Position Support**: Mehrere Chess960-Positionen pro Spiel

### Bekannte Issues
- **Castling Detection**: Manchmal fehlerhafte Rochade-Erkennung
- **Engine Compatibility**: Nicht alle Engines unterstützen FRC vollständig
- **Board Reset**: Gelegentliche Desynchronisation bei Reset

## Quick Reference für Claude

### Neue Plugin erstellen
```python
from DGTCentaurMods.classes.Plugin import Plugin, Centaur

class MyPlugin(Plugin):
    def key_callback(self, key: Enums.Btn) -> bool:
        if key == Enums.Btn.PLAY:
            Centaur.start_game(white="You", black="Bot")
            return True
        return False

    def event_callback(self, event: Enums.Event, outcome):
        if event == Enums.Event.PLAY:
            # Computer move logic here
            pass
```

### Chess960-Engine hinzufügen
1. UCI-Datei: `engines-chess960/myengine.uci`
2. Binary: `engines-chess960/myengine`
3. Plugin scannt automatisch

### WebSocket Message senden
```python
SOCKET.send_web_message({
    "fen": current_fen,
    "uci_move": last_move,
    "custom_data": my_data
})
```

### Hardware-Zugriff
```python
# LED-Steuerung
CentaurBoard.get().led_from_to(from_square, to_square)

# Sound abspielen
Centaur.sound(Enums.Sound.CORRECT_MOVE)

# Screen-Update
CentaurScreen.get().write_text(5, "Hello World")
```

Diese Dokumentation soll Claude helfen, schnell zu verstehen, wo Code geändert werden muss und wie die verschiedenen Komponenten zusammenarbeiten, besonders im Kontext der Chess960-Entwicklung.
