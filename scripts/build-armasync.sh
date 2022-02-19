#!/bin/bash

# rename all files to lowercase
find /home/arma3server/serverfiles/mods/ -depth -type f -exec rename 's/(.*)\/([^\/]*)/$1\/\L$2/' {} \;

cd /home/arma3server/
find serverfiles/mods.* -name '*.bisign' -delete
find serverfiles/mods.* -name '*.bisign.zsync' -delete
cd arma3sync
./build-all.sh
