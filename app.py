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

# ===== 종목 DB (한글명 추가) =====
STOCK_DATABASE = {
    # 코스피
    "삼성전자": {"ticker": "005930.KS", "code": "005930", "name_kr": "삼성전자"},
    "SK하이닉스": {"ticker": "000660.KS", "code": "000660", "name_kr": "SK하이닉스"},
    "NAVER": {"ticker": "035420.KS", "code": "035420", "name_kr": "네이버"},
    "카카오": {"ticker": "035720.KS", "code": "035720", "name_kr": "카카오"},
    "삼성바이오로직스": {"ticker": "207940.KS", "code": "207940", "name_kr": "삼성바이오로직스"},
    "LG화학": {"ticker": "051910.KS", "code": "051910", "name_kr": "LG화학"},
    "LG생활건강": {"ticker": "051900.KS", "code": "051900", "name_kr": "LG생활건강"},
    "삼성SDI": {"ticker": "006400.KS", "code": "006400", "name_kr": "삼성SDI"},
    "현대차": {"ticker": "005380.KS", "code": "005380", "name_kr": "현대자동차"},
    "현대제철": {"ticker": "004020.KS", "code": "004020", "name_kr": "현대제철"},
    "기아": {"ticker": "000270.KS", "code": "000270", "name_kr": "기아"},
    "POSCO홀딩스": {"ticker": "005490.KS", "code": "005490", "name_kr": "POSCO홀딩스"},
    "셀트리온": {"ticker": "068270.KS", "code": "068270", "name_kr": "셀트리온"},
    "KB금융": {"ticker": "105560.KS", "code": "105560", "name_kr": "KB금융"},
    "신한지주": {"ticker": "055550.KS", "code": "055550", "name_kr": "신한지주"},
    "LG전자": {"ticker": "066570.KS", "code": "066570", "name_kr": "LG전자"},
    "삼성물산": {"ticker": "028260.KS", "code": "028260", "name_kr": "삼성물산"},
    "SK이노베이션": {"ticker": "096770.KS", "code": "096770", "name_kr": "SK이노베이션"},
    "한국전력": {"ticker": "015760.KS", "code": "015760", "name_kr": "한국전력"},
    "SK텔레콤": {"ticker": "017670.KS", "code": "017670", "name_kr": "SK텔레콤"},
    "KT&G": {"ticker": "033780.KS", "code": "033780", "name_kr": "KT&G"},
    "HMM": {"ticker": "011200.KS", "code": "011200", "name_kr": "HMM"},
    "삼성생명": {"ticker": "032830.KS", "code": "032830", "name_kr": "삼성생명"},
    "삼성전기": {"ticker": "009150.KS", "code": "009150", "name_kr": "삼성전기"},
    "하나금융지주": {"ticker": "086790.KS", "code": "086790", "name_kr": "하나금융지주"},
    "포스코퓨처엠": {"ticker": "003670.KS", "code": "003670", "name_kr": "포스코퓨처엠"},
    "SK스퀘어": {"ticker": "402340.KS", "code": "402340", "name_kr": "SK스퀘어"},
    "LG유플러스": {"ticker": "032640.KS", "code": "032640", "name_kr": "LG유플러스"},
    "영원무역": {"ticker": "111770.KS", "code": "111770", "name_kr": "영원무역"},
    
    # 코스닥
    "에코프로비엠": {"ticker": "247540.KQ", "code": "247540", "name_kr": "에코프로비엠"},
    "엘앤에프": {"ticker": "066970.KQ", "code": "066970", "name_kr": "엘앤에프"},
    "에코프로": {"ticker": "086520.KQ", "code": "086520", "name_kr": "에코프로"},
    "알테오젠": {"ticker": "196170.KQ", "code": "196170", "name_kr": "알테오젠"},
    "리노공업": {"ticker": "058470.KQ", "code": "058470", "name_kr": "리노공업"},
    "위메이드": {"ticker": "112040.KQ", "code": "112040", "name_kr": "위메이드"},
    "펄어비스": {"ticker": "263750.KQ", "code": "263750", "name_kr": "펄어비스"},
    "카카오게임즈": {"ticker": "293490.KQ", "code": "293490", "name_kr": "카카오게임즈"},
    "셀트리온헬스케어": {"ticker": "091990.KQ", "code": "091990", "name_kr": "셀트리온헬스케어"},
    "셀트리온제약": {"ticker": "068760.KQ", "code": "068760", "name_kr": "셀트리온제약"},
    
    # 미국 (한글명 추가)
    "애플": {"ticker": "AAPL", "code": "AAPL", "name_kr": "애플"},
    "Apple": {"ticker": "AAPL", "code": "AAPL", "name_kr": "애플"},
    "마이크로소프트": {"ticker": "MSFT", "code": "MSFT", "name_kr": "마이크로소프트"},
    "Microsoft": {"ticker": "MSFT", "code": "MSFT", "name_kr": "마이크로소프트"},
    "구글": {"ticker": "GOOGL", "code": "GOOGL", "name_kr": "구글"},
    "Google": {"ticker": "GOOGL", "code": "GOOGL", "name_kr": "구글"},
    "아마존": {"ticker": "AMZN", "code": "AMZN", "name_kr": "아마존"},
    "Amazon": {"ticker": "AMZN", "code": "AMZN", "name_kr": "아마존"},
    "테슬라": {"ticker": "TSLA", "code": "TSLA", "name_kr": "테슬라"},
    "Tesla": {"ticker": "TSLA", "code": "TSLA", "name_kr": "테슬라"},
    "엔비디아": {"ticker": "NVDA", "code": "NVDA", "name_kr": "엔비디아"},
    "NVIDIA": {"ticker": "NVDA", "code": "NVDA", "name_kr": "엔비디아"},
    "메타": {"ticker": "META", "code": "META", "name_kr": "메타"},
    "Meta": {"ticker": "META", "code": "META", "name_kr": "메타"},
    "버크셔해서웨이": {"ticker": "BRK-B", "code": "BRK-B", "name_kr": "버크셔해서웨이"},
    "Berkshire": {"ticker": "BRK-B", "code": "BRK-B", "name_kr": "버크셔해서웨이"},
    "JP모건": {"ticker": "JPM", "code": "JPM", "name_kr": "JP모건"},
    "JPMorgan": {"ticker": "JPM", "code": "JPM", "name_kr": "JP모건"},
    "비자": {"ticker": "V", "code": "V", "name_kr": "비자"},
    "Visa": {"ticker": "V", "code": "V", "name_kr": "비자"},
    "월마트": {"ticker": "WMT", "code": "WMT", "name_kr": "월마트"},
    "Walmart": {"ticker": "WMT", "code": "WMT", "name_kr": "월마트"},
    "코카콜라": {"ticker": "KO", "code": "KO", "name_kr": "코카콜라"},
    "Coca-Cola": {"ticker": "KO", "code": "KO", "name_kr": "코카콜라"},
    "인텔": {"ticker": "INTC", "code": "INTC", "name_kr": "인텔"},
    "Intel": {"ticker": "INTC", "code": "INTC", "name_kr": "인텔"},
}

# 버핏 추천 종목 (저PBR + 우량주)
BUFFETT_PICKS = [
    {"ticker": "005930.KS", "name": "삼성전자", "reason": "저PBR (0.9배) + 높은 시총 + 안정적 배당"},
    {"ticker": "066570.KS", "name": "LG전자", "reason": "PBR 0.4배 극저평가 + 가전 글로벌 1위"},
    {"ticker": "105560.KS", "name": "KB금융", "reason": "PBR 0.5배 + 배당 5% 이상 + 낮은 부채"},
    {"ticker": "055550.KS", "name": "신한지주", "reason": "PBR 0.4배 + 은행주 대표 + 높은 배당"},
    {"ticker": "033780.KS", "name": "KT&G", "reason": "독과점 사업구조 + 배당 6% + PBR 1.0"},
    {"ticker": "BRK-B", "name": "버크셔해서웨이", "reason": "워렌 버핏의 직접 운영 기업"},
    {"ticker": "KO", "name": "코카콜라", "reason": "버핏의 대표 보유주 + 배당귀족주"},
    {"ticker": "V", "name": "비자", "reason": "독과점 결제망 + 높은 마진"},
    {"ticker": "JPM", "name": "JP모건", "reason": "미국 1위 은행 + 안정적 수익"},
    {"ticker": "WMT", "name": "월마트", "reason": "경기방어주 + 안정적 현금흐름"},
]

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
    .stMetric [data-testid="stMetricValue"] { color: #1a1a1a !important; font-size: 20px; font-weight: 700; }
    h1, h2, h3 { color: #1a1a1a; font-weight: 700; }
    .score-card {
        background: white; border: 2px solid #e0e0e0; border-radius: 12px;
        padding: 24px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .score-number { font-size: 56px; font-weight: 800; margin: 16px 0; }
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
    }
    .buffett-verdict {
        font-size: 18px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 16px 0;
        padding: 16px;
        background: white;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
    }
    .buffett-disclaimer {
        background: rgba(255,255,255,0.9);
        padding: 20px;
        border-radius: 8px;
        margin: 16px 0;
        border: 2px dashed #ff9800;
    }
    .pick-card {
        background: white;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    .pick-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    .insight-box { background: #f0f7ff; border-left: 4px solid #2196F3; padding: 16px; border-radius: 4px; margin: 12px 0; }
    .warning-box { background: #fff3e0; border-left: 4px solid #ff9800; padding: 16px; border-radius: 4px; margin: 12px 0; }
    .success-box { background: #e8f5e9; border-left: 4px solid #4caf50; padding: 16px; border-radius: 4px; margin: 12px 0; }
</style>
""", unsafe_allow_html=True)

# ===== 검색 =====
def search_stocks(query):
    query_lower = query.lower()
    results = []
    seen = set()
    for name, data in STOCK_DATABASE.items():
        ticker = data['ticker']
        if ticker in seen:
            continue
        if query_lower in name.lower() or query_lower in data['code'].lower():
            results.append(f"{data['name_kr']} ({data['code']})")
            seen.add(ticker)
    return sorted(results)

# ===== FRED =====
@st.cache_data(ttl=3600)
def fetch_fred_data(series_id):
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {'series_id': series_id, 'api_key': FRED_KEY, 'file_type': 'json', 'limit': 180, 'sort_order': 'desc'}
        response = requests.get(url, params=params)
        data = response.json()
        df = pd.DataFrame(data['observations'])
        df = df[df['value'] != '.']
        df['value'] = pd.to_numeric(df['value'])
        return df
    except:
        return pd.DataFrame()

# ===== 주식 데이터 =====
@st.cache_data(ttl=3600)  # 1시간 캐싱
def fetch_stock_data(ticker):
    import time
    
    # User-Agent 설정으로 rate limit 회피
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # yfinance session에 헤더 설정
            session = requests.Session()
            session.headers.update(headers)
            
            stock = yf.Ticker(ticker, session=session)
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
            error_msg = str(e)
            
            # Rate limit 에러인 경우 재시도
            if 'Too Many Requests' in error_msg or '429' in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 2초, 4초, 6초
                    time.sleep(wait_time)
                    continue
            
            return {'success': False, 'error': error_msg}
    
    return {'success': False, 'error': 'Rate limit exceeded. Please try again in a few minutes.'}

# ===== NCAV =====
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

# ===== 워렌 버핏 평가 (완화된 기준) =====
def warren_buffett_evaluation(info, balance_sheet, market_cap, stock_name_kr):
    ncav, ncav_ratio = calculate_ncav(balance_sheet, market_cap)
    
    roe = info.get('returnOnEquity', 0)
    debt_to_equity = info.get('debtToEquity', 100)
    current_ratio = info.get('currentRatio', 1.0)
    
    buffett_score = 0
    reasons = []
    
    # 1. NCAV (완화: 0.5x 이상도 인정)
    if ncav_ratio and ncav_ratio >= 1.0:
        buffett_score += 30
        reasons.append(f"✅ 벤저민 그레이엄의 담뱃재 기준 충족 (NCAV 배수: {ncav_ratio:.2f}x)")
    elif ncav_ratio and ncav_ratio >= 0.5:
        buffett_score += 20
        reasons.append(f"⚠️ NCAV 절반 이상 확보 (NCAV 배수: {ncav_ratio:.2f}x)")
    else:
        reasons.append(f"❌ NCAV 기준 미달 (유동자산이 부족하거나 부채 과다)")
    
    # 2. ROE (완화: 10% 이상)
    if roe and roe * 100 >= 15:
        buffett_score += 25
        reasons.append(f"✅ 우수한 ROE ({roe*100:.1f}%)")
    elif roe and roe * 100 >= 10:
        buffett_score += 18
        reasons.append(f"⚠️ 적정 수준의 ROE ({roe*100:.1f}%)")
    else:
        reasons.append(f"❌ 낮은 ROE ({roe*100:.1f}% - 이상적으로는 15% 이상)")
    
    # 3. 부채 (완화: 100% 이하)
    if debt_to_equity <= 50:
        buffett_score += 25
        reasons.append(f"✅ 보수적 재무구조 (부채비율: {debt_to_equity:.1f}%)")
    elif debt_to_equity <= 100:
        buffett_score += 18
        reasons.append(f"⚠️ 적정 부채비율 ({debt_to_equity:.1f}%)")
    else:
        reasons.append(f"❌ 높은 부채비율 ({debt_to_equity:.1f}%)")
    
    # 4. 유동성
    if current_ratio >= 2.0:
        buffett_score += 20
        reasons.append(f"✅ 풍부한 유동성 (유동비율: {current_ratio:.2f})")
    elif current_ratio >= 1.5:
        buffett_score += 12
        reasons.append(f"⚠️ 적정 유동성 (유동비율: {current_ratio:.2f})")
    else:
        reasons.append(f"❌ 부족한 유동성 (유동비율: {current_ratio:.2f})")
    
    if buffett_score >= 70:
        verdict = f"💎 한국의 워렌 버핏이라면 {stock_name_kr}에 투자했을 것입니다"
        verdict_color = "#4caf50"
    elif buffett_score >= 50:
        verdict = f"🤔 한국의 워렌 버핏이라면 {stock_name_kr}을(를) 신중히 검토했을 것입니다"
        verdict_color = "#ff9800"
    else:
        verdict = f"❌ 한국의 워렌 버핏이라면 현 시점에 {stock_name_kr}에 투자하지 않았을 것입니다"
        verdict_color = "#f44336"
    
    return {
        'score': buffett_score,
        'verdict': verdict,
        'verdict_color': verdict_color,
        'reasons': reasons
    }

# ===== Guardrail Score (개선: PBR 가중치 상향) =====
def calculate_guardrail_score_v2(info):
    scores = {}
    
    # 1. 밸류에이션 (40%)
    pbr = info.get('priceToBook', None)
    per = info.get('trailingPE', None)
    
    valuation_score = 0
    if pbr is not None and pbr > 0:
        # PBR: 0.3 이하 만점, 2.0 이상 0점 (가중치 높임)
        if pbr <= 0.3:
            pbr_score = 100
        elif pbr >= 2.0:
            pbr_score = 0
        else:
            pbr_score = 100 - ((pbr - 0.3) / 1.7) * 100
        valuation_score += pbr_score * 0.7  # PBR 가중치 상승
    
    if per is not None and per > 0:
        if per <= 8:
            per_score = 100
        elif per >= 25:
            per_score = 0
        else:
            per_score = 100 - ((per - 8) / 17) * 100
        valuation_score += per_score * 0.3
    
    scores['valuation'] = valuation_score if valuation_score > 0 else 50
    
    # 2. 수익성 (30%)
    roe = info.get('returnOnEquity', None)
    profit_margin = info.get('profitMargins', None)
    
    profitability_score = 0
    if roe is not None:
        roe_pct = roe * 100
        # ROE: 8% 이상도 점수 부여 (완화)
        if roe_pct >= 15:
            roe_score = 100
        elif roe_pct >= 8:
            roe_score = 50 + ((roe_pct - 8) / 7) * 50
        elif roe_pct >= 0:
            roe_score = (roe_pct / 8) * 50
        else:
            roe_score = 0
        profitability_score += roe_score * 0.6
    
    if profit_margin is not None:
        margin_pct = profit_margin * 100
        if margin_pct >= 10:
            margin_score = 100
        elif margin_pct >= 0:
            margin_score = (margin_pct / 10) * 100
        else:
            margin_score = 0
        profitability_score += margin_score * 0.4
    
    scores['profitability'] = profitability_score if profitability_score > 0 else 50
    
    # 3. 안정성 (20%)
    debt_to_equity = info.get('debtToEquity', None)
    current_ratio = info.get('currentRatio', None)
    
    stability_score = 0
    if debt_to_equity is not None:
        # 부채비율: 120% 이하도 점수 부여 (완화)
        if debt_to_equity <= 50:
            debt_score = 100
        elif debt_to_equity <= 120:
            debt_score = 100 - ((debt_to_equity - 50) / 70) * 50
        elif debt_to_equity <= 200:
            debt_score = 50 - ((debt_to_equity - 120) / 80) * 50
        else:
            debt_score = 0
        stability_score += debt_score * 0.5
    
    if current_ratio is not None:
        if current_ratio >= 2.0:
            current_score = 100
        elif current_ratio >= 1.0:
            current_score = (current_ratio - 1.0) * 100
        else:
            current_score = current_ratio * 50
        stability_score += current_score * 0.5
    
    scores['stability'] = stability_score if stability_score > 0 else 50
    
    # 4. 성장성 (10%)
    revenue_growth = info.get('revenueGrowth', None)
    
    growth_score = 50  # 기본값
    if revenue_growth is not None:
        growth_pct = revenue_growth * 100
        if growth_pct >= 15:
            growth_score = 100
        elif growth_pct >= 0:
            growth_score = 50 + (growth_pct / 15) * 50
        elif growth_pct >= -5:
            growth_score = 50 + (growth_pct / 5) * 50
        else:
            growth_score = 0
    
    scores['growth'] = growth_score
    
    final_score = (
        scores['valuation'] * 0.40 +
        scores['profitability'] * 0.30 +
        scores['stability'] * 0.20 +
        scores['growth'] * 0.10
    )
    
    return round(final_score, 2), scores

def get_score_grade(score):
    if score >= 80:
        return "우수", "#4caf50"
    elif score >= 65:
        return "양호", "#8bc34a"
    elif score >= 50:
        return "보통", "#ff9800"
    elif score >= 35:
        return "주의", "#ff5722"
    else:
        return "위험", "#f44336"

# ===== 사이드바 =====
with st.sidebar:
    st.markdown("## 🔍 종목 검색")
    
    search_query = st.text_input(
        "종목명 또는 코드",
        placeholder="예: 삼성, 애플, AAPL",
        help="한글, 영문, 코드번호 모두 검색 가능"
    )
    
    if search_query:
        filtered_stocks = search_stocks(search_query)
        
        if filtered_stocks:
            selected = st.selectbox("검색 결과", filtered_stocks, key="search_result")
            
            # 종목명 추출
            display_name = selected.split(" (")[0]
            # ticker 찾기
            ticker = None
            for name, data in STOCK_DATABASE.items():
                if data['name_kr'] == display_name:
                    ticker = data['ticker']
                    stock_name_kr = data['name_kr']
                    break
        else:
            st.warning("검색 결과 없음")
            selected = None
            ticker = None
    else:
        st.markdown("#### 인기 종목")
        popular = ["삼성전자 (005930)", "SK하이닉스 (000660)", "애플 (AAPL)", "테슬라 (TSLA)", "엔비디아 (NVDA)"]
        selected = st.selectbox("선택", popular, key="popular")
        display_name = selected.split(" (")[0]
        for name, data in STOCK_DATABASE.items():
            if data['name_kr'] == display_name:
                ticker = data['ticker']
                stock_name_kr = data['name_kr']
                break
    
    analyze_btn = st.button("📊 분석 시작", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 📈 거시지표")
    with st.spinner("로딩..."):
        dff = fetch_fred_data('DFF')
        dexkous = fetch_fred_data('DEXKOUS')  # 원/달러
        us10y = fetch_fred_data('DGS10')
        
        if len(dff) > 0:
            st.metric("미국 기준금리", f"{dff['value'].iloc[0]:.2f}%")
        if len(dexkous) > 0:
            st.metric("원/달러 환율", f"₩{dexkous['value'].iloc[0]:.2f}")
        if len(us10y) > 0:
            st.metric("미국 10년물", f"{us10y['value'].iloc[0]:.2f}%")
    
    st.markdown("---")
    
    # 버핏 추천 섹션
    st.markdown("### 💎 버핏이 좋아할 종목")
    st.caption("저PBR + 우량 펀더멘털")
    
    for pick in BUFFETT_PICKS[:5]:  # 상위 5개만 표시
        if st.button(f"{pick['name']}", key=f"pick_{pick['ticker']}", use_container_width=True):
            # 여기서 ticker 설정하고 분석 트리거
            st.session_state['selected_ticker'] = pick['ticker']
            st.session_state['selected_name'] = pick['name']
            st.rerun()

# ===== 메인 =====
st.title("📊 Deep-Value Quant Guardrail")
st.markdown("**실시간 데이터 기반 이중 평가 시스템**")

# 세션 상태 확인
if 'selected_ticker' in st.session_state:
    ticker = st.session_state['selected_ticker']
    stock_name_kr = st.session_state['selected_name']
    analyze_btn = True
    del st.session_state['selected_ticker']
    del st.session_state['selected_name']

if analyze_btn and ticker:
    
    with st.spinner(f"**{stock_name_kr} ({ticker})** 분석 중..."):
        data = fetch_stock_data(ticker)
    
    if not data['success']:
        st.error(f"❌ 데이터 로딩 실패: {data['error']}")
    else:
        info = data['info']
        hist = data['history']
        balance_sheet = data['balance_sheet']
        
        current_price = info.get('currentPrice', hist['Close'].iloc[-1] if len(hist) > 0 else 0)
        market_cap = info.get('marketCap', 0)
        
        # ===== 헤더 =====
        st.markdown(f"## {stock_name_kr}")
        st.caption(f"{ticker} · 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # ===== KPI =====
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            prev_close = info.get('previousClose', current_price if current_price else 0)
            change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close and current_price else 0
            currency = "₩" if ticker.endswith('.KS') or ticker.endswith('.KQ') else "$"
            price_display = f"{currency}{current_price:,.0f}" if ticker.endswith(('.KS', '.KQ')) else f"{currency}{current_price:,.2f}"
            st.metric("현재가", price_display, f"{change_pct:+.2f}%")
        
        with col2:
            cap_display = f"${market_cap/1e9:.1f}B" if market_cap else "N/A"
            st.metric("시가총액", cap_display)
        
        with col3:
            pbr = info.get('priceToBook', None)
            pbr_display = f"{pbr:.2f}" if pbr else "데이터 없음"
            st.metric("PBR", pbr_display)
        
        with col4:
            per = info.get('trailingPE', None)
            per_display = f"{per:.2f}" if per else "데이터 없음"
            st.metric("PER", per_display)
        
        with col5:
            roe = info.get('returnOnEquity', None)
            roe_display = f"{roe*100:.1f}%" if roe else "데이터 없음"
            st.metric("ROE", roe_display)
        
        st.markdown("---")
        
        # ===== Guardrail Score =====
        final_score, component_scores = calculate_guardrail_score_v2(info)
        grade, grade_color = get_score_grade(final_score)
        
        st.markdown("### 🎯 Guardrail Score")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div class='score-card'>
                <div style='font-size:14px; color:#666; margin-bottom:8px'>종합 점수</div>
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
        
        # ===== 워렌 버핏 평가 =====
        st.markdown("### 💎 워렌 버핏 스타일 평가")
        
        buffett_eval = warren_buffett_evaluation(info, balance_sheet, market_cap, stock_name_kr)
        
        st.markdown(f"""
        <div class='buffett-card'>
            <div class='buffett-title'>
                💼 한국의 워렌 버핏이라면?
            </div>
            
            <div class='buffett-verdict' style='border-left-color:{buffett_eval['verdict_color']}'>
                {buffett_eval['verdict']}
            </div>
            
            <div style='background:rgba(255,255,255,0.7); padding:16px; border-radius:8px; margin:16px 0'>
                <strong>💡 워렌 버핏의 투자 철학</strong><br><br>
                
                워렌 버핏은 스승인 <strong>벤저민 그레이엄</strong>으로부터 가치투자를 배웠습니다. 
                그레이엄의 "<strong>담뱃재(Cigar Butt)</strong>" 투자 전략은 다음과 같습니다:<br><br>
                
                <em>"길거리에 버려진 담배꽁초처럼, 한두 모금 남아있다면 공짜로 주워 피울 가치가 있다"</em><br><br>
                
                이는 <strong>청산가치(NCAV: 유동자산 - 총부채)</strong>보다 시가총액이 낮은 기업을 매수하는 전략입니다.
                이론적으로 회사를 당장 청산해도 이익이 나는 구조이기 때문에 <strong>하방 리스크가 제한적</strong>입니다.<br><br>
                
                후에 버핏은 "<strong>위대한 기업을 합리적 가격에</strong>" 매수하는 방향으로 진화했지만,
                높은 ROE, 낮은 부채비율, 풍부한 현금흐름이라는 핵심 원칙은 변하지 않았습니다.
            </div>
            
            <div style='margin-top:16px; font-weight:600'>
                📊 평가 근거:
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
        <div class='buffett-disclaimer'>
            <strong style='font-size:16px'>⚠️ 중요한 면책사항</strong><br><br>
            
            이 평가는 <strong>주가가 오르지 않는다는 의미가 아닙니다.</strong><br>
            오히려 높은 리스크는 <strong>더 큰 가격 상승 가능성</strong>을 동반할 수 있습니다.<br><br>
            
            버핏 스타일에 부합하지 않는 종목도 성장주, 테마주로서 큰 수익을 낼 수 있습니다.<br>
            이 평가는 단지 "<strong>보수적 가치투자자의 관점</strong>"에서 본<br>
            안전마진과 펀더멘털 건전성을 보여줄 뿐입니다.
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ===== 차트 =====
        st.markdown("### 📈 주가 차트")
        
        if len(hist) > 0:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3]
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
                st.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.2f}%" if info.get('returnOnEquity') else "데이터 없음")
                st.metric("ROA", f"{info.get('returnOnAssets', 0)*100:.2f}%" if info.get('returnOnAssets') else "데이터 없음")
                st.metric("영업이익률", f"{info.get('profitMargins', 0)*100:.2f}%" if info.get('profitMargins') else "데이터 없음")
            
            with col2:
                st.markdown("#### 안정성 지표")
                st.metric("부채비율", f"{info.get('debtToEquity', 0):.1f}%" if info.get('debtToEquity') else "데이터 없음")
                st.metric("유동비율", f"{info.get('currentRatio', 0):.2f}" if info.get('currentRatio') else "데이터 없음")
                st.metric("당좌비율", f"{info.get('quickRatio', 0):.2f}" if info.get('quickRatio') else "데이터 없음")
        
        with tab2:
            st.markdown("#### Guardrail Score 종합 평가")
            
            if final_score >= 80:
                st.markdown(f"""
                <div class='success-box'>
                <strong>✅ 우수한 투자 대상</strong><br>
                {stock_name_kr}은(는) Guardrail Score {final_score:.2f}점으로 <strong>{grade}</strong> 등급을 받았습니다.
                밸류에이션, 수익성, 안정성 모든 면에서 우수한 평가를 받았습니다.
                </div>
                """, unsafe_allow_html=True)
            
            elif final_score >= 50:
                st.markdown(f"""
                <div class='insight-box'>
                <strong>ℹ️ 중간 수준 투자 대상</strong><br>
                {stock_name_kr}은(는) Guardrail Score {final_score:.2f}점으로 <strong>{grade}</strong> 등급입니다.
                일부 지표에서 개선이 필요하나, 투자 검토 가능한 수준입니다.
                </div>
                """, unsafe_allow_html=True)
            
            else:
                st.markdown(f"""
                <div class='warning-box'>
                <strong>⚠️ 주의 필요</strong><br>
                {stock_name_kr}은(는) Guardrail Score {final_score:.2f}점으로 <strong>{grade}</strong> 등급입니다.
                투자 전 심층 분석이 권장됩니다.
                </div>
                """, unsafe_allow_html=True)
            
            if component_scores['valuation'] >= 70:
                st.success(f"✅ 밸류에이션: 현재 PBR {pbr:.2f}배로 저평가 구간입니다." if pbr else "✅ 밸류에이션: 저평가 구간입니다.")
            
            if component_scores['profitability'] >= 70:
                st.success(f"✅ 수익성: ROE {roe*100:.1f}%로 우수한 수익성을 보입니다." if roe else "✅ 수익성: 우수합니다.")
            
            if component_scores['stability'] < 50:
                debt = info.get('debtToEquity', 0)
                st.warning(f"⚠️ 안정성: 부채비율 {debt:.1f}%로 재무 안정성 점검이 필요합니다." if debt else "⚠️ 안정성: 점검이 필요합니다.")
        
        with tab3:
            st.markdown("#### 전체 재무 데이터")
            st.json(info, expanded=False)

else:
    st.info("👈 왼쪽에서 종목을 검색하고 '분석 시작'을 눌러주세요")
    
    # 버핏 추천 주식 메인 화면 표시
    st.markdown("### 💎 워렌 버핏이 좋아할 종목 TOP 10")
    st.markdown("저PBR + 우량 펀더멘털 기준")
    
    for i, pick in enumerate(BUFFETT_PICKS):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div class='pick-card'>
                <strong style='font-size:16px'>{i+1}. {pick['name']}</strong><br>
                <span style='color:#666; font-size:14px'>{pick['reason']}</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("분석", key=f"analyze_{pick['ticker']}", use_container_width=True):
                st.session_state['selected_ticker'] = pick['ticker']
                st.session_state['selected_name'] = pick['name']
                st.rerun()
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔍 스마트 검색**
        - 한글 초성 검색
        - 종목코드 검색
        - 영문/한글명 검색
        """)
    
    with col2:
        st.markdown("""
        **📊 이중 평가**
        - Guardrail Score (연속형)
        - 워렌 버핏 스타일 평가
        - 실시간 데이터
        """)
    
    with col3:
        st.markdown("""
        **🌍 전세계 주식**
        - 코스피/코스닥
        - 미국 주요 종목
        - 실시간 업데이트
        """)
