# hjmqtt
### Setup:
**Accessory file:**
<br>config/{SERIAL}.csv
<br>SERIAL: Rpi serial number (/proc/cpuinfo)
<br>default csv file: setup/default.csv
<br>documentation: https://github.com/OSA83/hjhome-doc
<br><br>**Configuration file:**
<br>config/hjmqtt.py
<br>MQTT_SERVER: mqtt server IP address
<br>VERSION: version string
### Build:
>`docker build -f Docker.hjhome -t hjmqtt .`
### Run:
>`docker run -d --rm --name=hjmqtt -v "$(pwd)"/my/config:/root/config hjmqtt`
<br>or
<br>`docker run -d --restart=always --name=hjmqtt -v "$(pwd)"/my/config:/root/config hjmqtt`
