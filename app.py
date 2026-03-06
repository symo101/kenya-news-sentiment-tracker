import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from wordcloud import WordCloud

st.set_page_config(
    page_title="Kenya News Sentiment Tracker",
    page_icon="📰",
    layout="wide"
)

#Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #1565C0;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #1565C0; }
    .metric-label { font-size: 13px; color: #666; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)


#Load data 
@st.cache_data
def load_data():
    df = pd.read_csv("news_clean.csv")
    df["scraped_at"] = pd.to_datetime(df["scraped_at"])
    return df

df = load_data()


#score any text
def score_headline(text):
    polarity = TextBlob(str(text)).sentiment.polarity
    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"
    return polarity, label

#  HEADER
st.title("Kenya News Sentiment Tracker")
st.markdown("**Scraped from StandardMedia.co.ke · TextBlob NLP · 213 headlines**")

#  SIDEBAR FILTERS

st.sidebar.header("Filters")

all_categories = ["All"] + sorted(df["category"].unique().tolist())
selected_cat   = st.sidebar.selectbox("Category", all_categories)

all_sentiments = ["All", "Positive", "Neutral", "Negative"]
selected_sent  = st.sidebar.selectbox("Sentiment", all_sentiments)

filtered = df.copy()
if selected_cat != "All":
    filtered = filtered[filtered["category"] == selected_cat]
if selected_sent != "All":
    filtered = filtered[filtered["sentiment"] == selected_sent]

st.sidebar.markdown(f"**Showing {len(filtered)} of {len(df)} headlines**")

#  TOP METRICS

col1, col2, col3, col4 = st.columns(4)

positive_pct  = (df["sentiment"] == "Positive").mean() * 100
negative_pct  = (df["sentiment"] == "Negative").mean() * 100
mean_polarity = df["polarity"].mean()

with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{len(df)}</div>
        <div class="metric-label">Total Headlines</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="color:#2E7D32">{positive_pct:.0f}%</div>
        <div class="metric-label">Positive</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="color:#C62828">{negative_pct:.0f}%</div>
        <div class="metric-label">Negative</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{mean_polarity:.3f}</div>
        <div class="metric-label">Mean Polarity</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

#  MAIN LAYOUT

left, right = st.columns([1, 2], gap="large")


#Live Scorer + Top Headlines
with left:
    st.subheader(" Live Headline Scorer")
    st.markdown("Type any headline to instantly score its sentiment.")

    user_input = st.text_area("Enter a headline:",
                              placeholder="e.g. Kenya economy grows 5% in Q1...",
                              height=100)

    if user_input.strip():
        polarity, label = score_headline(user_input)
        subjectivity    = TextBlob(user_input).sentiment.subjectivity
        color = {"Positive": "#2E7D32", "Negative": "#C62828", "Neutral": "#F9A825"}[label]
    

        st.markdown(f"""
        <div style="background:{color}18; border-left:4px solid {color};
                    border-radius:8px; padding:16px; margin-top:10px;">
            <div style="font-size:22px; font-weight:bold; color:{color}">
                {emoji} {label}
            </div>
            <div style="margin-top:8px; color:#444; font-size:14px">
                Polarity     : <b>{polarity:.3f}</b><br>
                Subjectivity : <b>{subjectivity:.3f}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Most Negative")
    for _, row in df.nsmallest(5, "polarity").iterrows():
        st.markdown(f"**[{row['category']}]** {row['headline'][:75]}  \n"
                    f"<span style='color:#C62828; font-size:12px'>Score: {row['polarity']:.3f}</span>",
                    unsafe_allow_html=True)
        st.markdown("---")

    st.subheader("Most Positive")
    for _, row in df.nlargest(5, "polarity").iterrows():
        st.markdown(f"**[{row['category']}]** {row['headline'][:75]}  \n"
                    f"<span style='color:#2E7D32; font-size:12px'>Score: {row['polarity']:.3f}</span>",
                    unsafe_allow_html=True)
        st.markdown("---")


#Charts
with right:
    st.subheader("Analysis")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview", "By Category", "Word Clouds", "Headlines Table"
    ])

    # TAB 1: Overview
    with tab1:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))

        counts = df["sentiment"].value_counts()
        colors = [{"Positive":"#2E7D32","Neutral":"#F9A825","Negative":"#C62828"}[s]
                  for s in counts.index]
        axes[0].bar(counts.index, counts.values, color=colors, edgecolor="white")
        axes[0].set_title("Sentiment Distribution")
        axes[0].set_ylabel("Headlines")
        for i, v in enumerate(counts.values):
            axes[0].text(i, v + 0.5, str(v), ha="center", fontweight="bold")

        axes[1].hist(df["polarity"], bins=25, color="steelblue", edgecolor="white")
        axes[1].axvline(0, color="black", linestyle="--", linewidth=1, label="Neutral (0)")
        axes[1].axvline(df["polarity"].mean(), color="red", linestyle="--",
                        linewidth=1.5, label=f"Mean ({df['polarity'].mean():.3f})")
        axes[1].set_title("Polarity Distribution")
        axes[1].set_xlabel("Polarity Score")
        axes[1].set_ylabel("Count")
        axes[1].legend()

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # TAB 2: By Category
    with tab2:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))

        cat_pol   = df.groupby("category")["polarity"].mean().sort_values()
        bar_colors = ["#C62828" if v < 0 else "#2E7D32" for v in cat_pol.values]
        axes[0].barh(cat_pol.index, cat_pol.values, color=bar_colors)
        axes[0].axvline(0, color="black", linestyle="--", linewidth=0.8)
        axes[0].set_title("Mean Polarity by Category")
        axes[0].set_xlabel("Mean Polarity")
        for i, v in enumerate(cat_pol.values):
            axes[0].text(v + 0.001 if v >= 0 else v - 0.001, i,
                         f"{v:.3f}", va="center",
                         ha="left" if v >= 0 else "right", fontsize=8)

        cat_sent = df.groupby(["category","sentiment"]).size().unstack(fill_value=0)
        for col in ["Positive","Neutral","Negative"]:
            if col not in cat_sent.columns:
                cat_sent[col] = 0
        cat_sent[["Positive","Neutral","Negative"]].plot(
            kind="bar", ax=axes[1],
            color=["#2E7D32","#F9A825","#C62828"], edgecolor="white"
        )
        axes[1].set_title("Sentiment by Category")
        axes[1].set_ylabel("Headlines")
        axes[1].set_xlabel("")
        axes[1].tick_params(axis="x", rotation=30)
        axes[1].legend(title="Sentiment")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        most_neg = df.groupby("category")["polarity"].mean().idxmin()
        most_pos = df.groupby("category")["polarity"].mean().idxmax()
        st.info(f" Most negative: **{most_neg}** | Most positive: **{most_pos}**")

    # TAB 3: Word Clouds
    with tab3:
        fig, axes = plt.subplots(1, 3, figsize=(14, 4))
        fig.suptitle("Common Words by Sentiment", fontsize=13, fontweight="bold")

        for ax, sentiment, cmap in zip(
            axes,
            ["Positive", "Neutral", "Negative"],
            ["Greens",   "Blues",   "Reds"]
        ):
            text = " ".join(df[df["sentiment"] == sentiment]["headline_clean"].tolist())
            if text.strip():
                wc = WordCloud(width=400, height=250, background_color="white",
                               colormap=cmap, max_words=40).generate(text)
                ax.imshow(wc, interpolation="bilinear")
            count = (df["sentiment"] == sentiment).sum()
            ax.set_title(f"{sentiment} ({count})", fontweight="bold")
            ax.axis("off")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # TAB 4: Headlines Table
    with tab4:
        st.markdown(f"**{len(filtered)} headlines**")

        def highlight_sentiment(val):
            colors = {"Positive":"#c8e6c9","Negative":"#ffcdd2","Neutral":"#fff9c4"}
            return f"background-color: {colors.get(val, 'white')}"

        display = filtered[["headline","category","polarity","sentiment"]].copy()
        styled  = (display.style
                   .map(highlight_sentiment, subset=["sentiment"])
                   .format({"polarity": "{:.3f}"}))
        st.dataframe(styled, width='stretch', height=400)

#  FOOTER
st.markdown(
    "**Data:** Scraped from [StandardMedia.co.ke](https://www.standardmedia.co.ke) · "
    "**NLP:** TextBlob · "
    "**Built by:** Simon · "
    "**GitHub:** [symo101](https://github.com/symo101)"
)
