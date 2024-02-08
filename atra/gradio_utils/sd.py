from atra.gradio_utils.ui import GLOBAL_CSS, GET_GLOBAL_HEADER, launch_args
import gradio as gr
from atra.image_utils.diffusion import generate_images


def build_diffusion_ui() -> None:
    ui = gr.Blocks(css=GLOBAL_CSS)
    with ui:
        with gr.Row():
            GET_GLOBAL_HEADER()
        with gr.Column():
            images = gr.Gallery(label="Image")
            stats = gr.Markdown()

        with gr.Column():
            prompt = gr.Textbox(
                label="Prompt", info="Prompt of what you want to see", interactive=True
            )
            negatives = gr.Textbox(
                label="Negative Prompt",
                info="Prompt describing what you dont want to see, useful for refining image",
            )
            height = gr.Slider(
                minimum=512,
                maximum=1024,
                step=32,
                value=1024,
                label="Height",
            )
            width = gr.Slider(
                minimum=512,
                maximum=1024,
                step=32,
                value=1024,
                label="Width",
            )

        prompt.submit(
            generate_images,
            inputs=[prompt, negatives, height, width],
            outputs=[images, stats, prompt],
        )
        negatives.submit(
            generate_images,
            inputs=[prompt, negatives, height, width],
            outputs=[images, stats, prompt],
        )

        gr.Examples(
            [
                ["cyborg style, golden retriever"],
                [
                    "High nation-geographic symmetrical close-up portrait shoot in green jungle of an expressive lizard, anamorphic lens, ultra-realistic, hyper-detailed, green-core, jungle-core",
                ],
                ["Glowing jellyfish floating through a foggy forest at twilight", ""],
                [
                    "Elegant lavender garnish cocktail idea, cocktail glass, realistic, sharp focus, 8k high definition",
                ],
                [
                    "General Artificial Intelligence in data center, futuristic concept art, 3d rendering",
                ],
            ],
            inputs=[prompt],
        )

        gr.Textbox(value="the actual model used is: dataautogpt3/ProteusV0.2")

    ui.queue(api_open=False)

    ui.launch(**launch_args)
