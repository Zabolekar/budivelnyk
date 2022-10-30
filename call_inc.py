from ctypes import CDLL

libinc = CDLL("./libinc.so")
buffer = b"Gdkkn+\x1fw75^53 "
libinc.run(buffer)
print(buffer.decode())
