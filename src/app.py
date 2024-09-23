# Importing the required libraries
from src.utils import *
from scripts.setup import *
import streamlit as st
from streamlit_navigation_bar import st_navbar
import boto3
import os
from streamlit.runtime.uploaded_file_manager import UploadedFile
from datetime import datetime
from langchain_openai import OpenAIEmbeddings


# Responsible for running the Streamlit app
def run_app():

    # Setup - Environment Variables
    USER_CRED_AUTH_FUNC = os.getenv("USER_CRED_AUTH_FUNC")
    GLUE_CRAWL_FUNC = os.getenv("GLUE_CRAWL_FUNC")
    S3_BUCKET = os.getenv("USER_DOCS_S3_BUCKET")

    # Setup - Streamlit Session
    if 'login_active' not in st.session_state:
        st.session_state['login_active'] = False  # Initial login state
    if 'signup_active' not in st.session_state:
        st.session_state['signup_active'] = False  # Initial signup state
    if 'submit_clicked' not in st.session_state:
        st.session_state['submit_clicked'] = False


    # Creating clients for necessary AWS services
    s3_client = session.client('s3')

    # Responsible for Initialising the landing web page for the streamlit app
    try:

        nav_bar = st_navbar(["Home","Login","SignUp"])
        st.title("MPAnalytics_Assistant")
        st.header("Use the assistant as your buddy for helping you in solving your Data Analytics workflows")
        user_input_text = st.text_input("Enter your text here")
        files = st.file_uploader(label="Upload your files to let the assistant perform custom analytics",type=['csv','json','parquet','pdf','xlsx','docx'],accept_multiple_files=True)
        logger.info("The Application is Up and Running!")
    except Exception as e: 
        logger.debug(f"The Application hasn't started properly: {e}")

    # Responsible for Login and Signup event handling
    if not st.session_state['login_active']:
        if nav_bar == "Login":

            function_status = login_dialog_box(func_name = USER_CRED_AUTH_FUNC)
    if not st.session_state['signup_active']:
        if nav_bar == "SignUp":
            signup_dialog_box(func_name = USER_CRED_AUTH_FUNC)


    # For handling the Submit Job
    if st.button("Submit"):
        st.session_state['submit_clicked']=True
        all_files_upload_status=[]
           
        if (st.session_state['login_active']) or (st.session_state['signup_active'] and st.session_state['login_active']) :
            with st.spinner(text="Please wait while we process your request"):

                user_uuid = st.session_state['login_details']
                try:
                    if files is not None:
                        for file_obj in files:
                            s3_object_name = f'users/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}/{file_obj.name}'
                            
                            s3_presigned_url = s3_client.generate_presigned_url('put_object',
                                                        Params={
                                                            'Bucket':S3_BUCKET,
                                                            'Key':s3_object_name
                                                        })
                            file_upload_res = upload_file_to_presigned_url(file_object=file_obj,presigned_url=s3_presigned_url)
                            all_files_upload_status.append(file_upload_res)
                        
                        successful_file_uploads_list=list(filter(lambda file_upload_res:file_upload_res.status_code == 200,all_files_upload_status))
                        if len(successful_file_uploads_list) == len(files):
                            logger.info("ALL files uploaded to S3 bucket successfully")
                            files_metadata = extract_metadata(files)
                            #file_contents = get_files_content(vector_embedding_model,files)
                            st.write(files_metadata)
                        else:
                            logger.info("All the files did not get uploaded to s3 successfully")
                        # embedding_model = OpenAIEmbeddings()
                        # files_vector_embeddings = extract_vector_embeddings(embedding_model,files)
                        
                        
                    else:
                        logger.info("Executed the no uploaded doc section")
                    res = "passed"
                    st.write(res)
                except Exception as e:
                    logger.info(f"Encountered error after submit: {e}")
        
        else:
             st.error("You need to Login to start using the application!")
            



  