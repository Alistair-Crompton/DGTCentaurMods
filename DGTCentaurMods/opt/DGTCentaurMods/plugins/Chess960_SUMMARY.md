# Zusammenfassung der Chess960-Plugin-Dateien

Ich habe alle relevanten Dateien zum Chess960-Plugin gescannt und analysiert (basierend auf Suche nach "Chess960" in *.py-Dateien). Das Plugin ermöglicht Fischer Random Chess (Chess960) auf dem DGT Centaur Brett.

## Kern-Dateien

### 1. plugins/Chess960.py (Haupt-Plugin, ~400 Zeilen)
- **Funktion**: Erstellt ein Menü zur Auswahl von FRC-fähigem Engine (aus `engines-chess960/`), Stärke (aus .uci-Konfig) und Farbe (Weiß/Schwarz).
- **Ablauf**:
  - Scannt Engines in `consts.ENGINES_CHESS960_DIRECTORY` (engines-chess960/*.uci).
  - Generiert random Startposition (0-959), erzeugt FEN mit `chess.Board.from_chess960_pos()`.
  - Konfiguriert Engine (z.B. Stockfish Chess960-Variante) mit Stärke.
  - Startet Spiel via `GameFactoryChess960.Engine` mit `custom_fen`.
- **Menü-Handling**: UP/DOWN navigieren, PLAY auswählen, BACK beenden. Splash-Screen "CHESS960 BOT".
- **Callbacks**: key_callback (Menü/HELP), event_callback (Spielende), move_callback (Züge akzeptieren).
- **Autor**: chemtech1.

### 2. classes/GameFactoryChess960.py (~800 Zeilen, angepasste GameFactory)
- **Anpassungen für Chess960** (markiert "Chess960 Plugin edit by Chemtech1"):
  - Init mit `chess.Board(custom_fen, chess960=True)`, speichert `_original_fen`.
  - Reset-Erkennung via `BOARD_START_STATE` (bytearray-Vergleich), reset zu original FEN.
  - Unterstützt Chess960-Rochade als normale Züge.
- **Engine-Klasse**: Vollständige Spiel-Logik (PieceHandler für LIFT/PLACE, Undo, Promotion, Web-Moves).
  - Validiert legale Züge, Promotion-Menü, Takeback (mit LED-Anleitung).
  - Threads für Game/Evaluation, Socket-Integration, PGN/DB-Speicherung.
  - UI-Updates (FEN, PGN, Evaluation-Bar), Hint-Funktion.
- **Flags**: CAN_UNDO_MOVES, CAN_FORCE_MOVES usw.

### 3. Weitere Erwähnungen
- **consts/consts.py**: Definiert `ENGINES_CHESS960_DIRECTORY = OPT_DIRECTORY + "/engines-chess960"`.
- **engines-chess960/**: Binaries + .uci-Dateien (ct800, galjoen, maia, rodentIV, stockfish, texel, wyldChess, zahak) mit UCI_Chess960-Support und ELO-Stärken (DEFAULT, E-800 bis E-2000).

## Funktionsweise
- **Start**: PLAY → Menü (Engine → Stärke → Farbe) → Random FEN → Spielstart.
- **Spiel**: Engine vs. Mensch, volle Undo/Promotion/Web-Support, Chess960-kompatibel.
- **Abhängigkeiten**: python-chess, Plugin-Base, CentaurBoard/Screen/Engine-Wrapper.

Das Plugin ist funktional, aber mit Logs/Debugs (viel Log.info). Potenzial für Verbesserungen: Mehr Engines, feste Positionen, Tests.