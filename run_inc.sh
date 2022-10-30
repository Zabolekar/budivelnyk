#!/bin/sh

python3.10 compile.py inc.bf inc.s
gcc -shared -o libinc.so inc.s
python3.10 call_inc.py
