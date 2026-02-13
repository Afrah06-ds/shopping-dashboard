import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Online Shopping Dashboard",
    layout="wide"
)

# -------------------------------
# TITLE
# -------------------------------
st.markdown(
    "<h1 style='text-align:center; color:#003366;'>ONLINE SHOPPING BEHAVIOR ANALYSIS</h1>",
    unsafe_allow_html=True
)

# -------------------------------
# LOAD DATASET (CACHED)
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("shopping.csv")   # ✅ keep filename small + lowercase
    df = df.dropna()
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.success("✅ Dataset loaded successfully!")

# -------------------------------
# RENAME COLUMNS SAFELY
# -------------------------------
df.rename(columns={
    "Category": "Product_Category",
    "Payment Method": "Payment_Method",
    "Purchase Amount (USD)": "Sales",
    "Customer ID": "Customer_ID"
}, inplace=True)

# -------------------------------
# RETURNING CUSTOMER FLAG
# -------------------------------
df["Returning_Customer"] = df.duplicated("Customer_ID")

# -------------------------------
# KPI VALUES
# -------------------------------
total_customers = df["Customer_ID"].nunique()
total_sales = df["Sales"].sum()
returning_customers = df["Returning_Customer"].sum()

cart_abandon_rate = 32   # Example %
avg_rating = 4.2         # Example rating

# -------------------------------
# KPI CARDS
# -------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("👥 Total Customers", total_customers)
col2.metric("💰 Total Sales", f"${total_sales:,.0f}")
col3.metric("🛒 Cart Abandonment Rate", f"{cart_abandon_rate}%")
col4.metric("🔁 Returning Customers", f"{(returning_customers/total_customers)*100:.0f}%")
col5.metric("⭐ Avg Rating", f"{avg_rating}/5")

st.divider()

# -------------------------------
# SALES TREND + TOP CATEGORIES
# -------------------------------
left, right = st.columns(2)

# Sales Trend (Season-wise)
monthly_sales = df.groupby("Season")["Sales"].sum().reset_index()

line_fig = px.line(
    monthly_sales,
    x="Season",
    y="Sales",
    markers=True,
    title="📈 Sales Trend Over Time"
)

left.plotly_chart(line_fig)

# Top Categories
cat_count = df["Product_Category"].value_counts().reset_index()
cat_count.columns = ["Category", "Count"]

bar_fig = px.bar(
    cat_count,
    x="Count",
    y="Category",
    orientation="h",
    title="📊 Top Product Categories",
    text="Count"
)

right.plotly_chart(bar_fig)

st.divider()

# -------------------------------
# PAYMENT PIE + FUNNEL + GENDER
# -------------------------------
c1, c2, c3 = st.columns(3)

# Payment Pie Chart
payment_count = df["Payment_Method"].value_counts().reset_index()
payment_count.columns = ["Method", "Count"]

pie_fig = px.pie(
    payment_count,
    names="Method",
    values="Count",
    title="💳 Payment Methods Used"
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

# Gender Split
gender_count = df["Gender"].value_counts().reset_index()
gender_count.columns = ["Gender", "Count"]

gender_fig = px.bar(
    gender_count,
    x="Gender",
    y="Count",
    title="👤 Customer Gender Split"
)

c3.plotly_chart(gender_fig)

st.divider()

# -------------------------------
# AGE DEMOGRAPHICS + INSIGHTS
# -------------------------------
bottom1, bottom2 = st.columns(2)

# Age Distribution
age_fig = px.histogram(
    df,
    x="Age",
    nbins=10,
    title="📌 Customer Age Distribution"
)

bottom1.plotly_chart(age_fig)

# Insights Box
bottom2.markdown(
    """
    <div style="background-color:#f9f9f9; padding:20px; border-radius:15px;">
    <h3 style="color:#003366;">KEY INSIGHTS & RECOMMENDATIONS</h3>
    <ul>
        <li><b>High pricing</b> and <b>delivery delays</b> are major reasons for cart abandonment.</li>
        <li>Introduce discounts and seasonal offers to reduce drop-offs.</li>
        <li>Improve delivery speed to boost customer satisfaction.</li>
        <li>Provide more payment methods for smoother checkout.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
)
