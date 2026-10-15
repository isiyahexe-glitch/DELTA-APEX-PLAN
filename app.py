import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import json
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="DELTA APEX VIP - Futures & Risk Terminal",
    page_icon="⚡",
    layout="wide"
)

# --- ADVANCED 12D NEON STYLING ---
st.markdown("""
<style>
    .stApp {
        background-color: #06090f;
        color: #e0e6ed;
    }
    .vip-card {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 8px 32px rgba(0, 240, 255, 0.12);
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }
    .vip-title {
        color: #00f0ff;
        text-shadow: 0 0 12px rgba(0, 240, 255, 0.6);
        font-weight: 800;
        letter-spacing: 1.5px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #0088ff, #00f0ff);
        color: #000;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(0, 240, 255, 0.8);
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE STORAGE ---
DATA_FILE = "delta_apex_trades.json"

def load_trades():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_trades(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- LOGIN AUTHENTICATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='vip-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h2 class='vip-title'>⚡ DELTA APEX VIP</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8a99ad; font-size: 13px;'>FUTURES TERMINAL & RISK MANAGEMENT</p>", unsafe_allow_html=True)
        
        passcode = st.text_input("Enter VIP Access Key", type="password")
        if st.button("AUTHORIZE SYSTEM", use_container_width=True):
            if passcode == "apex123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid VIP Passcode!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MAIN DASHBOARD HEADER ---
st.markdown("<h2 class='vip-title'>⚡ DELTA APEX VIP // FUTURES TRADING COMMAND CENTER</h2>", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.markdown("## ⚙️ ACCOUNT CONFIG")
if st.sidebar.button("🔒 Logout System"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.markdown("---")
wallet_balance = st.sidebar.number_input("Wallet Balance ($)", min_value=10.0, value=1000.0, step=50.0)
target_pct = st.sidebar.slider("Daily Target Goal (%)", 0.5, 5.0, 1.0)
sl_pct = st.sidebar.slider("Max Daily Stop Loss (%)", 0.1, 3.0, 0.5)

daily_target_usd = (wallet_balance * target_pct) / 100
daily_sl_usd = (wallet_balance * sl_pct) / 100

st.sidebar.markdown(f"""
<div class='vip-card' style='padding: 12px; font-size: 13px; margin-top: 10px;'>
    <b>Target Goal:</b> <span style='color:#00ff66;'>+${daily_target_usd:.2f} (+{target_pct}%)</span><br>
    <b>Max Risk SL:</b> <span style='color:#ff0055;'>-${daily_sl_usd:.2f} (-{sl_pct}%)</span>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs(["🚀 Futures Position & Risk Calculator", "📝 Daily PnL & Target Tracker", "📊 Performance & Growth Analytics"])

# --- TAB 1: FUTURES RISK & POSITION SIZER ---
with tab1:
    st.markdown("<div class='vip-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #00f0ff;'>🎯 Advanced Futures Position Sizing Calculator</h4>", unsafe_allow_html=True)
    st.markdown("පහත Fields වලට ඔයා trade කරන්න හදන Pair එකේ details දාලා exact Position Size එක සහ Margin එක බලාගන්න.")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        trade_pair = st.text_input("Trading Pair", value="BTC/USDT")
        entry_price = st.number_input("Entry Price ($)", min_value=0.0001, value=65000.0, step=0.1)
        stop_loss_price = st.number_input("Stop Loss Price ($)", min_value=0.0001, value=64350.0, step=0.1)
    
    with col_f2:
        leverage = st.selectbox("Futures Leverage", [5, 10, 20, 25, 50, 75, 100], index=1)
        risk_dollar = st.number_input("Risk Amount ($) for this Trade", min_value=1.0, value=float(daily_sl_usd), step=1.0)
        take_profit_price = st.number_input("Take Profit Price ($)", min_value=0.0001, value=66500.0, step=0.1)

    if st.button("CALCULATE FUTURES POSITION SIZE", use_container_width=True):
        # Calculations
        price_diff_pct = abs(entry_price - stop_loss_price) / entry_price * 100
        if price_diff_pct == 0:
            st.error("Entry price and Stop loss cannot be identical!")
        else:
            position_notional_value = risk_dollar / (price_diff_pct / 100)
            margin_required = position_notional_value / leverage
            reward_dollar = position_notional_value * (abs(take_profit_price - entry_price) / entry_price)
            risk_reward_ratio = reward_dollar / risk_dollar if risk_dollar > 0 else 0

            st.markdown("---")
            st.markdown("<h5 style='color: #00ff66;'>⚡ Calculated Results:</h5>", unsafe_allow_html=True)
            
            res_col1, res_col2, res_col3, res_col4 = st.columns(4)
            res_col1.metric("Position Notional Size", f"${position_notional_value:.2f}")
            res_col2.metric("Margin Required (Margin Size)", f"${margin_required:.2f}", f"{leverage}x Leverage")
            res_col3.metric("Estimated Profit (TP)", f"${reward_dollar:.2f}")
            res_col4.metric("Risk / Reward Ratio", f"1 : {risk_reward_ratio:.2f}")
            
            if margin_required > wallet_balance:
                st.warning("⚠️ Warning: Required margin exceeds your wallet balance! Reduce leverage or position size.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: DAILY TARGET & PnL TRACKER ---
with tab2:
    st.markdown("<div class='vip-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #00f0ff;'>📅 Daily Target & SL Hit Log</h4>", unsafe_allow_html=True)
    
    trade_data = load_trades()
    
    col_t1, col_t2 = st.columns([1, 1.2])
    with col_t1:
        log_date = st.date_input("Log Date", date.today())
        outcome_option = st.selectbox("Trade Result Status", [
            "TARGET HIT (+1.0% / Target Achieved)",
            "STOP LOSS HIT (-0.5% / SL Triggered)",
            "CUSTOM PROFIT %",
            "CUSTOM LOSS / SL %"
        ])
        
        custom_pnl = 0.0
        if "TARGET HIT" in outcome_option:
            custom_pnl = target_pct
        elif "STOP LOSS HIT" in outcome_option:
            custom_pnl = -sl_pct
        elif "CUSTOM PROFIT" in outcome_option:
            custom_pnl = st.number_input("Achieved Profit %", min_value=0.01, value=1.5, step=0.1)
        else:
            custom_pnl = -abs(st.number_input("Loss %", min_value=0.01, value=0.4, step=0.1))
            
        pnl_usd_val = (wallet_balance * custom_pnl) / 100
        note = st.text_input("Trade Setup Note", placeholder="e.g. LTC/USDT breakout long")
        
        if st.button("RECORD TRADE RESULT TO SYSTEM", use_container_width=True):
            entry = {
                "date": str(log_date),
                "pnl_pct": float(custom_pnl),
                "pnl_usd": float(pnl_usd_val),
                "note": note
            }
            # Update if date already exists
            trade_data = [t for t in trade_data if t["date"] != str(log_date)]
            trade_data.append(entry)
            save_trades(trade_data)
            st.success("Trade Log Recorded Successfully!")
            st.rerun()

    with col_t2:
        st.markdown("<h5>📋 Recorded Logs History</h5>", unsafe_allow_html=True)
        if trade_data:
            df_logs = pd.DataFrame(trade_data).sort_values("date", ascending=False)
            st.dataframe(
                df_logs,
                column_config={
                    "date": "Date",
                    "pnl_pct": st.column_config.NumberColumn("PnL (%)", format="%.2f%%"),
                    "pnl_usd": st.column_config.NumberColumn("PnL ($)", format="$%.2f"),
                    "note": "Notes"
                },
                use_container_width=True
            )
            if st.button("🗑️ Clear All Logs"):
                save_trades([])
                st.rerun()
        else:
            st.info("No logs found yet. Record your daily trades here.")
            
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 3: PERFORMANCE & GROWTH ANALYTICS ---
with tab3:
    st.markdown("<div class='vip-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #00f0ff;'>📈 Performance & Equity Growth Curve</h4>", unsafe_allow_html=True)
    
    trade_data = load_trades()
    if trade_data:
        df_perf = pd.DataFrame(trade_data).sort_values("date")
        df_perf["cumulative_pct"] = df_perf["pnl_pct"].cumsum()
        df_perf["cumulative_usd"] = df_perf["pnl_usd"].cumsum()
        
        # Metrics summary
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
        st.info("Add trade history logs in Tab 2 to view equity curves and stats.")
        
    st.markdown("</div>", unsafe_allow_html=True)