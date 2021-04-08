# -*- coding: utf-8 -*-
import datetime
import glob
import json
import os
import os.path
import re
import subprocess
import sys
from flask import Flask, request, abort, jsonify
from werkzeug.utils import secure_filename

import faction_config_generator
from kekosync import KeKoSync
from stammspieler import Stammspieler

app = Flask(__name__)
settings = None
database = None
kekosync = None

CONFIG_FILEPATH = 'config.json'
MISSIONS_DIR = '/home/arma3server/serverfiles/mpmissions'

START_SCRIPT = 'sudo -u arma3server /home/arma3server/start_server.sh 2>&1'
STOP_SCRIPT = 'sudo -u arma3server /home/arma3server/stop_server.sh 2>&1'
UPDATE_SCRIPT = 'sudo -u arma3server /home/arma3server/update_server.sh 2>&1'
RUN_ARMA3SYNC = 'sudo -u arma3server /home/arma3server/build-armasync.sh 2>&1'
GET_ARMA_PROCESS = 'sudo -u arma3server /home/arma3server/get_arma_process.sh 2>&1'
INFO_SCRIPT = 'sudo -u arma3server /home/arma3server/modpack_info.sh 2>&1'
DELETE_MISSION_SCRIPT = 'sudo -u arma3server /home/arma3server/deletemissions.sh'
FIXPERMISSIONS_SCRIPT = 'sudo -u root /home/arma3server/fixpermissions.sh 2>&1'
SWITCH_MODPACK = 'sudo -u arma3server /home/arma3server/switch_modpack.sh'

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


def is_whitelisted(ip):
    whitelisted = ip in settings['ip_whitelist']
    if not whitelisted:
        print(ip, "is not whitelisted", file=sys.stderr)
    return whitelisted


@app.route("/")
def hello():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    return "Hello World!"


@app.route("/running")
def running():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if arma3server_running():
        return "server is running", 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return "server is stopped", 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/start")
def start():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if arma3server_running():
        return "server is already running", 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        stdout, stderr = run_shell_command(START_SCRIPT)
        return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/select_mods/<query_string>")
def select_mods(query_string):
    if not is_whitelisted(request.remote_addr):
        abort(403)

    query_params = query_string.split('&')
    query_dict = {'action': None, 'modpack': None, 'maps': [], 'event_mods': []}
    for query_param in query_params:
        param_split = query_param.split('=')
        key = param_split[0]
        value = param_split[1].replace('%40', '@')
        if key == 'maps' or key == 'event_mods':
            query_dict[key].append(value)
        else:
            query_dict[key] = value

    base_file_path = ''
    if query_dict['modpack'] == 'main':
        base_file_path = '/home/arma3server/serverfiles/mods.main/'
    elif query_dict['modpack'] == 'main-bundeswehr':
        base_file_path = '/home/arma3server/serverfiles/mods.main/'
    elif query_dict['modpack'] == 'ironfront':
        base_file_path = '/home/arma3server/serverfiles/mods.ironfront/'
    elif query_dict['modpack'] == 'vietnam':
        base_file_path = '/home/arma3server/serverfiles/mods.vietnam/'
    elif query_dict['modpack'] == 'gm':
        base_file_path = '/home/arma3server/serverfiles/mods.gm/'
    elif query_dict['modpack'] == 'scifi':
        base_file_path = '/home/arma3server/serverfiles/mods.scifi/'
    elif query_dict['modpack'] == 'special':
        base_file_path = '/home/arma3server/serverfiles/mods.special/'
    elif query_dict['modpack'] == 'vanilla':
        base_file_path = ''
    elif query_dict['modpack'] == 'vindicta':
        base_file_path = '/home/arma3server/serverfiles/mods.vindicta/'
    elif query_dict['modpack'] == 'antistasi':
        base_file_path = '/home/arma3server/serverfiles/mods.antistasi/'

    stdout, stderr = run_shell_command(SWITCH_MODPACK + ' ' + base_file_path)

    mods_file_path = '/home/arma3server/arma3server.mods'
    with open(mods_file_path, "a+") as f:
        if query_dict['modpack'] == 'main-bundeswehr':
            for subdir, dirs, files in os.walk('/home/arma3server/serverfiles/mods.bundeswehr/'):
                for sub_dir in dirs:
                    if sub_dir.startswith('@'):
                        f.write("mods=\"${mods}mods.bundeswehr/\\%s\\;\"\n" % sub_dir)

        if 'event_mods' in query_dict:
            for event_mod in query_dict['event_mods']:
                f.write("mods=\"${mods}mods.event/\\%s\\;\"\n" % event_mod)

        if 'maps' in query_dict:
            for map_mod in query_dict['maps']:
                f.write("mods=\"${mods}mods.maps/\\%s\\;\"\n" % map_mod)

        if 'gm' in query_dict:
            f.write("mods=\"gm\\;${mods}\"\n")

        f.close()

    return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/stop")
def stop():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if arma3server_running():
        stdout, stderr = run_shell_command(STOP_SCRIPT)
        return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return "server is not running", 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/update")
def update():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if arma3server_running():
        return "you have to stop the server first", 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        stdout, stderr = run_shell_command(UPDATE_SCRIPT)
        return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/run_arma3sync")
def run_arma3sync():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    stdout, stderr = run_shell_command(RUN_ARMA3SYNC)
    return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/info")
def info():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if arma3server_running():
        stdout, stderr = run_shell_command(INFO_SCRIPT)
        return "Aktuell laufende Mods:\n\n" + stdout.decode("utf-8"), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return "Der Server ist aktuell offline.", 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/missions")
def missions():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    missions_list = glob.glob(MISSIONS_DIR + "/*.pbo")
    missions_list.sort(key=str.lower)
    missions_list = [os.path.basename(f) for f in missions_list]
    return '\n'.join(missions_list), 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/missions/delete/<mission>")
def missions_delete(mission):
    if not is_whitelisted(request.remote_addr):
        abort(403)

    script = DELETE_MISSION_SCRIPT + ' ' + mission + ' 2>&1'
    stdout, stderr = run_shell_command(script)
    if not stdout:
        return "Mission gelöscht", 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/missions/upload", methods=['POST'])
def missions_upload():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    uploader = request.form.get('uploader').lower()
    file = request.files.get('mission_file')

    if not file:
        return 'Fehler! Keine Datei übergeben', 200, {'Content-Type': 'text/plain; charset=utf-8'}
    if not uploader:
        return 'Fehler! Kein Uploader übergeben', 200, {'Content-Type': 'text/plain; charset=utf-8'}

    filename = secure_filename(file.filename)
    p = re.compile(r"^([A-Za-z0-9]|_|-)+\.([A-Za-z0-9]|_|-)+\.pbo$")
    if not p.match(filename):
        return """Fehler! Erlaubte Zeichen im Dateinamen A-Z a-z 0-9 - und _ sowie Endung .pbo!
            Außerdem muss der Dateiname die Form <Missionsname>.<Mapname>.pbo einhalten,
            mehr Informationen im 
            <a href="https://wiki.kellerkompanie.com/index.php?title=FAQ#Wie_benenne_ich_meine_Missionsdatei.3F">
            FAQ</a>.""", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    filename_parts = filename.split('.')
    mission_name = '.'.join(filename_parts[:-2])
    mission_end = '.'.join(filename_parts[-2:])
    datetime_now = datetime.datetime.now()
    mission_name = mission_name + "." + datetime_now.strftime(
        "%Y%m%d.%H%M%S") + "." + "uploaded_by_" + uploader + "." + mission_end

    file.save(os.path.join(MISSIONS_DIR, mission_name))
    stdout, stderr = run_shell_command(FIXPERMISSIONS_SCRIPT)
    return 'Mission erfolgreich hochgeladen als ' + mission_name + ' ' + stdout.decode("utf-8"), 200, {
        'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/logs/<name>")
def logs(name):
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if name == "arma3server":
        script = LOGSHOW_SCRIPT_SERVER
    elif name == "hc1":
        script = LOGSHOW_SCRIPT_HC1
    elif name == "hc2":
        script = LOGSHOW_SCRIPT_HC2
    elif name == "hc3":
        script = LOGSHOW_SCRIPT_HC3
    else:
        return "Fehler! log file von unbekannter Quelle angefragt: " + name, 200, {
            'Content-Type': 'text/plain; charset=utf-8'}

    stdout, stderr = run_shell_command(script)
    return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/ls/<directory>")
def ls(directory):
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if directory == "mods.maps":
        filepath = "/home/arma3server/serverfiles/mods.maps/"
    elif directory == "mods.event":
        filepath = "/home/arma3server/serverfiles/mods.event/"
    else:
        return "Fehler! ls von unbekannter Quelle angefragt: " + directory, 200, {
            'Content-Type': 'text/plain; charset=utf-8'}

    subfolders = [f.path for f in os.scandir(filepath) if f.is_dir() and f.name.startswith("@")]
    output = "\n".join(subfolders)

    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/stammspieler/<steam_id>")
def stammspieler(steam_id):
    if not is_whitelisted(request.remote_addr):
        abort(403)

    response_dict = database.dict_mitgespielt(steam_id)
    response_dict.update(database.dict_stammspieler(steam_id))

    return json.dumps(response_dict), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/stammspieler")
def stammspieler_all():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    response = "<h2>Liste der Stammspieler</h2><pre>"
    response += database.ausgabe_stammspieler()
    response += "</pre>"

    response += "<h2>Missionen</h2><pre>"
    response += database.ausgabe_mission()
    response += "</pre>"

    response += "<h2>Aktivität aller Spieler</h2><pre>"
    response += database.ausgabe_aktivitaet()
    response += "</pre>"

    response += "<h2>Karten</h2><pre>"
    response += database.ausgabe_karten()
    response += "</pre>"

    response += "<h2>Teilnehmer</h2>"
    response += database.ausgabe_teilnehmer()

    return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/addon_group/<uuid>", methods=['GET', 'DELETE'])
def addon_group(uuid):
    if request.method == 'GET':
        response = kekosync.get_addon_group(uuid)
        return jsonify(response), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'DELETE':
        if not is_whitelisted(request.remote_addr):
            abort(403)

        response = kekosync.delete_addon_group(uuid)
        return jsonify(response), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return jsonify("unknown method"), 403, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/addon_groups", methods=['GET', 'POST'])
def addon_groups():
    if request.method == 'POST':
        if not is_whitelisted(request.remote_addr):
            abort(403)

        uuid = request.form.get('uuid')
        name = request.form.get('name')
        author = request.form.get('author')
        addon_list = json.loads(request.form.get('addons'))

        if uuid is not None:
            response = kekosync.update_addon_group(uuid, name, author, addon_list)
        else:
            response = kekosync.create_addon_group(name, author, addon_list)

        return jsonify(response), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        response = kekosync.get_addon_groups()
        return jsonify(response), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/addons")
def addons():
    response = kekosync.get_all_addons()
    return jsonify(response), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/addon/<name>", methods=['GET'])
def addon_name(name):
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if request.method == 'GET':
        response = {'uuid': kekosync.match_addon_name(name)}
        return jsonify(response), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return jsonify("unknown method"), 403, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/update_addons", methods=['POST'])
def update_addons():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    updated_addons = request.form.get('updated_addons')
    response = kekosync.update_addons(updated_addons)
    return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/faction_generator", methods=['POST'])
def faction_generator():
    if not is_whitelisted(request.remote_addr):
        abort(403)

    request_content = request.form.get('clipboard_paste')
    response = faction_config_generator.generate_config(request_content)
    return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/username/<steam_id>")
def username(steam_id):
    if not is_whitelisted(request.remote_addr):
        abort(403)

    _username = database.get_username(steam_id)
    if _username is None:
        response = ''
    else:
        response = _username
    return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}


def load_config():
    global settings

    if os.path.exists(CONFIG_FILEPATH):
        with open(CONFIG_FILEPATH) as json_file:
            settings = json.load(json_file)
    else:
        settings = {'host': '0.0.0.0',
                    'port': 5000,
                    'ssl_context_fullchain': '/etc/letsencrypt/live/server.kellerkompanie.com/fullchain.pem',
                    'ssl_context_privkey': '/etc/letsencrypt/live/server.kellerkompanie.com/privkey.pem',
                    'ip_whitelist': ['0.0.0.0']}

        with open(CONFIG_FILEPATH, 'w') as outfile:
            json.dump(settings, outfile, sort_keys=True, indent=4)


if __name__ == "__main__":
    load_config()
    database = Stammspieler()
    kekosync = KeKoSync()
    app.run(host=settings['host'], port=settings['port'],
            ssl_context=(settings['ssl_context_fullchain'], settings['ssl_context_privkey']))
