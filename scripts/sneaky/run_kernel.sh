#!/bin/sh

DEBUG=""

if [  "$1" = "-d" ]; then
    DEBUG="-s -S"
fi

qemu-system-i386 \
    -drive format=raw,file=bin/os.img \
    -serial stdio \
    $DEBUG
