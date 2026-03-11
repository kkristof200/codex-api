import json
import os
from dotenv import load_dotenv

from codexapi_client import CodexAPI, OpenAIChatCompletionAdaptorWS, OpenAIChatCompletionAdaptorHTTP


load_dotenv()


def main() -> None:
    chatgpt_acc_id = os.environ["CHATGPT_ACCOUNT_ID"]
    auth_token = os.environ["OPENAI_AUTH_TOKEN"]

    codex = CodexAPI()
    # for event in codex.request_ws(
    #     model_name="gpt-5.4",
    #     reasoning_effort="none",
    #     chatgpt_acc_id=chatgpt_acc_id,
    #     auth_token=auth_token,
    #     messages=[
    #         {
    #             "type": "message",
    #             "role": "user",
    #             "content": [
    #                 {
    #                     "type": "input_text",
    #                     "text": "What's up?"
    #                 }
    #             ],
    #         }
    #     ],
    #     adaptor=OpenAIChatCompletionAdaptorWS(),
    # ):
    #     print(event)

    res = codex.request_http(
        model_name="gpt-5.4",
        reasoning_effort="none",
        chatgpt_acc_id=chatgpt_acc_id,
        auth_token=auth_token,
        web_search=False,
        messages=[
            {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "How are you?"
                    }
                ],
            }
        ],
        adaptor=OpenAIChatCompletionAdaptorHTTP(),
    )
    print(json.dumps(res, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
