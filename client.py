from openai import OpenAI

clinet = OpenAI(
    api_key="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"
)

 

completion = clinet.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud"},
    {"role": "user", "content": "what is coding"}
  ]
)

print(completion.choices[0].message.content)