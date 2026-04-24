import streamlit as st
from snowflake.snowpark.context import get_active_session
import datetime
import pandas as pd
import altair as alt

PALETTE = ["#29B5E8", "#4ECDC4", "#FF6B6B", "#FFA07A", "#A0A0A0", "#9B59B6", "#F1C40F", "#2ECC71"]
ORIGIN_COLORS = {"CLI": "#29B5E8", "Snowsight": "#11567F"}

_CARD_CSS = """
<style>
.kpi-card{background:#ffffff;border:1.5px solid #c0d8ea;border-radius:10px;
  padding:14px 12px 10px;text-align:center;min-height:80px;}
.kpi-label{color:#4a6d84;font-size:10px;font-weight:700;letter-spacing:0.6px;
  text-transform:uppercase;margin:0 0 8px;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis;}
.kpi-value{color:#153d5e;font-size:17px;font-weight:700;line-height:1.2;
  word-break:break-word;background:#d4e6f1;border-radius:6px;padding:5px 12px;
  display:inline-block;margin-top:2px;min-width:60%;}
</style>
"""
_CSS_INJECTED = False


def _inject_css():
    global _CSS_INJECTED
    if not _CSS_INJECTED:
        st.markdown(_CARD_CSS, unsafe_allow_html=True)
        _CSS_INJECTED = True


def kpi_card(label, value):
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def kpi_row(items):
    _inject_css()
    cols = st.columns(len(items))
    for col, (label, val) in zip(cols, items):
        with col:
            kpi_card(label, val)
    st.markdown('<div style="margin-bottom:1.2rem"></div>', unsafe_allow_html=True)


def _daily_bar(df, x_col, y_col, color="#29B5E8", height=280):
    return (
        alt.Chart(df)
        .mark_bar(color=color, cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(f"{x_col}:T", title="Date"),
            y=alt.Y(f"{y_col}:Q", title=y_col),
            tooltip=[alt.Tooltip(f"{x_col}:T", title="Date"),
                     alt.Tooltip(f"{y_col}:Q", format=",.4f")],
        )
        .properties(height=height)
    )


def _ctrl_banner(title, subtitle, color, icon=""):
    st.markdown(
        f'<div style="background:linear-gradient(90deg,{color}22,{color}06);'
        f'border-left:4px solid {color};border-radius:8px;padding:14px 18px;margin-bottom:1.2rem;">'
        f'<div style="font-size:19px;font-weight:700;color:{color};">{icon}&nbsp;&nbsp;{title}</div>'
        f'<div style="font-size:12px;color:#555;margin-top:5px;">{subtitle}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _step_header(n, title, color="#29B5E8"):
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:1.4rem 0 0.5rem;">'
        f'<div style="background:{color};color:#fff;border-radius:50%;min-width:26px;height:26px;'
        f'display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;'
        f'flex-shrink:0;">{n}</div>'
        f'<div style="font-weight:600;font-size:15px;color:#153d5e;">{title}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _hbar(df, cat_col, val_col, color="#29B5E8", limit=15):
    d = df.head(limit)
    h = max(120, len(d) * 26 + 40)
    return (
        alt.Chart(d)
        .mark_bar(color=color, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(f"{val_col}:Q", title=val_col),
            y=alt.Y(f"{cat_col}:N", title="", sort="-x"),
            tooltip=[f"{cat_col}:N", alt.Tooltip(f"{val_col}:Q", format=",.4f")],
        )
        .properties(height=h)
    )


st.set_page_config(
    page_title="AI Cost Control & Monitoring",
    page_icon=":snowflake:",
    layout="wide",
)

session = get_active_session()


@st.cache_data(ttl=3600, show_spinner=False)
def load_account_info(_session=None):
    s = _session or session
    return s.sql("""
        SELECT
            CURRENT_ACCOUNT_NAME()  AS ACCT,
            CURRENT_ORGANIZATION_NAME() AS ORG,
            CURRENT_REGION()        AS REGION,
            CURRENT_USER()          AS USR,
            CURRENT_ROLE()          AS ROLE
    """).to_pandas()


with st.sidebar:
    st.markdown(
        '<div style="background:linear-gradient(135deg,rgba(41,181,232,0.15) 0%,'
        'rgba(41,181,232,0.05) 100%);border:1px solid rgba(41,181,232,0.3);'
        'border-radius:10px;padding:14px 16px;margin-bottom:12px;display:flex;'
        'align-items:center;gap:10px;">'
        '<span style="font-size:22px;">\u2744\uFE0F</span>'
        '<div>'
        '<div style="color:#0d3158;font-size:15px;font-weight:700;line-height:1.2;">AI Cost Monitor</div>'
        '<div style="color:#4a7aa8;font-size:10px;font-weight:500;letter-spacing:0.4px;">SNOWFLAKE AI USAGE</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    ai = load_account_info(_session=session)
    if not ai.empty:
        r = ai.iloc[0]
        st.markdown(
            f'<div style="background:linear-gradient(160deg,#f0f9ff 0%,#e8f4fd 60%,#f0fdf4 100%);'
            f'border:1px solid #bfdbfe;border-radius:10px;padding:14px 14px 10px;margin-bottom:4px;">'
            f'<div style="font-size:10px;font-weight:700;letter-spacing:0.8px;text-transform:uppercase;'
            f'color:#64748b;margin-bottom:10px;border-bottom:1px solid #dbeafe;padding-bottom:6px;">'
            f'\U0001f5a5 Account Info</div>'
            f'<div style="display:flex;align-items:center;margin-bottom:7px;">'
            f'<span style="background:#dbeafe;color:#1d4ed8;font-size:10px;font-weight:700;'
            f'border-radius:4px;padding:2px 6px;min-width:62px;text-align:center;margin-right:8px;">Account</span>'
            f'<span style="color:#1e293b;font-family:monospace;font-size:11px;">{r["ACCT"]}</span></div>'
            f'<div style="display:flex;align-items:center;margin-bottom:7px;">'
            f'<span style="background:#dbeafe;color:#1d4ed8;font-size:10px;font-weight:700;'
            f'border-radius:4px;padding:2px 6px;min-width:62px;text-align:center;margin-right:8px;">Org</span>'
            f'<span style="color:#1e293b;font-family:monospace;font-size:11px;">{r["ORG"]}</span></div>'
            f'<div style="display:flex;align-items:center;margin-bottom:7px;">'
            f'<span style="background:#dbeafe;color:#1d4ed8;font-size:10px;font-weight:700;'
            f'border-radius:4px;padding:2px 6px;min-width:62px;text-align:center;margin-right:8px;">Region</span>'
            f'<span style="color:#1e293b;font-family:monospace;font-size:11px;">{r["REGION"]}</span></div>'
            f'<div style="display:flex;align-items:center;margin-bottom:7px;">'
            f'<span style="background:#dbeafe;color:#1d4ed8;font-size:10px;font-weight:700;'
            f'border-radius:4px;padding:2px 6px;min-width:62px;text-align:center;margin-right:8px;">User</span>'
            f'<span style="color:#1e293b;font-family:monospace;font-size:11px;">{r["USR"]}</span></div>'
            f'<div style="display:flex;align-items:center;">'
            f'<span style="background:#dbeafe;color:#1d4ed8;font-size:10px;font-weight:700;'
            f'border-radius:4px;padding:2px 6px;min-width:62px;text-align:center;margin-right:8px;">Role</span>'
            f'<span style="color:#1e293b;font-family:monospace;font-size:11px;">{r["ROLE"]}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:7px;'
        'padding:8px 10px;margin-top:6px;margin-bottom:4px;">'
        '<div style="color:#92400e;font-size:10px;font-weight:700;margin-bottom:3px;">\u23f1 Data Latency</div>'
        '<div style="color:#78350f;font-size:10px;line-height:1.45;">'
        'ACCOUNT_USAGE views have latency. Recent activity may not yet be reflected.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.divider()
    days_back = st.slider("Days back", min_value=7, max_value=180, value=30, step=1,
                          help="Number of days of usage history to load. Larger ranges may take longer to query.")
    cutoff_date = datetime.date.today() - datetime.timedelta(days=days_back)
    date_str = str(cutoff_date)

    st.divider()
    long_running_threshold = st.slider("Long-running threshold (min)", min_value=1, max_value=120, value=10, step=1,
                                        help="Queries with duration exceeding this threshold (in minutes) are flagged in the Long-running LLM tab.")

    st.caption(f"Data from last **{days_back}** days \u00b7 {date_str} \u2192 today")

    st.divider()
    st.markdown("**Cost rates**")
    COST_PER_CREDIT = st.number_input(
        "$/credit (AI Functions, Analyst, Search)",
        min_value=0.01, max_value=100.00, value=3.40, step=0.10, format="%.2f",
        help="Standard Snowflake credit price for AI Functions, Cortex Analyst, and Cortex Search",
    )
    COST_PER_AI_CREDIT = st.number_input(
        "$/AI credit (CoCo, SI, Agents)",
        min_value=0.01, max_value=100.00, value=2.00, step=0.10, format="%.2f",
        help="AI credit price for Cortex Code, Snowflake Intelligence, and Cortex Agents (global: $2.00, regional: $2.20)",
    )

SERVICE_COST_RATES = {
    "LLM functions": COST_PER_CREDIT,
    "Cortex Analyst": COST_PER_CREDIT,
    "Cortex Search": COST_PER_CREDIT,
    "Intelligence": COST_PER_AI_CREDIT,
    "Cortex Agents": COST_PER_AI_CREDIT,
    "CoCo CLI": COST_PER_AI_CREDIT,
    "CoCo Snowsight": COST_PER_AI_CREDIT,
}


@st.cache_data(ttl=600, show_spinner=False)
def load_ai_functions(date_str, _session=None):
    s = _session or session
    return s.sql(f"""
        WITH base AS (
            SELECT
                C.START_TIME, C.END_TIME, C.FUNCTION_NAME, C.MODEL_NAME,
                C.QUERY_ID, C.WAREHOUSE_ID, C.CREDITS, C.IS_COMPLETED, C.USER_ID,
                MAX(CASE WHEN F.VALUE:key:metric::STRING = 'input' THEN F.VALUE:value::NUMBER END) AS INPUT_TOKENS,
                MAX(CASE WHEN F.VALUE:key:metric::STRING = 'output' THEN F.VALUE:value::NUMBER END) AS OUTPUT_TOKENS,
                MAX(CASE WHEN F.VALUE:key:metric::STRING = 'total' THEN F.VALUE:value::NUMBER END) AS TOTAL_TOKENS_RAW
            FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY C,
                LATERAL FLATTEN(INPUT => C.METRICS, OUTER => TRUE) F
            WHERE DATE(C.START_TIME) >= '{date_str}'
            GROUP BY C.START_TIME, C.END_TIME, C.FUNCTION_NAME, C.MODEL_NAME,
                     C.QUERY_ID, C.WAREHOUSE_ID, C.CREDITS, C.IS_COMPLETED, C.USER_ID
        )
        SELECT
            B.START_TIME, B.END_TIME, B.FUNCTION_NAME, B.MODEL_NAME,
            B.QUERY_ID, B.WAREHOUSE_ID, B.CREDITS, B.IS_COMPLETED,
            U.NAME AS USERNAME,
            NVL(B.INPUT_TOKENS, NVL(B.TOTAL_TOKENS_RAW, 0)) AS INPUT_TOKENS,
            NVL(B.OUTPUT_TOKENS, 0) AS OUTPUT_TOKENS
        FROM base B
            LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS U ON B.USER_ID = U.USER_ID
    """).to_pandas()


@st.cache_data(ttl=600, show_spinner=False)
def load_analyst(date_str, _session=None):
    s = _session or session
    return s.sql(f"""
        SELECT START_TIME, END_TIME, USERNAME, CREDITS, REQUEST_COUNT
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
        WHERE DATE(START_TIME) >= '{date_str}'
        ORDER BY START_TIME DESC
    """).to_pandas()


@st.cache_data(ttl=600, show_spinner=False)
def load_search(date_str, _session=None):
    s = _session or session
    return s.sql(f"""
        SELECT START_TIME, END_TIME, DATABASE_NAME, SCHEMA_NAME, SERVICE_NAME, CREDITS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_SERVING_USAGE_HISTORY
        WHERE DATE(START_TIME) >= '{date_str}'
        ORDER BY START_TIME DESC
    """).to_pandas()


@st.cache_data(ttl=600, show_spinner=False)
def load_intelligence(date_str, _session=None):
    s = _session or session
    return s.sql(f"""
        SELECT
            START_TIME, END_TIME, USER_NAME AS USERNAME,
            SNOWFLAKE_INTELLIGENCE_NAME, AGENT_DATABASE_NAME, AGENT_SCHEMA_NAME, AGENT_NAME,
            TOKEN_CREDITS AS CREDITS, TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY
        WHERE DATE(START_TIME) >= '{date_str}'
        ORDER BY START_TIME DESC
    """).to_pandas()


@st.cache_data(ttl=600, show_spinner=False)
def load_agents(date_str, _session=None):
    s = _session or session
    return s.sql(f"""
        SELECT
            START_TIME, END_TIME, USER_NAME AS USERNAME,
            AGENT_DATABASE_NAME, AGENT_SCHEMA_NAME, AGENT_NAME,
            TOKEN_CREDITS AS CREDITS, TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
        WHERE DATE(START_TIME) >= '{date_str}'
        ORDER BY START_TIME DESC
    """).to_pandas()


@st.cache_data(ttl=600, show_spinner=False)
def load_coco_cli(date_str, _session=None):
    s = _session or session
    return s.sql(f"""
        SELECT
            C.USER_ID, U.NAME AS USERNAME, C.REQUEST_ID,
            C.USAGE_TIME AS START_TIME, C.TOKEN_CREDITS AS CREDITS, C.TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY C
            LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS U ON C.USER_ID = U.USER_ID
        WHERE DATE(C.USAGE_TIME) >= '{date_str}'
        ORDER BY C.USAGE_TIME DESC
    """).to_pandas()


@st.cache_data(ttl=600, show_spinner=False)
def load_coco_snowsight(date_str, _session=None):
    s = _session or session
    return s.sql(f"""
        SELECT
            C.USER_ID, U.NAME AS USERNAME, C.REQUEST_ID,
            C.USAGE_TIME AS START_TIME, C.TOKEN_CREDITS AS CREDITS, C.TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY C
            LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS U ON C.USER_ID = U.USER_ID
        WHERE DATE(C.USAGE_TIME) >= '{date_str}'
        ORDER BY C.USAGE_TIME DESC
    """).to_pandas()


@st.cache_data(ttl=3600, show_spinner=False)
def load_monthly_trend(_session=None):
    s = _session or session
    parts = []
    queries = [
        ("LLM Functions",            "SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY",       "START_TIME",  "CREDITS"),
        ("Cortex Analyst",           "SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY",            "START_TIME",  "CREDITS"),
        ("Search Services",          "SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_SERVING_USAGE_HISTORY",     "START_TIME",  "CREDITS"),
        ("Snowflake Intelligence",   "SNOWFLAKE.ACCOUNT_USAGE.SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY",    "START_TIME",  "TOKEN_CREDITS"),
        ("Cortex Agents",            "SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY",              "START_TIME",  "TOKEN_CREDITS"),
        ("Cortex Code (CLI)",        "SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY",           "USAGE_TIME",  "TOKEN_CREDITS"),
        ("Cortex Code (Snowsight)",  "SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY",     "USAGE_TIME",  "TOKEN_CREDITS"),
    ]
    for label, view, time_col, credit_col in queries:
        try:
            df_part = s.sql(f"""
                SELECT
                    DATE_TRUNC('month', {time_col})::DATE AS MONTH,
                    SUM({credit_col})                     AS CREDITS,
                    '{label}'                             AS SERVICE
                FROM {view}
                WHERE {time_col} >= DATEADD('month', -12, DATE_TRUNC('month', CURRENT_DATE))
                GROUP BY 1
            """).to_pandas()
            if not df_part.empty:
                parts.append(df_part)
        except Exception:
            pass
    if parts:
        return pd.concat(parts, ignore_index=True).sort_values(["MONTH", "SERVICE"])
    return pd.DataFrame(columns=["MONTH", "CREDITS", "SERVICE"])


@st.cache_data(ttl=600, show_spinner=False)
def load_long_running(date_str, _session=None):
    s = _session or session
    return s.sql(f"""
        SELECT
            C.QUERY_ID, C.FUNCTION_NAME, C.MODEL_NAME,
            U.NAME AS USERNAME,
            MIN(C.START_TIME) AS FIRST_WINDOW,
            MAX(C.END_TIME) AS LAST_WINDOW,
            COUNT(*) AS WINDOW_COUNT,
            SUM(C.CREDITS) AS TOTAL_CREDITS,
            DATEDIFF('minute', MIN(C.START_TIME), MAX(C.END_TIME)) AS DURATION_MINUTES
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY C
            LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS U ON C.USER_ID = U.USER_ID
        WHERE DATE(C.START_TIME) >= '{date_str}'
        GROUP BY C.QUERY_ID, C.FUNCTION_NAME, C.MODEL_NAME, U.NAME
        HAVING COUNT(*) > 1
        ORDER BY DURATION_MINUTES DESC
    """).to_pandas()


_load_errors = {}

def _safe_load(key, fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        _load_errors[key] = str(e)
        return pd.DataFrame()

df_llm = _safe_load("ai_functions", load_ai_functions, date_str, _session=session)
df_analyst = _safe_load("analyst", load_analyst, date_str, _session=session)
df_search = _safe_load("search", load_search, date_str, _session=session)
df_intelligence = _safe_load("intelligence", load_intelligence, date_str, _session=session)
df_agents = _safe_load("agents", load_agents, date_str, _session=session)
df_coco = _safe_load("coco_cli", load_coco_cli, date_str, _session=session)
df_coco_ss = _safe_load("coco_snowsight", load_coco_snowsight, date_str, _session=session)
df_lr = _safe_load("long_running", load_long_running, date_str, _session=session)
df_monthly = _safe_load("monthly_trend", load_monthly_trend, _session=session)

_SVC_LABELS = {
    "ai_functions": "LLM Functions", "analyst": "Cortex Analyst",
    "search": "Cortex Search", "intelligence": "Snowflake Intelligence",
    "agents": "Cortex Agents", "coco_cli": "Cortex Code CLI",
    "coco_snowsight": "Cortex Code Snowsight", "long_running": "Long-Running Queries",
}

with st.sidebar:
    if _load_errors:
        st.divider()
        with st.expander("\u26a0\ufe0f Service Availability", expanded=True):
            st.caption("Some data sources could not be loaded. "
                       "The affected tabs will show empty state.")
            for key, err in _load_errors.items():
                label = _SVC_LABELS.get(key, key)
                st.markdown(
                    f'<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:6px;'
                    f'padding:6px 10px;margin-bottom:4px;">'
                    f'<span style="color:#dc2626;font-size:11px;font-weight:700;">\u2717 {label}</span><br>'
                    f'<span style="color:#7f1d1d;font-size:10px;">{err[:120]}{"…" if len(err) > 120 else ""}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
    else:
        st.divider()
        st.markdown(
            '<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:7px;'
            'padding:8px 10px;">'
            '<span style="color:#16a34a;font-size:11px;font-weight:700;">\u2713 All services loaded</span>'
            '</div>',
            unsafe_allow_html=True,
        )

st.title(":snowflake: AI Cost Control & Monitoring")
_total_cr = sum([
    df_llm["CREDITS"].sum() if not df_llm.empty else 0,
    df_analyst["CREDITS"].sum() if not df_analyst.empty else 0,
    df_search["CREDITS"].sum() if not df_search.empty else 0,
    df_intelligence["CREDITS"].sum() if not df_intelligence.empty else 0,
    df_agents["CREDITS"].sum() if not df_agents.empty else 0,
    df_coco["CREDITS"].sum() if not df_coco.empty else 0,
    df_coco_ss["CREDITS"].sum() if not df_coco_ss.empty else 0,
])
st.caption(
    f"Period: last **{days_back}** days ({date_str} \u2192 today)  \u00b7  "
    f"Total credits: **{_total_cr:,.2f}**"
)

tab_summary, tab_llm, tab_analyst, tab_search, tab_intelligence, tab_agents, tab_coco, tab_long, tab_controls = st.tabs([
    "\U0001f4ca Cost Summary",
    "\U0001f9e0 LLM Functions",
    "\U0001f4c8 Cortex Analyst",
    "\U0001f50e Search Services",
    "\U0001f52e Snowflake Intelligence",
    "\U0001f916 Cortex Agents",
    "\u27e8\u27e9 Cortex Code",
    "\u23f1 Long-running LLM",
    "\u2b55 Cost Controls",
])


def safe_credits(frame, col="CREDITS"):
    return frame[col].sum() if not frame.empty else 0


def render_service_tab(frame, credit_col="CREDITS", token_col=None, user_col="USERNAME",
                       detail_cols=None, title="", cost_rate=None,
                       extra_summaries=None):
    if frame.empty:
        st.info(f"No {title} usage found for the selected period.")
        return

    rate = cost_rate if cost_rate is not None else SERVICE_COST_RATES.get(title, COST_PER_CREDIT)
    frame = frame.copy()
    frame["DATE"] = pd.to_datetime(frame["START_TIME"]).dt.date
    credits = frame[credit_col].sum()
    cost = credits * rate

    kpi_values = [
        ("Credits", f"{credits:,.6f}"),
        ("Estimated cost", f"${cost:,.2f}"),
    ]
    if token_col and token_col in frame.columns:
        kpi_values.append(("Tokens", f"{int(frame[token_col].sum()):,}"))
    if user_col and user_col in frame.columns:
        kpi_values.append(("Unique users", f"{frame[user_col].nunique()}"))

    kpi_row(kpi_values)

    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.subheader("Daily credits")
            daily = frame.groupby("DATE")[credit_col].sum().reset_index()
            daily.columns = ["Date", "Credits"]
            st.altair_chart(_daily_bar(daily, "Date", "Credits"), use_container_width=True)
    with col2:
        if user_col and user_col in frame.columns:
            with st.container():
                st.subheader("Credits by user")
                by_user = frame.groupby(user_col)[credit_col].sum().reset_index()
                by_user.columns = ["User", "Credits"]
                by_user = by_user.sort_values("Credits", ascending=False)
                st.altair_chart(_hbar(by_user, "User", "Credits"), use_container_width=True)

    if token_col and token_col in frame.columns:
        with st.container():
            st.subheader("Daily tokens")
            daily_tok = frame.groupby("DATE")[token_col].sum().reset_index()
            daily_tok.columns = ["Date", "Tokens"]
            st.altair_chart(_daily_bar(daily_tok, "Date", "Tokens"), use_container_width=True)

    if extra_summaries:
        extra_charts = [(s_display, s_col) for s_label, s_col, s_display in extra_summaries if s_col != user_col]
        if extra_charts:
            extra_cols = st.columns(len(extra_charts))
            for i, (s_display, s_col) in enumerate(extra_charts):
                with extra_cols[i]:
                    with st.container():
                        st.subheader(f"Credits by {s_display.lower()}")
                        by_grp = frame.groupby(s_col)[credit_col].sum().reset_index()
                        by_grp.columns = [s_display, "Credits"]
                        by_grp = by_grp.sort_values("Credits", ascending=False)
                        st.altair_chart(_hbar(by_grp, s_display, "Credits"), use_container_width=True)

    view_options = ["Summary by day"]
    summary_map = {}
    if extra_summaries:
        for s_label, s_col, s_display in extra_summaries:
            view_options.append(s_label)
            summary_map[s_label] = (s_col, s_display)
    view_options.append("Raw data")

    view = st.radio(f"View", view_options, horizontal=True, key=f"svc_view_{title}")
    if view == "Summary by day":
        agg = {"Credits": (credit_col, "sum")}
        if token_col and token_col in frame.columns:
            agg["Tokens"] = (token_col, "sum")
        summary = frame.groupby("DATE").agg(**agg).reset_index()
        summary.rename(columns={"DATE": "Date"}, inplace=True)
        st.dataframe(
            summary.sort_values("Date", ascending=False),
            column_config={"Credits": st.column_config.NumberColumn(format="%.6f")},
            hide_index=True, use_container_width=True,
        )
    elif view in summary_map:
        s_col, s_display = summary_map[view]
        agg = {"Credits": (credit_col, "sum")}
        if token_col and token_col in frame.columns:
            agg["Tokens"] = (token_col, "sum")
        summary = frame.groupby(s_col).agg(**agg).reset_index()
        summary.rename(columns={s_col: s_display}, inplace=True)
        st.dataframe(
            summary.sort_values("Credits", ascending=False),
            column_config={"Credits": st.column_config.NumberColumn(format="%.6f")},
            hide_index=True, use_container_width=True,
        )
    elif view == "Raw data":
        show_cols = detail_cols or [c for c in frame.columns if c != "DATE"]
        st.dataframe(
            frame[show_cols].sort_values("START_TIME", ascending=False),
            column_config={credit_col: st.column_config.NumberColumn(format="%.6f")},
            hide_index=True, use_container_width=True,
        )


with tab_summary:
    llm_credits = safe_credits(df_llm)
    analyst_credits = safe_credits(df_analyst)
    search_credits = safe_credits(df_search)
    intelligence_credits = safe_credits(df_intelligence)
    agents_credits = safe_credits(df_agents)
    coco_credits = safe_credits(df_coco)
    coco_ss_credits = safe_credits(df_coco_ss)
    total_credits = llm_credits + analyst_credits + search_credits + intelligence_credits + agents_credits + coco_credits + coco_ss_credits
    total_cost = (
        (llm_credits + analyst_credits + search_credits) * COST_PER_CREDIT
        + (intelligence_credits + agents_credits + coco_credits + coco_ss_credits) * COST_PER_AI_CREDIT
    )

    active_svc = sum([
        llm_credits > 0, analyst_credits > 0, search_credits > 0,
        intelligence_credits > 0, agents_credits > 0, (coco_credits + coco_ss_credits) > 0,
    ])

    kpi_row([
        ("Total Credits",     f"{total_credits:,.2f}"),
        ("Estimated Cost",    f"${total_cost:,.2f}"),
        ("Active Services",   f"{active_svc} / 6"),
        ("LLM Functions",     f"{llm_credits:,.2f}"),
        ("Cortex Code",       f"{(coco_credits + coco_ss_credits):,.2f}"),
        ("Cortex Agents",     f"{agents_credits:,.2f}"),
        ("Snowflake Intel",   f"{intelligence_credits:,.2f}"),
        ("Search + Analyst",  f"{(search_credits + analyst_credits):,.2f}"),
    ])

    st.markdown("#### Service presence")
    svc_presence = {
        "LLM Functions":          llm_credits > 0,
        "Cortex Analyst":         analyst_credits > 0,
        "Search Services":        search_credits > 0,
        "Snowflake Intelligence": intelligence_credits > 0,
        "Cortex Agents":          agents_credits > 0,
        "Cortex Code":            (coco_credits + coco_ss_credits) > 0,
    }
    pres_cols = st.columns(len(svc_presence))
    for col, (svc, active) in zip(pres_cols, svc_presence.items()):
        with col:
            if active:
                st.markdown(
                    f'<div style="background:rgba(46,204,113,0.12);border:1px solid '
                    f'rgba(46,204,113,0.35);border-radius:8px;padding:12px 8px;'
                    f'text-align:center;height:72px;display:flex;align-items:center;'
                    f'justify-content:center;gap:8px;">'
                    f'<span style="color:#16a34a;font-size:18px;font-weight:700;">✓</span>'
                    f'<span style="color:#14532d;font-size:12px;font-weight:600;">{svc}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="background:#f3f4f6;border:1px solid #d1d5db;'
                    f'border-radius:8px;padding:12px 8px;'
                    f'text-align:center;height:72px;display:flex;align-items:center;'
                    f'justify-content:center;">'
                    f'<span style="color:#9ca3af;font-size:12px;font-weight:500;">{svc}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("")

    if not df_monthly.empty:
        with st.container():
            st.subheader("Monthly AI services cost trend — last 12 months")
            df_m = df_monthly.copy()
            df_m["MONTH"] = pd.to_datetime(df_m["MONTH"])
            df_m["_MonthLabel"] = df_m["MONTH"].dt.strftime("%b %Y")
            month_order = (
                df_m[["MONTH", "_MonthLabel"]].drop_duplicates()
                .sort_values("MONTH")["_MonthLabel"].tolist()
            )
            _PALETTE = PALETTE
            color_domain = sorted(df_m["SERVICE"].unique().tolist())
            monthly_chart = (
                alt.Chart(df_m)
                .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
                .encode(
                    x=alt.X("_MonthLabel:O", title="", sort=month_order,
                            axis=alt.Axis(labelAngle=-30, labelFontSize=11)),
                    y=alt.Y("CREDITS:Q", title="Credits", stack="zero"),
                    color=alt.Color(
                        "SERVICE:N",
                        scale=alt.Scale(domain=color_domain, range=_PALETTE[:len(color_domain)]),
                        legend=alt.Legend(orient="top", columns=4),
                    ),
                    tooltip=[
                        alt.Tooltip("_MonthLabel:O", title="Month"),
                        alt.Tooltip("SERVICE:N", title="Service"),
                        alt.Tooltip("CREDITS:Q", title="Credits", format=",.4f"),
                    ],
                )
                .properties(height=340)
            )
            st.altair_chart(monthly_chart, use_container_width=True)

    svc_data = pd.DataFrame({
        "Service": ["LLM functions", "Cortex Analyst", "Cortex Search", "Intelligence", "Cortex Agents", "CoCo CLI", "CoCo Snowsight"],
        "Credits": [llm_credits, analyst_credits, search_credits, intelligence_credits, agents_credits, coco_credits, coco_ss_credits],
    })
    svc_data = svc_data[svc_data["Credits"] > 0].sort_values("Credits", ascending=False)

    col_pie, col_trend = st.columns(2)
    with col_pie:
        with st.container():
            st.subheader("Credits by service")
            if not svc_data.empty:
                _pie_domain = svc_data["Service"].tolist()
                _pie_range  = PALETTE[:len(_pie_domain)]
                pie = alt.Chart(svc_data).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta("Credits:Q"),
                    color=alt.Color("Service:N", scale=alt.Scale(domain=_pie_domain, range=_pie_range)),
                    tooltip=["Service:N", alt.Tooltip("Credits:Q", format=".6f")],
                ).properties(height=300)
                st.altair_chart(pie, use_container_width=True)

    with col_trend:
        with st.container():
            st.subheader("Daily credits across all services")
            frames = []
            for label, frame, cc in [
                ("LLM functions", df_llm, "CREDITS"),
                ("Cortex Analyst", df_analyst, "CREDITS"),
                ("Cortex Search", df_search, "CREDITS"),
                ("Intelligence", df_intelligence, "CREDITS"),
                ("Cortex Agents", df_agents, "CREDITS"),
                ("CoCo CLI", df_coco, "CREDITS"),
                ("CoCo Snowsight", df_coco_ss, "CREDITS"),
            ]:
                if not frame.empty:
                    tmp = frame.copy()
                    tmp["DATE"] = pd.to_datetime(tmp["START_TIME"]).dt.date
                    agg = tmp.groupby("DATE")[cc].sum().reset_index()
                    agg.columns = ["Date", "Credits"]
                    agg["Service"] = label
                    frames.append(agg)
            if frames:
                combined = pd.concat(frames, ignore_index=True)
                _area_domain = combined["Service"].unique().tolist()
                _area_range  = PALETTE[:len(_area_domain)]
                area = alt.Chart(combined).mark_area(opacity=0.7).encode(
                    x=alt.X("Date:T"),
                    y=alt.Y("Credits:Q", stack=True),
                    color=alt.Color("Service:N", scale=alt.Scale(domain=_area_domain, range=_area_range)),
                    tooltip=["Date:T", "Service:N", alt.Tooltip("Credits:Q", format=".6f")],
                ).properties(height=300)
                st.altair_chart(area, use_container_width=True)

    with st.container():
        st.subheader("Credits breakdown")
        svc_data["Cost (USD)"] = svc_data["Service"].map(SERVICE_COST_RATES).fillna(COST_PER_CREDIT) * svc_data["Credits"]
        svc_data["Share (%)"] = ((svc_data["Cost (USD)"] / svc_data["Cost (USD)"].sum() * 100).round(1))/100
        st.dataframe(
            svc_data,
            column_config={
                "Credits": st.column_config.NumberColumn(format="%.6f"),
                "Cost (USD)": st.column_config.NumberColumn(format="$%.2f"),
                "Share (%)": st.column_config.ProgressColumn(min_value=0, max_value=100),
            },
            hide_index=True, use_container_width=True,
        )

    user_frames = []
    for label, frame, user_col in [
        ("LLM Functions",          df_llm,          "USERNAME"),
        ("Cortex Analyst",         df_analyst,       "USERNAME"),
        ("Snowflake Intelligence", df_intelligence,  "USERNAME"),
        ("Cortex Agents",          df_agents,        "USERNAME"),
        ("CoCo CLI",               df_coco,          "USERNAME"),
        ("CoCo Snowsight",         df_coco_ss,       "USERNAME"),
    ]:
        if not frame.empty and user_col in frame.columns:
            agg = frame.groupby(user_col).size().reset_index(name="ACTIVITY")
            agg.columns = ["USER", "ACTIVITY"]
            agg["Feature"] = label
            user_frames.append(agg)

    if user_frames:
        with st.container():
            st.subheader("Cross-feature user activity heatmap")
            cross = pd.concat(user_frames, ignore_index=True)
            pivot = cross.pivot_table(
                index="USER", columns="Feature", values="ACTIVITY", fill_value=0, aggfunc="sum"
            )
            pivot["TOTAL"] = pivot.sum(axis=1)
            pivot = pivot.sort_values("TOTAL", ascending=False).drop(columns="TOTAL").head(25)
            melted = pivot.reset_index().melt(id_vars="USER", var_name="Feature", value_name="Activity")
            users_s = pivot.index.tolist()
            feats_s = pivot.columns.tolist()
            _max_act = float(melted["Activity"].max()) if not melted.empty else 1.0
            _txt_thresh = _max_act * 0.35
            heatmap = (
                alt.Chart(melted)
                .mark_rect(cornerRadius=3)
                .encode(
                    x=alt.X("Feature:N", title="", sort=feats_s),
                    y=alt.Y("USER:N", title="", sort=users_s),
                    color=alt.condition(
                        alt.datum.Activity > 0,
                        alt.Color("Activity:Q", scale=alt.Scale(scheme="blues")),
                        alt.value("#f0f2f5"),
                    ),
                    tooltip=[alt.Tooltip("USER:N"), alt.Tooltip("Feature:N"), alt.Tooltip("Activity:Q")],
                )
                .properties(height=min(600, len(users_s) * 26 + 60))
            )
            text_lyr = (
                alt.Chart(melted[melted["Activity"] > 0])
                .mark_text(fontSize=10)
                .encode(
                    x=alt.X("Feature:N", sort=feats_s),
                    y=alt.Y("USER:N", sort=users_s),
                    text=alt.Text("Activity:Q", format=","),
                    color=alt.condition(
                        alt.datum.Activity > _txt_thresh,
                        alt.value("white"),
                        alt.value("#0d3158"),
                    ),
                )
            )
            st.altair_chart(heatmap + text_lyr, use_container_width=True)
            st.caption("Rows = users · Columns = AI features · Intensity = activity count")


with tab_llm:
    if df_llm.empty:
        st.info("No LLM function usage found for the selected period.")
    else:
        df_llm_view = df_llm.copy()
        df_llm_view["DATE"] = pd.to_datetime(df_llm_view["START_TIME"]).dt.date
        df_llm_view["TOTAL_TOKENS"] = df_llm_view["INPUT_TOKENS"] + df_llm_view["OUTPUT_TOKENS"]

        total_credits = df_llm_view["CREDITS"].sum()
        total_cost = total_credits * SERVICE_COST_RATES["LLM functions"]

        kpi_row([
            ("Credits",       f"{total_credits:,.2f}"),
            ("Estimated Cost", f"${total_cost:,.2f}"),
            ("Input Tokens",  f"{int(df_llm_view['INPUT_TOKENS'].sum()):,}"),
            ("Output Tokens", f"{int(df_llm_view['OUTPUT_TOKENS'].sum()):,}"),
            ("Unique Users",  f"{df_llm_view['USERNAME'].nunique():,}"),
        ])

        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                st.subheader("Daily credits")
                daily = df_llm_view.groupby("DATE")["CREDITS"].sum().reset_index()
                daily.columns = ["Date", "Credits"]
                st.altair_chart(_daily_bar(daily, "Date", "Credits", "#29B5E8"), use_container_width=True)
        with col2:
            with st.container():
                st.subheader("Credits by function")
                by_func = df_llm_view.groupby("FUNCTION_NAME")["CREDITS"].sum().reset_index()
                by_func.columns = ["Function", "Credits"]
                by_func = by_func.sort_values("Credits", ascending=False)
                st.altair_chart(_hbar(by_func, "Function", "Credits", "#FF6B6B"), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            with st.container():
                st.subheader("Credits by model")
                by_model = df_llm_view.groupby("MODEL_NAME")["CREDITS"].sum().reset_index()
                by_model.columns = ["Model", "Credits"]
                by_model = by_model.sort_values("Credits", ascending=False)
                st.altair_chart(_hbar(by_model, "Model", "Credits", "#4ECDC4"), use_container_width=True)
        with col4:
            with st.container():
                st.subheader("Credits by user")
                by_user = df_llm_view.groupby("USERNAME")["CREDITS"].sum().reset_index()
                by_user.columns = ["User", "Credits"]
                by_user = by_user.sort_values("Credits", ascending=False)
                st.altair_chart(_hbar(by_user, "User", "Credits", "#FFA07A"), use_container_width=True)

        with st.container():
            st.subheader("Daily trend by model")
            trend = df_llm_view.groupby(["DATE", "MODEL_NAME"])["CREDITS"].sum().reset_index()
            trend.columns = ["Date", "Model", "Credits"]
            _model_domain = trend["Model"].unique().tolist()
            _model_range  = PALETTE[:len(_model_domain)]
            chart = alt.Chart(trend).mark_area(opacity=0.7).encode(
                x=alt.X("Date:T", title="Date"),
                y=alt.Y("Credits:Q", title="Credits", stack=True),
                color=alt.Color("Model:N", scale=alt.Scale(domain=_model_domain, range=_model_range)),
                tooltip=["Date:T", "Model:N", alt.Tooltip("Credits:Q", format=".6f")],
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)

        view = st.radio("View", ["Summary by day", "Summary by user", "Summary by model", "Summary by function", "Raw data"], horizontal=True, key="llm_view")
        if view == "Summary by day":
            summary = df_llm_view.groupby("DATE").agg(
                Credits=("CREDITS", "sum"), Input_tokens=("INPUT_TOKENS", "sum"),
                Output_tokens=("OUTPUT_TOKENS", "sum"), Queries=("QUERY_ID", "nunique"),
            ).reset_index()
            summary.columns = ["Date", "Credits", "Input tokens", "Output tokens", "Queries"]
            st.dataframe(summary.sort_values("Date", ascending=False),
                         column_config={"Credits": st.column_config.NumberColumn(format="%.6f")},
                         hide_index=True, use_container_width=True)
        elif view == "Summary by user":
            summary = df_llm_view.groupby("USERNAME").agg(
                Credits=("CREDITS", "sum"), Total_tokens=("TOTAL_TOKENS", "sum"), Queries=("QUERY_ID", "nunique"),
            ).reset_index()
            summary.columns = ["User", "Credits", "Total tokens", "Queries"]
            st.dataframe(summary.sort_values("Credits", ascending=False),
                         column_config={"Credits": st.column_config.NumberColumn(format="%.6f")},
                         hide_index=True, use_container_width=True)
        elif view == "Summary by model":
            summary = df_llm_view.groupby("MODEL_NAME").agg(
                Credits=("CREDITS", "sum"), Input_tokens=("INPUT_TOKENS", "sum"),
                Output_tokens=("OUTPUT_TOKENS", "sum"), Queries=("QUERY_ID", "nunique"),
            ).reset_index()
            summary.columns = ["Model", "Credits", "Input tokens", "Output tokens", "Queries"]
            st.dataframe(summary.sort_values("Credits", ascending=False),
                         column_config={"Credits": st.column_config.NumberColumn(format="%.6f")},
                         hide_index=True, use_container_width=True)
        elif view == "Summary by function":
            summary = df_llm_view.groupby("FUNCTION_NAME").agg(
                Credits=("CREDITS", "sum"), Total_tokens=("TOTAL_TOKENS", "sum"), Queries=("QUERY_ID", "nunique"),
            ).reset_index()
            summary.columns = ["Function", "Credits", "Total tokens", "Queries"]
            st.dataframe(summary.sort_values("Credits", ascending=False),
                         column_config={"Credits": st.column_config.NumberColumn(format="%.6f")},
                         hide_index=True, use_container_width=True)
        else:
            st.dataframe(
                df_llm_view[["DATE", "FUNCTION_NAME", "MODEL_NAME", "USERNAME", "INPUT_TOKENS", "OUTPUT_TOKENS", "CREDITS"]].sort_values("DATE", ascending=False),
                column_config={"CREDITS": st.column_config.NumberColumn(format="%.6f")},
                hide_index=True, use_container_width=True)


with tab_analyst:
    render_service_tab(
        df_analyst, credit_col="CREDITS", user_col="USERNAME",
        detail_cols=["START_TIME", "USERNAME", "CREDITS", "REQUEST_COUNT"],
        title="Cortex Analyst",
        extra_summaries=[("Summary by user", "USERNAME", "User")],
    )


with tab_search:
    if df_search.empty:
        st.info("No Cortex Search usage found for the selected period.")
    else:
        df_s = df_search.copy()
        df_s["DATE"] = pd.to_datetime(df_s["START_TIME"]).dt.date
        credits = df_s["CREDITS"].sum()
        cost = credits * SERVICE_COST_RATES["Cortex Search"]

        kpi_row([
            ("Credits",  f"{credits:,.2f}"),
            ("Estimated Cost", f"${cost:,.2f}"),
            ("Services", f"{df_s['SERVICE_NAME'].nunique():,}"),
        ])

        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                st.subheader("Daily credits")
                daily = df_s.groupby("DATE")["CREDITS"].sum().reset_index()
                daily.columns = ["Date", "Credits"]
                st.altair_chart(_daily_bar(daily, "Date", "Credits", "#F39C12"), use_container_width=True)
        with col2:
            with st.container():
                st.subheader("Credits by service")
                by_svc = df_s.groupby("SERVICE_NAME")["CREDITS"].sum().reset_index()
                by_svc.columns = ["Service", "Credits"]
                by_svc = by_svc.sort_values("Credits", ascending=False)
                st.altair_chart(_hbar(by_svc, "Service", "Credits", "#E67E22"), use_container_width=True)

        view = st.radio("View", ["Summary by day", "Summary by service", "Raw data"], horizontal=True, key="search_view")
        if view == "Summary by day":
            summary = df_s.groupby("DATE").agg(Credits=("CREDITS", "sum")).reset_index()
            summary.columns = ["Date", "Credits"]
            st.dataframe(summary.sort_values("Date", ascending=False),
                         column_config={"Credits": st.column_config.NumberColumn(format="%.6f")},
                         hide_index=True, use_container_width=True)
        elif view == "Summary by service":
            summary = df_s.groupby("SERVICE_NAME").agg(Credits=("CREDITS", "sum")).reset_index()
            summary.columns = ["Service", "Credits"]
            st.dataframe(summary.sort_values("Credits", ascending=False),
                         column_config={"Credits": st.column_config.NumberColumn(format="%.6f")},
                         hide_index=True, use_container_width=True)
        else:
            st.dataframe(df_s[["START_TIME", "DATABASE_NAME", "SCHEMA_NAME", "SERVICE_NAME", "CREDITS"]].sort_values("START_TIME", ascending=False),
                         column_config={"CREDITS": st.column_config.NumberColumn(format="%.6f")},
                         hide_index=True, use_container_width=True)


with tab_intelligence:
    if df_intelligence.empty:
        st.info("No Snowflake Intelligence usage found for the selected period.")
    else:
        df_si = df_intelligence.copy()
        df_si["DATE"] = pd.to_datetime(df_si["START_TIME"]).dt.date
        si_credits = df_si["CREDITS"].sum()
        si_cost = si_credits * SERVICE_COST_RATES["Intelligence"]
        si_tokens = df_si["TOKENS"].sum() if "TOKENS" in df_si.columns else 0
        si_users = df_si["USERNAME"].nunique()
        si_names = df_si["SNOWFLAKE_INTELLIGENCE_NAME"].nunique() if "SNOWFLAKE_INTELLIGENCE_NAME" in df_si.columns else 0

        kpi_row([
            ("Credits",      f"{si_credits:,.2f}"),
            ("Estimated Cost", f"${si_cost:,.2f}"),
            ("Total Tokens", f"{int(si_tokens):,}"),
            ("Unique Users", f"{si_users:,}"),
            ("SI Objects",   f"{si_names:,}"),
        ])

        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                st.subheader("Daily credits")
                daily = df_si.groupby("DATE")["CREDITS"].sum().reset_index()
                daily.columns = ["Date", "Credits"]
                st.altair_chart(_daily_bar(daily, "Date", "Credits", "#FF6B6B"), use_container_width=True)
        with col2:
            with st.container():
                st.subheader("Distribution by agent")
                if "AGENT_NAME" in df_si.columns:
                    by_agent = df_si.groupby("AGENT_NAME")["CREDITS"].sum().reset_index()
                    by_agent.columns = ["Agent", "Credits"]
                    by_agent = by_agent[by_agent["Credits"] > 0].sort_values("Credits", ascending=False)
                    if not by_agent.empty:
                        _agent_domain = by_agent["Agent"].tolist()
                        _agent_range  = PALETTE[:len(_agent_domain)]
                        donut = alt.Chart(by_agent).mark_arc(innerRadius=50).encode(
                            theta=alt.Theta("Credits:Q"),
                            color=alt.Color("Agent:N", scale=alt.Scale(domain=_agent_domain, range=_agent_range)),
                            tooltip=["Agent:N", alt.Tooltip("Credits:Q", format=".6f")],
                        ).properties(height=260)
                        st.altair_chart(donut, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            with st.container():
                st.subheader("Credits by user")
                by_user = df_si.groupby("USERNAME")["CREDITS"].sum().reset_index()
                by_user.columns = ["User", "Credits"]
                by_user = by_user.sort_values("Credits", ascending=False)
                st.altair_chart(_hbar(by_user, "User", "Credits", "#FFA07A"), use_container_width=True)

        view = st.radio("View", ["Summary by day", "Summary by Agent", "Summary by user", "Raw data"], horizontal=True, key="si_view")
        if view == "Summary by day":
            agg = {"Credits": ("CREDITS", "sum")}
            if "TOKENS" in df_si.columns:
                agg["Tokens"] = ("TOKENS", "sum")
            summary = df_si.groupby("DATE").agg(**agg).reset_index()
            summary.rename(columns={"DATE": "Date"}, inplace=True)
            st.dataframe(summary.sort_values("Date", ascending=False),
                         column_config={"Credits": st.column_config.NumberColumn(format="%.6f")},
                         hide_index=True, use_container_width=True)
        elif view == "Summary by Agent" and "AGENT_NAME" in df_si.columns:
            tbl = (
                df_si.groupby(["AGENT_NAME", "AGENT_DATABASE_NAME", "AGENT_SCHEMA_NAME"])
                .agg(Credits=("CREDITS", "sum"), Tokens=("TOKENS", "sum"), Sessions=("CREDITS", "count"))
                .reset_index().sort_values("Credits", ascending=False)
            )
            st.dataframe(tbl, column_config={"Credits": st.column_config.NumberColumn(format="%.6f")},
                         hide_index=True, use_container_width=True)
        elif view == "Summary by user":
            agg = {"Credits": ("CREDITS", "sum")}
            if "TOKENS" in df_si.columns:
                agg["Tokens"] = ("TOKENS", "sum")
            summary = df_si.groupby("USERNAME").agg(**agg).reset_index()
            summary.rename(columns={"USERNAME": "User"}, inplace=True)
            st.dataframe(summary.sort_values("Credits", ascending=False),
                         column_config={"Credits": st.column_config.NumberColumn(format="%.6f")},
                         hide_index=True, use_container_width=True)
        else:
            detail_cols = [c for c in ["START_TIME", "USERNAME", "SNOWFLAKE_INTELLIGENCE_NAME", "AGENT_NAME", "CREDITS", "TOKENS"] if c in df_si.columns]
            st.dataframe(df_si[detail_cols].sort_values("START_TIME", ascending=False),
                         column_config={"CREDITS": st.column_config.NumberColumn(format="%.6f")},
                         hide_index=True, use_container_width=True)


with tab_agents:
    render_service_tab(
        df_agents, credit_col="CREDITS", token_col="TOKENS", user_col="USERNAME",
        detail_cols=["START_TIME", "USERNAME", "AGENT_DATABASE_NAME", "AGENT_SCHEMA_NAME", "AGENT_NAME", "CREDITS", "TOKENS"],
        title="Cortex Agents",
        extra_summaries=[
            ("Summary by agent", "AGENT_NAME", "Agent"),
            ("Summary by user", "USERNAME", "User"),
            ("Summary by database", "AGENT_DATABASE_NAME", "Database"),
        ],
    )


with tab_coco:
    coco_total_cr = coco_credits + coco_ss_credits
    coco_total_tok = (
        (int(df_coco["TOKENS"].sum()) if not df_coco.empty and "TOKENS" in df_coco.columns else 0)
        + (int(df_coco_ss["TOKENS"].sum()) if not df_coco_ss.empty and "TOKENS" in df_coco_ss.columns else 0)
    )
    coco_users = len(
        set(df_coco["USERNAME"].dropna().tolist() if not df_coco.empty else [])
        | set(df_coco_ss["USERNAME"].dropna().tolist() if not df_coco_ss.empty else [])
    )

    kpi_row([
        ("Total Credits",     f"{coco_total_cr:,.2f}"),
        ("Estimated Cost",    f"${coco_total_cr * COST_PER_AI_CREDIT:,.2f}"),
        ("Total Tokens",      f"{coco_total_tok:,}"),
        ("Unique Users",      f"{coco_users:,}"),
        ("CLI Credits",       f"{coco_credits:,.2f}"),
        ("Snowsight Credits", f"{coco_ss_credits:,.2f}"),
    ])

    if df_coco.empty and df_coco_ss.empty:
        st.info("No Cortex Code usage found for the selected period.")
    else:
        def _coco_daily(df, origin):
            if df.empty:
                return pd.DataFrame()
            d = df.copy()
            d["DATE"] = pd.to_datetime(d["START_TIME"]).dt.date
            agg = d.groupby("DATE").agg(CREDITS=("CREDITS", "sum"), TOKENS=("TOKENS", "sum")).reset_index()
            agg["Origin"] = origin
            return agg

        daily_combined = pd.concat([
            _coco_daily(df_coco, "CLI"),
            _coco_daily(df_coco_ss, "Snowsight"),
        ], ignore_index=True)

        all_coco = pd.concat([
            df_coco[["USERNAME", "CREDITS", "TOKENS"]].assign(Origin="CLI") if not df_coco.empty else pd.DataFrame(),
            df_coco_ss[["USERNAME", "CREDITS", "TOKENS"]].assign(Origin="Snowsight") if not df_coco_ss.empty else pd.DataFrame(),
        ], ignore_index=True)

        if not daily_combined.empty:
            daily_combined["DATE"] = pd.to_datetime(daily_combined["DATE"])
            ori_domain = daily_combined["Origin"].unique().tolist()
            ori_range = [ORIGIN_COLORS.get(o, "#A0A0A0") for o in ori_domain]

            col1, col2 = st.columns(2)
            with col1:
                with st.container():
                    st.subheader("Daily credits by origin")
                    bar_cr = alt.Chart(daily_combined).mark_bar().encode(
                        x=alt.X("DATE:T", title="Date"),
                        y=alt.Y("CREDITS:Q", title="Credits"),
                        color=alt.Color("Origin:N", scale=alt.Scale(domain=ori_domain, range=ori_range)),
                        tooltip=["DATE:T", "Origin:N", alt.Tooltip("CREDITS:Q", format=",.4f")],
                    ).properties(height=280)
                    st.altair_chart(bar_cr, use_container_width=True)
            with col2:
                with st.container():
                    st.subheader("Daily tokens by origin")
                    bar_tok = alt.Chart(daily_combined).mark_bar().encode(
                        x=alt.X("DATE:T", title="Date"),
                        y=alt.Y("TOKENS:Q", title="Tokens"),
                        color=alt.Color("Origin:N", scale=alt.Scale(domain=ori_domain, range=ori_range)),
                        tooltip=["DATE:T", "Origin:N", alt.Tooltip("TOKENS:Q", format=",")],
                    ).properties(height=280)
                    st.altair_chart(bar_tok, use_container_width=True)

        breakdown_df = pd.DataFrame({
            "Origin": ["CLI", "Snowsight"],
            "Credits": [coco_credits, coco_ss_credits],
        })
        breakdown_df = breakdown_df[breakdown_df["Credits"] > 0]

        col3, col4 = st.columns(2)
        with col3:
            with st.container():
                st.subheader("CLI vs Snowsight share")
                if not breakdown_df.empty:
                    donut_coco = alt.Chart(breakdown_df).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta("Credits:Q"),
                        color=alt.Color("Origin:N",
                                        scale=alt.Scale(domain=["CLI", "Snowsight"],
                                                        range=["#29B5E8", "#11567F"])),
                        tooltip=["Origin:N", alt.Tooltip("Credits:Q", format=",.4f")],
                    ).properties(height=280)
                    st.altair_chart(donut_coco, use_container_width=True)
        with col4:
            with st.container():
                st.subheader("Top users by credits")
                if not all_coco.empty:
                    by_user_coco = (
                        all_coco.groupby("USERNAME")
                        .agg(Credits=("CREDITS", "sum"), Tokens=("TOKENS", "sum"))
                        .reset_index().sort_values("Credits", ascending=False)
                    )
                    st.altair_chart(_hbar(by_user_coco, "USERNAME", "Credits", "#29B5E8"), use_container_width=True)

        col5, col6 = st.columns(2)
        with col5:
            with st.container():
                st.subheader("User distribution by surface")
                if not all_coco.empty:
                    users_by_surface = (
                        all_coco.groupby("Origin")["USERNAME"]
                        .nunique().reset_index()
                        .rename(columns={"USERNAME": "Unique Users"})
                    )
                    ori_d2 = users_by_surface["Origin"].tolist()
                    ori_r2 = [ORIGIN_COLORS.get(o, "#A0A0A0") for o in ori_d2]
                    surf_chart = (
                        alt.Chart(users_by_surface)
                        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                        .encode(
                            x=alt.X("Origin:N", title=""),
                            y=alt.Y("Unique Users:Q", title="Unique Users"),
                            color=alt.Color("Origin:N",
                                            scale=alt.Scale(domain=ori_d2, range=ori_r2),
                                            legend=None),
                            tooltip=["Origin:N", alt.Tooltip("Unique Users:Q", format=",")],
                        ).properties(height=280)
                    )
                    st.altair_chart(surf_chart, use_container_width=True)
        with col6:
            with st.container():
                st.subheader("Daily & monthly active users")
                if not all_coco.empty:
                    au_view = st.radio("Granularity", ["Daily", "Monthly"], horizontal=True,
                                       key="coco_au_view")
                    au_frames = []
                    for _df, _origin in [(df_coco, "CLI"), (df_coco_ss, "Snowsight")]:
                        if _df.empty:
                            continue
                        _d = _df.copy()
                        _d["DATE"] = pd.to_datetime(_d["START_TIME"]).dt.date
                        if au_view == "Daily":
                            _agg = _d.groupby("DATE")["USERNAME"].nunique().reset_index()
                            _agg.columns = ["Period", "Active Users"]
                        else:
                            _d["MONTH"] = pd.to_datetime(_d["START_TIME"]).dt.to_period("M").astype(str)
                            _agg = _d.groupby("MONTH")["USERNAME"].nunique().reset_index()
                            _agg.columns = ["Period", "Active Users"]
                        _agg["Surface"] = _origin
                        au_frames.append(_agg)
                    if au_frames:
                        au_combined = pd.concat(au_frames, ignore_index=True)
                        au_combined["Period"] = au_combined["Period"].astype(str)
                        surfaces = au_combined["Surface"].unique().tolist()
                        au_colors = [ORIGIN_COLORS.get(s, "#A0A0A0") for s in surfaces]
                        au_chart = (
                            alt.Chart(au_combined)
                            .mark_line(point=True)
                            .encode(
                                x=alt.X("Period:O", title="", axis=alt.Axis(labelAngle=-45)),
                                y=alt.Y("Active Users:Q", title="Active Users"),
                                color=alt.Color("Surface:N",
                                                scale=alt.Scale(domain=surfaces, range=au_colors),
                                                legend=alt.Legend(orient="top")),
                                tooltip=["Period:O", "Surface:N",
                                         alt.Tooltip("Active Users:Q", format=",")],
                            ).properties(height=250)
                        )
                        st.altair_chart(au_chart, use_container_width=True)

        with st.container():
            st.subheader("User details")
            if not all_coco.empty:
                user_detail = (
                    all_coco.groupby(["USERNAME", "Origin"])
                    .agg(Credits=("CREDITS", "sum"), Tokens=("TOKENS", "sum"),
                         Requests=("CREDITS", "count"))
                    .reset_index().sort_values("Credits", ascending=False)
                )
                user_detail["Credits"] = user_detail["Credits"].round(6)
                st.dataframe(user_detail, hide_index=True, use_container_width=True)


with tab_long:
    st.caption(
        f"Queries spanning more than **{long_running_threshold}** minute(s) across multiple 1-hour aggregation windows. "
        "Long-running LLM calls accumulate costs over their entire duration."
    )

    if df_lr.empty:
        st.info("No multi-window queries found for the selected period.")
    else:
        filtered = df_lr[df_lr["DURATION_MINUTES"] >= long_running_threshold]

        if filtered.empty:
            st.info(f"No queries exceeded {long_running_threshold} minute(s).")
        else:
            lr_credits = filtered["TOTAL_CREDITS"].sum()
            lr_cost = lr_credits * SERVICE_COST_RATES["LLM functions"]

            kpi_row([
                ("Long-running Queries", f"{len(filtered):,}"),
                ("Total Credits",        f"{lr_credits:,.2f}"),
                ("Estimated Cost",       f"${lr_cost:,.2f}"),
                ("Max Duration (min)",   f"{int(filtered['DURATION_MINUTES'].max()):,}"),
            ])

            with st.container():
                st.subheader("Duration distribution")
                dur_chart = alt.Chart(filtered).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                    x=alt.X("DURATION_MINUTES:Q", bin=alt.Bin(maxbins=20), title="Duration (minutes)"),
                    y=alt.Y("count()", title="Number of queries"),
                    tooltip=["count()", alt.Tooltip("DURATION_MINUTES:Q", title="Duration")],
                ).properties(height=250)
                st.altair_chart(dur_chart, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                with st.container():
                    st.subheader("By model")
                    lr_model = filtered.groupby("MODEL_NAME")["TOTAL_CREDITS"].sum().reset_index()
                    lr_model.columns = ["Model", "Credits"]
                    st.altair_chart(_hbar(lr_model, "Model", "Credits", "#FF6B6B"), use_container_width=True)
            with col2:
                with st.container():
                    st.subheader("By user")
                    lr_user = filtered.groupby("USERNAME")["TOTAL_CREDITS"].sum().reset_index()
                    lr_user.columns = ["User", "Credits"]
                    st.altair_chart(_hbar(lr_user, "User", "Credits", "#FFA07A"), use_container_width=True)

            with st.container():
                st.subheader("Query details")
                st.dataframe(
                    filtered[["QUERY_ID", "FUNCTION_NAME", "MODEL_NAME", "USERNAME",
                              "FIRST_WINDOW", "LAST_WINDOW", "WINDOW_COUNT",
                              "DURATION_MINUTES", "TOTAL_CREDITS"]].sort_values("DURATION_MINUTES", ascending=False),
                    column_config={
                        "TOTAL_CREDITS": st.column_config.NumberColumn("Credits", format="%.6f"),
                        "DURATION_MINUTES": st.column_config.NumberColumn("Duration (min)", format="%d"),
                        "WINDOW_COUNT": st.column_config.NumberColumn("Windows", format="%d"),
                    },
                    hide_index=True, use_container_width=True,
                )


with tab_controls:
    ctrl_section = st.radio(
        "Section",
        ["AI Functions Cost Control", "Cortex Code Cost Control", "Cortex Agent Resource Budgets"],
        horizontal=True,
        key="ctrl_sec",
    )

    if ctrl_section == "AI Functions Cost Control":
        _ctrl_banner(
            "AI Functions Cost Control",
            "Set up automated monitoring, per-user limits, and runaway query detection for Cortex AI Functions. "
            "Based on Snowflake documentation.",
            "#29B5E8",
            "🧠",
        )

        ai_sub = st.radio(
            "Select control",
            ["Account-level monthly spending alert", "Per-user monthly spending limits", "Runaway query detection"],
            horizontal=True,
        )

        if ai_sub == "Account-level monthly spending alert":
            with st.container():
                st.markdown("##### 🔔 Account-level monthly spending alert")
                st.caption(
                    "Sends an email when total monthly AI Function credit consumption exceeds a threshold. "
                    "Requires ACCOUNTADMIN and verified email addresses."
                )

                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    alert_recipients = st.text_input(
                        "Alert recipients (comma-separated emails)",
                        value="admin@company.com",
                        key="alert_recipients",
                    )
                with col_a2:
                    alert_threshold = st.number_input(
                        "Monthly credit threshold", min_value=1, value=1000, step=100, key="alert_threshold"
                    )

                alert_warehouse = st.text_input("Warehouse for alert", value="COMPUTE_WH", key="alert_wh")

                if st.button("Generate SQL", key="gen_alert"):
                    recipients_sql = ", ".join([f"'{e.strip()}'" for e in alert_recipients.split(",")])
                    first_recipient = alert_recipients.split(",")[0].strip()
                    sql_alert = f"""-- 1. Create notification integration
CREATE OR REPLACE NOTIFICATION INTEGRATION ai_cost_alerts
    TYPE = EMAIL
    ENABLED = TRUE
    ALLOWED_RECIPIENTS = ({recipients_sql});

-- 2. Create alert state table (prevents duplicate alerts per month)
CREATE TABLE IF NOT EXISTS AI_FUNCTIONS_ALERT_STATE (
    ALERT_NAME VARCHAR NOT NULL,
    ALERT_MONTH DATE NOT NULL,
    SENT_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREDITS_AT_ALERT NUMBER(38,6),
    PRIMARY KEY (ALERT_NAME, ALERT_MONTH)
);

-- 3. Create stored procedure for alert logic
CREATE OR REPLACE PROCEDURE SEND_MONTHLY_SPEND_ALERT(P_THRESHOLD FLOAT)
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
EXECUTE AS CALLER
AS
$$
    var check_sent = snowflake.execute({{
        sqlText: `SELECT COUNT(*) AS cnt FROM AI_FUNCTIONS_ALERT_STATE
                WHERE ALERT_NAME = 'monthly_spend'
                AND ALERT_MONTH = DATE_TRUNC('month', CURRENT_DATE())`
    }});
    check_sent.next();
    if (check_sent.getColumnValue(1) > 0) return 'Alert already sent for this month';

    var spend_result = snowflake.execute({{
        sqlText: `SELECT COALESCE(SUM(CREDITS), 0) AS total
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY
                WHERE START_TIME >= DATE_TRUNC('month', CURRENT_TIMESTAMP())`
    }});
    spend_result.next();
    var v_credits = spend_result.getColumnValue(1);
    if (v_credits <= P_THRESHOLD) return 'Threshold not exceeded. Current: ' + v_credits + ' / ' + P_THRESHOLD;

    snowflake.execute({{
        sqlText: `INSERT INTO AI_FUNCTIONS_ALERT_STATE (ALERT_NAME, ALERT_MONTH, CREDITS_AT_ALERT)
                VALUES ('monthly_spend', DATE_TRUNC('month', CURRENT_DATE()), ?)`,
        binds: [v_credits]
    }});

    snowflake.execute({{
        sqlText: `CALL SYSTEM$SEND_EMAIL('ai_cost_alerts', '{first_recipient}',
            'AI Functions Monthly Spend Alert',
            'Monthly AI Function credit consumption has exceeded the threshold.\\n\\n' ||
            'Current spend: ' || ${{v_credits}}::VARCHAR || ' credits\\n' ||
            'Threshold: ' || ${{P_THRESHOLD}}::VARCHAR || ' credits')`
    }});
    return 'Alert sent. Credits: ' + v_credits;
$$;

-- 4. Create the hourly alert
CREATE OR REPLACE ALERT ai_functions_monthly_spend_alert
    WAREHOUSE = {alert_warehouse}
    SCHEDULE = 'USING CRON 0 * * * * UTC'
    IF (EXISTS (
        SELECT 1
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY
        WHERE START_TIME >= DATE_TRUNC('month', CURRENT_TIMESTAMP())
        HAVING SUM(CREDITS) > {alert_threshold}
    ))
    THEN
        CALL SEND_MONTHLY_SPEND_ALERT({alert_threshold});

ALTER ALERT ai_functions_monthly_spend_alert RESUME;"""
                    st.code(sql_alert, language="sql")
                    if st.button("Execute all statements", key="exec_alert"):
                        stmts = [s.strip() for s in sql_alert.split(";") if s.strip() and not s.strip().startswith("--")]
                        for stmt in stmts:
                            try:
                                session.sql(stmt).collect()
                            except Exception as e:
                                st.error(f"Error: {e}")
                                break
                        else:
                            st.success("All statements executed successfully.")

        elif ai_sub == "Per-user monthly spending limits":
            with st.container():
                st.markdown("##### 👤 Per-user monthly spending limits")
                st.caption(
                    "Enforce per-user monthly credit budgets by granting/revoking a dedicated AI_FUNCTIONS_USER_ROLE. "
                    "Requires revoking SNOWFLAKE.CORTEX_USER from PUBLIC first."
                )

                st.warning(
                    "This will REVOKE `SNOWFLAKE.CORTEX_USER` from PUBLIC. "
                    "Only users explicitly granted `AI_FUNCTIONS_USER_ROLE` will have AI Function access.",
                    icon=":material/warning:",
                )

                user_wh = st.text_input("Warehouse for tasks", value="COMPUTE_WH", key="user_limit_wh")
                default_limit = st.number_input("Default monthly credit limit per user", min_value=1, value=100, step=50, key="default_user_limit")

                if st.button("Generate SQL", key="gen_user_limits"):
                    sql_user = f"""-- 1. Revoke default public access
REVOKE DATABASE ROLE SNOWFLAKE.CORTEX_USER FROM ROLE PUBLIC;

-- 2. Create AI Functions access role
CREATE ROLE IF NOT EXISTS AI_FUNCTIONS_USER_ROLE;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE AI_FUNCTIONS_USER_ROLE;
GRANT USAGE ON WAREHOUSE {user_wh} TO ROLE AI_FUNCTIONS_USER_ROLE;

-- 3. Create access control table
CREATE TABLE IF NOT EXISTS AI_FUNCTIONS_ACCESS_CONTROL (
    USER_NAME VARCHAR NOT NULL,
    USER_ID NUMBER,
    GRANTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    MONTHLY_CREDIT_LIMIT NUMBER(38,6) DEFAULT {default_limit},
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    REVOKED_AT TIMESTAMP_LTZ,
    REVOCATION_REASON VARCHAR,
    PRIMARY KEY (USER_NAME)
);

-- 4. Procedure to grant access and register user
CREATE OR REPLACE PROCEDURE GRANT_AI_FUNCTIONS_ACCESS(
    P_USER_NAME VARCHAR, P_MONTHLY_LIMIT NUMBER(38,6) DEFAULT {default_limit}
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE v_user_id NUMBER;
BEGIN
    SELECT USER_ID INTO :v_user_id FROM SNOWFLAKE.ACCOUNT_USAGE.USERS WHERE NAME = :P_USER_NAME LIMIT 1;
    EXECUTE IMMEDIATE 'GRANT ROLE AI_FUNCTIONS_USER_ROLE TO USER ' || P_USER_NAME;
    MERGE INTO AI_FUNCTIONS_ACCESS_CONTROL tgt
    USING (SELECT :P_USER_NAME AS USER_NAME) src ON tgt.USER_NAME = src.USER_NAME
    WHEN MATCHED THEN UPDATE SET USER_ID = :v_user_id, IS_ACTIVE = TRUE, MONTHLY_CREDIT_LIMIT = :P_MONTHLY_LIMIT,
        GRANTED_AT = CURRENT_TIMESTAMP(), REVOKED_AT = NULL, REVOCATION_REASON = NULL
    WHEN NOT MATCHED THEN INSERT (USER_NAME, USER_ID, MONTHLY_CREDIT_LIMIT, IS_ACTIVE)
        VALUES (:P_USER_NAME, :v_user_id, :P_MONTHLY_LIMIT, TRUE);
    RETURN 'Access granted to ' || P_USER_NAME || ' with limit ' || P_MONTHLY_LIMIT || ' credits';
END;
$$;

-- 5. Monthly access refresh task (1st of each month)
CREATE OR REPLACE PROCEDURE GRANT_ALL_ENTITLED_USERS()
RETURNS TABLE (USER_NAME VARCHAR, CREDIT_LIMIT NUMBER, ACTION VARCHAR)
LANGUAGE SQL
AS
$$
DECLARE result RESULTSET;
BEGIN
    result := (SELECT USER_NAME, MONTHLY_CREDIT_LIMIT AS CREDIT_LIMIT, 'GRANTED' AS ACTION FROM AI_FUNCTIONS_ACCESS_CONTROL);
    FOR rec IN result DO
        CALL GRANT_AI_FUNCTIONS_ACCESS(rec.USER_NAME, rec.CREDIT_LIMIT);
    END FOR;
    RETURN TABLE(result);
END;
$$;

CREATE OR REPLACE TASK MONTHLY_AI_FUNCTIONS_ACCESS_REFRESH
    WAREHOUSE = {user_wh}
    SCHEDULE = 'USING CRON 0 0 1 * * UTC'
AS
    CALL GRANT_ALL_ENTITLED_USERS();

ALTER TASK MONTHLY_AI_FUNCTIONS_ACCESS_REFRESH RESUME;

-- 6. Hourly enforcement task (revoke on overspend)
CREATE OR REPLACE PROCEDURE ENFORCE_AI_FUNCTIONS_LIMITS()
RETURNS TABLE (USER_NAME VARCHAR, CREDITS_USED NUMBER, CREDIT_LIMIT NUMBER, ACTION VARCHAR)
LANGUAGE SQL
AS
$$
DECLARE result RESULTSET;
BEGIN
    result := (
        SELECT ac.USER_NAME, COALESCE(u.total_credits, 0) AS CREDITS_USED,
            ac.MONTHLY_CREDIT_LIMIT AS CREDIT_LIMIT, 'REVOKED' AS ACTION
        FROM AI_FUNCTIONS_ACCESS_CONTROL ac
        LEFT JOIN (
            SELECT h.USER_ID, SUM(h.CREDITS) AS total_credits
            FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY h
            WHERE h.START_TIME >= DATE_TRUNC('month', CURRENT_TIMESTAMP())
            GROUP BY h.USER_ID
        ) u ON ac.USER_ID = u.USER_ID
        WHERE ac.IS_ACTIVE = TRUE AND COALESCE(u.total_credits, 0) > ac.MONTHLY_CREDIT_LIMIT
    );
    FOR rec IN result DO
        BEGIN
            EXECUTE IMMEDIATE 'REVOKE ROLE AI_FUNCTIONS_USER_ROLE FROM USER ' || rec.USER_NAME;
            UPDATE AI_FUNCTIONS_ACCESS_CONTROL SET IS_ACTIVE = FALSE, REVOKED_AT = CURRENT_TIMESTAMP(),
                REVOCATION_REASON = 'Monthly limit exceeded' WHERE USER_NAME = rec.USER_NAME;
        EXCEPTION WHEN OTHER THEN NULL;
        END;
    END FOR;
    RETURN TABLE(result);
END;
$$;

CREATE OR REPLACE TASK HOURLY_AI_FUNCTIONS_LIMIT_CHECK
    WAREHOUSE = {user_wh}
    SCHEDULE = 'USING CRON 0 * * * * UTC'
AS
    CALL ENFORCE_AI_FUNCTIONS_LIMITS();

ALTER TASK HOURLY_AI_FUNCTIONS_LIMIT_CHECK RESUME;"""
                    st.code(sql_user, language="sql")
                    if st.button("Execute setup", key="exec_user_setup"):
                        stmts = [s.strip() for s in sql_user.split(";") if s.strip() and not s.strip().startswith("--")]
                        for stmt in stmts:
                            try:
                                session.sql(stmt).collect()
                            except Exception as e:
                                st.error(f"Error: {e}")
                                break
                        else:
                            st.success("Per-user spending limit infrastructure created successfully.")

                st.divider()
                st.markdown("##### 📧 Grant access to a user")
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    grant_user = st.text_input("Username", key="grant_user_name")
                with col_u2:
                    grant_limit = st.number_input("Monthly credit limit", min_value=1, value=100, step=50, key="grant_user_limit")
                if st.button("Grant access", key="exec_grant_user") and grant_user:
                    try:
                        check = session.sql(
                            "SHOW PROCEDURES LIKE 'GRANT_AI_FUNCTIONS_ACCESS' IN ACCOUNT"
                        ).collect()
                        if not check:
                            st.error("Procedure `GRANT_AI_FUNCTIONS_ACCESS` does not exist. Click **Generate SQL** above and execute the setup statements first.")
                        else:
                            result = session.sql(f"CALL GRANT_AI_FUNCTIONS_ACCESS('{grant_user}', {grant_limit})").collect()
                            st.success(result[0][0])
                    except Exception as e:
                        st.error(f"Error: {e}")

                st.divider()
                st.markdown("##### 📋 Current access control status")
                if st.button("Refresh", key="refresh_acl"):
                    try:
                        acl_df = session.sql("SELECT * FROM AI_FUNCTIONS_ACCESS_CONTROL ORDER BY USER_NAME").to_pandas()
                        st.dataframe(acl_df, hide_index=True, use_container_width=True)
                    except Exception as e:
                        st.info("Access control table not found. Run the setup SQL first.")

        else:
            with st.container():
                st.markdown("##### ⚡ Runaway query detection & cancellation")
                st.caption(
                    "Automatically detect and cancel AI Function queries exceeding a credit threshold. "
                    "An email alert is sent with query details."
                )

                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    runaway_threshold = st.number_input("Credit threshold per query", min_value=1, value=50, step=10, key="runaway_thresh")
                with col_r2:
                    runaway_email = st.text_input("Alert email", value="admin@company.com", key="runaway_email")
                with col_r3:
                    runaway_wh = st.text_input("Warehouse", value="COMPUTE_WH", key="runaway_wh")

                if st.button("Generate SQL", key="gen_runaway"):
                    sql_runaway = f"""-- Procedure to detect and cancel expensive runaway queries
CREATE OR REPLACE PROCEDURE MONITOR_AND_CANCEL_RUNAWAY_QUERIES(
    P_CREDIT_THRESHOLD NUMBER DEFAULT {runaway_threshold}
)
RETURNS TABLE (
    QUERY_ID VARCHAR, USER_NAME VARCHAR, FUNCTION_NAME VARCHAR,
    MODEL_NAME VARCHAR, CREDITS NUMBER, START_TIME TIMESTAMP_LTZ, ACTION VARCHAR
)
LANGUAGE SQL
AS
$$
DECLARE result RESULTSET;
BEGIN
    result := (
        SELECT h.QUERY_ID, u.NAME AS USER_NAME, h.FUNCTION_NAME, h.MODEL_NAME,
            h.CREDITS, h.START_TIME, h.ROLE_NAMES, h.QUERY_TAG, h.WAREHOUSE_ID, 'CANCELLED' AS ACTION
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY h
        LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON h.USER_ID = u.USER_ID
        WHERE h.START_TIME >= DATEADD('hour', -48, CURRENT_TIMESTAMP())
            AND h.CREDITS > :P_CREDIT_THRESHOLD AND h.IS_COMPLETED = FALSE
    );
    FOR rec IN result DO
        BEGIN
            EXECUTE IMMEDIATE 'SELECT SYSTEM$CANCEL_QUERY(''' || rec.QUERY_ID || ''')';
        EXCEPTION WHEN OTHER THEN NULL;
        END;
        CALL SYSTEM$SEND_EMAIL('ai_cost_alerts', '{runaway_email}',
            'Runaway AI Query Cancelled - ' || rec.QUERY_ID,
            'Query cancelled due to excessive cost.\\n' ||
            'Query ID: ' || rec.QUERY_ID || '\\n' ||
            'User: ' || COALESCE(rec.USER_NAME, 'Unknown') || '\\n' ||
            'Function: ' || rec.FUNCTION_NAME || '\\n' ||
            'Model: ' || rec.MODEL_NAME || '\\n' ||
            'Credits: ' || rec.CREDITS::VARCHAR || '\\n' ||
            'Start Time: ' || rec.START_TIME::VARCHAR);
    END FOR;
    RETURN TABLE(result);
END;
$$;

-- Hourly task to monitor runaway queries
CREATE OR REPLACE TASK MONITOR_RUNAWAY_AI_QUERIES
    WAREHOUSE = {runaway_wh}
    SCHEDULE = 'USING CRON 0 * * * * UTC'
AS
    CALL MONITOR_AND_CANCEL_RUNAWAY_QUERIES({runaway_threshold});

ALTER TASK MONITOR_RUNAWAY_AI_QUERIES RESUME;"""
                    st.code(sql_runaway, language="sql")

                st.divider()
                st.markdown("##### 🔎 Run detection now")
                if st.button("Scan for runaway queries", key="exec_runaway"):
                    try:
                        result = session.sql(f"CALL MONITOR_AND_CANCEL_RUNAWAY_QUERIES({runaway_threshold})").to_pandas()
                        if result.empty:
                            st.success("No runaway queries detected.")
                        else:
                            st.warning(f"Cancelled {len(result)} runaway queries.")
                            st.dataframe(result, hide_index=True, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error: {e}. Ensure the procedure exists (run Generate SQL first).")

    elif ctrl_section == "Cortex Code Cost Control":
        _ctrl_banner(
            "Cortex Code Cost Control",
            "Set daily estimated credit limits per user for Cortex Code CLI and Snowsight. "
            "Account-level defaults apply to all users; per-user overrides take precedence. Requires ACCOUNTADMIN. "
            "Based on Snowflake documentation.",
            "#4ECDC4",
            "\u27e8\u27e9",
        )

        coco_sub = st.radio(
            "Select action",
            ["View current limits", "Set account-level defaults", "Set per-user override", "Remove per-user override"],
            horizontal=True,
            key="coco_sub",
        )

        if coco_sub == "View current limits":
            with st.container():
                st.markdown("##### 🔍 Account-level defaults")
                if st.button("Fetch account defaults", key="fetch_acct_defaults"):
                    try:
                        cli_df = session.sql(
                            "SHOW PARAMETERS LIKE 'CORTEX_CODE_CLI_DAILY_EST_CREDIT_LIMIT_PER_USER' IN ACCOUNT"
                        ).to_pandas()
                        ss_df = session.sql(
                            "SHOW PARAMETERS LIKE 'CORTEX_CODE_SNOWSIGHT_DAILY_EST_CREDIT_LIMIT_PER_USER' IN ACCOUNT"
                        ).to_pandas()
                        combined = pd.concat([cli_df, ss_df], ignore_index=True)
                        combined.columns = combined.columns.str.lower()
                        if combined.empty:
                            st.info("No account-level CoCo limits found.")
                        else:
                            show_cols = [c for c in ["key", "value", "default", "level", "description"] if c in combined.columns]
                            st.dataframe(
                                combined[show_cols] if show_cols else combined,
                                hide_index=True, use_container_width=True,
                            )
                    except Exception as e:
                        st.error(f"Error: {e}")

            with st.container():
                st.markdown("##### 👤 Per-user overrides")
                coco_check_user = st.text_input("Username to check", key="coco_check_user", placeholder="e.g. JSMITH")
                if st.button("Fetch user limits", key="fetch_user_limits") and coco_check_user:
                    try:
                        cli_u = session.sql(
                            f"SHOW PARAMETERS LIKE 'CORTEX_CODE_CLI_DAILY_EST_CREDIT_LIMIT_PER_USER' FOR USER {coco_check_user}"
                        ).to_pandas()
                        ss_u = session.sql(
                            f"SHOW PARAMETERS LIKE 'CORTEX_CODE_SNOWSIGHT_DAILY_EST_CREDIT_LIMIT_PER_USER' FOR USER {coco_check_user}"
                        ).to_pandas()
                        combined_u = pd.concat([cli_u, ss_u], ignore_index=True)
                        combined_u.columns = combined_u.columns.str.lower()
                        if combined_u.empty:
                            st.info(f"No CoCo limits found for {coco_check_user}.")
                        else:
                            show_cols_u = [c for c in ["key", "value", "default", "level", "description"] if c in combined_u.columns]
                            st.dataframe(
                                combined_u[show_cols_u] if show_cols_u else combined_u,
                                hide_index=True, use_container_width=True,
                            )
                    except Exception as e:
                        st.error(f"Error: {e}")

        elif coco_sub == "Set account-level defaults":
            with st.container():
                st.markdown("##### ⚙️ Set account-level daily credit limits")
                st.caption(
                    "These defaults apply to **all users** who do not have a per-user override. "
                    "Set to 0 to block all CoCo usage by default."
                )
                col_cc1, col_cc2 = st.columns(2)
                with col_cc1:
                    acct_cli_limit = st.number_input(
                        "CLI daily credit limit", min_value=-1, value=1, step=1, key="acct_cli_lim",
                        help="CORTEX_CODE_CLI_DAILY_EST_CREDIT_LIMIT_PER_USER (-1 = no limit, 0 = disabled)",
                    )
                with col_cc2:
                    acct_ss_limit = st.number_input(
                        "Snowsight daily credit limit", min_value=-1, value=1, step=1, key="acct_ss_lim",
                        help="CORTEX_CODE_SNOWSIGHT_DAILY_EST_CREDIT_LIMIT_PER_USER (-1 = no limit, 0 = disabled)",
                    )

                sql_acct = f"""ALTER ACCOUNT SET CORTEX_CODE_CLI_DAILY_EST_CREDIT_LIMIT_PER_USER = {int(acct_cli_limit)};
ALTER ACCOUNT SET CORTEX_CODE_SNOWSIGHT_DAILY_EST_CREDIT_LIMIT_PER_USER = {int(acct_ss_limit)};"""
                st.code(sql_acct, language="sql")
                if st.button("Apply account defaults", key="exec_acct_coco"):
                    try:
                        session.sql(f"ALTER ACCOUNT SET CORTEX_CODE_CLI_DAILY_EST_CREDIT_LIMIT_PER_USER = {int(acct_cli_limit)}").collect()
                        session.sql(f"ALTER ACCOUNT SET CORTEX_CODE_SNOWSIGHT_DAILY_EST_CREDIT_LIMIT_PER_USER = {int(acct_ss_limit)}").collect()
                        st.success(f"Account defaults set: CLI = {int(acct_cli_limit)}, Snowsight = {int(acct_ss_limit)} credits/day/user.")
                    except Exception as e:
                        st.error(f"Error: {e}")

        elif coco_sub == "Set per-user override":
            with st.container():
                st.markdown("##### ✏️ Set per-user daily credit override")
                st.caption(
                    "User-level overrides **always take precedence** over account-level defaults. "
                    "Use this to give power users higher limits or restrict specific users."
                )
                coco_user = st.text_input("Username", key="coco_override_user", placeholder="e.g. JSMITH")
                col_cu1, col_cu2 = st.columns(2)
                with col_cu1:
                    user_cli_limit = st.number_input(
                        "CLI daily credit limit", min_value=-1, value=1, step=1, key="user_cli_lim",
                    )
                with col_cu2:
                    user_ss_limit = st.number_input(
                        "Snowsight daily credit limit", min_value=-1, value=1, step=1, key="user_ss_lim",
                    )

                if coco_user:
                    sql_user_override = f"""ALTER USER {coco_user} SET CORTEX_CODE_CLI_DAILY_EST_CREDIT_LIMIT_PER_USER = {int(user_cli_limit)};
ALTER USER {coco_user} SET CORTEX_CODE_SNOWSIGHT_DAILY_EST_CREDIT_LIMIT_PER_USER = {int(user_ss_limit)};"""
                    st.code(sql_user_override, language="sql")
                    if st.button("Apply user override", key="exec_user_coco"):
                        try:
                            session.sql(f"ALTER USER {coco_user} SET CORTEX_CODE_CLI_DAILY_EST_CREDIT_LIMIT_PER_USER = {int(user_cli_limit)}").collect()
                            session.sql(f"ALTER USER {coco_user} SET CORTEX_CODE_SNOWSIGHT_DAILY_EST_CREDIT_LIMIT_PER_USER = {int(user_ss_limit)}").collect()
                            st.success(f"Override set for {coco_user}: CLI = {int(user_cli_limit)}, Snowsight = {int(user_ss_limit)} credits/day.")
                        except Exception as e:
                            st.error(f"Error: {e}")

        else:
            with st.container():
                st.markdown("##### ❌ Remove per-user override")
                coco_unset_user = st.text_input("Username", key="coco_unset_user", placeholder="e.g. JSMITH")
                if coco_unset_user:
                    sql_unset = f"""ALTER USER {coco_unset_user} UNSET CORTEX_CODE_CLI_DAILY_EST_CREDIT_LIMIT_PER_USER;
ALTER USER {coco_unset_user} UNSET CORTEX_CODE_SNOWSIGHT_DAILY_EST_CREDIT_LIMIT_PER_USER;"""
                    st.code(sql_unset, language="sql")
                    if st.button("Remove override", key="exec_unset_coco"):
                        try:
                            session.sql(f"ALTER USER {coco_unset_user} UNSET CORTEX_CODE_CLI_DAILY_EST_CREDIT_LIMIT_PER_USER").collect()
                            session.sql(f"ALTER USER {coco_unset_user} UNSET CORTEX_CODE_SNOWSIGHT_DAILY_EST_CREDIT_LIMIT_PER_USER").collect()
                            st.success(f"Override removed for {coco_unset_user}. Account defaults now apply.")
                        except Exception as e:
                            st.error(f"Error: {e}")

    else:
        _ctrl_banner(
            "Cortex Agent Resource Budgets",
            "Use Snowflake\u2019s tag-based cost attribution to create budgets for Cortex Agent objects. "
            "Based on Snowflake documentation.",
            "#9B59B6",
            "\U0001f916",
        )

        agent_sub = st.radio(
            "Select action",
            ["Setup tag & budget", "Configure threshold actions", "Monitor usage"],
            horizontal=True,
            key="agent_sub",
        )

        if agent_sub == "Setup tag & budget":
            with st.container():
                _step_header(1, "Create a cost center tag", "#9B59B6")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    tag_db = st.text_input("Tag database", value="COST_MGMT_DB", key="tag_db")
                    tag_schema = st.text_input("Tag schema", value="TAGS", key="tag_schema")
                with col_t2:
                    tag_name = st.text_input("Tag name", value="COST_CENTER", key="tag_name")
                    tag_value = st.text_input("Allowed tag value", value="org-level", key="tag_value")

                tag_fqn = f"{tag_db}.{tag_schema}.{tag_name}"

                sql_tag = f"""CREATE TAG IF NOT EXISTS {tag_fqn}
   ALLOWED_VALUES '{tag_value}'
   COMMENT = 'Cost center tag for Cortex Agent budgets';"""
                st.code(sql_tag, language="sql")
                if st.button("Create tag", key="exec_tag"):
                    try:
                        session.sql(f"CREATE DATABASE IF NOT EXISTS {tag_db}").collect()
                        session.sql(f"CREATE SCHEMA IF NOT EXISTS {tag_db}.{tag_schema}").collect()
                        session.sql(sql_tag).collect()
                        st.success(f"Tag `{tag_fqn}` created.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            with st.container():
                _step_header(2, "Apply tag to a Cortex Agent", "#9B59B6")
                agent_name = st.text_input("Agent name (fully qualified)", value="MY_DB.MY_SCHEMA.MY_AGENT", key="agent_name")
                sql_apply = f"ALTER AGENT IF EXISTS {agent_name}\n  SET TAG {tag_fqn} = '{tag_value}';"
                st.code(sql_apply, language="sql")
                if st.button("Apply tag", key="exec_apply_tag"):
                    try:
                        session.sql(sql_apply).collect()
                        st.success(f"Tag applied to `{agent_name}`.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            with st.container():
                _step_header(3, "Create a resource budget", "#9B59B6")
                st.caption(
                    "You can create budgets via Snowsight UI (Admin > Cost management > Budgets) "
                    "or via SQL. Below generates the SQL approach."
                )
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    budget_db = st.text_input("Budget database", value="BUDGETS_DB", key="budget_db")
                    budget_schema = st.text_input("Budget schema", value="BUDGETS_SCHEMA", key="budget_schema")
                with col_b2:
                    budget_name = st.text_input("Budget name", value="MY_BUDGET", key="budget_name")
                    budget_limit = st.number_input("Monthly credit limit", min_value=1, value=10000, step=1000, key="budget_limit")

                budget_fqn = f"{budget_db}.{budget_schema}.{budget_name}"

                sql_budget = f"""CREATE DATABASE IF NOT EXISTS {budget_db};
CREATE SCHEMA IF NOT EXISTS {budget_db}.{budget_schema};

CREATE OR REPLACE SNOWFLAKE.CORE.BUDGET {budget_fqn}()
  COPY GRANTS;

CALL {budget_fqn}!SET_SPENDING_LIMIT({budget_limit});

CALL {budget_fqn}!ADD_RESOURCE(
  SYSTEM$REFERENCE('TAG', '{tag_fqn}', 'TAG'));"""
                st.code(sql_budget, language="sql")
                if st.button("Create budget", key="exec_budget"):
                    for stmt in [s.strip() for s in sql_budget.split(";") if s.strip()]:
                        try:
                            session.sql(stmt).collect()
                        except Exception as e:
                            st.error(f"Error on: {stmt[:80]}... -> {e}")
                            break
                    else:
                        st.success(f"Budget `{budget_fqn}` created with {budget_limit} credit/month limit.")

        elif agent_sub == "Configure threshold actions":
            with st.container():
                st.markdown("##### 🔔 Notification threshold")
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    notify_budget = st.text_input("Budget (fully qualified)", value="BUDGETS_DB.BUDGETS_SCHEMA.MY_BUDGET", key="notify_budget")
                with col_n2:
                    notify_pct = st.number_input("Notify at % of budget", min_value=1, max_value=500, value=80, step=10, key="notify_pct")

                notify_integration = st.text_input("Notification integration name", value="budgets_notification_integration", key="notify_int")
                notify_emails = st.text_input("Notification emails (comma-separated)", value="costadmin@example.com", key="notify_emails")

                sql_notify = f"""CALL {notify_budget}!SET_EMAIL_NOTIFICATIONS(
  '{notify_integration}',
  '{notify_emails}'
);

CALL {notify_budget}!SET_NOTIFICATION_THRESHOLD({notify_pct});"""
                st.code(sql_notify, language="sql")
                if st.button("Set notification", key="exec_notify"):
                    for stmt in [s.strip() for s in sql_notify.split(";") if s.strip()]:
                        try:
                            session.sql(stmt).collect()
                        except Exception as e:
                            st.error(f"Error: {e}")
                            break
                    else:
                        st.success("Notification configured.")

            with st.container():
                st.markdown("##### 🚫 Revoke access at threshold")
                st.caption(
                    "Create a stored procedure that revokes a role when spending hits a threshold, "
                    "and register it as a custom budget action."
                )
                col_rv1, col_rv2 = st.columns(2)
                with col_rv1:
                    revoke_budget = st.text_input("Budget (fully qualified)", value="BUDGETS_DB.BUDGETS_SCHEMA.MY_BUDGET", key="revoke_budget")
                    revoke_db = st.text_input("Procedure database", value="BUDGETS_DB", key="revoke_db")
                    revoke_schema = st.text_input("Procedure schema", value="BUDGETS_SCHEMA", key="revoke_schema")
                with col_rv2:
                    revoke_agent = st.text_input("Agent name (short)", value="MY_AGENT", key="revoke_agent")
                    revoke_role = st.text_input("Role to revoke", value="ANALYST_ROLE", key="revoke_role")
                    revoke_pct = st.number_input("Revoke at % of budget", min_value=1, max_value=500, value=100, step=10, key="revoke_pct")

                sql_revoke = f"""-- Stored procedure to revoke agent access
CREATE OR REPLACE PROCEDURE {revoke_db}.{revoke_schema}.SP_REVOKE_AGENT_ACCESS(
   AGENT_NAME STRING, ROLE_NAME STRING
)
RETURNS STRING
LANGUAGE SQL
AS
BEGIN
   EXECUTE IMMEDIATE 'REVOKE ROLE AGENT_' || AGENT_NAME || '_ROLE FROM ROLE ' || ROLE_NAME;
   RETURN 'Access revoked for ' || AGENT_NAME;
END;

-- Grant access to Snowflake application
GRANT USAGE ON DATABASE {revoke_db} TO APPLICATION SNOWFLAKE;
GRANT USAGE ON SCHEMA {revoke_db}.{revoke_schema} TO APPLICATION SNOWFLAKE;
GRANT USAGE ON PROCEDURE {revoke_db}.{revoke_schema}.SP_REVOKE_AGENT_ACCESS(STRING, STRING)
   TO APPLICATION SNOWFLAKE;

-- Register custom action at {revoke_pct}% threshold
CALL {revoke_budget}!ADD_CUSTOM_ACTION(
   SYSTEM$REFERENCE('PROCEDURE',
      '{revoke_db}.{revoke_schema}.SP_REVOKE_AGENT_ACCESS(string, string)'),
   ARRAY_CONSTRUCT('{revoke_agent}', '{revoke_role}'),
   'ACTUAL',
   {revoke_pct});"""
                st.code(sql_revoke, language="sql")

            with st.container():
                st.markdown("##### ♻️ Reinstate access (cycle start)")
                st.caption("Automatically restore access at the start of each budget cycle.")
                reinstate_budget = st.text_input("Budget (fully qualified)", value="BUDGETS_DB.BUDGETS_SCHEMA.MY_BUDGET", key="reinstate_budget")
                reinstate_db = st.text_input("Procedure database", value="BUDGETS_DB", key="reinstate_db")
                reinstate_schema = st.text_input("Procedure schema", value="BUDGETS_SCHEMA", key="reinstate_schema")
                reinstate_agent = st.text_input("Agent name (short)", value="MY_AGENT", key="reinstate_agent")
                reinstate_role = st.text_input("Role to reinstate", value="ANALYST_ROLE", key="reinstate_role")

                sql_reinstate = f"""-- Stored procedure to reinstate agent access
CREATE OR REPLACE PROCEDURE {reinstate_db}.{reinstate_schema}.SP_REINSTATE_AGENT_ACCESS(
   AGENT_NAME STRING, ROLE_NAME STRING
)
RETURNS STRING
LANGUAGE SQL
AS
BEGIN
   EXECUTE IMMEDIATE 'GRANT ROLE AGENT_' || AGENT_NAME || '_ROLE TO ROLE ' || ROLE_NAME;
   RETURN 'Access reinstated for ' || AGENT_NAME;
END;

GRANT USAGE ON DATABASE {reinstate_db} TO APPLICATION SNOWFLAKE;
GRANT USAGE ON SCHEMA {reinstate_db}.{reinstate_schema} TO APPLICATION SNOWFLAKE;
GRANT USAGE ON PROCEDURE {reinstate_db}.{reinstate_schema}.SP_REINSTATE_AGENT_ACCESS(STRING, STRING)
   TO APPLICATION SNOWFLAKE;

CALL {reinstate_budget}!SET_CYCLE_START_ACTION(
   SYSTEM$REFERENCE('PROCEDURE', '{reinstate_db}.{reinstate_schema}.SP_REINSTATE_AGENT_ACCESS(string, string)'),
   ARRAY_CONSTRUCT('{reinstate_agent}', '{reinstate_role}')
);"""
                st.code(sql_reinstate, language="sql")

        else:
            with st.container():
                st.markdown("##### 📊 Budget usage report")
                mon_budget = st.text_input("Budget (fully qualified)", value="BUDGETS_DB.BUDGETS_SCHEMA.MY_BUDGET", key="mon_budget")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    mon_start = st.text_input("Start month (YYYY-MM)", value="2026-01", key="mon_start")
                with col_m2:
                    mon_end = st.text_input("End month (YYYY-MM)", value="2026-04", key="mon_end")

                if st.button("Get usage", key="exec_mon"):
                    try:
                        usage_df = session.sql(
                            f"CALL {mon_budget}!GET_SERVICE_TYPE_USAGE_V2('{mon_start}', '{mon_end}')"
                        ).to_pandas()
                        if usage_df.empty:
                            st.info("No usage data found for this period.")
                        else:
                            st.dataframe(usage_df, hide_index=True, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error: {e}")

            with st.container():
                st.markdown("##### ⚙️ Custom actions configured")
                actions_budget = st.text_input("Budget (fully qualified)", value="BUDGETS_DB.BUDGETS_SCHEMA.MY_BUDGET", key="actions_budget")
                if st.button("List actions", key="exec_actions"):
                    try:
                        actions_df = session.sql(f"CALL {actions_budget}!GET_CUSTOM_ACTIONS()").to_pandas()
                        if actions_df.empty:
                            st.info("No custom actions configured.")
                        else:
                            st.dataframe(actions_df, hide_index=True, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error: {e}")

            with st.container():
                st.markdown("##### ⏳ Enforcement latency")
                st.info(
                    "Budget enforcement runs periodically. Standard budgets may take up to **8 hours** after the budget is exceeded. "
                    "**Low latency budgets** reduce this to **2 hours**. Set an alert at 80% to respond before the 100% action triggers.",
                    icon=":material/schedule:",
                )


with st.sidebar:
    st.divider()
    st.caption(
        "Data source: `SNOWFLAKE.ACCOUNT_USAGE` views\n\n"
        f"Credit rate: ${COST_PER_CREDIT:.2f} | AI credit rate: ${COST_PER_AI_CREDIT:.2f}"
    )
