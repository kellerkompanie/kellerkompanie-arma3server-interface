#!/bin/bash

json_file="modpack_info.json"

source /home/arma3server/arma3server.mods

mod_paths=$(echo $mods | tr ";" " " | sed 's/\\//g')
ARRAY=()

for addr in $mod_paths
do
	id_file="/home/arma3server/serverfiles/${addr}/.id"
	name=$(cut -d "/" -f 2 <<< "${addr}")
	uuid="null"
	if [ -f $id_file ]; then
		uuid=$(cat "$id_file")
	fi

	ARRAY+=($name $uuid)
done

printf "{\n" > $json_file
printf '\t"mods": [\n' >> $json_file
for ((i=0;i< ${#ARRAY[@]} ;i+=2));
do
	if [ $i -gt 0 ]; then
		printf ",\n" >> $json_file
	fi
	printf "\t\t{\n" >> $json_file
    printf '\t\t\t"name": \"%s\",\n' "${ARRAY[i]}" >> $json_file
    printf '\t\t\t"uuid": \"%s\"\n' "${ARRAY[i+1]}" >> $json_file
    printf "\t\t}" >> $json_file
done
printf '\n\t]\n' >> $json_file
printf "}\n" >> $json_file

cat $json_file