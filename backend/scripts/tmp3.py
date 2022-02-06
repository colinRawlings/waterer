import struct

my_arr = bytearray(b"\x10'\x00\x00")

print(my_arr)


val = struct.unpack("<I", my_arr)[0]
print(val)

val = struct.unpack(">I", my_arr)[0]
print(val)


arr = struct.pack("<I", 10000)
print(arr)
