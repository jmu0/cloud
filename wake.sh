server1='00:1c:23:ba:38:77'
server2='00:1b:78:6e:5b:96'
cloud01='00:0f:fe:58:c2:f4'
htpc='50:e5:49:be:e8:9e'

if [ $1 == 'server2' ]; then
    echo "waking $1"
    wol $server2
elif [ $1 == 'server1' ]; then
    echo "waking $1"
    wol $server1
elif [ $1 == 'cloud01' ]; then
    echo "waking $1"
    wol $cloud01
elif [ $1 == 'htpc' ]; then
    echo "waking $1"
    wol $htpc
fi
