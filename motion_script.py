#!/home/pi/Desktop/PycharmProjects/catDetector/venv/bin/python3.7
import telegram
import sys
import os
from google.cloud import vision
from google.cloud.vision import types
from telegram import ChatAction
import glob
from main import get_Keyboard
import dropbox
from datetime import date

def checkCat(image):
    client = vision.ImageAnnotatorClient()
    content = image.read()
    image = types.Image(content=content)
    response = client.label_detection(image=image)
    labels = response.label_annotations
    for label in labels:
        print("LABEL:", label.description, " SCORE:", label.score)
        if label.description == 'Cat' and label.score > 0.6:
            return True
    return False

def get_last_motion_video_path():
    list=glob.glob(MOTION_FOLDER+'/*.mp4')
    latest_video=max(list,key=os.path.getctime)
    return latest_video

def upload_to_dropbox(file,filename,type):
    dbx = dropbox.Dropbox(DBX_TOKEN)
    dbx.files_upload(file.read(), type + str(date.today())+'/'+filename)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/Desktop/PycharmProjects/catDetector/catDetector-63ad1f321ae3.json"
CHAT_ID=***
BOT_TOKEN=***
DBX_TOKEN=***
MOTION_FOLDER="/home/pi/Desktop/motion"
bot=telegram.Bot(token=BOT_TOKEN)


last_image_path=sys.argv[1]
last_image=open(last_image_path,'rb')
cat=checkCat(last_image)
last_image.seek(0)

#snapshot mode
if last_image_path.endswith("snapshot.jpg"):
    if not cat:
        bot.send_message(chat_id=CHAT_ID,text="Cat not detected",reply_markup=get_Keyboard())
    else:
        bot.send_chat_action(chat_id=CHAT_ID, action=ChatAction.UPLOAD_PHOTO)
        bot.send_photo(chat_id=CHAT_ID, photo=last_image, caption="Cat detected!",reply_markup=get_Keyboard())
        last_image.seek(0)
        upload_to_dropbox(last_image,os.path.basename(last_image_path),type='/snapshots/')
    #os.remove(last_image_path)
#auto mode
else:
    # get last video path
    last_video_path = get_last_motion_video_path()
    if cat:
        bot.send_chat_action(chat_id=CHAT_ID, action=ChatAction.UPLOAD_PHOTO)
        bot.send_photo(chat_id=CHAT_ID,photo=last_image,caption="Cat detected!",reply_markup=get_Keyboard())
        last_image.seek(0)
        upload_to_dropbox(last_image, os.path.basename(last_image_path), type='/photos/')
        if os.path.exists(MOTION_FOLDER+'/cat.mp4'):
            os.remove(MOTION_FOLDER+'/cat.mp4')
        upload_to_dropbox(open(last_video_path,'rb'), os.path.basename(last_video_path), type='/videos/')
        os.rename(last_video_path,os.path.dirname(last_video_path)+'/cat.mp4')
    else:
        print("no cat detected in auto mode")
        #os.remove(last_video_path)
    #os.remove(last_image_path)


