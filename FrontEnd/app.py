from flask import Flask, render_template, request, make_response
import subprocess
import os
import re

app = Flask(__name__)

path = '/home/pi/Wedding-Audio-Book'
dbPath = path + '/DB/'

@app.route("/")
def landing():
    bat = battery()
    storage = sdCard()
    temp = temperature()
    successFactor = successFactorRatio()
    remainingFiles = remainingFilesToBeUploaded()
    wifi = wifiSignalStrength()
    netName = networkName()
    ipAddr = ipAddress()
    # bat = "88 %"
    # storage = "86G OF 127G"
    # temp = "45 °C"
    # successFactor = "100 %"
    # remainingFiles = "0 of 13"
    # wifi = "Good"
    # netName = "NetGear"
    # ipAddr = "192.168.1.100"
    return render_template('index.html', bat=bat, storage=storage, temp=temp, successFactor=successFactor,
                           remainingFiles=remainingFiles, wifi=wifi, netName=netName, ipAddr=ipAddr)

def battery():
    bat = os.popen('echo "get battery" | nc -q 0 127.0.0.1 8423').read()
    if bat[:15] == "singlebattery: ":
        bat = (bat[15:] + "%").replace('\n', ' ')
        return bat
    elif bat[:9] == "battery: ":
        bat = (bat[9:] + "%").replace('\n', ' ')
        return bat

def temperature():
    temp = os.popen('cat /sys/class/thermal/thermal_zone0/temp').read()
    temp = int(temp) / 1000
    return str(temp) + " °C"

def sdCard():
    storage = os.popen('df -h /').read()
    storage = storage[77:82] + " of " + storage[66:69]
    return storage

def successFactorRatio():
    successFactorDB = open(dbPath + "successFactor.txt", "r")
    successFactor = successFactorDB.readline()
    successFactorDB.close()
    return successFactor + " %"

def remainingFilesToBeUploaded():
    noOfOneDriveFilesDB = open(dbPath + "noOfOneDriveFiles.txt", "r")
    noOfOneDriveFiles = noOfOneDriveFilesDB.readline()
    noOfOneDriveFilesDB.close()

    noOfLocalFilesDB = open(dbPath + "noOfLocalFiles.txt", "r")
    noOfLocalFiles = noOfLocalFilesDB.readline()
    noOfLocalFilesDB.close()

    remainingFiles = int(noOfLocalFiles) - int(noOfOneDriveFiles)

    return str(remainingFiles) + " of " + str(noOfLocalFiles)

def wifiSignalStrength():
    output = subprocess.check_output(['iwconfig', 'wlan0'])
    output = output.decode('utf-8')

    strength = 0
    for line in output.split('\n'):
        if 'Signal level' in line:
            pattern = re.compile(r'Signal level=(-?\d+) dBm')
            match = pattern.search(line)
            strength = int(match.group(1)[1:])
            break

    strength = (strength + 100) / 2

    if strength >= 75:
        return 'Good'
    elif strength >= 50:
        return 'Fair'
    else:
        return 'Bad'

def networkName():
    netName = os.popen('iwgetid').read()
    pattern = re.compile(r'ESSID:"(.+)"')
    match = pattern.search(netName)
    if match:
        return match.group(1)
    else:
        return "Not Connected"

def ipAddress():
    ipAddr = os.popen('hostname -I').read()
    return ipAddr[:13]

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=90)
