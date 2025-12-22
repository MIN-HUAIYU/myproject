# SiliconFlow OCR API 配置文件
# 位置: config/siliconflow_settings.py

# ========== API 配置 ==========
SILICONFLOW_API_KEY = "sk-qepmhiojucrpxwbyoshbefarhcaulhtculebjlrzuvgrtxvx"
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1/chat/completions"
SILICONFLOW_MODEL = "deepseek-ai/DeepSeek-OCR"

# ========== 请求超时设置 ==========
REQUEST_TIMEOUT = 60  # 秒

# ========== 代理设置（可选） ==========
# 如果需要使用代理，取消注释下面的配置
# PROXY = {
#     "http": "http://proxy.example.com:8080",
#     "https": "http://proxy.example.com:8080"
# }
