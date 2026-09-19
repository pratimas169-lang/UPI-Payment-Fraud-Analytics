# UPI Payment & Fraud Analytics

## Project Overview

This project analyzes UPI transaction activity and fraud patterns using transaction, user, merchant and fraud-label data.

The project covers data quality validation, data cleaning, feature engineering, descriptive analytics, diagnostic analytics, predictive fraud modelling and prescriptive risk-based actions.

## Business Problem

UPI payment platforms generate large volumes of transactions and need effective ways to monitor transaction activity and identify potentially fraudulent behaviour.

This project analyzes transaction patterns and key risk indicators such as new devices, IP-location mismatch, failed attempts, transaction velocity and amount deviation to support fraud monitoring and decision-making.

## Business Objectives

- Analyze overall UPI transaction performance.
- Identify fraud patterns across users, payment apps, devices, time and merchants.
- Identify important transaction-level risk indicators.
- Develop a predictive model for fraud detection.
- Convert fraud probabilities into risk-based business actions.
- Build interactive dashboards and an analytical application.

## Dataset

The project uses four datasets:

| Dataset | Records | Description |
|---|---:|---|
| Users | 2,000 | User-level information |
| Merchants | 400 | Merchant-level information |
| Transactions | 20,000 | Transaction-level information |
| Fraud Labels | 20,000 | Fraud labels and risk indicators |

The transaction data covers the period from January 2024 to December 2024.

## Data Quality & Cleaning

Key validation and cleaning activities included:

- Duplicate transaction ID validation.
- Missing-value analysis.
- Invalid transaction amount checks.
- Fraud-label validation.
- User and merchant relationship validation.
- Date and timestamp consistency checks.
- Negative time-since-last-transaction handling.
- Missing transaction velocity handling.
- Missing amount deviation score handling.

No transactions were deleted because of these data-quality issues.

## Feature Engineering

The following analytical features were created or prepared:

- `TIME_PERIOD`
- `AMOUNT_CATEGORY`
- `CLEAN_TIME_SINCE_LAST_TXN_MIN`
- `CLEAN_TRANSACTION_VELOCITY`
- `CLEAN_AMOUNT_DEVIATION_SCORE`
- `TIME_SINCE_LAST_TXN_MISSING_FLAG`

## Descriptive Analytics

The descriptive analysis focused on overall payment performance.

Key areas:

- Transaction volume and value
- Transaction trends over time
- Payment app activity
- Device distribution
- Transaction status

## Diagnostic Analytics

The diagnostic analysis focused on identifying fraud-related patterns.

Key areas:

- Fraud trend over time
- Fraud rate by payment app
- Fraud distribution by device type
- Fraud transactions by hour
- New device activity
- IP-location mismatch
- Failed attempts
- Transaction velocity
- Amount deviation

## Predictive Analytics

A Random Forest Classifier was developed in Databricks using transaction behaviour and risk-related features.

### Target Variable

`IS_FRAUD`

### Features

- `AMOUNT`
- `HOUR_OF_DAY`
- `IS_WEEKEND`
- `IS_NIGHT_TRANSACTION`
- `NEW_DEVICE_FLAG`
- `IP_LOCATION_MISMATCH`
- `FAILED_ATTEMPTS_LAST_24H`
- `TRANSACTION_VELOCITY`
- `AMOUNT_DEVIATION_SCORE`

### Model Evaluation

| Metric | Result |
|---|---:|
| Precision | 0.0000 |
| Recall | 0.0000 |
| F1-Score | 0.9515 |
| ROC-AUC | 0.7339 |

These are the evaluation results obtained during the Databricks model run.

## Prescriptive Analytics

Fraud probability was converted into operational risk levels using business-defined thresholds:

| Fraud Probability | Risk Level | Action |
|---|---|---|
| < 30% | Low Risk | Normal Processing |
| 30%–70% | Medium Risk | Additional Verification |
| > 70% | High Risk | Flag for Investigation |

These thresholds are business rules and were not learned automatically by the model.

## Power BI Dashboards

### Dashboard 1 — UPI Executive & Transaction Overview

Focus:
- Transaction performance
- Payment app activity
- Device distribution
- Transaction status
- Transaction trends

### Dashboard 2 — Fraud & Risk Analysis

Focus:
- Fraudulent transactions
- Fraud transaction value
- Fraud trends
- Payment-app fraud rate
- Device-level fraud
- Hourly fraud activity
- Risk indicators

### Dashboard 3 — User, Merchant & Segment Analysis

Focus:
- User activity by age group
- Merchant category activity
- High-risk users by city tier
- Merchant-size fraud rate
- User and merchant KPIs

## Streamlit Application

The Streamlit application contains four sections:

1. Executive Overview
2. Fraud & Risk
3. User, Merchant & Segmentation
4. Fraud Prediction & Action

The application connects to Snowflake and provides interactive transaction analysis and fraud-risk prediction.

## Technology Stack

- **Excel** — Initial profiling and validation support
- **Snowflake** — Data warehouse, SQL validation and analytical queries
- **Databricks / PySpark** — Data processing, EDA, feature engineering and predictive modelling
- **Power BI** — Interactive dashboards
- **Streamlit** — Interactive analytics and fraud prediction application
- **GitHub** — Version control and project documentation
- **PPTX** — Mentor presentation

## Project Architecture

```text
Raw CSV Data
     ↓
Excel
     ↓
Databricks
(Data Cleaning + EDA + Feature Engineering + ML)
     ↓
Snowflake
(Curated Data + SQL Analysis)
     ↓
 ┌───────────────┬────────────────┐
 ↓               ↓
Power BI      Streamlit
Dashboards    Application# UPI-Payment-Fraud-Analytics
UPI Payment &amp; Fraud Analytics using Snowflake, Databricks, Power BI and Streamlit


Key Business Recommendations
Monitor fraud trends and risk indicators regularly.
Apply risk-based verification for medium- and high-risk transactions.
Monitor new-device activity, IP mismatch, failed attempts, velocity and amount deviation.
Review fraud patterns across payment apps, devices, merchants and time periods.
Improve merchant classification and data completeness.
Continue model validation and tuning before production deployment.

Project Outcome
The project combines data quality validation, analytical reporting, predictive modelling and risk-
based actions into an integrated UPI fraud analytics workflow.
