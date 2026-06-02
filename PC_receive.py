import socket
import wave
import time
import os
import json
from datetime import datetime

# =====================================================
# 配置
# =====================================================

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2

TIMEOUT_SECONDS = 30

# =====================================================
# 创建数据集目录
# =====================================================

ROOT_DIR = "SleepAudioDataset"
os.makedirs(ROOT_DIR, exist_ok=True)

start_dt = datetime.now()

record_id = start_dt.strftime("%Y%m%d_%H%M%S")

record_dir = os.path.join(ROOT_DIR, record_id)
os.makedirs(record_dir)

wav_path = os.path.join(record_dir, "audio.wav")
metadata_path = os.path.join(record_dir, "metadata.json")
log_path = os.path.join(record_dir, "recording.log")

# =====================================================
# Metadata
# =====================================================

metadata = {
    "record_id": record_id,
    "start_time": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
    "sample_rate": SAMPLE_RATE,
    "channels": CHANNELS,
    "bit_depth": 16,
    "mic": "INMP441",
    "device": "ESP32"
}

with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4, ensure_ascii=False)

# =====================================================
# Log
# =====================================================

def write_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{timestamp}] {msg}"

    print(line)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# =====================================================
# UDP Socket
# =====================================================

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.bind((UDP_IP, UDP_PORT))

# 关键：超时检测
sock.settimeout(1)

# =====================================================
# WAV
# =====================================================

wf = wave.open(wav_path, "wb")

wf.setnchannels(CHANNELS)
wf.setsampwidth(SAMPLE_WIDTH)
wf.setframerate(SAMPLE_RATE)

# =====================================================
# 状态变量
# =====================================================

total_bytes = 0
packet_count = 0

record_start_time = time.time()

last_data_time = time.time()

last_report_time = time.time()

# =====================================================
# 启动信息
# =====================================================

print("=" * 60)
print("Sleep Audio Recorder V2.0")
print("=" * 60)

print("Recording Folder:")
print(record_dir)

print()

write_log("Recording Started")

# =====================================================
# 主循环
# =====================================================

try:

    while True:

        try:

            data, addr = sock.recvfrom(4096)

            wf.writeframes(data)

            total_bytes += len(data)

            packet_count += 1

            last_data_time = time.time()

        except socket.timeout:
            pass

        now = time.time()

        # ==============================
        # 每10秒打印一次状态
        # ==============================

        if now - last_report_time >= 10:

            duration_hr = (
                now - record_start_time
            ) / 3600

            size_mb = (
                total_bytes
                / 1024
                / 1024
            )

            write_log(
                f"Recording | "
                f"{duration_hr:.2f} h | "
                f"{size_mb:.2f} MB | "
                f"{packet_count} packets"
            )

            last_report_time = now

        # ==============================
        # 断流检测
        # ==============================

        if now - last_data_time > TIMEOUT_SECONDS:

            write_log(
                f"WARNING: No audio data for "
                f"{TIMEOUT_SECONDS} seconds!"
            )

            last_data_time = now

except KeyboardInterrupt:

    write_log("Keyboard Interrupt")

finally:

    wf.close()

    sock.close()

    end_dt = datetime.now()

    duration_sec = (
        end_dt - start_dt
    ).total_seconds()

    size_mb = (
        total_bytes
        / 1024
        / 1024
    )

    metadata["end_time"] = end_dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    metadata["duration_hours"] = round(
        duration_sec / 3600,
        2
    )

    metadata["file_size_mb"] = round(
        size_mb,
        2
    )

    metadata["packet_count"] = packet_count

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=4,
            ensure_ascii=False
        )

    write_log("Recording Finished")

    print()
    print("=" * 60)
    print("Recording Saved")
    print("=" * 60)

    print("WAV:")
    print(wav_path)

    print()

    print("Metadata:")
    print(metadata_path)

    print()

    print(f"Duration : {duration_sec/3600:.2f} h")
    print(f"Size     : {size_mb:.2f} MB")
    print(f"Packets  : {packet_count}")