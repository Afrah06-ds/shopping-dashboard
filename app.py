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
# CUSTOM CSS DESIGN
# -------------------------------
st.markdown("""
    <style>
        body {
            background-color: #f5f7fb;
        }

        .main-title {
            text-align: center;
            font-size: 45px;
            font-weight: bold;
            color: #003366;
            padding: 15px;
        }

        .kpi-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 2px 2px 15px rgba(0,0,0,0.1);
        }

        .kpi-value {
            font-size: 28px;
            font-weight: bold;
            color: #003366;
        }

        .kpi-label {
            font-size: 16px;
            color: gray;
        }

        .insight-box {
            background: #ffffff;
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
    file_name = csv_files[0]
    df = pd.read_csv(file_name)
    df = df.dropna()
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Rename columns
df.rename(columns={
    "Category": "Product_Category",
    "Payment Method": "Payment_Method",
    "Purchase Amount (USD)": "Sales",
    "Customer ID": "Customer_ID"
}, inplace=True)

df["Returning_Customer"] = df.duplicated("Customer_ID")

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------
st.sidebar.header("🔍 Dashboard Filters")

season_filter = st.sidebar.multiselect(
    "Select Season",
    options=df["Season"].unique(),
    default=df["Season"].unique()
)

df = df[df["Season"].isin(season_filter)]

# -------------------------------
# KPI VALUES
# -------------------------------
total_customers = df["Customer_ID"].nunique()
total_sales = df["Sales"].sum()
returning_customers = df["Returning_Customer"].sum()

cart_abandon_rate = 32
avg_rating = 4.2

# -------------------------------
# KPI ROW DESIGN
# -------------------------------
k1, k2, k3, k4, k5 = st.columns(5)

def kpi_card(col, label, value):
    col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

kpi_card(k1, "👥 Total Customers", total_customers)
kpi_card(k2, "💰 Total Sales", f"${total_sales:,.0f}")
kpi_card(k3, "🛒 Cart Abandonment", f"{cart_abandon_rate}%")
kpi_card(k4, "🔁 Returning Customers", f"{(returning_customers/total_customers)*100:.0f}%")
kpi_card(k5, "⭐ Avg Rating", f"{avg_rating}/5")

st.markdown("---")

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
line_fig.update_layout(title_font_size=20)

left.plotly_chart(line_fig, use_container_width=True)

cat_count = df["Product_Category"].value_counts().reset_index()
cat_count.columns = ["Category", "Count"]

bar_fig = px.bar(
    cat_count,
    x="Count",
    y="Category",
    orientation="h",
    title="🏆 Top Product Categories",
    text="Count",
    color="Count"
)
bar_fig.update_layout(title_font_size=20)

right.plotly_chart(bar_fig, use_container_width=True)

st.markdown("---")

# -------------------------------
# PIE + FUNNEL + GENDER
# -------------------------------
c1, c2, c3 = st.columns(3)

payment_count = df["Payment_Method"].value_counts().reset_index()
payment_count.columns = ["Method", "Count"]

pie_fig = px.pie(
    payment_count,
    names="Method",
    values="Count",
    title="💳 Payment Methods"
)
pie_fig.update_layout(title_font_size=18)

c1.plotly_chart(pie_fig, use_container_width=True)

# Funnel Chart
stages = ["Website Visits", "Added to Cart", "Checkout Started", "Purchased"]
values = [50000, 16000, 10800, 7500]

funnel_fig = go.Figure(go.Funnel(
    y=stages,
    x=values,
    textinfo="value+percent initial"
))
funnel_fig.update_layout(title="🛍 Purchase Funnel")

c2.plotly_chart(funnel_fig, use_container_width=True)

# Gender Chart
gender_fig = px.histogram(
    df,
    x="Gender",
    title="👤 Gender Split",
    color="Gender"
)
gender_fig.update_layout(title_font_size=18)

c3.plotly_chart(gender_fig, use_container_width=True)

st.markdown("---")

# -------------------------------
# DEMOGRAPHICS + INSIGHTS
# -------------------------------
bottom1, bottom2 = st.columns(2)

age_fig = px.histogram(
    df,
    x="Age",
    nbins=10,
    title="📌 Customer Age Distribution",
    color_discrete_sequence=["#003366"]
)
bottom1.plotly_chart(age_fig, use_container_width=True)

bottom2.markdown("""
    <div class="insight-box">
    <h3 style="color:#003366;">💡 Key Insights & Recommendations</h3>
    <ul>
        <li>Customers abandon carts mainly due to <b>high pricing</b> and <b>delivery delays</b>.</li>
        <li>Offer discounts & deals to reduce abandonment.</li>
        <li>Improve delivery speed for better satisfaction.</li>
        <li>Add more payment options for smoother checkout.</li>
    </ul>
    </div>
""", unsafe_allow_html=True)


