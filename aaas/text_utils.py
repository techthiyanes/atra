from aaas.utils import timeit
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer, pipeline
from unidecode import unidecode

translation_model = None
translation_tokenizer = None
qa_pipeline = None


@timeit
def translate(text, source, target):
    global translation_model, translation_tokenizer

    if source in ["german", "english"]:
        text = unidecode(text)

    if source == target:
        return text

    if translation_model is None:
        translation_model = M2M100ForConditionalGeneration.from_pretrained(
            "facebook/m2m100_418M"
        )
        translation_tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

    translation_tokenizer.src_lang = source
    encoded_hi = translation_tokenizer(text, return_tensors="pt")
    generated_tokens = translation_model.generate(
        **encoded_hi, forced_bos_token_id=translation_tokenizer.get_lang_id(target)
    )
    translated = translation_tokenizer.batch_decode(
        generated_tokens, skip_special_tokens=True
    )[0]

    return translated


@timeit
def question_answering(question, context):
    global qa_pipeline
    if qa_pipeline is None:
        qa_pipeline = pipeline(
            "question-answering", model="timpal0l/mdeberta-v3-base-squad2"
        )

    return qa_pipeline(question=question, context=context)["answer"]
