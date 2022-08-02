from ctypes import CDLL, c_char

buffer = bytearray(b"Gdkkn+\x1fw75^53 \0")

c_array_type = c_char * len(buffer)
libinc = CDLL("./libinc.so")
libinc.run(c_array_type.from_buffer(buffer))

print(buffer.decode())
