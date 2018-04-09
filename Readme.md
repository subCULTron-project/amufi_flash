# aMuFi_Flash
#### *A script that flashes a subcultron aMussel or aFish with a fresh, correctly named and numbered image.*

### Usage:
```
amufi_flash.py [-h] [-p] [-f] [-c] [-n NUMBER] [-i IMAGE] [-v] [-s] [-cr] dev
```

+ **-h , --help**

+ **-p, --partition** -- partition 

+ **-f, --format** -- format data partition to ext4

+ **-c, --copy_image** -- flash the image

parser.add_argument('-n', '--number',  action='store',
                    help='specify the agent-number the image should be configured for')
parser.add_argument('-i', '--image',  action='store',
                    help="specify imagefile to be copied, default can be configured in 'config.ini'")
parser.add_argument('-v', '--verbose', action='store_true',
                    help='detailed output')
parser.add_argument('-s', '--size', action='store_true',
                    help='get size in bytes of device')
parser.add_argument('-cr', '--cardreader', action='store_true',
                    help='use cardreader instead of usb (changes partition prefix)')
parser.add_argument('dev', action='store',
                    help='device location of sd card')
