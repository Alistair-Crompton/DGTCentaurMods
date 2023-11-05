import bB from './assets/images/pieces/bB.png'
import bK from './assets/images/pieces/bK.png'
import bN from './assets/images/pieces/bN.png'
import bP from './assets/images/pieces/bP.png'
import bQ from './assets/images/pieces/bQ.png'
import bR from './assets/images/pieces/bR.png'
import wB from './assets/images/pieces/wB.png'
import wK from './assets/images/pieces/wK.png'
import wN from './assets/images/pieces/wN.png'
import wP from './assets/images/pieces/wP.png'
import wQ from './assets/images/pieces/wQ.png'
import wR from './assets/images/pieces/wR.png'

const pieces = { bB, bK, bN, bP, bQ, bR, wB, wK, wN, wP, wQ, wR }
export const pieceTheme = (piece: string) => pieces[piece]
