"""
DISCLAIMER: 

This software is provided solely for educational and research purposes. 
It is not intended to provide investment advice, and no investment recommendations are made herein. 
The developers are not financial advisors and accept no responsibility for any financial decisions or losses resulting from the use of this software. 
Always consult a professional financial advisor before making any investment decisions.
"""

import yfinance as yf
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import numpy as np
import concurrent.futures
import time
import smtplib
import sys
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# 强制 stdout/stderr 使用 UTF-8，避免 Windows cmd 编码报错
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ══════════════════════════════════════════════════════════════
#  📧  邮件配置  —  请修改以下三行
# ══════════════════════════════════════════════════════════════
EMAIL_SENDER   = os.environ.get('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')  # Gmail 应用专用密码（16位）
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', '')
# ══════════════════════════════════════════════════════════════

# ── Russell 1000 成分股 ───────────────────────────────────────────────────────
RUSSELL1000 = [
    "A", "AAL", "AAP", "AAPL", "ABBV", "ABNB", "ABT", "ACHC", "ACN", "ADBE",
    "ADC", "ADI", "ADP", "AEE", "AEO", "AEP", "AES", "AFL", "AIZ", "AJG",
    "AKAM", "ALB", "ALGN", "ALK", "ALL", "ALLE", "ALLY", "AMAT", "AMD", "AME",
    "AMG", "AMGN", "AMT", "AMZN", "AN", "ANF", "ANSS", "AON", "AOS", "APA",
    "APD", "APO", "APTV", "AR", "ARE", "ARES", "ANET", "ATMU", "ATO", "ATI",
    "AVB", "AVGO", "AVT", "AVTR", "AVY", "AWK", "AX", "AXON", "AXP", "AYI",
    "AZO", "AZZ",
    "BA", "BAC", "BALL", "BAX", "BBY", "BDX", "BEN", "BJ", "BJRI", "BK",
    "BKH", "BKR", "BLK", "BLMN", "BLDR", "BLK", "BMY", "BMRN", "BKNG",
    "BOOT", "BOX", "BRC", "BRBR", "BRK-B", "BRO", "BRT", "BSX", "BURL",
    "BWA", "BX", "BXP", "BYD", "BWXT",
    "C", "CABO", "CAG", "CAH", "CAKE", "CALX", "CARG", "CARR", "CASY",
    "CAT", "CB", "CBOE", "CBRE", "CCK", "CDW", "CDAY", "CDMO", "CDNS",
    "CE", "CEG", "CG", "CFG", "CF", "CHTR", "CHRW", "CHD", "CHWY",
    "CI", "CIEN", "CINF", "CIVI", "CLF", "CLH", "CLX", "CMC", "CME",
    "CMG", "CMI", "CMS", "CNC", "CNO", "CNS", "CNX", "CO", "COF",
    "COHU", "COLM", "COP", "COOP", "COR", "COST", "COO", "CPB", "CPT",
    "CR", "CG", "CRGY", "CRI", "CROX", "CRWD", "CRL", "CRM", "CSX",
    "CTSH", "CTVA", "CUBE", "CUZ", "CVS", "CVX", "CVLT", "CWT", "CZR",
    "D", "DAL", "DAR", "DDOG", "DD", "DE", "DECK", "DG", "DHI", "DHR",
    "DIN", "DIOD", "DIS", "DKS", "DLTR", "DKNG", "DLR", "DOW", "DPZ",
    "DRH", "DRI", "DRVN", "DT", "DTE", "DUK", "DVA", "DVN",
    "E", "EAT", "EBC", "ECL", "ED", "EG", "EGP", "EHC", "EIX", "EL",
    "ELV", "EMN", "EMR", "ENS", "ENPH", "EPC", "EPAM", "EPRT", "EQR",
    "EQIX", "EQT", "ERIE", "ESE", "ESS", "ETN", "ETSY", "ETR", "EVR",
    "EVRG", "EW", "EXC", "EXPE", "EXPD", "EXP",
    "F", "FANG", "FARO", "FAST", "FCNCA", "FDS", "FDX", "FE", "FHN",
    "FICO", "FI", "FIS", "FITB", "FIZZ", "FL", "FLS", "FLT", "FMC",
    "FNB", "FOX", "FOXA", "FOUR", "FRT", "FSS", "FTV", "FUL", "FUN",
    "G", "GATX", "GBCI", "GD", "GDDY", "GE", "GEV", "GFF", "GFS",
    "GFI", "GIII", "GILD", "GIS", "GME", "GM", "GMS", "GOOG", "GOOGL",
    "GPS", "GPRE", "GPC", "GPN", "GS", "GSK", "GTX", "GWW", "GXO",
    "HA", "HAL", "HALO", "HAS", "HBAN", "HCA", "HCC", "HD", "HEES",
    "HES", "HGV", "HIG", "HII", "HIW", "HLT", "HMN", "HNI", "HON",
    "HOLX", "HOMB", "HRL", "HST", "HSIC", "HUBS", "HUM", "HXL", "HZO",
    "IBM", "IBP", "ICE", "IDA", "IDEX", "IDXX", "IEX", "IFF", "ILMN",
    "INCY", "INDB", "INTC", "INTU", "INVH", "IONS", "IPGP", "IQV",
    "IR", "IRDM", "IRM", "ISRG", "ITW", "IVZ",
    "JACK", "JBHT", "JELD", "JCI", "JLL", "JKHY", "JNJ", "JNPR",
    "JPM", "JWN",
    "K", "KALU", "KBH", "KEY", "KFRC", "KIM", "KKR", "KMI", "KMT",
    "KNX", "KNSL", "KO", "KR", "KDP", "KHC", "KMPR",
    "L", "LBRT", "LCII", "LEA", "LEN", "LGIH", "LH", "LHX", "LII",
    "LIN", "LKQ", "LMT", "LNN", "LNTH", "LOPE", "LOW", "LPX",
    "LRCX", "LSTR", "LULU", "LUV", "LVS", "LW", "LXP", "LYB", "LZB", "LYV",
    "M", "MA", "MAR", "MAS", "MAT", "MATX", "MCK", "MCO", "MCD",
    "MCHP", "MCY", "MDT", "MDU", "MEDP", "META", "MET", "MGEE",
    "MGNI", "MGM", "MHO", "MKC", "MKTX", "MLM", "MMC", "MMM",
    "MMS", "MNK", "MNRO", "MO", "MOH", "MOS", "MOG-A", "MPC",
    "MPWR", "MRC", "MRK", "MRO", "MS", "MSA", "MSCI", "MSFT",
    "MTRN", "MTX", "MU", "MUR", "MVF",
    "NDAQ", "NBTB", "NCR", "NCLH", "NDSN", "NEE", "NEM", "NET",
    "NHI", "NI", "NKE", "NMI", "NMIH", "NOC", "NSA", "NSC", "NSIT",
    "NTAP", "NUE", "NUS", "NVR", "NXPI",
    "O", "ODFL", "OFG", "OGS", "OHI", "OI", "OKE", "OLLI",
    "OMCL", "OMC", "ONON", "OPCH", "ORCL", "ORLY", "OSIS", "OSK",
    "OTIS", "OTTR", "OXY",
    "PANW", "PARA", "PATK", "PAYX", "PBI", "PCAR", "PCTY", "PDC",
    "PFE", "PFGC", "PH", "PHIN", "PHM", "PIPR", "PKG", "PLD",
    "PLTR", "PLXS", "PM", "PNC", "PNFP", "POOL", "POST", "PPG",
    "PPL", "PRGO", "PRU", "PSA", "PSX", "PTC", "PVH", "PYPL",
    "QSR", "QLYS", "QCOM", "QRVO", "QTWO",
    "R", "RBC", "RCL", "RDN", "RDNT", "REG", "REGN", "REZI",
    "RF", "RJF", "RLI", "RL", "RMR", "ROAD", "ROCK", "ROK",
    "ROL", "ROIC", "ROST", "RPM", "RS", "RSG", "RTX", "RRR",
    "RXO", "RYN",
    "SAIA", "SBAC", "SBRA", "SBCF", "SBSI", "SCHW", "SCI", "SCSC",
    "SEDG", "SEM", "SEE", "SF", "SFNC", "SGRY", "SHO", "SHW",
    "SIG", "SITC", "SIRI", "SIX", "SKT", "SKX", "SKYW", "SLGN",
    "SLB", "SLM", "SNOW", "SNBR", "SOLV", "SON", "SONO", "SO",
    "SPG", "SPR", "SPXC", "SRCL", "SRE", "SSD", "SSB",
    "STT", "STC", "STLD", "STNG", "STRA", "STX", "SWK", "SWX",
    "SXT", "SYF", "SYY",
    "T", "TAP", "TDG", "TDOC", "TEAM", "TEX", "TFC", "TFX",
    "TGT", "THC", "THRY", "TILE", "TJX", "TMO", "TMUS", "TNC",
    "TOL", "TOWN", "TPR", "TRGP", "TRMB", "TRN", "TRV", "TRTX",
    "TRUP", "TSCO", "TSLA", "TTGT", "TTMI", "TT", "TXN",
    "TXRH",
    "UAL", "UCB", "UFI", "UFPI", "UHS", "UMBF", "UNF", "UNH",
    "UNP", "UNVR", "UPS", "URI", "USB", "UDR", "UVV",
    "V", "VAC", "VFC", "VIAV", "VICR", "VIRT", "VMC", "VNOM",
    "VSEC", "VSTS", "VTR", "VVV", "VZ",
    "W", "WAB", "WAT", "WBA", "WBD", "WDAY", "WDC", "WDFC",
    "WEC", "WELL", "WEN", "WEX", "WFC", "WM", "WMB", "WMT",
    "WOLF", "WOR", "WRLD", "WMS", "WSO", "WTW", "WTS", "WWW",
    "XPEL", "XHR", "XOM", "XPO", "XRAY", "XRX",
    "YELP", "YETI", "YUM",
    "Z", "ZBH", "ZI", "ZION", "ZS",
]

# ── 核心计算函数 ───────────────────────────────────────────────────────────────

def filter_dates(dates):
    today = datetime.today().date()
    cutoff_date = today + timedelta(days=45)
    sorted_dates = sorted(datetime.strptime(date, "%Y-%m-%d").date() for date in dates)
    arr = []
    for i, date in enumerate(sorted_dates):
        if date >= cutoff_date:
            arr = [d.strftime("%Y-%m-%d") for d in sorted_dates[:i+1]]
            break
    if len(arr) > 0:
        if arr[0] == today.strftime("%Y-%m-%d"):
            return arr[1:]
        return arr
    raise ValueError("No date 45 days or more in the future found.")


def yang_zhang(price_data, window=30, trading_periods=252, return_last_only=True):
    log_ho = (price_data['High'] / price_data['Open']).apply(np.log)
    log_lo = (price_data['Low'] / price_data['Open']).apply(np.log)
    log_co = (price_data['Close'] / price_data['Open']).apply(np.log)
    log_oc = (price_data['Open'] / price_data['Close'].shift(1)).apply(np.log)
    log_oc_sq = log_oc**2
    log_cc = (price_data['Close'] / price_data['Close'].shift(1)).apply(np.log)
    log_cc_sq = log_cc**2
    rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)
    close_vol = log_cc_sq.rolling(window=window, center=False).sum() * (1.0 / (window - 1.0))
    open_vol = log_oc_sq.rolling(window=window, center=False).sum() * (1.0 / (window - 1.0))
    window_rs = rs.rolling(window=window, center=False).sum() * (1.0 / (window - 1.0))
    k = 0.34 / (1.34 + ((window + 1) / (window - 1)))
    result = (open_vol + k * close_vol + (1 - k) * window_rs).apply(np.sqrt) * np.sqrt(trading_periods)
    if return_last_only:
        return result.iloc[-1]
    return result.dropna()


def build_term_structure(days, ivs):
    days = np.array(days)
    ivs = np.array(ivs)
    sort_idx = days.argsort()
    days = days[sort_idx]
    ivs = ivs[sort_idx]
    spline = interp1d(days, ivs, kind='linear', fill_value="extrapolate")
    def term_spline(dte):
        if dte < days[0]:
            return ivs[0]
        elif dte > days[-1]:
            return ivs[-1]
        else:
            return float(spline(dte))
    return term_spline


def get_current_price(ticker):
    todays_data = ticker.history(period='1d')
    return todays_data['Close'].iloc[0]


def get_earnings_info(stock):
    """
    获取财报日期和时间（BMO/AMC）。
    使用 stock.info 的 earningsTimestamp 字段，比 calendar 更准确。

    返回: (earnings_date, earnings_time, confirmed)
      earnings_date : datetime.date 或 None
      earnings_time : 'BMO' / 'AMC' / 'Unknown'
      confirmed     : True = 日期已确认，False = 估算日期
    """
    try:
        info = stock.info
        if not info:
            return None, 'Unknown', False

        # ── 财报日期：用 earningsTimestamp 转美东时间，避免时区偏差 ──
        ts = info.get('earningsTimestamp') or info.get('earningsTimestampStart')
        if not ts:
            return None, 'Unknown', False

        import pytz
        et_tz   = pytz.timezone('America/New_York')
        dt_et   = datetime.fromtimestamp(ts, tz=et_tz)
        edate   = dt_et.date()
        hour_et = dt_et.hour

        # ── BMO / AMC 判断：美东时间 ──
        # 盘前公布通常在 4:00-9:30（hour < 9 或 hour == 9 且 minute < 30）
        # 盘后公布通常在 16:00 之后（hour >= 16）
        if hour_et < 10:
            etime = 'BMO'
        elif hour_et >= 16:
            etime = 'AMC'
        else:
            etime = 'Unknown'

        # ── 是否为估算日期 ──
        confirmed = not info.get('isEarningsDateEstimate', True)

        return edate, etime, confirmed

    except Exception:
        # 降级：尝试从 calendar dict 读取
        try:
            cal = stock.calendar
            if not cal or 'Earnings Date' not in cal:
                return None, 'Unknown', False
            dates = cal['Earnings Date']
            if not dates:
                return None, 'Unknown', False
            val = dates[0]
            edate = val if isinstance(val, type(datetime.today().date())) else val.date() if hasattr(val, 'date') else datetime.strptime(str(val)[:10], "%Y-%m-%d").date()
            return edate, 'Unknown', False
        except Exception:
            return None, 'Unknown', False


def compute_recommendation(ticker_symbol):
    ticker_symbol = ticker_symbol.strip().upper()
    stock = yf.Ticker(ticker_symbol)

    # ── 财报日期过滤（1-3天内） ──────────────────────────────────────
    today = datetime.today().date()
    earnings_date, earnings_time, earnings_confirmed = get_earnings_info(stock)

    if earnings_date is None:
        return None  # 无财报信息，跳过

    days_to_earnings = (earnings_date - today).days
    if not (1 <= days_to_earnings <= 3):
        return None  # 不在1-3天窗口内，跳过
    # ────────────────────────────────────────────────────────────────

    if not stock.options or len(stock.options) == 0:
        return None

    exp_dates = list(stock.options)
    try:
        exp_dates = filter_dates(exp_dates)
    except Exception:
        return None

    options_chains = {d: stock.option_chain(d) for d in exp_dates}

    underlying_price = get_current_price(stock)
    if underlying_price is None:
        return None

    atm_iv = {}
    straddle = None
    for i, (exp_date, chain) in enumerate(options_chains.items()):
        calls, puts = chain.calls, chain.puts
        if calls.empty or puts.empty:
            continue
        call_idx = (calls['strike'] - underlying_price).abs().idxmin()
        put_idx  = (puts['strike']  - underlying_price).abs().idxmin()
        call_iv  = calls.loc[call_idx, 'impliedVolatility']
        put_iv   = puts.loc[put_idx,  'impliedVolatility']
        atm_iv[exp_date] = (call_iv + put_iv) / 2.0
        if i == 0:
            call_mid = (calls.loc[call_idx, 'bid'] + calls.loc[call_idx, 'ask']) / 2.0
            put_mid  = (puts.loc[put_idx,  'bid'] + puts.loc[put_idx,  'ask']) / 2.0
            straddle = call_mid + put_mid

    if not atm_iv:
        return None

    today = datetime.today().date()
    dtes, ivs = [], []
    for exp_date, iv in atm_iv.items():
        days_to_expiry = (datetime.strptime(exp_date, "%Y-%m-%d").date() - today).days
        dtes.append(days_to_expiry)
        ivs.append(iv)

    term_spline   = build_term_structure(dtes, ivs)
    ts_slope_0_45 = (term_spline(45) - term_spline(dtes[0])) / (45 - dtes[0])

    price_history = stock.history(period='3mo')
    iv30_rv30     = term_spline(30) / yang_zhang(price_history)
    avg_volume    = price_history['Volume'].rolling(30).mean().dropna().iloc[-1]
    expected_move = f"{round(straddle / underlying_price * 100, 2)}%" if straddle else "N/A"

    return {
        'ticker':              ticker_symbol,
        'avg_volume':          avg_volume >= 1_500_000,
        'iv30_rv30':           iv30_rv30 >= 1.25,
        'ts_slope_0_45':       ts_slope_0_45 <= -0.00406,
        'iv30_rv30_val':       round(iv30_rv30, 3),
        'ts_slope_val':        round(ts_slope_0_45, 6),
        'expected_move':       expected_move,
        'price':               round(underlying_price, 2),
        'earnings_date':       earnings_date.strftime("%Y-%m-%d"),
        'earnings_time':       earnings_time,       # BMO / AMC / Unknown
        'earnings_confirmed':  earnings_confirmed,  # True / False
        'days_to_earnings':    days_to_earnings,
    }


# ── 批量扫描 ──────────────────────────────────────────────────────────────────

def scan_all(tickers=RUSSELL1000, max_workers=4):
    results_all = []
    errors      = []
    passed      = []
    total       = len(tickers)

    print(f"\n{'='*60}")
    print(f"  Russell 1000 期权扫描器  |  共 {total} 只股票")
    print(f"  扫描条件：avg_volume ✓  iv30_rv30 ✓  ts_slope_0_45 ✓")
    print(f"{'='*60}\n")

    def _worker(sym, retries=3):
        for attempt in range(retries + 1):
            try:
                return sym, compute_recommendation(sym), None
            except Exception as e:
                if attempt < retries:
                    time.sleep(attempt + 1)  # 1秒, 2秒, 3秒
                else:
                    return sym, None, str(e)

    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_worker, sym): sym for sym in tickers}
        for future in concurrent.futures.as_completed(futures):
            sym, result, err = future.result()
            completed += 1
            pct = completed / total * 100
            bar = ('█' * int(pct // 5)).ljust(20)
            print(f"\r  [{bar}] {completed}/{total}  ({pct:.0f}%)  当前: {sym:<6}", end='', flush=True)

            if err:
                errors.append((sym, err))
            elif result is not None:
                results_all.append(result)
                if result['avg_volume'] and result['iv30_rv30'] and result['ts_slope_0_45']:
                    passed.append(result)

    print(f"\n\n{'='*60}")
    print(f"  扫描完成！成功处理 {len(results_all)} / {total} 只")
    if errors:
        print(f"  ⚠  跳过/出错: {len(errors)} 只  ({', '.join(s for s,_ in errors[:10])}{'...' if len(errors)>10 else ''})")
    print(f"{'='*60}\n")

    return passed, results_all, errors


def print_results(passed, results_all):
    print(f"{'━'*72}")
    print(f"  ✅  满足全部三项条件（含财报过滤）：{len(passed)} 只")
    print(f"{'━'*72}")
    if passed:
        header = f"  {'代码':<8} {'股价':>8} {'IV30/RV30':>10} {'TS斜率':>12} {'预期波幅':>10} {'财报日期':>12} {'时间':>5} {'确认':>4}"
        print(header)
        print(f"  {'-'*70}")
        for r in sorted(passed, key=lambda x: x['iv30_rv30_val'], reverse=True):
            confirmed_mark = '✓' if r['earnings_confirmed'] else '?'
            print(f"  {r['ticker']:<8} ${r['price']:>7.2f} {r['iv30_rv30_val']:>10.3f} {r['ts_slope_val']:>12.6f} {r['expected_move']:>10} {r['earnings_date']:>12} {r['earnings_time']:>5} {confirmed_mark:>4}")
    else:
        print("  （暂无满足全部条件且有近期财报的股票）")

    print(f"\n{'━'*60}")
    print(f"  📊  条件通过统计（共 {len(results_all)} 只有效数据）")
    print(f"{'━'*60}")
    v_pass = sum(1 for r in results_all if r['avg_volume'])
    i_pass = sum(1 for r in results_all if r['iv30_rv30'])
    t_pass = sum(1 for r in results_all if r['ts_slope_0_45'])
    print(f"  avg_volume   ≥ 1,500,000 : {v_pass:>4} 只通过")
    print(f"  iv30_rv30    ≥ 1.25      : {i_pass:>4} 只通过")
    print(f"  ts_slope_0_45 ≤ -0.00406 : {t_pass:>4} 只通过")

    def exactly_two(r):
        return sum([r['avg_volume'], r['iv30_rv30'], r['ts_slope_0_45']]) == 2

    two_groups = {
        ('avg_volume', 'iv30_rv30'):    ('V✓ I✓ T✗', '成交量 ✓  IV/RV ✓  TS斜率 ✗'),
        ('avg_volume', 'ts_slope_0_45'):('V✓ I✗ T✓', '成交量 ✓  IV/RV ✗  TS斜率 ✓'),
        ('iv30_rv30',  'ts_slope_0_45'):('V✗ I✓ T✓', '成交量 ✗  IV/RV ✓  TS斜率 ✓'),
    }

    any_two = False
    for (k1, k2), (short, label) in two_groups.items():
        group = [r for r in results_all
                 if r[k1] and r[k2] and sum([r['avg_volume'], r['iv30_rv30'], r['ts_slope_0_45']]) == 2]
        if group:
            if not any_two:
                print(f"\n{'━'*60}")
                print(f"  🟡  满足两项条件的股票（按组合分类）")
                print(f"{'━'*60}")
                any_two = True
            print(f"\n  [{short}]  {label}  —  共 {len(group)} 只")
            print(f"  {'代码':<8} {'股价':>8} {'IV30/RV30':>10} {'TS斜率':>12} {'预期波幅':>10}")
            print(f"  {'-'*56}")
            for r in sorted(group, key=lambda x: x['iv30_rv30_val'], reverse=True):
                print(f"  {r['ticker']:<8} ${r['price']:>7.2f} {r['iv30_rv30_val']:>10.3f} {r['ts_slope_val']:>12.6f} {r['expected_move']:>10}")

    if not any_two:
        print(f"\n  🟡  暂无恰好满足两项条件的股票")

    print(f"\n{'━'*60}")
    print("  免责声明：仅供学习研究，不构成投资建议。")
    print(f"{'━'*60}\n")


def build_email_html(passed, results_all, scan_time):
    date_str = scan_time.strftime("%Y-%m-%d")
    time_str = scan_time.strftime("%H:%M")

    def row_color(i):
        return "#f9f9f9" if i % 2 == 0 else "#ffffff"

    def result_table(rows):
        if not rows:
            return "<p style='color:#888'>（无）</p>"
        html = """
        <table style='border-collapse:collapse;width:100%;font-size:13px;font-family:monospace'>
          <thead>
            <tr style='background:#7b3f00;color:#fff'>
              <th style='padding:8px 12px;text-align:left'>代码</th>
              <th style='padding:8px 12px;text-align:right'>股价</th>
              <th style='padding:8px 12px;text-align:right'>IV30/RV30</th>
              <th style='padding:8px 12px;text-align:right'>TS斜率</th>
              <th style='padding:8px 12px;text-align:right'>预期波幅</th>
              <th style='padding:8px 12px;text-align:center'>财报日期</th>
              <th style='padding:8px 12px;text-align:center'>时间</th>
            </tr>
          </thead><tbody>"""
        for i, r in enumerate(sorted(rows, key=lambda x: x['iv30_rv30_val'], reverse=True)):
            etime = r.get('earnings_time', 'Unknown')
            etime_color = '#1a6600' if etime == 'BMO' else '#990000' if etime == 'AMC' else '#888888'
            edate_str = r.get('earnings_date', 'N/A')
            confirmed  = r.get('earnings_confirmed', True)
            edate_label = edate_str if confirmed else f"{edate_str} ⚠️未确认"
            edate_color = '#000' if confirmed else '#cc6600'
            html += f"""
            <tr style='background:{row_color(i)}'>
              <td style='padding:7px 12px;font-weight:bold'>{r['ticker']}</td>
              <td style='padding:7px 12px;text-align:right'>${r['price']:.2f}</td>
              <td style='padding:7px 12px;text-align:right'>{r['iv30_rv30_val']:.3f}</td>
              <td style='padding:7px 12px;text-align:right'>{r['ts_slope_val']:.6f}</td>
              <td style='padding:7px 12px;text-align:right'>{r['expected_move']}</td>
              <td style='padding:7px 12px;text-align:center;color:{edate_color}'>{edate_label}</td>
              <td style='padding:7px 12px;text-align:center;font-weight:bold;color:{etime_color}'>{etime}</td>
            </tr>"""
        html += "</tbody></table>"
        return html

    v_pass = sum(1 for r in results_all if r['avg_volume'])
    i_pass = sum(1 for r in results_all if r['iv30_rv30'])
    t_pass = sum(1 for r in results_all if r['ts_slope_0_45'])
    total  = len(results_all)

    two_groups = [
        ('avg_volume', 'iv30_rv30',    'V✓ I✓ T✗', '成交量 ✓  IV/RV ✓  TS斜率 ✗'),
        ('avg_volume', 'ts_slope_0_45','V✓ I✗ T✓', '成交量 ✓  IV/RV ✗  TS斜率 ✓'),
        ('iv30_rv30',  'ts_slope_0_45','V✗ I✓ T✓', '成交量 ✗  IV/RV ✓  TS斜率 ✓'),
    ]
    two_sections = ""
    for k1, k2, short, label in two_groups:
        grp = [r for r in results_all
               if r[k1] and r[k2] and sum([r['avg_volume'], r['iv30_rv30'], r['ts_slope_0_45']]) == 2]
        if grp:
            two_sections += f"""
            <h3 style='color:#b8860b;margin:20px 0 8px'>[{short}] {label} — {len(grp)} 只</h3>
            {result_table(grp)}"""

    subject_prefix = f"🟢 {len(passed)} 只全满足" if passed else "⚪ 今日无全满足"

    html = f"""
    <!DOCTYPE html><html><body style='font-family:Arial,sans-serif;max-width:760px;margin:0 auto;padding:20px;color:#222;background:#fafafa'>

      <div style='background:linear-gradient(135deg,#7b3f00,#c0620a);color:#fff;padding:22px 28px;border-radius:10px 10px 0 0'>
        <div style='font-size:11px;letter-spacing:2px;text-transform:uppercase;opacity:0.75;margin-bottom:6px'>Earnings Calendar Spread Scanner</div>
        <h1 style='margin:0;font-size:22px;font-weight:700'>📅 Russell 1000 财报期权扫描报告</h1>
        <p style='margin:8px 0 0;opacity:0.8;font-size:13px'>{date_str} {time_str} 北京时间 · 财报窗口：1-3天内 · 共 {total} 只有效数据</p>
      </div>

      <div style='background:#fff3e0;padding:12px 28px;border-left:5px solid #c0620a;font-size:13px;color:#7b3f00'>
        🔔 <b>策略提示：</b>以下标的均在 <b>1-3天内有财报</b>，同时满足期权扫描条件，适合评估日历价差机会。
        <span style='margin-left:16px'>
          <b style='color:#1a6600'>BMO</b> = 盘前公布 &nbsp;|&nbsp;
          <b style='color:#990000'>AMC</b> = 盘后公布 &nbsp;|&nbsp;
          <b style='color:#888'>Unknown</b> = 时间未知
        </span>
      </div>

      <div style='background:#fff8f0;padding:14px 28px;border-left:5px solid #e0a060;font-size:13px'>
        <b>条件通过统计</b>　　
        成交量 ≥150万: <b>{v_pass}</b> 只　
        IV30/RV30 ≥1.25: <b>{i_pass}</b> 只　
        TS斜率 ≤-0.00406: <b>{t_pass}</b> 只
      </div>

      <div style='background:#fff;border:1px solid #e8d5c0;border-radius:6px;padding:20px 24px;margin-top:16px'>
        <h2 style='color:#7b3f00;border-bottom:2px solid #c0620a;padding-bottom:8px;margin-top:0;font-size:16px'>
          ✅ 满足全部三项条件 — {len(passed)} 只
        </h2>
        {result_table(passed) if passed else "<p style='color:#aaa;font-style:italic'>今日无满足全部条件且有近期财报的股票</p>"}
      </div>

      <div style='background:#fff;border:1px solid #e8d5c0;border-radius:6px;padding:20px 24px;margin-top:12px'>
        <h2 style='color:#b8860b;border-bottom:2px solid #e0a060;padding-bottom:8px;margin-top:0;font-size:16px'>
          🟡 满足两项条件
        </h2>
        {two_sections if two_sections else "<p style='color:#aaa;font-style:italic'>今日无满足两项条件的股票</p>"}
      </div>

      <div style='background:#fff3e0;border:1px solid #f5c992;padding:12px 16px;border-radius:4px;font-size:11px;color:#888;margin-top:16px'>
        ⚠️ 免责声明：本报告仅供学习研究目的，不构成任何投资建议。请在做出任何投资决策前咨询专业金融顾问。
      </div>
    </body></html>"""

    return subject_prefix, html


def send_email(passed, results_all, scan_time):
    subject_prefix, html_body = build_email_html(passed, results_all, scan_time)
    date_str = scan_time.strftime('%Y-%m-%d')
    if passed:
        subject = f"⚠️ IMPORTANT | {subject_prefix} | Russell1000财报期权扫描 {date_str}"
    else:
        subject = f"📅 Russell1000财报期权扫描 {date_str} | 今日无全满足"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECEIVER
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        print(f"  📧  正在发送邮件到 {EMAIL_RECEIVER} ...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("  ✅  邮件发送成功！")
    except Exception as e:
        print(f"  ❌  邮件发送失败：{e}")


if __name__ == "__main__":
    start = time.time()
    scan_time = datetime.now()
    passed, results_all, errors = scan_all()
    print_results(passed, results_all)
    print(f"  ⏱  总耗时：{time.time()-start:.1f} 秒\n")
    send_email(passed, results_all, scan_time)