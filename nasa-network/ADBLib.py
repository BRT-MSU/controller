import subprocess

def runCommand(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    (output, err) = process.communicate()
    return output


def adbGetState():
    return runCommand('adb get-state')


def rebootTango():
    return runCommand ("adb reboot")


def startADB():
    return runCommand ("adb start-server")


def killADB():
    return runCommand ("adb kill-server")


def startApp():
    return runCommand(
        "adb shell am start -n com.example.angustomlinson.tangoautonomy20/.AutonomyActivity")


def stopApp():
    return runCommand(
        "adb shell am force-stop com.example.angustomlinson.tangoautonomy20") \
           + 'Stopping: com.example.angustomlinson.tangoautonomy20'


def forward(port):
    return runCommand("adb forward tcp:" + port, "tcp:" + port)
