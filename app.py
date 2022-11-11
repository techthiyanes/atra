import gradio as gr
import time
import glob
from aaas.audio_utils import (
    ffmpeg_read,
    model_vad,
    get_speech_timestamps,
    LANG_MAPPING,
    get_model_and_processor,
)
from aaas.text_utils import summarize, translate
from aaas.remote_utils import download_audio
import os
import torch

langs = list(LANG_MAPPING.keys())


def run_transcription(audio, main_lang, hotword_categories):
    global trans_pipes
    logs = ""
    start_time = time.time()
    chunks = []
    summarization = ""
    full_transcription = {"text": "", "en_text": ""}

    model, processor = get_model_and_processor(main_lang)

    logs += f"init vars time: {'{:.4f}'.format(time.time() - start_time)}\n"
    start_time = time.time()

    if audio is not None and len(audio) > 3:
        hotwords = []
        for h in hotword_categories:
            with open(f"{h}.txt", "r") as f:
                words = f.read().splitlines()
                for w in words:
                    if len(w) >= 3:
                        hotwords.append(w.strip())

        if len(hotwords) <= 1:
            hotwords = [" "]

        logs += f"init hotwords time: {'{:.4f}'.format(time.time() - start_time)}\n"
        start_time = time.time()

        if "https://" in audio:
            audio = download_audio(audio)
            model, processor = get_model_and_processor("universal")

        if isinstance(audio, str):
            with open(audio, "rb") as f:
                payload = f.read()
            os.remove(audio)

            logs += f"read audio time: {'{:.4f}'.format(time.time() - start_time)}\n"
            start_time = time.time()

            audio = ffmpeg_read(payload, sampling_rate=16000)
            logs += f"convert audio time: {'{:.4f}'.format(time.time() - start_time)}\n"
            start_time = time.time()

        speech_timestamps = get_speech_timestamps(
            audio,
            model_vad,
            sampling_rate=16000,
            min_silence_duration_ms=250,
            speech_pad_ms=200,
        )
        audio_batch = [
            audio[speech_timestamps[st]["start"] : speech_timestamps[st]["end"]]
            for st in range(len(speech_timestamps))
        ]

        do_stream = len(audio_batch) > 10

        if(do_stream == False):
            new_batch = []
            tmp_audio = []
            for b in audio_batch:
                if(len(tmp_audio) + len(b) < 30*16000):
                    tmp_audio.extend(b)
                elif(len(b) > 28*16000):
                    new_batch.append(tmp_audio)
                    tmp_audio = []
                    new_batch.append(b)
                else:
                    new_batch.append(tmp_audio)
                    tmp_audio = []

            if(tmp_audio != []):
                new_batch.append(tmp_audio)

            audio_batch = new_batch

        logs += (
            f"get speech timestamps time: {'{:.4f}'.format(time.time() - start_time)}\n"
        )
        start_time = time.time()

        for x in range(len(audio_batch)):
            data = audio_batch[x]

            input_values = processor.feature_extractor(
                data,
                sampling_rate=16000,
                return_tensors="pt",
                truncation=True,
            ).input_features

            logs += f"feature extractor: {'{:.4f}'.format(time.time() - start_time)}\n"
            start_time = time.time()

            with torch.inference_mode():
                if torch.cuda.is_available():
                    input_values = input_values.to("cuda").half()
                predicted_ids = model.generate(
                    input_values,
                    max_length=int(((len(data) / 16000) * 12) / 2) + 10,
                    use_cache=True,
                    no_repeat_ngram_size=1,
                    num_beams=2,
                    forced_decoder_ids=processor.get_decoder_prompt_ids(
                        language=LANG_MAPPING[main_lang], task="transcribe"
                    ),
                )

            logs += f"inference: {'{:.4f}'.format(time.time() - start_time)}\n"
            start_time = time.time()

            transcription = processor.batch_decode(
                predicted_ids, skip_special_tokens=True
            )[0]

            logs += f"decode: {'{:.4f}'.format(time.time() - start_time)}\n"
            start_time = time.time()

            chunks.append(
                {
                    "text": transcription,
                    "timestamp": (
                        speech_timestamps[x]["start"] / 16000,
                        speech_timestamps[x]["end"] / 16000,
                    ),
                }
            )

            full_transcription = {"text": "", "en_text": ""}

            for c in chunks:
                full_transcription["text"] += c["text"] + "\n"

            if do_stream == True:
                yield full_transcription["text"], chunks, hotwords, logs, summarization

        if do_stream == True:
            for c in range(len(chunks)):
                chunks[c]["en_text"] = translate(
                    chunks[c]["text"], LANG_MAPPING[main_lang], "en"
                )
                full_transcription["en_text"] += chunks[c]["en_text"] + "\n"
                yield full_transcription["text"], chunks, hotwords, logs, summarization
            logs += f"translate: {'{:.4f}'.format(time.time() - start_time)}\n"
            start_time = time.time()
            summarization = summarize(main_lang, full_transcription["en_text"][:12800])
        else:
            summarization = ""

        logs += f"summarization: {'{:.4f}'.format(time.time() - start_time)}\n"

        yield full_transcription["text"], chunks, hotwords, logs, summarization
    else:
        yield "", [], [], "", ""


"""
read the hotword categories from the index.txt file
"""


def get_categories():
    hotword_categories = []

    path = f"**/*.txt"
    for file in glob.glob(path, recursive=True):
        if "/" in file and "-" not in file:
            hotword_categories.append(file.split(".")[0])

    return hotword_categories


ui = gr.Blocks()

with ui:
    with gr.Tabs():
        with gr.TabItem("target language"):
            lang = gr.Radio(langs, value=langs[0])
        with gr.TabItem("hotword categories"):
            categories = gr.CheckboxGroup(choices=get_categories())

    with gr.Tabs():
        with gr.TabItem("Microphone"):
            mic = gr.Audio(source="microphone", type="filepath")
        with gr.TabItem("File"):
            audio_file = gr.Audio(source="upload", type="filepath")
        with gr.TabItem("URL"):
            video_url = gr.Textbox()

    with gr.Tabs():
        with gr.TabItem("Transcription"):
            transcription = gr.Textbox()
        with gr.TabItem("Subtitle"):
            chunks = gr.JSON()
        with gr.TabItem("Hotwords"):
            hotwordlist = gr.JSON()
        with gr.TabItem("Logs"):
            logs = gr.Textbox(lines=10)
        with gr.TabItem("Summarization"):
            sumarization = gr.Textbox()

    mic.change(
        fn=run_transcription,
        inputs=[mic, lang, categories],
        outputs=[transcription, chunks, hotwordlist, logs, sumarization],
        api_name="transcription",
    )
    audio_file.change(
        fn=run_transcription,
        inputs=[audio_file, lang, categories],
        outputs=[transcription, chunks, hotwordlist, logs, sumarization],
    )
    video_url.change(
        fn=run_transcription,
        inputs=[video_url, lang, categories],
        outputs=[transcription, chunks, hotwordlist, logs, sumarization],
    )


if __name__ == "__main__":
    ui.queue(concurrency_count=3)
    ui.launch(server_name="0.0.0.0")
