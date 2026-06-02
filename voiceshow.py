import socket
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# UDP配置
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
BUFFER_SIZE = 4096
DISPLAY_SIZE = 16000  # 显示1秒波形

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print("Listening for audio...")

wave_buffer = np.zeros(DISPLAY_SIZE, dtype=np.int16)

fig, ax = plt.subplots()
line, = ax.plot(wave_buffer)
ax.set_ylim(-32768, 32767)
ax.set_xlabel("Sample")
ax.set_ylabel("Amplitude")
ax.set_title("Real-time Audio Waveform")

def update(frame):
    global wave_buffer
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        pcm_data = np.frombuffer(data, dtype=np.int16)
        if len(pcm_data) >= DISPLAY_SIZE:
            wave_buffer = pcm_data[-DISPLAY_SIZE:]
        else:
            wave_buffer = np.roll(wave_buffer, -len(pcm_data))
            wave_buffer[-len(pcm_data):] = pcm_data
        line.set_ydata(wave_buffer)
    except BlockingIOError:
        pass  # 没有数据就跳过
    return line,

# 设置socket非阻塞
sock.setblocking(False)

ani = FuncAnimation(fig, update, interval=50)
plt.show()
sock.close()