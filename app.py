# --------------------------------------------------------------
#  Sherubtse College – Continuous Assessment Dashboard
#  Author: Dr. Bimal K Chetri (PhD) – 2025
# --------------------------------------------------------------

import streamlit as st
import pandas as pd
import subprocess
import os
from pathlib import Path
from datetime import datetime

# ===================== CONFIG =====================
st.set_page_config(
    page_title="Sherubtse CA Dashboard",
    page_icon="📊",
    layout="wide"
)

ACCENT = "#0D47A1"   # Deep blue
SECOND = "#42A5F5"   # Light blue
WARN   = "#C62828"   # Red
CARD   = "#F9FAFB"   # Card background

REPO_DIR = Path(__file__).parent
os.chdir(REPO_DIR)

# ===================== GIT HELPERS =====================
def git_pull():
    try:
        subprocess.run(["git", "pull", "origin", "main"], check=True, capture_output=True)
        st.toast("✅ Synced with GitHub")
    except Exception:
        st.warning("⚠️ Git pull failed (offline or conflict)")

def git_push(file_path: Path, msg: str):
    try:
        subprocess.run(["git", "add", str(file_path)], check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        st.success("✅ Data saved & pushed to GitHub")
    except Exception as e:
        st.error(f"❌ Push failed: {e}")

# ===================== HEADER =====================
if (REPO_DIR / "college_logo.png").exists():
    st.image("college_logo.png", width=120)

st.markdown(
    f"""
    <div style="text-align:center;">
        <h1 style="color:{ACCENT}; margin-bottom:0;">Sherubtse College</h1>
        <h3 style="color:#555;">Department of Life Sciences</h3>
        <h4 style="color:#333;">Continuous Assessment Dashboard</h4>
    </div>
    """,
    unsafe_allow_html=True
)

# ===================== DATA =====================
@st.cache_data(ttl=60)
def load_data():
    files = {
        "BTS101 - Algae and Fungi (1st Year)": "BTS101.CA.xlsx",
        "BTS306 - Plant Breeding & Horticulture (3rd Year)": "BTS306.CA.xlsx"
    }
    data = {}
    for k, f in files.items():
        try:
            df = pd.read_excel(f)
            df.columns = [c.strip() for c in df.columns]
            df["Student No"] = df["Student No"].astype(str).str.strip().str.zfill(8)
            data[k] = df
        except Exception as e:
            st.error(f"Error loading {f}: {e}")
    return data, files

data_dict, file_map = load_data()
components = ['Written Assignment (15)', 'Class Test (15)', 'Lab Record (10)', 
              'Presentation (10)', 'Project Report (10)']
max_marks = [15, 15, 10, 10, 10]

git_pull()

# ===================== ACCESS MODE =====================
st.markdown("---")
st.markdown("### 🔑 Choose Access Mode")

c1, c2 = st.columns(2)
role = None
with c1:
    if st.button("👨‍🎓 Student View", use_container_width=True):
        role = "student"
with c2:
    if st.button("🧑‍🏫 Admin Access", use_container_width=True):
        role = "admin"

if not role:
    st.stop()

# ===================== ADMIN PANEL =====================
if role == "admin":
    pwd = st.text_input("Enter Admin Password", type="password")
    if pwd != st.secrets.get("ADMIN_PASSWORD", "bimal@123"):
        st.error("Incorrect password")
        st.stop()

    st.success("Admin access granted ✅")

    module = st.selectbox("Select Module", list(data_dict.keys()))
    df = data_dict[module].copy()
    file = Path(file_map[module])

    st.markdown("#### ✏️ Edit Marks Table")
    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Student No": st.column_config.TextColumn("Student No"),
            "Name": st.column_config.TextColumn("Student Name"),
            "Gender": st.column_config.SelectboxColumn("Gender", options=["M", "F", "Other"]),
            **{c: st.column_config.NumberColumn(c, min_value=0, max_value=m) for c, m in zip(components, max_marks)}
        },
        height=450
    )

    if st.button("💾 Save & Push Updates", type="primary", use_container_width=True):
        edited.to_excel(file, index=False)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = f"Admin update – {module} – {ts}"
        git_push(file, msg)
        st.cache_data.clear()
        st.rerun()

# ===================== STUDENT PANEL =====================
else:
    module = st.selectbox("📘 Select Your Module", list(data_dict.keys()))
    df = data_dict[module]

    st.markdown("#### 🎯 Enter Your Student Number")
    stu_no = st.text_input("", placeholder="e.g. 07250087", key="id").strip().zfill(8)

    if st.button("🔍 View My Marks", type="primary", use_container_width=True):
        if stu_no not in df["Student No"].values:
            st.error("Student No not found. Please check and try again.")
        else:
            stu = df[df["Student No"] == stu_no].iloc[0]
            st.success(f"**{stu['Name']}** – {stu['Gender']} – `{stu_no}`")

            total = 0
            for comp in components:
                mark = int(stu[comp]) if pd.notna(stu[comp]) else 0
                max_m = int(comp.split("(")[1].split(")")[0])
                total += mark
                st.markdown(f"**{comp.split(' (')[0]}** ({mark}/{max_m})")
                st.progress(mark / max_m if max_m > 0 else 0)

            st.markdown(
                f"""
                <div style="background:{CARD}; padding:20px; border-radius:15px; 
                            text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.1); margin-top:20px;">
                    <h3 style="color:{ACCENT}; margin:0;">Total CA Marks</h3>
                    <h1 style="color:{WARN}; margin:5px 0;">{total} <span style="font-size:0.6em;">/ 60</span></h1>
                </div>
                """,
                unsafe_allow_html=True
            )

# ===================== FOOTER =====================
st.markdown("---")
st.caption("Developed by Dr. Bimal K. Chetri (PhD) | Sherubtse College | 2025")
