import streamlit as st
import pandas as pd


def display_summary(df):
    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Total Missing", df.isna().sum().sum())

    summary = pd.DataFrame({
        "Column": df.columns,
        "Datatype": df.dtypes,
        "Unique values": df.nunique(),
        "Missing values": df.isna().sum()
    })

    st.dataframe(summary)


def display_stats(df):
    st.subheader("Numerical Statistics")

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        st.info("No numerical columns found.")
        return

    stats = numeric_df.describe().T
    stats = stats[["min", "max", "mean", "50%", "std"]]
    stats = stats.rename(columns={"50%": "median"})

    st.dataframe(stats)


def display_unique_top(df):
    st.subheader("Top Values")

    for col in df.columns:
        with st.expander(f"{col}"):
            st.write(f"Unique values: **{df[col].nunique()}**")

            top = df[col].value_counts().head(3)

            if len(top) > 0:
                top_df = pd.DataFrame({
                    "Value": top.index,
                    "Count": top.values
                })
                st.table(top_df)
            else:
                st.write("No repeated values.")


def main():
    st.set_page_config(page_title="Dataframe Summary", layout="wide")

    st.title("Dataframe Summary")
    if "original_df" not in st.session_state:
        st.error("No CSV file loaded.")
        st.stop()
    source = st.radio(
        "Select dataset to work with:",
        ("Original Data", "Filtered Data")
    )
    if source == "Original Data":
        df = st.session_state.original_df
    else:
        df = st.session_state.filtered_df


    tab1, tab2, tab3 = st.tabs(["Overview", "Statistics", "Top Values"])

    with tab1:
        display_summary(df)

    with tab2:
        display_stats(df)

    with tab3:
        display_unique_top(df)


if __name__ == "__main__":
    main()
