#!/bin/sh

if [ $# -ne 4 ]; then
  echo "error: not enough arguments"
  exit 1
fi

flock -w 10 /tmp/$1.lock -c "echo $2:$3:$4 >> /tmp/$1"

# Wait until taktuk transfer is done or failed
while [ ! -f /tmp/$1.done -a ! -e /tmp/$1.error ]; do
  sleep 1
done

if [ -f /tmp/$1.error ]; then
  echo "error: taktuk transfer failed"
  exit 1
fi

SHA1=`ssh nimbus@$3 sha1sum $4`
flock -w 10 /tmp/$1.lock -c "echo $3:$4:$SHA1 >> /tmp/$1.done"
