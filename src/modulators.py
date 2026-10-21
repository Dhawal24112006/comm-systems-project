import numpy as np

class BPSKModulator:
    def __init__(self):
        self.order = 1

    def modulate(self, bits):
        symbols = (1.0 - 2.0 * bits).astype(np.complex128)
        return symbols

    def demodulate(self, symbols):
        bits = (np.real(symbols) < 0.0).astype(int)
        return bits
