import gitlab,json
gl = gitlab.Gitlab('http://gitlab.bail.asia/', oauth_token='c98fe8f1af1eacb67f49597587c1aebd8be7d5e618a18e4ae170fdd95c6184c0')

def get_projects():
    projects = gl.projects.list(owned=True, get_all=True)
    return [project.to_json() for project in projects]


from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="",
)
messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "列出仓库"
        }
      ]
    }
  ]
response = client.chat.completions.create(
  model="gpt-4.1",
  messages=messages, # pyright: ignore[reportArgumentType]
  response_format={
    "type": "text"
  },
  tools=[
    {
      "type": "function",
      "function": {
        "name": "get_projects",
        "description": "Retrieves a list of all projects owned by the user",
        "parameters": {
          "type": "object",
          "properties": {},
          "additionalProperties": False,
          "required": []
        },
        "strict": True
      }
    }
  ],
  temperature=1,
  max_completion_tokens=2048,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

tool_call = response.choices[0].message.tool_calls[0] # pyright: ignore[reportOptionalSubscript]
args = json.loads(tool_call.function.arguments)
result = get_projects()

messages.append(response.choices[0].message)  # pyright: ignore[reportArgumentType] # append model's function call message
messages.append({                               # append result message
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": str(result)
})

completion_2 = client.chat.completions.create(
    model="gpt-4.1",
    messages=messages # pyright: ignore[reportArgumentType]
)

print(completion_2.choices[0].message.content)  # print the final response from the model