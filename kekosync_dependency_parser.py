import os
import logging
import re
import subprocess
import tempfile
import shlex
from shlex import quote

from typing import List, Union

ARMAKE2_EXECUTABLE = None
PARSE2JSON_EXECUTABLE = None

logging.basicConfig(level=logging.DEBUG)

if os.name == 'nt':
    ARMAKE2_EXECUTABLE = 'bin/win_x64/armake2.exe'
    PARSE2JSON_EXECUTABLE = 'bin/win_64/parse2json.exe'


def run_shell_command(command, decode='utf-8') -> Union[str, bytes]:
    args = shlex.split(command)
    out = subprocess.Popen(args,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()

    if decode:
        return stdout.decode(decode)
    else:
        return stdout


def parse_internal_pbo_filenames(pbo_file_path: str) -> List[str]:
    shell_command = "%s %s %s" % (ARMAKE2_EXECUTABLE, 'inspect', quote(pbo_file_path))
    shell_output = run_shell_command(shell_command)

    internal_pbo_filenames = []
    # Iterate the shell output line-wise and extract all filenames.
    # Ignore first 10 lines which contain decorative console output, after that the actual files are listed
    for line in shell_output.splitlines()[10:]:
        regex_match = re.search(r'^(\S*)', line)
        internal_pbo_filenames.append(regex_match.group(0))

    return internal_pbo_filenames


def parse_pbo_dependencies(pbo_file_path: str):
    internal_pbo_filenames = parse_internal_pbo_filenames(pbo_file_path)
    config_filenames = list(filter(lambda f: f.lower().endswith("config.cpp"), internal_pbo_filenames))

    for config_filename in config_filenames:
        shell_command_armake2 = "%s %s %s %s" % (ARMAKE2_EXECUTABLE, 'cat', quote(pbo_file_path), config_filename)
        shell_output = run_shell_command(shell_command_armake2, decode=None)

        with tempfile.NamedTemporaryFile() as fp:
            fp.write(shell_output)
            fp.flush()

            shell_command_parse2json = "bin/win_x64/parse2json.exe " + quote(fp.name)
            shell_output = run_shell_command(shell_command_parse2json)
            print(shell_output)

    return None


def parse_addon_folder_dependencies(addon_folder_path: str):
    addon_dependencies = dict()
    for directory_path, directory_names, filenames in os.walk(addon_folder_path):
        for filename in list(filter(lambda f: f.endswith(".pbo"), filenames)):
            pbo_file_path = os.path.join(directory_path, filename)
            logging.info('parsing pbo: %s', pbo_file_path)
            addon_dependencies[filename] = parse_pbo_dependencies(pbo_file_path)
    return addon_dependencies


def main():
    parse_addon_folder_dependencies(r"D:\kellerkompanie-main\@ace")


if __name__ == "__main__":
    main()
