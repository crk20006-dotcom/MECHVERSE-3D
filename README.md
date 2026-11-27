# MECHVERSE AI
Seven departments, twenty-eight interactive analytical experiments, Plotly 3D schematics, guided tutorials and NVIDIA tutor.

## Deploy on Streamlit Community Cloud
1. Extract this ZIP and upload its contents to a GitHub repository, preserving directories.
2. Open https://share.streamlit.io/ and create an app from that repository.
3. Select `app.py` as the entry point.
4. In Advanced settings / Secrets paste:
```toml
NVIDIA_API_KEY = "YOUR_PRIVATE_KEY"
NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"
```
Choose a model available to your NVIDIA account if this default is unavailable.
5. Deploy. Never commit the real secrets.toml file.

## Local
Python 3.11 recommended. `pip install -r requirements.txt` then `streamlit run app.py`.
Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` for local AI access.

## Scope
3D graphics are educational schematics, not CAD or FEA/CFD. Sliders update geometry or calculated results depending on the experiment. No continuous physics animation or persistent student accounts. AI requires network access and a valid NVIDIA key. A public app shares the administrator's API quota; restrict access or add authentication before broad public use. Verify results independently before engineering use.

See docs/PROJECT_GUIDE.md for report and presentation starters. Run `python -m unittest test_models` for initial checks.
