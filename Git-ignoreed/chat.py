import os
import sys
import requests
from dotenv import load_dotenv
from openai import OpenAI

# chat_loop.py: Simple GPT-4o ↔ GPT4All HTTP loop
# - Starts from a user prompt
# - Remembers last 3 exchanges
# - Runs 2 cycles per pause, then pauses (continue/new prompt/exit)

# Load env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT4ALL_API_URL = os.getenv("GPT4ALL_API_URL", "http://localhost:4891/v1/chat/completions")
GPT4ALL_MODEL = os.getenv("GPT4ALL_MODEL", "Phi-3 Mini Instruct")
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY not found in .env", file=sys.stderr)
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

class ChatLoop:
    def __init__(self, memory_size=3, cycles_per_pause=2):
        self.memory_size = memory_size
        self.cycles_per_pause = cycles_per_pause
        self.history = []  # list of tuples (gpt4o, local)

    def call_gpt4o(self, messages):
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return resp.choices[0].message.content.strip()

    def call_gpt4all(self, user_text):
        payload = {
            "model": GPT4ALL_MODEL,
            "messages": [{"role": "user", "content": user_text}],
            "max_tokens": 512,
            "temperature": 0.7
        }
        r = requests.post(GPT4ALL_API_URL, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()

    def run(self):
        prompt = input("User prompt: ").strip()
        if not prompt:
            print("No prompt provided. Exiting.")
            return

        cycle = 0
        while True:
            # Build GPT-4o messages with memory
            msgs = [{"role":"system","content":"You are GPT-4o, a helpful assistant."}]
            for g, l in self.history:
                msgs.append({"role":"assistant","content":g})
                msgs.append({"role":"user","content":l})
            msgs.append({"role":"user","content": prompt})

            # GPT-4o -> text
            gpt_out = self.call_gpt4o(msgs)
            print(f"\nGPT-4o:\n{gpt_out}\n")

            # Local Llama HTTP
            local_out = self.call_gpt4all(gpt_out)
            print(f"Llama ({GPT4ALL_MODEL}):\n{local_out}\n")

            # update history
            self.history.append((gpt_out, local_out))
            if len(self.history) > self.memory_size:
                self.history.pop(0)

            cycle += 1
            if cycle >= self.cycles_per_pause:
                cycle = 0
                choice = input("[Enter]=continue, 'exit'=quit, or new prompt: ")
                if choice.strip().lower() == 'exit':
                    print("Goodbye.")
                    break
                if choice.strip():
                    prompt = choice.strip()
                    self.history.clear()
                # else: keep prompt

if __name__ == "__main__":
    ChatLoop().run()
