#!/usr/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: partition.sh [DEV]!"
    exit 1
fi

# The sed script strips off all the comments so that we can
# document what we're doing in-line with the actual commands
# Note that a blank line (commented as "defualt" will send a empty
# line terminated with a newline to take the fdisk default.
sed -e 's/\s*\([\+0-9a-zA-Z]*\).*/\1/' << EOF | fdisk $1
  n # new partition
  p # primary partition
  3  # partition number 3
    # default - start at beginning of empty space
    # default - end at the end of disk

  p # print the in-memory partition table
  w # write out partition table
  q # and we're done
EOF