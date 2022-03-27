# Kellerkompanie arma3server-interface
This is a flask framework that allows to control the arma3server via a
HTTPS API, e.g., to be called from a website frontend.

## Installation
Users wanting to install this should be familiar with basic concepts of
Linux and Python.

### Requirements
* Linux distribution (tested with Ubuntu 16.04)
* Python 3.7 or higher (+packages: flask, werkzeug)

### Create arma3server user
If not already present, create a user with disabled-login
```
sudo adduser --disabled-login arma3server
```

### Clone repository
Go to the home directory of the new user and clone this repository
```
sudo su - arma3server
cd ~
git clone https://github.com/kellerkompanie/kellerkompanie-arma3server-interface.git arma3server-interface
```

The upcoming steps assert a python virtual environment inside the cloned
repo. If not already present install the virtualenv tools:
```
sudo apt-get update
sudo apt-get install python3-venv
```
Switch to the freshly cloned repo and initialize a virtual environment:
```
cd /home/arma3server/arma3server-interface
python3 -m venv venv
```
To install the requirements we switch to the virtual environment and
install the packages using pip:
```
source venv/bin/activate
pip install flask
pip install werkzeug
pip install pymysql
pip install requests
```


### SSL certificates
You can skip this step if you already have SSL certificates for that 
server.

If not already installed, install the Let's Encrypt certbot
```
# necessary for Ubuntu 16.04
sudo add-apt-repository ppa:certbot/certbot

sudo apt-get update
sudo apt-get install certbot
```
Certbot needs to answer cryptographic challenges, so we need to open the
ports on the firewall
```
sudo ufw allow 80
sudo ufw allow 443
```
Now, create the SSL certificates
```
sudo certbot certonly --standalone --preferred-challenges https -d server.kellerkompanie.com
```
Follow the steps and if everything was successful the required files 
should be now visible
```
sudo ls /etc/letsencrypt/live/server.kellerkompanie.com
```
```
cert.pem  chain.pem  fullchain.pem  privkey.pem  README
```

### Create startscript
In order to start the interface we create a little runscript
```
sudo su - arma3server
cd ~
nano start_interface.sh
```
Now put the following content inside and save/exit using ```CTRL+X``` 
followed by ```y``` and ```ENTER```
```
#!/usr/bin/env bash

cd /home/arma3server/arma3server-interface
git pull
source venv/bin/activate
python arma3server-interface.py > /var/log/arma3server-interface.log 2>&1
```
Make the shell script executable:
```
chmod +x start_interface.sh
```
Crate the log file and set permissions for arma3server-interface to be able to write:
```
sudo touch /var/log/arma3server-interface.log
sudo chown arma3server:arma3server /var/log/arma3server-interface.log
```
Now you can run the interface using
```
./start_interface.sh
```

### Configure
On initial startup the config file will be created, adjust it so that the webpage server IP is whitelisted:
```
nano /home/arma3server/arma3server-interface/config.json
```
Default config:
```
{
    "host": "0.0.0.0",
    "ip_whitelist": [
        "<add webserver IPv4 here>",
        "<optionally add additional IPs, e.g., for debug computer>"
    ],
    "port": 5000,
    "ssl_context_fullchain": "/etc/letsencrypt/live/server.kellerkompanie.com/fullchain.pem",
    "ssl_context_privkey": "/etc/letsencrypt/live/server.kellerkompanie.com/privkey.pem"
}
```


### Declaring as service
To have automatic start on machine boot, we add the script as systemd 
service:
```
sudo nano /etc/systemd/system/arma3server-interface.service
```
Then we add the following content:
```
[Unit]
Description=arma3server-interface Flask API
After=network.target

[Service]
User=arma3server-interface
ExecStart=/home/arma3server/start_interface.sh
WorkingDirectory=/home/arma3server
Restart=always

[Install]
WantedBy=multi-user.target
```
Finally we enable the service and register it to run on boot:
```
sudo systemctl daemon-reload
sudo systemctl start arma3server-interface.service
sudo systemctl enable arma3server-interface.service
```

### Whitelisting local IP
If you need to access the API from an external source, like your local computer, you will need to whitelist your ip 
not only in the config.json, but also add an ufw rule. 
Make sure it is inserted above the deny all rules (here at index 3):
```
ufw insert 3 allow from 1.2.3.4 proto tcp to any port 5000
```
You can check the currently active rules using:
```
ufw status numbered
```
