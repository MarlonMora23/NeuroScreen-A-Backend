import gc
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

PREDEFINED_CHANNELS = [
    "F1", "F2", "F6", "FT7", "FT8", "FC3", "FC4", "FCZ",             # Frontal
    "O1", "O2",                                                      # Occipital
    "C1", "C2", "C3", "C4", "C5", "CP2", "CP3", "CP5", "CP6", "CPZ", # Central
    "AF7", "AF8",
    "P1", "P4", "P5", "P6", "P7", "P8", "PO1", "PO7", "O8",          # Parietal
    "T7", "T8", "TP7"
    ]

def normalize_signal(signal: np.ndarray) -> np.ndarray:
    """Z-score normalization of a signal"""
    if np.std(signal) > 1e-8:
        return (signal - np.mean(signal)) / np.std(signal)
    return signal

def extract_frequency_bands(signal, fs=256):
    """Extract EEG frequency bands"""
    bands = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 50)
    }

    nyquist = fs / 2
    filtered_signals = {'raw': signal}

    for band_name, (low, high) in bands.items():
        try:
            low_norm = max(low / nyquist, 0.01)
            high_norm = min(high / nyquist, 0.99)

            b, a = butter(4, [low_norm, high_norm], btype='band')
            filtered = filtfilt(b, a, signal)
            filtered_signals[band_name] = filtered
        except:
            filtered_signals[band_name] = np.zeros_like(signal)

    return filtered_signals

def get_channel_signal(trial_data, ch, start_idx, win_size) -> np.ndarray:
    """Extracts a windowed signal from a channel with padding if necessary"""
    ch_data = trial_data[trial_data['channel'] == ch].sort_values('sample')
    if start_idx + win_size <= len(ch_data):
        return ch_data['value'].iloc[start_idx:start_idx + win_size].values

    available_signal = ch_data['value'].iloc[start_idx:].values
    if len(available_signal) == 0:
        return np.zeros(win_size)

    return np.pad(available_signal, (0, win_size - len(available_signal)), mode='constant')


def process_channel(signal, use_bands, channel_idx, sample) -> int:
    """Process one channel: extract frequency bands or raw signal"""
    if use_bands:
        bands = extract_frequency_bands(signal, fs=256)
        for band_name in ['raw', 'delta', 'theta', 'alpha', 'beta', 'gamma']:
            if band_name in bands:
                band_signal = normalize_signal(bands[band_name])
                sample[channel_idx, :, 0] = band_signal
            channel_idx += 1
    else:
        signal = normalize_signal(signal)
        sample[channel_idx, :, 0] = signal
        channel_idx += 1
    return channel_idx


def build_tensor_from_parquet(
    parquet_path: str,
    channels: list[str] = None,
    win_size: int = 256,
    step_size: int = 256,
    use_bands: bool = True
) -> np.ndarray:
    """
    Build 4D tensor (N, C, T, 1) from a single parquet EEG file.
    """

    if channels is None:
        channels = PREDEFINED_CHANNELS

    df = pd.read_parquet(parquet_path)

    if df.empty:
        return np.array([])

    available_channels = set(df["channel"].unique())
    channels_to_use = list(set(channels) & available_channels)

    if not channels_to_use:
        return np.array([])

    actual_n_channels = len(channels_to_use) * 6 if use_bands else len(channels_to_use)

    X_data = []

    trials = df["trial"].unique()

    for trial_id in trials:

        trial_data = df[df["trial"] == trial_id]

        channel_lengths = {
            ch: len(trial_data[trial_data["channel"] == ch])
            for ch in channels_to_use
            if not trial_data[trial_data["channel"] == ch].empty
        }

        if not channel_lengths:
            continue

        min_length = min(channel_lengths.values())

        if min_length < win_size:
            continue

        n_windows = max(1, (min_length - win_size) // step_size + 1)

        for w in range(n_windows):

            start_idx = w * step_size
            sample = np.zeros((actual_n_channels, win_size, 1), dtype=np.float32)

            channel_idx = 0
            valid_channels_count = 0

            for ch in channels_to_use:

                ch_data = trial_data[trial_data["channel"] == ch]

                if ch_data.empty:
                    channel_idx += 6 if use_bands else 1
                    continue

                signal = get_channel_signal(trial_data, ch, start_idx, win_size)
                channel_idx = process_channel(signal, use_bands, channel_idx, sample)
                valid_channels_count += 1

            if valid_channels_count > 0:
                X_data.append(sample)

    del df
    gc.collect()

    if not X_data:
        return np.array([])

    return np.array(X_data, dtype=np.float32)
