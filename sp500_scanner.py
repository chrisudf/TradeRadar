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

# 强制 stdout/stderr 使用 UTF-8，避免 Windows cmd 编码报错
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ══════════════════════════════════════════════════════════════
#  📧  邮件配置  —  请修改以下三行
# ══════════════════════════════════════════════════════════════
EMAIL_SENDER   = "chengqiu03@gmail.com"    # 发件人（你自己的 Gmail）
EMAIL_PASSWORD = "itzz vmar gzih tlbr"         # Gmail 应用专用密码（16位）
EMAIL_RECEIVER = "chengqiu03@gmail.com"  # 收件人（可以和发件人相同）
# ══════════════════════════════════════════════════════════════

# ── S&P 500 成分股 ─────────────────────────────────────────────────────────────
SP500 = [
    "MMM", "AOS", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AES", "AFL", "A",
    "APD", "ABNB", "AKAM", "ALB", "ARE", "ALGN", "ALLE", "LNT", "ALL", "GOOGL",
    "GOOG", "MO", "AMZN", "AMCR", "AMP", "AME", "AMGN", "APH", "ADI", "ANSS",
    "AON", "APA", "AAPL", "AMAT", "APTV", "ACGL", "ADM", "ANET", "AJG", "AIZ",
    "T", "ATO", "ADSK", "ADP", "AZO", "AVB", "AVY", "AXON", "BKR", "BALL",
    "BAC", "BK", "BBWI", "BAX", "BDX", "WRB", "BBY", "BIO", "TECH", "BIIB",
    "BLK", "BX", "BA", "BCR", "BSX", "BMY", "AVGO", "BR", "BRO", "BF.B",
    "BLDR", "BG", "CDNS", "CZR", "CPT", "CPB", "COF", "CAH", "KMX", "CCL",
    "CARR", "CAT", "CBOE", "CBRE", "CDW", "CE", "COR", "CNC", "CNX", "CDAY",
    "CF", "CRL", "SCHW", "CHTR", "CVX", "CMG", "CB", "CHD", "CI", "CINF",
    "CTAS", "CSCO", "C", "CFG", "CLX", "CME", "CMS", "KO", "CTSH", "CL",
    "CMCSA", "CAG", "COP", "ED", "STZ", "CEG", "COO", "CPRT", "GLW", "CPAY",
    "CTVA", "CSGP", "COST", "CTRA", "CRWD", "CSX", "CMI", "CVS", "DHR", "DRI",
    "DVA", "DAY", "DECK", "DE", "DELL", "DAL", "DVN", "DXCM", "FANG", "DLR",
    "DFS", "DG", "DLTR", "D", "DPZ", "DOV", "DOW", "DHI", "DTE", "DUK",
    "DD", "EMN", "ETN", "EBAY", "ECL", "EIX", "EW", "EA", "ELV", "EMR",
    "ENPH", "ETR", "EOG", "EPAM", "EQT", "EFX", "EQIX", "EQR", "ESS", "EL",
    "ETSY", "EG", "EVRG", "ES", "EXC", "EXPE", "EXPD", "EXR", "XOM", "FFIV",
    "FDS", "FICO", "FAST", "FRT", "FDX", "FIS", "FITB", "FSLR", "FE", "FI",
    "FMC", "F", "FTNT", "FTV", "FOXA", "FOX", "BEN", "FCX", "GRMN", "IT",
    "GE", "GEHC", "GEV", "GEN", "GNRC", "GD", "GIS", "GM", "GPC", "GILD",
    "GS", "HAL", "HIG", "HAS", "HCA", "DOC", "HSIC", "HSY", "HES", "HPE",
    "HLT", "HOLX", "HD", "HON", "HRL", "HST", "HWM", "HPQ", "HUBB", "HUM",
    "HBAN", "HII", "IBM", "IEX", "IDXX", "ITW", "INCY", "IR", "PODD", "INTC",
    "ICE", "IFF", "IP", "IPG", "INTU", "ISRG", "IVZ", "INVH", "IQV", "IRM",
    "JBHT", "JBL", "JKHY", "J", "JNJ", "JCI", "JPM", "JNPR", "K", "KVUE",
    "KDP", "KEY", "KEYS", "KMB", "KIM", "KMI", "KLAC", "KHC", "KR", "LHX",
    "LH", "LRCX", "LW", "LVS", "LDOS", "LEN", "LIN", "LYV", "LKQ", "LMT",
    "L", "LOW", "LULU", "LYB", "MTB", "MRO", "MPC", "MKTX", "MAR", "MMC",
    "MLM", "MAS", "MA", "MTCH", "MKC", "MCD", "MCK", "MDT", "MRK", "META",
    "MET", "MTD", "MGM", "MCHP", "MU", "MSFT", "MAA", "MRNA", "MHK", "MOH",
    "TAP", "MDLZ", "MPWR", "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "NDAQ",
    "NTAP", "NWS", "NWSA", "NEM", "NFLX", "NWL", "NI", "NDSN", "NSC", "NTRS",
    "NOC", "NCLH", "NRG", "NUE", "NVDA", "NVR", "NXPI", "ORLY", "OXY", "ODFL",
    "OMC", "ON", "OKE", "ORCL", "OTIS", "PCAR", "PKG", "PLTR", "PANW", "PARA",
    "PH", "PAYX", "PAYC", "PYPL", "PNR", "PEP", "PFE", "PCG", "PM", "PSX",
    "PNW", "PNC", "POOL", "PPG", "PPL", "PFG", "PG", "PGR", "PRU", "PLD",
    "PRG", "PTC", "PSA", "PHM", "QRVO", "PWR", "QCOM", "DGX", "RL", "RJF",
    "RTX", "O", "REG", "REGN", "RF", "RSG", "RMD", "RVTY", "ROK", "ROL",
    "ROP", "ROST", "RCL", "SPGI", "CRM", "SBAC", "SLB", "STX", "SRE", "NOW",
    "SHW", "SPG", "SWKS", "SJM", "SW", "SNA", "SOLV", "SO", "LUV", "SWK",
    "SBUX", "STT", "STLD", "STE", "SYK", "SMCI", "SYF", "SNPS", "SYY", "TMUS",
    "TROW", "TTWO", "TPR", "TRGP", "TGT", "TEL", "TDY", "TFX", "TER", "TSLA",
    "TXN", "TXT", "TMO", "TJX", "TSCO", "TT", "TDG", "TRV", "TRMB", "TFC",
    "TYL", "TSN", "USB", "UBER", "UDR", "ULTA", "UNP", "UAL", "UPS", "URI",
    "UNH", "UHS", "VLO", "VTR", "VLTO", "VRSN", "VRSK", "VZ", "VRTX", "VIAV",
    "VST", "V", "VMC", "WRK", "WAB", "WBA", "WMT", "DIS", "WBD", "WM",
    "WAT", "WEC", "WFC", "WELL", "WST", "WDC", "WY", "WMB", "WTW", "GWW",
    "WYNN", "XEL", "XYL", "YUM", "ZBRA", "ZBH", "ZTS",
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


def compute_recommendation(ticker_symbol):
    ticker_symbol = ticker_symbol.strip().upper()
    stock = yf.Ticker(ticker_symbol)

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
        'ticker':        ticker_symbol,
        'avg_volume':    avg_volume >= 1_500_000,
        'iv30_rv30':     iv30_rv30 >= 1.25,
        'ts_slope_0_45': ts_slope_0_45 <= -0.00406,
        'iv30_rv30_val': round(iv30_rv30, 3),
        'ts_slope_val':  round(ts_slope_0_45, 6),
        'expected_move': expected_move,
        'price':         round(underlying_price, 2),
    }


# ── 批量扫描 ──────────────────────────────────────────────────────────────────

def scan_all(tickers=SP500, max_workers=4):
    results_all = []
    errors      = []
    passed      = []
    total       = len(tickers)

    print(f"\n{'='*60}")
    print(f"  S&P500 期权扫描器  |  共 {total} 只股票")
    print(f"  扫描条件：avg_volume ✓  iv30_rv30 ✓  ts_slope_0_45 ✓")
    print(f"{'='*60}\n")

    def _worker(sym, retries=2):
        for attempt in range(retries + 1):
            try:
                return sym, compute_recommendation(sym), None
            except Exception as e:
                if attempt < retries:
                    time.sleep(2 * (attempt + 1))  # 第1次等2秒，第2次等4秒
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
    print(f"{'━'*60}")
    print(f"  ✅  满足全部三项条件：{len(passed)} 只")
    print(f"{'━'*60}")
    if passed:
        header = f"  {'代码':<8} {'股价':>8} {'IV30/RV30':>10} {'TS斜率':>12} {'预期波幅':>10}"
        print(header)
        print(f"  {'-'*56}")
        for r in sorted(passed, key=lambda x: x['iv30_rv30_val'], reverse=True):
            print(f"  {r['ticker']:<8} ${r['price']:>7.2f} {r['iv30_rv30_val']:>10.3f} {r['ts_slope_val']:>12.6f} {r['expected_move']:>10}")
    else:
        print("  （暂无满足全部条件的股票）")

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
            <tr style='background:#1a3a2e;color:#fff'>
              <th style='padding:8px 12px;text-align:left'>代码</th>
              <th style='padding:8px 12px;text-align:right'>股价</th>
              <th style='padding:8px 12px;text-align:right'>IV30/RV30</th>
              <th style='padding:8px 12px;text-align:right'>TS斜率</th>
              <th style='padding:8px 12px;text-align:right'>预期波幅</th>
            </tr>
          </thead><tbody>"""
        for i, r in enumerate(sorted(rows, key=lambda x: x['iv30_rv30_val'], reverse=True)):
            html += f"""
            <tr style='background:{row_color(i)}'>
              <td style='padding:7px 12px;font-weight:bold'>{r['ticker']}</td>
              <td style='padding:7px 12px;text-align:right'>${r['price']:.2f}</td>
              <td style='padding:7px 12px;text-align:right'>{r['iv30_rv30_val']:.3f}</td>
              <td style='padding:7px 12px;text-align:right'>{r['ts_slope_val']:.6f}</td>
              <td style='padding:7px 12px;text-align:right'>{r['expected_move']}</td>
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
    <!DOCTYPE html><html><body style='font-family:Arial,sans-serif;max-width:720px;margin:0 auto;padding:20px;color:#222'>
      <div style='background:#1a3a2e;color:#fff;padding:20px 24px;border-radius:8px 8px 0 0'>
        <h1 style='margin:0;font-size:20px'>📊 S&P500 期权扫描报告</h1>
        <p style='margin:6px 0 0;opacity:0.7;font-size:13px'>{date_str} {time_str} 北京时间 · 共扫描 {total} 只有效数据</p>
      </div>

      <div style='background:#f0fff4;padding:16px 24px;border-left:4px solid #1a3a2e'>
        <b>条件通过统计</b>　　
        成交量 ≥150万: <b>{v_pass}</b> 只　
        IV30/RV30 ≥1.25: <b>{i_pass}</b> 只　
        TS斜率 ≤-0.00406: <b>{t_pass}</b> 只
      </div>

      <div style='padding:20px 0'>
        <h2 style='color:#006600;border-bottom:2px solid #006600;padding-bottom:6px'>
          ✅ 满足全部三项条件 — {len(passed)} 只
        </h2>
        {result_table(passed) if passed else "<p style='color:#888;font-style:italic'>今日无满足全部条件的股票</p>"}
      </div>

      <div style='padding:10px 0'>
        <h2 style='color:#b8860b;border-bottom:2px solid #b8860b;padding-bottom:6px'>
          🟡 满足两项条件
        </h2>
        {two_sections if two_sections else "<p style='color:#888;font-style:italic'>今日无满足两项条件的股票</p>"}
      </div>

      <div style='background:#fff8e1;border:1px solid #ffe082;padding:12px 16px;border-radius:4px;font-size:12px;color:#666;margin-top:20px'>
        ⚠️ 免责声明：本报告仅供学习研究目的，不构成任何投资建议。请在做出任何投资决策前咨询专业金融顾问。
      </div>
    </body></html>"""

    return subject_prefix, html


def send_email(passed, results_all, scan_time):
    subject_prefix, html_body = build_email_html(passed, results_all, scan_time)
    date_str = scan_time.strftime('%Y-%m-%d')
    if passed:
        subject = f"⚠️ IMPORTANT | {subject_prefix} | S&P500期权扫描 {date_str}"
    else:
        subject = f"S&P500期权扫描 {date_str} | 今日无全满足"

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