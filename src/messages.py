WELCOME_TEXT = 'The conversation will only start when both sides have started the bot.\n\n'
HELP_TEXT = (
    'This bot supports only text, photos, stickers, documents, audio, video, and animations.'
    '\n\nPlease note that a message from an Angel will be prefaced by an angel and a message from a mortal will be prefaced by a human.  DO NOT MIX UP YOUR CHATS!!!'
    '\n\nThe messages will not be recorded. The conversation will automatically end after the event.'
    '\n\nUse /help if you want to see this message again.'
)
ERROR_CHAT_ID = 'Sorry an error occured please type /start again.'
NOT_REGISTERED = 'Sorry you are not registered with the bot currently.'
PARTNER_UNAVAILABLE_MORTAL = 'You have started the chat but your mortal has not joined.'
PARTNER_UNAVAILABLE_ANGEL = 'You have started the chat but your angel has not joined.'
PARTNER_AVAILABLE_MORTAL = 'You have joined the chat and are now chatting with your mortal.'
PARTNER_AVAILABLE_ANGEL = 'You have joined the chat and are now chatting with your angel.'
INFORM_PARTNER_MORTAL = 'Your mortal has joined the chat.'
INFORM_PARTNER_ANGEL = 'Your angel has joined the chat.'
ADMIN_GUIDE = (
    '*FOR ADMIN USERS ONLY*\n\nFollow these steps to upload your pairings:\n\n'
    '1\) Open the `sample\.csv` file using Notepad \(Windows\) or TextEdit \(Mac\)\n'
    '2\) Enter the pairing in the format `telehandle1,telehandle2`\n'
    '3\) Once done, save the file\n'
    '4\) Send the file to me and I\'ll process it\n\n'
    'Do not that this will override any previous pairings\. Use /reset to clear the pairings and /reload to refresh the pairings from the last csv file\.'
)
