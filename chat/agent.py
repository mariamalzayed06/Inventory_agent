import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from .tools import (
    add_item,
    remove_item,
    check_stock,
    list_items,
    tool_declarations,
)

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

AVAILABLE_FUNCTIONS = {
    "add_item": add_item,
    "remove_item": remove_item,
    "check_stock": check_stock,
    "list_items": list_items,
}

SYSTEM_PROMPT = """
You are an inventory management assistant for a warehouse.

You have access to tools that let you add stock, remove stock, check
quantities, and list all items. Use these tools whenever the user's
request requires reading or changing inventory data — never guess or
make up quantities yourself.

Rules:
- Item names should be treated as case-insensitive and singular
  (e.g. "screwdrivers" refers to the item "screwdriver").
- If a user asks to remove more stock than is available, tell them
  clearly what went wrong instead of pretending it succeeded.
- If a request is ambiguous (e.g. no quantity given), ask a clarifying
  question instead of calling a tool with a guessed value.
- After calling a tool, always summarize the result for the user in
  plain, friendly language — do not just repeat raw numbers with no
  context.
- Do not answer any question unrelated to the inventory task.
"""

tools = types.Tool(function_declarations=tool_declarations)

config = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=[tools],
)


def run_agent(user_message: str) -> str:
    """
    Sends the user's message to Gemini, executes any function calls
    it requests, sends the results back, and repeats until the model
    responds with plain text. Returns that final text.
    """
    contents = [
        types.Content(role="user", parts=[types.Part(text=user_message)])
    ]

    while True:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents,
            config=config,
        )

        function_call = _extract_function_call(response)

        if function_call is None:
            return response.text

        name = function_call.name
        args = dict(function_call.args)

        func = AVAILABLE_FUNCTIONS.get(name)
        if func is None:
            result = {"error": f"Unknown function '{name}' requested."}
        else:
            result = func(**args)


        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=name,
                        response={"result": result},
                    )
                ],
            )
        )


def _extract_function_call(response):
    """
    Returns the function_call part of the model's response if there
    is one, otherwise None.
    """
    candidate = response.candidates[0]
    for part in candidate.content.parts:
        if part.function_call:
            return part.function_call
    return None