import anthropic
import os

client = anthropic.Anthropic(
    # Will automatically use the ANTHROPIC_API_KEY environment variable
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Replace placeholders like {{BOOK_CONTENT}} with real values,
# because the SDK does not support variables.
message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=20000,
    temperature=1,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hello, how are you?"
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "<literary_analysis>"
                }
            ]
        }
    ]
)
print(message.content[0].text)