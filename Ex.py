def llm_test(model):
    prompt = "Explain recursion in one sentence."
    response = model.generate(prompt)
    print(response)

llm_test(model)
 //model (grok)/DeepSeek R1 open source gpt 
