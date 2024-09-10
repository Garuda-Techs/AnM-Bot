import csv
import logging
import os
import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials
from firebase_admin import firestore

load_dotenv()
print('UPLOADER.PY BEGINS EXECUTION')
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.join(FILE_DIR, os.pardir)
pyers = os.path.join(PARENT_DIR, os.environ['CSV_PATH'])
logger = logging.getLogger(__name__)
dir = os.path.join(PARENT_DIR, 'src/creds.json')
# print(dir)

# Initialise an instance of Cloud Firestore on our own server.
# Ref: https://firebase.google.com/docs/firestore/quickstart?authuser=0&hl=en#python_1
# Use the bot's Firebase project service account credentials
# Ref: https://cloud.google.com/iam/docs/service-account-overview
def initialise_firestore():
    """ Returns a Firestore client with the necessary credentials configured.
    
    (None) -> Client
    """
    try:
        cred = credentials.Certificate(dir)
        if not firebase_admin._apps:
            logger.info("Initalising Firebase app...")
            app = firebase_admin.initialize_app(cred)
        else:
            logger.info("Firebase app already initialised. Continuing execution.")
        return firestore.client()
    except Exception as e:
        logger.error(f'Failed to initialise Firestore: {e}')
        logger.info('Please undeploy the A&M Bot and debug before re-deploying it.')
        exit()

def clear_firestore_collection(collection_ref, collection):
    """ Clears the Firestore collection to prepare it for a clean CSV upload.
    
    (CollectionReference) -> None
    """
    try:
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()
        logger.info(f'Cleared collection: {collection}')
    except Exception as e:
        logger.error(f'Failed to clear collection: {collection}')
        logger.info('Please undeploy the A&M Bot and debug before re-deploying it.')


def upload_data_to_firestore():
    """ Uploads all data from the pairings CSV file to Firestore.
    
    (None) -> None
    """
    db = initialise_firestore()
    # if os.getenv('DB_PATH') == 'pairings':
    #     collection = 'pairings'
    #     logger.info('Uploading to "pairings" db...')
    # elif os.getenv('DB_PATH') == 'pairings2':
    #     collection = 'pairings2'
    #     logger.info('Uploading to "pairings2" db...')
    # elif os.getenv('DB_PATH') == 'pairings3':
    #     collection = 'pairings3'
    #     logger.info('Uploading to "pairings3" db...')
    db_path = os.getenv('DB_PATH')
    collection = db.path
    collection_ref = db.collection(collection)
    batch = db.batch()
    try:
        clear_firestore_collection(collection_ref, collection)
        logger.info("Uploading data to Firestore...")        
        with open(pyers) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            results = ""
            for (line_count, row) in enumerate(csv_reader):
                if line_count == 0:
                    logger.info(f'Column names are {", ".join(row)}.')
                    results += f'Column names are {", ".join(row)}.\n'
                    # print(results)
                    continue
                else:
                    angel_name = {"username":row[0].strip().lower(),"chatId" :None}
                    mortal_name = {"username":row[1].strip().lower(),"chatId" :None}
                    batch.set(collection_ref.document(), angel_name)
                    batch.set(collection_ref.document(), mortal_name)
                    print(f'Prepared pair {line_count} {angel_name["username"], mortal_name["username"]} for DB commit.')
            logger.info('Committing batch...')
            batch.commit()
            logger.info('Batch commit successful. Database updated.\n')
            logger.info('CSV uploaded!')
                
    except Exception as e:
        logger.error(f'Failed to upload data to Firestore: {e}')
        logger.info('Please undeploy the A&M Bot and debug before re-deploying it.')
        exit()
                
if __name__ == "__main__":
    upload_data_to_firestore()
    print("Terminating uploader.py...")
