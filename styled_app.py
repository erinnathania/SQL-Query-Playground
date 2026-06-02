import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import streamlit as st
import sqlite3
import base64
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Board",
    page_icon="assets/logo.png", 
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>

/* ── Google Font ───────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');

/* ── Color System ──────────────────────────────────────────── */
:root {
    --bg: #f7f7f7;
    --surface: #ffffff;
    --border: #d9e7ea;

    --primary: #6ec8cd;
    --secondary: #60b0d2;
    --accent: #aee6e3;

    --text: #171616;
    --text-dim: #6b7280;

    --success: #6ec8cd;
    --error: #d96c6c;
}

/* ── Base Layout ───────────────────────────────────────────── */
.stApp {
    background: var(--bg);
    font-family: 'Open Sans', sans-serif;
    color: var(--text);
}

#MainMenu,
footer,
header {
    visibility: hidden;
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* ── Hero Header ───────────────────────────────────────────── */
.hero {
    display: flex;
    align-items: center;
    gap: 1rem;

    padding-bottom: 1.5rem;
    margin-bottom: 2rem;

    border-bottom: 1px solid var(--border);
}

.hero-logo img {
    height: 80px;
}

.hero-text h1 {
    margin: 0;

    font-family: 'Open Sans', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;

    color: var(--text);
}

.hero-text p {
    margin: 0.2rem 0 0;

    color: var(--text-dim);
    font-size: 0.95rem;
}

/* ── Section Headers ───────────────────────────────────────── */
.section-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;

    margin-bottom: 0.75rem;

    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;

    color: var(--secondary);
}

.section-label::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── File Uploader ─────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: white !important;
    border: 2px dashed var(--primary) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--secondary) !important;
}

[data-testid="stFileUploader"] label {
    color: var(--text-dim) !important;
}

/* ── Text Area ─────────────────────────────────────────────── */
textarea {
    background: white !important;

    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;

    color: var(--text) !important;
    font-family: 'Open Sans', sans-serif !important;
    font-size: 0.95rem !important;

    transition: all 0.2s ease !important;
}

textarea:focus {
    border-color: var(--secondary) !important;
    box-shadow: 0 0 0 3px rgba(96,176,210,0.15) !important;
    outline: none !important;
}

/* ── Buttons ───────────────────────────────────────────────── */
[data-testid="stButton"] > button {
    background: var(--primary) !important;
    color: white !important;

    border: none !important;
    border-radius: 12px !important;

    padding: 0.75rem 1.5rem !important;

    font-family: 'Open Sans', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;

    transition: all 0.2s ease !important;
}

[data-testid="stButton"] > button:hover {
    background: var(--secondary) !important;
    transform: translateY(-1px);
}

/* ── Dataframes ────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}

/* ── Alerts ────────────────────────────────────────────────── */
[data-testid="stSuccess"] {
    background: rgba(110,200,205,0.12) !important;
    border: 1px solid rgba(110,200,205,0.3) !important;
    border-radius: 12px !important;
}

[data-testid="stError"] {
    background: rgba(217,108,108,0.10) !important;
    border: 1px solid rgba(217,108,108,0.3) !important;
    border-radius: 12px !important;
}

[data-testid="stInfo"] {
    background: rgba(174,230,227,0.20) !important;
    border: 1px solid rgba(174,230,227,0.5) !important;
    border-radius: 12px !important;
}

/* ── Stats Chips ───────────────────────────────────────────── */
.stat-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;

    margin-bottom: 1.5rem;
}

.stat-chip {
    background: white;

    border: 1px solid var(--border);
    border-radius: 12px;

    padding: 0.65rem 1rem;

    font-size: 0.85rem;
    color: var(--text-dim);

    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

.stat-chip span {
    color: var(--secondary);
    font-weight: 700;
}

/* ── Scrollbar ─────────────────────────────────────────────── */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg);
}

::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 20px;
}

::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}

</style>
""", unsafe_allow_html=True)

# ── Helper: load logo as base64 ────────────────────────────────────────────────
def load_logo(path: str) -> str:
    """Return an <img> tag with the logo embedded as base64."""
    file = Path(path)
    if not file.exists():
        return ""
    ext = file.suffix.lower().lstrip(".")
    mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
    b64 = base64.b64encode(file.read_bytes()).decode()
    return f'<img src="data:{mime};base64,{b64}" alt="logo">'


# ── Header ────────────────────────────────────────────────────────────────────
# ↓ Change this path to your actual logo file path when you upload it
LOGO_PATH = "assets/logo.png"   

logo_html = load_logo(LOGO_PATH)
logo_block = f'<div class="hero-logo">{logo_html}</div>' if logo_html else ""

st.markdown(f"""
<div class="hero">
    {logo_block}
    <div class="hero-text">
        <h1>Data Board</h1>
        <p>Upload · Query · Visualize</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ── File Upload ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">01 &nbsp; Data Source</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drop a CSV file here or click to browse",
    type=["csv"],
    label_visibility="collapsed",
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    conn = sqlite3.connect(":memory:")
    df.to_sql("data", conn, index=False, if_exists="replace")

    # ── Stats row ──
    n_rows, n_cols = df.shape
    col_names = ", ".join(df.columns[:5]) + ("…" if n_cols > 5 else "")
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-chip">Rows &nbsp;<span>{n_rows:,}</span></div>
        <div class="stat-chip">Columns &nbsp;<span>{n_cols}</span></div>
        <div class="stat-chip">Table &nbsp;<span>data</span></div>
        <div class="stat-chip">Fields &nbsp;<span>{col_names}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Data Preview ──
    st.markdown('<div class="section-label">02 &nbsp; Preview</div>', unsafe_allow_html=True)
    st.dataframe(df.head(5), use_container_width=True)

    st.success(f"✓ `{uploaded_file.name}` loaded — query it as `data`")

    # ── SQL Editor ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">03 &nbsp; Query Editor</div>', unsafe_allow_html=True)

    query = st.text_area(
        "SQL",
        value="SELECT * FROM data LIMIT 10;",
        height=140,
        label_visibility="collapsed",
        placeholder="SELECT * FROM data LIMIT 10;",
    )

    run = st.button("▶  Run Query")

    # ── Results ───────────────────────────────────────────────────────────────
    if run:
        try:
            result_df = pd.read_sql(query, conn)

            st.markdown('<div class="section-label">04 &nbsp; Results</div>', unsafe_allow_html=True)

            r, c = result_df.shape
            st.markdown(f"""
            <div class="stat-row">
                <div class="stat-chip">Rows returned &nbsp;<span>{r:,}</span></div>
                <div class="stat-chip">Columns &nbsp;<span>{c}</span></div>
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(result_df, use_container_width=True)

            # ── Chart ────────────────────────────────────────────────────────
            numeric_cols = []
            if len(result_df.columns) >= 2:
                numeric_cols = result_df.select_dtypes(include="number").columns.tolist()

            if len(numeric_cols) >= 1:
                st.markdown('<div class="section-label">05 &nbsp; Chart</div>', unsafe_allow_html=True)

                x_col = result_df.columns[0]
                y_col = numeric_cols[0]

                # Dark matplotlib theme to match the app
                with mpl.rc_context({
                    "figure.facecolor":  "#0d1526",
                    "axes.facecolor":    "#090e1a",
                    "axes.edgecolor":    "#1a2a4a",
                    "axes.labelcolor":   "#5a7090",
                    "axes.titlecolor":   "#c8d8f0",
                    "xtick.color":       "#5a7090",
                    "ytick.color":       "#5a7090",
                    "grid.color":        "#1a2a4a",
                    "grid.linestyle":    "--",
                    "grid.alpha":        0.6,
                    "text.color":        "#c8d8f0",
                    "font.family":       "monospace",
                    "font.size":         9,
                }):
                    fig, ax = plt.subplots(figsize=(10, 4))

                    x_vals = result_df[x_col].astype(str)
                    y_vals = result_df[y_col]

                    bars = ax.bar(
                        x_vals, y_vals,
                        color="#00d4ff",
                        alpha=0.85,
                        width=0.6,
                        zorder=3,
                    )

                    # Glow effect: draw a blurred wider bar behind each bar
                    ax.bar(
                        x_vals, y_vals,
                        color="#00d4ff",
                        alpha=0.12,
                        width=0.85,
                        zorder=2,
                    )

                    # Value labels on top of bars
                    for bar in bars:
                        h = bar.get_height()
                        ax.text(
                            bar.get_x() + bar.get_width() / 2,
                            h * 1.01,
                            f"{h:,.1f}" if isinstance(h, float) else f"{h:,}",
                            ha="center", va="bottom",
                            fontsize=7.5, color="#00d4ff", alpha=0.9,
                        )

                    ax.set_title(f"{y_col}  ·  by  ·  {x_col}",
                                 fontsize=10, color="#c8d8f0", pad=14, loc="left")
                    ax.set_xlabel(x_col, labelpad=8)
                    ax.set_ylabel(y_col, labelpad=8)
                    ax.yaxis.grid(True, zorder=0)
                    ax.set_axisbelow(True)
                    ax.spines[["top", "right", "left"]].set_visible(False)
                    ax.spines["bottom"].set_color("#1a2a4a")

                    plt.xticks(rotation=40, ha="right")
                    plt.tight_layout()

                st.pyplot(fig)
                plt.close()

            else:
                st.info("No numeric columns in result — showing table only.")

        except Exception as e:
            st.error(f"SQL Error: {e}")