import struct
import numpy as np
print(np.dtype('int32').itemsize)
f = open('../tmp/myfiledump.bin', "rb")
while True:
    buf = f.read(int(np.dtype('int32').itemsize))
    if len(buf) == 0:
        break
    tmp = np.frombuffer(buf, dtype=np.dtype('int32'))
    print(tmp)
