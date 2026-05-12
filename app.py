"""
StockAnalyze - Personalized Investment Advisor
Analyzes macroeconomics, asset trends, and provides learning resources.
"""
import json
import datetime
import yfinance as yf
import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration: key assets to track
# ---------------------------------------------------------------------------
MARKET_ASSETS = {
    "美股指数 (US Indices)": [
        {"ticker": "^GSPC",  "name": "标普500 S&P 500"},
        {"ticker": "^IXIC",  "name": "纳斯达克 NASDAQ"},
        {"ticker": "^DJI",   "name": "道琼斯 Dow Jones"},
        {"ticker": "^RUT",   "name": "罗素2000 Russell 2000"},
    ],
    "中港股市 (China/HK)": [
        {"ticker": "000001.SS", "name": "上证指数 Shanghai"},
        {"ticker": "399001.SZ", "name": "深证成指 Shenzhen"},
        {"ticker": "^HSI",      "name": "恒生指数 Hang Seng"},
        {"ticker": "MCHI",      "name": "中国ETF MCHI"},
    ],
    "大宗商品 (Commodities)": [
        {"ticker": "GC=F",  "name": "黄金 Gold"},
        {"ticker": "CL=F",  "name": "原油 Crude Oil"},
        {"ticker": "SI=F",  "name": "白银 Silver"},
        {"ticker": "NG=F",  "name": "天然气 Nat Gas"},
    ],
    "加密货币 (Crypto)": [
        {"ticker": "BTC-USD", "name": "比特币 Bitcoin"},
        {"ticker": "ETH-USD", "name": "以太坊 Ethereum"},
        {"ticker": "SOL-USD", "name": "Solana"},
        {"ticker": "BNB-USD", "name": "币安 BNB"},
    ],
    "债券 (Bonds)": [
        {"ticker": "^TNX",  "name": "10年期美债 10Y UST"},
        {"ticker": "^TYX",  "name": "30年期美债 30Y UST"},
        {"ticker": "^FVX",  "name": "5年期美债 5Y UST"},
        {"ticker": "^IRX",  "name": "3月美债 3M UST"},
    ],
}

POPULAR_STOCKS = [
    {"ticker": "AAPL",  "name": "苹果 Apple"},
    {"ticker": "MSFT",  "name": "微软 Microsoft"},
    {"ticker": "NVDA",  "name": "英伟达 NVIDIA"},
    {"ticker": "TSLA",  "name": "特斯拉 Tesla"},
    {"ticker": "AMZN",  "name": "亚马逊 Amazon"},
    {"ticker": "GOOGL", "name": "谷歌 Alphabet"},
    {"ticker": "META",  "name": "Meta"},
    {"ticker": "BABA",  "name": "阿里巴巴 Alibaba"},
    {"ticker": "JD",    "name": "京东 JD.com"},
    {"ticker": "PDD",   "name": "拼多多 PDD"},
    {"ticker": "BIDU",  "name": "百度 Baidu"},
    {"ticker": "NIO",   "name": "蔚来 NIO"},
]

MACRO_INDICATORS = [
    {"ticker": "^TNX",  "name": "10年期美债收益率", "desc": "反映长期通胀预期和经济前景"},
    {"ticker": "DX-Y.NYB", "name": "美元指数 DXY",  "desc": "衡量美元相对其他主要货币的强弱"},
    {"ticker": "GC=F",     "name": "黄金期货",       "desc": "避险资产，反映全球不确定性"},
    {"ticker": "CL=F",     "name": "原油期货",       "desc": "全球经济活动的晴雨表"},
    {"ticker": "^VIX",     "name": "恐慌指数 VIX",  "desc": "市场波动率，高=恐慌 低=贪婪"},
    {"ticker": "^GSPC",    "name": "标普500",        "desc": "美国股市广泛代表性指标"},
]

LEARNING_RESOURCES = [
    # Videos
    {
        "type": "video",
        "title": "宏观经济学入门：如何影响股市",
        "source": "YouTube",
        "url": "https://www.youtube.com/results?search_query=macroeconomics+stock+market+explained",
        "thumbnail": "https://img.youtube.com/vi/d0nERTFo-Sk/hqdefault.jpg",
        "description": "了解GDP、通胀、利率如何影响资产价格，建立宏观投资框架。",
        "tags": ["宏观经济", "入门", "股市"],
    },
    {
        "type": "video",
        "title": "K线图技术分析完整教程",
        "source": "YouTube",
        "url": "https://www.youtube.com/results?search_query=candlestick+chart+technical+analysis+tutorial",
        "thumbnail": "https://img.youtube.com/vi/dTX1lcfCvEo/hqdefault.jpg",
        "description": "从零学习K线图形态、支撑阻力、均线交叉等技术分析方法。",
        "tags": ["技术分析", "K线", "图表"],
    },
    {
        "type": "video",
        "title": "价值投资：巴菲特的选股方法",
        "source": "YouTube",
        "url": "https://www.youtube.com/results?search_query=warren+buffett+value+investing+strategy",
        "thumbnail": "https://img.youtube.com/vi/41bCB2gDdJ8/hqdefault.jpg",
        "description": "学习如何分析公司基本面，发现被低估的优质股票。",
        "tags": ["价值投资", "基本面", "巴菲特"],
    },
    {
        "type": "video",
        "title": "中美贸易与金融市场解析",
        "source": "YouTube",
        "url": "https://www.youtube.com/results?search_query=china+us+trade+financial+markets+analysis",
        "thumbnail": "https://img.youtube.com/vi/3t7NkMuTr6c/hqdefault.jpg",
        "description": "深度解析中美关系对全球金融市场的影响与投资机会。",
        "tags": ["中美关系", "地缘政治", "全球市场"],
    },
    {
        "type": "video",
        "title": "债券市场与利率周期",
        "source": "YouTube",
        "url": "https://www.youtube.com/results?search_query=bond+market+interest+rate+cycle+investing",
        "thumbnail": "https://img.youtube.com/vi/5jJmR7q5gQ0/hqdefault.jpg",
        "description": "理解债券收益率曲线、利率周期与资产配置之间的关系。",
        "tags": ["债券", "利率", "资产配置"],
    },
    {
        "type": "video",
        "title": "加密货币与区块链投资逻辑",
        "source": "YouTube",
        "url": "https://www.youtube.com/results?search_query=cryptocurrency+bitcoin+investment+analysis+2024",
        "thumbnail": "https://img.youtube.com/vi/rYQgy8QDEBI/hqdefault.jpg",
        "description": "分析比特币、以太坊等主流加密资产的投资逻辑和风险。",
        "tags": ["加密货币", "比特币", "区块链"],
    },
    # Articles
    {
        "type": "article",
        "title": "全球宏观经济分析框架",
        "source": "Investopedia",
        "url": "https://www.investopedia.com/terms/m/macroeconomics.asp",
        "description": "系统讲解宏观经济分析的核心框架，包括GDP、CPI、PMI等关键指标的解读方法。",
        "tags": ["宏观分析", "经济指标", "框架"],
        "read_time": "15 分钟",
    },
    {
        "type": "article",
        "title": "如何读懂财报：PE、PB、ROE深度解析",
        "source": "Investopedia",
        "url": "https://www.investopedia.com/terms/p/price-earningsratio.asp",
        "description": "学习核心估值指标和财务分析方法，快速识别优质公司。",
        "tags": ["财务分析", "估值", "基本面"],
        "read_time": "12 分钟",
    },
    {
        "type": "article",
        "title": "资产配置：现代投资组合理论",
        "source": "Investopedia",
        "url": "https://www.investopedia.com/terms/m/modernportfoliotheory.asp",
        "description": "了解如何通过分散投资降低风险，构建适合自己的投资组合。",
        "tags": ["资产配置", "风险管理", "组合理论"],
        "read_time": "10 分钟",
    },
    {
        "type": "article",
        "title": "技术分析 vs 基本面分析",
        "source": "Investopedia",
        "url": "https://www.investopedia.com/ask/answers/difference-between-fundamental-and-technical-analysis/",
        "description": "深入比较两种主要分析方法的优缺点，找到适合自己的投资风格。",
        "tags": ["技术分析", "基本面", "投资策略"],
        "read_time": "8 分钟",
    },
    {
        "type": "article",
        "title": "A股市场投资特点与策略",
        "source": "知乎专栏",
        "url": "https://zhuanlan.zhihu.com/p/",
        "description": "分析A股市场与美股的差异，掌握适合中国市场的投资策略。",
        "tags": ["A股", "中国市场", "策略"],
        "read_time": "12 分钟",
    },
    {
        "type": "article",
        "title": "黄金与避险资产投资逻辑",
        "source": "World Gold Council",
        "url": "https://www.gold.org/goldhub/research",
        "description": "了解黄金在投资组合中的作用，以及在不同市场环境下的表现规律。",
        "tags": ["黄金", "避险资产", "大宗商品"],
        "read_time": "10 分钟",
    },
]

ADVISOR_ANALYSIS = {
    "conservative": {
        "name": "保守型 Conservative",
        "icon": "🛡️",
        "description": "稳健保值，追求稳定收益，承受风险能力低",
        "allocation": {
            "债券/国债": 50,
            "蓝筹股/ETF": 25,
            "黄金": 15,
            "现金": 10,
        },
        "recommendations": [
            "重仓美债ETF (TLT, SHY)，获取稳定利息收益",
            "配置标普500 ETF (SPY, VOO)，长期持有分红蓝筹",
            "保持10-15%黄金仓位对冲不确定性",
            "避免高波动的加密货币和成长型科技股",
        ],
        "risk_level": "低",
        "expected_return": "5-8% / 年",
    },
    "moderate": {
        "name": "稳健型 Moderate",
        "icon": "⚖️",
        "description": "平衡增长与保值，可承受中等风险",
        "allocation": {
            "股票/ETF": 50,
            "债券": 25,
            "大宗商品": 15,
            "加密货币": 10,
        },
        "recommendations": [
            "核心仓位：美股ETF (QQQ, SPY) + 中国ETF (MCHI)",
            "配置5-10%加密货币获取高成长暴露",
            "定期定额(DCA)策略平滑市场波动",
            "关注美联储利率决议和CPI数据对市场的影响",
        ],
        "risk_level": "中",
        "expected_return": "10-15% / 年",
    },
    "aggressive": {
        "name": "进取型 Aggressive",
        "icon": "🚀",
        "description": "追求高回报，可承受较大亏损波动",
        "allocation": {
            "成长股/科技股": 50,
            "加密货币": 25,
            "杠杆ETF": 15,
            "期权策略": 10,
        },
        "recommendations": [
            "重仓AI科技股：NVDA, MSFT, GOOGL",
            "配置比特币和以太坊，长期看好区块链趋势",
            "关注中国互联网反弹机会：BABA, JD, PDD",
            "学习期权策略（covered call）增强收益",
        ],
        "risk_level": "高",
        "expected_return": "20%+ / 年",
    },
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Main dashboard."""
    return render_template("index.html",
                           market_assets=MARKET_ASSETS,
                           popular_stocks=POPULAR_STOCKS)


@app.route("/macro")
def macro():
    """Macroeconomic analysis page."""
    return render_template("macro.html", indicators=MACRO_INDICATORS)


@app.route("/charts")
def charts():
    """Asset trend charts page."""
    all_assets = []
    for category, assets in MARKET_ASSETS.items():
        for a in assets:
            all_assets.append({**a, "category": category})
    all_assets.extend(POPULAR_STOCKS)
    return render_template("charts.html", assets=all_assets)


@app.route("/learn")
def learn():
    """Learning center page."""
    videos = [r for r in LEARNING_RESOURCES if r["type"] == "video"]
    articles = [r for r in LEARNING_RESOURCES if r["type"] == "article"]
    return render_template("learn.html", videos=videos, articles=articles)


@app.route("/advisor")
def advisor():
    """Investment advisor page."""
    return render_template("advisor.html", profiles=ADVISOR_ANALYSIS)


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.route("/api/market-overview")
def api_market_overview():
    """Return real-time market snapshot for dashboard cards."""
    results = {}
    for category, assets in MARKET_ASSETS.items():
        results[category] = []
        for asset in assets:
            ticker = asset["ticker"]
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="5d", interval="1d")
                if len(hist) >= 2:
                    prev_val = hist["Close"].iloc[-2]
                    curr_val = hist["Close"].iloc[-1]
                    if pd.isna(prev_val) or pd.isna(curr_val):
                        raise ValueError("NaN price values")
                    prev = float(prev_val)
                    curr = float(curr_val)
                    chg = ((curr - prev) / prev) * 100
                    results[category].append({
                        "ticker": ticker,
                        "name": asset["name"],
                        "price": round(curr, 4),
                        "change": round(chg, 2),
                    })
            except Exception:
                results[category].append({
                    "ticker": ticker,
                    "name": asset["name"],
                    "price": "N/A",
                    "change": 0,
                })
    return jsonify(results)


@app.route("/api/chart/<path:ticker>")
def api_chart(ticker):
    """Return Plotly JSON for an interactive candlestick chart."""
    period = request.args.get("period", "1y")
    interval = request.args.get("interval", "1d")
    chart_type = request.args.get("type", "candlestick")

    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period, interval=interval)

        if hist.empty:
            return jsonify({"error": "No data available"}), 404

        # Add technical indicators
        close = hist["Close"]
        hist["MA20"] = close.rolling(20).mean()
        hist["MA50"] = close.rolling(50).mean()
        hist["MA200"] = close.rolling(200).mean()

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.75, 0.25],
        )

        if chart_type == "line":
            fig.add_trace(go.Scatter(
                x=hist.index, y=close, name="Price",
                line={"color": "#00d4aa", "width": 2},
            ), row=1, col=1)
        else:
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist["Open"], high=hist["High"],
                low=hist["Low"], close=close,
                name="OHLC",
                increasing_line_color="#26a69a",
                decreasing_line_color="#ef5350",
            ), row=1, col=1)

        # Moving averages
        for ma, color in [("MA20", "#f39c12"), ("MA50", "#3498db"), ("MA200", "#e74c3c")]:
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist[ma], name=ma,
                line={"color": color, "width": 1, "dash": "dot"},
                opacity=0.8,
            ), row=1, col=1)

        # Volume
        colors = ["#26a69a" if c >= o else "#ef5350"
                  for c, o in zip(hist["Close"], hist["Open"])]
        fig.add_trace(go.Bar(
            x=hist.index, y=hist["Volume"], name="成交量",
            marker_color=colors, opacity=0.7,
        ), row=2, col=1)

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            paper_bgcolor="#1a1a2e",
            plot_bgcolor="#16213e",
            font={"color": "#e0e0e0"},
            legend={"orientation": "h", "y": 1.05},
            margin={"t": 20, "b": 20, "l": 60, "r": 20},
            height=520,
        )
        fig.update_yaxes(gridcolor="#2a2a4a", row=1, col=1)
        fig.update_yaxes(gridcolor="#2a2a4a", row=2, col=1)
        fig.update_xaxes(gridcolor="#2a2a4a")

        return jsonify(json.loads(plotly.io.to_json(fig)))

    except Exception:
        return jsonify({"error": "Failed to retrieve chart data. Please check the ticker symbol or try again later."}), 500


@app.route("/api/macro-chart/<path:ticker>")
def api_macro_chart(ticker):
    """Return a simple line chart for a macro indicator."""
    period = request.args.get("period", "2y")
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period, interval="1wk")
        if hist.empty:
            return jsonify({"error": "No data"}), 404

        close = hist["Close"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index, y=close, mode="lines",
            line={"color": "#00d4aa", "width": 2},
            fill="tozeroy",
            fillcolor="rgba(0,212,170,0.1)",
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1a1a2e",
            plot_bgcolor="#16213e",
            font={"color": "#e0e0e0"},
            margin={"t": 10, "b": 30, "l": 60, "r": 10},
            height=280,
            showlegend=False,
        )
        fig.update_xaxes(gridcolor="#2a2a4a")
        fig.update_yaxes(gridcolor="#2a2a4a")
        return jsonify(json.loads(plotly.io.to_json(fig)))
    except Exception:
        return jsonify({"error": "Failed to retrieve indicator data. Please try again later."}), 500


@app.route("/api/advisor-analysis", methods=["POST"])
def api_advisor_analysis():
    """Return personalized advisor recommendations based on user inputs."""
    data = request.get_json(force=True)
    risk = data.get("risk", "moderate")
    horizon = data.get("horizon", "medium")  # short / medium / long
    amount = data.get("amount", 10000)
    assets = data.get("assets", [])

    profile = ADVISOR_ANALYSIS.get(risk, ADVISOR_ANALYSIS["moderate"])

    # Dynamic insights based on inputs
    insights = []
    if horizon == "short":
        insights.append("⏰ 短线投资（<1年）建议关注技术面信号，控制仓位，设置止损点")
    elif horizon == "long":
        insights.append("📅 长线投资（>5年）建议坚持定投，忽略短期波动，复利是最强武器")
    else:
        insights.append("📊 中线投资（1-5年）平衡技术面和基本面，定期再平衡组合")

    if float(amount) > 100000:
        insights.append("💰 资金量较大，建议分批建仓（3-6个月），避免一次性全仓")
    elif float(amount) < 5000:
        insights.append("💡 资金量较小，建议优先投资宽基ETF，降低个股风险")

    if "crypto" in assets:
        insights.append("₿ 加密货币高波动，建议仓位不超过总资产的10-15%")
    if "china" in assets:
        insights.append("🇨🇳 中国资产估值较低，但需关注政策风险，建议长线持有")

    return jsonify({
        "profile": profile,
        "insights": insights,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    })


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
