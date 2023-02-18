import os, time, serial, requests, queue, tempfile, threading
import numpy as np
import sounddevice as sd
import soundfile as sf
import datetime as dt
from pydub import AudioSegment
from pydub.playback import play
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT
import RPi.GPIO as GPIO

# import OPi.GPIO as GPIO

# Variable for the GPIO pin number
hangUp = 15
hangUpDelay = 500
uploadLoop = 60
recordingTime = 60

path = '/home/mm/Wedding-Audio-Book'
recPath = path + '/Recordings/'
dbPath = path + '/DB/'

APP_ID = '9a240c30-561e-4f61-8234-430d5191c82d'

# Orange Pi Zero Board
# GPIO.setboard(GPIO.ZERO)

# Set up the GPIO pin for I/O
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setup(hangUp, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Read output from door sensor


def recThread(rec=None):
    fs = 44100
    q = queue.Queue()

    print(GPIO.input(hangUp))

    # GPIO.remove_event_detect(hangUp)

    def callback(indata, frames, time, status):
        q.put(indata.copy())

    if GPIO.input(hangUp) == 0:
        print("Recording Started")
        curFileName = str(dt.datetime.now())[:-5].replace(':', '.') + ".wav"

        sf.write(file=recPath + curFileName, samplerate=fs, data=np.empty((0, 1)))
        with sf.SoundFile(file=recPath + curFileName, mode='w', samplerate=fs, channels=1) as file:
            with sd.InputStream(samplerate=fs, channels=1, callback=callback):

                preTime = time.time()
                while GPIO.input(hangUp) == 0:
                    file.write(q.get())
                    curTime = time.time()
                    print("Recording")
                    if (curTime - preTime) > recordingTime:
                        print("Recording Ended")
                        play(AudioSegment.from_file("recordEnd.wav"))
                        break
    else:
        print("Recording Ended by Force")

    # GPIO.add_event_detect(hangUp, GPIO.BOTH, callback=recThread, bouncetime=hangUpDelay)


def uploadThread(upload=None):
    localFile = []
    oneDriveFile = []

    scopes = ['Files.ReadWrite']

    access_token = generate_access_token(APP_ID, scopes=scopes)
    headers = {
        'Authorization': 'Bearer ' + access_token['access_token']
    }

    response = requests.get(GRAPH_API_ENDPOINT + f'/me/drive/items/root:/Audios:/children', headers=headers)
    oneDriveFiles = response.json()['value']

    for file in oneDriveFiles:
        oneDriveFile.append(file['name'])

    for file in os.listdir(recPath):
        localFile.append(file)

    noOfOneDriveFiles = len(oneDriveFiles)
    noOfLocalFiles = len(os.listdir(recPath))
    successFactor = (noOfOneDriveFiles / noOfLocalFiles) * 100

    noOfOneDriveFilesDB = open(dbPath + "noOfOneDriveFiles.txt", "w")
    noOfOneDriveFilesDB.write(str(noOfOneDriveFiles))
    noOfOneDriveFilesDB.close()
    noOfLocalFilesDB = open(dbPath + "noOfLocalFiles.txt", "w")
    noOfLocalFilesDB.write(str(noOfLocalFiles))
    noOfLocalFilesDB.close()
    successFactorDB = open(dbPath + "successFactor.txt", "w")
    successFactorDB.write(str(successFactor)[:5])
    successFactorDB.close()

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
    # threading.Thread(target=uploadThread).start()
    # GPIO.add_event_detect(hangUp, GPIO.BOTH, callback=recThread, bouncetime=hangUpDelay)
    while True:
        if GPIO.input(hangUp) == 0:
            recThread()
        else:
            print("Do nothing")
        pass


if __name__ == '__main__':
    try:
        print("Program Started")
        loop()
    except:
        print("Error")
    finally:
        GPIO.cleanup()
