"""Remove the 700 Hz beep from a chirp-plus-beep tone with an STFT mask."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.io.wavfile import write
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import gaussian

OUT_DIR = Path(__file__).resolve().parent


def make_signal(fs: int = 2000) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Two-second chirp (100–500 Hz) plus a 700 Hz beep at 1.2 s."""
    t = np.arange(0, 2, 1 / fs)
    chirp = np.cos(2 * np.pi * (100 * t + 100 * t**2))
    beep = np.exp(-0.5 * ((t - 1.2) / 0.04) ** 2) * np.cos(2 * np.pi * 700 * t)
    return t, chirp, chirp + beep


def save_audio(path: Path, signal: np.ndarray, fs: int) -> None:
    peak = max(1.0, float(np.max(np.abs(signal))))
    write(path, fs, np.int16(signal / peak * 32767))


def plot_spectrogram(path: Path, times, freqs, z, title: str) -> None:
    plt.figure(figsize=(9, 4))
    plt.pcolormesh(
        times,
        freqs,
        20 * np.log10(np.maximum(np.abs(z), 1e-8)),
        shading="auto",
        cmap="viridis",
        vmin=-65,
    )
    plt.xlim(0, 2)
    plt.ylim(0, 900)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Frequency (Hz)")
    plt.title(title)
    plt.colorbar(label="Magnitude (dB)")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()


def main() -> None:
    fs = 2000
    t, chirp, x = make_signal(fs)

    sigma = 0.08
    nperseg = 801
    window = gaussian(nperseg, std=sigma * fs)
    sft = ShortTimeFFT(window, hop=20, fs=fs, mfft=2048, scale_to="magnitude")

    z = sft.stft(x)
    times = sft.t(len(x))
    freqs = sft.f

    # Zero the time-frequency patch that contains the beep.
    mask = np.ones_like(z)
    time_region = np.flatnonzero((times >= 1.05) & (times <= 1.35))
    freq_region = np.flatnonzero((freqs >= 620) & (freqs <= 780))
    mask[np.ix_(freq_region, time_region)] = 0
    z_filtered = z * mask

    reconstructed = sft.istft(z_filtered, k1=len(x))
    error = np.linalg.norm(reconstructed - chirp) / np.linalg.norm(chirp)
    print(f"Relative reconstruction error: {error:.6f}")

    plot_spectrogram(
        OUT_DIR / "original_spectrogram.png",
        times,
        freqs,
        z,
        "Original Chirp and Beep",
    )
    plot_spectrogram(
        OUT_DIR / "filtered_spectrogram.png",
        times,
        freqs,
        z_filtered,
        "After STFT Beep Removal",
    )

    zoom = (t >= 1.15) & (t <= 1.25)
    plt.figure(figsize=(10, 4))
    plt.plot(t[zoom], chirp[zoom], label="Original clean chirp", linewidth=2)
    plt.plot(
        t[zoom],
        reconstructed[zoom],
        label="Filtered reconstruction",
        linewidth=1.5,
        alpha=0.8,
    )
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.title("Clean Chirp vs Reconstructed Signal")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "reconstruction_comparison.png", dpi=300)
    plt.close()

    save_audio(OUT_DIR / "original.wav", x, fs)
    save_audio(OUT_DIR / "filtered.wav", reconstructed, fs)
    save_audio(OUT_DIR / "clean_chirp.wav", chirp, fs)

    for path in sorted(OUT_DIR.iterdir()):
        if path.suffix in {".png", ".wav"}:
            print(f"Saved {path}")


if __name__ == "__main__":
    main()
