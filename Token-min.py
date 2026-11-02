from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")

text = "Hello, how are you?"

tokens = tokenizer.encode(text)

print("Tokens:", tokens)
print("Token count:", len(tokens))
