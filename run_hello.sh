#!/bin/sh

python3.10 compile.py hello.bf hello.s
gcc -c -Wall -fpic hello.s
gcc -shared -o libhello.so hello.o
python3.10 call_hello.py
