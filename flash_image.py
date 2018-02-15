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

    parser.add_argument('-p', '--partition', action='store_true',
                        help='partition sd-card to "system" and "data" partition')
    parser.add_argument('-f', '--format', action='store_true',
                        help='format sd-card partitions to ext4')
    parser.add_argument('-c', '--copy_image', action='store_true',
                        help='copy image to "system" parition')
    parser.add_argument('-n', '--num',  action='store',
                        help='specify the agent-number the image should be configured for')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='detailed output')
    parser.add_argument('--force', action='store_true',
                        help='no safety checks')

    # parser.add_argument('-po', '--partition_only', action='store_true',
    #                     help='only do the partition')
    # parser.add_argument('-fo', '--format_only', action='store_true',
    #                     help='only do the formatting')
    # parser.add_argument('-co', '--copy_image_only', action='store_true',
    #                     help='only do the flashing of the image')

    parser.add_argument('-no', '--number_image_only', action='store_true',
                        help='only do the numbering/configuration of the image')

    return parser.parse_args()


def checks(args):
    """Check if device exists, has a filesystem on it already or has data on it.
    Several additional checks to mitigate risks of overwriting unintentionally.
    """
    dev = args.dev

    # device exists
    if not os.path.exists(dev):
        print("Error: device '{}' does not exist.".format(dev))
        sys.exit()
    # device is not a partition
    if dev[-1:].isdigit():
        print("Error: '{}' is probably a partition, use the device name, e.g. '/dev/sda'.".format(dev))
        sys.exit()

    # check if target device is a aMussel/aFish sd-card already
    try:
        if (subprocess.getoutput('e2label {}'.format(dev+str(1))) == 'system') and          (subprocess.getoutput('e2label {}'.format(dev+str(2))) == 'data'):
            print("Info: Device '{}' is likely a partitioned and formatted aMussel/aFish sd-card.".format(dev))
            print("continue? n/[Y]")
            k = input()
            if k == 'n':
                sys.exit()
            return
    except subprocess.CalledProcessError:
        print("checks(): subprocess error while calling commands.")
        sys.exit()

    # probably the wrong device - checks
    part_init=3
    part=part_init
    while True:
        if os.path.exists(dev+str(part)):
            print("Warning: '{}' exists, correct device?".format(dev+str(part)))
            part += 1
        else:
            break
    if part > part_init:
        print(
            "Having more than two partition hints at the target not being an empty sd-card or a aMu or aFi card.")
        print("continue? n/[Y]")
        k = input()
        if k == 'n':
            sys.exit()
        return



def partition(args, conf):
    """Construct the fdisk partition command and call the partition bash script to execute the command with the given options
    """
    sys_part_size=conf['DEFAULT']['SystemPartitionSize']

    print("Partitioning device {}: system - {}MB ; data - <device-size> -{}MB.".format(
        args.dev, sys_part_size, sys_part_size))

    # create partition command
    partition_script_path=os.path.join(dir_path, 'partition.sh')
    cmd=[partition_script_path, str(args.dev), str(sys_part_size)]

    if args.verbose:
        print("* Executing command: {} ...".format(" ".join(cmd)))

    # execute partition command
    try:
        subprocess.call(cmd, stdout=dev_null, stderr=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(" ".join(cmd)))
        sys.exit()

    if args.verbose:
        print(" -->  Formatted {}1 and {}2.\n".format(args.dev, args.dev))



def format(args, conf):
    """Format partitions 1 and 2 to ext4
    """
    dev=args.dev
    if args.verbose:
        print("Formatting devices {}1 and {}2 with ext4.".format(dev, dev))

    # create format partition commands
    cmd1=['mkfs.ext4', str('-L'), str('system'), str(dev+'1')]

    cmd2=['mkfs.ext4', str('-L'), str('data'), str(dev+'2')]

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
        print(" -->  Formatted ... \n      {}1 to ext4, labeled 'system'\n      {}2 to ext4, labeled 'data'\n".format(dev, dev))



def copy(args, conf):
    """ Flash the system partition of the sd with the image specified in 'config.ini' or in the 'image' cmd-line argument. Test if flashing was successful.
    """
    img=os.path.join(dir_path, conf['DEFAULT']['Image'])
    dev=args.dev

    if args.verbose:
        print("Flashing device {}1 with image {}.".format(dev, img))

    # create flashing command
    cmd=['dd', str('if={}'.format(img)), str(
        'of={}1'.format(dev)), str('status=progress'), str('bs=4M')]
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
    conf=configparser.ConfigParser()
    conf.read(conf_file)

    # parsing args
    args=initArgParse()

    # program start
    print("\n*aMuFi_flash*\n")

    # safety test: check if device is empty:
    if not args.force:
        checks(args)
    else:
        print("--force, no safety checks!")

    # partition:
    if args.partition:
        partition(args, conf)

    # format:
    if args.format:
        format(args, conf)

    # copy:
    if args.copy_image:
        copy(args, conf)

if __name__ == "__main__":
    main()
