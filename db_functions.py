import psycopg2
import os
import sys
from dotenv import load_dotenv
import logging


# Create and configure logger
logging.basicConfig(filename="assistant.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 
# Creating an object
logger = logging.getLogger()
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

# Load .env file
load_dotenv()

# Now get all the database Configs from .env file
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
user_name = os.getenv("DB_USER")
pass_word = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Function to generate a DB connection
def get_connection():
    con = psycopg2.connect(database=db_name,user=user_name,password=pass_word,host=host,port=port)
    cursor = con.cursor()
    return (con,cursor)


# Now get all the topics and their document details (id, name and URL/path)
def get_topic_details(topic_id):
    try:
        con,cursor = get_connection()
        cursor.execute(f"SELECT doc_id, doc_name, doc_url FROM tst_index_tab where topic='{topic_id}'")
        row = cursor.fetchall()
        con.close()
    except Exception as e:
        logger.error("get_topic_details()|"+repr(e))
        con.close()
        return False
    return row