import base64
import requests
import json
from config.siliconflow_settings import SILICONFLOW_API_KEY, SILICONFLOW_BASE_URL, SILICONFLOW_MODEL, REQUEST_TIMEOUT


class SiliconFlowOCRClient:
    """SiliconFlow DeepSeek-OCR 客户端"""

    def __init__(self):
        self.api_key = SILICONFLOW_API_KEY
        self.base_url = SILICONFLOW_BASE_URL
        self.model = SILICONFLOW_MODEL
        self.timeout = REQUEST_TIMEOUT

        # 验证API密钥
        if not self.api_key or self.api_key.startswith("sk-"):
            if len(self.api_key) < 10:
                raise ValueError("Invalid SiliconFlow API key")

    def recognize_local_image(self, image_path: str, prompt: str = "请仅输出图像中的文本内容。") -> str:
        """
        识别本地图片

        Args:
            image_path: 本地图片路径
            prompt: 识别提示词

        Returns:
            识别出的文本内容
        """
        with open(image_path, "rb") as f:
            image_data = f.read()

        base64_image = base64.b64encode(image_data).decode()

        # 根据文件扩展名确定MIME类型
        ext = image_path.lower().split(".")[-1]
        mime_types = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        mime_type = mime_types.get(ext, "image/jpeg")

        # 构建请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 4096
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            # 提取响应内容
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {})
                return message.get("content", "")
            else:
                raise ValueError(f"Unexpected response format: {result}")

        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request timeout after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse API response: {str(e)}")

    def recognize_image_url(self, image_url: str, prompt: str = "请仅输出图像中的文本内容。") -> str:
        """
        识别远程URL的图片

        Args:
            image_url: 图片URL
            prompt: 识别提示词

        Returns:
            识别出的文本内容
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 4096
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {})
                return message.get("content", "")
            else:
                raise ValueError(f"Unexpected response format: {result}")

        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request timeout after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse API response: {str(e)}")
