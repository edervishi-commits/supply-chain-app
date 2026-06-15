import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="AI-Driven Supply Chain Planning & Control System",
    page_icon="📦",
    layout="wide"
)

# =============================
# STYLE
# =============================
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

[data-testid="stSidebar"] * {
    color: white;
}

.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 60%, #38bdf8 100%);
    padding: 32px;
    border-radius: 24px;
    color: white;
    margin-bottom: 26px;
    box-shadow: 0 16px 35px rgba(15, 23, 42, 0.25);
}

.hero h1 {
    font-size: 40px;
    margin-bottom: 8px;
}

.hero p {
    font-size: 16px;
    color: #e0f2fe;
    margin-bottom: 0;
}

.section-title {
    font-size: 26px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 14px;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

div[data-testid="stMetricValue"] {
    color: #0f172a;
    font-weight: 800;
}

.info-box {
    background: #eff6ff;
    color: #1e3a8a;
    padding: 16px;
    border-radius: 16px;
    border-left: 6px solid #2563eb;
    margin-bottom: 18px;
}

.good-box {
    background: #dcfce7;
    color: #166534;
    padding: 14px;
    border-radius: 14px;
    border-left: 6px solid #16a34a;
    margin-bottom: 10px;
}

.bad-box {
    background: #fee2e2;
    color: #991b1b;
    padding: 14px;
    border-radius: 14px;
    border-left: 6px solid #dc2626;
    margin-bottom: 10px;
}

.warn-box {
    background: #fef3c7;
    color: #92400e;
    padding: 14px;
    border-radius: 14px;
    border-left: 6px solid #f59e0b;
    margin-bottom: 10px;
}

.stButton > button {
    border-radius: 12px;
    background: #2563eb;
    color: white;
    border: none;
    font-weight: 700;
    padding: 0.55rem 1rem;
}

.stButton > button:hover {
    background: #1d4ed8;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =============================
# DEFAULT DATA
# =============================
Z = 1.65

def default_products():
    return pd.DataFrame({
        "Product": ["Smart Light", "Smart Plug", "Security Cam", "Smart Thermostat", "Door Sensor", "Smart Speaker", "Smart Lock"],
        "Category": ["Lighting", "Energy", "Security", "Climate", "Security", "Audio", "Security"],
        "Supplier": ["Alpha Electronics", "Beta Components", "Gamma Tech", "Delta Logistics", "Omega Devices", "Alpha Electronics", "Gamma Tech"],
        "Annual Demand": [1200, 1800, 600, 900, 1500, 1100, 750],
        "Current Stock": [50, 20, 10, 120, 75, 160, 35],
        "Ordering Cost": [50, 45, 60, 55, 40, 48, 62],
        "Holding Cost": [2.0, 1.8, 3.0, 2.5, 1.5, 2.2, 3.4],
        "Lead Time": [5, 7, 10, 6, 4, 8, 9],
        "Demand SD": [4, 6, 3, 5, 7, 5, 4],
        "Unit Cost": [18, 12, 45, 60, 10, 35, 70],
        "Orders": [100, 140, 60, 80, 120, 95, 70],
        "Orders Fulfilled": [96, 130, 55, 78, 114, 90, 64],
        "Stockouts": [2, 5, 4, 1, 3, 2, 4],
        "Growth %": [8, 12, 5, 10, 7, 9, 6]
    })

def default_suppliers():
    return pd.DataFrame({
        "Supplier": ["Alpha Electronics", "Beta Components", "Gamma Tech", "Delta Logistics", "Omega Devices"],
        "Region": ["EU", "Asia", "EU", "Greece", "Asia"],
        "On-Time Delivery %": [92, 81, 74, 88, 90],
        "Quality %": [95, 88, 80, 90, 92],
        "Cost Score %": [85, 91, 76, 84, 87],
        "Risk Score %": [18, 32, 45, 24, 20]
    })

def default_kpi_targets():
    return pd.DataFrame({
        "KPI": ["Service Level %", "Stockout Rate %", "Supplier Score %", "Inventory Turnover"],
        "Target": [95, 2, 90, 10]
    })

if "products" not in st.session_state:
    st.session_state.products = default_products()

if "suppliers" not in st.session_state:
    st.session_state.suppliers = default_suppliers()

if "kpi_targets" not in st.session_state:
    st.session_state.kpi_targets = default_kpi_targets()

# =============================
# CALCULATIONS
# =============================
def calculate_products(df):
    df = df.copy()

    required_cols = [
        "Product", "Category", "Supplier", "Annual Demand", "Current Stock", "Ordering Cost",
        "Holding Cost", "Lead Time", "Demand SD", "Unit Cost", "Orders",
        "Orders Fulfilled", "Stockouts", "Growth %"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = "" if col in ["Product", "Category", "Supplier"] else 0

    numeric_cols = [
        "Annual Demand", "Current Stock", "Ordering Cost", "Holding Cost",
        "Lead Time", "Demand SD", "Unit Cost", "Orders", "Orders Fulfilled",
        "Stockouts", "Growth %"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Daily Demand"] = (df["Annual Demand"] / 300).round(2)

    df["EOQ"] = np.where(
        df["Holding Cost"] > 0,
        np.sqrt((2 * df["Annual Demand"] * df["Ordering Cost"]) / df["Holding Cost"]),
        0
    ).round(0)

    df["Safety Stock"] = (Z * df["Demand SD"] * np.sqrt(df["Lead Time"])).round(0)
    df["Reorder Point"] = (df["Daily Demand"] * df["Lead Time"] + df["Safety Stock"]).round(0)
    df["Inventory Value"] = (df["Current Stock"] * df["Unit Cost"]).round(2)

    df["Service Level %"] = np.where(
        df["Orders"] > 0,
        (df["Orders Fulfilled"] / df["Orders"]) * 100,
        0
    ).round(1)

    df["Stockout Rate %"] = np.where(
        df["Orders"] > 0,
        (df["Stockouts"] / df["Orders"]) * 100,
        0
    ).round(1)

    df["Inventory Turnover"] = np.where(
        df["Current Stock"] > 0,
        df["Annual Demand"] / df["Current Stock"],
        0
    ).round(2)

    df["Monthly Forecast"] = (df["Annual Demand"] / 12).round(0)
    df["Next Year Forecast"] = (df["Annual Demand"] * (1 + df["Growth %"] / 100)).round(0)

    df["Annual Usage Value"] = (df["Annual Demand"] * df["Unit Cost"]).round(2)

    df["Annual Ordering Cost"] = np.where(
        df["EOQ"] > 0,
        (df["Annual Demand"] / df["EOQ"]) * df["Ordering Cost"],
        0
    ).round(2)

    df["Annual Holding Cost"] = ((df["EOQ"] / 2) * df["Holding Cost"]).round(2)
    df["Total Inventory Cost"] = (df["Annual Ordering Cost"] + df["Annual Holding Cost"]).round(2)

    df["Decision"] = np.where(
        df["Current Stock"] <= df["Reorder Point"],
        "Reorder Required",
        "Healthy"
    )

    df["Order Status"] = np.where(
        df["Current Stock"] <= df["Reorder Point"],
        "Create Purchase Order",
        "No Order Required"
    )

    df["Recommended Order Qty"] = np.where(
        df["Current Stock"] <= df["Reorder Point"],
        df["EOQ"],
        0
    )

    total_usage = df["Annual Usage Value"].sum()
    df = df.sort_values("Annual Usage Value", ascending=False).reset_index(drop=True)
    df["Cumulative Value %"] = np.where(
        total_usage > 0,
        (df["Annual Usage Value"].cumsum() / total_usage) * 100,
        0
    ).round(1)

    df["ABC Class"] = np.select(
        [
            df["Cumulative Value %"] <= 80,
            df["Cumulative Value %"] <= 95
        ],
        ["A", "B"],
        default="C"
    )

    return df

def calculate_suppliers(df):
    df = df.copy()

    required_cols = ["Supplier", "Region", "On-Time Delivery %", "Quality %", "Cost Score %", "Risk Score %"]

    for col in required_cols:
        if col not in df.columns:
            df[col] = "" if col in ["Supplier", "Region"] else 0

    for col in ["On-Time Delivery %", "Quality %", "Cost Score %", "Risk Score %"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Supplier Score %"] = (
        df["On-Time Delivery %"] * 0.35 +
        df["Quality %"] * 0.35 +
        df["Cost Score %"] * 0.20 +
        (100 - df["Risk Score %"]) * 0.10
    ).round(1)

    df["Risk Level"] = np.where(
        df["Risk Score %"] >= 40,
        "High Risk",
        np.where(df["Risk Score %"] >= 25, "Medium Risk", "Low Risk")
    )

    df["Status"] = np.where(
        df["Supplier Score %"] >= 85,
        "Preferred",
        np.where(df["Supplier Score %"] >= 75, "Monitor", "Review")
    )

    return df

products = calculate_products(st.session_state.products)
suppliers = calculate_suppliers(st.session_state.suppliers)

# =============================
# HEADER
# =============================
st.markdown("""
<div class="hero">
    <h1>📦 AI-Driven Supply Chain Planning & Control System</h1>
    <p>Enterprise-style application for an online smart-home retailer, integrating forecasting, inventory planning, order management, supplier management, KPIs and AI-supported decision logic.</p>
</div>
""", unsafe_allow_html=True)

# =============================
# SIDEBAR
# =============================
page = st.sidebar.radio(
    "Control Tower",
    [
        "🏠 Executive Dashboard",
        "📘 How to Use This App",
        "🧾 Product Management",
        "📋 Order Management",
        "📈 Forecast Planning",
        "📦 Inventory Control",
        "🏷️ ABC Analysis",
        "💰 Cost Analysis",
        "🚚 Supplier Management",
        "🎯 KPI Targets",
        "🧪 Scenario Planning",
        "✅ Action Centre",
        "🤖 Generative AI Use",
        "⚠️ Limitations",
        "ℹ️ Assumptions",
        "📤 Export"
    ]
)

# =============================
# PAGES
# =============================
if page == "🏠 Executive Dashboard":
    st.markdown('<div class="section-title">Executive KPI Dashboard</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Products", len(products))
    c2.metric("Inventory Value", f"€{products['Inventory Value'].sum():,.0f}")
    c3.metric("Reorder Alerts", len(products[products["Decision"] == "Reorder Required"]))
    c4.metric("Supplier Score", f"{suppliers['Supplier Score %'].mean():.1f}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Service Level", f"{products['Service Level %'].mean():.1f}%")
    c6.metric("Stockout Rate", f"{products['Stockout Rate %'].mean():.1f}%")
    c7.metric("Inventory Turnover", f"{products['Inventory Turnover'].mean():.2f}")
    c8.metric("Open Purchase Orders", len(products[products["Order Status"] == "Create Purchase Order"]))

    st.markdown("""
    <div class="info-box">
    <b>Business Context:</b> SmartHome Solutions is a simulated online retailer of smart-home products.
    The application supports managers by combining forecasting, inventory planning, supplier performance,
    order recommendations and KPI-based decision support.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <b>Executive workflow:</b> Review KPI dashboard → analyse forecasts → check inventory status →
    review supplier performance → create purchase order recommendation → export KPI evidence for the report.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Inventory Control Summary")
    summary = products[["Product", "Category", "Supplier", "Current Stock", "EOQ", "Safety Stock", "Reorder Point", "Inventory Value", "Decision"]]
    st.dataframe(summary, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Stock Levels")
        st.bar_chart(products.set_index("Product")["Current Stock"])
    with col2:
        st.markdown("### EOQ Recommendations")
        st.bar_chart(products.set_index("Product")["EOQ"])

elif page == "📘 How to Use This App":
    st.markdown('<div class="section-title">How to Use This App</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    This application is designed as a managerial decision-support prototype for an online smart-home retailer.
    It follows a clear supply chain planning workflow.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### Recommended Manager Workflow

    1. **Executive Dashboard**  
       Review the main KPIs, inventory value, reorder alerts, supplier score and service level.

    2. **Forecast Planning**  
       Check monthly and next-year demand forecasts based on annual demand and growth assumptions.

    3. **Inventory Control**  
       Review EOQ, safety stock and reorder point calculations for each product.

    4. **Supplier Management**  
       Evaluate supplier performance using delivery, quality, cost and risk scores.

    5. **Order Management**  
       Convert inventory alerts into purchase order recommendations.

    6. **Action Centre**  
       Review automated recommendations and management actions.

    7. **Export**  
       Download KPI data for appendix evidence and reporting.
    """)

    st.success("The purpose of the application is not only to display data, but to support planning and control decisions.")

elif page == "🧾 Product Management":
    st.markdown('<div class="section-title">Product Management</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    Edit all product fields directly in the table. You can add new products, delete rows, change demand, supplier, costs, stock, lead time and growth assumptions.
    Press <b>Save Product Database</b> after editing.
    </div>
    """, unsafe_allow_html=True)

    edited_products = st.data_editor(
        st.session_state.products,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="product_editor"
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save Product Database"):
            st.session_state.products = edited_products
            st.success("Product database saved successfully. All KPIs have been recalculated.")
            st.rerun()

    with c2:
        if st.button("Reset Product Database"):
            st.session_state.products = default_products()
            st.rerun()

elif page == "📋 Order Management":
    st.markdown('<div class="section-title">Order Management & Purchase Order Recommendations</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    This module converts inventory alerts into purchase order recommendations. 
    Rule: <b>If Current Stock ≤ Reorder Point, create purchase order using EOQ quantity.</b>
    </div>
    """, unsafe_allow_html=True)

    orders = products[[
        "Product", "Supplier", "Current Stock", "Reorder Point", "EOQ",
        "Recommended Order Qty", "Order Status"
    ]]

    st.dataframe(orders, use_container_width=True, hide_index=True)

    open_orders = orders[orders["Order Status"] == "Create Purchase Order"]

    st.markdown("### Purchase Order Recommendations")
    if open_orders.empty:
        st.markdown('<div class="good-box">No purchase orders are currently required.</div>', unsafe_allow_html=True)
    else:
        for _, row in open_orders.iterrows():
            st.markdown(
                f"""
                <div class="bad-box">
                <b>{row['Product']}</b> from <b>{row['Supplier']}</b>: Create purchase order for 
                <b>{row['Recommended Order Qty']}</b> units because current stock 
                ({row['Current Stock']}) is at or below reorder point ({row['Reorder Point']}).
                </div>
                """,
                unsafe_allow_html=True
            )

elif page == "📈 Forecast Planning":
    st.markdown('<div class="section-title">Forecast Planning</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    Forecasts are calculated from annual demand and expected growth. Change the Growth % field in Product Management to update future demand.
    </div>
    """, unsafe_allow_html=True)

    forecast = products[["Product", "Category", "Annual Demand", "Growth %", "Monthly Forecast", "Next Year Forecast"]]
    st.dataframe(forecast, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Monthly Forecast")
        st.bar_chart(forecast.set_index("Product")["Monthly Forecast"])
    with col2:
        st.markdown("### Next Year Forecast")
        st.bar_chart(forecast.set_index("Product")["Next Year Forecast"])

elif page == "📦 Inventory Control":
    st.markdown('<div class="section-title">Inventory Control</div>', unsafe_allow_html=True)

    st.latex(r"EOQ=\sqrt{\frac{2DS}{H}}")
    st.latex(r"Safety\ Stock=Z \times \sigma_d \times \sqrt{LT}")
    st.latex(r"ROP=Daily\ Demand \times Lead\ Time + Safety\ Stock")

    inv = products[[
        "Product", "Current Stock", "Annual Demand", "EOQ", "Safety Stock",
        "Reorder Point", "Inventory Value", "Decision"
    ]]
    st.dataframe(inv, use_container_width=True, hide_index=True)

    st.markdown("### Operational Alerts")
    alerts = products[products["Decision"] == "Reorder Required"]

    if alerts.empty:
        st.markdown('<div class="good-box">All products are currently within safe inventory levels.</div>', unsafe_allow_html=True)
    else:
        for _, row in alerts.iterrows():
            st.markdown(
                f"""
                <div class="bad-box">
                <b>{row['Product']}</b>: Current stock is {row['Current Stock']} units.
                Reorder point is {row['Reorder Point']} units.
                Recommended EOQ order: <b>{row['EOQ']}</b> units.
                </div>
                """,
                unsafe_allow_html=True
            )

elif page == "🏷️ ABC Analysis":
    st.markdown('<div class="section-title">ABC Inventory Analysis</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    ABC analysis classifies products based on annual usage value: Annual Demand × Unit Cost.
    A-items represent the highest value inventory and require closer managerial control.
    </div>
    """, unsafe_allow_html=True)

    abc = products[[
        "Product", "Category", "Annual Demand", "Unit Cost", "Annual Usage Value",
        "Cumulative Value %", "ABC Class"
    ]]

    st.dataframe(abc, use_container_width=True, hide_index=True)
    st.bar_chart(abc.set_index("Product")["Annual Usage Value"])

elif page == "💰 Cost Analysis":
    st.markdown('<div class="section-title">Inventory Cost Analysis</div>', unsafe_allow_html=True)

    cost = products[[
        "Product", "Annual Ordering Cost", "Annual Holding Cost", "Total Inventory Cost"
    ]]

    st.dataframe(cost, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Total Inventory Cost")
        st.bar_chart(cost.set_index("Product")["Total Inventory Cost"])
    with col2:
        st.markdown("### Ordering vs Holding Cost")
        st.bar_chart(cost.set_index("Product")[["Annual Ordering Cost", "Annual Holding Cost"]])

elif page == "🚚 Supplier Management":
    st.markdown('<div class="section-title">Supplier Management</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    Edit supplier performance directly. Supplier score is recalculated using delivery, quality, cost and risk performance.
    </div>
    """, unsafe_allow_html=True)

    edited_suppliers = st.data_editor(
        st.session_state.suppliers,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="supplier_editor"
    )

    if st.button("Save Supplier Database"):
        st.session_state.suppliers = edited_suppliers
        st.success("Supplier database saved successfully.")
        st.rerun()

    suppliers = calculate_suppliers(st.session_state.suppliers)

    st.markdown("### Supplier Scorecard")
    st.dataframe(suppliers, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Supplier Score")
        st.bar_chart(suppliers.set_index("Supplier")["Supplier Score %"])
    with col2:
        st.markdown("### Supplier Risk")
        st.bar_chart(suppliers.set_index("Supplier")["Risk Score %"])

elif page == "🎯 KPI Targets":
    st.markdown('<div class="section-title">KPI Targets & Performance Gap</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    This page compares current KPI performance against target levels to support management evaluation.
    </div>
    """, unsafe_allow_html=True)

    current = pd.DataFrame({
        "KPI": ["Service Level %", "Stockout Rate %", "Supplier Score %", "Inventory Turnover"],
        "Current": [
            products["Service Level %"].mean().round(1),
            products["Stockout Rate %"].mean().round(1),
            suppliers["Supplier Score %"].mean().round(1),
            products["Inventory Turnover"].mean().round(2)
        ]
    })

    targets = st.session_state.kpi_targets.copy()
    targets["Target"] = pd.to_numeric(targets["Target"], errors="coerce").fillna(0)

    kpi_compare = current.merge(targets, on="KPI", how="left")
    kpi_compare["Gap"] = (kpi_compare["Current"] - kpi_compare["Target"]).round(2)

    st.dataframe(kpi_compare, use_container_width=True, hide_index=True)

    st.markdown("### Edit KPI Targets")
    edited_targets = st.data_editor(
        st.session_state.kpi_targets,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="target_editor"
    )

    if st.button("Save KPI Targets"):
        st.session_state.kpi_targets = edited_targets
        st.success("KPI targets saved.")
        st.rerun()

elif page == "🧪 Scenario Planning":
    st.markdown('<div class="section-title">Scenario Planning</div>', unsafe_allow_html=True)

    product = st.selectbox("Select product", products["Product"])
    demand_change = st.slider("Demand Change %", -50, 100, 20)
    lead_change = st.slider("Lead Time Increase", 0, 20, 5)
    holding_change = st.slider("Holding Cost Change %", -50, 100, 0)

    row = products[products["Product"] == product].iloc[0]

    new_demand = row["Annual Demand"] * (1 + demand_change / 100)
    new_lead = row["Lead Time"] + lead_change
    new_holding = row["Holding Cost"] * (1 + holding_change / 100)

    new_eoq = np.sqrt((2 * new_demand * row["Ordering Cost"]) / new_holding) if new_holding > 0 else 0
    new_ss = Z * row["Demand SD"] * np.sqrt(new_lead)
    new_rop = (new_demand / 300) * new_lead + new_ss

    c1, c2, c3 = st.columns(3)
    c1.metric("New EOQ", f"{new_eoq:.0f}")
    c2.metric("New Safety Stock", f"{new_ss:.0f}")
    c3.metric("New Reorder Point", f"{new_rop:.0f}")

    st.markdown("""
    <div class="warn-box">
    Scenario planning shows how changes in demand, lead time and holding cost affect inventory decisions.
    </div>
    """, unsafe_allow_html=True)

elif page == "✅ Action Centre":
    st.markdown('<div class="section-title">Action Centre</div>', unsafe_allow_html=True)

    for _, row in products.iterrows():
        if row["Current Stock"] <= row["Reorder Point"]:
            st.markdown(
                f"""
                <div class="bad-box">
                <b>{row['Product']}</b>: Stock is below reorder point.
                Recommended action: place an EOQ order of <b>{row['EOQ']}</b> units.
                </div>
                """,
                unsafe_allow_html=True
            )
        elif row["Inventory Turnover"] < 5:
            st.markdown(
                f"""
                <div class="warn-box">
                <b>{row['Product']}</b>: Inventory turnover is low.
                Recommended action: review demand forecast and stock policy.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="good-box">
                <b>{row['Product']}</b>: Inventory position is healthy.
                </div>
                """,
                unsafe_allow_html=True
            )

elif page == "🤖 Generative AI Use":
    st.markdown('<div class="section-title">Use of Generative Artificial Intelligence</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    This prototype was developed with the assistance of Generative AI as permitted by the assessment handout.
    GenAI was used as a support tool for application structure, dashboard design, coding logic and documentation.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### How Generative AI Supported Development

    - Generated the initial Streamlit application structure.
    - Helped design the dashboard layout and navigation flow.
    - Supported the coding of EOQ, safety stock and reorder point calculations.
    - Assisted in creating KPI cards, alerts and purchase order recommendations.
    - Helped improve the user interface and decision-support workflow.
    - Supported documentation wording for the report.

    ### Human Validation

    The final application logic was reviewed and adapted to align with supply chain planning and control concepts.
    The student is responsible for explaining the application, validating the calculations and critically reflecting on
    the limitations of AI-supported development.
    """)

elif page == "⚠️ Limitations":
    st.markdown('<div class="section-title">Limitations</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="warn-box">
    This application is a functional academic prototype. It is designed to demonstrate supply chain planning logic,
    not to operate as a production-ready enterprise system.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### Main Limitations

    - The data is simulated/mock data and does not represent real company transactions.
    - Forecasting is simplified and based on annual demand and growth assumptions.
    - Supplier scores are illustrative and not based on live supplier performance data.
    - The app is not connected to ERP, Shopify, warehouse or accounting systems.
    - Purchase orders are recommendations only; they are not sent automatically to suppliers.
    - The model does not include seasonality, promotions, transport disruption or real-time demand shocks.
    - Security, user permissions and database persistence would need improvement for real business use.

    ### Future Improvements

    - Connect the app to real sales, inventory and supplier data.
    - Add demand seasonality and forecast accuracy tracking.
    - Add user login and management approval workflows.
    - Integrate with ERP or e-commerce platforms.
    - Add automated purchase order generation and supplier email notifications.
    """)

elif page == "ℹ️ Assumptions":
    st.markdown('<div class="section-title">Assumptions & Academic Notes</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <b>Data assumption:</b> The application uses simulated/mock data for academic demonstration purposes.
    The data represents a hypothetical company, SmartHome Solutions.
    </div>
    """, unsafe_allow_html=True)

    st.write("""
    The system combines forecasting, inventory planning, EOQ, reorder point logic, safety stock, supplier scorecards,
    ABC analysis, inventory cost analysis and KPI targets. The purpose is to support managerial decision-making
    in a supply chain planning and control context.
    """)

    st.write("""
    Generative AI can be referenced in the accompanying report as a tool used to support application design,
    structure, coding logic, dashboard layout and documentation. The student remains responsible for explaining,
    validating and presenting the final application.
    """)

elif page == "📤 Export":
    st.markdown('<div class="section-title">Export Centre</div>', unsafe_allow_html=True)

    products_csv = products.to_csv(index=False).encode("utf-8")
    suppliers_csv = suppliers.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Product KPI Data",
        products_csv,
        "product_kpi_data.csv",
        "text/csv"
    )

    st.download_button(
        "Download Supplier Scorecard",
        suppliers_csv,
        "supplier_scorecard.csv",
        "text/csv"
    )

    st.info("Use these files as appendix evidence for the assignment.")
