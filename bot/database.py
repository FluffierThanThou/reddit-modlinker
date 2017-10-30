import logging
import os
from pymongo import MongoClient

log = logging.getLogger(__name__)

client = MongoClient( os.environ['MONGO_URI'].strip( "\"" ) )
db = client.teddy
requests = db.requests_collection

def log_record( redditor, mod ):
    record = {
        "requestingRedditor": redditor,
        "mod": mod.toObject()
    }
    try:
        requests.insert_one( record )
    except Exception as err:
        log.error( "%s: .\n%s", type(err), err )


if __name__ == '__main__':
    print requests.count(), "requests logged"