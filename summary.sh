#!/bin/bash

. ${HOME}/bin/blib.sh

TARGET_FOLDER=${HOME}/Documents/Tesla
SHOW_SECONDS=0

function getValue() {
	ss=".*\"${1}\": \([0-9a-zA-Z.\"]*\),"	
	value=$(expr "${str}" : "${ss}")
	echo "${value}"
}

function cecho() {
	echo -e "\033[38;5;214m${1}\033[m = \033[38;5;82m${2}${3}\033[m"	
}

function showKeyValue() {
	value=$(getValue ${1})
	cecho "${1}" "${value}" "${2}"
}

function prettyAgeString() {
    local d=$((${1}/60/60/24));
    local h=$((${1}/60/60%24));
    local m=$((${1}/60%60));
    local s=$((${1}%60));
    # String in English
    str=""
    if [[ ${d} > 0 ]]; then str="${str}${d} day";    if [[ ${d} > 1 ]]; then str="${str}s "; else str="${str} "; fi; fi
    if [[ ${h} > 0 ]]; then str="${str}${h} hour";   if [[ ${h} > 1 ]]; then str="${str}s "; else str="${str} "; fi; fi
    if [[ ${m} > 0 ]]; then str="${str}${m} minute"; if [[ ${m} > 1 ]]; then str="${str}s "; else str="${str} "; fi; fi
    if [[ ${SHOW_SECONDS} > 0 ]]; then
	    if [[ ${s} > 0 ]]; then str="${str}${s} second"; if [[ ${s} > 1 ]]; then str="${str}s "; else str="${str} "; fi; fi
	fi
    if [ ! -z "${str}" ]; then
        echo "${str}ago"
    else
        echo "now"
    fi
}

#
#     M  A  I  N
#

verbose=0
while getopts "hrv" option; do
    case ${option} in
        h)
            echo "Vehicle Summary:"
            echo ""
            echo "summary.sh [-r] [-v]"
            echo ""
            echo "   - h    shows this help text"
            echo "   - r    shows the real-time summary"
            echo "   - v    increases verbosity"
            echo ""
            exit 0
            ;;
        r)
            realtime=1
            ;;
        v)
            verbose=$((verbose+1))
            ;;
        *)
            ;;
    esac
done

# ==============================================================

if [ "${realtime}" ]; then
    str=$(python showStat.py)

    echo -e "From the vehicle directly:"
else
    dateFolder=$(ls ${TARGET_FOLDER} | tail -n 1)
    logfile=$(ls ${TARGET_FOLDER}/${dateFolder}/*.json | tail -n 1)
    str=$(cat ${logfile})

    echo -e "From \033[38;5;228m${logfile}\033[m:"
fi

logTime=$(getValue "timestamp")
logTime=$((logTime/1000))
nowTime=$(date +%s)
logAge=$((nowTime - ${logTime}))
logAgeString=$(prettyAgeString ${logAge})
logAgeString=${logAgeString% }

if [ "${verbose}" -gt 0 ]; then
    echo "${str}"
    echo "logTime = ${logTime}"
fi

if [ "$(uname)" == "Linux" ]; then
	datestr=$(date -d ${logTime} +%Y%m%d-%H%M%S)
else
	datestr=$(date -r ${logTime} +%Y%m%d-%H%M%S)
fi
cecho "timestamp" "${datestr} (${logAgeString% })"

r=$(getValue "battery_range")
p=$(getValue "battery_level")
f=$(echo "scale=1; ${r} / ${p} * 100.0" | bc)
cecho "derived_battery_health" "${f} mi"

showKeyValue "ideal_battery_range" " mi"
showKeyValue "battery_range" " mi"
showKeyValue "battery_level" "%"
# showKeyValue "inside_temp" "°C"
c=$(getValue "inside_temp")
f=$(echo "scale=1; ${c} * 9 / 5 + 32.0" | bc)
cecho "inside_temp" "${c}°C / ${f}°F"
c=$(getValue "charging_state")
cecho "charging_state" "${c}"
if [ "${c}" == "\"Charging\"" ]; then
    showKeyValue "charger_power" " kW"
    showKeyValue "charger_voltage" " V"
    showKeyValue "charger_actual_current" " A"
fi

