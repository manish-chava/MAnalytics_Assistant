# Importing required libraries
import boto3
import json
import streamlit as st
from scripts.setup import logger
import requests
from scripts.setup import session
import pandas as pd
import pyarrow.parquet as pq
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from langchain_community.document_loaders import PyPDFLoader


# Responsible for invoking an AWS Lambda function
# **kwargs - consists details for accessing and executing the required lambda function 
def invoke_lambda(**kwargs):
    lambda_client = session.client('lambda')
    payload = json.dumps(kwargs['custom_data'])
    
    response = lambda_client.invoke(FunctionName=kwargs['function_name'],
                                    InvocationType='RequestResponse',
                                    Payload = payload)
    response_payload = json.loads(response['Payload'].read())
    return response_payload

# Custom streamlit native Dialog box for handling Login Job
@st.dialog("Login")
def login_dialog_box(func_name):
    user_email_login_cred = st.text_input("EmailId")
    user_pswd_login_cred = st.text_input("Password")
    if st.button("Login"):
        response_payload = invoke_lambda(function_name=func_name,custom_data={'login_request':True,'signup_request':False, 'User_Email':user_email_login_cred,'User_Pswd':user_pswd_login_cred})
        logger.info(f"The lambda function for login gave the following response: {response_payload}")
        if response_payload['statusCode']==200 and response_payload['req_success']:

            st.success("Thank You for logging in")
            logger.info(response_payload['body'])
            logger.info("success")
            st.session_state['login_active']=True,
            st.session_state['login_details']=response_payload['user_uuid']
            st.session_state['status']=True
            return True
          

        else:
            st.error(response_payload['body'])
            logger.info(response_payload['body'])
            st.session_state['login_details':None]
            st.session_state['status':False]
            # Function status - True: Login button pressed
            return True
    else:
        return False

# Custom streamlit native Dialog box for handling Signup Job
@st.dialog("Signup to start using the application")
def signup_dialog_box(func_name):
    user_email_signup_cred = st.text_input("Enter a valid email")
    user_pswd_signup_cred = st.text_input("Create your password")
    if st.button("Signup"):

        response_payload = invoke_lambda(function_name=func_name,custom_data={'login_request':False,'signup_request':True, 'User_Email':user_email_signup_cred,'User_Pswd':user_pswd_signup_cred})
        if response_payload['statusCode']==300 and not response_payload['req_success']:
            st.error("User already exists with the provided credentials, Go ahead and Login!")
            logger.info(response_payload['body'])
            return False

        elif response_payload['statusCode']==200 and response_payload['req_success']:
            st.success("Signup Successful, Go ahead and Login!")
            logger.info(response_payload['body'])
            return True
            
        else:
            logger.debug(response_payload['body'])
            return False
    return False

# Responsible for generating a pre-signed URL for the s3 bucket
def upload_file_to_presigned_url(**kwargs):
    file_object = kwargs['file_object']
    presigned_url = kwargs['presigned_url']
    
    s3_put_req_response = requests.put(presigned_url,data=file_object.read())

    return s3_put_req_response

def fetch_metadata(file_obj):
    file_obj.seek(0)
    metadata = None
    try:
        if file_obj.type == 'text/csv':

            df = pd.read_csv(file_obj)
            metadata = df.dtypes.to_dict()
        elif file_obj.type == 'application/json':
            # For JSON files, you may want to parse the JSON and convert to Pandas DataFrame
            # depending on whether it's a structured JSON object or a list of records
            json_data = json.load(file_obj)
            # If it's a list of dictionaries, convert to DataFrame
            if isinstance(json_data, list):
                df = pd.json_normalize(json_data)
                metadata = df.dtypes.to_dict()
            else:
                metadata = {key: type(value).__name__ for key, value in json_data.items()}
            
        elif file_obj.type in ['application/x-parquet','application/octet-stream']:
            table = pq.read_table(file_obj)
            schema = table.schema
            metadata = { name:str(type_) for name,type_ in zip(schema.names,schema.types)}

        elif file_obj.type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/vnd.ms-excel']:
            df = pd.read_excel(file_obj)
            metadata = df.dtypes.to_dict()
    except Exception as e:
        logger.info(f'Enbcountered an error while fetching the metadata: {e}')

    return metadata

def extract_metadata(files):
    metadata_compliant_file_formats = ['text/csv','application/x-parquet','application/json','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/vnd.ms-excel','application/avro','application/octet-stream']
    metadata_compliant_files  = list(filter(lambda file_obj:file_obj.type in metadata_compliant_file_formats,files))
    file_names = list(map(lambda file_obj: file_obj.name,files))
    files_metadata = dict.fromkeys(file_names,None)

    # Extracting Metadata

    for file_obj in metadata_compliant_files:
        files_metadata[file_obj.name] = fetch_metadata(file_obj)
    return files_metadata


def fetch_file_content(file_obj):
    file_obj_type = file_obj.type 
    # if file_obj_type == 'text/csv':
    #     with open(file_obj)


    pass


def extract_vector_embeddings(embedding_model,files):
    file_names = list(map(lambda file_obj: file_obj.name),files)
    files_content = dict.fromkeys(file_names,None)
    for file_obj in files:
        pass

    files_content = list(map(lambda file_obj: fetch_file_content(file_obj),files))
    vector_embeddings = embedding_model.embed_documents(files_content)
    files_vector_embeddings = dict(zip(file_names,vector_embeddings))
    
    return files_vector_embeddings

def get_files_content(embedding_model,files):

    files_metadata = extract_metadata(files)

    files_vector_embeddings = extract_vector_embeddings(embedding_model,files)
        






    






