#!/bin/bash

cd /home/arma3server/
find serverfiles/mods.* -name '*.bisign' -delete
find serverfiles/mods.* -name '*.bisign.zsync' -delete
cd arma3sync
./build-all.sh
