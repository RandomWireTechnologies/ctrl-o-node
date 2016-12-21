# Basic makefile for building nfc program to interface to libnfc and read cards

nfc: nfc.c
	gcc -o nfc nfc.c -lnfc

clean:
	rm nfc
