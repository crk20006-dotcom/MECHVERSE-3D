import json, os
import streamlit as st
from catalog import LABS
from tutor import answer
st.set_page_config(page_title="MECHVERSE AI",page_icon="⚙️",layout="wide")
st.title("MECHVERSE AI")
st.caption("Interactive mechanical engineering laboratory · 7 departments · 28 experiments")
with st.sidebar:
    st.header("Laboratory")
    department=st.selectbox("Department",list(LABS))
    name=st.selectbox("Experiment",list(LABS[department]))
    solver,params=LABS[department][name]
    st.subheader("Experiment controls")
    values=[st.slider(label,lo,hi,default,step,key=name+label) for label,lo,hi,default,step in params]
    def reset():
        for label,lo,hi,default,step in params: st.session_state[name+label]=default
    st.button("Reset controls",on_click=reset)
r=solver(*values)
context=json.dumps({"experiment":name,"inputs":dict(zip([p[0] for p in params],values)),"results":{k:float(v) for k,v in r["metrics"].items()},"assumptions":r["note"]})
lab,tutor,guide=st.tabs(["3D laboratory","AI tutor","Tutorial & export"])
with lab:
    st.subheader(name)
    cols=st.columns(3)
    for i,(k,v) in enumerate(r["metrics"].items()): cols[i%3].metric(k,f"{v:,.4g}")
    st.plotly_chart(r["fig"],use_container_width=True,key=name+"3d")
    st.caption("Drag to orbit · scroll/pinch to zoom · use chart toolbar to reset camera")
    st.plotly_chart(r["chart"],use_container_width=True,key=name+"graph")
    st.latex(r["formula"]);st.info(r["note"])
    if name=="Helical spring designer":
        if r["metrics"]["Stress safety ratio"]<1: st.error("Calculated shear stress exceeds the selected allowable stress.")
        if not 4<=r["metrics"]["Spring index"]<=12: st.warning("Spring index outside the common preliminary design range of 4–12.")
    if name=="Pressure vessel" and values[1]/values[2]<=20: st.warning("Thin-wall assumption is not satisfied.")
with tutor:
    st.subheader("NVIDIA AI Tutor")
    try: key=st.secrets.get("NVIDIA_API_KEY",""); model=st.secrets.get("NVIDIA_MODEL","meta/llama-3.3-70b-instruct")
    except Exception: key="";model="meta/llama-3.3-70b-instruct"
    key=key or os.getenv("NVIDIA_API_KEY","")
    if not key: st.warning("Administrator: configure NVIDIA_API_KEY in Streamlit secrets. Simulations work without it.")
    history=st.session_state.setdefault("history_"+name,[])
    if st.button("Clear conversation"): history.clear()
    for msg in history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    question=st.chat_input("Ask about this experiment",disabled=not bool(key))
    if question:
        history.append({"role":"user","content":question})
        with st.chat_message("user"): st.markdown(question)
        with st.chat_message("assistant"):
            try:
                with st.spinner("Tutor is thinking..."): reply=answer(key,model,history,context)
                st.markdown(reply);history.append({"role":"assistant","content":reply})
            except Exception: st.error("NVIDIA request failed. Check model access, API key, quota and connectivity.")
with guide:
    st.subheader("Guided experiment")
    st.markdown("**Aim:** Investigate "+name.lower()+" and the relationship between its inputs and outputs.")
    st.markdown("1. Record the initial parameters and calculated results.\n2. Rotate the 3D model and inspect its geometry.\n3. Change one input while holding the others constant.\n4. Compare the graph and numerical results with the governing equation.\n5. Ask the AI tutor to explain the trend and discuss assumptions.")
    st.latex(r["formula"]);st.write(r["note"])
    st.subheader("Observation journal")
    observation=st.text_area("Record your observations",key="obs_"+name)
    report="# "+name+"\\n\\n## Inputs and results\\n"+context+"\\n\\n## Observations\\n"+observation
    st.download_button("Download lab journal",report,file_name="lab_journal.md")
    st.download_button("Download interactive 3D model",r["fig"].to_html(include_plotlyjs=True),file_name="model.html",mime="text/html")
    st.download_button("Download experiment data",context,file_name="experiment.json",mime="application/json")
