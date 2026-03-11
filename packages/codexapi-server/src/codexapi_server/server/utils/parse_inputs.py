import copy
from dataclasses import dataclass

from codexapi_client import GPT_MODEL_NAME, REASONING_EFFORT, REASONING_SUMMARY
from ..vars import GPT_MODEL_NAME_SET, GPT_MODELS, REASONING_SUMMARY_VALUES, REASONING_EFFORT_VALUES


@dataclass
class ModelConfig:
    model: GPT_MODEL_NAME
    reasoning_effort: REASONING_EFFORT
    web_search: bool | None = None
    reasoning_summary: REASONING_SUMMARY | None = None


def parse_model_config(
    model: str # gpt-5.4-high-[web_search:true,reasoning_summary:detailed]
) -> ModelConfig:
    if model in GPT_MODEL_NAME_SET:
        return ModelConfig(model=model, reasoning_effort=GPT_MODELS[model][0])

    # get model parts
    model_parts = model.split("-")
    model_name_parts = []

    extra_args = {}
    reasoning_effort: REASONING_EFFORT | None = None
    web_search: bool | None = None
    reasoning_summary: REASONING_SUMMARY | None = None

    # gpt 5.4 high [web_search:true,reasoning_summary:detailed]

    for part in copy.deepcopy(model_parts):
        if part.startswith("[") and part.endswith("]"):
            # extra args
            extra_args = {
                kw_pair[0]: kw_pair[-1]
                for kw_pair in part.split(":")
                for kw in part.split(",")
            }

            for k, v in extra_args.items():
                if k == "web_search":
                    _v = str(v).lower()

                    if _v in {"true", "yes", "on", "1"}:
                        web_search = True
                    elif _v in {"false", "no", "off", "0"}:
                        web_search = False
                elif k == "reasoning_summary":
                    _reasoning_summary = str(v).lower()

                    if _reasoning_summary in REASONING_SUMMARY_VALUES:
                        reasoning_summary = _reasoning_summary

            continue

        if part in REASONING_EFFORT_VALUES:
            reasoning_effort = part
            continue

        model_name_parts.append(part)

    model_name = "-".join(model_name_parts)

    if model_name not in GPT_MODEL_NAME_SET:
        raise ValueError(f"Invalid model: {model}")

    if reasoning_effort is None:  # type: ignore[arg-type]
        reasoning_effort = GPT_MODELS[model_name][0]

    return ModelConfig(
        model=model_name,
        reasoning_effort=reasoning_effort,
        web_search=web_search,
        reasoning_summary=reasoning_summary
    )
