# app.py – Sherubtse CA Dashboard | Student Results Viewer
# Developed by B.K. Chetri (PhD), Sherubtse College © 2025

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# ---------------------- Page Setup ----------------------
st.set_page_config(page_title="Sherubtse CA Results", page_icon="🎓", layout="wide")

# ---------------------- CSS ----------------------
st.markdown("""
<style>
.title {color: #003366; font-weight: bold; text-align: center; font-size: 2.5rem;}
.subtitle {color: #0066cc; text-align: center; font-size: 1.3rem;}
.header-box {background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}
.success-box {background: #d4edda; color: #155724; padding: 1rem; border-radius: 10px; font-size: 1.2rem; font-weight: bold; text-align: center;}
.footer {color: #555; font-size: 1rem; text-align: center; margin-top: 2rem; font-style: italic;}
</style>
""", unsafe_allow_html=True)

# ---------------------- Header ----------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if os.path.exists("college_logo.png"):
        st.image("college_logo.png", width=140)
    st.markdown('<div class="header-box"><div class="title">Sherubtse College</div>'
                '<div class="subtitle">Continuous Assessment Results</div></div>', unsafe_allow_html=True)

# ---------------------- Excel Files ----------------------
excel_files = {"BTS101": "BTS101.CA.xlsx", "BTS306": "BTS306.CA.xlsx"}

# ---------------------- Load Data ----------------------
@st.cache_data(ttl=3600)
def load_data():
    dfs = []
    for subj, file in excel_files.items():
        if not os.path.exists(file):
            continue
        df = pd.read_excel(file, dtype=str)
        df.columns = df.columns.str.strip()
        df["Student No"] = df["Student No"].str.strip()
        keep_cols = ["Student No", "Name", "Gender"]
        marks_cols = [c for c in df.columns if re.search(r"\(\d+\)", c)]
        if not marks_cols:
            continue
        melted = df.melt(id_vars=keep_cols, value_vars=marks_cols,
                         var_name="Assessment_Type", value_name="Marks_Obtained")
        melted["Marks_Obtained"] = pd.to_numeric(melted["Marks_Obtained"], errors="coerce")
        melted = melted.dropna(subset=["Marks_Obtained"])
        melted["Max_Marks"] = melted["Assessment_Type"].str.extract(r"\((\d+)\)").astype(float)
        melted["Subject"] = subj
        melted["Student_Number"] = melted["Student No"]
        dfs.append(melted)
    if not dfs:
        return pd.DataFrame()
    df_all = pd.concat(dfs, ignore_index=True)
    df_all["Percentage"] = (df_all["Marks_Obtained"] / df_all["Max_Marks"] * 100).round(1)
    return df_all

df = load_data()

# ---------------------- Sidebar Login ----------------------
with st.sidebar:
    st.markdown("### 🎓 Student Login")
    if df.empty:
        st.error("No data available. Check Excel files.")
        st.stop()
    subject_list = sorted(df["Subject"].unique())
    subject = st.selectbox("Select Module", subject_list)
    student_input = st.text_input("Enter Student No", placeholder="e.g., 07250087", type="password")
    st.markdown("---")
    st.caption("🔒 Secure & Private • View Only")

# ---------------------- Process Login ----------------------
if student_input and subject:
    clean = ''.join(filter(str.isdigit, student_input.strip()))
    candidates = {clean}
    if clean.startswith("7") and len(clean) == 7:
        candidates.add("0" + clean)
    if clean.startswith("0") and len(clean) == 8:
        candidates.add(clean[1:])
    filt = df[(df["Subject"] == subject) & (df["Student_Number"].isin(candidates))]

    if filt.empty:
        st.warning("No results found. Try with or without leading zero.")
    else:
        row = filt.iloc[0]
        name, sid = row["Name"], row["Student_Number"]
        st.markdown(f'<div class="success-box">Hello <strong>{name}</strong>!<br>Module: <strong>{subject}</strong> (ID: {sid})</div>', unsafe_allow_html=True)

        # Metrics
        col1, col2, col3 = st.columns(3)
        avg_pct = filt["Percentage"].mean()
        col1.metric("Average %", f"{avg_pct:.1f}%")
        col2.metric("Assessments", len(filt))
        col3.metric("Status", "PASS" if avg_pct >= 50 else "AT RISK")

        # Marks Table
        st.markdown("### 📈 Your Marks")
        table = filt[["Assessment_Type", "Marks_Obtained", "Max_Marks", "Percentage"]]
        st.dataframe(table, use_container_width=True)

        # Bar Chart
        fig = px.bar(table, x="Assessment_Type", y="Percentage", text="Percentage",
                     color="Percentage", color_continuous_scale="Blues", title="Performance Overview")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.add_hline(y=50, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------- Footer ----------------------
st.markdown("""
<div class="footer">
Developed by Bimal K. Chetri (PhD), Sherubtse College © 2025
</div>
""", unsafe_allow_html=True)

