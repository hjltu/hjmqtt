#!/bin/bash

# 21-aug-18
# installing hjhome service

# check sudo

ME=`whoami`

if [[ $ME != root ]] ; then
	echo run it with sudo
	exit 1
fi

# check installed supervisor and pano-mqtt

if [[ $1 != -y ]] ; then
	echo installing hjhome services
	read -p 'supervisor and paho-mqtt is installed? y/n :' ANS

	if [[ $ANS != y ]] ; then
		exit 1
	fi
fi

# check filegen file exist
if [ ! -f $PWD/filegen.sh ]; then
	echo "ERR: file filegen.sh not found in $PWD"
	exit 1
fi

# add to set date for user
#echo "$SUDO_USER ALL=NOPASSWD:/bin/date" | (editor='tee -a' visudo)
#CHECK="ALL=(ALL) NOPASSWD:ALL"
#if tail -1 /etc/sudoers | grep $SUDO_USER | grep -q "$CHECK"
#then
#    echo "$SUDO_USER already NOPASSWD"
#else
#    echo "enable NOPASSWD for $SUDO_USER"
#    echo "$SUDO_USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
#fi

# file gen

echo generate conf files

gen_conf_file(){

# check json file exist
if [ ! -f $PWD/$1.py ]; then
	echo "ERR: file $1.py not found in /home/$SUDO_USER"
	return
fi

cat > $1.conf << EOF
;apt install supervisor
;/etc/supervisor/conf.d/$1.conf
;supervisorctl reread
;supervisorctl update
;service supervisor restart

[program:$1.py]
environment=PYTHONPATH="/home/$SUDO_USER:$PYTHONPATH",HOME="/home/$SUDO_USER",TERM="xterm"
directory=$PWD
user=$SUDO_USER
;command=/usr/bin/python3 -u $PWD/$1.py
command=/usr/bin/python3 $PWD/$1.py
autostart=true
autorestart=true
stdout_logfile=/var/log/$1.out.log
stderr_logfile=/var/log/$1.err.log

stdout_logfile_maxbytes=10MB
stderr_logfile_maxbytes=10MB
stdout_logfile_backups=1
stderr_logfile_backups=1
EOF

chmod +x $1.py
chmod +x $1.conf
mv $1.conf /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update
service supervisor restart
}

gen_service_file(){

# check json file exist
if [ ! -f /home/$SUDO_USER/$1.json ]; then
	echo "ERR: file $1.json not found in /home/$SUDO_USER"
	return
fi

cat > $1.service << EOF
[Unit]
Description=$1
After=syslog.target network.target

[Service]
ExecStart=/usr/bin/homekit2mqtt -m /home/$SUDO_USER/$1.json -b "$1" -a "$2" -c "$3"
Restart=on-failure
KillSignal=SIGINT

# log output to syslog as '$1'
SyslogIdentifier=$1
StandardOutput=syslog

# non-root user to run as
WorkingDirectory=/home/$SUDO_USER/
User=$SUDO_USER
Group=$SUDO_USER

[Install]
WantedBy=multi-user.target
EOF

chmod +x $1.service
mv $1.service /etc/systemd/system
sudo systemctl daemon-reload 
sudo systemctl enable $1.service 
sudo systemctl start $1.service
}

# create accesories
bash filegen.sh hjhome.json
chown pi:pi *json
mv *json /home/$SUDO_USER

gen_conf_file hjmqtt
gen_service_file hjhome AA:BB:CC:DD:EE:FF 123-45-678




echo end











