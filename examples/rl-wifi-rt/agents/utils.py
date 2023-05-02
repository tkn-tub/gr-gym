import numpy as np

def float_to_bin_vec(v, no_bits=10):
    scale = np.power(2, no_bits-1)

    # convert to binary vector
    y = list(bin(round(v * scale))[2:])
    y = [int(v) for v in y]
    y2 = list(np.zeros(no_bits - len(y)))
    y2.extend(y)

    return np.reshape(y2, [1, no_bits])

def bin_vec_to_float(b, no_bits=10):
    p = [np.power(2, x) for x in range(no_bits-1, -1, -1)]
    scale = np.power(2, no_bits-1)
    y = sum(b[0] * p) / scale

    return y