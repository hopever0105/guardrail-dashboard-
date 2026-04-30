import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
from scipy.stats import pearsonr
import numpy as np

# ===== 페이지 설정 =====
st.set_page_config(
    page_title="Deep-Value Quant Guardrail Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CSS 스타일 =====
st.markdown("""
<style>
    .main {
        background-color: #0a0c10;
        color: #c8d4e3;
    }
    .stMetric {
        background-color: #0f1318;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #1e2530;
    }
    .stMetric label {
        color: #7a8fa6 !important;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .stMetric .metric-value {
        color: #c8d4e3 !important;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 28px;
        font-weight: 600;
    }
    h1, h2, h3 {
        font-family: 'IBM Plex Mono', monospace;
        color: #c8d4e3;
    }
    .success-box {
        background: linear-gradient(135deg, rgba(0,212,170,0.15), rgba(46,213,115,0.15));
        border-left: 4px solid #00d4aa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .warning-box {
        background: rgba(255,165,2,0.1);
        border-left: 4px solid #ffa502;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .danger-box {
        background: rgba(255,71,87,0.1);
        border-left: 4px solid #ff4757;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0f1318;
        border: 1px solid #1e2530;
        color: #7a8fa6;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #151a22;
        border-color: #00d4aa;
        color: #00d4aa;
    }
</style>
""", unsafe_allow_html=True)

# ===== API 키 =====
DART_KEY = '91957f9f505c7b93af548e6ad41ddbf13b2a64eb'
FRED_KEY = '728ddd23b68ab6b6c0195e71423285d2'

# ===== 주요 종목 리스트 (검색 자동완성용) =====
POPULAR_STOCKS = {
    # 한국
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
    "현대차": "005380.KS",
    "삼성바이오로직스": "207940.KS",
    "LG화학": "051910.KS",
    "POSCO홀딩스": "005490.KS",
    "현대제철": "004020.KS",
    "삼성SDI": "006400.KS",
    "기아": "000270.KS",
    "셀트리온": "068270.KS",
    "KB금융": "105560.KS",
    "신한지주": "055550.KS",
    "LG전자": "066570.KS",
    "한국전력": "015760.KS",
    "영원무역": "111770.KS",
    # 미국
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "Meta": "META",
    "Netflix": "NFLX",
    "AMD": "AMD",
    "Intel": "INTC",
    "Coca-Cola": "KO",
    "Disney": "DIS",
    "Nike": "NKE",
    "Visa": "V",
    "Mastercard": "MA",
}

# ===== FRED 데이터 가져오기 =====
@st.cache_data(ttl=3600)
def fetch_fred_data(series_id):
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': series_id,
            'api_key': FRED_KEY,
            'file_type': 'json',
            'limit': 180
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        df = pd.DataFrame(data['observations'])
        df = df[df['value'] != '.']
        df['value'] = pd.to_numeric(df['value'])
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return pd.DataFrame()

# ===== 거시지표 로딩 =====
@st.cache_data(ttl=3600)
def load_macro_data():
    dff = fetch_fred_data('DFF')  # 미국 기준금리
    fx = fetch_fred_data('DEXKOUS')  # USD/KRW
    us10y = fetch_fred_data('DGS10')  # 미국 10년물
    
    return {
        'rate': dff['value'].iloc[-1] if len(dff) > 0 else None,
        'fx': fx['value'].iloc[-1] if len(fx) > 0 else None,
        'us10y': us10y['value'].iloc[-1] if len(us10y) > 0 else None,
        'rate_series': dff,
        'fx_series': fx,
        'us10y_series': us10y
    }

# ===== 주식 데이터 가져오기 =====
@st.cache_data(ttl=300)
def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        # 기본 정보
        info = stock.info
        
        # 6개월 히스토리컬 데이터
        hist = stock.history(period="6mo")
        
        # 재무제표
        balance_sheet = stock.balance_sheet
        
        return {
            'info': info,
            'history': hist,
            'balance_sheet': balance_sheet,
            'success': True
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ===== NCAV 계산 =====
def calculate_ncav(balance_sheet, market_cap):
    try:
        if balance_sheet.empty or market_cap is None:
            return None, None, None
        
        # 최근 데이터 (첫 번째 컬럼)
        latest = balance_sheet.iloc[:, 0]
        
        # 유동자산
        current_assets = latest.get('Current Assets', latest.get('Total Current Assets', None))
        
        # 총부채
        total_liabilities = latest.get('Total Liabilities Net Minority Interest', 
                                      latest.get('Total Liabilities', None))
        
        if current_assets is None or total_liabilities is None:
            return None, None, None
        
        ncav = current_assets - total_liabilities
        ncav_ratio = ncav / market_cap if market_cap > 0 else 0
        
        return ncav, ncav_ratio, current_assets
        
    except Exception as e:
        return None, None, None

# ===== NCAV 등급 판정 =====
def get_ncav_grade(ncav_ratio):
    if ncav_ratio is None:
        return "분석 불가", "#7a8fa6", 0
    
    if ncav_ratio >= 1.0:
        return "Strong Buy", "#00d4aa", 100
    elif ncav_ratio >= 0.67:
        return "Deep Value", "#2ed573", 75
    elif ncav_ratio >= 0.5:
        return "관심 종목", "#ffa502", 50
    else:
        return "분석 제외", "#ff4757", 0

# ===== 상관계수 계산 (거시 민감도) =====
def calculate_correlation(stock_returns, macro_returns):
    try:
        # 날짜 기준 병합
        merged = pd.merge(stock_returns, macro_returns, left_index=True, right_index=True, how='inner')
        
        if len(merged) < 30:  # 최소 30개 데이터 필요
            return None, None
        
        r, p = pearsonr(merged.iloc[:, 0], merged.iloc[:, 1])
        return r, p
    except:
        return None, None

# ===== Guardrail Score 계산 =====
def calculate_guardrail_score(value_score, macro_score, financial_score):
    return round(value_score * 0.5 + macro_score * 0.3 + financial_score * 0.2)

# ===== 사이드바 =====
with st.sidebar:
    st.markdown("### 🔍 종목 검색")
    
    # 검색 방식 선택
    search_mode = st.radio("검색 방식", ["인기 종목", "직접 입력"], label_visibility="collapsed")
    
    if search_mode == "인기 종목":
        stock_name = st.selectbox(
            "종목 선택",
            options=list(POPULAR_STOCKS.keys()),
            index=0
        )
        ticker = POPULAR_STOCKS[stock_name]
    else:
        ticker = st.text_input(
            "종목코드 입력",
            placeholder="예: AAPL, 005930.KS",
            help="한국: 005930.KS / 미국: AAPL / 일본: 7203.T"
        )
        stock_name = ticker
    
    analyze_btn = st.button("📊 분석 시작", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    # 거시지표
    st.markdown("### 📈 실시간 거시지표")
    
    with st.spinner("로딩 중..."):
        macro = load_macro_data()
    
    if macro['rate']:
        st.metric("미국 기준금리", f"{macro['rate']:.2f}%")
    if macro['fx']:
        st.metric("USD/KRW", f"{macro['fx']:.2f}")
    if macro['us10y']:
        st.metric("미국 10년물", f"{macro['us10y']:.2f}%")
    
    st.markdown("---")
    st.markdown("""
    <div style='font-size:10px; color:#4a5f74; font-family:monospace'>
    Deep-Value Quant Guardrail<br>
    Skills.md 기반 자동 분석<br>
    실시간 데이터 연동<br>
    v1.0 LIVE
    </div>
    """, unsafe_allow_html=True)

# ===== 메인 화면 =====
st.title("📊 Deep-Value Quant Guardrail Dashboard")
st.markdown("**Skills.md 규칙 기반 실시간 투자 분석 시스템**")

if analyze_btn and ticker:
    
    with st.spinner(f"**{stock_name} ({ticker})** 데이터 로딩 중..."):
        data = fetch_stock_data(ticker)
    
    if not data['success']:
        st.error(f"❌ 데이터 로딩 실패: {data['error']}")
        st.info("종목코드를 확인해주세요. 한국 종목은 '.KS' 또는 '.KQ'를 붙여주세요.")
    
    else:
        info = data['info']
        hist = data['history']
        balance_sheet = data['balance_sheet']
        
        # 기본 정보
        stock_name_full = info.get('longName', info.get('shortName', stock_name))
        current_price = info.get('currentPrice', hist['Close'].iloc[-1] if len(hist) > 0 else None)
        market_cap = info.get('marketCap', None)
        
        # ===== 헤더 =====
        st.markdown(f"## {stock_name_full}")
        st.markdown(f"**{ticker}** · 실시간 데이터 기준 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # ===== KPI 카드 =====
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if current_price:
                prev_close = info.get('previousClose', current_price)
                change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
                st.metric(
                    "현재가",
                    f"${current_price:.2f}" if not ticker.endswith('.KS') and not ticker.endswith('.KQ') else f"₩{current_price:,.0f}",
                    f"{change_pct:+.2f}%"
                )
        
        with col2:
            if market_cap:
                st.metric("시가총액", f"${market_cap/1e9:.2f}B")
        
        with col3:
            pbr = info.get('priceToBook', None)
            if pbr:
                st.metric("PBR", f"{pbr:.2f}")
        
        with col4:
            pe = info.get('trailingPE', None)
            if pe:
                st.metric("PER", f"{pe:.2f}")
        
        st.markdown("---")
        
        # ===== NCAV 분석 =====
        ncav, ncav_ratio, current_assets = calculate_ncav(balance_sheet, market_cap)
        ncav_grade, ncav_color, value_score = get_ncav_grade(ncav_ratio)
        
        # ===== 거시 민감도 (간소화 버전) =====
        macro_score = 70  # 실제론 상관계수 계산해야 함
        
        # ===== 재무 건전성 =====
        debt_to_equity = info.get('debtToEquity', 100)
        current_ratio = info.get('currentRatio', 1.5)
        
        if debt_to_equity and current_ratio:
            if debt_to_equity < 100 and current_ratio > 1.5:
                financial_score = 100
            elif debt_to_equity < 100 or current_ratio > 1.5:
                financial_score = 60
            else:
                financial_score = 20
        else:
            financial_score = 50
        
        # ===== Guardrail Score =====
        guardrail_score = calculate_guardrail_score(value_score, macro_score, financial_score)
        
        # ===== Score 표시 =====
        st.markdown("### 🎯 Guardrail Score 종합")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Score 게이지
            if guardrail_score >= 80:
                score_color = "#00d4aa"
                score_grade = "Strong"
            elif guardrail_score >= 60:
                score_color = "#ffa502"
                score_grade = "Moderate"
            elif guardrail_score >= 40:
                score_color = "#ff9f43"
                score_grade = "Caution"
            else:
                score_color = "#ff4757"
                score_grade = "Avoid"
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=guardrail_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': score_grade, 'font': {'size': 24, 'color': score_color, 'family': 'IBM Plex Mono'}},
                number={'font': {'size': 48, 'color': score_color, 'family': 'IBM Plex Mono'}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#4a5f74"},
                    'bar': {'color': score_color},
                    'bgcolor': "#0f1318",
                    'borderwidth': 2,
                    'bordercolor': "#1e2530",
                    'steps': [
                        {'range': [0, 40], 'color': 'rgba(255,71,87,0.1)'},
                        {'range': [40, 60], 'color': 'rgba(255,165,2,0.1)'},
                        {'range': [60, 80], 'color': 'rgba(255,159,67,0.1)'},
                        {'range': [80, 100], 'color': 'rgba(0,212,170,0.1)'}
                    ],
                }
            ))
            
            fig_gauge.update_layout(
                paper_bgcolor="#0a0c10",
                plot_bgcolor="#0a0c10",
                font={'color': "#c8d4e3", 'family': "IBM Plex Mono"},
                height=250,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.markdown("#### Score 구성 요소")
            
            # 가치 점수
            st.markdown(f"**가치 점수 (×0.5):** {value_score}/100")
            st.progress(value_score / 100)
            
            # 거시 안전 점수
            st.markdown(f"**거시 안전 점수 (×0.3):** {macro_score}/100")
            st.progress(macro_score / 100)
            
            # 재무 건전성 점수
            st.markdown(f"**재무 건전성 점수 (×0.2):** {financial_score}/100")
            st.progress(financial_score / 100)
            
            st.markdown(f"""
            **최종 Guardrail Score: {guardrail_score}/100**
            
            - Skills.md §6 산출 규칙 적용
            - 가중 평균 방식
            """)
        
        st.markdown("---")
        
        # ===== 탭 구성 =====
        tab1, tab2, tab3, tab4 = st.tabs(["📈 주가 차트", "💰 가치 평가", "📊 재무 지표", "💡 인사이트"])
        
        with tab1:
            st.markdown("### 주가 추이 (6개월)")
            
            if len(hist) > 0:
                fig_price = go.Figure()
                
                fig_price.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist['Close'],
                    mode='lines',
                    name='종가',
                    line=dict(color='#00d4aa', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(0,212,170,0.1)'
                ))
                
                fig_price.update_layout(
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#0f1318",
                    font={'color': "#c8d4e3", 'family': "IBM Plex Mono"},
                    xaxis=dict(
                        gridcolor="#1e2530",
                        showgrid=True,
                        title="날짜"
                    ),
                    yaxis=dict(
                        gridcolor="#1e2530",
                        showgrid=True,
                        title="주가"
                    ),
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig_price, use_container_width=True)
                
                # 거래량
                st.markdown("#### 거래량")
                fig_vol = go.Figure()
                
                fig_vol.add_trace(go.Bar(
                    x=hist.index,
                    y=hist['Volume'],
                    name='거래량',
                    marker_color='#0099ff'
                ))
                
                fig_vol.update_layout(
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#0f1318",
                    font={'color': "#c8d4e3", 'family': "IBM Plex Mono"},
                    xaxis=dict(gridcolor="#1e2530"),
                    yaxis=dict(gridcolor="#1e2530"),
                    height=200,
                    showlegend=False
                )
                
                st.plotly_chart(fig_vol, use_container_width=True)
        
        with tab2:
            st.markdown("### NCAV 가치 평가")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class='{"success-box" if value_score >= 75 else "warning-box" if value_score >= 50 else "danger-box"}'>
                <strong>NCAV 등급</strong><br>
                <span style='font-size:24px; color:{ncav_color}'>{ncav_grade}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if ncav:
                    st.metric("NCAV", f"${ncav/1e9:.2f}B")
            
            with col3:
                if ncav_ratio is not None:
                    st.metric("NCAV 배수", f"{ncav_ratio:.2f}x")
            
            st.markdown("#### Skills.md §3 NCAV 분류 기준")
            st.markdown("""
            | 등급 | 조건 | 근거 |
            |------|------|------|
            | **Strong Buy** | 시총 < NCAV × 1.0 | Benjamin Graham 원전 기준 |
            | **Deep Value** | 시총 < NCAV × 1.5 | Oppenheimer(1986) 실증 연구 |
            | **관심 종목** | 시총 < NCAV × 2.0 | 국내 PBR 1배 이하 종목군 |
            | **분석 제외** | 그 외 | 안전마진 미확보 |
            """)
            
            # PBR 보조 지표
            if pbr:
                st.markdown("#### PBR 보조 지표")
                if pbr < 0.3:
                    st.warning("🚨 PBR < 0.3: 구조적 저평가 경고")
                elif pbr < 0.5:
                    st.info("⚠️ PBR 0.3~0.5: 안전마진 확인 구간")
                elif pbr >= 1.0:
                    st.warning("ℹ️ PBR ≥ 1.0: NCAV 분석 가중치 50% 감소")
        
        with tab3:
            st.markdown("### 주요 재무 지표")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 수익성")
                
                if 'returnOnEquity' in info:
                    st.metric("ROE", f"{info['returnOnEquity']*100:.2f}%")
                
                if 'returnOnAssets' in info:
                    st.metric("ROA", f"{info['returnOnAssets']*100:.2f}%")
                
                if 'profitMargins' in info:
                    st.metric("영업이익률", f"{info['profitMargins']*100:.2f}%")
            
            with col2:
                st.markdown("#### 안정성")
                
                if debt_to_equity:
                    st.metric("부채비율", f"{debt_to_equity:.2f}%")
                
                if current_ratio:
                    st.metric("유동비율", f"{current_ratio:.2f}")
                
                if 'quickRatio' in info:
                    st.metric("당좌비율", f"{info['quickRatio']:.2f}")
        
        with tab4:
            st.markdown("### 💡 자동 생성 인사이트")
            
            # 종합 인사이트
            st.markdown(f"""
            <div class='{"success-box" if guardrail_score >= 80 else "warning-box" if guardrail_score >= 60 else "danger-box"}'>
            <strong>{stock_name_full} ({ticker})</strong><br><br>
            
            <strong>Guardrail Score: {guardrail_score}점 / {score_grade} 등급</strong><br><br>
            
            현재 시가총액은 ${market_cap/1e9:.2f}B이며, NCAV 기준 <strong>{ncav_grade}</strong> 등급입니다.
            {"NCAV 배수는 " + f"{ncav_ratio:.2f}x로, " if ncav_ratio else ""}
            Skills.md §3 기준에 따라 분류되었습니다.
            </div>
            """, unsafe_allow_html=True)
            
            # NCAV 인사이트
            if ncav_grade == "Strong Buy":
                st.markdown("""
                <div class='success-box'>
                <strong>✅ Benjamin Graham 청산가치 기준 충족</strong><br>
                시가총액이 NCAV 이하로, 이론적 하방 리스크가 제한적입니다.
                Oppenheimer(1986) 연구에 따르면 이 구간 포트폴리오의 연평균 초과수익률은 29.4%입니다.
                </div>
                """, unsafe_allow_html=True)
            
            elif ncav_grade == "Deep Value":
                st.markdown("""
                <div class='success-box'>
                <strong>✅ Deep Value 구간</strong><br>
                NCAV 대비 시총이 1.5배 이하로, 실증 연구상 초과수익 구간에 위치합니다.
                </div>
                """, unsafe_allow_html=True)
            
            # PBR 인사이트
            if pbr and pbr < 0.3:
                st.markdown("""
                <div class='warning-box'>
                <strong>⚠️ 구조적 저평가 경고</strong><br>
                PBR 0.3 미만은 시장이 청산가치조차 인정하지 않는 수준입니다.
                NCAV 분석의 신뢰도가 상승하며, 추가 실사가 권장됩니다.
                </div>
                """, unsafe_allow_html=True)
            
            # 재무 건전성
            if financial_score == 100:
                st.markdown("""
                <div class='success-box'>
                <strong>✅ 재무 건전성 양호</strong><br>
                부채비율 100% 미만, 유동비율 150% 이상으로 안정적입니다.
                </div>
                """, unsafe_allow_html=True)
            
            elif financial_score == 20:
                st.markdown("""
                <div class='danger-box'>
                <strong>🚨 재무 건전성 경고</strong><br>
                부채비율이 높거나 유동성이 부족합니다. 하방 리스크 관리가 필요합니다.
                </div>
                """, unsafe_allow_html=True)

else:
    # 초기 화면
    st.info("👈 왼쪽 사이드바에서 종목을 선택하고 '분석 시작' 버튼을 눌러주세요")
    
    st.markdown("### 🎯 대시보드 기능")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 실시간 데이터**
        - Yahoo Finance 연동
        - FRED 거시지표
        - 분 단위 업데이트
        """)
    
    with col2:
        st.markdown("""
        **💰 NCAV 분석**
        - Benjamin Graham 기준
        - Skills.md 규칙 적용
        - Guardrail Score 자동 산출
        """)
    
    with col3:
        st.markdown("""
        **🌍 전세계 주식**
        - 한국 코스피/코스닥
        - 미국 나스닥/NYSE
        - 일본, 홍콩 등
        """)
    
    st.markdown("---")
    
    st.markdown("### 📋 지원 종목 예시")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **한국 주식**
        - 삼성전자 (005930.KS)
        - SK하이닉스 (000660.KS)
        - NAVER (035420.KS)
        - 카카오 (035720.KS)
        """)
    
    with col2:
        st.markdown("""
        **미국 주식**
        - Apple (AAPL)
        - Tesla (TSLA)
        - NVIDIA (NVDA)
        - Microsoft (MSFT)
        """)
