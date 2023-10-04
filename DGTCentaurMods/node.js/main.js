const express = require('express')
const app = express()
const http = require('http')
const server = http.createServer(app)
const { Server } = require("socket.io")
const io = new Server(server)
const crypto = require('crypto')

const port = process.env.PORT || 3000
const connectionString = process.env.PGSTRING

//console.log(process.argv)

console.log("PORT (ENV):"+process.env.PORT)
console.log("PORT:"+port)
console.log("PGSTRING:"+connectionString)

const { Pool, Client } = require('pg')

const pool = new Pool({ connectionString })

pool.on('error', (e, client) => {
    console.error('DB Error:', e)
})

//app.get('/', (req, res) => {
//    res.send('<h2>Alistair-Centaur-Mods socket.io server</h2>')
//})

const SERVER_BOT = 'ADMIN BOT'

var SERVER_CUUID = null

//app.get('/', (req, res) => {
//    res.send('<h2>Alistair-Centaur-Mods socket.io server</h2>')
//})

async function read_server_bot_cuuid() {

    const result = await pool.query("SELECT cuuid FROM public.users WHERE tag=$1", [SERVER_BOT])

    let cuuid = crypto.randomUUID()

    // Server bot does not exist
    if (result.rowCount == 0) {

        await pool.query("INSERT INTO public.users(cuuid, tag) VALUES ($1, $2)", [cuuid, SERVER_BOT])
        
    } else {
        cuuid = result.rows[0].cuuid
        console.log("SERVER_CUUID="+cuuid)
    }
    SERVER_CUUID = cuuid
}

read_server_bot_cuuid()

async function broadcast_message(socket, _message, event, chatLockedFeedback){

    try {
        const message = _message.external_request
            ? _message.external_request
            : _message.chat_message
                ? _message.chat_message
                : null

        // Unknown or incomplete message
        if (!message || !message.cuuid || !message.tag) return

        // Server impersonation not allowed
        if (message.cuuid == SERVER_CUUID) return

        const remoteAddress = socket.handshake.address

        const result = await pool.query("SELECT tag, remote_address, locked FROM public.users WHERE cuuid=$1 OR remote_address=$2", [message.cuuid, remoteAddress])

        let locked = false

        // User does not exist yet
        if (result.rowCount == 0) {

            await pool.query("INSERT INTO public.users(cuuid, tag, remote_address) VALUES ($1, $2, $3)", [message.cuuid, message.tag, remoteAddress])
            
        } else {

            for (let row of result.rows) {
                locked = row.locked
                if (locked) break
            }

            // Tag update if needed
            if (message.tag != result.rows[0].tag) {
                await pool.query("UPDATE public.users set tag=$2 WHERE cuuid=$1", [message.cuuid, message.tag])
            }
        }

        // User locked, we leave
        if (locked) {

            if (chatLockedFeedback) {
                // We send the feedback only to the sender
                socket.emit(event, { _target:message.cuuid, chat_message:{ cuuid:SERVER_CUUID, author:SERVER_BOT, tag:message.tag, message:'You have been LOCKED - Please contact an admin.'}})
            }
            return
        }

        // We can broadcast the message
        io.emit(event, _message)

    } catch (e) {
        console.log(_message)
        console.error(e)
    } finally {

    }
}

/*pool.connect()
    .then((client) => {
        client.query('SELECT locked FROM public.users')
            .then(res => {
                for (let row of res.rows) {
                    console.log(row)
                }
            })
            .catch(err => {
                console.error(err)
            })
    })
    .catch(err => {
        console.error(err)
    })*/

io.on('connection', (socket) => {
    //console.log('A user is connected.')

    socket.on('disconnect', () => {
        //console.log('A user is disconnected.')
    })

    socket.on('request', (request) => {
        broadcast_message(socket, request, 'request', true)
    })

    socket.on('web_message', (message) => {
        broadcast_message(socket, message, 'web_message')
    })
})

server.listen(port, () => {
    console.log('listening on *:'+port)
})