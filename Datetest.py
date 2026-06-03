import wave
import numpy as np
import matplotlib.pyplot as plt

# =============================================
# 修改为你上传的 WAV 文件路径
# =============================================
file_path = "SleepAudioDataset/20260602_223825/audio.wav"  # 替换成你的文件名

# =============================================
# 读取 WAV
# =============================================
wf = wave.open(file_path, "rb")
n_channels = wf.getnchannels()
sample_rate = wf.getframerate()
n_frames = wf.getnframes()

print(f"Channels: {n_channels}, Sample Rate: {sample_rate}, Total Frames: {n_frames}")

data = wf.readframes(n_frames)
pcm = np.frombuffer(data, dtype=np.int16)
wf.close()

if n_channels > 1:
    pcm = pcm[::n_channels]

# =============================================
# 设置滚动窗口
# =============================================
window_seconds = 30  # 每次显示30秒
window_size = window_seconds * sample_rate
step_seconds = 15    # 每次滑动15秒
step_size = step_seconds * sample_rate

# =============================================
# 分块可视化
# =============================================
for start in range(0, len(pcm), step_size):
    end = start + window_size
    chunk = pcm[start:end]
    if len(chunk) == 0:
        break

    rms = np.sqrt(np.mean(chunk.astype(np.float32) ** 2))

    time_axis = np.arange(len(chunk)) / sample_rate

    plt.figure(figsize=(12,4))
    plt.plot(time_axis, chunk, color='blue', label='Waveform')
    plt.title(f"Time {start/sample_rate:.1f} - {min(end,len(pcm))/sample_rate:.1f}s | RMS={rms:.2f}")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")

    max_val = np.max(np.abs(chunk))
    if max_val < 1000:
        plt.ylim([-1000, 1000])
    else:
        plt.ylim([-max_val, max_val])

    plt.legend()
    plt.show()