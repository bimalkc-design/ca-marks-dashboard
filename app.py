cat > app.py <<'PY'
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
    page_title="Sherubtse CA Marks",
    page_icon="Chart",
    layout="wide",
    initial_sidebar_state="expanded"
)

ACCENT = "#1F618D"
WARN   = "#CB4335"
CARD   = "#FFFFFF"

REPO_DIR = Path(__file__).parent
os.chdir(REPO_DIR)

# ===================== GIT HELPERS (SSH) =====================
def git_pull():
    try:
        result = subprocess.run(["git", "pull", "origin", "main"], 
                              capture_output=True, text=True, check=True)
        if "Already up to date" not in result.stdout:
            st.toast("Synced with GitHub")
    except Exception:
        st.warning("Git pull failed (offline or conflict)")

def git_push(file_path: Path, msg: str):
    try:
        subprocess.run(["git", "add", str(file_path)], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", msg], check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        st.success(f"Pushed: {msg}")
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode() if e.stderr else str(e)
        st.error(f"Push failed: {err}")
        raise

# ===================== HEADER =====================
logo_path = REPO_DIR / "college_logo.png"
if logo_path.exists():
    st.image(str(logo_path), width=100)
st.markdown(
    f"<h1 style='text-align:center; color:{ACCENT};'>Sherubtse College</h1>"
    "<h2 style='text-align:center; color:#555;'>Department of Life Science</h2>"
    "<h3 style='text-align:center; color:#333;'>Continuous Assessment Dashboard</h3>",
    unsafe_allow_html=True
)

# ===================== DATA LOADING =====================
@st.cache_data(ttl=60)
def load_data():
    files = {
        "BTS101 - Algae and Fungi (1st Year)": "BTS101.CA.xlsx",
        "BTS306 - Plant Breeding & Horticulture (3rd Year)": "BTS306.CA.xlsx"
    }
    data = {}
    for name, fn in files.items():
        try:
            df = pd.read_excel(fn)
            df.columns = [c.strip() for c in df.columns]
            df["Student No"] = df["Student No"].astype(int).astype(str).str.zfill(8)
            data[name] = df
        except Exception as e:
            st.error(f"Failed to load **{fn}**: {e}")
    return data, files

data_dict, file_map = load_data()
ca_components = [
    'Written Assignment (15)', 'Class Test (15)', 'Lab Record (10)',
    'Presentation (10)', 'Project Report (10)'
]
max_vals = [15, 15, 10, 10, 10]

git_pull()  # Sync on start

# ===================== ACCESS MODE =====================
st.markdown("### Choose Access Mode")
c1, c2 = st.columns(2)
role = None
with c1:
    if st.button("Student View", use_container_width=True):
        role = "student"
with c2:
    if st.button("Admin Login", use_container_width=True):
        role = "admin"

if not role:
    st.info("Please select your access mode.")
    st.stop()

# ===================== ADMIN SECTION =====================
if role == "admin":
    pwd = st.text_input("Admin Password", type="password")
    if pwd != st.secrets.get("ADMIN_PASSWORD", "bimal@123"):
        st.error("Incorrect password")
        st.stop()

    st.success("Admin access granted")
    module = st.selectbox("Module", list(data_dict.keys()))
    df = data_dict[module].copy()
    excel_file = Path(file_map[module])

    st.markdown("#### Edit All Students")
    edited = st.data_editor(
        df,
        num_rows="dynamic",
        column_config={
            "Student No": st.column_config.TextColumn(required=True),
            "Name": st.column_config.TextColumn(required=True),
            "Gender": st.column_config.SelectboxColumn("Gender", options=["M", "F", "Other"], required=True),
            **{c: st.column_config.NumberColumn(c, min_value=0, max_value=m) for c, m in zip(ca_components, max_vals)}
        },
        use_container_width=True
    )

    col_save, col_log = st.columns([1, 2])
    with col_save:
        if st.button("Save & Push to GitHub", type="primary", use_container_width=True):
            edited.to_excel(excel_file, index=False)
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            msg = f"Admin update – {module} – {ts}"
            try:
                git_push(excel_file, msg)
                st.cache_data.clear()
                st.rerun()
            except:
                pass  # error already shown

    with col_log:
        st.markdown("#### Recent Commits")
        try:
            log = subprocess.check_output(["git", "log", "--oneline", "-8"], text=True).strip().split("\n")
            for line in log:
                if line.strip():
                    sha, *rest = line.split(" ", 1)
                    msg = rest[0] if rest else ""
                    st.caption(f"`{sha[:7]}` {msg}")
        except:
            st.caption("Log unavailable")

    st.markdown("---")
    st.markdown("#### Quick Edit (Single Student)")
    sel_stu = st.selectbox("Select Student", edited["Student No"].tolist(), key="quick")
    row_idx = edited[edited["Student No"] == sel_stu].index[0]
    stu = edited.loc[row_idx]

    cols = st.columns(3)
    new_marks = {}
    for i, comp in enumerate(ca_components):
        with cols[i % 3]:
            cur = stu[comp] if pd.notna(stu[comp]) else 0
            new_marks[comp] = st.number_input(comp, min_value=0, max_value=max_vals[i], value=int(cur), step=1, key=f"m{i}")

    if st.button("Update This Student"):
        for c, v in new_marks.items():
            edited.at[row_idx, c] = v
        edited.to_excel(excel_file, index=False)
        msg = f"Quick edit: {stu['Name']} ({sel_stu})"
        try:
            git_push(excel_file, msg)
            st.success("Updated!")
            st.cache_data.clear()
            st.rerun()
        except:
            pass

# ===================== STUDENT SECTION =====================
else:
    module = st.selectbox("Module", list(data_dict.keys()))
    df = data_dict[module]

    st.markdown("### Enter Your Student No")
    stu_no = st.text_input("", placeholder="e.g. 07250087", key="id").strip().zfill(8)

    if stu_no and st.button("View My Marks", use_container_width=True):
        if stu_no not in df["Student No"].values:
            st.error("Student No not found.")
        else:
            stu = df[df["Student No"] == stu_no].iloc[0]
            st.success(f"**{stu['Name']}** – {stu['Gender']} – `{stu_no}`")

            total = 0
            for comp in ca_components:
                mark = int(stu[comp]) if pd.notna(stu[comp]) else 0
                max_m = int(comp.split("(")[1].split(")")[0])
                total += mark
                prog = mark / max_m if max_m > 0 else 0
                st.markdown(f"**{comp.split(' (')[0]}**")
                st.progress(prog)
                st.caption(f"{mark} / {max_m}")

            st.markdown(
                f"""
                <div style="text-align:center; margin:30px 0; padding:20px;
                            background:{CARD}; border-radius:15px;
                            box-shadow:0 4px 12px rgba(0,0,0,0.1)">
                    <h2 style="color:{ACCENT}; margin:0">Total CA Marks</h2>
                    <h1 style="color:{WARN}; margin:5px 0">{total}<small style="font-size:0.6em">/60</small></h1>
                </div>
                """,
                unsafe_allow_html=True
            )

# ===================== FOOTER =====================
st.markdown("---")
st.caption("Developed using AI tool by Bimal K Chetri (PhD) | Sherubtse College | 2025")

