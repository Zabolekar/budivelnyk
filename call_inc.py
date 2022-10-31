from ctypes import CDLL

libinc = CDLL("./libinc.so")
buffer = b"Gdkkn+\x1f`rrdlakx "
libinc.run(buffer)
print(buffer.decode())
