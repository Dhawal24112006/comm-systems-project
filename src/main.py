import numpy as np
import config
from modulators import BPSKModulator
from pulse_shaping import PulseShaper
from channel import WirelessChannel
from receiver import Receiver

class SimpleAdaptation:
    AVAILABLE_MODS = sorted(config.MODULATION_SCHEMES.keys())

    def __init__(self):
        self.mod_idx = 0 
        self.consecutive_acks = 0

    @property
    def current_mod_order(self):
        return self.AVAILABLE_MODS[self.mod_idx]

    def update(self, ack: bool):
        if ack:
            self.consecutive_acks += 1
            if self.consecutive_acks >= config.N_UP_ACKS:
                if self.mod_idx < len(self.AVAILABLE_MODS) - 1:
                    self.mod_idx += 1
                self.consecutive_acks = 0
        else:
            self.consecutive_acks = 0
            if self.mod_idx > 0:
                self.mod_idx -= 1 


def sim_loop(total_slots = 50):
    pulse_shaper = PulseShaper(config.RRC_ROLLOFF, config.RRC_SPAN, config.SPS)
    channel = WirelessChannel(config)
    # adapter = SimpleAdaptation()

    current_payload_bits = None
    current_block_id = 0
    retry_count = 0
    
    total_unique_bits_delivered = 0
    total_retransmissions = 0
    ack_count = 0
    nack_count = 0

    print("=" * 85)
    print(f"{'Slot':<5} | {'BlockID':<7} | {'ARQ State':<16} | {'Modulation':<8} | {'ACI':<5} | {'Errors':<8} | {'Feedback':<8}")
    print("=" * 85)

    for slot_idx in range(total_slots):
        period = config.ACI_BURST_BLOCKS_ON + config.ACI_BURST_BLOCKS_OFF
        aci_active = (slot_idx % period) < config.ACI_BURST_BLOCKS_ON

        # current_m = adapter.current_mod_order
        current_m = 1
        modulator = BPSKModulator()
        receiver = Receiver(pulse_shaper, modulator)

        if current_payload_bits is None:
            arq_state_str = "TX"
            current_block_id += 1
            retry_count = 0
            num_bits = config.N_SYM_PER_BLOCK * current_m
            current_payload_bits = np.random.randint(0, 2, size=num_bits)
        else:
            # STATE: RETRANSMISSION
            retry_count += 1
            total_retransmissions += 1
            arq_state_str = f"RETRY #{retry_count}"
            
            required_bits = config.N_SYM_PER_BLOCK * current_m
            if len(current_payload_bits) != required_bits:
                current_payload_bits = np.random.randint(0, 2, size=required_bits)

        tx_symbols = modulator.modulate(current_payload_bits)
        tx_waveform = pulse_shaper.tx_filter(tx_symbols)
        rx_waveform = channel.pass_through(tx_waveform, aci_active=aci_active)

        result = receiver.process_block(rx_waveform, current_payload_bits)
        ack_status = result['ack']

        # adapter.update(ack_status)

        print(f"{slot_idx:<5d} | #{current_block_id:<6d} | {arq_state_str:<16s} | {current_m}-BPS   | "
              f"{'ON ' if aci_active else 'OFF'} | {result['bit_errors']:<2d}/{len(current_payload_bits):<5d} | "
              f"{'[ ACK ]' if ack_status else '[NACK]':<8s}")

        if ack_status:
            ack_count += 1
            total_unique_bits_delivered += len(current_payload_bits)
            current_payload_bits = None
        else:
            nack_count += 1

    total_time_sec = total_slots * (config.N_SYM_PER_BLOCK / config.SYMBOL_RATE)
    goodput_bps = total_unique_bits_delivered / total_time_sec

    print("\n" + "=" * 85)
    print("SIMULATION SUMMARY")
    print("=" * 85)
    print(f"Total Time Slots Executed  : {total_slots}")
    print(f"Unique Blocks Delivered    : {current_block_id if current_payload_bits is None else current_block_id - 1}")
    print(f"Total Retransmissions Sent : {total_retransmissions}")
    print(f"ACK Count / NACK Count     : {ack_count} / {nack_count}")
    print(f"Total Unique Bits Delivered: {total_unique_bits_delivered} bits")
    print(f"Achieved Goodput           : {goodput_bps / 1e6:.4f} Mbps[cite: 4, 7]")
    print("=" * 85)

if __name__ == '__main__':
    sim_loop(total_slots=50)
