#!/bin/sh

PS_CMD="/bin/ps -ef"

WORK_DIR=$(dirname $(cd "$(dirname "$0")"; pwd))
PYSCRIPTS_PATH=$WORK_DIR/src
CONFIG_PATH=$WORK_DIR/conf
SCRIPTS_PATH=$WORK_DIR/scripts

REPLACE_STR='s#%ProjectHome%#'$WORK_DIR'#g'
sed -i $REPLACE_STR $CONFIG_PATH/supervisor.ini

start() {
    export PYTHONPATH=$PYTHONPATH:$PYSCRIPTS_PATH
    export PYTHON_EGG_CACHE=/var/tmp
    python -m supervisor.supervisord -c $CONFIG_PATH/supervisor.ini
}

wait_stop() {
    cnt=0         
    while [[ `$PS_CMD | grep -w "supervisor.ini" | grep -v grep` != "" ]]; do
        sleep 1
        let cnt+=1
        if [[ $cnt -gt 30 ]]; then
            break
        fi
    done
}

stop() {
    for i in `$PS_CMD | grep -w "supervisor.ini" | grep -v grep | awk '{ print $2 }'`
    do
        /bin/kill $i > /dev/null 2>&1
    done
    wait_stop
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
    start
    ;;

*)
    echo "usage: $0 start|stop|restart"
    exit 1
    ;;
esac


