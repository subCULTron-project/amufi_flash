#!/usr/bin/env python3
import argparse
import configparser
import os
import subprocess
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
conf_file = os.path.join(dir_path, 'config.ini')
dev_null = open(os.devnull, 'w')

def initArgParse():
    """Parse cmd-line arguments and return the parser
    """
    # cmd line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('dev', action='store',
                        help='device location of sd card')

    parser.add_argument('-if','--is_fish',  action='store_true',                
                        help='flashed sd is for aFish')

    parser.add_argument('-n','--num',  action='store',                    
                        help='specify the number for the generated image for aMussel | aFish')

    parser.add_argument('-f', '--force', action='store_true',
                        help='no comfirmations required during run')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='detailed output')

    parser.add_argument('-p', '--partition_only', action='store_true',
                        help='only do the partition')
   
    parser.add_argument('-i', '--image_only', action='store_true',
                        help='only do the flashing of the image')

    return parser.parse_args()


def partition(args, conf):
    """Construct the fdisk partition command and call the partition bash script to execute the command with the given options
    """
    sys_part_size = conf['DEFAULT']['SystemPartitionSize']

    print("Partitioning device {}: system - {}MB ; data - <device-size> -{}MB.".format(args.dev, sys_part_size, sys_part_size))

    # create partition command
    partition_script_path = os.path.join(dir_path, 'partition.sh')
    cmd = [partition_script_path, str(args.dev),str(sys_part_size)]

    if args.verbose:
        print("* Executing command: {} ...".format(" ".join(cmd)))

    # execute partition command
    try:
        subprocess.call(cmd, stdout=dev_null, stderr=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(" ".join(cmd)))
        sys.exit()

    if args.verbose:
        print(" -->  Formatted {}1 and {}2.\n".format(args.dev,args.dev))
 


def format(args, conf):
    """Format partitions 1 and 2 to ext4
    """
    dev = args.dev
    if args.verbose:
        print("Formatting devices {}1 and {}2 with ext4.".format(dev, dev))

    # create format partition commands
    cmd1 = ['mkfs.ext4', str('-L'),str('system'),str(dev+'1')]

    cmd2 = ['mkfs.ext4', str('-L'),str('data'),str(dev+'2')]
    
    if args.verbose:
        print("* Executing commands: \n* {} ...\n* {} ...".format(" ".join(cmd1), " ".join(cmd2)))
    try:
        subprocess.call(cmd1, stdout=dev_null, stderr=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(" ".join(cmd1)))
        sys.exit()

    try:
        subprocess.call(cmd2, stdout=dev_null, stderr=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(" ".join(cmd2)))
        sys.exit()
    
    if args.verbose:
        print(" -->  Formatted {}1 to ext4, labeled 'system', {}2 to ext4, labeled 'data'\n".format(dev, dev))



def flash(args, conf):
    """ Flash the system partition of the sd with the image specified in 'config.ini' or in the 'image' cmd-line argument. Test if flashing was successful.
    """
    img = os.path.join(dir_path, conf['DEFAULT']['Image'])
    dev = args.dev

    if args.verbose:
        print("Flashing device {}1 with image {}.".format(dev, img))

    # create flashing command
    cmd = ['dd', str('if={}'.format(img)), str('of={}1'.format(dev)), str('status=progress'), str('bs=4M')]
    if args.verbose:
        print("* Executing command: {} ...".format(" ".join(cmd)))

    # execute command
    try:
        subprocess.call(cmd, stdout=dev_null, stderr=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(" ".join(cmd)))
        sys.exit()

    if args.verbose:
        print(" --> Flashed image '{}' to device {}1\n".format(img, dev))


def main():
    """Main function
    """    
    # configuragtion parsing
    config = configparser.ConfigParser()
    config.read(conf_file)

    # parsing args
    args = initArgParse()

    ### program start
    print("*aMuFiFlash*")
    print("$$$")

    # partition sd
    if not args.image_only:
        partition(args, config)

    # format sd
    if not args.image_only:
        format(args, config)

    # flashing of image
    if not args.partition_only:
        flash(args, config)

    # naming and numbering



    

if __name__ == "__main__":
    main()
