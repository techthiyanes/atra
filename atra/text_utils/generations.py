import re
import torch
from threading import Thread

from transformers import AutoTokenizer, AutoModelForCausalLM, StoppingCriteriaList, TextIteratorStreamer, StoppingCriteria, PreTrainedTokenizer
from atra.model_utils.model_utils import free_gpu
from atra.statics import END_OF_TEXT_TOKEN, MODEL_MAPPING, ASSISTANT_PREFIX, HUMAN_PREFIX

model = None
tokenizer = None

def do_generation(input, constraints: list[list[str]] = None, max_len = 512):
    global model, tokenizer
    if model is None:
        free_gpu(except_model="chat")
        tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=MODEL_MAPPING["chat"]["universal"][
                "name"
            ],
        )
        FREE_GPU_MEM = int(torch.cuda.mem_get_info()[0] / 1024**3)-3  # in GB
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_MAPPING["chat"]["universal"]["name"],
            device_map="auto",
            low_cpu_mem_usage=True,
            torch_dtype=torch.float16,
            trust_remote_code=True,
            max_memory = {0: f"{FREE_GPU_MEM}GiB", "cpu": "64GiB"},
        )
        model.eval()
        model = torch.compile(model, mode="max-autotune", backend="onnxrt")

    if constraints is not None:
        constraints = [tokenizer(x).input_ids for x in constraints]

    # Tokenize the messages string
    input_ids = tokenizer(
        input + END_OF_TEXT_TOKEN, return_tensors="pt", max_length=1024, truncation=True
    )
    input_ids.pop("token_type_ids", None)
    input_ids = input_ids.to(model.device)
    streamer = TextIteratorStreamer(
        tokenizer=tokenizer,
        timeout=60.0,
        skip_prompt=True,
        skip_special_tokens=True,
    )
    class StopOnTokens(StoppingCriteria):
        def __init__(self, stopwords, tokenizer: PreTrainedTokenizer ) -> None:
            super().__init__()
            self.stopword_ids = [tokenizer.encode(text=word, add_special_tokens=False, padding=False)[0] for word in stopwords]

        def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
            for stop_id in self.stopword_ids:
                if input_ids[0][-1] == stop_id:
                    return True
            return False

    generate_kwargs = dict(
        **input_ids,
        max_new_tokens=max_len,
        min_new_tokens = int(max_len/4),
        do_sample=False,
        num_beams=1,
        temperature=0.01,
        no_repeat_ngram_size=3,
        use_cache = True,
        stopping_criteria=StoppingCriteriaList([StopOnTokens(stopwords=[END_OF_TEXT_TOKEN, HUMAN_PREFIX, ASSISTANT_PREFIX], tokenizer=tokenizer)]),
    )
    if constraints is not None:
        generate_kwargs["force_words_ids"] = constraints
        generate_kwargs["num_beams"] = 3
        return tokenizer.batch_decode(model.generate(**generate_kwargs))[0]
    else:
        generate_kwargs["streamer"] = streamer

        def generate_and_signal_complete():
            model.generate(**generate_kwargs) # pad_token_id=tokenizer.eos_token_id

        t1 = Thread(target=generate_and_signal_complete)
        t1.start()

        # Initialize an empty string to store the generated text
        partial_text = ""
        for new_text in streamer:
            partial_text += new_text
            partial_text = re.sub(r"<.*?\|.*?\|.*?>", "", partial_text)
            yield partial_text