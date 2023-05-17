import torch
from atra.model_utils.model_utils import get_model_and_processor
from atra.statics import LANG_MAPPING
from atra.utils import timeit


@timeit
def translate(text, src, dest) -> str:
    if src == dest:
        return text
    src = LANG_MAPPING[src]
    dest = LANG_MAPPING[dest]
    model, tokenizer = get_model_and_processor("universal", "translation")
    tokenizer.src_lang = src # type: ignore
    input_features = tokenizer(text, return_tensors="pt").input_ids
    if torch.cuda.is_available():
        input_features = input_features.cuda()
    generated_tokens = model.generate(
        inputs=input_features, forced_bos_token_id=tokenizer.get_lang_id(dest) # type: ignore
    )
    result = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return result[0]
