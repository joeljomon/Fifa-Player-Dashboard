import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

from src.clean_cluster import clean_data, cluster_players

st.set_page_config(page_title="Player Performance Dashboard", layout="wide")

st.title("Player Performance Dashboard")
st.write("Analyze player stats, compare performance, and cluster players by playing style.")

uploaded_file = st.sidebar.file_uploader("Upload player CSV", type=["csv"])
k = st.sidebar.slider("Number of clusters", min_value=2, max_value=6, value=4)

if uploaded_file:
    raw_df = pd.read_csv(uploaded_file)
else:
    raw_df = pd.read_csv("data/sample_players.csv")

df = clean_data(raw_df)
df, features = cluster_players(df, k=k)

st.sidebar.header("Filters")
positions = ["All"] + sorted(df["Position"].dropna().unique().tolist())
clubs = ["All"] + sorted(df["Club"].dropna().unique().tolist())

selected_position = st.sidebar.selectbox("Position", positions)
selected_club = st.sidebar.selectbox("Club", clubs)

filtered = df.copy()
if selected_position != "All":
    filtered = filtered[filtered["Position"] == selected_position]
if selected_club != "All":
    filtered = filtered[filtered["Club"] == selected_club]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Players", len(filtered))
col2.metric("Avg Age", round(filtered["Age"].mean(), 1) if len(filtered) else 0)
col3.metric("Total Goals", int(filtered["Goals"].sum()) if len(filtered) else 0)
col4.metric("Avg Value", f"€{filtered['Market_Value'].mean()/1_000_000:.1f}M" if len(filtered) else "€0M")

st.subheader("Playing Style Clusters")
fig_cluster = px.scatter(
    filtered,
    x="Goals_per_90",
    y="Assists_per_90",
    color="Playing_Style",
    size="Market_Value",
    hover_data=["Player", "Club", "Position", "Age", "Minutes"],
    title="Goals per 90 vs Assists per 90"
)
st.plotly_chart(fig_cluster, use_container_width=True)

left, right = st.columns(2)

with left:
    st.subheader("Top Players by Goal Contributions per 90")
    top_gc = filtered.sort_values("Goal_Contrib_per_90", ascending=False).head(10)
    fig_gc = px.bar(
        top_gc,
        x="Goal_Contrib_per_90",
        y="Player",
        color="Position",
        orientation="h",
        title="Top 10 Goal Contributors"
    )
    fig_gc.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_gc, use_container_width=True)

with right:
    st.subheader("Age vs Market Value")
    fig_value = px.scatter(
        filtered,
        x="Age",
        y="Market_Value",
        color="Position",
        hover_data=["Player", "Club"],
        title="Player Age and Market Value"
    )
    st.plotly_chart(fig_value, use_container_width=True)

st.subheader("Cluster Summary")
summary = filtered.groupby("Playing_Style")[[
    "Age", "Market_Value", "Minutes", "Goals_per_90", "Assists_per_90", "Goal_Contrib_per_90"
]].mean().round(2)
st.dataframe(summary, use_container_width=True)

st.subheader("Correlation Heatmap")
heatmap_cols = ["Age", "Market_Value", "Minutes", "Goals", "Assists", "Goals_per_90", "Assists_per_90", "Goal_Contrib_per_90"]
fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(filtered[heatmap_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)

st.subheader("Player Data")
st.dataframe(filtered.sort_values("Goal_Contrib_per_90", ascending=False), use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download clustered data", csv, "clustered_players.csv", "text/csv")
