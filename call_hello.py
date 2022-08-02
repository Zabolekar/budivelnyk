from ctypes import CDLL, c_char

buffer = bytearray(6)

c_array_type = c_char * len(buffer)
libhello = CDLL("./libhello.so")
libhello.run(c_array_type.from_buffer(buffer))
