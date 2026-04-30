# Deep-Value Quant Guardrail Dashboard

Skills.md 기반 실시간 투자 분석 대시보드

## 배포 방법 (Streamlit Cloud)

### 1. GitHub 저장소 생성

1. github.com 로그인
2. New repository 클릭
3. 이름: `guardrail-dashboard`
4. Public 선택
5. Create repository

### 2. 파일 업로드

다음 파일들을 저장소에 업로드:
- `app.py`
- `requirements.txt`
- `Skills.md`

### 3. Streamlit Cloud 배포

1. share.streamlit.io 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. Repository: `guardrail-dashboard` 선택
5. Main file path: `app.py` 입력
6. Deploy 클릭

### 4. 배포 완료

약 2-3분 후 자동으로 URL 생성됨:
```
https://[계정명]-guardrail-dashboard-[랜덤].streamlit.app
```

이 URL이 제출할 배포 링크입니다.

## 기능

- ✅ 실시간 주가 데이터 (Yahoo Finance)
- ✅ 실시간 거시지표 (FRED API)
- ✅ NCAV 자동 계산
- ✅ Guardrail Score 산출
- ✅ 전세계 주식 지원 (한국/미국/일본)
- ✅ 검색 자동완성
- ✅ 인터랙티브 차트
- ✅ Skills.md 규칙 완벽 구현

## 기술 스택

- Python 3.9+
- Streamlit
- YFinance (주가 데이터)
- FRED API (거시지표)
- Plotly (차트)
- Pandas, Scipy (데이터 분석)
