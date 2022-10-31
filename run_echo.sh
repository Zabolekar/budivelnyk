#!/bin/sh

python3.10 compile.py echo.bf echo.s
gcc -shared -o libecho.so echo.s
python3.10 call_echo.py
