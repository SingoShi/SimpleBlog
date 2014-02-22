#!/bin/sh

PS_CMD="/bin/ps -ef"

WORK_DIR=$(dirname $(cd "$(dirname "$0")"; pwd))
PYSCRIPTS_PATH=$WORK_DIR/src
CONFIG_PATH=$WORK_DIR/conf
SCRIPTS_PATH=$WORK_DIR/scripts

REPLACE_STR='s#%ProjectHome%#'$WORK_DIR'#g'
sed -i $REPLACE_STR $CONFIG_PATH/nginx.conf
chmod 777 -R $WORK_DIR/frontend

start()
{
    export PATH=/usr/local/nginx/sbin:$PATH
    nginx -c $CONFIG_PATH/nginx.conf
}

wait_stop() {
    cnt=0         
    while [[ `$PS_CMD | grep -w "$CONFIG_PATH/nginx.conf" | grep -v grep` != "" ]]; do
        sleep 1
        let cnt+=1
        if [[ $cnt -gt 30 ]]; then
            break
        fi
    done
}

stop()
{
    export PATH=/usr/local/nginx/sbin:$PATH
    nginx -s stop -c $CONFIG_PATH/nginx.conf > /dev/nulll 2>&1
}

case "$1" in
'start')
    start
    ;;

'stop')
    stop
    ;;

'restart')
    stop
    wait_stop
    start
    ;;

*)
    echo "usage: $0 start|stop|restart"
    exit 1
    ;;
esac


