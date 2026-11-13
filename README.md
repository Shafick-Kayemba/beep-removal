# Beep removal with a short-time Fourier transform

This repo builds a two-second sound: a chirp whose frequency rises from 100 Hz to 500 Hz, plus a short 700 Hz beep at 1.2 seconds. It then removes the beep by zeroing that region of a Gaussian-window short-time Fourier transform and reconstructing the waveform with the inverse transform.

The repository contains only the script and its dependencies. Running it recreates the audio and the plots.

## Requirements

- Python 3.9 or newer
- The packages in `requirements.txt` (`numpy`, `scipy` 1.12 or newer, `matplotlib`)

## Recreate the audio and plots

From this directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python beep_removal.py
```

On Windows, activate the environment with `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

The script writes these files next to itself:

| File | Contents |
| --- | --- |
| `original.wav` | Chirp plus beep |
| `filtered.wav` | Reconstructed signal after the beep is removed |
| `clean_chirp.wav` | Chirp alone, for comparison |
| `original_spectrogram.png` | Spectrogram before masking |
| `filtered_spectrogram.png` | Spectrogram after the beep region is zeroed |
| `reconstruction_comparison.png` | Clean chirp and reconstruction, zoomed around the beep |

The WAVs use a sample rate of 2000 Hz. Play them in a program that honors that rate.

The script also prints a relative reconstruction error, comparing the filtered signal with the clean chirp. A fresh run should print about `0.003689`.
