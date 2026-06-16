from transformers import pipeline

# Small model, beginner-friendly
generator = pipeline("text-generation", model="distilgpt2")

prompt = "Artificial Intelligence is"

output = generator(
    prompt,
    max_new_tokens=50,
    do_sample=True,
    temperature=0.7
)

print(output[0]["generated_text"])
