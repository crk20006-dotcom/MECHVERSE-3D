from pathlib import Path
import json, os, urllib.request, urllib.error
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(page_title="MECHVERSE 3D", page_icon="⚙️", layout="wide")
root=Path(__file__).parent
from tutorials import LESSONS
st.title("MECHVERSE 3D")
page=st.radio("Choose a section", ["3D Laboratory", "Tutorial Centre", "AI Tutor — Chat"], horizontal=True, key="navigation")
if page == "Tutorial Centre":
    st.header("Tutorial Centre")
    name=st.selectbox("Choose experiment", list(LESSONS))
    theory,formula,variables,example,procedure,question,answer=LESSONS[name]
    for heading,content in [("Theory",theory),("Formula",formula),("Variables and units",variables),("Solved example",example),("Simulation procedure",procedure),("Viva question",question)]:
        st.subheader(heading); st.write(content)
    with st.expander("Reveal viva answer"): st.write(answer)
    st.download_button("Download tutorial notes", "\n\n".join([name,theory,formula,variables,example,procedure,question,answer]), file_name="tutorial.txt")
if page == "3D Laboratory":
    html=(root/"index.html").read_text(encoding="utf-8")
    for name in ("labs.js","app.js"):
        html=html.replace(f'<script src="{name}"></script>', '<script>'+ (root/name).read_text(encoding="utf-8")+'</script>')
    components.html(html,height=1800,scrolling=True)
if page == "AI Tutor — Chat":
    st.header("Mechanical engineering AI tutor")
    try:
        key=st.secrets.get("GROQ_API_KEY", "")
        model=st.secrets.get("GROQ_MODEL", "openai/gpt-oss-120b")
    except Exception:
        key=""; model="openai/gpt-oss-120b"
    key=key or os.getenv("GROQ_API_KEY", "")
    st.caption("Enter your experiment parameters or paste your readings for tailored help. The 3D workspace does not automatically transmit its state to this tutor.")
    history=st.session_state.setdefault("groq_history", [])
    if st.button("Clear chat"):
        history.clear()
    if not key: st.info("Set GROQ_API_KEY in Streamlit Secrets to enable chat.")
    for msg in history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    with st.form("ask_tutor", clear_on_submit=True):
        question=st.text_area("Type your question here", placeholder="Explain the slider-crank mechanism...", disabled=not bool(key))
        send=st.form_submit_button("Send question", disabled=not bool(key))
    question=question.strip() if send else ""
    if question:
        history.append({"role":"user","content":question})
        with st.chat_message("user"): st.markdown(question)
        with st.chat_message("assistant"):
            try:
                payload={"model":model,"messages":[{"role":"system","content":"You are a mechanical engineering tutor. Explain equations, units, assumptions and numerical steps. Do not invent experimental readings or certify designs."}]+history[-12:],"temperature":0.3,"max_completion_tokens":1500}
                req=urllib.request.Request("https://api.groq.com/openai/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
                with st.spinner("Thinking..."):
                    with urllib.request.urlopen(req,timeout=60) as response: reply=json.load(response)["choices"][0]["message"]["content"]
                st.markdown(reply); history.append({"role":"assistant","content":reply})
            except urllib.error.HTTPError as e:
                hints={400:"Check model name and request settings.",401:"Check your Groq API key.",403:"Check account permissions.",404:"Check model availability.",429:"Rate limit or quota reached; retry later."}
                st.error(f"Groq HTTP {e.code}: {hints.get(e.code, 'Provider request failed; retry later.')}")
            except (urllib.error.URLError,TimeoutError): st.error("Groq connection failed or timed out. Retry later.")
            except Exception: st.error("Unexpected tutor response. Check model configuration and retry.")
