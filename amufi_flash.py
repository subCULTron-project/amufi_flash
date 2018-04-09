#!/usr/bin/env python3
import argparse
import configparser
import fileinput
import os
import re
import subprocess
import sys
import time


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
    parser.add_argument('-n', '--number',  action='store',
                        help='specify the agent-number the image should be configured for')
    parser.add_argument('-i', '--image',  action='store',
                        help="specify imagefile to be copied, default can be configured in 'config.ini'")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='detailed output')
    parser.add_argument('--force', action='store_true',
                        help='no safety checks')
    parser.add_argument('-s', '--size', action='store_true',
                        help='get size in bytes of device')

    parser.add_argument('-cr', '--cardreader', action='store_true',
                        help='use cardreader instead of usb (changes partition prefix)')
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
    print('* Device path OK')

    # check for signs that it is the wrong device by comparing to the size of bytes specified in conf.
    fd = os.open(dev, os.O_RDONLY)
    try:
        size = int(os.lseek(fd, 0, os.SEEK_END))
    finally:
        os.close(fd)
    if size != int(conf['DEFAULT']['SDSize']):
        print("WARNING: Device '{}' has a different size than specified in the conf file!".format(dev))
        print("WARNING: Specified: {}".format(conf['DEFAULT']['SDSize']))
        print("WARNING: Detected : {}".format(size))

        print("continue? [N]/y")
        k = input()
        if k != 'y':
            sys.exit()
    print('* Device size OK')

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
    print('* Image path OK')
    print("*** Basic checks OK. \n")


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

    print("* Partitioning the unused space on device {} for a data partition.".format(dev))

    # create partition command
    partition_script_path = os.path.join(dir_path, 'partition.sh')
    cmd = [partition_script_path, str(args.dev)]

    if args.verbose:
        print("* Executing command: {} ...".format(" ".join(cmd)))

    # execute partition command
    try:
        subprocess.call(cmd, stdout=dev_null, stderr=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(" ".join(cmd)))
        sys.exit()
    # the 'Re-reading the partition table failed.: Device or resource busy' warning is suppressed here,
    # since partprobe is called to update partitiontable in kernel here
    try:
        cmd = ['partprobe' , dev]
        subprocess.call(cmd, stdout=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(cmd))
        sys.exit()

    print("*** Partitioning done.\n")


def format(args, conf):
    """Format partitions3 to ext4
    """
    dev = args.dev

    # determine correct partition prefix
    if args.cardreader:
        part = conf['CARDREADER']['DataPart']
    else:
        part = conf['DEFAULT']['DataPart']
    print("* Formatting data partition {}{} to ext4.".format(dev,part))

    # create format partition commands
    cmd = ['mkfs.ext4', '-L', 'data', '-F', dev+part]

    if args.verbose:
        print("* Executing command: {}".format(cmd))
    try:
        subprocess.call(cmd, stdout=dev_null)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(" ".join(cmd)))
        sys.exit()

    print("*** Formatting done.\n")


def number(args, conf):
    """Configure the hostname, and ip settings of the target device.
    """
    dev = args.dev

    # determine correct partition prefix
    if args.cardreader:
        part = conf['CARDREADER']['SysPart']
    else:
        part = conf['DEFAULT']['SysPart']

    # mount flashed image to 'mnt'
    mnt_folder = conf['DEFAULT']['Mountpoint']
    if not os.path.exists(mnt_folder):
        os.system('mkdir {}'.format(mnt_folder))

    mount_return_code = os.WEXITSTATUS(os.system("mount {}{} mnt".format(dev, part)))
    if mount_return_code != 32 and mount_return_code != 0: # 32 means already mounted
        print("Error: could not mount {}{}".format(dev, part))
        sys.exit()

    NEW_HOSTNAME = "aMussel"+args.number

    # hostname file
    print("* Setting hostname in file "+conf["PATHS"]["HostNamePath"]+" to "+NEW_HOSTNAME)
    f = open(conf["PATHS"]["HostNamePath"], 'w')
    f.write(NEW_HOSTNAME+ os.linesep)
    f.close()

    # hosts file
    print("* Setting hostname in file "+conf["PATHS"]["HostsPath"]+" to "+NEW_HOSTNAME)
    r = re.compile(r"(127\.0\.1\.1).*$")
    with fileinput.FileInput(conf["PATHS"]["HostsPath"], inplace=True, backup='.bak') as file:
        for line in file:
            print(r.sub(r"\1   %s" % NEW_HOSTNAME, line), end='')

    # interfaces file
    ip_num = args.number
    print("* Setting ip in file "+conf["PATHS"]["InterfacesPath"]+" to end with "+ip_num)
    r = re.compile(r"(address).*$")
    with fileinput.FileInput(conf["PATHS"]["InterfacesPath"], inplace=True, backup='.bak') as file:
        for line in file:
            print(r.sub(r"\1 %s" % "10.0.200."+ip_num, line), end='')


    # print("lsof:")
    # os.system('lsof +D mnt')
    # unmount and remove temp mnt folder
    os.system('umount {}'.format(mnt_folder))

    print("*** Numbering done.")



def main():
    """Main function
    """
    # configuragtion parsing
    conf = configparser.ConfigParser()
    conf.read(conf_file)

    # parsing args
    args = initArgParse()

    # program start
    print("\n# aMuFi_flash #\n")

    # just check device size:
    if args.size:
        fd = os.open(args.dev, os.O_RDONLY)
        try:
            size = int(os.lseek(fd, 0, os.SEEK_END))
            print(size)
        finally:
            os.close(fd)
            print("Device {} size: {}".format(args.dev, size))
            sys.exit()


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
    if args.number:
        number(args, conf)


if __name__ == "__main__":
    main()
