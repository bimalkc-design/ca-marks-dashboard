# app.py – Sherubtse CA Dashboard | Student Results Viewer | Mobile + PC
# Developed using AI tool by Bimal K. Chetri (PhD), Dept. of Life Science, B.Sc. in Life Science, Sherubtse © 2025

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# ----------------------
# Page Configuration
# ----------------------
st.set_page_config(
    page_title="Sherubtse CA Results",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------
# Appealing & Large-Font CSS (Big, Bold, Colorful)
# ----------------------
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #e6f7ff, #f0f8ff); padding: 2rem; border-radius: 15px;}
    .title {color: #003366; font-weight: bold; text-align: center; font-size: 3.5rem; margin-bottom: 0.5rem;}
    .subtitle {color: #0066cc; text-align: center; font-size: 1.8rem; margin-bottom: 1.5rem;}
    .header-box {background: #ffffff; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;}
    .success-box {background: #d4edda; color: #155724; padding: 1rem; border-radius: 10px; font-size: 1.6rem; font-weight: bold; text-align: center;}
    .metric-label {font-size: 1.4rem !important; font-weight: bold;}
    .metric-value {font-size: 2.2rem !important; color: #0066cc;}
    .stDataFrame {font-size: 1.6rem !important; text-align: center;}
    .stTextInput > div > div > input {font-size: 1.6rem; padding: 1rem; border-radius: 10px;}
    .stSelectbox > div > div {font-size: 1.6rem;}
    .stButton>button {background: #0066cc; color: white; font-size: 1.6rem; padding: 1rem; border-radius: 10px; width: 100%; font-weight: bold;}
    .footer {color: #555; font-size: 1.2rem; text-align: center; margin-top: 3rem; font-style: italic;}
    @media (max-width: 768px) {
        .title {font-size: 2.5rem;}
        .subtitle {font-size: 1.4rem;}
        .success-box {font-size: 1.4rem;}
        .metric-value {font-size: 1.8rem;}
        .stDataFrame {font-size: 1.4rem !important;}
        .stTextInput > div > div > input {font-size: 1.4rem;}
    }
</style>
""", unsafe_allow_html=True)

# ----------------------
# Header with Logo & Sherubtse Branding
# ----------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("college_logo.png"):
        st.image("college_logo.png", width=150)
    st.markdown('<div class="header-box"><div class="title">Sherubtse College</div><div class="subtitle">Continuous Assessment Results</div></div>', unsafe_allow_html=True)

# ----------------------
# Local Excel Files
# ----------------------
excel_files = {
    "BTS101": "BTS101.CA.xlsx",
    "BTS306": "BTS306.CA.xlsx"
}

# ----------------------
# Load Data – Exact Match from Excel
# ----------------------
@st.cache_data(ttl=3600)
def load_data():
    dfs = []
    base_path = "."  # Streamlit Cloud root
    for subj, filename in excel_files.items():
        path = os.path.join(base_path, filename)
        if not os.path.exists(path):
            st.error(f"File not found: {filename}. Contact Dr. Bimal.")
            continue
        try:
            df = pd.read_excel(path, dtype={"Student No": str})
            keep = ["Student No", "Name", "Gender"]
            mark_cols = [c for c in df.columns if re.search(r"\(\d+\)", c)]
            if not mark_cols:
                st.warning(f"No assessment columns in {filename}")
                continue
            melted = df.melt(id_vars=keep, value_vars=mark_cols,
                             var_name="Assessment_Type", value_name="Marks_Obtained")
            melted["Max_Marks"] = melted["Assessment_Type"].str.extract(r"\((\d+)\)").astype(float)
            melted["Marks_Obtained"] = pd.to_numeric(melted["Marks_Obtained"], errors="coerce")
            melted = melted.dropna(subset=["Marks_Obtained"])
            melted["Subject"] = subj
            melted["Student_Number"] = melted["Student No"].astype(str).str.strip()
            dfs.append(melted)
        except Exception as e:
            st.error(f"Error reading {filename}: {e}")
    if not dfs:
        st.error("No data loaded. Please try again later.")
        st.stop()
    data = pd.concat(dfs, ignore_index=True)
    data["Percentage"] = (data["Marks_Obtained"] / data["Max_Marks"] * 100).round(2)
    return data

df = load_data()

# ----------------------
# Sidebar – Simple & Friendly Login
# ----------------------
with st.sidebar:
    st.markdown("### 🎓 Student Login")
    subject = st.selectbox("**Select Module**", options=sorted(df["Subject"].unique()))
    student_input = st.text_input(
        "**Enter Student No**",
        placeholder="e.g., 07250087",
        type="password"
    )
    st.markdown("---")
    st.caption("🔒 Secure & Private • View Only")

if student_input and subject:
    clean_input = ''.join(filter(str.isdigit, student_input.strip()))
    
    if not (7 <= len(clean_input) <= 8):
        st.error("⚠️ Please enter 7–8 digits")
    else:
        candidates = [clean_input]
        if clean_input.startswith('7') and len(clean_input) == 7:
            candidates.append('0' + clean_input)
        if clean_input.startswith('0') and len(clean_input) == 8:
            candidates.append(clean_input[1:])

        filt = df[(df["Subject"] == subject) & (df["Student_Number"].isin(candidates))]
        
        if filt.empty:
            st.warning(f"❌ No results found for **{subject}**")
            st.info("💡 Try with or without leading zero")
        else:
            row = filt.iloc[0]
            name = row["Name"]
            matched_id = row["Student_Number"]
            st.markdown(f'<div class="success-box">Hello <strong>{name}</strong>! 👋<br>Module: <strong>{subject}</strong> (ID: {matched_id})</div>', unsafe_allow_html=True)

            # ---- Big Colorful Metrics ----
            col1, col2, col3 = st.columns(3)
            avg_pct = filt["Percentage"].mean()
            with col1:
                st.metric("**Average %**", f"{avg_pct:.1f}%", delta=None)
            with col2:
                st.metric("**Assessments**", len(filt))
            with col3:
                status = "🟢 **PASS**" if avg_pct >= 50 else "🔴 **AT RISK**"
                st.markdown(f"<div style='text-align:center;font-size:2rem;font-weight:bold;color:{'green' if avg_pct>=50 else 'red'}'>{status}</div>", unsafe_allow_html=True)

            # ---- Big Marks Table ----
            disp = filt[["Assessment_Type", "Marks_Obtained", "Max_Marks", "Percentage"]]
            st.markdown("### 📈 Your Marks")
            st.dataframe(
                disp.style.format({"Percentage": "{:.1f}%", "Marks_Obtained": "{:.1f}", "Max_Marks": "{:.0f}"})
                .applymap(lambda x: f"background-color: {'#d4edda' if x>=50 else '#f8d7da'}", subset=["Percentage"]),
                use_container_width=True
            )

            # ---- Big Bar Chart ----
            fig_bar = px.bar(
                disp, x="Assessment_Type", y="Percentage",
                title="📊 Performance Overview",
                color="Percentage", color_continuous_scale="Blues",
                text="Percentage"
            )
            fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_bar.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Pass Line")
            fig_bar.update_layout(height=400, font_size=16)
            st.plotly_chart(fig_bar, use_container_width=True)

            # ---- Big Pie Chart ----
            fig_pie = px.pie(
                disp, values="Percentage", names="Assessment_Type",
                title="🍰 Assessment Breakdown", hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=16)
            fig_pie.update_layout(height=400, font_size=16)
            st.plotly_chart(fig_pie, use_container_width=True)

# ----------------------
# Footer – Sherubtse Pride
# ----------------------
st.markdown("""
<div class="footer">
    Developed using AI tool by Bimal K. Chetri (PhD), Dept. of Life Science, B.Sc. in Life Science, Sherubtse © 2025
</div>
""", unsafe_allow_html=True)
