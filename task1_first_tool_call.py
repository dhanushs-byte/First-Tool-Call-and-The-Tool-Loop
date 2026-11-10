
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL = os.getenv("OPENAI_MODEL")


# 1. Weather database
weather_data = {
    "Chennai": {
        "temperature": 31,
        "condition": "light rain"
    },
    "Bangalore": {
        "temperature": 24,
        "condition": "cloudy"
    },
    "Mumbai": {
        "temperature": 29,
        "condition": "sunny"
    }
}


# 2. Python function
def get_weather(city):
    return weather_data.get(
        city,
        {"error": f"Weather data unavailable for {city}"}
    )


# 3. Tool schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Get weather information for a city. "
                "Use this when the user asks about rain, "
                "temperature or weather conditions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"],
                "additionalProperties": False
            }
        }
    }
]


# 4. Initial conversation
messages = [
    {
        "role": "user",
        "content": "Is it raining in Chennai?"
    }
]


# 5. First LLM call
response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

assistant_message = response.choices[0].message

# Add assistant response
messages.append(
    assistant_message.model_dump(exclude_none=True)
)


# 6. Detect tool calls
if assistant_message.tool_calls:

    for tool_call in assistant_message.tool_calls:

        function_name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments
        )

        print(
            f"Tool requested: {function_name}"
            f"({json.dumps(arguments)})"
        )

        # Execute selected Python function
        if function_name == "get_weather":
            result = get_weather(**arguments)
        else:
            result = {"error": "Unknown tool"}

        print("Tool result:", result)

        # 7. Append tool result
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })

    # 8. Second LLM call
    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools
    )

    print("\nFinal:", final_response.choices[0].message.content)

else:
    print("Final:", assistant_message.content)
