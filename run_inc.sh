#!/bin/sh

python3.10 compile.py inc.bf inc.s
gcc -c -Wall -fpic inc.s
gcc -shared -o libinc.so inc.o
python3.10 call_inc.py
