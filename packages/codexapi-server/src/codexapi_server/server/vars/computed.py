from typing import get_args

from codexapi_client import GPT_MODELS, GPT_MODEL_NAME, REASONING_SUMMARY, REASONING_EFFORT


GPT_MODEL_NAME_SET: set[GPT_MODEL_NAME] = set(get_args(GPT_MODEL_NAME))
ALL_GPT_MODELS = set(list(GPT_MODEL_NAME_SET) + [
    base_model_name + "-" + effort
    for base_model_name in GPT_MODEL_NAME_SET
    for effort in GPT_MODELS[base_model_name][1]
])

REASONING_SUMMARY_VALUES: set[REASONING_SUMMARY] = set(get_args(REASONING_SUMMARY))
REASONING_EFFORT_VALUES: set[REASONING_EFFORT] = set(get_args(REASONING_EFFORT))
