"""
Financial Report Generation System
===================================
Uses Generative AI (Claude API via Anthropic) to analyze financial data
and produce comprehensive, insight-rich reports.

Author: Project 4 – Financial AI Report System
Version: 1.0
"""

import json
import os
import sys
import urllib.request
import urllib.error
import datetime
import random

# ─────────────────────────────────────────────────────────
# SECTION 1: FINANCIAL DATA (Simulated Company Dataset)
# ─────────────────────────────────────────────────────────

COMPANY_NAME = "TechNova Solutions Inc."
FISCAL_YEAR = 2024

# Quarterly Revenue & Expenses (in USD millions)
QUARTERLY_DATA = {
    "Q1": {"revenue": 142.5, "cogs": 68.4, "opex": 41.2, "rd_expense": 18.3},
    "Q2": {"revenue": 158.3, "cogs": 74.1, "opex": 43.8, "rd_expense": 19.7},
    "Q3": {"revenue": 171.6, "cogs": 79.8, "opex": 46.1, "rd_expense": 21.4},
    "Q4": {"revenue": 195.2, "cogs": 88.3, "opex": 51.4, "rd_expense": 24.1},
}

# Balance Sheet Data (Year-End, USD millions)
BALANCE_SHEET = {
    "current_assets": {
        "cash_and_equivalents": 312.4,
        "accounts_receivable": 98.7,
        "inventory": 45.2,
        "prepaid_expenses": 12.1,
    },
    "non_current_assets": {
        "property_plant_equipment": 487.3,
        "intangible_assets": 203.6,
        "long_term_investments": 156.8,
    },
    "current_liabilities": {
        "accounts_payable": 87.4,
        "short_term_debt": 55.0,
        "accrued_liabilities": 43.2,
    },
    "non_current_liabilities": {
        "long_term_debt": 280.0,
        "deferred_tax": 38.9,
    },
    "equity": {
        "common_stock": 50.0,
        "retained_earnings": 776.6,
    },
}

# Prior Year Comparison Data
PRIOR_YEAR = {
    "total_revenue": 584.2,
    "gross_profit": 284.9,
    "operating_income": 128.4,
    "net_income": 98.7,
    "total_assets": 1312.6,
    "total_equity": 712.4,
}

# Cash Flow Data (USD millions)
CASH_FLOW = {
    "operating_activities": 218.4,
    "investing_activities": -145.2,
    "financing_activities": -62.8,
    "capex": -88.6,
    "dividends_paid": -28.4,
    "share_buybacks": -34.4,
}

# Market Data
MARKET_DATA = {
    "share_price": 87.42,
    "shares_outstanding": 142.6,  # millions
    "dividend_per_share": 0.72,
    "eps_prior_year": 2.84,
    "industry_pe_average": 24.8,
    "beta": 1.18,
}

# ─────────────────────────────────────────────────────────
# SECTION 2: FINANCIAL CALCULATIONS
# ─────────────────────────────────────────────────────────

def compute_financials(quarterly_data, balance_sheet, cash_flow, market_data):
    """Compute all key financial metrics from raw data."""
    
    # Income Statement
    total_revenue = sum(q["revenue"] for q in quarterly_data.values())
    total_cogs = sum(q["cogs"] for q in quarterly_data.values())
    total_opex = sum(q["opex"] for q in quarterly_data.values())
    total_rd = sum(q["rd_expense"] for q in quarterly_data.values())
    
    gross_profit = total_revenue - total_cogs
    ebitda = gross_profit - total_opex
    ebit = ebitda - (total_rd * 0.3)  # Amortization proxy
    interest_expense = 280.0 * 0.045  # Long-term debt * rate
    ebt = ebit - interest_expense
    net_income = ebt * 0.79  # 21% effective tax rate
    
    # Gross margin
    gross_margin = (gross_profit / total_revenue) * 100
    operating_margin = (ebit / total_revenue) * 100
    net_margin = (net_income / total_revenue) * 100
    ebitda_margin = (ebitda / total_revenue) * 100
    
    # Balance Sheet Aggregates
    total_current_assets = sum(balance_sheet["current_assets"].values())
    total_non_current_assets = sum(balance_sheet["non_current_assets"].values())
    total_assets = total_current_assets + total_non_current_assets
    
    total_current_liabilities = sum(balance_sheet["current_liabilities"].values())
    total_non_current_liabilities = sum(balance_sheet["non_current_liabilities"].values())
    total_liabilities = total_current_liabilities + total_non_current_liabilities
    total_equity = sum(balance_sheet["equity"].values())
    
    # Liquidity Ratios
    current_ratio = total_current_assets / total_current_liabilities
    quick_ratio = (total_current_assets - balance_sheet["current_assets"]["inventory"]) / total_current_liabilities
    cash_ratio = balance_sheet["current_assets"]["cash_and_equivalents"] / total_current_liabilities
    
    # Leverage Ratios
    debt_to_equity = (balance_sheet["non_current_liabilities"]["long_term_debt"] + 
                      balance_sheet["current_liabilities"]["short_term_debt"]) / total_equity
    debt_to_assets = total_liabilities / total_assets
    interest_coverage = ebit / interest_expense
    net_debt = (balance_sheet["non_current_liabilities"]["long_term_debt"] + 
                balance_sheet["current_liabilities"]["short_term_debt"] - 
                balance_sheet["current_assets"]["cash_and_equivalents"])
    ev_to_ebitda = ((market_data["share_price"] * market_data["shares_outstanding"]) + net_debt) / ebitda
    
    # Profitability Ratios
    roe = (net_income / total_equity) * 100
    roa = (net_income / total_assets) * 100
    roce = (ebit / (total_assets - total_current_liabilities)) * 100
    
    # Per Share Metrics
    eps = net_income / market_data["shares_outstanding"]
    pe_ratio = market_data["share_price"] / eps
    dividend_yield = (market_data["dividend_per_share"] / market_data["share_price"]) * 100
    market_cap = market_data["share_price"] * market_data["shares_outstanding"]
    price_to_book = market_cap / total_equity
    
    # Cash Flow Metrics
    free_cash_flow = cash_flow["operating_activities"] + cash_flow["capex"]
    fcf_yield = (free_cash_flow / market_cap) * 100
    fcf_margin = (free_cash_flow / total_revenue) * 100
    
    # YoY Growth
    revenue_growth = ((total_revenue - PRIOR_YEAR["total_revenue"]) / PRIOR_YEAR["total_revenue"]) * 100
    gp_growth = ((gross_profit - PRIOR_YEAR["gross_profit"]) / PRIOR_YEAR["gross_profit"]) * 100
    ni_growth = ((net_income - PRIOR_YEAR["net_income"]) / PRIOR_YEAR["net_income"]) * 100
    
    # Quarterly trends
    q_revenues = [quarterly_data[q]["revenue"] for q in ["Q1", "Q2", "Q3", "Q4"]]
    q_growth_rates = [
        ((q_revenues[i] - q_revenues[i-1]) / q_revenues[i-1]) * 100
        for i in range(1, len(q_revenues))
    ]
    
    return {
        "income_statement": {
            "total_revenue": round(total_revenue, 2),
            "cogs": round(total_cogs, 2),
            "gross_profit": round(gross_profit, 2),
            "total_opex": round(total_opex, 2),
            "rd_expense": round(total_rd, 2),
            "ebitda": round(ebitda, 2),
            "ebit": round(ebit, 2),
            "interest_expense": round(interest_expense, 2),
            "ebt": round(ebt, 2),
            "net_income": round(net_income, 2),
        },
        "margins": {
            "gross_margin": round(gross_margin, 2),
            "ebitda_margin": round(ebitda_margin, 2),
            "operating_margin": round(operating_margin, 2),
            "net_margin": round(net_margin, 2),
        },
        "balance_sheet_summary": {
            "total_current_assets": round(total_current_assets, 2),
            "total_non_current_assets": round(total_non_current_assets, 2),
            "total_assets": round(total_assets, 2),
            "total_current_liabilities": round(total_current_liabilities, 2),
            "total_non_current_liabilities": round(total_non_current_liabilities, 2),
            "total_liabilities": round(total_liabilities, 2),
            "total_equity": round(total_equity, 2),
        },
        "liquidity": {
            "current_ratio": round(current_ratio, 2),
            "quick_ratio": round(quick_ratio, 2),
            "cash_ratio": round(cash_ratio, 2),
        },
        "leverage": {
            "debt_to_equity": round(debt_to_equity, 2),
            "debt_to_assets": round(debt_to_assets, 2),
            "interest_coverage": round(interest_coverage, 2),
            "net_debt": round(net_debt, 2),
            "ev_to_ebitda": round(ev_to_ebitda, 2),
        },
        "profitability": {
            "roe": round(roe, 2),
            "roa": round(roa, 2),
            "roce": round(roce, 2),
        },
        "per_share": {
            "eps": round(eps, 2),
            "pe_ratio": round(pe_ratio, 2),
            "dividend_yield": round(dividend_yield, 2),
            "market_cap": round(market_cap, 2),
            "price_to_book": round(price_to_book, 2),
        },
        "cash_flow_metrics": {
            "operating_cash_flow": cash_flow["operating_activities"],
            "free_cash_flow": round(free_cash_flow, 2),
            "fcf_yield": round(fcf_yield, 2),
            "fcf_margin": round(fcf_margin, 2),
            "capex": cash_flow["capex"],
        },
        "growth": {
            "revenue_growth_yoy": round(revenue_growth, 2),
            "gross_profit_growth_yoy": round(gp_growth, 2),
            "net_income_growth_yoy": round(ni_growth, 2),
            "q_sequential_revenue_growth": [round(r, 2) for r in q_growth_rates],
        }
    }

# ─────────────────────────────────────────────────────────
# SECTION 3: AI-POWERED REPORT GENERATION
# ─────────────────────────────────────────────────────────

def call_claude_api(prompt, system_prompt="You are a senior financial analyst producing professional reports."):
    """
    Call the Anthropic Claude API to generate AI insights.
    Falls back to a placeholder if API call fails.
    """
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": os.environ.get("ANTHROPIC_API_KEY", "")
    }
    
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1500,
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["content"][0]["text"]
    except Exception as e:
        # Graceful fallback with structured placeholder
        return f"[AI Analysis unavailable: {str(e)[:80]}. Financial data has been computed and is displayed below.]"


def generate_executive_summary(metrics, company, year):
    prompt = f"""You are writing an executive summary for the {year} Annual Financial Report of {company}.

Key Financial Results:
- Total Revenue: ${metrics['income_statement']['total_revenue']}M (YoY Growth: {metrics['growth']['revenue_growth_yoy']}%)
- Net Income: ${metrics['income_statement']['net_income']}M (YoY Growth: {metrics['growth']['net_income_growth_yoy']}%)
- EBITDA: ${metrics['income_statement']['ebitda']}M (Margin: {metrics['margins']['ebitda_margin']}%)
- Free Cash Flow: ${metrics['cash_flow_metrics']['free_cash_flow']}M
- EPS: ${metrics['per_share']['eps']} vs prior year ${MARKET_DATA['eps_prior_year']}
- Return on Equity: {metrics['profitability']['roe']}%
- Market Cap: ${metrics['per_share']['market_cap']}M

Write a compelling, professional 3-paragraph executive summary suitable for investor-facing documentation. 
Cover: (1) overall financial performance and highlights, (2) operational drivers and margin dynamics, 
(3) capital allocation and forward-looking commentary. Be specific with numbers. Tone: confident, factual."""
    
    return call_claude_api(prompt)


def generate_risk_analysis(metrics, company):
    prompt = f"""As a senior financial analyst, provide a concise risk analysis for {company} based on these metrics:

Financial Health Indicators:
- Current Ratio: {metrics['liquidity']['current_ratio']} (industry benchmark: 1.5-2.5)
- Debt-to-Equity: {metrics['liquidity']['current_ratio']} 
- Interest Coverage: {metrics['leverage']['interest_coverage']}x
- Net Debt: ${metrics['leverage']['net_debt']}M
- EV/EBITDA: {metrics['leverage']['ev_to_ebitda']}x (industry avg P/E: {MARKET_DATA['industry_pe_average']})
- Beta: {MARKET_DATA['beta']}
- Revenue concentration: Single segment (technology)

Identify and analyze 4-5 key financial risks with severity ratings (Low/Medium/High) and recommended mitigations. 
Format as a structured analysis. Be analytical and specific."""

    return call_claude_api(prompt)


def generate_segment_insights(quarterly_data, metrics):
    q_revs = [quarterly_data[q]['revenue'] for q in ['Q1','Q2','Q3','Q4']]
    q_margins = [
        round(((quarterly_data[q]['revenue'] - quarterly_data[q]['cogs']) / quarterly_data[q]['revenue']) * 100, 1)
        for q in ['Q1','Q2','Q3','Q4']
    ]
    
    prompt = f"""Analyze the following quarterly financial trend data for a technology company:

Quarterly Revenue ($M): Q1={q_revs[0]}, Q2={q_revs[1]}, Q3={q_revs[2]}, Q4={q_revs[3]}
Sequential Growth: Q2={metrics['growth']['q_sequential_revenue_growth'][0]}%, Q3={metrics['growth']['q_sequential_revenue_growth'][1]}%, Q4={metrics['growth']['q_sequential_revenue_growth'][2]}%
Quarterly Gross Margins: Q1={q_margins[0]}%, Q2={q_margins[1]}%, Q3={q_margins[2]}%, Q4={q_margins[3]}%
R&D as % of Revenue: {round(metrics['income_statement']['rd_expense']/metrics['income_statement']['total_revenue']*100, 1)}%

Provide a 2-paragraph analysis of: (1) revenue trajectory and seasonal patterns, 
(2) margin evolution and operational leverage. Conclude with one forward-looking observation."""

    return call_claude_api(prompt)


def generate_valuation_commentary(metrics):
    prompt = f"""Provide a brief valuation commentary for a technology company with these metrics:

- P/E Ratio: {metrics['per_share']['pe_ratio']}x (industry average: {MARKET_DATA['industry_pe_average']}x)
- Price-to-Book: {metrics['per_share']['price_to_book']}x
- EV/EBITDA: {metrics['leverage']['ev_to_ebitda']}x
- FCF Yield: {metrics['cash_flow_metrics']['fcf_yield']}%
- Dividend Yield: {metrics['per_share']['dividend_yield']}%
- Revenue Growth: {metrics['growth']['revenue_growth_yoy']}% YoY
- ROE: {metrics['profitability']['roe']}%

Write 2 concise paragraphs covering: (1) current valuation relative to peers and growth profile, 
(2) key valuation drivers and what metrics investors should monitor. Be balanced and analytical."""

    return call_claude_api(prompt)


# ─────────────────────────────────────────────────────────
# SECTION 4: REPORT ASSEMBLY & OUTPUT
# ─────────────────────────────────────────────────────────

def format_currency(value, decimals=1):
    return f"${value:,.{decimals}f}M"

def format_pct(value, decimals=1):
    return f"{value:+.{decimals}f}%" if value != 0 else f"{value:.{decimals}f}%"

def draw_bar(value, max_val, width=20):
    filled = int((value / max_val) * width)
    return "█" * filled + "░" * (width - filled)

def print_section_header(title, char="═", width=72):
    print(f"\n{char * width}")
    pad = (width - len(title) - 2) // 2
    print(f"{char * pad} {title} {char * (width - pad - len(title) - 2)}")
    print(f"{char * width}")

def print_kpi_row(label, value, benchmark=None, status=None):
    status_icon = {"GOOD": "✅", "CAUTION": "⚠️", "ALERT": "🔴", None: "  "}.get(status, "  ")
    bench_str = f"  (Benchmark: {benchmark})" if benchmark else ""
    print(f"  {status_icon} {label:<35} {value}{bench_str}")


def generate_report(metrics, quarterly_data, balance_sheet, cash_flow, market_data):
    """Generate the complete financial report."""
    
    report_date = datetime.datetime.now().strftime("%B %d, %Y")
    report_lines = []  # Collect for file output too
    
    def out(line=""):
        print(line)
        report_lines.append(line)
    
    # ── TITLE ──
    out("=" * 72)
    out(f"{'ANNUAL FINANCIAL REPORT':^72}")
    out(f"{COMPANY_NAME:^72}")
    out(f"{'Fiscal Year ' + str(FISCAL_YEAR):^72}")
    out(f"{'Generated: ' + report_date:^72}")
    out(f"{'Powered by Generative AI (Claude)':^72}")
    out("=" * 72)
    
    # ── EXECUTIVE SUMMARY ──
    out("\n╔══════════════════════════════════════════════════════════════════════╗")
    out("║                       EXECUTIVE SUMMARY                             ║")
    out("╚══════════════════════════════════════════════════════════════════════╝")
    out("\n[Generating AI-powered executive summary...]\n")
    exec_summary = generate_executive_summary(metrics, COMPANY_NAME, FISCAL_YEAR)
    out(exec_summary)
    
    # ── KEY METRICS DASHBOARD ──
    print_section_header("KEY FINANCIAL METRICS DASHBOARD", "═")
    
    m = metrics
    
    out("\n  ┌─────────────────────────────────────────────────────────────────┐")
    out("  │                    INCOME STATEMENT ($M)                        │")
    out("  ├─────────────────────────────────────────────────────────────────┤")
    out(f"  │  Total Revenue:       {format_currency(m['income_statement']['total_revenue']):>10}   YoY Growth: {format_pct(m['growth']['revenue_growth_yoy']):>8}     │")
    out(f"  │  Cost of Goods Sold:  {format_currency(m['income_statement']['cogs']):>10}   Gross Margin: {m['margins']['gross_margin']:>6.1f}%       │")
    out(f"  │  Gross Profit:        {format_currency(m['income_statement']['gross_profit']):>10}                                │")
    out(f"  │  Operating Expenses:  {format_currency(m['income_statement']['total_opex']):>10}   EBITDA Margin: {m['margins']['ebitda_margin']:>5.1f}%       │")
    out(f"  │  R&D Expense:         {format_currency(m['income_statement']['rd_expense']):>10}   Op. Margin: {m['margins']['operating_margin']:>7.1f}%       │")
    out(f"  │  EBITDA:              {format_currency(m['income_statement']['ebitda']):>10}   Net Margin: {m['margins']['net_margin']:>7.1f}%       │")
    out(f"  │  Net Income:          {format_currency(m['income_statement']['net_income']):>10}   YoY Growth: {format_pct(m['growth']['net_income_growth_yoy']):>8}     │")
    out("  └─────────────────────────────────────────────────────────────────┘")
    
    # Quarterly Revenue Trend (ASCII bar chart)
    out("\n  QUARTERLY REVENUE TREND ($M)")
    out("  " + "─" * 55)
    q_max = max(quarterly_data[q]['revenue'] for q in ['Q1','Q2','Q3','Q4'])
    for q in ['Q1','Q2','Q3','Q4']:
        rev = quarterly_data[q]['revenue']
        bar = draw_bar(rev, q_max, 30)
        gm = ((rev - quarterly_data[q]['cogs']) / rev) * 100
        out(f"  {q}: {bar} ${rev:.1f}M  GM:{gm:.1f}%")
    out()
    
    # ── BALANCE SHEET SUMMARY ──
    print_section_header("BALANCE SHEET SUMMARY", "─")
    bs = m['balance_sheet_summary']
    out(f"\n  {'ASSETS':^34} │ {'LIABILITIES & EQUITY':^33}")
    out(f"  {'─'*34}─┼─{'─'*33}")
    out(f"  Current Assets:  {format_currency(bs['total_current_assets']):>12}    │ Current Liabilities:  {format_currency(bs['total_current_liabilities']):>10}")
    out(f"  Non-Current:     {format_currency(bs['total_non_current_assets']):>12}    │ Long-Term Liabilities: {format_currency(bs['total_non_current_liabilities']):>9}")
    out(f"  {'─'*34} │ {'─'*33}")
    out(f"  Total Assets:    {format_currency(bs['total_assets']):>12}    │ Total Equity:         {format_currency(bs['total_equity']):>10}")
    
    # ── FINANCIAL RATIOS ──
    print_section_header("FINANCIAL RATIOS & KPIs", "─")
    
    out("\n  LIQUIDITY RATIOS")
    cr = m['liquidity']['current_ratio']
    print_kpi_row("Current Ratio", f"{cr:.2f}x", "1.5–2.5x", "GOOD" if 1.5 <= cr <= 2.5 else "CAUTION")
    qr = m['liquidity']['quick_ratio']
    print_kpi_row("Quick Ratio", f"{qr:.2f}x", "> 1.0x", "GOOD" if qr >= 1.0 else "CAUTION")
    
    out("\n  LEVERAGE RATIOS")
    de = m['leverage']['debt_to_equity']
    print_kpi_row("Debt-to-Equity", f"{de:.2f}x", "< 2.0x", "GOOD" if de < 2.0 else "CAUTION")
    ic = m['leverage']['interest_coverage']
    print_kpi_row("Interest Coverage", f"{ic:.1f}x", "> 3.0x", "GOOD" if ic >= 3.0 else "ALERT")
    print_kpi_row("EV/EBITDA", f"{m['leverage']['ev_to_ebitda']:.1f}x", "Industry avg ~15x")
    
    out("\n  PROFITABILITY RATIOS")
    print_kpi_row("Return on Equity (ROE)", f"{m['profitability']['roe']:.1f}%", "> 15%", 
                  "GOOD" if m['profitability']['roe'] >= 15 else "CAUTION")
    print_kpi_row("Return on Assets (ROA)", f"{m['profitability']['roa']:.1f}%", "> 5%",
                  "GOOD" if m['profitability']['roa'] >= 5 else "CAUTION")
    print_kpi_row("Return on Capital Employed", f"{m['profitability']['roce']:.1f}%", "> 10%",
                  "GOOD" if m['profitability']['roce'] >= 10 else "CAUTION")
    
    out("\n  PER SHARE & MARKET METRICS")
    print_kpi_row("Earnings Per Share (EPS)", f"${m['per_share']['eps']:.2f}", 
                  f"Prior Year: ${MARKET_DATA['eps_prior_year']}")
    print_kpi_row("Price-to-Earnings (P/E)", f"{m['per_share']['pe_ratio']:.1f}x",
                  f"Industry: {MARKET_DATA['industry_pe_average']}x")
    print_kpi_row("Price-to-Book", f"{m['per_share']['price_to_book']:.2f}x")
    print_kpi_row("Dividend Yield", f"{m['per_share']['dividend_yield']:.2f}%")
    print_kpi_row("Market Capitalization", f"${m['per_share']['market_cap']:,.1f}M")
    
    out("\n  CASH FLOW METRICS")
    print_kpi_row("Operating Cash Flow", format_currency(m['cash_flow_metrics']['operating_cash_flow']))
    print_kpi_row("Free Cash Flow", format_currency(m['cash_flow_metrics']['free_cash_flow']))
    fcfm = m['cash_flow_metrics']['fcf_margin']
    print_kpi_row("FCF Margin", f"{fcfm:.1f}%", "> 10%", "GOOD" if fcfm >= 10 else "CAUTION")
    print_kpi_row("FCF Yield", f"{m['cash_flow_metrics']['fcf_yield']:.1f}%")
    print_kpi_row("Capital Expenditure", format_currency(abs(cash_flow['capex'])))
    
    # ── QUARTERLY ANALYSIS ──
    print_section_header("QUARTERLY PERFORMANCE ANALYSIS", "─")
    out("\n[Generating AI-powered quarterly analysis...]\n")
    quarterly_insights = generate_segment_insights(quarterly_data, metrics)
    out(quarterly_insights)
    
    out("\n  QUARTERLY INCOME STATEMENT ($M)")
    out(f"  {'Metric':<22} {'Q1':>8} {'Q2':>8} {'Q3':>8} {'Q4':>8} {'FY Total':>10}")
    out("  " + "─" * 68)
    for metric, label in [("revenue","Revenue"), ("cogs","COGS"), ("rd_expense","R&D Expense"), ("opex","Oper. Expenses")]:
        vals = [quarterly_data[q][metric] for q in ['Q1','Q2','Q3','Q4']]
        total = sum(vals)
        out(f"  {label:<22} {vals[0]:>8.1f} {vals[1]:>8.1f} {vals[2]:>8.1f} {vals[3]:>8.1f} {total:>10.1f}")
    
    gps = [(quarterly_data[q]['revenue'] - quarterly_data[q]['cogs']) for q in ['Q1','Q2','Q3','Q4']]
    out(f"  {'Gross Profit':<22} {gps[0]:>8.1f} {gps[1]:>8.1f} {gps[2]:>8.1f} {gps[3]:>8.1f} {sum(gps):>10.1f}")
    
    # ── RISK ANALYSIS ──
    print_section_header("RISK ANALYSIS", "─")
    out("\n[Generating AI-powered risk analysis...]\n")
    risk_analysis = generate_risk_analysis(metrics, COMPANY_NAME)
    out(risk_analysis)
    
    # ── VALUATION ──
    print_section_header("VALUATION COMMENTARY", "─")
    out("\n[Generating AI-powered valuation commentary...]\n")
    valuation = generate_valuation_commentary(metrics)
    out(valuation)
    
    # ── CASH FLOW STATEMENT ──
    print_section_header("CASH FLOW STATEMENT ($M)", "─")
    out(f"\n  {'Cash from Operating Activities:':45} {cash_flow['operating_activities']:>+8.1f}")
    out(f"  {'Cash from Investing Activities:':45} {cash_flow['investing_activities']:>+8.1f}")
    out(f"    {'  Capital Expenditures:':43} {cash_flow['capex']:>+8.1f}")
    out(f"  {'Cash from Financing Activities:':45} {cash_flow['financing_activities']:>+8.1f}")
    out(f"    {'  Dividends Paid:':43} {cash_flow['dividends_paid']:>+8.1f}")
    out(f"    {'  Share Buybacks:':43} {cash_flow['share_buybacks']:>+8.1f}")
    out("  " + "─" * 56)
    net_change = sum(cash_flow.values())
    out(f"  {'Net Change in Cash:':45} {net_change:>+8.1f}")
    
    # ── FOOTER ──
    out("\n" + "═" * 72)
    out(f"  Report generated: {report_date}")
    out(f"  Data as of: December 31, {FISCAL_YEAR}")
    out(f"  AI Model: Claude (Anthropic)")
    out(f"  DISCLAIMER: This report is generated using AI-assisted analysis.")
    out(f"  It is for informational purposes only and does not constitute")
    out(f"  financial advice. All figures are in USD millions unless stated.")
    out("═" * 72)
    
    return "\n".join(report_lines)


# ─────────────────────────────────────────────────────────
# SECTION 5: MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────

def main():
    print("\n🔄 Financial Report Generation System - Initializing...")
    print(f"   Company: {COMPANY_NAME}")
    print(f"   Fiscal Year: {FISCAL_YEAR}")
    print(f"   Computing financial metrics...")
    
    # Compute all metrics
    metrics = compute_financials(QUARTERLY_DATA, BALANCE_SHEET, CASH_FLOW, MARKET_DATA)
    
    print(f"   ✅ Financial calculations complete.")
    print(f"   🤖 Calling Generative AI for analysis and insights...")
    print(f"   (This may take 15-30 seconds)\n")
    
    # Generate the full report
    report_text = generate_report(metrics, QUARTERLY_DATA, BALANCE_SHEET, CASH_FLOW, MARKET_DATA)
    
    # Save report to file
    output_path = "/home/claude/financial_report_output.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print(f"\n\n✅ Report saved to: {output_path}")
    print(f"📊 Key Metrics Summary:")
    print(f"   Revenue: ${metrics['income_statement']['total_revenue']}M  |  Net Income: ${metrics['income_statement']['net_income']}M")
    print(f"   EPS: ${metrics['per_share']['eps']}  |  Market Cap: ${metrics['per_share']['market_cap']}M")
    
    return metrics


if __name__ == "__main__":
    main()
