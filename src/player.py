import csv
import logging
import os
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
from uploader import initialise_firestore, upload_data_to_firestore

print('PLAYER.PY BEGINS EXECUTION')
load_dotenv()
logger = logging.getLogger(__name__)
print('Initialising Firestore...')
initialise_firestore()
print('Firestore initialised. Uploading data to Firestore...')
upload_data_to_firestore()
print('Data successfully uploaded to Firestore.')
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.join(FILE_DIR, os.pardir)
dir = os.path.join(PARENT_DIR, 'src/creds.json')
pyers = os.path.join(PARENT_DIR, os.environ['CSV_PATH'])
cred = credentials.Certificate(dir)
db = firestore.client()
dbName = os.environ['DB_PATH']

class Player():
    def __init__(self):
        self.username = None
        self.partner = None
        self.chat_id = None
        self.isAngel = False

    def setChatId(self, id):
        self.chat_id = id
        docs = db.collection(dbName).where('username', '==', self.username).stream()
        
        # Initialize indent to None
        indent = None
        
        # Assign indent only if the document exists
        for doc in docs:
            indent = db.collection(dbName).document(doc.id)
        
        # Check if indent is None (i.e., no matching document found)
        if indent is None:
            logger.error(f"No Firestore document found for username: {self.username}")
            # raise ValueError(f"No Firestore document found for username: {self.username}")
        
        # Update Firestore document if found
        indent.update({
            'chatId': id
        })


# Initialise dict of players from players file
def loadPlayers(players: dict) -> str:
    players.clear()
    results = ""
    with open(pyers) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                logger.info(f'Column names are {", ".join(row)}.')
                results += f'Column names are {", ".join(row)}.\n'
                line_count += 1
            else:
                playerName = row[0].strip().lower()
                partnerName = row[1].strip().lower()

                for doc in db.collection(dbName).where('username','==',playerName).stream(): 
                    player = doc.to_dict()
                    
                try:
                    players[playerName].username = playerName
                    players[playerName].partner = players[partnerName]
                    players[playerName].chat_id = player["chatId"]
                    players[playerName].isAngel = True
                    print(f"user: {players[playerName].username}")
                    print(f"partner: {players[playerName].partner}")
                    print(f"chat_id: {players[playerName].chat_id}")
                    print(f"isAngel: {players[playerName].isAngel}")
                    print()
                # players[playerName].chat_id = player["chatId"] will throw an UnboundLocalError
                # if a Firestore document wasn't assigned to player in the previous for loop
                # This may occur when you use the /reload function while the bot is running.
                # To handle this error, 
                except UnboundLocalError:
                    print(f'{playerName} could not be found in Firestore. \
                        This likely means the Firestore Database is outdated. \
                        Re-uploading CSV to Firestore...')
                    upload_data_to_firestore()
                    return loadPlayers(players)
                    
                players[playerName].username = playerName
                players[playerName].partner = players[partnerName]
                players[playerName].chat_id = player["chatId"]
                players[playerName].isAngel = True

                for doc in db.collection(dbName).where(u'username',u'==',partnerName).stream(): 
                    partner = doc.to_dict()

                players[partnerName].username = partnerName
                players[partnerName].partner = players[playerName]
                players[partnerName].chat_id = partner["chatId"]
                players[partnerName].isAngel = False

                logger.info(f'Angel {playerName} has Mortal {partnerName}.')
                results += f'\nAngel {playerName} has Mortal {partnerName}.'
                line_count += 1
        logger.info(f'Processed {line_count} lines.')
        results += f'\n\nProcessed {line_count} lines.\n'
    results += validatePairings(players)
    return results


# Checks if players relation is symmetric
def validatePairings(players: dict) -> str:
    for _, player in players.items():
        if player.partner.partner.username != player.username:
            logger.error(f'Error with {player.username}\'s pairings. Please check the csv file and try again.')
            return f'Error with {player.username}\'s pairings. Please check the csv file and try again.'
    logger.info('Validation complete. There are no issues with pairings.')
    return 'Validation complete. There are no issues with pairings.'
