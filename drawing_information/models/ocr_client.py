import base64
from openai import OpenAI
from config.settings import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, OCR_MODEL


class AliyunOCRClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
        )
        self.model = OCR_MODEL

    def recognize_image(self, image_url: str, prompt: str = "请仅输出图像中的文本内容。") -> str:
        """
        识别图像中的文本

        Args:
            image_url: 图片URL或本地路径
            prompt: 识别提示词

        Returns:
            识别出的文本内容
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        return completion.choices[0].message.content

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

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        return completion.choices[0].message.content
