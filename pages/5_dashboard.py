import streamlit as st
import plotly.express as px
import uuid
def render_single_plot(plot_type, df, config, page):
    if plot_type == "Scatter Plot":
        fig = px.scatter(df, x=config["x"], y=config["y"], color=config["colour_column"])
    elif plot_type == "Line plot":
        fig = px.line(df, x=config["x"], y=config["y"], color=config["colour_column"])
    elif plot_type == "Bar Chart":
        fig = px.bar(df, x=config["x"], y=config["y"], color=config["colour_column"])
    elif plot_type == "Histogram":
        fig = px.histogram(df, x=config["column"], color=config["colour_column"])
    elif plot_type == "Box Plot":
        fig = px.box(df, x=config["x"], y=config["y"], color=config["colour_column"])
    elif plot_type == "Violin Plot":
        fig = px.violin(df, x=config["x"], y=config["y"], color=config["colour_column"])
    elif plot_type == "Pie Chart":
        fig = px.pie(df, names=config["column"])
    elif plot_type == "Heatmap":
        numeric_df = df.select_dtypes(include="number")
        fig = px.imshow(numeric_df.corr(), text_auto=True)
    else:
        st.error("Unsupported plot type")
        return
    unique_key = f"{page}:{config['title']}:{uuid.uuid4()}"
    st.plotly_chart(fig, use_container_width=True, key=unique_key)

def VisualizationDashboard():
  st.subheader("Visualization Dashboard")

  col1, col2 = st.columns(2)
  with col1:
    if st.button("Clear Dashboard"):
      st.session_state.dashboard_plots = []
      st.success("Dashboard Cleared")
  with col2:
    plots_per_row = st.slider("Plots per Row", min_value=1, max_value=6,   value=3, key="visualizations_plot_per_row")

  plots = st.session_state.dashboard_plots
  numerical_columns = st.session_state.original_df.select_dtypes(include=["number"]).columns.tolist()
  categorical_columns = st.session_state.original_df.select_dtypes(include=["object"]).columns.tolist()

  for i in range(0, len(plots), plots_per_row):
    row_plots = plots[i:i + plots_per_row]
    cols = st.columns(len(row_plots))
    for j, plot_config in enumerate(row_plots):
      with cols[j]:
        with st.expander(plot_config["title"], expanded=True):
          df = st.session_state.original_df if plot_config["data_source"] == "Original" else st.session_state.filtered_df

          action = st.radio(
            "",
            ["", "Edit", "Remove"],
            index=0,
            horizontal=True,
            key=f"action_{plot_config['id']}"
          )

          if action == "Remove":
            st.session_state.dashboard_plots.pop(i + j)
            st.rerun()

          elif action == "Edit":
            # Inline editing widgets
            plot_type = st.selectbox(
              "Plot type",
              ["Scatter Plot", "Line plot", "Bar Chart", "Histogram",
               "Box Plot", "Heatmap", "Violin Plot", "Pie Chart"],
              index=["Scatter Plot", "Line plot", "Bar Chart", "Histogram",
                     "Box Plot", "Heatmap", "Violin Plot", "Pie Chart"].index(plot_config["plot_type"]),
              key=f"edit_plot_type_{plot_config['id']}"
            )

            x_column = y_column = column = None
            if plot_type in ["Scatter Plot", "Line plot"]:
              x_column = st.selectbox("X column", numerical_columns,
                index=numerical_columns.index(plot_config["x"]) if plot_config["x"] in numerical_columns else 0,
                key=f"edit_x_{plot_config['id']}")
              y_column = st.selectbox("Y column", numerical_columns,
                index=numerical_columns.index(plot_config["y"]) if plot_config["y"] in numerical_columns else 0,
                key=f"edit_y_{plot_config['id']}")
            elif plot_type == "Bar Chart":
              x_column = st.selectbox("X column", categorical_columns,
                  index=categorical_columns.index(plot_config["x"]) if plot_config["x"] in categorical_columns else 0,
                  key=f"edit_x_{plot_config['id']}")
              y_column = st.selectbox("Y column", numerical_columns,
                  index=numerical_columns.index(plot_config["y"]) if plot_config["y"] in numerical_columns else 0,
                  key=f"edit_y_{plot_config['id']}")
            elif plot_type == "Histogram":
              column = st.selectbox("Column", numerical_columns,
                  index=numerical_columns.index(plot_config["column"]) if plot_config["column"] in numerical_columns else 0,
                  key=f"edit_column_{plot_config['id']}")
            elif plot_type in ["Box Plot", "Violin Plot"]:
              x_column = st.selectbox("X column (Group by)", categorical_columns,
                  index=categorical_columns.index(plot_config["x"]) if plot_config["x"] in categorical_columns else 0,
                  key=f"edit_x_{plot_config['id']}")
              y_column = st.selectbox("Y column", numerical_columns,
                  index=numerical_columns.index(plot_config["y"]) if plot_config["y"] in numerical_columns else 0,
                  key=f"edit_y_{plot_config['id']}")
            elif plot_type == "Pie Chart":
              column = st.selectbox("Column", categorical_columns,
                  index=categorical_columns.index(plot_config["column"]) if plot_config["column"] in categorical_columns else 0,
                  key=f"edit_column_{plot_config['id']}")
            

            if plot_type not in ["Pie Chart", "Heatmap"]:
              available_color_columns = [
                  col for col in categorical_columns
                  if col not in [x_column, y_column]
              ]

              color_column = st.selectbox(
                  "Color by (optional)",
                  [None] + available_color_columns,
                  index=categorical_columns.index(plot_config["colour_column"]) if plot_config["colour_column"] is not None else 0,
                  key=f"edit_{plot_config['id']} visualizations_color"
              )
            else:
                color_column = None

            plot_config["colour_column"] = color_column
    

            plot_title = st.text_input("Plot Title",
              value=plot_config["title"],
              key=f"edit_title_{plot_config['id']}")

            if st.button("Save Changes", key=f"save_{plot_config['id']}"):
              plot_config.update({
                "plot_type": plot_type,
                "title": plot_title,
                "x": x_column,
                "y": y_column,
                "column": column,
                "colour_column": color_column
              })
              st.success("Plot updated!")
              st.rerun()

          # Render the plot
          render_single_plot(plot_config["plot_type"], df, plot_config, f"dashboard_{plot_config['id']}")

def main():
    st.title("📈 Dashboard")


    if "dashboard_plots" not in st.session_state:
        st.session_state.dashboard_plots = []

    VisualizationDashboard()

if __name__ == "__main__":
    main()