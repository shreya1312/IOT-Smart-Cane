#!/usr/bin/env python3
import requests
# If you are using a Jupyter notebook, uncomment the following line.
#%matplotlib inline
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import os
import time
from pydub import AudioSegment
from gtts import gTTS
from trialcam import picamera
# Replace <Subscription Key> with your valid subscription key.
subscription_key = "afa83a7332b044f98fd5e506191158b8"
assert subscription_key

# You must use the same region in your REST call as you used to get your
# subscription keys. For example, if you got your subscription keys from
# westus, replace "westcentralus" in the URI below with "westus".
#
# Free trial subscription keys are generated in the "westus" region.
# If you use a free trial subscription key, you shouldn't need to change
# this region.
vision_base_url = "https://centralindia.api.cognitive.microsoft.com/vision/v2.0/"

analyze_url = vision_base_url + "analyze"
'''with picamera.PiCamera() as camera:
    camera.start_preview()
    time.sleep(0.5)
    camera.capture('/home/pi/qwerty.jpg')
    camera.stop_preview()
    print ("image captured")'''
os.system('fswebcam -r 1280x720 --no-banner qwerty.jpg')


# Set image_path to the local path of an image that you want to analyze.
image_path = "/home/pi/qwerty.jpg"

# Read the image into a byte array
image_data = open(image_path, "rb").read()
headers    = {'Ocp-Apim-Subscription-Key': subscription_key,
              'Content-Type': 'application/octet-stream'}
params     = {'visualFeatures': 'Categories,Description,Color'}
response = requests.post(
    analyze_url, headers=headers, params=params, data=image_data)
response.raise_for_status()

# The 'analysis' object contains various fields that describe the image. The most
# relevant caption for the image is obtained from the 'description' property.
analysis = response.json()
print(analysis)
image_caption = analysis["description"]["captions"][0]["text"].capitalize()
print(image_caption)
myobj = gTTS(text=image_caption, lang='en', slow=False)
myobj.save("imageh.mp3")
src="/home/pi/imageh.mp3"
dstn="/home/pi/imageh.wav"
sound=AudioSegment.from_mp3(src)
sound.export(dstn,format="wav")
os.system('aplay -D plughw:1,0 imageh.wav')
