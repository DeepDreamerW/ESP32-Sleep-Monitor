#include <WiFi.h>
#include <WiFiUdp.h>
#include "driver/i2s.h"

// =====================================================
// WiFi
// =====================================================

const char* ssid = "your WiFi";
const char* password = "WiFi password";

// =====================================================
// PC IP
// =====================================================

const char* pc_ip = "192.168.1.100";   // your computer's IP

const int pc_port = 5005;

WiFiUDP udp;

// =====================================================
// I2S 引脚
// =====================================================

#define I2S_WS   15
#define I2S_SCK  14
#define I2S_SD   32

// =====================================================
// 音频参数
// =====================================================

#define SAMPLE_RATE 16000

#define BUFFER_SIZE 1024

// 32bit Buffer
int32_t i2s_buffer[BUFFER_SIZE];

// 转换后的16bit PCM
int16_t pcm_buffer[BUFFER_SIZE];

// =====================================================
// I2S 初始化
// =====================================================

void setupI2S()
{
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(
            I2S_MODE_MASTER |
            I2S_MODE_RX
        ),

        .sample_rate = SAMPLE_RATE,

        .bits_per_sample =
            I2S_BITS_PER_SAMPLE_32BIT,

        .channel_format =
            I2S_CHANNEL_FMT_ONLY_LEFT,

        .communication_format =
            I2S_COMM_FORMAT_I2S,

        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,

        .dma_buf_count = 8,

        .dma_buf_len = 256,

        .use_apll = true,

        .tx_desc_auto_clear = false,

        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {

        .bck_io_num = I2S_SCK,

        .ws_io_num = I2S_WS,

        .data_out_num = -1,

        .data_in_num = I2S_SD
    };

    // 安装 I2S 驱动
    i2s_driver_install(
        I2S_NUM_0,
        &i2s_config,
        0,
        NULL
    );

    // 设置引脚
    i2s_set_pin(
        I2S_NUM_0,
        &pin_config
    );

    // 清空DMA
    i2s_zero_dma_buffer(I2S_NUM_0);
}

// =====================================================
// Setup
// =====================================================

void setup()
{
    Serial.begin(115200);

    Serial.println();
    Serial.println("Connecting WiFi...");

    // WiFi STA模式
    WiFi.mode(WIFI_STA);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("WiFi Connected");

    Serial.print("ESP32 IP: ");

    Serial.println(WiFi.localIP());

    // UDP启动
    udp.begin(pc_port);

    // 初始化I2S
    setupI2S();

    Serial.println("Audio Streaming Start");
}

// =====================================================
// 主循环
// =====================================================

void loop()
{
    size_t bytes_read = 0;

    // 读取I2S数据
    i2s_read(
        I2S_NUM_0,

        (void*)i2s_buffer,

        sizeof(i2s_buffer),

        &bytes_read,

        portMAX_DELAY
    );

    // 实际采样数
    int samples = bytes_read / 4;

    // 32bit -> 16bit
    for (int i = 0; i < samples; i++)
    {
        // INMP441 左对齐24bit
        pcm_buffer[i] = (int16_t)(i2s_buffer[i] >> 14);
    }

    // UDP发送
    udp.beginPacket(pc_ip, pc_port);

    udp.write(
        (uint8_t*)pcm_buffer,
        samples * 2
    );

    udp.endPacket();
}