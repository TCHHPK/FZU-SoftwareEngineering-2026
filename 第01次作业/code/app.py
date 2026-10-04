import os

import gradio as gr
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


def generate_image(prompt):
    if not prompt.strip():
        raise gr.Error("请输入图像提示词")

    try:
        image = client.text_to_image(
            prompt=prompt,
            model=MODEL_ID,
        )
        return image

    except Exception as e:
        raise gr.Error(f"图像生成失败：{e}")


with gr.Blocks(title="FLUX Realism Image Generator") as demo:
    gr.Markdown(
        """
        # FLUX Realism Image Generator

        使用 Hugging Face API 调用 **XLabs-AI/flux-RealismLora**
        生成写实风格图像。
        """
    )

    prompt_input = gr.Textbox(
        label="Prompt",
        placeholder="请输入图像描述……",
        lines=5,
    )

    generate_button = gr.Button("生成图片")

    output_image = gr.Image(
        label="生成结果",
        type="pil",
    )

    generate_button.click(
        fn=generate_image,
        inputs=prompt_input,
        outputs=output_image,
    )


if __name__ == "__main__":
    demo.launch()