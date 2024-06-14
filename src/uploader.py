import csv
import logging
import os
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.join(FILE_DIR, os.pardir)
logger = logging.getLogger(__name__)
dir = os.path.join(PARENT_DIR, 'src/creds.json')
cred = credentials.Certificate(dir)
app = firebase_admin.initialize_app(cred)
db = firestore.client()
dbName = u'anm_1'

with open('./csv/anm_1.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    results = ""
    for row in csv_reader:
        if line_count == 0:
            logger.info(f'Column names are {", ".join(row)}.')
            results += f'Column names are {", ".join(row)}.\n'
            line_count += 1
        else:
            playerName = {"username":row[0].strip().lower(),"chatId" :None}
            partnerName = {"username":row[1].strip().lower(),"chatId" :None}
            db.collection(dbName).add(playerName)
            db.collection(dbName).add(partnerName)

            
