from ctypes import CDLL

libhello = CDLL("./libhello.so")
buffer = bytes(3)
libhello.run(buffer)
