# Cortex AI Budget & Usage Dashboard

A Streamlit in Snowflake (SiS) app for monitoring and controlling costs across all Snowflake Cortex AI services.

## Features

### Usage Monitoring (9 tabs)

| Tab | Data Source | Key Metrics |
|-----|------------|-------------|
| **Cost Summary** | All views | Donut chart, stacked area trend, per-service breakdown |
| **LLM Functions** | `CORTEX_AI_FUNCTIONS_USAGE_HISTORY` | Credits by model/function/user, input/output tokens |
| **Cortex Analyst** | `CORTEX_ANALYST_USAGE_HISTORY` | Credits, request count, daily trend |
| **Cortex Search** | `CORTEX_SEARCH_SERVING_USAGE_HISTORY` | Credits by service, daily trend |
| **Intelligence** | `SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY` | Credits, tokens, by agent/user |
| **Cortex Agents** | `CORTEX_AGENT_USAGE_HISTORY` | Credits, tokens, by agent/user |
| **CoCo CLI** | `CORTEX_CODE_CLI_USAGE_HISTORY` | Credits, tokens, by user |
| **CoCo Snowsight** | `CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY` | Credits, tokens, by user |
| **Long-running LLM** | `CORTEX_AI_FUNCTIONS_USAGE_HISTORY` | Multi-window query detection, duration distribution |

### Cost Controls (1 tab, 2 sections)

**AI Functions Cost Control**
- Account-level monthly spending alerts (notification integration + hourly alert)
- Per-user monthly spending limits (RBAC-based access control with hourly enforcement)
- Runaway query detection and cancellation (auto-cancel + email alert)

**Cortex Agent Resource Budgets**
- Tag creation and application to Cortex Agent objects
- Budget creation with `SNOWFLAKE.CORE.BUDGET`
- Threshold actions (notify at %, revoke access at %, reinstate on cycle start)
- Usage monitoring and custom action listing

### Dual Pricing Model

| Credit Type | Default Rate | Applies To |
|-------------|-------------|------------|
| Standard credit | $3.40 | AI Functions, Cortex Analyst, Cortex Search, Adjust it as per your edition |
| AI credit | $2.00 (global) | Cortex Code, Snowflake Intelligence, Cortex Agents, $2.2 for Regional |

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
