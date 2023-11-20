from datetime import datetime
import cv2 ,time
import pandas as pd
import pyttsx3
import threading

alarm_sound = pyttsx3.init()
voices = alarm_sound.getProperty('voices')
alarm_sound.setProperty('voice', voices[0].id)
alarm_sound.setProperty('rate', 150)

def voice_alarm(alarm_sound):
    alarm_sound.say("Object Detected")
    alarm_sound.runAndWait()

first_frame = None
status_list = [None, None]
times = []
df = pd.DataFrame(columns=["Start", "End"])


video = cv2.VideoCapture(0)

while True:
    check, frame = video.read()
    status = 0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if first_frame is None:       #to capture 1st frame to take reference
        first_frame = gray
        continue

    delta_frame = cv2.absdiff(first_frame, gray)     #1st frame jo capture hoga aur jo hum object ke sath krenge unke bech ka time diff h
    thresh_delta = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]  #jo object 30 pixle se neche h use black covert krdega
    thresh_delta = cv2.dilate(thresh_delta, None, iterations=0)
    cnts,_ = cv2.findContours(thresh_delta.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  #add green border

    for contour in cnts:
        if cv2.contourArea(contour) < 1000:  #1000 pixles i.e. particular threshold freq se km hona chaiye
            continue
        status = 1
        (x, y, w, h) = cv2.boundingRect(contour)   #to show cv in rectangle shape
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)  #green color for border



    status_list.append(status)                       #checking date and time and dimension of hand inserted
    if status_list[-1]>= 1 and status_list[-2]==0:
        alarm = threading.Thread(target=voice_alarm, args=(alarm_sound,))  #running different functions
        alarm.start()

    status_list = status_list[-2:]

    if status_list[-1] == 1 and status_list[-2] == 0:
        times.append(datetime.now())
    if status_list[-1] == 0 and status_list[-2] == 1:
        times.append(datetime.now())

    cv2.imshow("frame", frame)
    cv2.imshow('Capturing', gray)
    cv2.imshow('delta', delta_frame)
    cv2.imshow('thresh', thresh_delta)

    key = cv2.waitKey(1)    #screen 1milisecond ke bad refresh krti rhegi
    if key == ord('q'):
        break

print(status_list)
print(times)

for i in range(0, len(times), 2):
    df = df.append({"Start": times[i], "End": times[i+1]}, ignore_index=True)

df.to_csv("Times.csv")

video.release()
cv2.destroyAllWindows()