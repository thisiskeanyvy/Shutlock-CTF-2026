#!/bin/sh

gdb \
    -x ./scripts/gdb_script.txt \
    --args ./bin/os.img
