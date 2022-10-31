from ctypes import CDLL

libecho = CDLL("./libecho.so")
buffer = bytes(1)
libecho.run(buffer)
print()
