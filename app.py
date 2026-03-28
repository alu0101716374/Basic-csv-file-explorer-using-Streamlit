import streamlit as st

def main():
  main_page = st.Page("pages/1_main_page.py", title="Dataframe Explorer", default=True)
  summary_page = st.Page("pages/2_Display_Summary.py", title="Stat Summary")
  build_plot_page = st.Page("pages/4_build_a_plot.py", title="Build a Plot")
  dashboard_page = st.Page("pages/5_dashboard.py", title="Dashboard")
  missing_page = st.Page("pages/3_Clean_Data.py", title="Data Cleaning")
  pages = [main_page]
  if "original_df" in st.session_state and st.session_state.original_df is not None:
    pages.extend([summary_page, missing_page, build_plot_page, dashboard_page])
  pg = st.navigation(pages)
  pg.run()

        

if __name__ == "__main__":
    main()