# Importing the required libraries
from src.utils import *
from scripts.setup import *
import streamlit as st
from streamlit_navigation_bar import st_navbar
import boto3
import os
from streamlit.runtime.uploaded_file_manager import UploadedFile
from datetime import datetime


# Responsible for running the Streamlit app
def run_app():

    # Setup - Environment Variables
    USER_CRED_AUTH_FUNC = os.getenv("USER_CRED_AUTH_FUNC")

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
        files = st.file_uploader(label="Upload your files to let the assistant perform custom analytics",type=['csv','json','parquet'],accept_multiple_files=True)
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

           
        if (st.session_state['login_active']) or (st.session_state['signup_active'] and st.session_state['login_active']) :
            with st.spinner(text="Please wait while we process your request"):
                try:
                    if files is not None:
                        s3_bucket_name = 'mpanalytics-user-docs'
                        user_uuid = st.session_state['login_details']
            
                        if isinstance(files,list):
                            all_files_upload_status = []

                            for file_obj in files:
                                s3_object_name = f'users/{user_uuid}/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}/{file_obj.name}'
                                s3_presigned_url = s3_client.generate_presigned_url('put_object',
                                                        Params={
                                                            'Bucket':s3_bucket_name,
                                                            'Key':s3_object_name
                                                        })
                                logger.info("presigned url creation is successful")
                                
                            file_upload_res = upload_file_to_presigned_url(file_object=file_obj,presigned_url=s3_presigned_url)

                            all_files_upload_status.append(file_upload_res)
                    
                            successful_file_uploads_list=list(filter(lambda file_upload_res:file_upload_res.status_code == 200,all_files_upload_status))

                            if len(successful_file_uploads_list) == len(files):
                                logger.info("All Files Uploaded to S3 Successfully")
                            else:
                                logger.info("Failed to upload all the files to S3")
                        
                    else:
                        logger.info("Executed the no uploaded doc section")
                    res = "passed"
                    st.write(res)
                except Exception as e:
                    logger.info(f"Encountered error after submit: {e}")
        
        else:
             st.error("You need to Login to start using the application!")
            



  