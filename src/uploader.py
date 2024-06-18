import csv
import logging
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

print('UPLOADER.PY BEGINS EXECUTION')
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.join(FILE_DIR, os.pardir)
logger = logging.getLogger(__name__)
dir = os.path.join(PARENT_DIR, 'src/creds.json')

# Initialise an instance of Cloud Firestore on our own server.
# Ref: https://firebase.google.com/docs/firestore/quickstart?authuser=0&hl=en#python_1
# Use the bot's Firebase project service account credentials
# Ref: https://cloud.google.com/iam/docs/service-account-overview
cred = credentials.Certificate(dir)
if not firebase_admin._apps:
    print("Initalising Firebase app...")
    app = firebase_admin.initialize_app(cred)
else:
    print("Firebase app already initialised. Continuing execution.")
db = firestore.client()
dbName = 'pairings'

def upload_data_to_firestore():
    with open('./csv/pairings.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        results = ""
        for (line_count, row) in enumerate(csv_reader):
            if line_count == 0:
                logger.info(f'Column names are {", ".join(row)}.')
                results += f'Column names are {", ".join(row)}.\n'
                print(results)
            else:
                angel_name = {"username":row[0].strip().lower(),"chatId" :None}
                mortal_name = {"username":row[1].strip().lower(),"chatId" :None}
                db.collection(dbName).add(angel_name)
                db.collection(dbName).add(mortal_name)
                print(f'Added pair {line_count} ({angel_name["username"], mortal_name["username"]}) to the database.')
