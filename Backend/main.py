import os, time, serial, requests, queue, tempfile, threading
import pygame
import numpy as np
import sounddevice as sd
import soundfile as sf
import datetime as dt
from pydub import AudioSegment
from pydub.playback import play
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT
import RPi.GPIO as GPIO

# import OPi.GPIO as GPIO

# Variables
recFlag = 0
hangUp = 7
bootDelay = 10
uploadLoop = 10
recordingTime = 180

path = '/home/pi/Wedding-Audio-Book'
recPath = path + '/Recordings/'
dbPath = path + '/DB/'

APP_ID = '9a240c30-561e-4f61-8234-430d5191c82d'

# initialize pygame
pygame.init()
pygame.mixer.init()

# Set up the GPIO pin for I/O
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setup(hangUp, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def greetings():
    pygame.mixer.music.load(path + "/Backend/" + "greeting.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        if GPIO.input(hangUp) == 0:
            pygame.mixer.music.stop()
            break
        pygame.time.Clock().tick(1)


def recThread(rec=None):
    global recFlag

    fs = 44100
    q = queue.Queue()

    # print("hangUp")
    # print(GPIO.input(hangUp))
    # GPIO.remove_event_detect(hangUp)

    def callback(indata, frames, time, status):
        q.put(indata.copy())

    if recFlag == 0 and GPIO.input(hangUp) == 1:
        print("Recording Started")
        greetings()

        curFileName = str(dt.datetime.now())[:-5].replace(':', '.') + ".wav"

        sf.write(file=recPath + curFileName, samplerate=fs, data=np.empty((0, 1)))
        with sf.SoundFile(file=recPath + curFileName, mode='w', samplerate=fs, channels=1) as file:
            with sd.InputStream(samplerate=fs, channels=1, callback=callback):

                preTime = time.time()
                while GPIO.input(hangUp) == 1:
                    file.write(q.get())
                    curTime = time.time()
                    # print("Recording")
                    if (curTime - preTime) > recordingTime:
                        print("Recording Ended")
                        play(AudioSegment.from_file(path + "/Backend/" + "recordEnd.wav"))
                        break

    recFlag = recFlag + 1


def recFlagThread(rec=None):
    global recFlag

    recFlag = 0


def generateToken(generate=None):
    global headers
    scopes = ['Files.ReadWrite']

    access_token = generate_access_token(APP_ID, scopes=scopes)
    headers = {
        'Authorization': 'Bearer ' + access_token['access_token']
    }


def uploadThread(upload=None):
    localFile = []
    oneDriveFile = []

    response = requests.get(GRAPH_API_ENDPOINT + f'/me/drive/items/root:/Audios:/children', headers=headers)
    oneDriveFiles = response.json()['value']

    noOfOneDriveFiles = len(oneDriveFiles)
    noOfLocalFiles = len(os.listdir(recPath))

    if noOfOneDriveFiles != 0 and noOfLocalFiles != 0:
        successFactor = (noOfOneDriveFiles / noOfLocalFiles) * 100

    else:
        successFactor = 0

    noOfOneDriveFilesDB = open(dbPath + "noOfOneDriveFiles.txt", "w")
    noOfOneDriveFilesDB.write(str(noOfOneDriveFiles))
    noOfOneDriveFilesDB.close()
    noOfLocalFilesDB = open(dbPath + "noOfLocalFiles.txt", "w")
    noOfLocalFilesDB.write(str(noOfLocalFiles))
    noOfLocalFilesDB.close()
    successFactorDB = open(dbPath + "successFactor.txt", "w")
    successFactorDB.write(str(successFactor)[:5])
    successFactorDB.close()

    for file in oneDriveFiles:
        oneDriveFile.append(file['name'])

    for file in os.listdir(recPath):
        localFile.append(file)

    fileToBeUploaded = list(set(localFile).difference(set(oneDriveFile)))
    print(fileToBeUploaded)

    for uploads in range(len(fileToBeUploaded)):
        file_path = recPath + fileToBeUploaded[uploads]
        curTime = time.time()
        fileCreatedTime = os.path.getctime(file_path)

        if curTime - fileCreatedTime > recordingTime:
            with open(file_path, 'rb') as uploadFile:
                media_content = uploadFile.read()

            response = requests.put(
                GRAPH_API_ENDPOINT + f'/me/drive/items/root:/Audios/{fileToBeUploaded[uploads]}:/content',
                headers=headers,
                data=media_content
            )

    time.sleep(uploadLoop)
    threading.Thread(target=uploadThread).start()


def loop():
    threading.Thread(target=uploadThread).start()
    GPIO.add_event_detect(hangUp, GPIO.FALLING, callback=recFlagThread)
    while True:
        if GPIO.input(hangUp) == 1:
            recThread()


if __name__ == '__main__':
    try:
        generateToken()
        time.sleep(bootDelay)
        print("Program Started")
        loop()
    except:
        print("Error")
    finally:
        GPIO.cleanup()
