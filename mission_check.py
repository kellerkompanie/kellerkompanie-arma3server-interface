import os.path
import subprocess
import json
from logging import Logger

UNPACKED_MISSIONS_DIR = '/home/arma3server/serverfiles/mpmissions.unpacked'


def run_shell_command(command):
    out = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return out.communicate()


def unpack_mission(logger: Logger, mission_file: str):
    mission_name = os.path.splitext(os.path.basename(mission_file))[0]
    unpacked_mission_folder = os.path.join(UNPACKED_MISSIONS_DIR, mission_name)
    command = 'armake2 unpack {} {}'.format(mission_file, unpacked_mission_folder)
    stdout, stderr = run_shell_command(command)

    if stderr:
        logger.error(stderr)

    return unpacked_mission_folder


def parse_mission_sqm(logger: Logger, mission_sqm_file: str):
    command = 'config2json {}'.format(mission_sqm_file)
    stdout, stderr = run_shell_command(command)
    if stderr:
        logger.error(stderr)
    return json.loads(stdout)


def check_mission(logger: Logger, mission_file: str):
    unpacked_mission_folder = unpack_mission(logger, mission_file)
    mission_sqm_file = os.path.join(unpacked_mission_folder, 'mission.sqm')
    mission_sqm = parse_mission_sqm(logger, mission_sqm_file)
    addons = mission_sqm['addons']
    external_addons = list(filter(lambda x: not x.startswith('A3'), addons))
    logger.info('external addons: ' + str(external_addons))
