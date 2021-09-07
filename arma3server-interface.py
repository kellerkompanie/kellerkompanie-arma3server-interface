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
import logging
from werkzeug.utils import secure_filename

import faction_config_generator
import mission_check
from kekosync import KeKoSync
from stammspieler import Stammspieler

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

settings = None
database = None
kekosync = None

CONFIG_FILEPATH = 'config.json'
MISSIONS_DIR = '/home/arma3server/serverfiles/mpmissions'
MODS_FILE = '/home/arma3server/arma3server.mods'

START_SCRIPT = '/home/arma3server/start_server.sh 2>&1'
STOP_SCRIPT = '/home/arma3server/stop_server.sh 2>&1'
UPDATE_SCRIPT = '/home/arma3server/update_server.sh 2>&1'
RUN_ARMA3SYNC = '/home/arma3server/build-armasync.sh 2>&1'
RUN_KEKOSYNC = '/home/arma3server/run-kekosync.sh 2>&1'
GET_ARMA_PROCESS = '/home/arma3server/get_arma_process.sh 2>&1'
INFO_SCRIPT = '/home/arma3server/modpack_info.sh 2>&1'
DELETE_MISSION_SCRIPT = '/home/arma3server/deletemissions.sh'

LOGSHOW_SCRIPT_SERVER = 'tail -n 300 /home/arma3server/log/console/arma3server-console.log'
LOGSHOW_SCRIPT_HC1 = 'tail -n 300 /home/arma3server/log/console/arma3hc1-console.log'
LOGSHOW_SCRIPT_HC2 = 'tail -n 300 /home/arma3server/log/console/arma3hc2-console.log'
LOGSHOW_SCRIPT_HC3 = 'tail -n 300 /home/arma3server/log/console/arma3hc3-console.log'


def run_shell_command(command):
    app.logger.debug('run_shell_command: ' + command)
    out = subprocess.Popen(command.split(" "),
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    return out.communicate()


def arma3server_running():
    app.logger.debug('arma3server_running')
    stdout, stderr = run_shell_command(GET_ARMA_PROCESS)
    if not stdout:
        return False
    else:
        return True


def is_whitelisted(ip):
    app.logger.debug('is_whitelisted: ' + ip)
    whitelisted = ip in settings['ip_whitelist']
    if not whitelisted:
        print(ip, "is not whitelisted", file=sys.stderr)
    return whitelisted


@app.route("/")
def hello():
    app.logger.debug('hello')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    return "Hello World!"


@app.route("/running")
def running():
    app.logger.debug('running')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if arma3server_running():
        return "server is running", 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return "server is stopped", 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/start")
def start():
    app.logger.debug('start')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if arma3server_running():
        return "server is already running", 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        stdout, stderr = run_shell_command(START_SCRIPT)
        return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


def get_addon_folders(directory):
    addon_folders = []
    for root, dirs, files in os.walk(directory):
        for sub_dir in dirs:
            if sub_dir.startswith('@'):
                sub_dir = '\\' + sub_dir
                relative_root = root.replace('/home/arma3server/serverfiles/', '')
                addon_folders.append(os.path.join(relative_root, sub_dir))
    return addon_folders


@app.route("/select_mods/<query_string>")
def select_mods(query_string):
    app.logger.debug('select_mods: ' + query_string)
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

    addon_folders = []
    enable_server_mods = True
    if query_dict['modpack'] == 'main':
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.main/'))
    elif query_dict['modpack'] == 'main-bundeswehr':
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.main/'))
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.bundeswehr/'))
    elif query_dict['modpack'] == 'main-gm':
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.main/'))
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.gm/'))
    elif query_dict['modpack'] == 'ironfront':
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.ironfront/'))
    elif query_dict['modpack'] == 'vietnam':
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.vietnam/'))
        enable_server_mods = False
    elif query_dict['modpack'] == 'vietnam-liquidblaze':
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.vietnam-liquidblaze/'))
        enable_server_mods = False
    elif query_dict['modpack'] == 'scifi':
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.scifi/'))
    elif query_dict['modpack'] == 'special':
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.special/'))
        enable_server_mods = False
    elif query_dict['modpack'] == 'vanilla':
        enable_server_mods = False
    elif query_dict['modpack'] == 'vindicta':
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.vindicta/'))
    elif query_dict['modpack'] == 'antistasi':
        addon_folders.extend(get_addon_folders('/home/arma3server/serverfiles/mods.antistasi/'))

    if 'event_mods' in query_dict:
        for event_mod in query_dict['event_mods']:
            addon_folders.append(os.path.join('mods.event', '\\' + event_mod))

    if 'maps' in query_dict:
        for map_mod in query_dict['maps']:
            addon_folders.append(os.path.join('mods.maps', '\\' + map_mod))

    if 'gm' in query_dict:
        addon_folders.append('gm')

    if 'sog' in query_dict:
        addon_folders.append('vn')

    if 'csla' in query_dict:
        addon_folders.append('csla')

    with open(MODS_FILE, "w+") as f:
        for addon_folder in addon_folders:
            f.write("mods=\"${mods}%s\\;\"\n" % addon_folder)

        if enable_server_mods:
            for subdir, dirs, files in os.walk('/home/arma3server/serverfiles/mods.server/'):
                for sub_dir in dirs:
                    if sub_dir.startswith('@'):
                        f.write("serverMods=\"${serverMods}mods.server/\\%s\\;\"\n" % sub_dir)

        if 'disable_logs' in query_dict:
            f.write("disableLogs=true\n")

        f.close()

    return jsonify(addon_folders), 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/stop")
def stop():
    app.logger.debug('stop')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if arma3server_running():
        stdout, stderr = run_shell_command(STOP_SCRIPT)
        return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return "server is not running", 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/update")
def update():
    app.logger.debug('update')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if arma3server_running():
        return "you have to stop the server first", 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        stdout, stderr = run_shell_command(UPDATE_SCRIPT)
        return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/run_arma3sync")
def run_arma3sync():
    app.logger.debug('run_arma3sync')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    stdout, stderr = run_shell_command(RUN_ARMA3SYNC)
    return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/run_kekosync")
def run_kekosync():
    app.logger.debug('run_kekosync')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    stdout, stderr = run_shell_command(RUN_KEKOSYNC)
    return stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/info")
def info():
    app.logger.debug('info')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if arma3server_running():
        stdout, stderr = run_shell_command(INFO_SCRIPT)
        return "Aktuell laufende Mods:\n\n" + stdout.decode("utf-8"), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return "Der Server ist aktuell offline.", 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/missions")
def missions():
    app.logger.debug('missions')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    missions_list = glob.glob(MISSIONS_DIR + "/*.pbo")
    missions_list.sort(key=str.lower)
    missions_list = [os.path.basename(f) for f in missions_list]
    return '\n'.join(missions_list), 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/missions/delete/<mission>")
def missions_delete(mission):
    app.logger.debug('missions_delete: ' + mission)
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
    app.logger.debug('missions_upload')
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

    mission_file = os.path.join(MISSIONS_DIR, mission_name)
    file.save(mission_file)

    try:
        mission_check.check_mission(app.logger, mission_file)
    except UnicodeDecodeError:
        app.logger.error("unable to perform mission check, mission pbo is probably binarized")

    return 'Mission erfolgreich hochgeladen als ' + mission_name, 200, {
        'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/logs/<name>")
def logs(name):
    app.logger.debug('logs: ' + name)
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
    app.logger.debug('ls: ' + directory)
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
    app.logger.debug('stammspieler: ' + steam_id)
    if not is_whitelisted(request.remote_addr):
        abort(403)

    response_dict = database.dict_mitgespielt(steam_id)
    response_dict.update(database.dict_stammspieler(steam_id))
    app.logger.debug('response_dict: ' + str(response_dict))

    json_response = json.dumps(response_dict)
    app.logger.debug('json_response: ' + json_response)

    return json_response, 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/stammspieler")
def stammspieler_all():
    app.logger.debug('stammspieler_all')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    response = "<h2>Liste der Stammspieler</h2><pre>"
    response += database.output_stammspieler()
    response += "</pre>"

    response += "<h2>Missionen</h2><pre>"
    response += database.output_mission()
    response += "</pre>"

    response += "<h2>Aktivität aller Spieler</h2><pre>"
    response += database.output_activity()
    response += "</pre>"

    response += "<h2>Karten</h2><pre>"
    response += database.output_maps()
    response += "</pre>"

    response += "<h2>Teilnehmer</h2>"
    response += database.output_participants()

    return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/addon_group/<uuid>", methods=['GET', 'DELETE'])
def addon_group(uuid):
    app.logger.debug('addon_group: ' + uuid)
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
    app.logger.debug('addon_groups')
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
    app.logger.debug('addons')
    response = kekosync.get_all_addons()
    return jsonify(response), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/addon/<name>", methods=['GET'])
def addon_name(name):
    app.logger.debug('addon_name: ' + name)
    if not is_whitelisted(request.remote_addr):
        abort(403)

    if request.method == 'GET':
        response = {'uuid': kekosync.match_addon_name(name)}
        return jsonify(response), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return jsonify("unknown method"), 403, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/update_addons", methods=['POST'])
def update_addons():
    app.logger.debug('update_addons')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    updated_addons = request.form.get('updated_addons')
    response = kekosync.update_addons(updated_addons)
    return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/faction_generator", methods=['POST'])
def faction_generator():
    app.logger.debug('faction_generator')
    if not is_whitelisted(request.remote_addr):
        abort(403)

    request_content = request.form.get('clipboard_paste')
    response = faction_config_generator.generate_config(request_content)
    return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/username/<steam_id>")
def username(steam_id):
    app.logger.debug('username: ' + steam_id)
    if not is_whitelisted(request.remote_addr):
        abort(403)

    _username = database.get_username(steam_id)
    if _username is None:
        response = ''
    else:
        response = _username
    return response, 200, {'Content-Type': 'text/plain; charset=utf-8'}


def load_config():
    app.logger.debug('load_config')
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
    app.logger.debug('__main__')
    load_config()
    database = Stammspieler()
    kekosync = KeKoSync()
    app.run(host=settings['host'], port=settings['port'], debug=True,
            ssl_context=(settings['ssl_context_fullchain'], settings['ssl_context_privkey']))
