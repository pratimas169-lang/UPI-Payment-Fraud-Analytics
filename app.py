import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="UPI Payment & Fraud Analytics",
    page_icon="💳",
    layout="wide"
)

st.title("💳 UPI Payment & Fraud Analytics")
st.caption("Transaction, Fraud Risk, User Analytics & Fraud Prediction")


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

@st.cache_resource
def get_connection():
    return st.connection("snowflake")


conn = get_connection()

try:
    conn.query("SELECT 1")
    st.success("Snowflake connection successful!")
except Exception:
    st.error("Snowflake connection failed.")
    st.stop()


# ============================================================
# TABLE NAMES
# ============================================================

TRANSACTIONS_TABLE = """
UPI_FRAUD_ANALYTICS.CURATED.TRANSACTIONS_CURATED
"""

USERS_TABLE = """
UPI_FRAUD_ANALYTICS.RAW_DATA.USERS
"""

MERCHANTS_TABLE = """
UPI_FRAUD_ANALYTICS.RAW_DATA.MERCHANTS
"""


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Executive Overview",
    "Fraud & Risk",
    "User, Merchant & Segmentation",
    "Fraud Prediction & Action"
])


# ============================================================
# TAB 1 — EXECUTIVE OVERVIEW
# ============================================================

with tab1:

    st.header("Executive Overview")
    st.subheader("Descriptive Analytics")

    kpi_query = f"""
    SELECT
        COUNT(*) AS TOTAL_TRANSACTIONS,

        SUM(AMOUNT) AS TOTAL_TRANSACTION_VALUE,

        SUM(
            CASE
                WHEN UPPER(TRIM(STATUS)) = 'SUCCESS'
                THEN 1 ELSE 0
            END
        ) AS SUCCESSFUL_TRANSACTIONS,

        ROUND(
            AVG(
                CASE
                    WHEN IS_FRAUD = 1 THEN 1
                    ELSE 0
                END
            ) * 100, 2
        ) AS FRAUD_RATE,

        ROUND(AVG(AMOUNT), 2)
            AS AVERAGE_TRANSACTION_AMOUNT

    FROM {TRANSACTIONS_TABLE}
    """

    kpi = conn.query(kpi_query)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Transactions (Count)",
        f"{int(kpi.iloc[0]['TOTAL_TRANSACTIONS']):,}"
    )

    col2.metric(
        "Total Transaction Value",
        f"{kpi.iloc[0]['TOTAL_TRANSACTION_VALUE']:,.2f}"
    )

    col3.metric(
        "Successful Transactions (Count)",
        f"{int(kpi.iloc[0]['SUCCESSFUL_TRANSACTIONS']):,}"
    )

    col4.metric(
        "Fraud Rate (%)",
        f"{kpi.iloc[0]['FRAUD_RATE']:.2f}%"
    )

    col5.metric(
        "Average Transaction Amount",
        f"{kpi.iloc[0]['AVERAGE_TRANSACTION_AMOUNT']:,.2f}"
    )

    st.divider()

    # Transaction Trend
    st.subheader("Transaction Trend Over Time")

    trend_query = f"""
    SELECT
        DATE,
        COUNT(*) AS TRANSACTION_COUNT
    FROM {TRANSACTIONS_TABLE}
    GROUP BY DATE
    ORDER BY DATE
    """

    trend_df = conn.query(trend_query)
    trend_df["DATE"] = pd.to_datetime(trend_df["DATE"])

    st.line_chart(
        trend_df.set_index("DATE")["TRANSACTION_COUNT"]
    )

    # Payment App
    st.subheader("Transaction Value by Payment App")

    app_query = f"""
    SELECT
        PAYMENT_APP,
        SUM(AMOUNT) AS TRANSACTION_VALUE
    FROM {TRANSACTIONS_TABLE}
    GROUP BY PAYMENT_APP
    ORDER BY TRANSACTION_VALUE DESC
    """

    app_df = conn.query(app_query)

    st.bar_chart(
        app_df.set_index("PAYMENT_APP")["TRANSACTION_VALUE"]
    )

    # Device Type
    st.subheader("Transactions by Device Type")

    device_query = f"""
    SELECT
        DEVICE_TYPE,
        COUNT(*) AS TRANSACTION_COUNT
    FROM {TRANSACTIONS_TABLE}
    GROUP BY DEVICE_TYPE
    ORDER BY TRANSACTION_COUNT DESC
    """

    device_df = conn.query(device_query)

    st.bar_chart(
        device_df.set_index("DEVICE_TYPE")["TRANSACTION_COUNT"]
    )

    # Status
    st.subheader("Transaction Status Distribution")

    status_query = f"""
    SELECT
        STATUS,
        COUNT(*) AS TRANSACTION_COUNT
    FROM {TRANSACTIONS_TABLE}
    GROUP BY STATUS
    ORDER BY TRANSACTION_COUNT DESC
    """

    status_df = conn.query(status_query)

    st.bar_chart(
        status_df.set_index("STATUS")["TRANSACTION_COUNT"]
    )


# ============================================================
# TAB 2 — FRAUD & RISK
# ============================================================

with tab2:

    st.header("Fraud & Risk")
    st.subheader("Diagnostic Analytics")

    fraud_kpi_query = f"""
    SELECT
        COUNT_IF(IS_FRAUD = 1)
            AS FRAUDULENT_TRANSACTIONS,

        SUM(
            CASE
                WHEN IS_FRAUD = 1 THEN AMOUNT
                ELSE 0
            END
        ) AS FRAUD_TRANSACTION_VALUE,

        COUNT_IF(NEW_DEVICE_FLAG = 1)
            AS NEW_DEVICE_TRANSACTIONS,

        COUNT_IF(
            NEW_DEVICE_FLAG = 1
            OR IP_LOCATION_MISMATCH = 1
            OR FAILED_ATTEMPTS_LAST_24H > 0
        ) AS RISK_FLAGGED_TRANSACTIONS

    FROM {TRANSACTIONS_TABLE}
    """

    fraud_kpi = conn.query(fraud_kpi_query)

    high_risk_query = f"""
    SELECT COUNT(*) AS HIGH_RISK_USERS
    FROM {USERS_TABLE}
    WHERE IS_HIGH_RISK_USER = 1
    """

    high_risk_df = conn.query(high_risk_query)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Fraudulent Transactions (Count)",
        f"{int(fraud_kpi.iloc[0]['FRAUDULENT_TRANSACTIONS']):,}"
    )

    col2.metric(
        "Fraud Transaction Value",
        f"{fraud_kpi.iloc[0]['FRAUD_TRANSACTION_VALUE']:,.2f}"
    )

    col3.metric(
        "High-Risk Users (Count)",
        f"{int(high_risk_df.iloc[0]['HIGH_RISK_USERS']):,}"
    )

    col4.metric(
        "New Device Transactions (Count)",
        f"{int(fraud_kpi.iloc[0]['NEW_DEVICE_TRANSACTIONS']):,}"
    )

    col5.metric(
        "Risk-Flagged Transactions (Count)",
        f"{int(fraud_kpi.iloc[0]['RISK_FLAGGED_TRANSACTIONS']):,}"
    )

    st.divider()

    # Fraud Trend
    st.subheader("Fraud Transaction Trend")

    fraud_trend_query = f"""
    SELECT
        DATE,
        COUNT_IF(IS_FRAUD = 1) AS FRAUD_COUNT
    FROM {TRANSACTIONS_TABLE}
    GROUP BY DATE
    ORDER BY DATE
    """

    fraud_trend_df = conn.query(fraud_trend_query)
    fraud_trend_df["DATE"] = pd.to_datetime(
        fraud_trend_df["DATE"]
    )

    st.line_chart(
        fraud_trend_df.set_index("DATE")["FRAUD_COUNT"]
    )

    # Fraud Rate by App
    st.subheader("Fraud Rate by Payment App")

    fraud_app_query = f"""
    SELECT
        PAYMENT_APP,
        ROUND(AVG(IS_FRAUD) * 100, 2)
            AS FRAUD_RATE_PERCENT
    FROM {TRANSACTIONS_TABLE}
    GROUP BY PAYMENT_APP
    ORDER BY FRAUD_RATE_PERCENT DESC
    """

    fraud_app_df = conn.query(fraud_app_query)

    st.bar_chart(
        fraud_app_df.set_index("PAYMENT_APP")[
            "FRAUD_RATE_PERCENT"
        ]
    )

    # Fraud by Device
    st.subheader("Fraud by Device Type")

    fraud_device_query = f"""
    SELECT
        DEVICE_TYPE,
        COUNT_IF(IS_FRAUD = 1) AS FRAUD_COUNT
    FROM {TRANSACTIONS_TABLE}
    GROUP BY DEVICE_TYPE
    ORDER BY FRAUD_COUNT DESC
    """

    fraud_device_df = conn.query(fraud_device_query)

    st.bar_chart(
        fraud_device_df.set_index("DEVICE_TYPE")[
            "FRAUD_COUNT"
        ]
    )

    # Fraud by Hour
    st.subheader("Fraud Transactions by Hour")

    fraud_hour_query = f"""
    SELECT
        HOUR_OF_DAY,
        COUNT_IF(IS_FRAUD = 1) AS FRAUD_COUNT
    FROM {TRANSACTIONS_TABLE}
    GROUP BY HOUR_OF_DAY
    ORDER BY HOUR_OF_DAY
    """

    fraud_hour_df = conn.query(fraud_hour_query)

    st.line_chart(
        fraud_hour_df.set_index("HOUR_OF_DAY")[
            "FRAUD_COUNT"
        ]
    )


# ============================================================
# TAB 3 — USER, MERCHANT & SEGMENTATION
# ============================================================

with tab3:

    st.header("User, Merchant & Segmentation")

    user_kpi_query = f"""
    SELECT

        (SELECT COUNT(*)
         FROM {USERS_TABLE})
         AS TOTAL_USERS,

        (SELECT COUNT(*)
         FROM {MERCHANTS_TABLE})
         AS TOTAL_MERCHANTS,

        (SELECT ROUND(AVG(AMOUNT), 2)
         FROM {TRANSACTIONS_TABLE})
         AS AVERAGE_USER_TRANSACTION_VALUE,

        (SELECT ROUND(
            COUNT(*) / COUNT(DISTINCT USER_ID), 2
         )
         FROM {TRANSACTIONS_TABLE})
         AS AVERAGE_TRANSACTIONS_PER_USER,

        (SELECT ROUND(
            AVG(AVG_MONTHLY_TRANSACTIONS), 2
         )
         FROM {USERS_TABLE})
         AS AVERAGE_MONTHLY_TRANSACTIONS
    """

    user_kpi = conn.query(user_kpi_query)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Users (Count)",
        f"{int(user_kpi.iloc[0]['TOTAL_USERS']):,}"
    )

    col2.metric(
        "Total Merchants (Count)",
        f"{int(user_kpi.iloc[0]['TOTAL_MERCHANTS']):,}"
    )

    col3.metric(
        "Average User Transaction Value",
        f"{user_kpi.iloc[0]['AVERAGE_USER_TRANSACTION_VALUE']:,.2f}"
    )

    col4.metric(
        "Average Transactions per User",
        f"{user_kpi.iloc[0]['AVERAGE_TRANSACTIONS_PER_USER']:,.2f}"
    )

    col5.metric(
        "Average Monthly Transactions",
        f"{user_kpi.iloc[0]['AVERAGE_MONTHLY_TRANSACTIONS']:,.2f}"
    )

    st.divider()

    # Age Group
    st.subheader("Transactions by Age Group")

    age_query = f"""
    SELECT
        U.AGE_GROUP,
        COUNT(T.TRANSACTION_ID)
            AS TRANSACTION_COUNT
    FROM {TRANSACTIONS_TABLE} T
    INNER JOIN {USERS_TABLE} U
        ON T.USER_ID = U.USER_ID
    GROUP BY U.AGE_GROUP
    ORDER BY TRANSACTION_COUNT DESC
    """

    age_df = conn.query(age_query)

    st.bar_chart(
        age_df.set_index("AGE_GROUP")[
            "TRANSACTION_COUNT"
        ]
    )

    # Merchant Category
    st.subheader("Top Merchant Categories by Transaction Value")

    merchant_category_query = f"""
    SELECT
        M.MERCHANT_CATEGORY,
        SUM(T.AMOUNT) AS TRANSACTION_VALUE
    FROM {TRANSACTIONS_TABLE} T
    INNER JOIN {MERCHANTS_TABLE} M
        ON T.RECEIVER_ID = M.MERCHANT_ID
    WHERE LOWER(TRIM(T.RECEIVER_TYPE)) = 'merchant'
    GROUP BY M.MERCHANT_CATEGORY
    ORDER BY TRANSACTION_VALUE DESC
    """

    merchant_category_df = conn.query(
        merchant_category_query
    )

    st.bar_chart(
        merchant_category_df.set_index(
            "MERCHANT_CATEGORY"
        )["TRANSACTION_VALUE"]
    )

    # City Tier
    st.subheader("High-Risk Users by City Tier")

    city_risk_query = f"""
    SELECT
        CITY_TIER,
        COUNT(*) AS HIGH_RISK_USERS
    FROM {USERS_TABLE}
    WHERE IS_HIGH_RISK_USER = 1
    GROUP BY CITY_TIER
    ORDER BY HIGH_RISK_USERS DESC
    """

    city_risk_df = conn.query(city_risk_query)

    st.bar_chart(
        city_risk_df.set_index("CITY_TIER")[
            "HIGH_RISK_USERS"
        ]
    )

    # Merchant Size
    st.subheader("Merchant Size by Fraud Rate")

    merchant_size_query = f"""
    SELECT
        M.MERCHANT_SIZE,
        ROUND(AVG(T.IS_FRAUD) * 100, 2)
            AS FRAUD_RATE_PERCENT
    FROM {TRANSACTIONS_TABLE} T
    INNER JOIN {MERCHANTS_TABLE} M
        ON T.RECEIVER_ID = M.MERCHANT_ID
    WHERE LOWER(TRIM(T.RECEIVER_TYPE)) = 'merchant'
    GROUP BY M.MERCHANT_SIZE
    ORDER BY FRAUD_RATE_PERCENT DESC
    """

    merchant_size_df = conn.query(
        merchant_size_query
    )

    st.bar_chart(
        merchant_size_df.set_index("MERCHANT_SIZE")[
            "FRAUD_RATE_PERCENT"
        ]
    )


# ============================================================
# TAB 4 — FRAUD PREDICTION & ACTION
# ============================================================

with tab4:

    st.header("Fraud Prediction & Recommended Action")

    st.write(
        "Predictive Analytics → Fraud Probability → "
        "Risk Level → Recommended Business Action"
    )

    # ========================================================
    # PREDICTIVE MODEL PERFORMANCE
    # ========================================================

    st.subheader("Predictive Model Performance")

    st.caption(
        "Evaluation results from the Random Forest model "
        "developed in Databricks."
    )

    # Actual Databricks results
    databricks_precision = 0.0000
    databricks_recall = 0.0000
    databricks_f1 = 0.9515
    databricks_roc_auc = 0.7339

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Precision",
        f"{databricks_precision:.4f}"
    )

    col2.metric(
        "Recall",
        f"{databricks_recall:.4f}"
    )

    col3.metric(
        "F1-Score",
        f"{databricks_f1:.4f}"
    )

    col4.metric(
        "ROC-AUC",
        f"{databricks_roc_auc:.4f}"
    )

    st.divider()

    # ========================================================
    # PRESCRIPTIVE ACTION FRAMEWORK
    # ========================================================

    st.subheader("Prescriptive Risk-Action Framework")

    st.write(
        "The recommended action is based on the predicted "
        "fraud probability."
    )

    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        st.success(
            "**LOW RISK**\n\n"
            "Fraud Probability < 30%\n\n"
            "Recommended Action:\n"
            "**Normal processing**"
        )

    with action_col2:
        st.warning(
            "**MEDIUM RISK**\n\n"
            "Fraud Probability 30%–70%\n\n"
            "Recommended Action:\n"
            "**Additional verification**"
        )

    with action_col3:
        st.error(
            "**HIGH RISK**\n\n"
            "Fraud Probability > 70%\n\n"
            "Recommended Action:\n"
            "**Flag for investigation**"
        )

    st.divider()

    # ========================================================
    # LOAD MODELING DATA
    # ========================================================

    @st.cache_data
    def load_model_data():

        model_query = f"""
        SELECT
            AMOUNT,
            HOUR_OF_DAY,
            IS_WEEKEND,
            IS_NIGHT_TRANSACTION,
            NEW_DEVICE_FLAG,
            IP_LOCATION_MISMATCH,
            FAILED_ATTEMPTS_LAST_24H,
            TRANSACTION_VELOCITY,
            AMOUNT_DEVIATION_SCORE,
            IS_FRAUD

        FROM {TRANSACTIONS_TABLE}

        WHERE AMOUNT IS NOT NULL
          AND HOUR_OF_DAY IS NOT NULL
          AND IS_WEEKEND IS NOT NULL
          AND IS_NIGHT_TRANSACTION IS NOT NULL
          AND NEW_DEVICE_FLAG IS NOT NULL
          AND IP_LOCATION_MISMATCH IS NOT NULL
          AND FAILED_ATTEMPTS_LAST_24H IS NOT NULL
          AND TRANSACTION_VELOCITY IS NOT NULL
          AND AMOUNT_DEVIATION_SCORE IS NOT NULL
          AND IS_FRAUD IS NOT NULL
        """

        return conn.query(model_query)


    model_df = load_model_data()

    # ========================================================
    # FEATURES
    # ========================================================

    features = [
        "AMOUNT",
        "HOUR_OF_DAY",
        "IS_WEEKEND",
        "IS_NIGHT_TRANSACTION",
        "NEW_DEVICE_FLAG",
        "IP_LOCATION_MISMATCH",
        "FAILED_ATTEMPTS_LAST_24H",
        "TRANSACTION_VELOCITY",
        "AMOUNT_DEVIATION_SCORE"
    ]

    target = "IS_FRAUD"

    X = model_df[features]
    y = model_df[target]

    # ========================================================
    # TRAIN / TEST SPLIT
    # ========================================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    # ========================================================
    # RANDOM FOREST
    # ========================================================

    @st.cache_resource
    def train_random_forest(X_train, y_train):

        rf_model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )

        rf_model.fit(X_train, y_train)

        return rf_model


    model = train_random_forest(
        X_train,
        y_train
    )

    # ========================================================
    # INTERACTIVE PREDICTION INPUT
    # ========================================================

    st.subheader("Enter Transaction Details")

    col1, col2, col3 = st.columns(3)

    with col1:

        amount = st.number_input(
            "Transaction Amount",
            min_value=0.0,
            value=1000.0,
            step=100.0
        )

        hour_of_day = st.slider(
            "Hour of Day",
            min_value=0,
            max_value=23,
            value=12
        )

        is_weekend = st.selectbox(
            "Weekend Transaction?",
            [0, 1],
            format_func=lambda x:
            "Yes" if x == 1 else "No"
        )

    with col2:

        is_night_transaction = st.selectbox(
            "Night Transaction?",
            [0, 1],
            format_func=lambda x:
            "Yes" if x == 1 else "No"
        )

        new_device_flag = st.selectbox(
            "New Device?",
            [0, 1],
            format_func=lambda x:
            "Yes" if x == 1 else "No"
        )

        ip_location_mismatch = st.selectbox(
            "IP Location Mismatch?",
            [0, 1],
            format_func=lambda x:
            "Yes" if x == 1 else "No"
        )

    with col3:

        failed_attempts = st.number_input(
            "Failed Attempts in Last 24 Hours",
            min_value=0,
            value=0,
            step=1
        )

        transaction_velocity = st.number_input(
            "Transaction Velocity",
            min_value=0,
            value=0,
            step=1
        )

        amount_deviation = st.number_input(
            "Amount Deviation Score",
            value=0.4445,
            step=0.1
        )

    # ========================================================
    # PREDICT BUTTON
    # ========================================================

    predict_button = st.button(
        "🔍 Predict Fraud Risk",
        type="primary",
        use_container_width=True
    )

    if predict_button:

        input_data = pd.DataFrame({

            "AMOUNT": [amount],

            "HOUR_OF_DAY": [hour_of_day],

            "IS_WEEKEND": [is_weekend],

            "IS_NIGHT_TRANSACTION": [
                is_night_transaction
            ],

            "NEW_DEVICE_FLAG": [
                new_device_flag
            ],

            "IP_LOCATION_MISMATCH": [
                ip_location_mismatch
            ],

            "FAILED_ATTEMPTS_LAST_24H": [
                failed_attempts
            ],

            "TRANSACTION_VELOCITY": [
                transaction_velocity
            ],

            "AMOUNT_DEVIATION_SCORE": [
                amount_deviation
            ]
        })

        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        prediction = model.predict(input_data)[0]

        fraud_probability = model.predict_proba(
            input_data
        )[0][1]

        # ----------------------------------------------------
        # Prescriptive Risk Logic
        # ----------------------------------------------------

        if fraud_probability < 0.30:

            risk_level = "Low Risk"

            recommended_action = (
                "Normal processing"
            )

        elif fraud_probability < 0.70:

            risk_level = "Medium Risk"

            recommended_action = (
                "Additional verification"
            )

        else:

            risk_level = "High Risk"

            recommended_action = (
                "Flag for investigation"
            )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        st.divider()

        st.subheader("Prediction Result")

        result_col1, result_col2, result_col3 = st.columns(3)

        result_col1.metric(
            "Fraud Probability",
            f"{fraud_probability * 100:.2f}%"
        )

        if prediction == 1:

            prediction_text = "Potential Fraud"

        else:

            prediction_text = "Non-Fraud"

        result_col2.metric(
            "Model Prediction",
            prediction_text
        )

        result_col3.metric(
            "Risk Level",
            risk_level
        )

        # ----------------------------------------------------
        # RECOMMENDED BUSINESS ACTION
        # ----------------------------------------------------

        st.subheader(
            "🎯 Recommended Business Action"
        )

        if risk_level == "Low Risk":

            st.success(
                "🟢 **LOW RISK**\n\n"
                "**Recommended Action: NORMAL PROCESSING**"
            )

        elif risk_level == "Medium Risk":

            st.warning(
                "🟡 **MEDIUM RISK**\n\n"
                "**Recommended Action: "
                "ADDITIONAL VERIFICATION**"
            )

        else:

            st.error(
                "🔴 **HIGH RISK**\n\n"
                "**Recommended Action: "
                "FLAG FOR INVESTIGATION**"
            )

        # ----------------------------------------------------
        # Transaction Input Summary
        # ----------------------------------------------------

        with st.expander(
            "View Transaction Input"
        ):

            st.dataframe(
                input_data,
                use_container_width=True
            )