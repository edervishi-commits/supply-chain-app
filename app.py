import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="AI-Driven Supply Chain Planning & Control System",
    page_icon="📦",
    layout="wide"
)

# =========================================================
# DESIGN
# =========================================================
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
    font-size: 38px;
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

# =========================================================
# DEFAULT DATA
# =========================================================
def default_products():
    return pd.DataFrame({
        "Product": ["Smart Light", "Smart Plug", "Security Cam", "Smart Thermostat", "Door Sensor", "Smart Speaker", "Smart Lock"],
        "Category": ["Lighting", "Energy", "Security", "Climate", "Security", "Audio", "Security"],
        "Supplier": ["Alpha Electronics", "Beta Components", "Gamma Tech", "Delta Logistics", "Omega Devices", "Alpha Electronics", "Gamma Tech"],

        # Editable demand and forecast fields
        "Annual Demand": [1200, 1800, 600, 900, 1500, 1100, 750],
        "Actual Monthly Demand": [105, 170, 52, 82, 130, 96, 66],
        "Growth %": [8, 12, 5, 10, 7, 9, 6],

        # Editable inventory fields
        "Current Stock": [50, 20, 10, 120, 75, 160, 35],
        "Ordering Cost": [50, 45, 60, 55, 40, 48, 62],
        "Holding Cost": [2.0, 1.8, 3.0, 2.5, 1.5, 2.2, 3.4],
        "Lead Time Days": [5, 7, 10, 6, 4, 8, 9],
        "Demand SD": [4, 6, 3, 5, 7, 5, 4],
        "Unit Cost": [18, 12, 45, 60, 10, 35, 70],
        "Selling Price": [30, 22, 80, 95, 18, 55, 110],

        # Editable operational fields
        "Orders": [100, 140, 60, 80, 120, 95, 70],
        "Orders Fulfilled": [96, 130, 55, 78, 114, 90, 64],
        "Stockouts": [2, 5, 4, 1, 3, 2, 4],
        "Review Period Days": [30, 30, 30, 30, 30, 30, 30],
        "Target Service Level %": [95, 95, 95, 95, 95, 95, 95]
    })

def default_suppliers():
    return pd.DataFrame({
        "Supplier": ["Alpha Electronics", "Beta Components", "Gamma Tech", "Delta Logistics", "Omega Devices"],
        "Region": ["EU", "Asia", "EU", "Greece", "Asia"],
        "On-Time Delivery %": [92, 81, 74, 88, 90],
        "Quality %": [95, 88, 80, 90, 92],
        "Cost Score %": [85, 91, 76, 84, 87],
        "Risk Score %": [18, 32, 45, 24, 20],
        "Average Lead Time Days": [5, 8, 10, 6, 7]
    })

def default_settings():
    return {
        "working_days_per_year": 300,
        "default_z_value": 1.65,
        "forecast_horizon_value": 6,
        "forecast_horizon_unit": "Months"
    }

if "products" not in st.session_state:
    st.session_state.products = default_products()

if "suppliers" not in st.session_state:
    st.session_state.suppliers = default_suppliers()

if "settings" not in st.session_state:
    st.session_state.settings = default_settings()

if "manual_override_enabled" not in st.session_state:
    st.session_state.manual_override_enabled = False

if "manual_products" not in st.session_state:
    st.session_state.manual_products = None

# =========================================================
# CALCULATIONS
# =========================================================
def z_from_service_level(service_level):
    # Simple mapping for common service levels
    if service_level >= 99:
        return 2.33
    if service_level >= 98:
        return 2.05
    if service_level >= 97:
        return 1.88
    if service_level >= 95:
        return 1.65
    if service_level >= 90:
        return 1.28
    return 1.00

def calculate_products(df, settings):
    df = df.copy()

    required_cols = [
        "Product", "Category", "Supplier", "Annual Demand", "Actual Monthly Demand", "Growth %",
        "Current Stock", "Ordering Cost", "Holding Cost", "Lead Time Days", "Demand SD",
        "Unit Cost", "Selling Price", "Orders", "Orders Fulfilled", "Stockouts",
        "Review Period Days", "Target Service Level %"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = "" if col in ["Product", "Category", "Supplier"] else 0

    numeric_cols = [
        "Annual Demand", "Actual Monthly Demand", "Growth %", "Current Stock",
        "Ordering Cost", "Holding Cost", "Lead Time Days", "Demand SD",
        "Unit Cost", "Selling Price", "Orders", "Orders Fulfilled", "Stockouts",
        "Review Period Days", "Target Service Level %"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    working_days = settings["working_days_per_year"]
    df["Daily Demand"] = np.where(working_days > 0, df["Annual Demand"] / working_days, 0).round(2)

    df["Z Value"] = df["Target Service Level %"].apply(z_from_service_level)

    df["EOQ"] = np.where(
        df["Holding Cost"] > 0,
        np.sqrt((2 * df["Annual Demand"] * df["Ordering Cost"]) / df["Holding Cost"]),
        0
    ).round(0)

    df["Safety Stock"] = (
        df["Z Value"] * df["Demand SD"] * np.sqrt(df["Lead Time Days"])
    ).round(0)

    df["Reorder Point"] = (
        df["Daily Demand"] * df["Lead Time Days"] + df["Safety Stock"]
    ).round(0)

    df["Review Period Demand"] = (df["Daily Demand"] * df["Review Period Days"]).round(0)

    df["Order-Up-To Level"] = (
        df["Daily Demand"] * (df["Lead Time Days"] + df["Review Period Days"]) + df["Safety Stock"]
    ).round(0)

    df["Recommended Order Qty"] = np.where(
        df["Current Stock"] <= df["Reorder Point"],
        df["EOQ"],
        0
    ).round(0)

    df["Order Status"] = np.where(
        df["Current Stock"] <= df["Reorder Point"],
        "Create Purchase Order",
        "No Order Required"
    )

    df["Decision"] = np.where(
        df["Current Stock"] <= df["Reorder Point"],
        "Reorder Required",
        "Healthy"
    )

    df["Inventory Value"] = (df["Current Stock"] * df["Unit Cost"]).round(2)

    df["Annual Usage Value"] = (df["Annual Demand"] * df["Unit Cost"]).round(2)

    df["Annual Ordering Cost"] = np.where(
        df["EOQ"] > 0,
        (df["Annual Demand"] / df["EOQ"]) * df["Ordering Cost"],
        0
    ).round(2)

    df["Annual Holding Cost"] = ((df["EOQ"] / 2) * df["Holding Cost"]).round(2)
    df["Total Inventory Cost"] = (df["Annual Ordering Cost"] + df["Annual Holding Cost"]).round(2)

    df["Monthly Forecast"] = (df["Annual Demand"] / 12).round(0)
    df["Weekly Forecast"] = (df["Annual Demand"] / 52).round(0)
    df["Forecast Error"] = (df["Actual Monthly Demand"] - df["Monthly Forecast"]).round(0)

    df["Forecast Accuracy %"] = np.where(
        df["Actual Monthly Demand"] > 0,
        100 - (abs(df["Forecast Error"]) / df["Actual Monthly Demand"]) * 100,
        0
    ).round(1).clip(0, 100)

    horizon_value = settings["forecast_horizon_value"]
    horizon_unit = settings["forecast_horizon_unit"]

    if horizon_unit == "Days":
        df["Selected Horizon Forecast"] = (df["Daily Demand"] * horizon_value).round(0)
    elif horizon_unit == "Weeks":
        df["Selected Horizon Forecast"] = (df["Weekly Forecast"] * horizon_value).round(0)
    else:
        df["Selected Horizon Forecast"] = (df["Monthly Forecast"] * horizon_value).round(0)

    df["Next Year Forecast"] = (
        df["Annual Demand"] * (1 + df["Growth %"] / 100)
    ).round(0)

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

    df["Days of Cover"] = np.where(
        df["Daily Demand"] > 0,
        df["Current Stock"] / df["Daily Demand"],
        0
    ).round(1)

    df["Revenue Potential"] = (df["Annual Demand"] * df["Selling Price"]).round(2)
    df["COGS"] = (df["Annual Demand"] * df["Unit Cost"]).round(2)

    df["Gross Margin %"] = np.where(
        df["Selling Price"] > 0,
        ((df["Selling Price"] - df["Unit Cost"]) / df["Selling Price"]) * 100,
        0
    ).round(1)

    total_usage = df["Annual Usage Value"].sum()
    df = df.sort_values("Annual Usage Value", ascending=False).reset_index(drop=True)

    df["Cumulative Value %"] = np.where(
        total_usage > 0,
        (df["Annual Usage Value"].cumsum() / total_usage) * 100,
        0
    ).round(1)

    df["ABC Class"] = np.select(
        [df["Cumulative Value %"] <= 80, df["Cumulative Value %"] <= 95],
        ["A", "B"],
        default="C"
    )

    df["Suggested Action"] = np.select(
        [
            df["Current Stock"] <= df["Reorder Point"],
            df["Forecast Accuracy %"] < 75,
            df["Stockout Rate %"] > 5,
            df["Gross Margin %"] < 25
        ],
        [
            "Create purchase order",
            "Review forecast assumptions",
            "Increase safety stock",
            "Review price or supplier cost"
        ],
        default="Monitor"
    )

    return df

def calculate_suppliers(df):
    df = df.copy()

    required_cols = [
        "Supplier", "Region", "On-Time Delivery %", "Quality %",
        "Cost Score %", "Risk Score %", "Average Lead Time Days"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = "" if col in ["Supplier", "Region"] else 0

    for col in ["On-Time Delivery %", "Quality %", "Cost Score %", "Risk Score %", "Average Lead Time Days"]:
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

products = calculate_products(st.session_state.products, st.session_state.settings)
suppliers = calculate_suppliers(st.session_state.suppliers)

# Manual override mechanism:
# If enabled, the app uses the edited calculated table instead of only automatic calculations.
if st.session_state.manual_override_enabled and st.session_state.manual_products is not None:
    products = st.session_state.manual_products.copy()

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <h1>📦 AI-Driven Supply Chain Planning & Control System</h1>
    <p>Editable, automated and decision-focused supply chain prototype with EOQ, forecasting, order management, supplier performance, visual analytics and AI assistance.</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
page = st.sidebar.radio(
    "Control Tower",
    [
        "🏠 Executive Dashboard",
        "⚙️ Global Settings",
        "🧾 Product Management",
        "🛠️ Manual Override Centre",
        "🚚 Supplier Management",
        "📈 Forecast Planning",
        "📊 Forecast Accuracy",
        "📦 Inventory Control",
        "📋 Order Management",
        "🧾 Purchase Order Generator",
        "📊 Visual Analytics",
        "🏷️ ABC Analysis",
        "💰 Cost Analysis",
        "🎯 KPI Targets",
        "🧪 Scenario Planning",
        "🤖 AI Assistance",
        "✅ Action Centre",
        "ℹ️ Assumptions",
        "📤 Export"
    ]
)

# =========================================================
# PAGES
# =========================================================
if page == "🏠 Executive Dashboard":
    st.markdown('<div class="section-title">Executive KPI Dashboard</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Products", len(products))
    c2.metric("Inventory Value", f"€{products['Inventory Value'].sum():,.0f}")
    c3.metric("Reorder Alerts", len(products[products["Decision"] == "Reorder Required"]))
    c4.metric("Supplier Score", f"{suppliers['Supplier Score %'].mean():.1f}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Forecast Accuracy", f"{products['Forecast Accuracy %'].mean():.1f}%")
    c6.metric("Service Level", f"{products['Service Level %'].mean():.1f}%")
    c7.metric("Inventory Turnover", f"{products['Inventory Turnover'].mean():.2f}")
    c8.metric("Open Purchase Orders", len(products[products["Order Status"] == "Create Purchase Order"]))

    if st.session_state.manual_override_enabled:
        st.markdown("""
        <div class="warn-box">
        Manual override mode is active. Some calculated numbers may have been edited manually in Manual Override Centre.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box">
        Automatic mode is active. The app recalculates EOQ, safety stock, reorder point, forecasts, purchase orders and KPIs automatically whenever the editable input data changes.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Management Summary")
    st.dataframe(
        products[[
            "Product", "Supplier", "Current Stock", "EOQ", "Safety Stock",
            "Reorder Point", "Days of Cover", "Forecast Accuracy %",
            "Inventory Value", "Suggested Action"
        ]],
        use_container_width=True,
        hide_index=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Stock vs Reorder Point")
        st.bar_chart(products.set_index("Product")[["Current Stock", "Reorder Point"]])
    with col2:
        st.markdown("### EOQ Recommendations")
        st.bar_chart(products.set_index("Product")["EOQ"])

elif page == "⚙️ Global Settings":
    st.markdown('<div class="section-title">Global Planning Settings</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    Change these global assumptions to update the whole application. Days and months are included where they are needed for planning.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        working_days = st.number_input(
            "Working days per year",
            min_value=1,
            max_value=365,
            value=int(st.session_state.settings["working_days_per_year"]),
            step=1
        )

    with col2:
        horizon_value = st.number_input(
            "Forecast horizon value",
            min_value=1,
            max_value=60,
            value=int(st.session_state.settings["forecast_horizon_value"]),
            step=1
        )

    with col3:
        horizon_unit = st.selectbox(
            "Forecast horizon unit",
            ["Days", "Weeks", "Months"],
            index=["Days", "Weeks", "Months"].index(st.session_state.settings["forecast_horizon_unit"])
        )

    if st.button("Save Global Settings"):
        st.session_state.settings["working_days_per_year"] = working_days
        st.session_state.settings["forecast_horizon_value"] = horizon_value
        st.session_state.settings["forecast_horizon_unit"] = horizon_unit
        st.success("Global settings saved. All calculations have been updated.")
        st.rerun()

elif page == "🧾 Product Management":
    st.markdown('<div class="section-title">Product Management: Fully Editable Input Data</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    Edit every input number here. The calculated fields are not typed manually; they are generated automatically by the model.
    After editing, press <b>Save Product Data</b> and the whole app updates.
    </div>
    """, unsafe_allow_html=True)

    edited_products = st.data_editor(
        st.session_state.products,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="product_editor",
        column_config={
            "Product": st.column_config.TextColumn("Product"),
            "Category": st.column_config.TextColumn("Category"),
            "Supplier": st.column_config.TextColumn("Supplier"),
            "Annual Demand": st.column_config.NumberColumn("Annual Demand", min_value=0, step=1),
            "Actual Monthly Demand": st.column_config.NumberColumn("Actual Monthly Demand", min_value=0, step=1),
            "Growth %": st.column_config.NumberColumn("Growth %", step=0.5),
            "Current Stock": st.column_config.NumberColumn("Current Stock", min_value=0, step=1),
            "Ordering Cost": st.column_config.NumberColumn("Ordering Cost", min_value=0.0, step=1.0),
            "Holding Cost": st.column_config.NumberColumn("Holding Cost", min_value=0.01, step=0.1),
            "Lead Time Days": st.column_config.NumberColumn("Lead Time Days", min_value=1, step=1),
            "Demand SD": st.column_config.NumberColumn("Demand SD", min_value=0.0, step=0.5),
            "Unit Cost": st.column_config.NumberColumn("Unit Cost", min_value=0.0, step=0.5),
            "Selling Price": st.column_config.NumberColumn("Selling Price", min_value=0.0, step=0.5),
            "Orders": st.column_config.NumberColumn("Orders", min_value=0, step=1),
            "Orders Fulfilled": st.column_config.NumberColumn("Orders Fulfilled", min_value=0, step=1),
            "Stockouts": st.column_config.NumberColumn("Stockouts", min_value=0, step=1),
            "Review Period Days": st.column_config.NumberColumn("Review Period Days", min_value=1, step=1),
            "Target Service Level %": st.column_config.NumberColumn("Target Service Level %", min_value=50, max_value=99, step=1)
        }
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Product Data"):
            st.session_state.products = edited_products
            st.session_state.manual_products = None
            st.session_state.manual_override_enabled = False
            st.success("Product data saved. Manual overrides cleared and all EOQ, ROP, forecast and KPI calculations updated automatically.")
            st.rerun()

    with col2:
        if st.button("Reset Product Data"):
            st.session_state.products = default_products()
            st.rerun()

    st.markdown("### Automatic Calculation Preview")
    st.dataframe(
        products[[
            "Product", "EOQ", "Safety Stock", "Reorder Point", "Monthly Forecast",
            "Forecast Accuracy %", "Recommended Order Qty", "Suggested Action"
        ]],
        use_container_width=True,
        hide_index=True
    )


elif page == "🛠️ Manual Override Centre":
    st.markdown('<div class="section-title">Manual Override Centre: Edit Calculated Numbers</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    This page gives you two ways to use the application:
    <br><br>
    <b>Automatic mode:</b> You edit input numbers in Product Management and the app calculates EOQ, Safety Stock, ROP, Forecasts, Costs and KPIs automatically.
    <br>
    <b>Manual override mode:</b> You can directly edit calculated results such as EOQ, Safety Stock, Reorder Point, Forecast Accuracy, Inventory Value, Total Cost and Recommended Order Quantity.
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio(
        "Choose calculation mode",
        ["Automatic calculations", "Manual override calculations"],
        index=1 if st.session_state.manual_override_enabled else 0
    )

    if mode == "Automatic calculations":
        st.session_state.manual_override_enabled = False
        st.warning("Automatic mode is active. Calculated fields are generated from the input data.")
        st.dataframe(products, use_container_width=True, hide_index=True)

        if st.button("Clear manual overrides and return to automatic mode"):
            st.session_state.manual_products = None
            st.session_state.manual_override_enabled = False
            st.success("Manual overrides cleared.")
            st.rerun()

    else:
        st.session_state.manual_override_enabled = True
        st.markdown("""
        <div class="warn-box">
        Manual override mode is active. You can directly change calculated fields. 
        Use this if you want to test managerial judgement or force a scenario manually.
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.manual_products is None:
            editable_calculated = calculate_products(st.session_state.products, st.session_state.settings)
        else:
            editable_calculated = st.session_state.manual_products.copy()

        manual_edit = st.data_editor(
            editable_calculated,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="manual_override_editor",
            column_config={
                "Product": st.column_config.TextColumn("Product"),
                "Category": st.column_config.TextColumn("Category"),
                "Supplier": st.column_config.TextColumn("Supplier"),

                "Annual Demand": st.column_config.NumberColumn("Annual Demand", min_value=0, step=1),
                "Actual Monthly Demand": st.column_config.NumberColumn("Actual Monthly Demand", min_value=0, step=1),
                "Growth %": st.column_config.NumberColumn("Growth %", step=0.5),

                "Current Stock": st.column_config.NumberColumn("Current Stock", min_value=0, step=1),
                "Ordering Cost": st.column_config.NumberColumn("Ordering Cost", min_value=0.0, step=1.0),
                "Holding Cost": st.column_config.NumberColumn("Holding Cost", min_value=0.01, step=0.1),
                "Lead Time Days": st.column_config.NumberColumn("Lead Time Days", min_value=1, step=1),
                "Demand SD": st.column_config.NumberColumn("Demand SD", min_value=0.0, step=0.5),
                "Unit Cost": st.column_config.NumberColumn("Unit Cost", min_value=0.0, step=0.5),
                "Selling Price": st.column_config.NumberColumn("Selling Price", min_value=0.0, step=0.5),

                "Orders": st.column_config.NumberColumn("Orders", min_value=0, step=1),
                "Orders Fulfilled": st.column_config.NumberColumn("Orders Fulfilled", min_value=0, step=1),
                "Stockouts": st.column_config.NumberColumn("Stockouts", min_value=0, step=1),
                "Review Period Days": st.column_config.NumberColumn("Review Period Days", min_value=1, step=1),
                "Target Service Level %": st.column_config.NumberColumn("Target Service Level %", min_value=50, max_value=99, step=1),

                "Daily Demand": st.column_config.NumberColumn("Daily Demand", min_value=0.0, step=0.1),
                "Z Value": st.column_config.NumberColumn("Z Value", min_value=0.0, step=0.01),
                "EOQ": st.column_config.NumberColumn("EOQ", min_value=0.0, step=1.0),
                "Safety Stock": st.column_config.NumberColumn("Safety Stock", min_value=0.0, step=1.0),
                "Reorder Point": st.column_config.NumberColumn("Reorder Point", min_value=0.0, step=1.0),
                "Order-Up-To Level": st.column_config.NumberColumn("Order-Up-To Level", min_value=0.0, step=1.0),
                "Recommended Order Qty": st.column_config.NumberColumn("Recommended Order Qty", min_value=0.0, step=1.0),
                "Inventory Value": st.column_config.NumberColumn("Inventory Value", min_value=0.0, step=1.0),
                "Monthly Forecast": st.column_config.NumberColumn("Monthly Forecast", min_value=0.0, step=1.0),
                "Weekly Forecast": st.column_config.NumberColumn("Weekly Forecast", min_value=0.0, step=1.0),
                "Selected Horizon Forecast": st.column_config.NumberColumn("Selected Horizon Forecast", min_value=0.0, step=1.0),
                "Next Year Forecast": st.column_config.NumberColumn("Next Year Forecast", min_value=0.0, step=1.0),
                "Forecast Error": st.column_config.NumberColumn("Forecast Error", step=1.0),
                "Forecast Accuracy %": st.column_config.NumberColumn("Forecast Accuracy %", min_value=0.0, max_value=100.0, step=0.1),
                "Service Level %": st.column_config.NumberColumn("Service Level %", min_value=0.0, max_value=100.0, step=0.1),
                "Stockout Rate %": st.column_config.NumberColumn("Stockout Rate %", min_value=0.0, max_value=100.0, step=0.1),
                "Inventory Turnover": st.column_config.NumberColumn("Inventory Turnover", min_value=0.0, step=0.1),
                "Days of Cover": st.column_config.NumberColumn("Days of Cover", min_value=0.0, step=0.1),
                "Revenue Potential": st.column_config.NumberColumn("Revenue Potential", min_value=0.0, step=1.0),
                "COGS": st.column_config.NumberColumn("COGS", min_value=0.0, step=1.0),
                "Gross Margin %": st.column_config.NumberColumn("Gross Margin %", step=0.1),
                "Annual Usage Value": st.column_config.NumberColumn("Annual Usage Value", min_value=0.0, step=1.0),
                "Annual Ordering Cost": st.column_config.NumberColumn("Annual Ordering Cost", min_value=0.0, step=1.0),
                "Annual Holding Cost": st.column_config.NumberColumn("Annual Holding Cost", min_value=0.0, step=1.0),
                "Total Inventory Cost": st.column_config.NumberColumn("Total Inventory Cost", min_value=0.0, step=1.0),
                "Cumulative Value %": st.column_config.NumberColumn("Cumulative Value %", min_value=0.0, max_value=100.0, step=0.1),
                "ABC Class": st.column_config.TextColumn("ABC Class"),
                "Decision": st.column_config.TextColumn("Decision"),
                "Order Status": st.column_config.TextColumn("Order Status"),
                "Suggested Action": st.column_config.TextColumn("Suggested Action")
            }
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Save Manual Overrides"):
                st.session_state.manual_products = manual_edit.copy()
                st.session_state.manual_override_enabled = True
                st.success("Manual override values saved. All pages now use these numbers.")
                st.rerun()

        with col2:
            if st.button("Recalculate from Inputs"):
                st.session_state.manual_products = calculate_products(st.session_state.products, st.session_state.settings)
                st.session_state.manual_override_enabled = True
                st.success("Manual table recalculated from input data.")
                st.rerun()

        with col3:
            if st.button("Disable Manual Override"):
                st.session_state.manual_products = None
                st.session_state.manual_override_enabled = False
                st.success("Manual override disabled. Automatic calculations restored.")
                st.rerun()

    st.markdown("""
    ### What this page solves

    - You can edit input numbers manually.
    - You can let the model calculate automatically.
    - You can override calculated numbers if you want a custom managerial scenario.
    - All other pages use the saved override values while manual mode is enabled.
    """)


elif page == "🚚 Supplier Management":
    st.markdown('<div class="section-title">Supplier Management: Editable Supplier Data</div>', unsafe_allow_html=True)

    edited_suppliers = st.data_editor(
        st.session_state.suppliers,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="supplier_editor",
        column_config={
            "Supplier": st.column_config.TextColumn("Supplier"),
            "Region": st.column_config.TextColumn("Region"),
            "On-Time Delivery %": st.column_config.NumberColumn("On-Time Delivery %", min_value=0, max_value=100, step=1),
            "Quality %": st.column_config.NumberColumn("Quality %", min_value=0, max_value=100, step=1),
            "Cost Score %": st.column_config.NumberColumn("Cost Score %", min_value=0, max_value=100, step=1),
            "Risk Score %": st.column_config.NumberColumn("Risk Score %", min_value=0, max_value=100, step=1),
            "Average Lead Time Days": st.column_config.NumberColumn("Average Lead Time Days", min_value=1, step=1)
        }
    )

    if st.button("Save Supplier Data"):
        st.session_state.suppliers = edited_suppliers
        st.success("Supplier data saved and supplier scores recalculated.")
        st.rerun()

    st.markdown("### Supplier Scorecard")
    st.dataframe(suppliers, use_container_width=True, hide_index=True)
    st.bar_chart(suppliers.set_index("Supplier")[["Supplier Score %", "Risk Score %"]])

elif page == "📈 Forecast Planning":
    st.markdown('<div class="section-title">Forecast Planning</div>', unsafe_allow_html=True)

    forecast = products[[
        "Product", "Annual Demand", "Actual Monthly Demand", "Monthly Forecast",
        "Weekly Forecast", "Selected Horizon Forecast", "Next Year Forecast", "Growth %"
    ]]

    st.dataframe(forecast, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Monthly Forecast")
        st.bar_chart(forecast.set_index("Product")["Monthly Forecast"])
    with col2:
        st.markdown(f"### Selected Horizon Forecast ({st.session_state.settings['forecast_horizon_value']} {st.session_state.settings['forecast_horizon_unit']})")
        st.bar_chart(forecast.set_index("Product")["Selected Horizon Forecast"])

elif page == "📊 Forecast Accuracy":
    st.markdown('<div class="section-title">Forecast Accuracy</div>', unsafe_allow_html=True)

    accuracy = products[[
        "Product", "Actual Monthly Demand", "Monthly Forecast",
        "Forecast Error", "Forecast Accuracy %"
    ]]

    st.dataframe(accuracy, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Actual Demand vs Forecast Demand")
        st.bar_chart(accuracy.set_index("Product")[["Actual Monthly Demand", "Monthly Forecast"]])
    with col2:
        st.markdown("### Forecast Accuracy %")
        st.bar_chart(accuracy.set_index("Product")["Forecast Accuracy %"])

elif page == "📦 Inventory Control":
    st.markdown('<div class="section-title">Inventory Control: EOQ, Safety Stock and Reorder Point</div>', unsafe_allow_html=True)

    st.latex(r"EOQ=\sqrt{\frac{2DS}{H}}")
    st.latex(r"Safety\ Stock=Z \times \sigma_d \times \sqrt{LT}")
    st.latex(r"ROP=Daily\ Demand \times Lead\ Time + Safety\ Stock")

    inv = products[[
        "Product", "Annual Demand", "Current Stock", "Daily Demand", "EOQ",
        "Safety Stock", "Reorder Point", "Order-Up-To Level",
        "Days of Cover", "Decision"
    ]]

    st.dataframe(inv, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Current Stock vs ROP")
        st.bar_chart(products.set_index("Product")[["Current Stock", "Reorder Point"]])
    with col2:
        st.markdown("### Days of Cover")
        st.bar_chart(products.set_index("Product")["Days of Cover"])

elif page == "📋 Order Management":
    st.markdown('<div class="section-title">Order Management</div>', unsafe_allow_html=True)

    orders = products[[
        "Product", "Supplier", "Current Stock", "Reorder Point", "EOQ",
        "Recommended Order Qty", "Order Status"
    ]]

    st.dataframe(orders, use_container_width=True, hide_index=True)

    open_orders = orders[orders["Order Status"] == "Create Purchase Order"]

    if open_orders.empty:
        st.markdown('<div class="good-box">No purchase orders are currently required.</div>', unsafe_allow_html=True)
    else:
        for _, row in open_orders.iterrows():
            st.markdown(
                f"""
                <div class="bad-box">
                <b>{row['Product']}</b>: create purchase order for <b>{row['Recommended Order Qty']}</b> units from <b>{row['Supplier']}</b>.
                </div>
                """,
                unsafe_allow_html=True
            )

elif page == "🧾 Purchase Order Generator":
    st.markdown('<div class="section-title">Purchase Order Generator</div>', unsafe_allow_html=True)

    purchase_orders = products[products["Order Status"] == "Create Purchase Order"][
        ["Supplier", "Product", "Current Stock", "Reorder Point", "EOQ", "Recommended Order Qty", "Unit Cost"]
    ].copy()

    if purchase_orders.empty:
        st.markdown('<div class="good-box">No purchase orders are required at the moment.</div>', unsafe_allow_html=True)
    else:
        purchase_orders["Estimated Order Value"] = (
            purchase_orders["Recommended Order Qty"] * purchase_orders["Unit Cost"]
        ).round(2)

        st.dataframe(purchase_orders, use_container_width=True, hide_index=True)

        selected_supplier = st.selectbox("Select supplier", purchase_orders["Supplier"].unique())
        selected_orders = purchase_orders[purchase_orders["Supplier"] == selected_supplier]

        st.markdown("### Generated Purchase Order")
        st.write(f"**Supplier:** {selected_supplier}")

        for _, row in selected_orders.iterrows():
            st.write(
                f"- Order {int(row['Recommended Order Qty'])} units of {row['Product']} "
                f"(estimated value €{row['Estimated Order Value']:,.2f})."
            )

        st.success(f"Total PO value: €{selected_orders['Estimated Order Value'].sum():,.2f}")

elif page == "📊 Visual Analytics":
    st.markdown('<div class="section-title">Visual Analytics</div>', unsafe_allow_html=True)

    chart_choice = st.selectbox(
        "Choose chart",
        [
            "EOQ by Product",
            "Current Stock vs Reorder Point",
            "Inventory Value",
            "Forecast Accuracy",
            "Gross Margin",
            "Supplier Score and Risk",
            "ABC Usage Value",
            "Total Inventory Cost"
        ]
    )

    if chart_choice == "EOQ by Product":
        st.bar_chart(products.set_index("Product")["EOQ"])
    elif chart_choice == "Current Stock vs Reorder Point":
        st.bar_chart(products.set_index("Product")[["Current Stock", "Reorder Point"]])
    elif chart_choice == "Inventory Value":
        st.bar_chart(products.set_index("Product")["Inventory Value"])
    elif chart_choice == "Forecast Accuracy":
        st.bar_chart(products.set_index("Product")["Forecast Accuracy %"])
    elif chart_choice == "Gross Margin":
        st.bar_chart(products.set_index("Product")["Gross Margin %"])
    elif chart_choice == "Supplier Score and Risk":
        st.bar_chart(suppliers.set_index("Supplier")[["Supplier Score %", "Risk Score %"]])
    elif chart_choice == "ABC Usage Value":
        st.bar_chart(products.set_index("Product")["Annual Usage Value"])
    elif chart_choice == "Total Inventory Cost":
        st.bar_chart(products.set_index("Product")["Total Inventory Cost"])

elif page == "🏷️ ABC Analysis":
    st.markdown('<div class="section-title">ABC Inventory Analysis</div>', unsafe_allow_html=True)

    abc = products[[
        "Product", "Annual Demand", "Unit Cost", "Annual Usage Value",
        "Cumulative Value %", "ABC Class"
    ]]

    st.dataframe(abc, use_container_width=True, hide_index=True)
    st.bar_chart(abc.set_index("Product")["Annual Usage Value"])

elif page == "💰 Cost Analysis":
    st.markdown('<div class="section-title">Inventory Cost Analysis</div>', unsafe_allow_html=True)

    cost = products[[
        "Product", "Annual Ordering Cost", "Annual Holding Cost", "Total Inventory Cost",
        "Revenue Potential", "COGS", "Gross Margin %"
    ]]

    st.dataframe(cost, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Inventory Cost")
        st.bar_chart(cost.set_index("Product")[["Annual Ordering Cost", "Annual Holding Cost"]])
    with col2:
        st.markdown("### Gross Margin %")
        st.bar_chart(cost.set_index("Product")["Gross Margin %"])

elif page == "🎯 KPI Targets":
    st.markdown('<div class="section-title">KPI Targets</div>', unsafe_allow_html=True)

    kpi_data = pd.DataFrame({
        "KPI": ["Service Level %", "Stockout Rate %", "Forecast Accuracy %", "Supplier Score %", "Inventory Turnover"],
        "Current": [
            products["Service Level %"].mean().round(1),
            products["Stockout Rate %"].mean().round(1),
            products["Forecast Accuracy %"].mean().round(1),
            suppliers["Supplier Score %"].mean().round(1),
            products["Inventory Turnover"].mean().round(2)
        ],
        "Target": [95, 2, 90, 90, 10]
    })
    kpi_data["Gap"] = (kpi_data["Current"] - kpi_data["Target"]).round(2)
    st.dataframe(kpi_data, use_container_width=True, hide_index=True)

elif page == "🧪 Scenario Planning":
    st.markdown('<div class="section-title">Scenario Planning</div>', unsafe_allow_html=True)

    product = st.selectbox("Select product", products["Product"])
    row = products[products["Product"] == product].iloc[0]

    demand_change = st.slider("Demand Change %", -50, 100, 20)
    lead_change = st.slider("Lead Time Change Days", -5, 20, 5)
    holding_change = st.slider("Holding Cost Change %", -50, 100, 0)

    new_demand = row["Annual Demand"] * (1 + demand_change / 100)
    new_lead = max(1, row["Lead Time Days"] + lead_change)
    new_holding = row["Holding Cost"] * (1 + holding_change / 100)

    new_daily = new_demand / st.session_state.settings["working_days_per_year"]
    new_eoq = np.sqrt((2 * new_demand * row["Ordering Cost"]) / new_holding) if new_holding > 0 else 0
    new_ss = row["Z Value"] * row["Demand SD"] * np.sqrt(new_lead)
    new_rop = new_daily * new_lead + new_ss

    c1, c2, c3 = st.columns(3)
    c1.metric("Scenario EOQ", f"{new_eoq:.0f}")
    c2.metric("Scenario Safety Stock", f"{new_ss:.0f}")
    c3.metric("Scenario Reorder Point", f"{new_rop:.0f}")

elif page == "🤖 AI Assistance":
    st.markdown('<div class="section-title">AI Assistance / Decision Assistant</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    This is a transparent rule-based AI assistant. It explains management actions using EOQ, reorder point,
    forecast accuracy, supplier risk, stockout rate and margin.
    </div>
    """, unsafe_allow_html=True)

    question = st.selectbox(
        "Choose what you need help with",
        [
            "Overall management summary",
            "Which products need ordering?",
            "Which forecasts are weak?",
            "Which suppliers are risky?",
            "Which products have low margin?",
            "What should I prioritise?"
        ]
    )

    if question == "Overall management summary":
        st.write(f"Products monitored: {len(products)}")
        st.write(f"Reorder alerts: {len(products[products['Decision'] == 'Reorder Required'])}")
        st.write(f"Average forecast accuracy: {products['Forecast Accuracy %'].mean():.1f}%")
        st.write(f"Average supplier score: {suppliers['Supplier Score %'].mean():.1f}%")
        st.success("Priority: fix reorder alerts first, then review weak forecasts and supplier risks.")

    elif question == "Which products need ordering?":
        subset = products[products["Order Status"] == "Create Purchase Order"]
        if subset.empty:
            st.success("No product currently requires ordering.")
        else:
            for _, row in subset.iterrows():
                st.warning(f"{row['Product']}: order {row['Recommended Order Qty']} units from {row['Supplier']}.")

    elif question == "Which forecasts are weak?":
        subset = products[products["Forecast Accuracy %"] < 75]
        if subset.empty:
            st.success("Forecast accuracy is acceptable.")
        else:
            for _, row in subset.iterrows():
                st.warning(f"{row['Product']}: forecast accuracy {row['Forecast Accuracy %']}%, error {row['Forecast Error']} units.")

    elif question == "Which suppliers are risky?":
        subset = suppliers[(suppliers["Risk Score %"] >= 40) | (suppliers["Supplier Score %"] < 80)]
        if subset.empty:
            st.success("No high supplier risk detected.")
        else:
            for _, row in subset.iterrows():
                st.warning(f"{row['Supplier']}: score {row['Supplier Score %']}%, risk {row['Risk Score %']}%, status {row['Status']}.")

    elif question == "Which products have low margin?":
        subset = products[products["Gross Margin %"] < 25]
        if subset.empty:
            st.success("No low-margin products detected.")
        else:
            for _, row in subset.iterrows():
                st.warning(f"{row['Product']}: gross margin {row['Gross Margin %']}%.")

    elif question == "What should I prioritise?":
        st.markdown("### Priority list")
        for _, row in products.iterrows():
            if row["Suggested Action"] != "Monitor":
                st.write(f"- {row['Product']}: {row['Suggested Action']}")
        st.info("If nothing appears above, the system is currently stable.")

elif page == "✅ Action Centre":
    st.markdown('<div class="section-title">Action Centre</div>', unsafe_allow_html=True)

    for _, row in products.iterrows():
        if row["Suggested Action"] == "Create purchase order":
            st.markdown(f'<div class="bad-box"><b>{row["Product"]}</b>: create purchase order for {row["EOQ"]} units.</div>', unsafe_allow_html=True)
        elif row["Suggested Action"] != "Monitor":
            st.markdown(f'<div class="warn-box"><b>{row["Product"]}</b>: {row["Suggested Action"]}.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="good-box"><b>{row["Product"]}</b>: monitor.</div>', unsafe_allow_html=True)

elif page == "ℹ️ Assumptions":
    st.markdown('<div class="section-title">Assumptions & Academic Notes</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    The app uses simulated data for academic demonstration. It is a functional prototype, not a production ERP system.
    </div>
    """, unsafe_allow_html=True)

    st.write("""
    The application supports forecasting, inventory planning, EOQ, safety stock, reorder point,
    order management, supplier management, KPI monitoring, visual analytics and AI-style decision assistance.
    """)

elif page == "📤 Export":
    st.markdown('<div class="section-title">Export Centre</div>', unsafe_allow_html=True)

    st.download_button(
        "Download Product Calculations",
        products.to_csv(index=False).encode("utf-8"),
        "product_calculations.csv",
        "text/csv"
    )

    st.download_button(
        "Download Supplier Scorecard",
        suppliers.to_csv(index=False).encode("utf-8"),
        "supplier_scorecard.csv",
        "text/csv"
    )

    actions = products[["Product", "Supplier", "Suggested Action", "EOQ", "Reorder Point", "Recommended Order Qty"]]
    st.download_button(
        "Download Management Actions",
        actions.to_csv(index=False).encode("utf-8"),
        "management_actions.csv",
        "text/csv"
    )
