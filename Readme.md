# aMuFi_Flash
#### *A script that flashes a subcultron aMussel or aFish with a fresh, correctly named and numbered image.*

### Usage:
```
amufi_flash.py [-h] [-p] [-f] [-c] [-n NUMBER] [-i IMAGE] [-v] [-s] [-cr] dev
```



#### positional arguments:

...  **dev**                   device location of sd card



#### optional arguments:


...**-h, --help**            show this help message and exit

...**-p, --partition**       partition the remaining space on the sd card after flashing the image

...**-f, --format**          format the created data partition to ext4

...**-c, --copy_image**      flash the specified image (with -i or in the config file)

...**-n NUMBER, --number NUMBER**
......                       specify the agent-number the image should be configured for

...**-i IMAGE, --image IMAGE**
......                       specify imagefile to be copied, default can be configured in 'config.ini'


...**-s, --size**            just get size in bytes of device and exit

...**-cr, --cardreader**     use cardreader instead of usb (changes partition prefix)
