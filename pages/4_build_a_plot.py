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

def plot_exists(new_plot):
    for p in st.session_state.dashboard_plots:
        if (
            p["plot_type"] == new_plot["plot_type"] and
            p["data_source"] == new_plot["data_source"] and
            p["x"] == new_plot["x"] and
            p["y"] == new_plot["y"] and
            p["column"] == new_plot["column"]
        ):
            return True
    return False

def BuildPlot(edit_plot=None):
  st.subheader("Build a Plot")
  st.sidebar.title("Plot config")

  numerical_columns = st.session_state.original_df.select_dtypes(include=["number"]).columns.tolist()
  categorical_columns = st.session_state.original_df.select_dtypes(include=["object"]).columns.tolist()

  prefix = f"{edit_plot['id']}_" if edit_plot else ""

  plot_type_default = edit_plot["plot_type"] if edit_plot else "Scatter Plot"
  data_source_default = edit_plot["data_source"] if edit_plot else "Original"
  plot_title_default = edit_plot["title"] if edit_plot else plot_type_default
  x_default = edit_plot["x"] if edit_plot else None
  y_default = edit_plot["y"] if edit_plot else None
  column_default = edit_plot["column"] if edit_plot else None
  colour_column_default = edit_plot["colour_column"] if edit_plot else None

  plot_type = st.sidebar.selectbox(
    "Plot type",
    ["Scatter Plot", "Line plot", "Bar Chart", "Histogram",
     "Box Plot", "Heatmap", "Violin Plot", "Pie Chart"],
    index=["Scatter Plot", "Line plot", "Bar Chart", "Histogram",
           "Box Plot", "Heatmap", "Violin Plot", "Pie Chart"].index(plot_type_default),
    key=f"visualizations_plot_type_{prefix}"
  )

  data_source = st.sidebar.radio(
    "Choose Data Source",
    ["Original", "Filtered", "Both"],
    index=["Original", "Filtered", "Both"].index(data_source_default),
    key=f"visualizations_data_source_{prefix}"
  )

  x_column = y_column = column = None
  if plot_type in ["Scatter Plot", "Line plot"]:
    x_column = st.sidebar.selectbox(
      "X column", numerical_columns,
      index=numerical_columns.index(x_default) if x_default in numerical_columns else 0,
      key=f"visualizations_x_column_{prefix}"
    )
    y_column = st.sidebar.selectbox(
      "Y column", numerical_columns,
      index=numerical_columns.index(y_default) if y_default in numerical_columns else 0,
      key=f"visualizations_y_column_{prefix}"
    )
  elif plot_type == "Bar Chart":
    x_column = st.sidebar.selectbox(
      "X column", categorical_columns,
      index=categorical_columns.index(x_default) if x_default in categorical_columns else 0,
      key=f"visualizations_x_column_{prefix}"
    )
    y_column = st.sidebar.selectbox(
      "Y column", numerical_columns,
      index=numerical_columns.index(y_default) if y_default in numerical_columns else 0,
      key=f"visualizations_y_column_{prefix}"
    )
  elif plot_type == "Histogram":
    column = st.sidebar.selectbox(
      "Column", numerical_columns,
      index=numerical_columns.index(column_default) if column_default in numerical_columns else 0,
      key=f"visualizations_column_{prefix}"
    )
  elif plot_type in ["Box Plot", "Violin Plot"]:
    x_column = st.sidebar.selectbox(
      "X column (Group by)", categorical_columns,
      index=categorical_columns.index(x_default) if x_default in categorical_columns else 0,
      key=f"visualizations_x_column_{prefix}"
    )
    y_column = st.sidebar.selectbox(
      "Y column", numerical_columns,
      index=numerical_columns.index(y_default) if y_default in numerical_columns else 0,
      key=f"visualizations_y_column_{prefix}"
    )
  elif plot_type == "Pie Chart":
    column = st.sidebar.selectbox(
      "Column", categorical_columns,
      index=categorical_columns.index(column_default) if column_default in categorical_columns else 0,
      key=f"visualizations_column_{prefix}"
    )
  elif plot_type == "Heatmap":
    st.sidebar.info("Heatmap uses all numerical columns automatically")

  if plot_type not in ["Pie Chart", "Heatmap"]:
    available_color_columns = [
        col for col in categorical_columns
        if col not in [x_column, y_column]
    ]

    color_column = st.sidebar.selectbox(
        "Color by (optional)",
        [None] + available_color_columns,
        key="visualizations_color"
    )
  else:
      color_column = None
    
  # determine default title dynamically
  default_title = plot_type
  if plot_type in ["Scatter Plot", "Line plot", "Bar Chart", "Box Plot", "Violin Plot"]:
    if x_column and y_column:
        default_title += f": {x_column} vs {y_column}"
  elif plot_type in ["Histogram", "Pie Chart"]:
      if column:
        default_title += f": {column}"
  elif plot_type == "Heatmap":
      default_title += " (Heatmap)"
  st.session_state.plot_title_input = default_title
  plot_title = st.text_input(
    "Plot Title",
    key="plot_title_input"
  )



  config_for_preview = {
    "plot_type": plot_type,
    "data_source": data_source,
    "x": x_column,
    "y": y_column,
    "column": column,
    "colour_column": color_column,
    "title": st.session_state.plot_title_input
  }

  if data_source == "Original":
    render_single_plot(plot_type, st.session_state.original_df, config_for_preview, f"preview_original_{prefix}")
  elif data_source == "Filtered":
    render_single_plot(plot_type, st.session_state.filtered_df, config_for_preview, f"preview_filtered_{prefix}")
  else:
    col1, col2 = st.columns(2)
    with col1:
      render_single_plot(plot_type, st.session_state.original_df, config_for_preview, f"preview_original_{prefix}")
    with col2:
      render_single_plot(plot_type, st.session_state.filtered_df, config_for_preview, f"preview_filtered_{prefix}")

  # Add to dashboard button for new plots
  if not edit_plot:
    if st.sidebar.button("Add to Dashboard"):
      new_plots = []
      if data_source == "Both":
        new_plots.append({
          "id": str(uuid.uuid4()), "plot_type": plot_type,
          "data_source": "Original", "title": f"{plot_title} (Original)",
          "x": x_column, "y": y_column, "column": column, "colour_column": color_column
        })
        new_plots.append({
          "id": str(uuid.uuid4()), "plot_type": plot_type,
          "data_source": "Filtered", "title": f"{plot_title} (Filtered)",
          "x": x_column, "y": y_column, "column": column, "colour_column": color_column
        })
      else:
        new_plots.append({
          "id": str(uuid.uuid4()), "plot_type": plot_type,
          "data_source": data_source, "title": f"{plot_title} ({data_source})",
          "x": x_column, "y": y_column, "column": column,  "colour_column": color_column
        })

      added = False
      for p in new_plots:
        if not plot_exists(p):
          st.session_state.dashboard_plots.append(p)
          added = True

      if added:
        st.success(f"'{plot_title}' added to dashboard!")
      else:
        st.warning("This plot already exists in the dashboard!")

def main():
    st.title("Build a Plot")

    if "dashboard_plots" not in st.session_state:
        st.session_state.dashboard_plots = []
    
    BuildPlot()

if __name__ == "__main__":
    main()