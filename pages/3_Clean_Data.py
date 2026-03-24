import streamlit as st
import pandas as pd


def DisplayMissing():
  df = st.session_state.original_df
  col1, col2, col3 = st.columns(3)
  col1.metric("Total Rows: ", df.shape[0])
  col2.metric("Total Missing Entries: ", df.isna().sum().sum())
  missing_percent = (df.isna().sum() / df.shape[0] * 100).round(2)
  col3.metric("Missing Percentage: ", missing_percent.sum().astype(str) + "%")

  summary = pd.DataFrame({
    "Column:": df.columns,
    "Datatype": df.dtypes,
    "Missing count":df.isna().sum(),
    "Missing Percentage": missing_percent.astype(str) + "%"
  })
  st.dataframe(summary)


def CleanData():
  if "edited_df" not in st.session_state:
     st.session_state.edited_df = st.session_state.original_df
  if st.session_state.original_df.isna().sum().sum() > 0:
    if st.button("Drop missing entries"):
        st.session_state.edited_df = st.session_state.original_df.copy().dropna()
        st.info("Missing entries Dropped")

  st.session_state.edited_df = st.data_editor(st.session_state.edited_df)  
  if st.button("Save Changes"):
     st.info("Applying Changes")
     st.session_state.original_df = st.session_state.edited_df
     st.rerun()

def main():
  if "original_df" not in st.session_state: 
    st.error("No csv file loaded")
    st.stop()
  else:
    st.title("Clean Data")
    tab1, tab2 = st.tabs(["Missing Data overview", "Clean data"])
    with tab2:
        CleanData()
    with tab1:
        DisplayMissing()

if __name__ == "__main__":
    main()