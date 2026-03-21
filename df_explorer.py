import pandas as pd
import streamlit as st
from functools import reduce
import operator

def init_state():
    if "original_df" not in st.session_state:
        st.session_state.original_df = None
    if "filter_groups" not in st.session_state:
        st.session_state.filter_groups = []  
    if "current_file" not in st.session_state:
        st.session_state.current_file = None
    if "selected_group" not in st.session_state:
        st.session_state.selected_group = 0
    if "global_group_logic" not in st.session_state:
        st.session_state.global_group_logic = "OR"  

def add_group_ui():
    st.sidebar.subheader("Groups")
    if st.sidebar.button("Add Group"):
        st.session_state.filter_groups.append({
            "logic": "AND",  
            "filters": []
        })
def add_filter_to_group_ui(df, group_idx):
    with st.expander("Add Filter to this group", expanded=False):
        st.session_state.selected_group = group_idx
        group = st.session_state.filter_groups[group_idx]

        # Group logic inside the group
        logic = st.radio(
            "Group logic (inside this group)",
            ["AND", "OR"],
            index=0 if group["logic"] == "AND" else 1,
            key=f"group_logic_{group_idx}"
        )
        group["logic"] = logic

        # Column selection
        column = st.selectbox("Column", df.columns, key=f"column_{group_idx}")
        col_data = df[column]

        if pd.api.types.is_numeric_dtype(col_data):
            key_min = f"min_{group_idx}_{column}"
            key_max = f"max_{group_idx}_{column}"

            # Initialize session state
            if key_min not in st.session_state:
                st.session_state[key_min] = float(col_data.min())
            if key_max not in st.session_state:
                st.session_state[key_max] = float(col_data.max())

            # Number inputs for min/max
            st.session_state[key_min] = st.number_input(
                "Min",
                min_value=float(col_data.min()),
                max_value=st.session_state[key_max],
                value=st.session_state[key_min],
                key=f"num_min_{group_idx}_{column}"
            )
            st.session_state[key_max] = st.number_input(
                "Max",
                min_value=st.session_state[key_min],
                max_value=float(col_data.max()),
                value=st.session_state[key_max],
                key=f"num_max_{group_idx}_{column}"
            )

            # Add filter button
            if st.button("Add Filter", key=f"add_{group_idx}_{column}_num"):
                group["filters"].append({
                    "column": column,
                    "type": "range",
                    "min": st.session_state[key_min],
                    "max": st.session_state[key_max]
                })
                st.rerun()

        else:
            values = st.multiselect(
                "Values",
                options=col_data.unique(),
                key=f"values_{group_idx}_{column}"
            )

            if st.button("Add Filter", key=f"add_{group_idx}_{column}_cat"):
                if values:
                    group["filters"].append({
                        "column": column,
                        "type": "categorical",
                        "values": values
                    })
                    st.rerun()


def show_filter_groups_ui():
    st.sidebar.subheader("Active Groups & Filters")
    if not st.session_state.filter_groups:
        st.sidebar.write("No active groups")
        return

    # Global logic selector
    st.sidebar.radio(
        "Combine groups using",
        ["AND", "OR"],
        index=0 if st.session_state.global_group_logic=="AND" else 1,
        key="global_group_logic"
    )

    for group_idx, group in enumerate(st.session_state.filter_groups):
        with st.sidebar.expander(f"Group {group_idx} - Logic: {group['logic']}", expanded=True):
            remove_group_key = f"Remove_{group_idx}" 
            if st.button("Remove Group", key=remove_group_key):
                st.session_state.filter_groups.pop(group_idx)
                st.rerun()
            add_filter_to_group_ui(st.session_state.original_df, group_idx)
            for filter_idx, f in enumerate(list(group["filters"])):
                label = (f"🔹 {f['column']} between {f['min']} and {f['max']}" 
                         if f["type"]=="range" else f"🔹 {f['column']} in {f['values']}")
                col1,col2 = st.columns([4,1])
                col1.write(label)
                remove_key = f"remove_{group_idx}_{filter_idx}_{f['column']}"
                if col2.button("X", key=remove_key):
                    group["filters"].pop(filter_idx)
                    st.rerun()


def main():
    st.title("📊 Dataframe Explorer - Grouped Filters")

    init_state()

    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        if (st.session_state.original_df is None 
            or uploaded_file.name != st.session_state.current_file):
            df = pd.read_csv(uploaded_file)
            st.session_state.original_df = df
            st.session_state.filter_groups = []
            st.session_state.current_file = uploaded_file.name
            st.success("Dataset successfully loaded")
            st.session_state.filtered_df = df


    if st.session_state.original_df is not None:
        df = st.session_state.original_df

        # Sidebar UI
        add_group_ui()
        show_filter_groups_ui()

        # Apply filters
        st.session_state.filtered_df = apply_groups(df)

        # Display
        st.subheader("📄 Filtered Data")
        st.dataframe(st.session_state.filtered_df)

if __name__ == "__main__":
    main()