#!/bin/bash

echo "json file generator for homekit2mqtt"

if [ -z $1 ]
then
	FILE="test.json"
	echo  "filename: test.json"
else
	FILE=$1
fi

echo "create file: $FILE"

touch $FILE
echo "{" > $FILE

########## accessories ###########################

lamp() {
LAMP="
\t	\"Light-$1\": {\n
\t	\t	\"service\": \"Lightbulb\",\n
\t	\t	\"name\":    \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"setOn\":    \"/homekit/$1\",\n
\t	\t	\t	\"statusOn\": \"/homekit/$1-stat\"\n
\t	\t	},\n
\t	\t	\"payload\": {\n
\t	\t	\t	\"onTrue\":  1,\n
\t	\t	\t	\"onFalse\": 0\n
\t	\t	},\n
\t	\t	\"manufacturer\": \"Generic\",\n
\t	\t	\"model\": \"Lightbulb\"\n
\t	},\n"
echo -e $LAMP >> $FILE
}

outlet() {
OUTLET="
\t	\"Outlet-$1\": {\n
\t	\t	\"service\": \"Outlet\",\n
\t	\t	\"name\":    \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"setOn\":             \"/homekit/$1\",\n
\t	\t	\t	\"statusOn\": \"/homekit/$1-stat\",\n
\t	\t	\t	\"statusOutletInUse\": \"/homekit/$1-stat\"\n
\t	\t	},\n
\t	\t	\"payload\": {\n
\t	\t	\t	\"onTrue\":  1,\n
\t	\t	\t	\"onFalse\": 0\n
\t	\t	},\n
\t	\t	\"manufacturer\": \"Generic\",\n
\t	\t	\"model\": \"Outlet\"\n
\t	},\n"
echo -e $OUTLET >> $FILE
}

dimm_lamp() {
DIMM_LAMP="
\t	\"Light-dimm-$1\": {\n
\t	\t	\"service\":  \"Lightbulb\",\n
\t	\t	\"name\":     \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"setOn\":            \"/homekit/$1\",\n
\t	\t	\t	\"setBrightness\":    \"/homekit/$1-dimm\",\n
\t	\t	\t	\"statusOn\":         \"/homekit/$1-stat\",\n
\t	\t	\t	\"statusBrightness\": \"/homekit/$1-dimm-stat\"\n
\t		},\n
\t		\"payload\": {\n
\t	\t	\t	\"onTrue\": 1,\n
\t	\t	\t	\"onFalse\": 0,\n
\t	\t	\t	\"brightnessFactor\": 2.54\n
\t	\t	},\n
\t	\t	\"manufacturer\": \"Generic\",\n
\t	\t	\"model\": \"Lightbulb Dimmable\"\n
\t	},\n"
echo -e $DIMM_LAMP >> $FILE
}

rgb_lamp() {
RGB_LAMP="
\t	\"Light-rgb-$1\": {\n
\t	\t	\"service\":  \"Lightbulb\",\n
\t	\t	\"name\":     \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"setOn\":            \"/homekit/$1\",\n
\t	\t	\t	\"setBrightness\":    \"/homekit/$1-br\",\n
\t	\t	\t	\"setHue\":           \"/homekit/$1-hue\",\n
\t	\t	\t	\"setSaturation\":    \"/homekit/$1-sat\",\n
\t	\t	\t	\"statusOn\":         \"/homekit/$1-stat\",\n
\t	\t	\t	\"statusBrightness\": \"/homekit/$1-br-stat\",\n
\t	\t	\t	\"statusHue\":        \"/homekit/$1-hue-stat\",\n
\t	\t	\t	\"statusSaturation\": \"/homekit/$1-sat-stat\"\n
\t	\t	},\n
\t	\t	\"payload\": {\n
\t	\t	\t	\"onTrue\":  1,\n
\t	\t	\t	\"onFalse\": 0,\n
\t	\t	\t	\"brightnessFactor\": 2.54,\n
\t	\t	\t	\"hueFactor\": 1,\n
\t	\t	\t	\"saturationFactor\": 2.54\n
\t	\t	},\n
\t	\"manufacturer\": \"Generic\",\n
\t	\"model\": \"Lightbulb Color\"\n
\t	},\n"
echo -e $RGB_LAMP >> $FILE
}

fan() {
FAN="
\t	\"Fan-$1\": {\n
\t	\t	\"service\": \"Fan\",\n
\t	\t	\"name\": \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"setOn\":    \"/homekit/$1\",\n
\t	\t	\t	\"statusOn\": \"/homekit/$1-stat\"\n
\t	\t	},\n
\t	\t	\"payload\": {\n
\t	\t	\t	\"onTrue\":  1,\n
\t	\t	\t	\"onFalse\": 0\n
\t	\t	},\n
\t	\t	\"manufacturer\": \"Generic\",\n
\t	\t	\"model\": \"Fan\"\n
\t	},\n"
echo -e $FAN >> $FILE
}

blinds() {

if [ -z $3 ]
then
	FACTOR=1
else
	FACTOR=$3
fi
BLINDS="
\t	\"WindowCowering-$1\": {\n
\t	\t	\"service\":  \"WindowCovering\",\n
\t	\t	\"name\": \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"setTargetPosition\":     \"/homekit/$1\",\n
\t	\t	\t	\"statusTargetPosition\":  \"/homekit/$1-stat\",\n
\t	\t	\t	\"statusCurrentPosition\": \"/homekit/$1-stat\"\n
\t	\t	},\n
\t	\t	\"payload\": {\n
\t	\t	\t	\"targetPositionFactor\":  $FACTOR,\n
\t	\t	\t	\"currentPositionFactor\": $FACTOR\n
\t	\t	},\n
\t	\t	\"manufacturer\": \"Generic\",\n
\t	\t	\"model\": \"WindowCovering\"\n
\t	},\n"
echo -e $BLINDS >> $FILE
}

temp() {
TEMP="
\t	\"TemperatureSensor-$1\": {\n
\t	\t	\"service\": \"TemperatureSensor\",\n
\t	\t	\"name\": \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"statusTemperature\": \"/homekit/$1-curr\"\n
\t	\t	},\n
\t	\t	\"manufacturer\": \"Generic\",\n
\t	\t	\"model\": \"TemperatureSensor\"\n
\t	},\n"
echo -e $TEMP >> $FILE
}

hum() {
HUM="
\t	\"HumiditySensor-$1\": {\n
\t	\t	\"service\": \"HumiditySensor\",\n
\t	\t	\"name\": \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"statusHumidity\": \"/homekit/$1-curr\"\n
\t	\t	},\n
\t	\t	\"manufacturer\": \"Generic\",\n
\t	\t	\"model\": \"HumiditySensor\"\n
\t	},\n"
echo -e $HUM >> $FILE
}

term() {
TERM="
\t	\"Thermostat-$1\": {\n
\t	\t	\"service\": \"Thermostat\",\n
\t	\t	\"name\": \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"setTargetTemperature\":             \"/homekit/$1-target\",\n
\t	\t	\t	\"statusCurrentTemperature\":         \"/homekit/$1-curr\",\n
\t	\t	\t	\"statusTargetTemperature\":          \"/homekit/$1-stat\",\n
\t	\t	\t	\"setTargetHeatingCoolingState\":     \"/homekit/$1-mode\",\n
\t	\t	\t	\"statusCurrentHeatingCoolingState\": \"/homekit/$1-mode-stat\"\n
\t	\t	},\n
\t	\t	\"config\": {\n
\t	\t	\t	\"TemperatureDisplayUnits\": 0\n
\t	\t	},\n
\t	\t	\"manufacturer\": \"Generic\",\n
\t	\t	\"model\": \"Thermostat\"\n
\t	},\n"
echo -e $TERM >> $FILE
}

switch() {
SWITCH="
\t	\"Switch-$1\": {\n
\t	\t	\"service\": \"Switch\",\n
\t	\t	\"name\": \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"setOn\":    \"/homekit/$1\",\n
\t	\t	\t	\"statusOn\": \"/homekit/$1-stat\"\n
\t	\t	},\n
\t	\t	\"payload\": {\n
\t	\t	\t	\"onTrue\":  1,\n
\t	\t	\t	\"onFalse\": 0\n
\t	\t	},\n
\t	\t	\"manufacturer\": \"Generic\",\n
\t	\t	\"model\": \"Switch\"\n
\t	},\n"
echo -e $SWITCH >> $FILE
}

leak() {
LEAK="
\t	\"LeakSensor-$1\": {\n
\t	\t	\"service\": \"LeakSensor\",\n
\t	\t	\"name\": \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"statusLeakDetected\": \"/homekit/$1-curr\"\n
\t	\t	},\n
\t	\t	\"payload\": {\n
\t	\t	\t	\"onLeakDetected\": 1\n
\t	\t	},\n
\t	\t	\"manufacturer\": \"Generic\",\n
\t	\t	\"model\": \"LeakSensor\"\n
\t	},\n"
echo -e $LEAK >> $FILE
}

motion() {
MOTION="
\t	\"MotionSensor-$1\": {\n
\t	\t	\"service\": \"MotionSensor\",\n
\t	\t	\"name\": \"$1\",\n
\t	\t	\"topic\": {\n
\t	\t	\t	\"statusMotionDetected\": \"/homekit/$1-curr\"\n
\t	\t	},\n
\t	\t	\"payload\": {\n
\t	\t	\t	\"onMotionDetected\": 1\n
\t	\t	},\n
\t	\t	\"manufacturer\": \"Generic\",\n
\t	\t	\"model\": \"MotionSensor\"\n
\t	},\n"
echo -e $MOTION >> $FILE
}

###################################################

echo "create accessories"

lamp "test"
#lamp lamp1
#outlet sonoff1
dimm_lamp dimmer1
#rgb_lamp rgb1
#fan fan1
#blinds blind1 1,2.54
temp temp1
#term term1
#switch sw1
#leak leak1
#motion motion1


#################################################

echo "}" >> $FILE

LINE=`cat $FILE | wc -l`
if [ $LINE -gt 10 ]
then
	echo " remove (,) after last accessory"
	let LINE=$LINE-2
	echo "$LINE"
	sed -i "${LINE}s/,//" $FILE
else
	echo "no accessories"
fi
echo "end"
#cat $FILE



























