#!/bin/sh

python3.10 compile.py hello.bf hello.s
gcc -shared -o libhello.so hello.s
python3.10 call_hello.py
