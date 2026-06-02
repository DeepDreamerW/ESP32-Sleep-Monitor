import socket
import wave
import time
import os

# =====================================================
# UDP配置
# =====================================================

UDP_IP = "0.0.0.0"

UDP_PORT = 5005

# =====================================================
# 创建UDP Socket
# =====================================================

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.bind((UDP_IP, UDP_PORT))

print("Sleep Audio Recording Start")

# =====================================================
# 创建 recordings 文件夹
# =====================================================

if not os.path.exists("recordings"):

    os.makedirs("recordings")

# =====================================================
# 文件名
# =====================================================

filename = time.strftime(
    "recordings/sleep_%Y%m%d_%H%M%S.wav"
)

# =====================================================
# WAV文件
# =====================================================

wf = wave.open(filename, "wb")

wf.setnchannels(1)

wf.setsampwidth(2)

wf.setframerate(16000)

print("Saving:", filename)

# =====================================================
# 数据统计
# =====================================================

total_bytes = 0

start_time = time.time()

# =====================================================
# 主循环
# =====================================================

try:

    while True:

        data, addr = sock.recvfrom(4096)

        wf.writeframes(data)

        total_bytes += len(data)

        # 每10秒打印一次状态
        elapsed = time.time() - start_time

        if elapsed >= 10:

            mb = total_bytes / 1024 / 1024

            print(f"Recording... {mb:.2f} MB")

            start_time = time.time()

except KeyboardInterrupt:

    print("\nStop Recording")

finally:

    wf.close()

    sock.close()

    print("Saved:", filename)