# Cortex AI Budget & Usage Dashboard

A Streamlit in Snowflake (SiS) app for monitoring and controlling costs across all Snowflake Cortex AI services.

## Features

### Usage Monitoring (8 tabs)

| Tab | Data Source | Key Metrics |
|-----|------------|-------------|
| **Cost Summary** | All 7 usage views | Donut chart, stacked area trend, per-service breakdown |
| **LLM Functions** | `CORTEX_AI_FUNCTIONS_USAGE_HISTORY` | Credits by model/function/user, input/output tokens |
| **Cortex Analyst** | `CORTEX_ANALYST_USAGE_HISTORY` | Credits, request count, daily trend |
| **Search Services** | `CORTEX_SEARCH_SERVING_USAGE_HISTORY` | Credits by service, daily trend |
| **Snowflake Intelligence** | `SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY` | Credits, tokens, by SI instance/user |
| **Cortex Agents** | `CORTEX_AGENT_USAGE_HISTORY` | Credits, tokens, by agent/user |
| **Cortex Code** | `CORTEX_CODE_CLI_USAGE_HISTORY` + `CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY` | Combined CLI + Snowsight credits, tokens, by user |
| **Long-running LLM** | `CORTEX_AI_FUNCTIONS_USAGE_HISTORY` | Multi-window query detection, duration distribution |

### Cost Controls (1 tab, 3 sections)

**AI Functions Cost Control**
- Account-level monthly spending alerts (notification integration + hourly alert)
- Per-user monthly spending limits (RBAC-based access control with hourly enforcement)
- Runaway query detection and cancellation (auto-cancel + email alert)

**Cortex Code Cost Control**
- View current account-level and per-user daily credit limits
- Set account-level defaults (`CORTEX_CODE_CLI_DAILY_EST_CREDIT_LIMIT_PER_USER`, `CORTEX_CODE_SNOWSIGHT_DAILY_EST_CREDIT_LIMIT_PER_USER`)
- Set per-user overrides (always takes precedence over account default)
- Remove per-user overrides to revert to account default

**Cortex Agent Resource Budgets**
- Tag creation and application to Cortex Agent objects
- Budget creation with `SNOWFLAKE.CORE.BUDGET`
- Threshold actions (notify at %, revoke access at %, reinstate on cycle start)
- Usage monitoring and custom action listing

### Dual Pricing Model

| Credit Type | Default Rate | Applies To |
|-------------|-------------|------------|
| Standard credit | $3.40 | AI Functions, Cortex Analyst, Cortex Search |
| AI credit | $2.00 (global) / $2.20 (regional) | Cortex Code, Snowflake Intelligence, Cortex Agents |

Both rates are configurable via sidebar sliders.

## Prerequisites

- Snowflake account with `ACCOUNTADMIN` role (or equivalent privileges)
- Access to `SNOWFLAKE.ACCOUNT_USAGE` views
- Streamlit in Snowflake (SiS) enabled

## Deployment

1. Upload `cortex_ai_budget_dashboard.py` to a Snowflake stage
2. Create a Streamlit app in Snowsight pointing to the staged file
3. Grant the app access to `SNOWFLAKE.ACCOUNT_USAGE`

## Data Sources

All data comes from `SNOWFLAKE.ACCOUNT_USAGE` views with up to 60 minutes of latency. No custom tables are required for the monitoring tabs. The Cost Controls tab generates SQL to create supporting objects (tables, procedures, tasks, alerts) on demand.

### Important: METERING_HISTORY vs Individual Usage Views

The `METERING_HISTORY` view contains an `AI_SERVICES` service type bucket that **partially overlaps** with separate `CORTEX_CODE_CLI`, `CORTEX_AGENTS`, and `CORTEX_CODE_SNOWSIGHT` rows. Summing `AI_SERVICES` + `CORTEX_*` from `METERING_HISTORY` will **double-count** credits. This dashboard queries the 7 individual `*_USAGE_HISTORY` views instead to get accurate totals.

### Note: CORTEX_REST_API_USAGE_HISTORY (not covered)

`SNOWFLAKE.ACCOUNT_USAGE.CORTEX_REST_API_USAGE_HISTORY` tracks usage from the Cortex REST API endpoint (e.g., direct HTTP calls to `/api/v2/cortex/inference:complete`). This view is **not currently covered** by the dashboard because it follows a different cost model:

| Attribute | Detail |
|-----------|--------|
| **Credit column** | None — the view has no `CREDITS` column. Cost must be estimated as `$ / 1,000,000 tokens`, varying by model and region |
| **Credit type** | $ per one million tokens (varies by model and region) |
| **Key columns** | `START_TIME`, `END_TIME`, `REQUEST_ID`, `MODEL_NAME`, `TOKENS`, `TOKENS_GRANULAR`, `USER_ID`, `INFERENCE_REGION` |
| **Token breakdown** | `TOKENS_GRANULAR` is a semi-structured OBJECT with `input`, `output`, and optionally `cache_read_input` keys |
| **User column** | `USER_ID` only — requires `LEFT JOIN` to `SNOWFLAKE.ACCOUNT_USAGE.USERS` to resolve usernames |

REST API credits are small in volume for most accounts but may be significant for customers using the Cortex Inference REST API programmatically at scale.

**Screenshots**

<img width="1580" height="807" alt="image" src="https://github.com/user-attachments/assets/2c691b2c-e133-4843-a195-f41fab4f21f9" />

<img width="1567" height="746" alt="image" src="https://github.com/user-attachments/assets/a5da283e-1806-4bb6-b998-98eba047d224" />

<img width="1592" height="653" alt="image" src="https://github.com/user-attachments/assets/ce03a712-3d82-4975-a93b-689538f6027a" />

<img width="1575" height="791" alt="image" src="https://github.com/user-attachments/assets/17b36cd7-6cad-4329-ac84-e5a0c220478c" />

<img width="1577" height="733" alt="image" src="https://github.com/user-attachments/assets/c7663684-b024-4c1d-bb6a-207e2d8dc618" />






