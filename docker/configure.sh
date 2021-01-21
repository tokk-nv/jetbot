#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

export JETBOT_DIR="$DIR/../"
echo "export JETBOT_DIR=$JETBOT_DIR"

input="$JETBOT_DIR/setup.py"
while IFS= read -r line
do
    match=`echo $line|grep "version"`
    if [ $? -eq 0 ]; then
        [[ $line =~ '[0-9]' ]]
        echo $line
        export JETBOT_VERSION=`echo $line | cut -d'=' -f2 | sed "s/'//g" | sed "s/,//g"`
        echo "JETBOT_VERSION=$JETBOT_VERSION"
    fi
done < "$input"

if [ -z $JETBOT_VERSION ]; then
    JETBOT_VERSION=0.4.2
fi

echo "export JETBOT_VERSION=$JETBOT_VERSION"

L4T_VERSION_STRING=$(head -n 1 /etc/nv_tegra_release)
L4T_RELEASE=$(echo $L4T_VERSION_STRING | cut -f 2 -d ' ' | grep -Po '(?<=R)[^;]+')
L4T_REVISION=$(echo $L4T_VERSION_STRING | cut -f 2 -d ',' | grep -Po '(?<=REVISION: )[^;]+')

export L4T_VERSION="$L4T_RELEASE.$L4T_REVISION"
echo "export L4T_VERSION=$L4T_RELEASE.$L4T_REVISION"
export JETBOT_DOCKER_REMOTE=jetbot
echo "export JETBOT_DOCKER_REMOTE=$JETBOT_DOCKER_REMOTE"

if [[ "$L4T_VERSION" == "32.4.3" ]]
then
    # docker hub
    echo "export JETBOT_DOCKER_REMOTE=jetbot"
    export JETBOT_DOCKER_REMOTE=jetbot
elif [[ "$L4T_VERSION" == "32.4.4" ]]
then
    echo "export JETBOT_DOCKER_REMOTE=jetbot"
    export JETBOT_DOCKER_REMOTE=jetbot
fi

./set_nvidia_runtime.sh
sudo systemctl enable docker

# check system memory
SYSTEM_RAM_KILOBYTES=$(awk '/^MemTotal:/{print $2}' /proc/meminfo)

if [ $SYSTEM_RAM_KILOBYTES -gt 3000000 ]
then
    echo "export JETBOT_JUPYTER_MEMORY=500m"
    echo "export JETBOT_JUPYTER_MEMORY_SWAP=3G"
    export JETBOT_JUPYTER_MEMORY=500m
    export JETBOT_JUPYTER_MEMORY_SWAP=3G
fi



