import streamlit as st
import pandas as pd

# detect missing entries (option to fill or drop them)
def MissingEntries(df):
  total_missing = df.isna().sum().sum()
  st.metric("Total Missing Entries: ", total_missing)
  summary = pd.DataFrame({
    "Column": df.columns,
    "Missing Entries": df.isna().sum(),
    "Missing percentage: ": (df.isna().sum() / df.shape[0])
  })
  st.dataframe(summary)

def CleanMissing(df):
    with st.form("missing_data_form"):
        option = st.radio(
            "Choose a cleaning action:",
            ("Drop missing rows", "Fill numeric with mean")
        )
        submit = st.form_submit_button("Apply")

    if submit:
        if option == "Drop missing rows":
            rows_before = len(df)
            df = df.dropna()
            rows_after = len(df)
            st.success(f"Dropped {rows_before - rows_after} rows with missing values.")

        elif option == "Fill numeric with mean":
            numeric_cols = df.select_dtypes(include="number").columns
            df[numeric_cols] = df[numeric_cols].fillna(
                df[numeric_cols].mean()
            )
            st.success(f"Filled missing values in {len(numeric_cols)} numeric columns.")

   
    st.markdown("---")
    st.subheader("Manual edits (edit any cell below)")

    # Initialize session state for manual edits
    if "manual_edit" not in st.session_state:
        st.session_state.manual_edit = df.copy()

    # Show editor and bind to session state
    edited_df = st.data_editor(
        st.session_state.manual_edit,
        key="manual_editor",
        num_rows="dynamic"
    )

    # Save button updates the main df
    if st.button("Save manual edits"):
        st.success("Manual edits applied!")
        return edited_df 
    st.session_state.manual_edit = df
    st.rerun()
    return df

def main():
  if "original_df" in st.session_state:
    source = st.radio(
        "Select dataset to work with:",
        ("Original Data", "Filtered Data")
    )
    if source == "Original Data":
        df = st.session_state.original_df
    else:
        df = st.session_state.filtered_df
    tab1, tab2 = st.tabs(["Missing overview", "Clean data"])
    with tab1:
       st.subheader("Missing entries overwiew")
       MissingEntries(df)
    with tab2:
      st.subheader("Clean data")
      if source == "Original Data": 
        st.session_state.original_df = CleanMissing(df)  
      else: 
         st.sesison_state.filtered_df = CleanMissing(df)
  else:
    st.error("No csv file has been uploaded")

  st.stop()
main()
