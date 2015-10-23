#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home
# set crontab to launch at startup
# sudo crontab -e
# @reboot sh /home/pi/CG3002-blindman/launcher.sh >/home/pi/logs/cronlog 2>&1

cd /
cd home/pi/CG3002-blindman
sudo python logic.py
cd /
