import tiktoken

text = """
Hello, I am Akshay. I am an AI/ML engineer.
Testing tokenization in Python.
"""

encoding = tiktoken.get_encoding("cl100k_base")

tokens = encoding.encode(text)

print("Text:", text)
print("Token IDs:", tokens)
print("Total Tokens:", len(tokens))
print("Decoded:", encoding.decode(tokens))
