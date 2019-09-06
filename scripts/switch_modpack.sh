#!/bin/bash
echo "pwd switch_modpack #1: $(pwd)"

mod_folder=$1
#echo "mod_folder: ${mod_folder}"
mods=""

echo "Loading all mods from ${mod_folder}"

for subdir in $mod_folder*; do
	if [ -d $subdir ]; then
    	#echo "Detected mod: ${subdir}"
    	folder=${subdir/\/home\/arma3server\/serverfiles\//}
    	mods="${mods}${folder/@/\\@}\;"
	fi
done

echo ""

# echo "mods=\"${mods}\""

rm -f /home/arma3server/serverfiles/keys/*

#source /home/arma3server/arma3server.mods

mod_paths=$(echo $mods | tr ";" " " | sed 's/\\//g')

for addr in $mod_paths
do
	echo "loading: ${addr}"
	find -L /home/arma3server/serverfiles/$addr -name "*.bikey" -exec cp -n -t /home/arma3server/serverfiles/keys {} +
done

if [ -z ${optionals+x} ]; then 
	:
else
	optional_paths=$(echo $optionals | tr ";" " " | sed 's/\\//g')

	for addr in $optional_paths
	do
		echo "loading: ${addr}"
		find -L /home/arma3server/serverfiles/$addr -name "*.bikey" -exec cp -n -t /home/arma3server/serverfiles/keys {} +
	done
fi

#cp /home/arma3server/serverfiles/a3.bikey /home/arma3server/serverfiles/keys

serverMods=""
for subdir in /home/arma3server/serverfiles/mods.server/*; do
	if [ -d $subdir ]; then
		folder=${subdir/\/home\/arma3server\/serverfiles\//}
    	serverMods="${serverMods}${folder/@/\\@}\;"		
	fi
done


#echo "mods=\"${mods}\""
#echo "serverMods=\"${serverMods}\""

echo "mods=\"${mods}\"" > /home/arma3server/arma3server.mods
echo "serverMods=\"${serverMods}\"" >> /home/arma3server/arma3server.mods

echo ""
echo "Content of /home/arma3server/arma3server.mods:"
cat /home/arma3server/arma3server.mods
echo ""
