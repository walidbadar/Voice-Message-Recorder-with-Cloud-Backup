import os, time, serial, requests, queue, tempfile, threading
import sounddevice as sd
import soundfile as sf
import datetime as dt
from pydub import AudioSegment
from pydub.playback import play
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT
import RPi.GPIO as GPIO
# import OPi.GPIO as GPIO

# Variable for the GPIO pin number
hangUp = 11
uploadLoop = 10
recordingTime = 10

path = '/home/Wedding-Audio-Book'
recPath = path + '/Recordings/'
dbPath = path + '/DB/'

APP_ID = '9a240c30-561e-4f61-8234-430d5191c82d'

# Orange Pi Zero Board
# GPIO.setboard(GPIO.ZERO)

# Set up the GPIO pin for I/O
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setup(hangUp, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Read output from door sensor

def recThread(rec=None):
    fs = 44100
    q = queue.Queue()

    GPIO.remove_event_detect(hangUp)

    def callback(indata, frames, time, status):
        q.put(indata.copy())

    if GPIO.input(hangUp):
        print("Recording Started")
        curFileName = str(dt.datetime.now())[:-5].replace(':', '.') + ".wav"

        # write(curFileName, 44100, np.empty((0, 1)))
        with sf.SoundFile(path+"\\"+curFileName, mode='x', samplerate=fs, channels=2) as file:
            with sd.InputStream(samplerate=fs, channels=2, callback=callback):

                preTime = time.time()
                while GPIO.input(hangUp):
                    file.write(q.get())
                    curTime = time.time()
                    if (curTime - preTime) > recordingTime:
                        print("Recording Ended")
                        play(AudioSegment.from_file("recordEnd.wav"))
                        break
    else:
        print("Recording Ended by Force")

    GPIO.add_event_detect(hangUp, GPIO.RISING, callback=recThread, bouncetime=1000)

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

threading.Thread(target=uploadThread).start()
GPIO.add_event_detect(hangUp, GPIO.RISING, callback=recThread, bouncetime=1000)

while True:
    pass
