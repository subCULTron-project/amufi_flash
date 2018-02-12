#!/usr/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: partition.sh [DEV] [SIZE OF BOOT IN MB]!"
    exit 1
fi

# The sed script strips off all the comments so that we can 
# document what we're doing in-line with the actual commands
# Note that a blank line (commented as "defualt" will send a empty
# line terminated with a newline to take the fdisk default.
sed -e 's/\s*\([\+0-9a-zA-Z]*\).*/\1/' << EOF | fdisk $1
  o # clear the in memory partition table
  n # new partition
  p # primary partition
  1  # partition number 1
    # default - start at beginning of disk 
  +$2M # create boot parttion (size specified in $2)
  a # make a partition bootable
    # bootable partition is partition 1 
  n # new partition
  p # primary partition
  2 # partion number 2
    # default, start immediately after preceding partition
    # default, extend partition to end of disk
  p # print the in-memory partition table
  w # write out partition table
  q # and we're done
EOF