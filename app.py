from transformers import pipeline, set_seed
import torch

# Reproducible output ke liye
set_seed(42)

# GPU available ho to use karega, warna CPU
device = 0 if torch.cuda.is_available() else -1

generator = pipeline(
    "text-generation",
    model="distilgpt2",
    device=device
)

prompt = "Artificial Intelligence is"

output = generator(
    prompt,
    max_new_tokens=50,
    do_sample=True,
    temperature=0.7,
    top_k=50,
    top_p=0.9,
    repetition_penalty=1.2,
    pad_token_id=generator.tokenizer.eos_token_id,
    return_full_text=False
)

print(prompt + output[0]["generated_text"])
