#!/usr/bin/env python3
import os
import speech_recognition as sr
from geopy.geocoders import Nominatim
from geopy import distance
from geopy import Point
from six.moves import urllib
from gtts import gTTS 
import json
import pyttsx
import re
from os import path
from pydub import AudioSegment
import time
import paho.mqtt.client as paho
import reverse_geocoder as rg

flag=0
origin='13.0309553,77.5648559396817'
broker="192.168.0.5"
#define callback
endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
api_key = 'AIzaSyBXVnSEhGjmxb1vSyD8ywbjAPjqIHDIEOs'
import RPi.GPIO as GPIO
    #origin = raw_input('Where are you?: ').replace(' ','+')


def startNav(origin):
    print("in startNav")
    #Google MapsDdirections API endpoint
    print(origin)
        #Building the URL for the request
    nav_request = 'origin={}&destination={}&key={}'.format(origin,destination,api_key)
    request = endpoint + nav_request
    #Sends the request and reads the response.
    response = urllib.request.urlopen(request).read()
    #Loads response as JSON
    directions = dict(json.loads(response))
    ans=directions[u'routes'][0][u'legs'][0][u'steps']

    for k in ans:
        if(type(k)==dict and k.has_key(u'html_instructions')):
            a=re.compile(r'<.*?>').sub('',k[u'html_instructions'])
            print(a)
            myobj = gTTS(text=a, lang='en', slow=False)
            myobj.save("welcome.mp3")
            src="/home/pi/welcome.mp3"
            dstn="/home/pi/wel.wav"
            sound=AudioSegment.from_mp3(src)
            sound.export(dstn,format="wav")
            os.system('aplay -D plughw:1,0 wel.wav')
            break
                
def on_message(client, userdata, message):
    time.sleep(1)
    global flag
    flag=1
    s=str(message.payload.decode("utf-8")).split()
    s1=s[0]+','+s[1]
    global origin
    origin=s1
    print(origin)
    startNav(origin)
while True:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    input_state = GPIO.input(18)
    if input_state == False:


        print('Where do you want to go?: ')
        os.system('aplay -D plughw:1,0 where.wav')
        os.system("arecord -D plughw:1,0 -d 10 -f cd rec4.wav")
        with sr.AudioFile("/home/pi/rec4.wav") as source:
                audio =sr.Recognizer().record(source)
                print("You said: " + sr.Recognizer().recognize_google(audio))
                destination=sr.Recognizer().recognize_google(audio).replace(' ','+')
        geolocator = Nominatim()
        location = geolocator.geocode(destination.replace('+',' '))
        print((location.latitude, location.longitude))
        dcord=Point(str(location.latitude)+' '+str(location.longitude))
        while((distance.distance(Point(origin.split(',')[0]+' '+origin.split(',')[1]),dcord).kilometers)>0.01):
            flag=0
            client= paho.Client("client-001") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
        #####Bind function to callback
            client.on_message=on_message
            #####
            print("connecting to broker ",broker)
            client.connect(broker)#connect
            client.loop_start() #start loop to process received messages
            print("subscribing ")
            client.subscribe("esp8266")#subscribe
            time.sleep(6)
            client.disconnect() #disconnect
            client.loop_stop() #stop loop
            if (flag==0):
                startNav(origin)


        os.system('aplay -D plughw:1,0 dstnr.wav')



