import streamlit as st
import pandas as pd
import os
import random

st.set_page_config(page_title="IQAC Planner & Tracker", layout="wide")

# File paths
SCHOOL_DEPT_PATH = "school_department_mapping_cleaned.csv"
TARGET_PLAN_PATH = "iqac_target_plan.csv"
os.makedirs("data", exist_ok=True)

# Load or initialize school-dept mapping
if os.path.exists(SCHOOL_DEPT_PATH):
    school_df = pd.read_csv(SCHOOL_DEPT_PATH).dropna().drop_duplicates()
else:
    school_df = pd.DataFrame(columns=["School", "Department"])

# Tabs: Master | Planner | Tracker
tab1, tab2, tab3 = st.tabs(["🏫 School–Department Master", "🎯 Target Planner", "📊 Demo – Target Progress"])

# -------------------- TAB 1: MASTER --------------------
with tab1:
    st.title("🏫 School & Department Master Editor")
    st.markdown("Add, edit, or delete Schools and their Departments below.")

    edited_school_df = st.data_editor(
        school_df,
        num_rows="dynamic",
        use_container_width=True,
        key="school_editor"
    )

    if st.button("💾 Save School–Department Master", key="save_school"):
        edited_school_df.dropna(subset=["School", "Department"], inplace=True)
        edited_school_df.drop_duplicates(inplace=True)
        edited_school_df.to_csv(SCHOOL_DEPT_PATH, index=False)
        st.success("✅ Master list saved successfully!")

    st.download_button(
        "📥 Download School–Department CSV",
        data=edited_school_df.to_csv(index=False).encode("utf-8"),
        file_name="school_department_master.csv",
        mime="text/csv"
    )

# -------------------- TAB 2: TARGET PLANNER --------------------
with tab2:
    st.title("🎯 IQAC Target Planner")
    st.markdown("Define targets for each department or school.")

    # Reload school mapping
    if os.path.exists(SCHOOL_DEPT_PATH):
        school_df = pd.read_csv(SCHOOL_DEPT_PATH).dropna().drop_duplicates()
        schools = sorted(school_df["School"].unique())
        dept_map = {
            school: sorted(school_df[school_df["School"] == school]["Department"].unique())
            for school in schools
        }
    else:
        schools = []
        dept_map = {}

    # Load existing targets
    if os.path.exists(TARGET_PLAN_PATH):
        target_df = pd.read_csv(TARGET_PLAN_PATH)
    else:
        target_df = pd.DataFrame(columns=["School", "Department", "Target Field", "Target Quantity"])

    st.subheader("➕ Add New Target")

    # School → Department selection
    selected_school = st.selectbox("School", schools, key="school_selectbox")
    dept_options = ["ALL"] + dept_map.get(selected_school, [])
    selected_dept = st.selectbox("Department", dept_options, key="dept_selectbox")

    with st.form("add_target_form"):
        col1, col2 = st.columns(2)
        with col1:
            target_field = st.text_input("Target Field (e.g., FDPs, Workshops)")
        with col2:
            quantity = st.number_input("Target Quantity", min_value=0, step=1)

        if st.form_submit_button("Add Target"):
            if not target_field.strip():
                st.error("Target field cannot be empty.")
            else:
                new_row = {
                    "School": selected_school,
                    "Department": selected_dept,
                    "Target Field": target_field.strip(),
                    "Target Quantity": int(quantity)
                }
                target_df = pd.concat([target_df, pd.DataFrame([new_row])], ignore_index=True)
                target_df.to_csv(TARGET_PLAN_PATH, index=False)
                st.success("✅ Target added.")
                st.rerun()

    # Editable target table
    st.subheader("📋 All Targets")
    edited_targets = st.data_editor(
        target_df,
        num_rows="dynamic",
        use_container_width=True,
        key="target_editor"
    )

    if st.button("💾 Save All Targets", key="save_targets"):
        edited_targets.dropna(subset=["School", "Target Field", "Target Quantity"], inplace=True)
        edited_targets.to_csv(TARGET_PLAN_PATH, index=False)
        st.success("✅ Targets saved successfully!")

    st.download_button(
        "📥 Download Target Plan CSV",
        data=edited_targets.to_csv(index=False).encode("utf-8"),
        file_name="iqac_target_plan.csv",
        mime="text/csv"
    )

# -------------------- TAB 3: MOCK TRACKER --------------------
with tab3:
    st.title("📊 Demo – Target Progress Tracker")

    if os.path.exists(TARGET_PLAN_PATH):
        df = pd.read_csv(TARGET_PLAN_PATH)

        if df.empty:
            st.warning("No target data found. Please add targets in Tab 2.")
        else:
            st.markdown("This is a **demo** using mock data for 'Target Achieved'.")

            # Simulate Target Achieved
            def mock_achieved(row):
                lower = max(0, int(row["Target Quantity"]) - 2)
                upper = int(row["Target Quantity"]) + 3
                return random.randint(lower, upper)

            df["Target Achieved"] = df.apply(mock_achieved, axis=1)
            df["% Achieved"] = (df["Target Achieved"] / df["Target Quantity"].replace(0, 1)) * 100
            df["% Achieved"] = df["% Achieved"].round(1)

            for idx, row in df.iterrows():
                st.markdown(f"**🎯 {row['School']} – {row['Department']} | {row['Target Field']}**")
                st.progress(min(int(row["% Achieved"]), 100), text=f"{row['Target Achieved']} / {row['Target Quantity']}")

            st.dataframe(df, use_container_width=True)
    else:
        st.warning("Target file not found. Add some entries first.")
