import numpy as np

def generate_rrc_filter(alpha, span, samples_per_sym):
    n_samples = span * samples_per_sym
    t = np.arange(-n_samples / 2, n_samples / 2 + 1) / samples_per_sym
    h = np.zeros_like(t, dtype=np.float64)

    for i, ti in enumerate(t):
        if ti == 0.0:
            h[i] = 1.0 - alpha + (4.0 * alpha / np.pi)
        elif abs(abs(ti) - 1.0 / (4.0 * alpha)) < 1e-6:
            h[i] = (alpha / np.sqrt(2.0)) * (
                (1.0 + 2.0 / np.pi) * np.sin(np.pi / (4.0 * alpha)) +
                (1.0 - 2.0 / np.pi) * np.cos(np.pi / (4.0 * alpha))
            )
        else:
            denom = np.pi * ti * (1.0 - (4.0 * alpha * ti)**2)
            num = np.sin(np.pi * ti * (1.0 - alpha)) + 4.0 * alpha * ti * np.cos(np.pi * ti * (1.0 + alpha))
            h[i] = num / denom

    return h / np.sqrt(np.sum(h**2))


class PulseShaper:
    def __init__(self, alpha, span, samples_per_sym):
        self.samples_per_sym = samples_per_sym
        self.span = span
        self.rrc_filter = generate_rrc_filter(alpha, span, samples_per_sym)
        self.delay_samples = (span * samples_per_sym) // 2

    def tx_filter(self, symbols: np.ndarray) -> np.ndarray:
        upsampled = np.zeros(len(symbols) * self.samples_per_sym, dtype=np.complex128)
        upsampled[::self.samples_per_sym] = symbols
        tx_waveform = np.convolve(upsampled, self.rrc_filter, mode='full')
        return tx_waveform

    def rx_matched_filter(self, rx_waveform: np.ndarray, num_symbols: int) -> np.ndarray:
        mf_output = np.convolve(rx_waveform, self.rrc_filter, mode='full')
        total_delay = 2 * self.delay_samples
        
        sample_indices = total_delay + np.arange(num_symbols) * self.samples_per_sym
        return mf_output[sample_indices]
