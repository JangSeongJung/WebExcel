# advanced_app.py - 오류 수정 버전
import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Excel 분석 프로", layout="wide")

# 사이드바 - 옵션 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    analysis_type = st.selectbox(
        "분석 유형",
        ["기본 분석", "매출 분석", "재고 분석", "고객 분석"]
    )
    
    remove_duplicates = st.checkbox("중복 제거", value=True)
    fill_na = st.checkbox("빈 값 채우기", value=False)
    
    st.markdown("---")
    st.info("💡 팁: 파일은 서버에 저장되지 않습니다")

# 메인 영역
st.title("🚀 Excel 분석 전문 도구")

uploaded_file = st.file_uploader(
    "Excel 파일 업로드", 
    type=['xlsx', 'xls'],
    help="최대 200MB까지 업로드 가능"
)

if uploaded_file:
    try:
        # 로딩 표시
        with st.spinner('데이터를 분석 중입니다...'):
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ {len(df):,}개 행 로드 완료!")
        
        # 데이터 전처리
        if remove_duplicates:
            before = len(df)
            df = df.drop_duplicates()
            if before > len(df):
                st.info(f"🔄 중복 제거: {before - len(df)}개 행 제거됨")
        
        if fill_na:
            df = df.fillna(0)
            st.info("🔄 빈 값을 0으로 채움")
        
        # 컬럼 선택
        st.subheader("📊 분석할 컬럼 선택")
        cols = st.multiselect(
            "컬럼을 선택하세요 (여러 개 가능)",
            df.columns.tolist(),
            default=df.columns.tolist()[:min(3, len(df.columns))]
        )
        
        if cols:
            # 선택된 컬럼만 표시
            df_filtered = df[cols]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("데이터 미리보기")
                st.dataframe(df_filtered.head(10), use_container_width=True)
            
            with col2:
                st.subheader("기본 통계")
                st.dataframe(df_filtered.describe(), use_container_width=True)
            
            # 분석 유형에 따른 처리
            if analysis_type == "매출 분석":
                st.subheader("💰 매출 분석")
                numeric_cols = df_filtered.select_dtypes(include=['number']).columns
                
                if len(numeric_cols) > 0:
                    for col in numeric_cols:
                        total = df_filtered[col].sum()
                        avg = df_filtered[col].mean()
                        st.metric(
                            label=f"{col} 합계",
                            value=f"{total:,.0f}",
                            delta=f"평균: {avg:,.0f}"
                        )
            
            # 그룹별 집계
            st.subheader("📈 그룹별 집계")
            if len(df_filtered.columns) >= 2:
                numeric_cols = df_filtered.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    group_col = st.selectbox("그룹화할 컬럼", df_filtered.columns)
                    agg_col = st.selectbox("집계할 컬럼", numeric_cols)
                    
                    if group_col and agg_col:
                        grouped = df_filtered.groupby(group_col)[agg_col].sum().sort_values(ascending=False)
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.bar_chart(grouped)
                        with col2:
                            st.dataframe(grouped)
            
            # 결과 다운로드
            st.subheader("💾 결과 다운로드")
            
            # 새로운 BytesIO 객체 생성 (완전히 새 파일)
            output = io.BytesIO()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 엑셀 작성 - mode 지정 없이 새 파일로
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # 처리된 데이터
                df_filtered.to_excel(writer, sheet_name='처리된데이터', index=False)
                
                # 통계
                df_filtered.describe().to_excel(writer, sheet_name='통계정보')
                
                # 그룹 요약 (조건부)
                if len(df_filtered.columns) >= 2:
                    numeric_cols = df_filtered.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0 and group_col and agg_col:
                        try:
                            grouped.to_excel(writer, sheet_name='그룹요약')
                        except:
                            pass
            
            # BytesIO 포인터를 처음으로
            output.seek(0)
            
            st.download_button(
                label="📥 Excel 다운로드",
                data=output.getvalue(),
                file_name=f"분석결과_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")
        st.info("파일 형식을 확인해주세요")

else:
    # 안내 메시지
    st.info("👈 왼쪽 사이드바에서 파일을 업로드해주세요")
    
    # 사용 방법 안내
    with st.expander("📖 사용 방법"):
        st.markdown("""
        1. **파일 업로드**: Excel 파일 (.xlsx, .xls) 선택
        2. **옵션 설정**: 사이드바에서 분석 옵션 선택
        3. **컬럼 선택**: 분석할 컬럼 선택
        4. **결과 확인**: 자동으로 분석된 결과 확인
        5. **다운로드**: 처리된 Excel 파일 다운로드
        """)
    
    # 데모 데이터
    if st.button("🎯 샘플 데이터로 테스트"):
        demo_df = pd.DataFrame({
            '날짜': pd.date_range('2024-01-01', periods=20),
            '제품': ['노트북', '마우스', '키보드', '모니터'] * 5,
            '매출': [1500000, 35000, 89000, 450000] * 5,
            '수량': [3, 10, 5, 2] * 5
        })
        st.dataframe(demo_df, use_container_width=True)