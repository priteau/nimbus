#!/bin/sh

set -e

NMACHINES="$1"
UUID="$2"
FILE="/tmp/$2"

while [ `cat "$FILE" | wc -l` != "$NMACHINES" ]; do
  sleep 1
done

NODEFILE=`mktemp`
TAKTUK_COMMAND="/home/rennes/priteau/kastafior -d -1 -l nimbus -m localhost -f $NODEFILE -- -v"

# Parse the file populated by the control agents
LOCAL_PATH=`head -1 "$FILE" | cut -d: -f 1`
TAKTUK_COMMAND+=" -s 'cat $LOCAL_PATH'"

while read line; do
  HOSTNAME=`echo $line | cut -d: -f 2`
  REMOTE_PATH=`echo $line | cut -d: -f 3`

  echo $HOSTNAME >> $NODEFILE
  TAKTUK_COMMAND+=" -c 'cat >$REMOTE_PATH'"
done < "$FILE"

# Transfer the image with taktuk
SCRIPT=`mktemp`
echo $TAKTUK_COMMAND > $SCRIPT
sh $SCRIPT

if [ $? == 0 ]; then
  touch "$FILE.done"
else
  touch "$FILE.error"
  exit 1
fi

while [ `cat "$FILE.done" | wc -l` != "$NMACHINES" ]; do
  sleep 1
done

#rm -f "$FILE"
#rm -f "$FILE.lock"
#rm -f "$FILE.done"
#rm -f "$NODEFILE"
#rm -f "$SCRIPT"
