import os
import json
import pyotp
import datetime
from SmartApi import SmartConnect

# 1. Angel One Authentication Setup
API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_ID = os.getenv("ANGEL_CLIENT_ID")
PASSWORD = os.getenv("ANGEL_PIN")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

def get_session():
    try:
        totp = pyotp.TOTP(TOTP_SECRET).now()
        smartApi = SmartConnect(api_key=API_KEY)
        data = smartApi.generateSession(CLIENT_ID, PASSWORD, totp)
        if data.get('status'):
            print("Authentication Successful")
            return smartApi
        else:
            print("Authentication Failed:", data.get('message'))
            return None
    except Exception as e:
        print("Error during authentication:", e)
        return None

# 2. Main Analytics Engine (Fast & Pure Python - No Heavy Libraries)
def analyze_market_data(smartApi):
    dashboard_data = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "buildup_analysis": [],
        "sector_performance": [],
        "ranking_15min": [],
        "volume_shockers": [],
        "pdh_pdl_breakouts": []
    }

    # F&O Stocks Sample Structure
    # Note: Connect your SmartAPI token loop here for live candles/depth
    stocks_data = [
        {"symbol": "NIFTY", "sector": "INDEX", "ltp": 24200, "pdh": 24150, "pdl": 23950, "oi": 120000, "avg_oi_30d": 95000, "vol_15m": 45000, "avg_vol_22d": 20000, "p_change": 0.8, "oi_change": 5.2},
        {"symbol": "BANKNIFTY", "sector": "INDEX", "ltp": 52100, "pdh": 51900, "pdl": 51600, "oi": 98000, "avg_oi_30d": 85000, "vol_15m": 35000, "avg_vol_22d": 15000, "p_change": 1.1, "oi_change": 6.4},
        {"symbol": "RELIANCE", "sector": "OIL & GAS", "ltp": 2750, "pdh": 2740, "pdl": 2710, "oi": 85000, "avg_oi_30d": 70000, "vol_15m": 12000, "avg_vol_22d": 4000, "p_change": 1.2, "oi_change": 8.1},
        {"symbol": "SBIN", "sector": "BANKING", "ltp": 810, "pdh": 815, "pdl": 795, "oi": 60000, "avg_oi_30d": 65000, "vol_15m": 8000, "avg_vol_22d": 9000, "p_change": -0.6, "oi_change": 4.5},
        {"symbol": "HDFCBANK", "sector": "BANKING", "ltp": 1740, "pdh": 1730, "pdl": 1710, "oi": 110000, "avg_oi_30d": 90000, "vol_15m": 22000, "avg_vol_22d": 10000, "p_change": 0.9, "oi_change": 7.3},
        {"symbol": "TCS", "sector": "IT", "ltp": 4120, "pdh": 4150, "pdl": 4080, "oi": 40000, "avg_oi_30d": 42000, "vol_15m": 2500, "avg_vol_22d": 3000, "p_change": -1.1, "oi_change": -2.3},
        {"symbol": "INFY", "sector": "IT", "ltp": 1850, "pdh": 1870, "pdl": 1840, "oi": 55000, "avg_oi_30d": 50000, "vol_15m": 4000, "avg_vol_22d": 6000, "p_change": -0.8, "oi_change": 3.1}
    ]

    sector_totals = {}
    sector_counts = {}

    for stock in stocks_data:
        # A. Long / Short Buildup & 30-Day OI Comparison
        buildup_type = "Neutral"
        if stock["p_change"] > 0 and stock["oi_change"] > 0:
            buildup_type = "Long Buildup"
        elif stock["p_change"] < 0 and stock["oi_change"] > 0:
            buildup_type = "Short Buildup"
        elif stock["p_change"] > 0 and stock["oi_change"] < 0:
            buildup_type = "Short Covering"
        elif stock["p_change"] < 0 and stock["oi_change"] < 0:
            buildup_type = "Long Unwinding"

        oi_vs_30d_pct = round(((stock["oi"] - stock["avg_oi_30d"]) / stock["avg_oi_30d"]) * 100, 2)

        buildup_item = {
            "symbol": stock["symbol"],
            "buildup": buildup_type,
            "current_oi": stock["oi"],
            "avg_oi_30d": stock["avg_oi_30d"],
            "oi_vs_30d_change_pct": oi_vs_30d_pct,
            "oi_change_pct": stock["oi_change"]
        }
        dashboard_data["buildup_analysis"].append(buildup_item)

        # B. Volume Spurt (22-Day Avg Volume vs Today's 15-Min Volume)
        vol_ratio = round(stock["vol_15m"] / stock["avg_vol_22d"], 2) if stock["avg_vol_22d"] > 0 else 0
        if vol_ratio >= 1.5:
            dashboard_data["volume_shockers"].append({
                "symbol": stock["symbol"],
                "vol_15m": stock["vol_15m"],
                "avg_vol_22d": stock["avg_vol_22d"],
                "volume_multiplier": f"{vol_ratio}x"
            })

        # C. PDH / PDL Breakout Tracker
        breakout_status = "Inside Range"
        if stock["ltp"] > stock["pdh"]:
            breakout_status = "PDH Breakout (Bullish)"
        elif stock["ltp"] < stock["pdl"]:
            breakout_status = "PDL Breakdown (Bearish)"

        if breakout_status != "Inside Range":
            dashboard_data["pdh_pdl_breakouts"].append({
                "symbol": stock["symbol"],
                "ltp": stock["ltp"],
                "pdh": stock["pdh"],
                "pdl": stock["pdl"],
                "status": breakout_status
            })

        # Sector calculation aggregation
        sec = stock["sector"]
        sector_totals[sec] = sector_totals.get(sec, 0) + stock["p_change"]
        sector_counts[sec] = sector_counts.get(sec, 0) + 1

    # D. Sector Heatmap Calculation (Green vs Red)
    for sec in sector_totals:
        avg_change = round(sector_totals[sec] / sector_counts[sec], 2)
        dashboard_data["sector_performance"].append({
            "sector": sec,
            "avg_change_pct": avg_change,
            "status": "Green (Bullish)" if avg_change > 0 else "Red (Bearish)"
        })

    # E. 15-Min Momentum Ranking (Sorted by Highest OI & Price Change)
    sorted_stocks = sorted(dashboard_data["buildup_analysis"], key=lambda x: x["oi_change_pct"], reverse=True)
    for rank, item in enumerate(sorted_stocks, 1):
        if item["buildup"] in ["Long Buildup", "Short Buildup"]:
            dashboard_data["ranking_15min"].append({
                "rank": rank,
                "symbol": item["symbol"],
                "buildup": item["buildup"],
                "oi_change_pct": item["oi_change_pct"]
            })

    # Save finalized data to data.json
    with open("data.json", "w") as f:
        json.dump(dashboard_data, f, indent=4)
        
    print("Market Data updated successfully in data.json")

if __name__ == "__main__":
    session = get_session()
    analyze_market_data(session)
