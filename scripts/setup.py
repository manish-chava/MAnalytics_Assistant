# Importing required Libraries
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import os
import logging
import boto3


# Logging Setup Config
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename='logs/app.log',level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Loading the variables into the project environment
load_dotenv()


# Initiating an aws user session for accessing the aws services directly
USER_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
USER_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
USER_REGION = os.getenv("AWS_REGION")

session = boto3.Session(
    aws_access_key_id=USER_ACCESS_KEY,
    aws_secret_access_key = USER_SECRET_ACCESS_KEY,
    region_name = USER_REGION

)


# Connecting to the Pinecone Vector Store DB 
try:

    pinecone_conn = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    logger.info("Successfully established connection the Pinecone Vector Store DB")

except Exception as e:
    logger.error(f"Encountered trouble while establishing connection to Pinecone Vector Store DB: {e}")







