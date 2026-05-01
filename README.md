# 💎 Deep-Value Quant Guardrail Dashboard

**워렌 버핏 스타일 가치투자 + 연속형 정량 평가 통합 시스템**

고려대학교 통계학과 송호빈 | 2025 해커톤 출품작

---

## 🎯 프로젝트 개요

본 대시보드는 **Skills.md에 명문화된 투자 분석 규칙**을 기반으로, 
전세계 주식을 실시간 데이터로 평가하는 범용 금융 분석 시스템입니다.

### 핵심 특징

1. **이중 평가 시스템**
   - **Guardrail Score**: PBR·PER·ROE·성장률 기반 연속형 정량 모델 (0.00~100.00)
   - **워렌 버핏 스타일 평가**: NCAV·부채비율·현금흐름 기반 가치투자 철학 구현

2. **Skills.md 기반 자동 생성**
   - 분석 규칙을 문서로 명문화
   - 데이터 구조가 바뀌어도 동일한 규칙 적용
   - AI 바이브 코딩을 통한 수동 구현 최소화

3. **실시간 데이터 연동**
   - Yahoo Finance API (전세계 주식 주가)
   - FRED API (거시경제 지표)
   - 분 단위 자동 업데이트

4. **스마트 검색**
   - 한글 초성 검색 지원
   - 종목코드 직접 입력
   - 코스피/코스닥/미국 주요 종목 60개 이상

---

## 🛠️ 기술 스택

- **Language**: Python 3.9+
- **Framework**: Streamlit
- **Data Sources**: Yahoo Finance, FRED API
- **Libraries**: yfinance, pandas, plotly, requests, numpy
- **Deployment**: Streamlit Cloud

---

## 🚀 배포 URL

실시간 대시보드를 체험해보세요!

---

## 📊 주요 기능

### 1. Guardrail Score (연속형 정량 모델)

각 지표를 0.00~100.00 범위로 정밀 평가:
- 밸류에이션 (40%): PBR, PER
- 수익성 (30%): ROE, 영업이익률
- 안정성 (20%): 부채비율, 유동비율
- 성장성 (10%): 매출/이익 성장률

### 2. 워렌 버핏 스타일 평가

"한국의 워렌 버핏이라면 이 주식에 투자했을까?"
- NCAV (담뱃재 전략)
- 높은 ROE & 낮은 부채
- 풍부한 현금흐름

---

**Made with ❤️ using Streamlit & Skills.md**
