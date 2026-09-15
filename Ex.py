def llm_test(model):
    prompt = "Explain recursion in one sentence."
    response = model.generate(prompt)
    print(response)

llm_test(model)
