# -*- coding: utf-8 -*-
import datetime
import glob
import json
import os.path
import re
import subprocess

from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
settings = None

CONFIG_FILEPATH = 'config.json'
MISSIONS_DIR = '/home/arma3server/serverfiles/mpmissions'

START_SCRIPT = 'sudo -u arma3server /home/arma3server/start_server.sh 2>&1'
STOP_SCRIPT = 'sudo -u arma3server /home/arma3server/stop_server.sh 2>&1'
UPDATE_SCRIPT = 'sudo -u arma3server /home/arma3server/update_server.sh 2>&1'
RUN_ARMA3SYNC = 'sudo -u arma3server /home/arma3server/build-armasync.sh 2>&1'
GET_ARMA_PROCESS = 'sudo -u arma3server /home/arma3server/get_arma_process.sh 2>&1'
INFO_SCRIPT = 'sudo -u arma3server /home/arma3server/modpack_info.sh 2>&1'
DELETE_MISSION_SCRIPT = 'sudo -u arma3server /home/arma3server/deletemissions.sh 2>&1'

LOGSHOW_SCRIPT_SERVER = 'tail -n 300 /home/arma3server/log/console/arma3server-console.log'
LOGSHOW_SCRIPT_HC1 = 'tail -n 300 /home/arma3server/log/console/arma3hc1-console.log'
LOGSHOW_SCRIPT_HC2 = 'tail -n 300 /home/arma3server/log/console/arma3hc2-console.log'
LOGSHOW_SCRIPT_HC3 = 'tail -n 300 /home/arma3server/log/console/arma3hc3-console.log'


def run_shell_command(command):
    out = subprocess.Popen(command.split(" "),
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    return out.communicate()


def arma3server_running():
    stdout, stderr = run_shell_command(GET_ARMA_PROCESS)
    if not stdout:
        return False
    else:
        return True


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/running")
def running():
    if arma3server_running():
        return "server is running"
    else:
        return "server is stopped"


@app.route("/start")
def start():
    if arma3server_running():
        return "server is already running"
    else:
        stdout, stderr = run_shell_command(START_SCRIPT)
        return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/stop")
def stop():
    if arma3server_running():
        stdout, stderr = run_shell_command(STOP_SCRIPT)
        return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return "server is not running"


@app.route("/update")
def update():
    if arma3server_running():
        return "you have to stop the server first"
    else:
        stdout, stderr = run_shell_command(UPDATE_SCRIPT)
        return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/run_arma3sync")
def run_arma3sync():
    stdout, stderr = run_shell_command(RUN_ARMA3SYNC)
    return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/info")
def info():
    if arma3server_running():
        stdout, stderr = run_shell_command(INFO_SCRIPT)
        return "Aktuell laufende Mods:\n\n" + stdout
    else:
        return "Der Server ist aktuell offline."


@app.route("/missions")
def missions():
    missions_list = glob.glob(MISSIONS_DIR + "/*.pbo")
    missions_list.sort(key=str.lower)
    missions_list = [os.path.basename(f) for f in missions_list]
    return '\n'.join(missions_list), 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/missions/delete/<mission>")
def missions_delete(mission):
    script = DELETE_MISSION_SCRIPT + ' ' + mission
    stdout, stderr = run_shell_command(script)
    if not stdout:
        return "Mission gelöscht", 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/missions/upload", methods=['POST'])
def missions_upload():
    uploader = request.form.get('uploader').lower()
    file = request.files.get('mission_file')

    if not file:
        return 'Fehler! Keine Datei übergeben', 200, {'Content-Type': 'text/plain; charset=utf-8'}
    if not uploader:
        return 'Fehler! Kein Uploader übergeben', 200, {'Content-Type': 'text/plain; charset=utf-8'}

    filename = secure_filename(file.filename)
    if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in {"pbo"}):
        return 'Fehler! Datei muss mit .pbo enden: ' + file.filename, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    p = re.compile(r"^([A-Za-z0-9]|_|-)+\\.([A-Za-z0-9]|_|-)+\\.pbo$")
    if not p.match(filename):
        return 'Fehler! Erlaubte Zeichen im Dateinamen A-Z a-z 0-9 - und _ sowie Endung .pbo!', 200, {
            'Content-Type': 'text/plain; charset=utf-8'}

    filename_parts = filename.split('.')
    if len(filename_parts) < 3:
        return 'Fehler! Dateiname muss die Form <name>.<mapname>.pbo haben: ' + file.filename, 200, {
            'Content-Type': 'text/plain; charset=utf-8'}

    mission_name = '.'.join(filename_parts[:-2])
    mission_end = '.'.join(filename_parts[-2:])
    datetime_now = datetime.datetime.now()
    mission_name = mission_name + "." + datetime_now.strftime(
        "%Y%m%d.%H%M%S") + "." + "uploaded_by_" + uploader + "." + mission_end

    file.save(os.path.join(MISSIONS_DIR, mission_name))
    return 'Mission erfolgreich hochgeladen als ' + mission_name, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/logs/<name>")
def logs(name):
    if name == "arma3server":
        script = LOGSHOW_SCRIPT_SERVER
    elif name == "hc1":
        script = LOGSHOW_SCRIPT_HC1
    elif name == "hc2":
        script = LOGSHOW_SCRIPT_HC2
    elif name == "hc3":
        script = LOGSHOW_SCRIPT_HC3
    else:
        raise Exception("log file of unknown name requested: " + name)

    out = subprocess.Popen(script.split(" "),
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


def load_config():
    global settings

    if os.path.exists(CONFIG_FILEPATH):
        with open(CONFIG_FILEPATH) as json_file:
            settings = json.load(json_file)
    else:
        settings = {'host': '0.0.0.0', 'port': 5000,
                    'ssl_context_fullchain': '/etc/letsencrypt/live/server.kellerkompanie.com/fullchain.pem',
                    'ssl_context_privkey': '/etc/letsencrypt/live/server.kellerkompanie.com/privkey.pem'}

        with open(CONFIG_FILEPATH, 'w') as outfile:
            json.dump(settings, outfile, sort_keys=True, indent=4)


if __name__ == "__main__":
    load_config()
    app.run(host=settings['host'], port=settings['port'],
            ssl_context=(settings['ssl_context_fullchain'], settings['ssl_context_privkey']))
