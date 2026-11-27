from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(page_title='MECHVERSE 3D', page_icon='⚙️', layout='wide')
root=Path(__file__).parent
html=(root/'index.html').read_text(encoding='utf-8')
for name in ('labs.js','app.js'):
    html=html.replace(f'<script src="{name}"></script>', '<script>'+ (root/name).read_text(encoding='utf-8')+'</script>')
components.html(html,height=1800,scrolling=True)
