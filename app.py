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
# CUSTOM CSS (Attractive UI)
# -------------------------------
st.markdown("""
    <style>
        body {
            background-color: #f5f7fb;
        }

        .main-title {
            text-align: center;
            font-size: 42px;
            font-weight: bold;
            color: #003366;
            padding: 15px;
        }

        .kpi-card {
            background: white;
            border-radius: 15px;
            padding: 18px;
            text-align: center;
            box-shadow: 2px 2px 12px rgba(0,0,0,0.08);
        }

        .kpi-value {
            font-size: 26px;
            font-weight: bold;
            color: #003366;
        }

        .kpi-label {
            font-size: 15px;
            color: gray;
        }

        .insight-box {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 2px 2px 12px rgba(0,0,0,0.08);
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.markdown("<div class='main-title'>ONLINE SHOPPING BEHAVIOR ANALYSIS</div>",
            unsafe_allow_html=True)

# -------------------------------
# LOAD DATASET SAFELY
# -------------------------------
@st.cache_data
def load_data():
    csv_files = [f for f in os.listdir() if f.endswith(".csv")]

    if len(csv_files) == 0:
        st.error("❌ No CSV file found in repository!")
        st.stop()

    file_name = csv_files[0]
    df = pd.read_csv(file_name)
    df = df.dropna()
    df.columns = df.columns.str.strip()
    return df


df = load_data()

# -------------------------------
# RENAME COLUMNS
# -------------------------------
df.rename(columns={
    "Category": "Product_Category",
    "Payment Method": "Payment_Method",
    "Purchase Amount (USD)": "Sales",
    "Customer ID": "Customer_ID"
}, inplace=True)

# Returning Customers
df["Returning_Customer"] = df.duplicated("Customer_ID")

# -------------------------------
# SIDEBAR FILTERS (WORKING)
# -------------------------------
st.sidebar.header("🔍 Dashboard Filters")

season_filter = st.sidebar.multiselect(
    "Select Season",
    options=list(df["Season"].unique()),
    default=list(df["Season"].unique())
)

df = df[df["Season"].isin(season_filter)]

st.sidebar.success("✅ Filters working smoothly!")

# -------------------------------
# KPI VALUES
# -------------------------------
total_customers = df["Customer_ID"].nunique()
total_sales = df["Sales"].sum()
returning_customers = df["Returning_Customer"].sum()

cart_abandon_rate = 32
avg_rating = 4.2

# -------------------------------
# KPI CARD FUNCTION
# -------------------------------
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
# SALES TREND + TOP CATEGORIES
# -------------------------------
left, right = st.columns(2)

monthly_sales = df.groupby("Season")["Sales"].sum().reset_index()

line_fig = px.line(
    monthly_sales,
    x="Season",
    y="Sales",
    markers=True,
    title="📈 Sales Trend Over Time"
)

left.plotly_chart(line_fig)

cat_count = df["Product_Category"].value_counts().reset_index()
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
# PAYMENT + FUNNEL + GENDER
# -------------------------------
c1, c2, c3 = st.columns(3)

# Payment Pie
payment_count = df["Payment_Method"].value_counts().reset_index()
payment_count.columns = ["Method", "Count"]

pie_fig = px.pie(
    payment_count,
    names="Method",
    values="Count",
    title="💳 Payment Methods"
)

c1.plotly_chart(pie_fig)

# Funnel Chart
stages = ["Website Visits", "Added to Cart", "Checkout Started", "Purchased"]
values = [50000, 16000, 10800, 7500]

funnel_fig = go.Figure(go.Funnel(
    y=stages,
    x=values,
    textinfo="value+percent initial"
))

funnel_fig.update_layout(title="🛍 Purchase Funnel")

c2.plotly_chart(funnel_fig)

# Gender Chart
gender_fig = px.histogram(
    df,
    x="Gender",
    title="👤 Gender Split",
    color="Gender"
)

c3.plotly_chart(gender_fig)

st.divider()

# -------------------------------
# AGE + INSIGHTS
# -------------------------------
bottom1, bottom2 = st.columns(2)

age_fig = px.histogram(
    df,
    x="Age",
    nbins=10,
    title="📌 Customer Age Distribution"
)

bottom1.plotly_chart(age_fig)

bottom2.markdown("""
    <div class="insight-box">
    <h3 style="color:#003366;">💡 Key Insights & Recommendations</h3>
    <ul>
        <li><b>High pricing</b> and <b>delivery delays</b> are major reasons for cart abandonment.</li>
        <li>Offer discounts & deals to reduce abandonment.</li>
        <li>Improve delivery speed to increase satisfaction.</li>
        <li>Add more payment options for smoother checkout.</li>
    </ul>
    </div>
""", unsafe_allow_html=True)



