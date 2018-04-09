# aMuFi_Flash
#### *A script that flashes a subcultron aMussel or aFish with a fresh, correctly named and numbered image.*



### Usage:

```
amufi_flash.py [-h] [-p] [-f] [-c] [-n NUMBER] [-i IMAGE] [-v] [-s] [-cr] [--fish] dev
```



#### Positional arguments:

**dev**                   device location of sd card



#### Optional arguments:


**-h, --help**            show this help message and exit

**-p, --partition**       partition the remaining space on the sd card after flashing the image

**-f, --format**          format the created data partition to ext4

**-c, --copy_image**      flash the specified image (with -i or in the config file)

**-n NUMBER, --number NUMBER**  specify the agent-number the image should be configured for

**-i IMAGE, --image IMAGE**  specify imagefile to be copied, default can be configured in 'config.ini'

**-s, --size**            just get size in bytes of device and exit

**-g, --garbage**            add some prime garbage to the output 

**-cr, --cardreader**     use cardreader instead of usb (changes partition prefix)

**--fish**                the target agent is an aFish, ensures that the correct IP and naming scheme are used



#### Examples:

```
amufi_flash.py -cpf -n 69 /dev/sda
```
*Flashes the in the config.ini under 'Image' specified image, partitions the remaining space on the sd card and formats it to ext4. The hostname and IP are configured to the number 69 (aMussel69, 10.0.200.69).*

```
amufi_flash.py -s /dev/sda
```
*Shows the size of the blockdevice /dev/sda in bytes. Since the script tests for this before flashing, whenever you use a new, not standard subcultron sandisd 16G sd card, this needs to be updated in the config.ini under 'SDSize'.*

```
amufi_flash.py -cr -cpf -i Other_image.img /dev/mmcblk0
```
*Just like example one, except the image to be flashed is now implicitly specified and since an internal cardreader is used, the '-cr' option is given to have the correct partition prefix (mmcblk0**p2** instead of sda**2**) [todo: automate this]*