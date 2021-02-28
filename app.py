import streamlit as st

from datetime import datetime, date
from functions import load_data, pace, read_markdown_file, filedownload, summary_stats
from charts import radar_chart, time_series, clustering

# Title and info
st.title('cRUNching the numbers')
intro_markdown = read_markdown_file("info.md")
st.markdown(intro_markdown, unsafe_allow_html=True)
st.markdown("---")

# Sidebar inputs
st.sidebar.header('k-means clustering')
st.sidebar.write('Select a date range and the number of clusters, then click Run to see a preview of the clustered data')
start_date = st.sidebar.date_input('Start date', date(2018, 1, 1))
end_date = st.sidebar.date_input('End date', date.today())
slider_input = st.sidebar.slider('Number of clusters (k)', min_value=1, max_value=10)

# Load cleaned data
runs = load_data()

# k-means clustering
if st.sidebar.button('Run'):
    output = clustering(runs, start_date, end_date, slider_input)

    cluster_counts = output[0]
    st.sidebar.write('Clusters')
    st.sidebar.dataframe(cluster_counts)

    st.write('Preview')
    bucket_data = output[1]
    st.dataframe(bucket_data.head())
    st.sidebar.markdown(filedownload(bucket_data), unsafe_allow_html=True)
st.sidebar.markdown("---")

# Radar chart 
radar_chart_fig = radar_chart(runs)
st.plotly_chart(radar_chart_fig)

# Time series plot
ts_fig = time_series(runs)
st.plotly_chart(ts_fig)
