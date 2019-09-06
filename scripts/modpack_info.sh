#!/bin/bash

source /home/arma3server/arma3server.mods

mod_paths=$(echo $mods | tr ";" " " | sed 's/\\//g')

for addr in $mod_paths
do
	echo "${addr}"
done

if [ -z ${optionals+x} ]; then 
	:
else
	optional_paths=$(echo $optionals | tr ";" " " | sed 's/\\//g')

	for addr in $optional_paths
	do
		echo "${addr}"
	done
fi
