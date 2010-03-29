#!/bin/sh

set -e

NMACHINES=""
UUID=""
OLDIFS="$IFS"

while getopts ":n::u:" opt; do
  case $opt in
    n)
      NMACHINES="$OPTARG"
      ;;
    u)
      UUID="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

if [ "$NMACHINES" == "" -o "$UUID" == "" ]; then
  echo "error: arguments -n and -u required"
  exit 1
fi

FILE="/tmp/$UUID"
touch "$FILE"

nohup `dirname $0`/cluster_propagate_daemon.sh $NMACHINES $UUID 1>/tmp/$UUID.log 2>&1 &
