import random
import numpy as np
import math
import struct

def rand_complex(x):
    r = random.random() * x
    i = math.sqrt(x * x - r * r)
    return np.complex(r, i)

def ph(x):
    return struct.pack('<h', x)

N = 400
DEST = 137

def get_byte(byte):
    N = 400
    DEST = 137
    a = [np.complex(0, 0)] * (N / 2 + 1)
    a[DEST] = rand_complex(float(byte) / 256 * N / 2)
    a = np.fft.irfft(a, N)
    a = [int(x * 32768) for x in a]
    return ''.join(map(ph, a))

