from openai import OpenAI
def answer(key,model,messages,context):
    client=OpenAI(base_url="https://integrate.api.nvidia.com/v1",api_key=key,timeout=60)
    system="""You are MECHVERSE, a mechanical engineering tutor. Explain step by step with units, assumptions, equations and checks. Use the supplied experiment context, distinguish schematic visualization from validated physics, and do not invent measurements. Teach in the student's requested language. Never claim a design is certified safe."""
    response=client.chat.completions.create(model=model,messages=[{"role":"system","content":system+"\nCurrent experiment: "+context}]+messages[-12:],temperature=.3,max_tokens=1800)
    return response.choices[0].message.content or "No text returned."
