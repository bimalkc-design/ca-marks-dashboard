# app.py – Sherubtse CA Dashboard | Simplified Student Results Viewer
# Refined by B.K. Chetri (PhD), Sherubtse College © 2025

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# ---------------------- Page Setup ----------------------
st.set_page_config(
    page_title="Sherubtse CA Results",
    page_icon="🎓",
    layout="wide"
)

# ---------------------- CSS ----------------------
st.markdown("""
<style>
.title {color: #003366; font-weight: bold; text-align: center; font-size: 2.5rem;}
.subtitle {color: #0066cc; text-align: center; font-size: 1.2rem;}
.header-box {background: white; padding: 1rem; border-radius: 12px; text-align:center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);}
.success-box {background: #d4edda; color: #155724; padding: 1rem; border-radius: 10px; font-weight: bold; text-align: center;}
.footer {color: #555; font-size: 0.9rem; text-align: center; margin-top: 1.5rem; font-style: italic;}
</style>
""", unsafe_allow_html=True)

# ---------------------- Header ----------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if os.path.exists("college_logo.png"):
        st.image("college_logo.png", width=140)
    st.markdown('<div class="header-box"><div class="title">Sherubtse College</div>'
                '<div class="subtitle">Continuous Assessment Results</div></div>',
                unsafe_allow_html=True)

# ---------------------- Excel Files ----------------------
excel_files = {
    "BTS101": "BTS101.CA.xlsx",
    "BTS306": "BTS306.CA.xlsx"
}

# ---------------------- Load Data ----------------------
@st.cache_data(ttl=3600)
def load_data():
    dfs = []
    for subj, file in excel_files.items():
        if not os.path.exists(file):
            st.warning(f"Missing file: {file}")
            continue

        df = pd.read_excel(file, dtype=str).apply(lambda x: x.str.strip() if x.dtype=='object' else x)
        marks_cols = [c for c in df.columns if re.search(r"\(\d+\)", c)]
        if not marks_cols:
            continue

        df_melted = df.melt(
            id_vars=["Student No", "Name", "Gender"],
            value_vars=marks_cols,
            var_name="Assessment_Type",
            value_name="Marks_Obtained"
        )
        df_melted["Max_Marks"] = df_melted["Assessment_Type"].str.extract(r"\((\d+)\)").astype(float)
        df_melted["Marks_Obtained"] = pd.to_numeric(df_melted["Marks_Obtained"], errors="coerce")
        df_melted = df_melted.dropna(subset=["Marks_Obtained"])
        df_melted["Subject"] = subj
        df_melted["Student_Number"] = df_melted["Student No"]
        dfs.append(df_melted)

    if not dfs:
        return pd.DataFrame()
    df_all = pd.concat(dfs, ignore_index=True)
    df_all["Percentage"] = (df_all["Marks_Obtained"] / df_all["Max_Marks"] * 100).round(2)
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
    st.caption("🔒 Secure & Private • View Only")

# ---------------------- Display Results ----------------------
if student_input and subject:
    sid_clean = ''.join(filter(str.isdigit, student_input.strip()))
    candidates = {sid_clean, "0"+sid_clean} if len(sid_clean)==7 else {sid_clean, sid_clean[1:]}

    filt = df[(df["Subject"]==subject) & (df["Student_Number"].isin(candidates))]

    if filt.empty:
        st.warning("No results found. Try with or without leading zero.")
    else:
        student = filt.iloc[0]
        st.markdown(f'<div class="success-box">Hello <strong>{student["Name"]}</strong>! '
                    f'Module: <strong>{subject}</strong> (ID: {student["Student_Number"]})</div>',
                    unsafe_allow_html=True)

        # ---------- Metrics ----------
        avg_pct = filt["Percentage"].mean()
        col1, col2, col3 = st.columns(3)
        col1.metric("Average %", f"{avg_pct:.1f}%")
        col2.metric("Assessments", len(filt))
        col3.metric("Status", "PASS" if avg_pct>=50 else "AT RISK")

        # ---------- Marks Table ----------
        st.markdown("### 📈 Your Marks")
        st.dataframe(filt[["Assessment_Type","Marks_Obtained","Max_Marks","Percentage"]], use_container_width=True)

        # ---------- Bar Chart ----------
        fig = px.bar(filt, x="Assessment_Type", y="Percentage", color="Percentage",
                     title="Performance Overview", text="Percentage", color_continuous_scale="Blues")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.add_hline(y=50, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------- Footer ----------------------
st.markdown("""
<div class="footer">
Developed using AI tool by Bimal K. Chetri (PhD), Dept. of Life Science, Sherubtse College © 2025
</div>
""", unsafe_allow_html=True)
