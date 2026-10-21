import numpy as n

SYMBOL_RATE = 1e6
SPS = 8     # Samples per symbol
FS = SYMBOL_RATE * SPS      # Sampling frequency (8 MHz)

RRC_ROLLOFF = 0.35
RRC_SPAN = 8        # cutoff RRC pulse after RRC_SPAN symbol periods
CHANNEL_BW = SYMBOL_RATE * (1 + RRC_ROLLOFF)

N_SYM_PER_BLOCK = 300
HEADER_LEN_BITS = 16    # BPSK header carrying Block ID & Modulation ID
HEADER_MOD_ORDER = 1    # BPSK for header

MODULATION_SCHEMES = {
    1: 'BPSK',
    2: 'QPSK',
    4: '16-QAM',
    6: '64-QAM'
}
DEFAULT_MOD_ORDER = 1

PA_TYPE = 'linear'  # 'linear' or 'nonlinear'
PA_A1 = 1.0
PA_A3 = -0.08

SNR_DB = 15.0   # Es/N0 in dB

ACI_ENABLED = True
ACI_FREQ_OFFSET = 1.35 * SYMBOL_RATE 
ACI_POWER_DB = 8.0
ACI_DUTY_CYCLE = 0.30

ACI_BURST_BLOCKS_ON = 100       # Duration of ACI active pulse in blocks
ACI_BURST_BLOCKS_OFF = 200      # Duration of ACI idle pulse in blocks[
