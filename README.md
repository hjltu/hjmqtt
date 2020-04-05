# hjmqtt
### Setup:
#### Config:
>config/{SERIAL}.csv
>SERIAL: Rpi serial number (/proc/cpuinfo)
>default csv file: setup/default.csv
>documentation: https://github.com/OSA83/hjhome-doc
### Build:
>docker build -f Docker.hjhome -t hjmqtt .
### Run:
>docker run -d --rm --name=hjmqtt -v "$(pwd)"/my/config:/root/config hjmqtt
>docker run -d --restart=always --name=hjmqtt -v "$(pwd)"/my/config:/root/config hjmqtt
