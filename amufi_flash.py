#!/usr/bin/env python3
import argparse
import configparser
import os
import subprocess
import sys
import time

from utils import Checks

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
    # parser.add_argument('-n', '--number',  action='store',
    #                     help='specify the agent-number the image should be configured for')

    parser.add_argument('-i', '--image',  action='store',
                        help="specify imagefile to be copied, default can be configured in 'config.ini'")

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='detailed output')
    parser.add_argument('--force', action='store_true',
                        help='no safety checks')

    return parser.parse_args()


def checks(args, conf):
    """Check if device exists, has a filesystem on it already or has data on it.
    Several additional checks to mitigate risks of overwriting data unintentionally.
    """
    dev = args.dev

    # device exists
    if not os.path.exists(dev):
        print("Error: device '{}' does not exist.".format(dev))
        sys.exit()

    # check if target device is a aMussel/aFish sd-card already by checking for labels of partitions
    # try:
    #     if (subprocess.getoutput('e2label {}'.format(dev+str(1))) == 'system') and (subprocess.getoutput('e2label {}'.format(dev+str(2))) == 'data'):
    #         print(
    #             "Info: Device '{}' is likely a partitioned and formatted aMussel/aFish sd-card.".format(dev))
    #         print("continue? n/[Y]")
    #         k = input()
    #         if k == 'n':
    #             sys.exit()
    # except subprocess.CalledProcessError:
    #     pass
        # print("checks: subprocess error while calling commands.")
        # sys.exit()

    # check for signs that it is the wrong device by comparing to the size of bytes specified in conf.
    fd = os.open(dev, os.O_RDONLY)
    try:
        size = str(os.lseek(fd, 0, os.SEEK_END))
        print(size )
    finally:
        os.close(fd)
    if int(size) != int(conf['DEFAULT']['SDSize']): 
        print("WARNING: Device '{}' has a different size than specified in the conf file!".format(dev))
        print("WARNING: Specified: {}".format(conf['DEFAULT']['SDSize']))
        print("WARNING: Detected : {}".format(size))

        print("continue? [N]/y")
        k = input()
        if k != 'y':
            sys.exit()


    # if copying image: image exists?
    try:
        # image from cmd-line arg
        if args.image:
            img = os.path.join(dir_path, args.image)
            if not os.path.exists(img):
                print("Error: image '{}' does not exist.".format(img))
                sys.exit()

        # image specified in 'config/ini'
        img = os.path.join(dir_path, conf['DEFAULT']['Image'])
        if not os.path.exists(img):
            print("Error: image '{}' does not exist.".format(img))
            sys.exit()

    except NameError:
        pass

    print("* Basic checks OK.")


def copy(args, conf):
    """ Flash the system partition of the sd with the image specified in 'config.ini' or in the 'image' cmd-line argument. Test if flashing was successful.
    """
    img = os.path.join(dir_path, conf['DEFAULT']['Image'])
    dev = args.dev

    print("Flashing device {} with image {}.".format(dev, img))

    # create flashing command
    cmd = ['dd', str('if={}'.format(img)), str(
        'of={}'.format(dev)), str('bs=4M')]
    if args.verbose:
        print("* Executing command: {} ...".format(" ".join(cmd)))

    # execute command
    try:
        subprocess.call(cmd, stdout=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(" ".join(cmd)))
        sys.exit()
    print("Flashing done.\n")


def partition(args, conf):
    """Construct the fdisk partition command and call the partition bash script to execute the command with the given options
    """
    dev = args.dev

    print("Partitioning the unused space on device {}.".format(dev))

    # create partition command
    partition_script_path = os.path.join(dir_path, 'partition.sh')
    cmd = [partition_script_path, str(args.dev)]

    if args.verbose:
        print("* Executing command: {} ...".format(" ".join(cmd)))

    # execute partition command
    try:
        subprocess.call(cmd, stdout=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(" ".join(cmd)))
        sys.exit()

    # execute partprobe to update partitiontable in kernel
    try:
        cmd = ['partprobe']  # , str(dev)]
        subprocess.call(cmd, stdout=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(cmd))
        sys.exit()

    print("Partitioning done.\n")


def format(args, conf):
    """Format partitions3 to ext4
    """
    dev = args.dev

    print("Formatting data partition to ext4.".format(dev))

    # create format partition commands
    cmd = ['mkfs.ext4', '-L', 'data', '-F', str(dev+'3')]

    if args.verbose:
        print("* Executing command: {}".format(cmd))
    try:
        subprocess.call(cmd, stdout=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(" ".join(cmd)))
        sys.exit()

    print("Formatting done.\n")


def number(args, conf):
    """Configure the hostname, and ip settings of the target device.
    """
    dev = args.dev

    # mount flashed image to 'mnt'
    mnt_folder = "mnt"
    os.system('mkdir {}'.format(mnt_folder))

    if os.WEXITSTATUS(os.system('mount {}1 mnt'.format(dev))) != 0:
        print("Error: Could not mount {}1.".format(dev))
        sys.exit()

    mountpoint = os.path.join(dir_path, mnt_folder)

    interfaces_path = os.path.join(
        mountpoint, conf.get('DEFAULT', 'InterfacesPath'))
    hosts_path = os.path.join(mountpoint, conf.get('DEFAULT', 'HostsPath'))
    hostname_path = os.path.join(
        mountpoint, conf.get('DEFAULT', 'HostnamePath'))

    print(interfaces_path)
    print(hostname_path)
    print(hosts_path)

    # check if files exist:
    # TODO:

    # unmount and remove temp mnt folder
    os.system('umount {}'.format(mnt_folder))
    os.system('rm -r {}'.format(mnt_folder))
    print("Numbering done.\n")


def main():
    """Main function
    """
    # configuragtion parsing
    conf = configparser.ConfigParser()
    conf.read(conf_file)

    # parsing args
    args = initArgParse()

    # program start
    print("\n aMuFi_flash")

    # safety test: check if device is empty:
    if not args.force:
        checks(args, conf)
    else:
        print("--force, no safety checks!")

    # copy:
    if args.copy_image:
        copy(args, conf)

    # partition:
    if args.partition:
        partition(args, conf)

    # format:
    if args.format:
        format(args, conf)

    # # number configs
    # if args.number:
    #     number(args, conf)


if __name__ == "__main__":
    main()
