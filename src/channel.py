import numpy as np
from pulse_shaping import generate_rrc_filter

class WirelessChannel:
    def __init__(self, config):
        self.config = config

    def apply_power_amplifier(self, x):
        if self.config.PA_TYPE == 'linear':
            return self.config.PA_A1 * x
        else:
            return self.config.PA_A1 * x + 0.75 * self.config.PA_A3 * (np.abs(x)**2) * x

    def generate_aci(self, num_samples):
        aci_symbols = (1.0 - 2.0 * np.random.randint(0, 2, size=num_samples // self.config.SPS))
        
        upsampled = np.zeros(len(aci_symbols) * self.config.SPS, dtype=np.complex128)
        upsampled[::self.config.SPS] = aci_symbols
        rrc = generate_rrc_filter(self.config.RRC_ROLLOFF, self.config.RRC_SPAN, self.config.SPS)
        aci_baseband = np.convolve(upsampled, rrc, mode='same')

        t = np.arange(len(aci_baseband)) / self.config.FS
        aci_shifted = aci_baseband * np.exp(1j * 2.0 * np.pi * self.config.ACI_FREQ_OFFSET * t)

        aci_power_linear = 10.0 ** (self.config.ACI_POWER_DB / 10.0)
        current_power = np.mean(np.abs(aci_shifted)**2)
        if current_power > 0:
            aci_shifted *= np.sqrt(aci_power_linear / current_power)

        return aci_shifted

    def pass_through(self, tx_waveform, aci_active):
        composite_input = tx_waveform.copy()
        
        if self.config.ACI_ENABLED and aci_active:
            aci_signal = self.generate_aci(len(tx_waveform))
            min_len = min(len(composite_input), len(aci_signal))
            composite_input[:min_len] += aci_signal[:min_len]

        pa_output = self.apply_power_amplifier(composite_input)

        snr_linear = 10.0 ** (self.config.SNR_DB / 10.0)
        signal_power = np.mean(np.abs(pa_output)**2)
        noise_power = signal_power / snr_linear
        
        noise = (np.random.normal(0, np.sqrt(noise_power / 2.0), len(pa_output)) +
                 1j * np.random.normal(0, np.sqrt(noise_power / 2.0), len(pa_output)))

        return pa_output + noise
