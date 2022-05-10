# freestyle

import urllib.request
from moviepy.editor import *

# s3 bucket integration?
# https://stackoverflow.com/questions/64828755/how-to-find-location-of-downloaded-files-on-heroku
import os
import boto3
import botocore
from dotenv import load_dotenv
load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

session = boto3.Session()
bucket = boto3.resource("s3")

def download_MP4(url_link, name):
    try:
        print("Downloading starts...\n")
        urllib.request.urlretrieve(url_link, os.getcwd()+"/Videos/"+name)
        print("Download completed..!!")
    except Exception as e:
        print(e)

# testing

def MP4_to_GIF(url_link, term):
    try:
        bucket.Object('stix-bot-database', term+".gif").load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            # The object does not exist.
            print("yuh oh it doesn't exist yet!\n")
            download_MP4(url_link, term+".mp4")
            location = os.getcwd()+"/Videos/"+term+".mp4"
            clip = VideoFileClip(location)
            clip.write_gif("Gifs/"+term+".gif",program='ffmpeg', fps=15)
            clip.close()
            s3 = session.client('s3',  aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
            s3.upload_file(os.getcwd()+"/Gifs/"+term+".gif", 'stix-bot-database', term+".gif")
        else:
            # Something else has gone wrong.
            raise


# url = input("enter url")
# name = "Videos/"
# term = input("download file as: ")
# name += term + ".mp4"

# download_MP4(url, name)
# MP4_to_GIF(term)