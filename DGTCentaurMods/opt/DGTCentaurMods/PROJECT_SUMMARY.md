
# Project Summary: Alistair_DGTCentaurMods

## Overview

`Alistair_DGTCentaurMods` is a comprehensive modification and enhancement package for the DGT Centaur electronic chessboard. It replaces and extends the standard firmware to unlock a vast range of new functionalities. The project is built primarily in Python and includes a web-based interface, a modular plugin system for new game modes, and deep integration with the board's hardware (LEDs, e-paper screen, piece detection).

It is designed to be installed as a set of system services on the Centaur's underlying Debian-based Linux system, effectively transforming the board into a more powerful and versatile chess computer.

## Key Features

- **Modular Plugin System**: Easily add new game modes or features by creating new Python files in the `plugins` directory. Examples include `AlthoffBot`, `RandomBot`, and the custom `Hand+Brain` plugin.
- **Web Interface**: A full-fledged web UI, built with Vue.js and a Python backend, allows for remote interaction, game monitoring, and configuration from a browser.
- **Multiple Chess Engines**: The system supports various UCI chess engines (Stockfish, Maia, etc.), allowing players to choose their opponent and configure its skill level (ELO).
- **Lichess Integration**: A dedicated module (`lichess_module.py`) enables playing online matches on Lichess.org directly from the physical board.
- **Hardware Control**: Provides a high-level API in Python to control the board's LEDs, read user moves, and draw custom text and graphics on the e-paper display.
- **System Service Integration**: Packaged as a Debian (`.deb`) file, it installs itself as `systemd` services, ensuring that the mods run automatically in the background.
- **Auto-Update Mechanism**: Includes scripts and a dedicated service to automatically check for and apply updates.

## Core Architecture and Key Files

The project is primarily located within the `DGTCentaurMods/opt/DGTCentaurMods/` directory, mimicking its installation path on the device.

- **`main.py`**: The main entry point of the application. It initializes the board, screen, and loads the main menu and plugins.

- **`classes/`**: Contains the core object-oriented logic and hardware abstraction layers.
    - **`Plugin.py`**: The abstract base class that all game-mode plugins must inherit from. Defines the core interface (`on_start_callback`, `key_callback`, etc.).
    - **`CentaurBoard.py`**: The crucial interface for all interactions with the physical chessboard (e.g., `leds_on`, `get_user_move`, `get_fen`).
    - **`CentaurScreen.py`**: Manages the e-paper display, providing methods to draw text, images, and board positions.
    - **`ChessEngine.py`**: A wrapper for managing UCI chess engine subprocesses, including setting ELO and getting the best move.
    - **`CentaurConfig.py`**: Handles loading and saving of configuration settings.

- **`plugins/`**: Home to all modular game modes. Each `.py` file in this directory is treated as a potential plugin.
    - `AlthoffBot.py`: A good example of a complete plugin with engine selection and game logic.

- **`modules/`**: Contains specific, self-contained functionalities that can be used by the main application or plugins.
    - `lichess_module.py`: Implements the logic for connecting to and playing on Lichess.
    - `uci_module.py`: A general-purpose mode for playing against a selected UCI engine.

- **`web/`**: The complete web interface.
    - **`app.py`**: A Python Flask server that acts as the backend, communicating with the main application and serving the frontend.
    - **`client/`**: A Vue.js single-page application that provides the user-facing web interface.

- **`engines/`**: Contains the binary files for the various UCI chess engines supported by the mod.

- **`DEBIAN/` & `etc/`**: These directories contain the packaging scripts and `systemd` service files (`DGTCentaurMods.service`, `DGTCentaurModsWeb.service`) required to install the project as a robust service on the DGT Centaur.
