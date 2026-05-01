import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import numpy as np
from datetime import datetime

# ===== 페이지 설정 =====
st.set_page_config(
    page_title="Deep-Value Quant Guardrail",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 종목 DB =====
STOCK_DATABASE = {
    # 코스피
    "삼성전자": {"ticker": "005930.KS", "code": "005930"},
    "SK하이닉스": {"ticker": "000660.KS", "code": "000660"},
    "NAVER": {"ticker": "035420.KS", "code": "035420"},
    "카카오": {"ticker": "035720.KS", "code": "035720"},
    "삼성바이오로직스": {"ticker": "207940.KS", "code": "207940"},
    "LG화학": {"ticker": "051910.KS", "code": "051910"},
    "삼성SDI": {"ticker": "006400.KS", "code": "006400"},
    "현대차": {"ticker": "005380.KS", "code": "005380"},
    "기아": {"ticker": "000270.KS", "code": "000270"},
    "POSCO홀딩스": {"ticker": "005490.KS", "code": "005490"},
    "셀트리온": {"ticker": "068270.KS", "code": "068270"},
    "KB금융": {"ticker": "105560.KS", "code": "105560"},
    "신한지주": {"ticker": "055550.KS", "code": "055550"},
    "현대제철": {"ticker": "004020.KS", "code": "004020"},
    "LG전자": {"ticker": "066570.KS", "code": "066570"},
    "삼성물산": {"ticker": "028260.KS", "code": "028260"},
    "SK이노베이션": {"ticker": "096770.KS", "code": "096770"},
    "한국전력": {"ticker": "015760.KS", "code": "015760"},
    "SK텔레콤": {"ticker": "017670.KS", "code": "017670"},
    "KT&G": {"ticker": "033780.KS", "code": "033780"},
    "HMM": {"ticker": "011200.KS", "code": "011200"},
    "LG생활건강": {"ticker": "051900.KS", "code": "051900"},
    "삼성생명": {"ticker": "032830.KS", "code": "032830"},
    "삼성전기": {"ticker": "009150.KS", "code": "009150"},
    "하나금융지주": {"ticker": "086790.KS", "code": "086790"},
    "포스코퓨처엠": {"ticker": "003670.KS", "code": "003670"},
    "SK스퀘어": {"ticker": "402340.KS", "code": "402340"},
    "LG유플러스": {"ticker": "032640.KS", "code": "032640"},
    "기업은행": {"ticker": "024110.KS", "code": "024110"},
    "영원무역": {"ticker": "111770.KS", "code": "111770"},
    
    # 코스닥
    "에코프로비엠": {"ticker": "247540.KQ", "code": "247540"},
    "엘앤에프": {"ticker": "066970.KQ", "code": "066970"},
    "에코프로": {"ticker": "086520.KQ", "code": "086520"},
    "알테오젠": {"ticker": "196170.KQ", "code": "196170"},
    "리노공업": {"ticker": "058470.KQ", "code": "058470"},
    "위메이드": {"ticker": "112040.KQ", "code": "112040"},
    "펄어비스": {"ticker": "263750.KQ", "code": "263750"},
    "카카오게임즈": {"ticker": "293490.KQ", "code": "293490"},
    "셀트리온헬스케어": {"ticker": "091990.KQ", "code": "091990"},
    "셀트리온제약": {"ticker": "068760.KQ", "code": "068760"},
    "클래시스": {"ticker": "214150.KQ", "code": "214150"},
    
    # 미국
    "Apple": {"ticker": "AAPL", "code": "AAPL"},
    "Microsoft": {"ticker": "MSFT", "code": "MSFT"},
    "Google": {"ticker": "GOOGL", "code": "GOOGL"},
    "Amazon": {"ticker": "AMZN", "code": "AMZN"},
    "Tesla": {"ticker": "TSLA", "code": "TSLA"},
    "NVIDIA": {"ticker": "NVDA", "code": "NVDA"},
    "Meta": {"ticker": "META", "code": "META"},
    "Berkshire Hathaway": {"ticker": "BRK-B", "code": "BRK-B"},
    "JPMorgan": {"ticker": "JPM", "code": "JPM"},
    "Visa": {"ticker": "V", "code": "V"},
    "Walmart": {"ticker": "WMT", "code": "WMT"},
    "Mastercard": {"ticker": "MA", "code": "MA"},
    "Netflix": {"ticker": "NFLX", "code": "NFLX"},
    "Disney": {"ticker": "DIS", "code": "DIS"},
    "Nike": {"ticker": "NKE", "code": "NKE"},
    "Coca-Cola": {"ticker": "KO", "code": "KO"},
    "Intel": {"ticker": "INTC", "code": "INTC"},
    "AMD": {"ticker": "AMD", "code": "AMD"},
}

FRED_KEY = '728ddd23b68ab6b6c0195e71423285d2'

# ===== CSS =====
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: white; padding: 16px; border-radius: 8px;
        border: 1px solid #e0e0e0; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .stMetric label { color: #666 !important; font-size: 12px; font-weight: 600; }
    .stMetric [data-testid="stMetricValue"] { color: #1a1a1a !important; font-size: 24px; font-weight: 700; }
    h1, h2, h3 { color: #1a1a1a; font-weight: 700; }
    .score-card {
        background: white; border: 2px solid #e0e0e0; border-radius: 12px;
        padding: 24px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .score-number { font-size: 56px; font-weight: 800; margin: 16px 0; }
    .score-label { font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 1px; }
    .buffett-card {
        background: linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%);
        border: 2px solid #ff9800;
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(255,152,0,0.2);
    }
    .buffett-title {
        font-size: 24px;
        font-weight: 800;
        color: #e65100;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .buffett-verdict {
        font-size: 20px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 16px 0;
        padding: 16px;
        background: white;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
    }
    .buffett-philosophy {
        background: rgba(255,255,255,0.7);
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
        font-size: 14px;
        line-height: 1.7;
    }
    .insight-box { background: #f0f7ff; border-left: 4px solid #2196F3; padding: 16px; border-radius: 4px; margin: 12px 0; }
    .warning-box { background: #fff3e0; border-left: 4px solid #ff9800; padding: 16px; border-radius: 4px; margin: 12px 0; }
    .success-box { background: #e8f5e9; border-left: 4px solid #4caf50; padding: 16px; border-radius: 4px; margin: 12px 0; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { background-color: white; border: 1px solid #e0e0e0; color: #666; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #2196F3; border-color: #2196F3; color: white; }
</style>
""", unsafe_allow_html=True)

# ===== 검색 =====
def search_stocks(query):
    query_lower = query.lower()
    results = []
    for name, data in STOCK_DATABASE.items():
        if query_lower in name.lower() or query_lower in data['code'].lower():
            results.append(f"{name} ({data['code']})")
    return sorted(results)

# ===== FRED =====
@st.cache_data(ttl=3600)
def fetch_fred_data(series_id):
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {'series_id': series_id, 'api_key': FRED_KEY, 'file_type': 'json', 'limit': 180}
        response = requests.get(url, params=params)
        data = response.json()
        df = pd.DataFrame(data['observations'])
        df = df[df['value'] != '.']
        df['value'] = pd.to_numeric(df['value'])
        return df
    except:
        return pd.DataFrame()

# ===== 주식 데이터 =====
@st.cache_data(ttl=300)
def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="6mo")
        balance_sheet = stock.balance_sheet
        
        return {
            'info': info,
            'history': hist,
            'balance_sheet': balance_sheet,
            'success': True
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ===== NCAV 계산 (워렌 버핏 평가용) =====
def calculate_ncav(balance_sheet, market_cap):
    try:
        if balance_sheet.empty or not market_cap:
            return None, None
        
        latest = balance_sheet.iloc[:, 0]
        current_assets = latest.get('Current Assets', latest.get('Total Current Assets', None))
        total_liabilities = latest.get('Total Liabilities Net Minority Interest', 
                                      latest.get('Total Liabilities', None))
        
        if current_assets is None or total_liabilities is None:
            return None, None
        
        ncav = current_assets - total_liabilities
        ncav_ratio = ncav / market_cap if market_cap > 0 else 0
        
        return ncav, ncav_ratio
    except:
        return None, None

# ===== 워렌 버핏 스타일 평가 =====
def warren_buffett_evaluation(info, balance_sheet, market_cap):
    """
    워렌 버핏이라면 이 주식에 투자했을까?
    """
    
    # NCAV 계산 (벤저민 그레이엄 스타일)
    ncav, ncav_ratio = calculate_ncav(balance_sheet, market_cap)
    
    # 버핏의 핵심 지표
    roe = info.get('returnOnEquity', 0)
    debt_to_equity = info.get('debtToEquity', 100)
    current_ratio = info.get('currentRatio', 1.0)
    profit_margin = info.get('profitMargins', 0)
    
    # 평가 점수
    buffett_score = 0
    reasons = []
    
    # 1. NCAV (담뱃재 투자)
    if ncav_ratio and ncav_ratio >= 1.0:
        buffett_score += 30
        reasons.append(f"✅ 벤저민 그레이엄의 담뱃재(Cigar Butt) 기준 충족 (NCAV 배수: {ncav_ratio:.2f}x)")
    elif ncav_ratio and ncav_ratio >= 0.67:
        buffett_score += 20
        reasons.append(f"⚠️ NCAV가 시가총액을 초과하지는 않지만 저평가 구간 (NCAV 배수: {ncav_ratio:.2f}x)")
    else:
        reasons.append(f"❌ NCAV 기준 미달 (현금성 자산이 부족하거나 부채가 과다)")
    
    # 2. ROE (높은 수익성)
    if roe and roe * 100 >= 15:
        buffett_score += 25
        reasons.append(f"✅ 우수한 자기자본이익률 (ROE: {roe*100:.1f}%)")
    elif roe and roe * 100 >= 10:
        buffett_score += 15
        reasons.append(f"⚠️ 적정 수준의 ROE ({roe*100:.1f}%)")
    else:
        reasons.append(f"❌ 낮은 자기자본이익률 (ROE: {roe*100:.1f}% - 버핏은 최소 15% 이상 선호)")
    
    # 3. 낮은 부채
    if debt_to_equity <= 50:
        buffett_score += 25
        reasons.append(f"✅ 보수적인 재무구조 (부채비율: {debt_to_equity:.1f}%)")
    elif debt_to_equity <= 100:
        buffett_score += 15
        reasons.append(f"⚠️ 적정 부채비율 ({debt_to_equity:.1f}%)")
    else:
        reasons.append(f"❌ 높은 부채비율 ({debt_to_equity:.1f}% - 버핏은 부채를 극도로 경계)")
    
    # 4. 높은 현금흐름
    if current_ratio >= 2.0:
        buffett_score += 20
        reasons.append(f"✅ 풍부한 유동성 (유동비율: {current_ratio:.2f})")
    elif current_ratio >= 1.5:
        buffett_score += 10
        reasons.append(f"⚠️ 적정 유동성 (유동비율: {current_ratio:.2f})")
    else:
        reasons.append(f"❌ 부족한 유동성 (유동비율: {current_ratio:.2f} - 단기 지급능력 우려)")
    
    # 최종 판단
    if buffett_score >= 70:
        verdict = "💎 한국의 워렌 버핏이라면 이 주식에 투자했을 것입니다"
        verdict_color = "#4caf50"
    elif buffett_score >= 50:
        verdict = "🤔 한국의 워렌 버핏이라면 신중하게 검토했을 것입니다"
        verdict_color = "#ff9800"
    else:
        verdict = "❌ 한국의 워렌 버핏이라면 현 시점에 이 주식에 투자하지 않았을 것입니다"
        verdict_color = "#f44336"
    
    return {
        'score': buffett_score,
        'verdict': verdict,
        'verdict_color': verdict_color,
        'reasons': reasons,
        'ncav': ncav,
        'ncav_ratio': ncav_ratio
    }

# ===== Guardrail Score (연속형) =====
def calculate_guardrail_score_v2(info):
    scores = {}
    
    # 1. 밸류에이션 (40%)
    pbr = info.get('priceToBook', None)
    per = info.get('trailingPE', None)
    
    valuation_score = 0
    if pbr is not None:
        if pbr <= 0.5:
            pbr_score = 100
        elif pbr >= 3.0:
            pbr_score = 0
        else:
            pbr_score = 100 - ((pbr - 0.5) / 2.5) * 100
        valuation_score += pbr_score * 0.6
    
    if per is not None and per > 0:
        if per <= 10:
            per_score = 100
        elif per >= 30:
            per_score = 0
        else:
            per_score = 100 - ((per - 10) / 20) * 100
        valuation_score += per_score * 0.4
    
    scores['valuation'] = valuation_score if valuation_score > 0 else 50
    
    # 2. 수익성 (30%)
    roe = info.get('returnOnEquity', None)
    profit_margin = info.get('profitMargins', None)
    
    profitability_score = 0
    if roe is not None:
        roe_pct = roe * 100
        if roe_pct >= 15:
            roe_score = 100
        elif roe_pct <= 0:
            roe_score = 0
        else:
            roe_score = (roe_pct / 15) * 100
        profitability_score += roe_score * 0.6
    
    if profit_margin is not None:
        margin_pct = profit_margin * 100
        if margin_pct >= 10:
            margin_score = 100
        elif margin_pct <= 0:
            margin_score = 0
        else:
            margin_score = (margin_pct / 10) * 100
        profitability_score += margin_score * 0.4
    
    scores['profitability'] = profitability_score if profitability_score > 0 else 50
    
    # 3. 안정성 (20%)
    debt_to_equity = info.get('debtToEquity', 100)
    current_ratio = info.get('currentRatio', 1.0)
    
    stability_score = 0
    if debt_to_equity is not None:
        if debt_to_equity <= 50:
            debt_score = 100
        elif debt_to_equity >= 200:
            debt_score = 0
        else:
            debt_score = 100 - ((debt_to_equity - 50) / 150) * 100
        stability_score += debt_score * 0.5
    
    if current_ratio is not None:
        if current_ratio >= 2.0:
            current_score = 100
        elif current_ratio <= 1.0:
            current_score = 0
        else:
            current_score = (current_ratio - 1.0) * 100
        stability_score += current_score * 0.5
    
    scores['stability'] = stability_score if stability_score > 0 else 50
    
    # 4. 성장성 (10%)
    revenue_growth = info.get('revenueGrowth', None)
    earnings_growth = info.get('earningsQuarterlyGrowth', None)
    
    growth_score = 0
    if revenue_growth is not None:
        growth_pct = revenue_growth * 100
        if growth_pct >= 20:
            rev_growth_score = 100
        elif growth_pct <= -10:
            rev_growth_score = 0
        else:
            rev_growth_score = ((growth_pct + 10) / 30) * 100
        growth_score += rev_growth_score * 0.5
    
    if earnings_growth is not None:
        earn_growth_pct = earnings_growth * 100
        if earn_growth_pct >= 20:
            earn_growth_score = 100
        elif earn_growth_pct <= -10:
            earn_growth_score = 0
        else:
            earn_growth_score = ((earn_growth_pct + 10) / 30) * 100
        growth_score += earn_growth_score * 0.5
    
    scores['growth'] = growth_score if growth_score > 0 else 50
    
    final_score = (
        scores['valuation'] * 0.40 +
        scores['profitability'] * 0.30 +
        scores['stability'] * 0.20 +
        scores['growth'] * 0.10
    )
    
    return round(final_score, 2), scores

def get_score_grade(score):
    if score >= 80:
        return "STRONG", "#4caf50"
    elif score >= 65:
        return "GOOD", "#8bc34a"
    elif score >= 50:
        return "MODERATE", "#ff9800"
    elif score >= 35:
        return "WEAK", "#ff5722"
    else:
        return "AVOID", "#f44336"

# ===== 사이드바 =====
with st.sidebar:
    st.markdown("## 🔍 종목 검색")
    
    search_query = st.text_input(
        "종목명 또는 코드 입력",
        placeholder="예: 삼성, 005930, Apple, AAPL",
        help="한글, 영문, 코드번호 모두 검색 가능"
    )
    
    if search_query:
        filtered_stocks = search_stocks(search_query)
        
        if filtered_stocks:
            selected = st.selectbox("검색 결과", filtered_stocks, key="search_result")
            stock_name = selected.split(" (")[0]
            ticker = STOCK_DATABASE[stock_name]['ticker']
        else:
            st.warning("검색 결과가 없습니다")
            selected = None
            ticker = None
    else:
        st.markdown("#### 인기 종목")
        popular = ["삼성전자 (005930)", "SK하이닉스 (000660)", "Apple (AAPL)", "Tesla (TSLA)", "NVIDIA (NVDA)"]
        selected = st.selectbox("선택", popular, key="popular")
        stock_name = selected.split(" (")[0]
        ticker = STOCK_DATABASE[stock_name]['ticker']
    
    analyze_btn = st.button("📊 분석 시작", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 📈 거시지표")
    with st.spinner("로딩..."):
        dff = fetch_fred_data('DFF')
        fx = fetch_fred_data('DEXKOUS')
        us10y = fetch_fred_data('DGS10')
        
        if len(dff) > 0:
            st.metric("미국 기준금리", f"{dff['value'].iloc[-1]:.2f}%")
        if len(fx) > 0:
            st.metric("USD/KRW", f"{fx['value'].iloc[-1]:.2f}")
        if len(us10y) > 0:
            st.metric("미국 10년물", f"{us10y['value'].iloc[-1]:.2f}%")

# ===== 메인 =====
st.title("📊 Deep-Value Quant Guardrail")
st.markdown("**실시간 데이터 기반 다차원 주식 평가 시스템**")

if analyze_btn and ticker:
    
    with st.spinner(f"**{stock_name} ({ticker})** 분석 중..."):
        data = fetch_stock_data(ticker)
    
    if not data['success']:
        st.error(f"❌ 데이터 로딩 실패: {data['error']}")
    else:
        info = data['info']
        hist = data['history']
        balance_sheet = data['balance_sheet']
        
        stock_name_full = info.get('longName', info.get('shortName', stock_name))
        current_price = info.get('currentPrice', hist['Close'].iloc[-1] if len(hist) > 0 else 0)
        market_cap = info.get('marketCap', 0)
        
        # ===== 헤더 =====
        st.markdown(f"## {stock_name_full}")
        st.caption(f"{ticker} · 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # ===== KPI =====
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            prev_close = info.get('previousClose', current_price)
            change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
            currency = "₩" if ticker.endswith('.KS') or ticker.endswith('.KQ') else "$"
            st.metric("현재가", f"{currency}{current_price:,.2f}", f"{change_pct:+.2f}%")
        
        with col2:
            st.metric("시가총액", f"${market_cap/1e9:.2f}B" if market_cap else "N/A")
        
        with col3:
            pbr = info.get('priceToBook', 0)
            st.metric("PBR", f"{pbr:.2f}" if pbr else "N/A")
        
        with col4:
            per = info.get('trailingPE', 0)
            st.metric("PER", f"{per:.2f}" if per else "N/A")
        
        with col5:
            roe = info.get('returnOnEquity', 0)
            st.metric("ROE", f"{roe*100:.2f}%" if roe else "N/A")
        
        st.markdown("---")
        
        # ===== Guardrail Score =====
        final_score, component_scores = calculate_guardrail_score_v2(info)
        grade, grade_color = get_score_grade(final_score)
        
        st.markdown("### 🎯 Guardrail Score")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div class='score-card'>
                <div class='score-label'>종합 점수</div>
                <div class='score-number' style='color:{grade_color}'>{final_score:.2f}</div>
                <div style='font-size:20px; font-weight:700; color:{grade_color}'>{grade}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 점수 구성")
            
            st.markdown(f"**밸류에이션 (40%):** {component_scores['valuation']:.2f}/100")
            st.progress(component_scores['valuation'] / 100)
            
            st.markdown(f"**수익성 (30%):** {component_scores['profitability']:.2f}/100")
            st.progress(component_scores['profitability'] / 100)
            
            st.markdown(f"**안정성 (20%):** {component_scores['stability']:.2f}/100")
            st.progress(component_scores['stability'] / 100)
            
            st.markdown(f"**성장성 (10%):** {component_scores['growth']:.2f}/100")
            st.progress(component_scores['growth'] / 100)
        
        st.markdown("---")
        
        # ===== 워렌 버핏 평가 (추가) =====
        st.markdown("### 💎 워렌 버핏 스타일 평가")
        
        buffett_eval = warren_buffett_evaluation(info, balance_sheet, market_cap)
        
        st.markdown(f"""
        <div class='buffett-card'>
            <div class='buffett-title'>
                <span style='font-size:32px'>💼</span>
                한국의 워렌 버핏이라면?
            </div>
            
            <div class='buffett-verdict' style='border-left-color:{buffett_eval['verdict_color']}'>
                {buffett_eval['verdict']}
            </div>
            
            <div class='buffett-philosophy'>
                <strong>💡 워렌 버핏의 투자 철학</strong><br><br>
                
                워렌 버핏은 스승인 <strong>벤저민 그레이엄</strong>으로부터 가치투자를 배웠습니다. 
                그레이엄의 "<strong>담뱃재(Cigar Butt)</strong>" 투자 전략은 다음과 같습니다:
                <br><br>
                
                <em>"길거리에 버려진 담배꽁초처럼, 한두 모금 남아있다면 공짜로 주워 피울 가치가 있다"</em>
                <br><br>
                
                이는 <strong>청산가치(NCAV: 유동자산 - 총부채)</strong>보다 시가총액이 낮은 기업을 매수하는 전략입니다.
                이론적으로 회사를 당장 청산해도 이익이 나는 구조이기 때문에 <strong>하방 리스크가 제한적</strong>입니다.
                <br><br>
                
                후에 버핏은 "<strong>위대한 기업을 합리적 가격에</strong>" 매수하는 방향으로 진화했지만,
                높은 ROE, 낮은 부채비율, 풍부한 현금흐름이라는 핵심 원칙은 변하지 않았습니다.
            </div>
            
            <div style='margin-top:16px'>
                <strong>📊 평가 근거:</strong>
            </div>
        """, unsafe_allow_html=True)
        
        for reason in buffett_eval['reasons']:
            if reason.startswith("✅"):
                st.success(reason)
            elif reason.startswith("⚠️"):
                st.warning(reason)
            else:
                st.error(reason)
        
        st.markdown("""
        <div class='buffett-philosophy' style='margin-top:16px'>
            <strong>⚠️ 중요한 면책사항</strong><br><br>
            
            이 평가는 <strong>이 주식이 오르지 않는다는 의미가 아닙니다.</strong><br>
            오히려 높은 리스크는 <strong>더 큰 가격 상승 가능성</strong>을 동반할 수 있습니다.
            <br><br>
            
            버핏 스타일에 부합하지 않는 종목도 성장주, 테마주로서 큰 수익을 낼 수 있습니다.
            이 평가는 단지 "<strong>보수적 가치투자자의 관점</strong>"에서 본 안전마진과 펀더멘털 건전성을 보여줄 뿐입니다.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ===== 차트 =====
        st.markdown("### 📈 주가 차트")
        
        if len(hist) > 0:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=('주가', '거래량')
            )
            
            fig.add_trace(
                go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name='주가',
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                ),
                row=1, col=1
            )
            
            colors = ['#26a69a' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] else '#ef5350' 
                      for i in range(len(hist))]
            
            fig.add_trace(
                go.Bar(
                    x=hist.index,
                    y=hist['Volume'],
                    name='거래량',
                    marker_color=colors,
                    showlegend=False
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                height=600,
                xaxis_rangeslider_visible=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#1a1a1a'),
                hovermode='x unified'
            )
            
            fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
            fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
            
            st.plotly_chart(fig, use_container_width=True)
        
        # ===== 탭 =====
        tab1, tab2, tab3 = st.tabs(["📊 재무 분석", "💡 종합 인사이트", "📋 상세 정보"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 수익성 지표")
                st.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.2f}%")
                st.metric("ROA", f"{info.get('returnOnAssets', 0)*100:.2f}%")
                st.metric("영업이익률", f"{info.get('profitMargins', 0)*100:.2f}%")
            
            with col2:
                st.markdown("#### 안정성 지표")
                st.metric("부채비율", f"{info.get('debtToEquity', 0):.2f}%")
                st.metric("유동비율", f"{info.get('currentRatio', 0):.2f}")
                st.metric("당좌비율", f"{info.get('quickRatio', 0):.2f}")
        
        with tab2:
            st.markdown("#### Guardrail Score 종합 평가")
            
            if final_score >= 80:
                st.markdown(f"""
                <div class='success-box'>
                <strong>✅ 우수한 투자 대상</strong><br>
                {stock_name_full}은(는) Guardrail Score {final_score:.2f}점으로 STRONG 등급을 받았습니다.
                밸류에이션, 수익성, 안정성 모든 면에서 우수한 평가를 받았습니다.
                </div>
                """, unsafe_allow_html=True)
            
            elif final_score >= 50:
                st.markdown(f"""
                <div class='insight-box'>
                <strong>ℹ️ 중간 수준 투자 대상</strong><br>
                {stock_name_full}은(는) Guardrail Score {final_score:.2f}점으로 MODERATE 등급입니다.
                일부 지표에서 개선이 필요하나, 투자 검토 가능한 수준입니다.
                </div>
                """, unsafe_allow_html=True)
            
            else:
                st.markdown(f"""
                <div class='warning-box'>
                <strong>⚠️ 주의 필요</strong><br>
                {stock_name_full}은(는) Guardrail Score {final_score:.2f}점으로 낮은 등급입니다.
                투자 전 심층 분석이 권장됩니다.
                </div>
                """, unsafe_allow_html=True)
            
            if component_scores['valuation'] >= 70:
                st.success(f"✅ 밸류에이션: 현재 PBR {pbr:.2f}배로 저평가 구간입니다.")
            
            if component_scores['profitability'] >= 70:
                st.success(f"✅ 수익성: ROE {info.get('returnOnEquity', 0)*100:.2f}%로 우수한 수익성을 보입니다.")
            
            if component_scores['stability'] < 50:
                st.warning(f"⚠️ 안정성: 부채비율 {info.get('debtToEquity', 0):.1f}%로 재무 안정성 점검이 필요합니다.")
        
        with tab3:
            st.json(info, expanded=False)

else:
    st.info("👈 왼쪽에서 종목을 검색하고 '분석 시작'을 눌러주세요")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔍 스마트 검색**
        - 한글 초성 검색
        - 종목코드 검색
        - 영문명 검색
        """)
    
    with col2:
        st.markdown("""
        **📊 이중 평가 시스템**
        - Guardrail Score (연속형 모델)
        - 워렌 버핏 스타일 평가
        - 실시간 데이터 반영
        """)
    
    with col3:
        st.markdown("""
        **🌍 전세계 주식**
        - 코스피/코스닥 전체
        - 미국 주요 종목
        - 실시간 업데이트
        """)
