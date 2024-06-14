import * as functions from 'firebase-functions'
import * as express from 'express'
import * as cors from 'cors'

// Builds Express app
const app = express()

// Applies CORS middleware to enable all CORS requests.
app.use(cors({origin: true}))

// Entry point for every message
app.post('/', async (req, res) => {
  // Checks if the incoming message is a valid Telegram message
  const isTelegramMessage = req.body
                          && req.body.message
                          && req.body.message.chat
                          && req.body.message.chat.id
                          && req.body.message.from
                          && req.body.message.from.first_name

  // If it is, extract the chat ID and the sender's first name from the message.
  if (isTelegramMessage) {
    const chat_id = req.body.message.chat.id
    const {first_name} = req.body.message.from // Destructuring

    // 
    return res.status(200).send({
      method: 'sendMessage',
      chat_id,
      text: `Hello ${first_name}`
    })
  }

  return res.status(200).send({ status: 'not a telegram message' })
})

// Export router function for use by Firebase
export const router = functions.https.onRequest(app)