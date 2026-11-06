"""Original royalty-free background music generator (no network needed)."""
import numpy as np, wave

PROGRESSIONS = [
    [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],  # Am F C G
    [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]],  # C G Am F
    [[50, 53, 57], [46, 50, 53], [48, 52, 55], [45, 49, 52]],  # Dm Bb C A
    [[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]],  # Em C G D
    [[53, 57, 60], [55, 59, 62], [52, 55, 59], [57, 60, 64]],  # F G Em Am
]

def note(m): return 440 * 2 ** ((m - 69) / 12)

def make_music(path, dur, seed=0, sr=44100):
    rng = np.random.default_rng(seed)
    chords = PROGRESSIONS[seed % len(PROGRESSIONS)]
    bpm = [88, 92, 96, 90, 94][seed % 5]
    n = int(sr * dur); t = np.arange(n) / sr
    beat = 60 / bpm; bar = beat * 4
    out = np.zeros(n)
    for i in range(int(dur / bar) + 1):
        s = int(i * bar * sr); e = min(n, int((i + 1) * bar * sr))
        if s >= n: break
        tt = np.arange(e - s) / sr
        env = np.minimum(1, tt / 0.4) * np.minimum(1, (bar - tt) / 0.4)
        for m in chords[i % 4]:
            f = note(m)
            out[s:e] += 0.07 * env * (np.sin(2*np.pi*f*tt) + 0.3*np.sin(2*np.pi*2*f*tt) + 0.15*np.sin(2*np.pi*f*1.003*tt))
        out[s:e] += 0.12 * env * np.sin(2*np.pi*note(chords[i % 4][0] - 12)*tt)
    step = beat / 2
    pattern = [[0, 1, 2, 1], [0, 2, 1, 2], [2, 1, 0, 1], [0, 1, 2, 0], [1, 2, 0, 2]][seed % 5]
    for k in range(int(dur / step)):
        s = int(k * step * sr); e = min(n, s + int(0.35 * sr))
        ch = chords[int(k * step / bar) % 4]; m = ch[pattern[k % 4]] + 12
        tt = np.arange(e - s) / sr
        out[s:e] += 0.05 * np.exp(-tt * 9) * np.sin(2*np.pi*note(m)*tt)
    for k in range(int(dur / beat)):
        s = int(k * beat * sr)
        if s >= n: break
        if k % 2 == 0:
            e = min(n, s + int(0.25 * sr)); tt = np.arange(e - s) / sr
            out[s:e] += 0.35 * np.exp(-tt*18) * np.sin(2*np.pi*(55 + 90*np.exp(-tt*30))*tt)
        else:
            e = min(n, s + int(0.12 * sr)); tt = np.arange(e - s) / sr
            out[s:e] += 0.08 * np.exp(-tt*35) * rng.standard_normal(e - s)
        hs = s + int(beat * sr / 2); he = min(n, hs + int(0.04 * sr))
        if hs < n: out[hs:he] += 0.03 * np.exp(-np.arange(he - hs)/sr*80) * rng.standard_normal(he - hs)
    out *= np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 2.0)
    out /= np.max(np.abs(out)) * 1.25
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(np.stack([pcm, pcm], 1).tobytes())
