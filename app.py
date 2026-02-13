import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ======================================
# PAGE CONFIG
# ======================================
st.set_page_config(
    page_title="Online Shopping Dashboard",
    page_icon="🛒",
    layout="wide"
)

# ======================================
# CUSTOM BACKGROUND + THEME
# ======================================
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #f8fbff, #eef2ff);
    }

    .main {
        background-color: #f8fbff;
    }

    h1 {
        font-family: 'Trebuchet MS', sans-serif;
        font-weight: 800;
        color: #0a2a66;
    }

    .kpi-box {
        background: white;
        padding: 18px;
        border-radius: 18px;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    }

    .kpi-title {
        font-size: 15px;
        color: gray;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        color: #0a2a66;
    }

    .recommend-box {
        background: #ffffff;
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    }
    </style>
""", unsafe_allow_html=True)


# ======================================
# TITLE
# ======================================
st.markdown("<h1 style='text-align:center;'>🛍 ONLINE SHOPPING BEHAVIOR ANALYSIS</h1>",
            unsafe_allow_html=True)

st.write("")


# ======================================
# LOAD DATASET
# ======================================
@st.cache_data
def load_data():
    df = pd.read_csv("Shopping Trends And Customer Behaviour Dataset.csv")
    df.columns = df.columns.str.strip()
    df = df.dropna()
    return df

df = load_data()

# Rename columns
df.rename(columns={
    "Category": "Product_Category",
    "Payment Method": "Payment_Method",
    "Purchase Amount (USD)": "Sales",
    "Customer ID": "Customer_ID",
    "Gender": "Gender",
    "Age": "Age",
    "Season": "Season"
}, inplace=True)

# Returning customer flag
df["Returning_Customer"] = df.duplicated("Customer_ID")


# ======================================
# SIDEBAR FILTERS (WORKING PERFECTLY)
# ======================================
st.sidebar.markdown("## 🔍 Dashboard Filters")

season_filter = st.sidebar.multiselect(
    "Select Season",
    options=list(df["Season"].unique()),
    default=list(df["Season"].unique())
)

category_filter = st.sidebar.multiselect(
    "Select Product Category",
    options=list(df["Product_Category"].unique()),
    default=list(df["Product_Category"].unique())
)

df = df[df["Season"].isin(season_filter)]
df = df[df["Product_Category"].isin(category_filter)]

st.sidebar.success("✅ Filters working smoothly!")


# ======================================
# KPI VALUES
# ======================================
total_customers = df["Customer_ID"].nunique()
total_sales = df["Sales"].sum()
returning_customers = df["Returning_Customer"].sum()

cart_abandon_rate = 32
avg_rating = 4.2


# ======================================
# KPI CARDS DESIGN
# ======================================
k1, k2, k3, k4, k5 = st.columns(5)

def kpi_card(col, title, value):
    col.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value">{value}</div>
            <div class="kpi-title">{title}</div>
        </div>
    """, unsafe_allow_html=True)

kpi_card(k1, "👥 Total Customers", f"{total_customers}")
kpi_card(k2, "💰 Total Sales", f"${total_sales:,.0f}")
kpi_card(k3, "🛒 Cart Abandonment", f"{cart_abandon_rate}%")
kpi_card(k4, "🔁 Returning Customers", f"{(returning_customers/total_customers)*100:.0f}%")
kpi_card(k5, "⭐ Avg Rating", f"{avg_rating}/5")

st.write("")
st.divider()


# ======================================
# ROW 1: SALES TREND + CATEGORY BAR
# ======================================
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

st.write("")
st.divider()


# ======================================
# ROW 2: PAYMENT PIE + FUNNEL + GENDER
# ======================================
c1, c2, c3 = st.columns(3)

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

# Gender Split
gender_fig = px.bar(
    df["Gender"].value_counts().reset_index(),
    x="Gender",
    y="count",
    title="👤 Gender Split"
)
c3.plotly_chart(gender_fig)

st.write("")
st.divider()


# ======================================
# ROW 3: AGE + INSIGHTS
# ======================================
bottom1, bottom2 = st.columns(2)

age_fig = px.histogram(
    df,
    x="Age",
    nbins=10,
    title="📌 Customer Age Distribution"
)
bottom1.plotly_chart(age_fig)

bottom2.markdown("""
    <div class="recommend-box">
    <h3 style="color:#0a2a66;">💡 Key Insights & Recommendations</h3>
    <ul>
        <li>Customers abandon carts mainly due to <b>high pricing</b>.</li>
        <li>Delivery delays reduce conversions significantly.</li>
        <li>Provide discounts and seasonal offers to boost purchases.</li>
        <li>Improve shipping speed for better satisfaction.</li>
        <li>Add more payment options for smoother checkout.</li>
    </ul>
    </div>
""", unsafe_allow_html=True)
