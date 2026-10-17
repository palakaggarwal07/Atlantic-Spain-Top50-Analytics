import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Spain Top 50 Analytics",
    page_icon="🎵",
    layout="wide"
)

# ==========================================
# LOAD DATA
# ==========================================

@st.cache_data
def load_data():
    return pd.read_csv("data/feature_data.csv")


df = load_data()

# Convert date columns
df["entry_date"] = pd.to_datetime(df["entry_date"], errors="coerce")
df["exit_date"] = pd.to_datetime(df["exit_date"], errors="coerce")

# ==========================================
# TITLE
# ==========================================

st.title("🎵 Spain Top 50 Songs Analytics")

st.markdown(
    "### Content Maturity, Release Lifecycle & Playlist Rotation Analysis"
)

st.write(
    "Interactive analysis of song lifecycle, playlist retention, "
    "rank movement, popularity growth, and playlist rotation."
)

# ==========================================
# INTERACTIVE FILTERS
# ==========================================

st.markdown("## 🎛️ Dashboard Filters")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    lifecycle_filter = st.multiselect(
        "Lifecycle Stage",
        options=sorted(df["lifecycle_stage"].dropna().unique()),
        default=sorted(df["lifecycle_stage"].dropna().unique())
    )

with filter_col2:
    content_filter = st.multiselect(
        "Content Type",
        options=sorted(df["content_type"].dropna().unique()),
        default=sorted(df["content_type"].dropna().unique())
    )

with filter_col3:
    release_filter = st.multiselect(
        "Release Type",
        options=sorted(df["release_type"].dropna().unique()),
        default=sorted(df["release_type"].dropna().unique())
    )

with filter_col4:
    duration_filter = st.multiselect(
        "Duration Category",
        options=sorted(df["duration_category"].dropna().unique()),
        default=sorted(df["duration_category"].dropna().unique())
    )

# ==========================================
# APPLY FILTERS
# ==========================================

filtered_df = df[
    df["lifecycle_stage"].isin(lifecycle_filter)
    & df["content_type"].isin(content_filter)
    & df["release_type"].isin(release_filter)
    & df["duration_category"].isin(duration_filter)
].copy()

st.write(
    f"Showing **{len(filtered_df):,}** records "
    f"out of **{len(df):,}** total records."
)

# ==========================================
# FILTERED KPI CALCULATIONS
# ==========================================

total_songs = filtered_df["song"].nunique()

avg_lifecycle = filtered_df["days_on_playlist"].mean()

avg_observed_days = filtered_df["observed_playlist_days"].mean()

avg_stability = filtered_df["retention_stability_index"].mean()

avg_popularity_growth = filtered_df["popularity_growth"].mean()

# ==========================================
# KPI CARDS
# ==========================================

st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "🎵 Total Songs",
        total_songs
    )

with col2:
    st.metric(
        "📅 Avg Lifecycle",
        f"{avg_lifecycle:.2f} days"
    )

with col3:
    st.metric(
        "⏱️ Avg Observed Days",
        f"{avg_observed_days:.2f} days"
    )

with col4:
    st.metric(
        "📈 Avg Stability",
        f"{avg_stability:.2f}"
    )

with col5:
    st.metric(
        "🔥 Avg Popularity Growth",
        f"{avg_popularity_growth:.2f}"
    )

# ==========================================
# DATASET OVERVIEW
# ==========================================

st.markdown("## 📋 Dataset Overview")

col1, col2 = st.columns(2)

with col1:
    st.write(f"**Filtered Records:** {len(filtered_df):,}")

with col2:
    st.write(f"**Total Features:** {len(df.columns)}")

st.dataframe(
    filtered_df.head(10),
    use_container_width=True
)

# ==========================================
# LIFECYCLE STAGE ANALYSIS
# ==========================================

st.markdown("## 🔄 Song Lifecycle Distribution")

lifecycle_counts = (
    filtered_df["lifecycle_stage"]
    .value_counts()
    .reindex([
        "New Entry",
        "Growth Phase",
        "Peak Phase",
        "Mature Phase",
        "Decline Phase"
    ])
    .fillna(0)
    .reset_index()
)

lifecycle_counts.columns = [
    "Lifecycle Stage",
    "Songs"
]

st.bar_chart(
    lifecycle_counts,
    x="Lifecycle Stage",
    y="Songs"
)

# ==========================================
# MONTHLY PLAYLIST ROTATION
# ==========================================

st.markdown("## 🔄 Monthly Playlist Rotation")

monthly_entries = (
    filtered_df
    .groupby(filtered_df["entry_date"].dt.to_period("M"))
    .size()
    .reset_index(name="Entries")
)

monthly_entries["month"] = (
    monthly_entries["entry_date"]
    .astype(str)
)

monthly_exits = (
    filtered_df
    .groupby(filtered_df["exit_date"].dt.to_period("M"))
    .size()
    .reset_index(name="Exits")
)

monthly_exits["month"] = (
    monthly_exits["exit_date"]
    .astype(str)
)

monthly_rotation = pd.merge(
    monthly_entries[["month", "Entries"]],
    monthly_exits[["month", "Exits"]],
    on="month",
    how="outer"
).fillna(0)

monthly_rotation = monthly_rotation.sort_values("month")

st.line_chart(
    monthly_rotation.set_index("month")[["Entries", "Exits"]]
)

# Churn calculation
if len(monthly_rotation) > 0:
    average_churn = (
        (
            monthly_rotation["Entries"]
            + monthly_rotation["Exits"]
        ) / 50 * 100
    ).mean()
else:
    average_churn = 0

st.metric(
    "🔄 Average Monthly Churn",
    f"{average_churn:.2f}%"
)

# ==========================================
# POPULARITY BY LIFECYCLE STAGE
# ==========================================

st.markdown("## 📈 Popularity Across Lifecycle Stages")

popularity_data = (
    filtered_df
    .groupby("lifecycle_stage")
    .agg(
        Entry_Popularity=("entry_popularity", "mean"),
        Peak_Popularity=("peak_popularity", "mean"),
        Latest_Popularity=("latest_popularity", "mean")
    )
    .reindex([
        "New Entry",
        "Growth Phase",
        "Peak Phase",
        "Mature Phase",
        "Decline Phase"
    ])
    .round(2)
)

st.bar_chart(
    popularity_data
)

# ==========================================
# CLEAN VS EXPLICIT ANALYSIS
# ==========================================

st.markdown("## 🎧 Clean vs Explicit Content")

content_comparison = (
    filtered_df
    .groupby("content_type")
    .agg(
        Songs=("song", "count"),
        Avg_Lifecycle=("days_on_playlist", "mean"),
        Avg_Observed_Days=(
            "observed_playlist_days",
            "mean"
        ),
        Avg_Stability=(
            "retention_stability_index",
            "mean"
        ),
        Avg_Popularity_Growth=(
            "popularity_growth",
            "mean"
        )
    )
    .round(2)
)

st.dataframe(
    content_comparison,
    use_container_width=True
)

# ==========================================
# SINGLE VS ALBUM ANALYSIS
# ==========================================

st.markdown("## 💿 Single vs Album Performance")

release_comparison = (
    filtered_df
    .groupby("release_type")
    .agg(
        Songs=("song", "count"),
        Avg_Lifecycle=(
            "days_on_playlist",
            "mean"
        ),
        Avg_Observed_Days=(
            "observed_playlist_days",
            "mean"
        ),
        Avg_Time_to_Peak=(
            "time_to_peak_days",
            "mean"
        ),
        Avg_Peak_Position=(
            "peak_position",
            "mean"
        ),
        Avg_Stability=(
            "retention_stability_index",
            "mean"
        ),
        Avg_Popularity_Growth=(
            "popularity_growth",
            "mean"
        )
    )
    .round(2)
)

st.dataframe(
    release_comparison,
    use_container_width=True
)

# ==========================================
# SONG DURATION ANALYSIS
# ==========================================

st.markdown("## ⏱️ Song Duration vs Playlist Performance")

duration_comparison = (
    filtered_df
    .groupby("duration_category")
    .agg(
        Songs=("song", "count"),
        Avg_Observed_Days=(
            "observed_playlist_days",
            "mean"
        ),
        Avg_Lifecycle=(
            "days_on_playlist",
            "mean"
        ),
        Avg_Peak_Position=(
            "peak_position",
            "mean"
        ),
        Avg_Stability=(
            "retention_stability_index",
            "mean"
        )
    )
    .reindex([
        "Short (<3 min)",
        "Medium (3–4 min)",
        "Long (>4 min)"
    ])
    .round(2)
)

st.dataframe(
    duration_comparison,
    use_container_width=True
)

# ==========================================
# ALBUM SIZE ANALYSIS
# ==========================================

st.markdown("## 💿 Album Size vs Playlist Retention")

filtered_df["album_size_category"] = pd.cut(
    filtered_df["total_tracks"],
    bins=[0, 1, 7, 12, float("inf")],
    labels=[
        "1 Track",
        "2–7 Tracks",
        "8–12 Tracks",
        "13+ Tracks"
    ]
)

album_size_comparison = (
    filtered_df
    .groupby(
        "album_size_category",
        observed=True
    )
    .agg(
        Songs=("song", "count"),
        Avg_Observed_Days=(
            "observed_playlist_days",
            "mean"
        ),
        Avg_Lifecycle=(
            "days_on_playlist",
            "mean"
        ),
        Avg_Stability=(
            "retention_stability_index",
            "mean"
        )
    )
    .round(2)
)

st.dataframe(
    album_size_comparison,
    use_container_width=True
)

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "Spain Top 50 Songs Analytics | "
    "Content Maturity, Release Lifecycle & Playlist Rotation Analysis"
)

# ==========================================
# SONG EXPLORER
# ==========================================

st.markdown("---")
st.markdown("## 🔎 Song Explorer")

search_term = st.text_input(
    "Search by song title or artist",
    placeholder="Enter a song name or artist..."
)

if search_term:
    search_results = filtered_df[
        filtered_df["song"].astype(str).str.contains(
            search_term, case=False, na=False
        )
        | filtered_df["artist"].astype(str).str.contains(
            search_term, case=False, na=False
        )
    ]

    if not search_results.empty:
        st.dataframe(
            search_results[
                [
                    "song",
                    "artist",
                    "entry_date",
                    "exit_date",
                    "entry_position",
                    "peak_position",
                    "latest_position",
                    "lifecycle_stage",
                    "days_on_playlist",
                    "popularity_growth"
                ]
            ],
            use_container_width=True
        )
    else:
        st.info("No matching songs found. Try another title or artist.")
else:
    st.caption("Enter a song title or artist to explore its playlist performance.")



# ==========================================
# KEY BUSINESS INSIGHTS
# ==========================================

st.markdown("---")
st.markdown("## 💡 Key Business Insights")

if not filtered_df.empty:

    decline_pct = (
        filtered_df["lifecycle_stage"]
        .eq("Decline Phase")
        .mean() * 100
    )

    single_lifecycle = filtered_df.loc[
        filtered_df["release_type"] == "Single",
        "days_on_playlist"
    ].mean()

    album_lifecycle = filtered_df.loc[
        filtered_df["release_type"] == "Album",
        "days_on_playlist"
    ].mean()

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            f"**Lifecycle:** {decline_pct:.2f}% of "
            "filtered records are in the Decline Phase. "
            "This helps identify songs that may need "
            "closer performance monitoring."
        )

        if pd.notna(single_lifecycle) and pd.notna(album_lifecycle):
            st.success(
                f"**Release Type:** Singles average "
                f"{single_lifecycle:.2f} playlist days, "
                f"compared with {album_lifecycle:.2f} "
                "days for albums in the selected data."
            )

    with col2:
        avg_growth = filtered_df["popularity_growth"].mean()

        st.info(
            f"**Popularity:** Average popularity growth "
            f"is {avg_growth:.2f} points in the selected data."
        )

        avg_retention = (
            filtered_df["observed_playlist_days"].mean()
        )

        st.success(
            f"**Playlist Retention:** Songs remain on the "
            f"playlist for an average of "
            f"{avg_retention:.2f} observed days."
        )

else:
    st.warning(
        "No records match the selected filters. "
        "Choose at least one option in each filter."
    )
