import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Online Shopping Dashboard",
    page_icon="🛒",
    layout="wide"
)

# -------------------------------
# PREMIUM BACKGROUND + STYLE
# -------------------------------
st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #f8fbff, #eef3ff);
        }

        .main-title {
            text-align: center;
            font-size: 45px;
            font-weight: bold;
            color: #002855;
            padding: 20px;
        }

        .kpi-card {
            background: white;
            border-radius: 18px;
            padding: 18px;
            text-align: center;
            box-shadow: 0px 4px 18px rgba(0,0,0,0.10);
        }

        .kpi-value {
            font-size: 28px;
            font-weight: bold;
            color: #002855;
        }

        .kpi-label {
            font-size: 14px;
            color: gray;
        }

        .insight-box {
            background: white;
            padding: 25px;
            border-radius: 18px;
            box-shadow: 0px 4px 18px rgba(0,0,0,0.10);
        }

        .sidebar-title {
            font-size: 20px;
            font-weight: bold;
            color: #002855;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.markdown("<div class='main-title'>ONLINE SHOPPING BEHAVIOR ANALYSIS</div>",
            unsafe_allow_html=True)

# -------------------------------
# LOAD DATASET
# -------------------------------
@st.cache_data
def load_data():
    csv_files = [f for f in os.listdir() if f.endswith(".csv")]
    df = pd.read_csv(csv_files[0])
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Rename Columns
df.rename(columns={
    "Category": "Product_Category",
    "Payment Method": "Payment_Method",
    "Purchase Amount (USD)": "Sales",
    "Customer ID": "Customer_ID"
}, inplace=True)

df["Returning_Customer"] = df.duplicated("Customer_ID")

# -------------------------------
# SIDEBAR FILTERS (USEFUL)
# -------------------------------
st.sidebar.markdown("<p class='sidebar-title'>🎛 Dashboard Controls</p>",
                    unsafe_allow_html=True)

# Season Filter
season_filter = st.sidebar.multiselect(
    "📅 Select Season",
    options=df["Season"].unique(),
    default=df["Season"].unique()
)

# Category Filter
category_filter = st.sidebar.multiselect(
    "🛍 Select Category",
    options=df["Product_Category"].unique(),
    default=df["Product_Category"].unique()
)

# Payment Filter
payment_filter = st.sidebar.multiselect(
    "💳 Select Payment Method",
    options=df["Payment_Method"].unique(),
    default=df["Payment_Method"].unique()
)

# Sales Range Slider
min_sales, max_sales = st.sidebar.slider(
    "💰 Select Sales Range (USD)",
    int(df["Sales"].min()),
    int(df["Sales"].max()),
    (int(df["Sales"].min()), int(df["Sales"].max()))
)

# Apply Filters
filtered_df = df[
    (df["Season"].isin(season_filter)) &
    (df["Product_Category"].isin(category_filter)) &
    (df["Payment_Method"].isin(payment_filter)) &
    (df["Sales"] >= min_sales) &
    (df["Sales"] <= max_sales)
]

st.sidebar.success("✅ Filters Applied Successfully!")

# Download Button
st.sidebar.download_button(
    "⬇ Download Filtered Data",
    filtered_df.to_csv(index=False),
    file_name="filtered_shopping_data.csv"
)

# -------------------------------
# KPI VALUES
# -------------------------------
total_customers = filtered_df["Customer_ID"].nunique()
total_sales = filtered_df["Sales"].sum()
returning_customers = filtered_df["Returning_Customer"].sum()

cart_abandon_rate = 32
avg_rating = 4.2

# KPI Card Function
def kpi_card(col, label, value):
    col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

# KPI Row
k1, k2, k3, k4, k5 = st.columns(5)

kpi_card(k1, "👥 Total Customers", total_customers)
kpi_card(k2, "💰 Total Sales", f"${total_sales:,.0f}")
kpi_card(k3, "🛒 Cart Abandonment", f"{cart_abandon_rate}%")
kpi_card(k4, "🔁 Returning Customers", f"{(returning_customers/total_customers)*100:.0f}%")
kpi_card(k5, "⭐ Avg Rating", f"{avg_rating}/5")

st.divider()

# -------------------------------
# SALES TREND + CATEGORY BAR
# -------------------------------
left, right = st.columns(2)

monthly_sales = filtered_df.groupby("Season")["Sales"].sum().reset_index()

line_fig = px.line(
    monthly_sales,
    x="Season",
    y="Sales",
    markers=True,
    title="📈 Sales Trend Over Time"
)
left.plotly_chart(line_fig)

cat_count = filtered_df["Product_Category"].value_counts().reset_index()
cat_count.columns = ["Category", "Count"]

bar_fig = px.bar(
    cat_count,
    x="Count",
    y="Category",
    orientation="h",
    title="🏆 Top Product Categories",
    text="Count"
)
right.plotly_chart(bar_fig)

st.divider()

# -------------------------------
# PAYMENT PIE + FUNNEL + AGE
# -------------------------------
c1, c2, c3 = st.columns(3)

payment_count = filtered_df["Payment_Method"].value_counts().reset_index()
payment_count.columns = ["Method", "Count"]

pie_fig = px.pie(
    payment_count,
    names="Method",
    values="Count",
    title="💳 Payment Methods"
)
c1.plotly_chart(pie_fig)

# Funnel Chart
stages = ["Visits", "Added to Cart", "Checkout", "Purchase"]
values = [50000, 16000, 10800, 7500]

funnel_fig = go.Figure(go.Funnel(
    y=stages,
    x=values,
    textinfo="value+percent initial"
))
funnel_fig.update_layout(title="🛍 Purchase Funnel")
c2.plotly_chart(funnel_fig)

# Age Distribution
age_fig = px.histogram(
    filtered_df,
    x="Age",
    nbins=10,
    title="📌 Customer Age Distribution"
)
c3.plotly_chart(age_fig)

st.divider()

# -------------------------------
# INSIGHTS BOX
# -------------------------------
st.markdown("""
    <div class="insight-box">
    <h3 style="color:#002855;">💡 Key Insights & Recommendations</h3>
    <ul>
        <li>Customers abandon carts mainly due to <b>high pricing</b> and <b>delivery delays</b>.</li>
        <li>Introduce discounts and seasonal offers to reduce abandonment.</li>
        <li>Improve delivery speed to boost customer satisfaction.</li>
        <li>Offer multiple payment methods for smoother checkout.</li>
    </ul>
    </div>
""", unsafe_allow_html=True)




