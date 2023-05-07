import dotenv
import os
import streamlit as st
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
import azure.cognitiveservices.speech as speechsdk


dotenv.load_dotenv()


def uploadToBlobStorage(blob_path, blob_name, file_contents):

    # load env variables from .env file
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    # add env variables from .secrets.toml file
    connection_string = st.secrets["AZURE_STORAGE_CONNECTION_STRING"]

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path+"/"+blob_name)

    # Upload the file contents directly to blob storage
    blob_client.upload_blob(file_contents, blob_type="BlockBlob", overwrite=True)



def listBlobs(blob_path, filter="", max_results=10, return_string=False):
    
    # load env variables from .env file
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    # add env variables from .secrets.toml file
    connection_string = st.secrets["AZURE_STORAGE_CONNECTION_STRING"]

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    blob_list = container_client.list_blobs(prefix=blob_path)
    blob_path_filter = blob_path + "/" + filter

    filtered_list = [blob.name for blob in blob_list if blob.name.startswith(blob_path_filter)]

    #remove the path from the list
    filtered_list = [blob.split("/")[-1] for blob in filtered_list]

    filtered_list = filtered_list[:max_results]

    if return_string:
        filtered_list = ("\n".join(filtered_list))  ##not adding properly the new line

    return filtered_list


def getBlob(blob_path, blob_name):
    
    # load env variables from .env file
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    # add env variables from .secrets.toml file
    connection_string = st.secrets["AZURE_STORAGE_CONNECTION_STRING"]

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
   
    # Get the BlobClient for the specified blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path+"/"+blob_name)

    # Download the content of the blob
    try:
        blob_content = blob_client.download_blob()
    except:
        blob_content = False
        
    return blob_content


def text_to_speech(text, voicetype="it-IT-IsabellaNeural"):
    subscription_key = st.secrets["AZURE_COGNITIVE_SERVICES_KEY"]
    region = os.getenv("AZURE_COGNITIVE_SERVICES_REGION")

    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
 
    speech_config.speech_synthesis_voice_name = voicetype

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    result = speech_synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Text-to-speech synthesis completed.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        print("Text-to-speech synthesis was canceled.")


def detect_language(text):

    dotenv.load_dotenv()
    subscription_key = st.secrets["AZURE_COGNITIVE_SERVICES_KEY"]
    endpoint = os.getenv("AZURE_COGNITIVE_SERVICES_ENDPOINT")

    # Create the Text Analytics client
    client = TextAnalyticsClient(endpoint, AzureKeyCredential(subscription_key))

    # Perform language detection
    response = client.detect_language(documents=[text])[0]

    # Get the detected language
    detected_language = response.primary_language.iso6391_name

    return detected_language


##there should be a way to get a wave file from text to speech and then play it separately, thus avoiding the deployment issues with text_to_speech library
##this is still to be developed, so text to speech only works locally

    