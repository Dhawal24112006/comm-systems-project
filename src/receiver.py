import numpy as np

class Receiver:
    def __init__(self, pulse_shaper, modulator):
        self.pulse_shaper = pulse_shaper
        self.modulator = modulator

    def process_block(self, rx_waveform, tx_info_bits):
        num_symbols = len(tx_info_bits) // self.modulator.order
        rx_symbols = self.pulse_shaper.rx_matched_filter(rx_waveform, num_symbols)
        rx_bits = self.modulator.demodulate(rx_symbols)
        bit_errors = int(np.sum(tx_info_bits != rx_bits))
        ack = (bit_errors == 0)

        return {
            'rx_bits': rx_bits,
            'bit_errors': bit_errors,
            'ack': ack,
            'ber': bit_errors / len(tx_info_bits)
        }
