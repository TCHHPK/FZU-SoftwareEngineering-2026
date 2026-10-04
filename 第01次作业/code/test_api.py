import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

token = os.getenv("HF_TOKEN")

if not token:
    raise ValueError("没有读取到 HF_TOKEN，请检查 .env 文件")

MODEL_ID = "XLabs-AI/flux-RealismLora"

client = InferenceClient(
    provider="auto",
    api_key=token,
)

prompt = (
    "A highly realistic street photograph of a modern Asian city after rain, "
    "pedestrians walking naturally, wet pavement reflecting city lights, "
    "natural skin texture, realistic lighting, 35mm photography, "
    "documentary photography, photorealistic"
)

print("正在调用模型：", MODEL_ID)
print("正在生成图片，请稍候……")

try:
    image = client.text_to_image(
        prompt=prompt,
        model=MODEL_ID,
    )

    output_path = "../outputs/test_realism.png"
    image.save(output_path)

    print("生成成功！")
    print("图片保存至：", output_path)

except Exception as e:
    print("API 调用失败：")
    print(type(e).__name__)
    print(e)