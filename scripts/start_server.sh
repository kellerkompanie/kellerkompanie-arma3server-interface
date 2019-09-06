#!/bin/bash
python3 /var/www/html/controlscript/write_squadxml.py
/home/arma3server/modpack_info_json.sh

/home/arma3server/arma3server start
/home/arma3server/arma3hc1 start
/home/arma3server/arma3hc2 start
/home/arma3server/arma3hc3 start
