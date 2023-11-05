# Getting Started

The Mod exposes a socket.io server, so the Vue interface doesn't need to run on
the board.  The easiest way to try it out is to run it locally on your desktop.

Start by configuring the Vite development proxy in `vite.config.js` to redirect
socket.io to your centaur board.

```javascript
server: {
  proxy: {
    '/socket.io': {
      target: 'ws://centaur.local',
      ws: true,
    },
  },
},
```

Then run the development server.

```bash
npm install
npm run dev
```

And visit http://127.0.0.1:5173

As Vite supports hot-module reloading, you can then proceed to edit the UI code
and see your changes live.

# On the board

Compile the production build with

```bash
npm run build
```

Or just type `make`.  This compiles the Vue UI into the local `dist` directory.
Copy this to your board.

```bash
ssh pi@centaur.local mkdir /opt/DGTCentaurMods/web/client
rsync -av dist pi@centaur.local:/opt/DGTCentaurMods/web/client
```

Also copy over the modified Flask server.

```bash
scp ../app.py pi@centaur.local:/opt/DGTCentaurMods/web
```

This modified server recognizes a new setting in your Centaur config.  Using
the Angular UI, edit the `[system]` section of your config to add`vue_ui = 1`,
then restart the web service.  Reload and you're running the new UI.

In the new UI, you can edit your config to `vue_ui = 0` and restart the web
service to return to the Angular UI.

# References

- Vue for rendering https://vuejs.org/guide/introduction.html
- Pinia for managing application data https://pinia.vuejs.org/core-concepts/
- Daisy UI for components, styles, and themes https://daisyui.com/components/
- Tailwind CSS for layout and typography https://tailwindcss.com/docs/installation
- Hero icons https://heroicons.com/
- Vite for builds and development server https://vitejs.dev/guide/
- chess.js to support FEN and PGN https://github.com/jhlywa/chess.js/
- chessboard.js to display the board https://www.chessboardjs.com/docs
- socket.io to talk to the backend https://socket.io/docs/v4/client-api/
- stockfish.js for local evaluation https://github.com/nmrugg/stockfish.js
- Codemirror for editing https://github.com/surmon-china/vue-codemirror
