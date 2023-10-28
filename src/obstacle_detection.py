#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import pyttsx
import os


TRIG = 23 
ECHO = 24

while 1:
    GPIO.setmode(GPIO.BCM)


    #GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    #GPIO.setmode(GPIO.BCM)
    print ("Distance Measurement In Progress")
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)

    GPIO.output(TRIG, False)
    print ("Waiting For Sensor To Settle")
    time.sleep(5)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)               

    while GPIO.input(ECHO)==0:
        pulse_start = time.time()

    while GPIO.input(ECHO)==1:
        pulse_end = time.time()
            
            
    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150

    distance = round(distance, 2)

    print ("Distance:",distance,"cm")
    if distance <= 50:
            
            
        os.system('aplay -D plughw:1,0 alert.wav')
            
        execfile('testpic.py')        
            
        time.sleep(2)
            
            
    GPIO.cleanup()
