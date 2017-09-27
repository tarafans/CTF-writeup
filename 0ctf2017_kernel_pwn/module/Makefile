obj-m += note.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
	sudo insmod note.ko
	sudo mknod /dev/knote c 1337 1
	sudo chmod a+rw /dev/knote

clean:
	sudo rmmod note.ko || true
	sudo rm /dev/knote || true
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
