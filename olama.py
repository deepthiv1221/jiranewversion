import subprocess
import json

# Example prompt
prompt = "Summarize this text: 'Hello world, I am testing Ollama.'"

# Call the Ollama CLI
result = subprocess.run(
    ["ollama", "generate", "gemma:2b", prompt, "--json"],
    capture_output=True,
    text=True
)

# Parse the JSON output
response = json.loads(result.stdout)
print(response['text'])
