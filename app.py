import streamlit as st
import zipfile
import io
from datetime import datetime

st.set_page_config(page_title="컴퓨터 정리의 기본", layout="wide", page_icon="📁")

st.title("📁 컴퓨터 정리의 기본")

tab1, tab2 = st.tabs(["📂 모든 파일 한 곳에 모으기", "✏️ 파일명 일괄 수정"])

# ==================== 기능 1: 파일 모으기 ====================
with tab1:
    st.header("📂 폴더 내 모든 파일을 한 폴더에 놓기")
    st.markdown("ZIP 파일을 업로드하면 모든 파일을 한 곳에 모아서 다시 압축해드립니다.")
    
    uploaded_zip = st.file_uploader("📁 ZIP 파일 업로드", type="zip", key="upload1")
    
    if uploaded_zip and st.button("🚀 파일 모으기 시작", key="collect_btn", use_container_width=True):
        try:
            with st.spinner("파일을 수집하는 중..."):
                # 업로드된 ZIP 파일 읽기
                input_zip = zipfile.ZipFile(uploaded_zip)
                
                # 모든 파일 추출
                all_files = input_zip.namelist()
                
                if not all_files:
                    st.warning("⚠️ ZIP 파일에 파일이 없습니다")
                else:
                    # 결과 ZIP 생성
                    output_zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(output_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as output_zip:
                        file_counter = {}
                        
                        for file_name in all_files:
                            if file_name.endswith('/'):  # 폴더 스킵
                                continue
                            
                            # 파일명만 추출
                            base_file_name = file_name.split('/')[-1]
                            
                            # 중복 처리
                            if base_file_name in file_counter:
                                file_counter[base_file_name] += 1
                                name, ext = base_file_name.rsplit('.', 1)
                                final_name = f"{name}_{file_counter[base_file_name]}.{ext}"
                            else:
                                file_counter[base_file_name] = 0
                                final_name = base_file_name
                            
                            # 파일 읽기 및 새 ZIP에 추가
                            file_content = input_zip.read(file_name)
                            output_zip.writestr(final_name, file_content)
                    
                    output_zip_buffer.seek(0)
                    
                    st.success(f"✅ 총 {len(all_files)}개 파일 수집 완료!")
                    
                    st.download_button(
                        label="📥 압축 파일 다운로드",
                        data=output_zip_buffer.getvalue(),
                        file_name=f"모든파일_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                    
                    with st.expander("📋 수집된 파일 목록 보기"):
                        for i, file_name in enumerate(all_files[:100], 1):
                            st.text(f"{i}. {file_name.split('/')[-1]}")
                        if len(all_files) > 100:
                            st.text(f"... 외 {len(all_files) - 100}개")
        
        except Exception as e:
            st.error(f"❌ 오류 발생: {str(e)}")