# Excel 분석 도구

Streamlit 기반 Excel 자동 분석 웹 앱

## 기능
- Excel 파일 업로드
- 자동 데이터 분석
- 결과 다운로드
```

### 4단계: Streamlit Cloud 배포

**Streamlit Cloud 가입:**
1. https://share.streamlit.io 접속
2. `Sign up` 클릭
3. **GitHub 계정으로 로그인** (연동됨)
4. 권한 승인

**앱 배포:**
1. 로그인 후 `New app` 클릭
2. 설정:
   - Repository: `your-username/excel-analyzer` 선택
   - Branch: `main`
   - Main file path: `app.py`
3. `Deploy!` 클릭

**5~10분 후 완료!** 🎉

자동으로 URL 생성: `https://your-username-excel-analyzer.streamlit.app`

### 5단계: URL 공유

이제 누구나 이 링크로 접속 가능합니다!
- 포트폴리오에 추가
- 크몽 프로필에 링크
- 클라이언트에게 데모 보여주기

## 코드 수정 시 자동 업데이트

**로컬에서 수정:**
1. VSCode에서 코드 수정
2. GitHub에 새 파일 업로드 (덮어쓰기)
3. Streamlit Cloud가 **자동으로 재배포!**

## GitHub Desktop 사용 (더 편리)

**설치:**
1. https://desktop.github.com 다운로드
2. GitHub 계정 로그인
3. 저장소 Clone

**작업 흐름:**
```
VSCode에서 코드 수정
↓
GitHub Desktop에서 Commit
↓
Push origin
↓
Streamlit Cloud 자동 업데이트
```

## 빠른 시작 체크리스트
```
□ GitHub 계정 생성
□ 새 Repository 생성 (Public)
□ app.py 업로드
□ requirements.txt 업로드
□ Streamlit Cloud 가입 (GitHub 연동)
□ New app → Deploy
□ URL 확인 및 테스트
