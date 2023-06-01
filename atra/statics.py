from transformers import (
    WhisperForConditionalGeneration,
    M2M100ForConditionalGeneration,
    M2M100Tokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM,
    AutoModel,
    AutoTokenizer,
    AutoProcessor,
)

MODEL_MAPPING = {
    "speech_lang_detection": {
        "universal": {
            "name": "openai/whisper-small",
            "class": WhisperForConditionalGeneration,
            "processor": AutoProcessor,
        },
    },
    "asr": {
        "german": {
            "name": "flozi00/whisper-large-v2-german-cv13",
            "class": WhisperForConditionalGeneration,
            "processor": AutoProcessor,
        },
        "universal": {
            "name": "openai/whisper-large-v2",
            "class": WhisperForConditionalGeneration,
            "processor": AutoProcessor,
        },
    },
    "translation": {
        "universal": {
            "name": "facebook/m2m100_1.2B",
            "class": M2M100ForConditionalGeneration,
            "processor": M2M100Tokenizer,
        }
    },
    "summarization": {
        "english": {
            "name": "google/flan-t5-xl",
            "class": AutoModelForSeq2SeqLM,
            "processor": AutoTokenizer,
        },
        "german": {
            "name": "google/flan-t5-xl",
            "class": AutoModelForSeq2SeqLM,
            "processor": AutoTokenizer,
        },
    },
    "question-answering": {
        "english": {
            "name": "google/flan-t5-xl",
            "class": AutoModelForSeq2SeqLM,
            "processor": AutoTokenizer,
        },
        "german": {
            "name": "google/flan-t5-xl",
            "class": AutoModelForSeq2SeqLM,
            "processor": AutoTokenizer,
        },
    },
    "chat": {
        "universal": {
            "name": "OpenAssistant/pythia-12b-sft-v8-7k-steps",
            "class": AutoModelForCausalLM,
            "processor": AutoTokenizer,
        },
    },
    "embedding": {
        "universal": {
            "name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "class": AutoModel,
            "processor": AutoTokenizer,
        },
    },
}

LANGUAGE_CODES = {
    "en": "english",
    "zh": "chinese",
    "de": "german",
    "es": "spanish",
    "ru": "russian",
    "ko": "korean",
    "fr": "french",
    "ja": "japanese",
    "pt": "portuguese",
    "tr": "turkish",
    "pl": "polish",
    "ca": "catalan",
    "nl": "dutch",
    "ar": "arabic",
    "sv": "swedish",
    "it": "italian",
    "id": "indonesian",
    "hi": "hindi",
    "fi": "finnish",
    "vi": "vietnamese",
    "iw": "hebrew",
    "uk": "ukrainian",
    "el": "greek",
    "ms": "malay",
    "cs": "czech",
    "ro": "romanian",
    "da": "danish",
    "hu": "hungarian",
    "ta": "tamil",
    "no": "norwegian",
    "th": "thai",
    "ur": "urdu",
    "hr": "croatian",
    "bg": "bulgarian",
    "lt": "lithuanian",
    "la": "latin",
    "mi": "maori",
    "ml": "malayalam",
    "cy": "welsh",
    "sk": "slovak",
    "te": "telugu",
    "fa": "persian",
    "lv": "latvian",
    "bn": "bengali",
    "sr": "serbian",
    "az": "azerbaijani",
    "sl": "slovenian",
    "kn": "kannada",
    "et": "estonian",
    "mk": "macedonian",
    "br": "breton",
    "eu": "basque",
    "is": "icelandic",
    "hy": "armenian",
    "ne": "nepali",
    "mn": "mongolian",
    "bs": "bosnian",
    "kk": "kazakh",
    "sq": "albanian",
    "sw": "swahili",
    "gl": "galician",
    "mr": "marathi",
    "pa": "punjabi",
    "si": "sinhala",
    "km": "khmer",
    "sn": "shona",
    "yo": "yoruba",
    "so": "somali",
    "af": "afrikaans",
    "oc": "occitan",
    "ka": "georgian",
    "be": "belarusian",
    "tg": "tajik",
    "sd": "sindhi",
    "gu": "gujarati",
    "am": "amharic",
    "yi": "yiddish",
    "lo": "lao",
    "uz": "uzbek",
    "fo": "faroese",
    "ht": "haitian creole",
    "ps": "pashto",
    "tk": "turkmen",
    "nn": "nynorsk",
    "mt": "maltese",
    "sa": "sanskrit",
    "lb": "luxembourgish",
    "my": "myanmar",
    "bo": "tibetan",
    "tl": "tagalog",
    "mg": "malagasy",
    "as": "assamese",
    "tt": "tatar",
    "haw": "hawaiian",
    "ln": "lingala",
    "ha": "hausa",
    "ba": "bashkir",
    "jw": "javanese",
    "su": "sundanese",
}

LANG_MAPPING = {v: k for k, v in LANGUAGE_CODES.items()}

TASK_MAPPING = {
    "asr": ["start", "end", "language"],
    "translation": ["source", "target"],
    "summarization": ["long_text", "short_text"],
    "question-answering": ["question", "lang"],
}

PROMPTS = {
    "question-answering": {
        "german": """Frage: {question}
    Beantworte die gegebene Frage detailiert mit dem folgenden Kontext:
    {text}""",
        "english": """Question: {question}
    Answer the given Question detailed with the following Context:
    {text}""",
    }
}