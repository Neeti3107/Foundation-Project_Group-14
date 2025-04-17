import os
from datetime import datetime

# === 1. Write config.toml for light theme ===
os.makedirs(".streamlit", exist_ok=True)
with open(".streamlit/config.toml", "w") as f:
    f.write("""
[theme]
base="light"
primaryColor="#d73b3e"
backgroundColor="#ffffff"
secondaryBackgroundColor="#f5f5f5"
textColor="#262730"
font="sans serif"
""")

# === 2. Inject header & branding into app.py ===
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

branding_block = '''
st.set_page_config(
    page_title="Sugar Forecast App",
    page_icon="🍬",
    layout="wide"
)

st.markdown(\"\"\"
    <style>
    .title-wrapper {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .title-wrapper h1 {
        color: #d73b3e;
        font-size: 2.2rem;
    }
    .title-wrapper p {
        color: #444;
        font-size: 1.1rem;
        margin-top: -0.5rem;
    }
    </style>
    <div class="title-wrapper">
        <h1>🍬 Sugar Price Forecasting App</h1>
        <p>Built with ❤️ using LSTM + FastAPI + Streamlit</p>
    </div>
\"\"\", unsafe_allow_html=True)
'''

if "title-wrapper" not in "".join(lines):
    for i, line in enumerate(lines):
        if "st.set_page_config" in line or line.startswith("st.title"):
            lines.insert(i + 1, branding_block)
            break

# === 3. Update metrics display ===
for i, line in enumerate(lines):
    if 'st.success(f"📅 Forecast Month:' in line:
        lines[i] = 'col1, col2 = st.columns(2)\n'
        lines[i+1] = 'col1.success(f"📅 Forecast Month: **{first[\'month\']}**")\n'
        lines[i+2] = 'col2.metric("Predicted Price (INR)", f"₹{first[\'price\']}")\n'
        break

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ Styling & branding successfully applied!")
