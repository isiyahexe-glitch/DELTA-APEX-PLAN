import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import hmac
import json
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="DELTA APEX VIP - XAUUSD Tracker",
    page_icon="⚡",
    layout="wide"
)

# --- USERS (passcode -> user name). Each user has their own saved data. ---
USERS = {
    "apex123": "OWNER",
    "RITHU201": "RITHU",
    "SHAFANI2007": "SHAFANI",
    "SADUNI123": "SADUNI",
    "SASIKOLU": "SASIKOLU",
}

SYMBOL = "XAUUSD"

# --- ADVANCED 12D NEON STYLING ---
st.markdown("""
<style>
    @keyframes gridMove { from {background-position: 0 0;} to {background-position: 0 60px;} }
    @keyframes pulseGlow {
        0%,100% { box-shadow: 0 0 18px rgba(0,240,255,.25), inset 0 0 18px rgba(0,240,255,.05); }
        50%     { box-shadow: 0 0 34px rgba(0,240,255,.55), inset 0 0 26px rgba(0,240,255,.10); }
    }
    @keyframes shimmer { 0% {background-position: 0% 50%;} 100% {background-position: 200% 50%;} }

    .stApp {
        background:
            radial-gradient(1200px 600px at 10% -10%, rgba(0,136,255,.22), transparent 60%),
            radial-gradient(900px 500px at 100% 0%, rgba(176,0,255,.18), transparent 60%),
            linear-gradient(rgba(0,240,255,.04) 1px, transparent 1px) 0 0/60px 60px,
            linear-gradient(90deg, rgba(0,240,255,.04) 1px, transparent 1px) 0 0/60px 60px,
            #05080e;
        animation: gridMove 6s linear infinite;
        color: #e0e6ed;
    }
    .vip-card {
        background: linear-gradient(145deg, rgba(15,23,42,.88), rgba(8,12,24,.88));
        border: 1px solid rgba(0,240,255,.35);
        border-radius: 16px;
        padding: 22px;
        backdrop-filter: blur(14px);
        margin-bottom: 20px;
        animation: pulseGlow 4.5s ease-in-out infinite;
    }
    .vip-title {
        background: linear-gradient(90deg,#00f0ff,#7b61ff,#ff00c8,#00f0ff);
        background-size: 200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: shimmer 5s linear infinite;
        font-weight: 900; letter-spacing: 2px;
    }
    .user-chip {
        display:inline-block; padding:6px 14px; border-radius:999px;
        border:1px solid rgba(0,255,102,.5); color:#00ff66; font-weight:700;
        background:rgba(0,255,102,.08); box-shadow:0 0 14px rgba(0,255,102,.25);
        letter-spacing:1px; font-size:13px;
    }
    .stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {
        background: linear-gradient(45deg, #0088ff, #00f0ff);
        color: #000;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.45);
        transition: all 0.3s ease;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 0 28px rgba(0, 240, 255, 0.9);
    }
    div[data-testid="stMetric"] {
        background: rgba(0,240,255,.05);
        border: 1px solid rgba(0,240,255,.25);
        border-radius: 12px; padding: 12px 14px;
        box-shadow: 0 6px 24px rgba(0,0,0,.45), 0 0 14px rgba(0,240,255,.12);
    }
    div[data-testid="stMetricValue"] { color:#00f0ff; text-shadow:0 0 10px rgba(0,240,255,.6); }
    .stTabs [aria-selected="true"] { color:#00f0ff !important; text-shadow:0 0 10px rgba(0,240,255,.7); }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg,#070c16,#0a1020);
        border-right: 1px solid rgba(0,240,255,.2);
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE STORAGE (separate files per user) ---
DATA_DIR = "apex_data"
os.makedirs(DATA_DIR, exist_ok=True)

def _file(user, kind):
    return os.path.join(DATA_DIR, f"{user.lower()}_{kind}.json")

def _load(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return default
    return default

def _save(path, data):
    # write to a temp file first so a crash can never corrupt saved data
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=4)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def load_trades(user):
    return _load(_file(user, "trades"), [])

def save_trades(user, data):
    _save(_file(user, "trades"), data)

DEFAULT_SETTINGS = {"wallet": 1000.0, "target_pct": 1.0, "sl_pct": 0.5}

def load_settings(user):
    s = dict(DEFAULT_SETTINGS)
    s.update(_load(_file(user, "settings"), {}))
    return s

# --- LOGIN AUTHENTICATION ---
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("username", None)

def check_passcode(code):
    found = None
    for key, name in USERS.items():
        if hmac.compare_digest(code.encode(), key.encode()):
            found = name
    return found

if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='vip-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h2 class='vip-title'>⚡ DELTA APEX VIP</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8a99ad; font-size: 13px;'>XAUUSD DAILY TRACKER</p>", unsafe_allow_html=True)

        with st.form("login_form"):
            passcode = st.text_input("Enter VIP Access Key", type="password")
            submitted = st.form_submit_button("AUTHORIZE SYSTEM", use_container_width=True)
        if submitted:
            user = check_passcode(passcode.strip())
            if user:
                st.session_state.authenticated = True
                st.session_state.username = user
                st.rerun()
            else:
                st.error("Invalid VIP Passcode!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

USER = st.session_state.username
settings = load_settings(USER)

# --- MAIN DASHBOARD HEADER ---
st.markdown("<h2 class='vip-title'>⚡ DELTA APEX VIP // XAUUSD DAILY TRACKER</h2>", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.markdown("## ⚙️ ACCOUNT CONFIG")
st.sidebar.markdown(f"<span class='user-chip'>👤 {USER}</span>", unsafe_allow_html=True)
if st.sidebar.button("🔒 Logout System"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

st.sidebar.markdown("---")
wallet_balance = st.sidebar.number_input("Wallet Balance ($)", min_value=10.0, value=float(settings["wallet"]), step=50.0)
target_pct = st.sidebar.slider("Daily Target Goal (%)", 0.5, 5.0, float(settings["target_pct"]))
sl_pct = st.sidebar.slider("Max Daily Stop Loss (%)", 0.1, 3.0, float(settings["sl_pct"]))

new_settings = {"wallet": wallet_balance, "target_pct": target_pct, "sl_pct": sl_pct}
if new_settings != {k: settings[k] for k in new_settings}:
    _save(_file(USER, "settings"), new_settings)

daily_target_usd = (wallet_balance * target_pct) / 100
daily_sl_usd = (wallet_balance * sl_pct) / 100

st.sidebar.markdown(f"""
<div class='vip-card' style='padding: 12px; font-size: 13px; margin-top: 10px;'>
    <b>Target Goal:</b> <span style='color:#00ff66;'>+${daily_target_usd:.2f} (+{target_pct}%)</span><br>
    <b>Max Risk SL:</b> <span style='color:#ff0055;'>-${daily_sl_usd:.2f} (-{sl_pct}%)</span>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION TABS ---
tab2, tab3 = st.tabs(["📝 Daily PnL & Target Tracker", "📊 Performance & Growth Analytics"])

# --- TAB: DAILY TARGET & PnL TRACKER ---
with tab2:
    st.markdown("<div class='vip-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #00f0ff;'>📅 Daily Target & SL Hit Log</h4>", unsafe_allow_html=True)

    flash = st.session_state.pop("flash", None)
    if flash:
        st.success(flash)

    trade_data = load_trades(USER)

    col_t1, col_t2 = st.columns([1, 1.2])
    with col_t1:
        log_date = st.date_input("Log Date", date.today())
        outcome_option = st.selectbox("Trade Result Status", [
            f"TARGET HIT (+{target_pct}%)",
            f"STOP LOSS HIT (-{sl_pct}%)",
            "CUSTOM PROFIT %",
            "CUSTOM LOSS %"
        ])

        if outcome_option.startswith("TARGET HIT"):
            custom_pnl = target_pct
        elif outcome_option.startswith("STOP LOSS HIT"):
            custom_pnl = -sl_pct
        elif outcome_option == "CUSTOM PROFIT %":
            custom_pnl = st.number_input("Achieved Profit %", min_value=0.01, value=1.5, step=0.1)
        else:
            custom_pnl = -abs(st.number_input("Loss %", min_value=0.01, value=0.4, step=0.1))

        pnl_usd_val = (wallet_balance * custom_pnl) / 100
        st.caption(f"Result: **{custom_pnl:+.2f}%  →  ${pnl_usd_val:+.2f}**")
        note = st.text_input("Trade Setup Note", placeholder="e.g. XAUUSD breakout buy")

        existing = [t for t in trade_data if t["date"] == str(log_date)]
        if existing:
            st.info(f"A log for {log_date} already exists. Saving will update it.")

        if st.button("RECORD TRADE RESULT TO SYSTEM", use_container_width=True):
            entry = {
                "date": str(log_date),
                "symbol": SYMBOL,
                "pnl_pct": float(custom_pnl),
                "pnl_usd": float(pnl_usd_val),
                "note": note
            }
            trade_data = [t for t in trade_data if t["date"] != str(log_date)]
            trade_data.append(entry)
            save_trades(USER, trade_data)
            st.session_state["flash"] = f"✅ Saved {log_date}: {custom_pnl:+.2f}% (${pnl_usd_val:+.2f})"
            st.rerun()

    with col_t2:
        st.markdown("<h5>📋 Recorded Logs History</h5>", unsafe_allow_html=True)
        if trade_data:
            df_logs = pd.DataFrame(trade_data).sort_values("date", ascending=False)
            if "symbol" not in df_logs:
                df_logs["symbol"] = SYMBOL
            st.dataframe(
                df_logs[["date", "symbol", "pnl_pct", "pnl_usd", "note"]],
                column_config={
                    "date": "Date",
                    "symbol": "Symbol",
                    "pnl_pct": st.column_config.NumberColumn("PnL (%)", format="%.2f%%"),
                    "pnl_usd": st.column_config.NumberColumn("PnL ($)", format="$%.2f"),
                    "note": "Notes"
                },
                use_container_width=True,
                hide_index=True
            )

            d1, d2 = st.columns(2)
            with d1:
                del_date = st.selectbox("Delete a day", sorted({t["date"] for t in trade_data}, reverse=True))
                if st.button("Delete Selected Day", use_container_width=True):
                    save_trades(USER, [t for t in trade_data if t["date"] != del_date])
                    st.rerun()
            with d2:
                confirm = st.checkbox("Confirm clear ALL logs")
                if st.button("🗑️ Clear All Logs", use_container_width=True, disabled=not confirm):
                    save_trades(USER, [])
                    st.rerun()
        else:
            st.info("No logs found yet. Record your daily trades here.")

        # --- BACKUP / RESTORE ---
        st.markdown("---")
        st.markdown("##### 💾 Backup / Restore")
        st.caption("Download a backup now and then, so your data is safe even if the server restarts.")
        st.download_button(
            "⬇️ Download My Backup",
            data=json.dumps(trade_data, indent=4),
            file_name=f"{USER.lower()}_xauusd_backup.json",
            mime="application/json",
            use_container_width=True,
        )
        uploaded = st.file_uploader("Restore from backup (.json)", type="json")
        if uploaded is not None and st.button("Restore Backup", use_container_width=True):
            try:
                restored = json.load(uploaded)
                ok = isinstance(restored, list) and all(
                    isinstance(t, dict) and {"date", "pnl_pct", "pnl_usd"} <= t.keys() for t in restored
                )
                if ok:
                    save_trades(USER, restored)
                    st.session_state["flash"] = f"✅ Restored {len(restored)} logs."
                    st.rerun()
                else:
                    st.error("That file doesn't look like a valid backup.")
            except json.JSONDecodeError:
                st.error("Could not read that file.")

    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB: PERFORMANCE & GROWTH ANALYTICS ---
with tab3:
    st.markdown("<div class='vip-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #00f0ff;'>📈 Performance & Equity Growth Curve</h4>", unsafe_allow_html=True)

    trade_data = load_trades(USER)
    if trade_data:
        df_perf = pd.DataFrame(trade_data).sort_values("date")
        df_perf["cumulative_pct"] = df_perf["pnl_pct"].cumsum()
        df_perf["cumulative_usd"] = df_perf["pnl_usd"].cumsum()

        m1, m2, m3 = st.columns(3)
        total_pnl_pct = df_perf["pnl_pct"].sum()
        total_pnl_usd = df_perf["pnl_usd"].sum()
        win_rate = (len(df_perf[df_perf["pnl_pct"] > 0]) / len(df_perf)) * 100

        m1.metric("Net Total Return (%)", f"{total_pnl_pct:+.2f}%")
        m2.metric("Net Total Profit ($)", f"${total_pnl_usd:+.2f}")
        m3.metric("Strategy Win Rate", f"{win_rate:.0f}%")

        st.markdown("---")

        fig = px.line(df_perf, x="date", y="cumulative_pct", markers=True, title="Cumulative Return Curve (%) over Time")
        fig.update_traces(line_color="#00f0ff", line_width=3, marker=dict(size=8, color="#00ff66"))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e6ed",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add trade history logs in the Daily Tracker tab to view equity curves and stats.")

    st.markdown("</div>", unsafe_allow_html=True)
