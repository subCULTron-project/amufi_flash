#!/usr/bin/env python3
import argparse
import configparser
import os
import subprocess
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
conf_file = os.path.join(dir_path, 'config.ini')


def main():
    """Main funtion
    """
    # configuragtion parsing
    config = configparser.ConfigParser()
    config.read(conf_file)

    sys_part_size = config['DEFAULT']['SystemPartitionSize']


    # cmd line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('dev', action='store',
                        help='device location of sd card')

    parser.add_argument('-a','--agent',  action='store',                        
                        help='specify the agent type [aMussel | aFish]')
    parser.add_argument('-n','--num',  action='store',                    
                        help='specify the number for the generated image for aMussel | aFish')
    parser.add_argument('-f', '--force', action='store_true',
                        help='no comfirmations required during run')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='detailed output')
    args = parser.parse_args()
    dev = args.dev

    print("*aMuFiFlash*")
    print("$$$")
    
    print("Flashing device {} with {} MB system- and <device-size> -{} MB data partition.".format(dev.upper(), sys_part_size, sys_part_size))

    if not args.force:
        print("Press the <enter> key to continue...")
        input()

    partition_script_path = os.path.join(dir_path, 'partition.sh')
    cmd = [partition_script_path, str(dev),str(sys_part_size)]

    if args.verbose:
        print("Command: {}".format(" ".join(cmd)))

    try:
        output = subprocess.check_output(cmd)
    except subprocess.CalledProcessError:
        print("subprocess error while calling '{}'.".format(" ".join(cmd)))
        sys.exit()

    print(str(output))
    

if __name__ == "__main__":
    main()
