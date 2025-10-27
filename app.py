import streamlit as st
import os
import shutil
import zipfile
from pathlib import Path
import io
from datetime import datetime

st.set_page_config(page_title="컴퓨터 정리의 기본", layout="wide", page_icon="📁")

# 메인 타이틀
st.title("📁 컴퓨터 정리의 기본")

# 탭으로 기능 구분
tab1, tab2 = st.tabs(["📂 모든 파일 한 곳에 모으기", "✏️ 파일명 일괄 수정"])

# ==================== 기능 1: 모든 파일 한 곳에 모으기 ====================
with tab1:
    st.header("📂 폴더 내 모든 파일을 한 폴더에 놓기")
    st.markdown("하위 폴더의 모든 파일을 한 곳에 모아서 다운로드합니다.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("💡 왼쪽에서 폴더를 선택하고 처리 버튼을 누르세요")
    
    with col2:
        folder_path_1 = st.text_input("📁 폴더 경로", key="folder1", placeholder="C:\\Users\\...")
    
    if st.button("🚀 파일 모으기 시작", key="collect_btn", use_container_width=True):
        if not folder_path_1 or not os.path.exists(folder_path_1):
            st.error("❌ 올바른 폴더 경로를 입력해주세요")
        else:
            try:
                with st.spinner("파일을 수집하는 중..."):
                    # 모든 파일 찾기
                    all_files = []
                    for root, dirs, files in os.walk(folder_path_1):
                        for file in files:
                            all_files.append(os.path.join(root, file))
                    
                    if not all_files:
                        st.warning("⚠️ 폴더에 파일이 없습니다")
                    else:
                        # 메모리에 ZIP 파일 생성
                        zip_buffer = io.BytesIO()
                        
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for file_path in all_files:
                                # 파일명만 추출 (경로 제거)
                                file_name = os.path.basename(file_path)
                                
                                # 중복 파일명 처리
                                base_name = file_name
                                counter = 1
                                while any(zinfo.filename == file_name for zinfo in zip_file.filelist):
                                    name, ext = os.path.splitext(base_name)
                                    file_name = f"{name}_{counter}{ext}"
                                    counter += 1
                                
                                # ZIP에 추가
                                zip_file.write(file_path, file_name)
                        
                        zip_buffer.seek(0)
                        
                        st.success(f"✅ 총 {len(all_files)}개 파일 수집 완료!")
                        
                        # 다운로드 버튼
                        st.download_button(
                            label="📥 압축 파일 다운로드",
                            data=zip_buffer.getvalue(),
                            file_name=f"모든파일_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                        
                        # 파일 목록 미리보기
                        with st.expander("📋 수집된 파일 목록 보기"):
                            for i, file_path in enumerate(all_files[:100], 1):
                                st.text(f"{i}. {os.path.basename(file_path)}")
                            if len(all_files) > 100:
                                st.text(f"... 외 {len(all_files) - 100}개")
            
            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")

# ==================== 기능 2: 파일명 일괄 수정 ====================
with tab2:
    st.header("✏️ 폴더 내 모든 파일들의 제목 수정")
    st.markdown("파일명을 규칙에 맞게 일괄 변경합니다.")
    
    # 레이아웃
    col_left, col_right = st.columns([3, 1])
    
    with col_left:
        # 옵션 설정
        col_opt1, col_opt2, col_opt3 = st.columns(3)
        
        with col_opt1:
            # 확장자 선택 (나중에 동적으로 채워짐)
            ext_options = st.session_state.get('ext_options', ['모든 파일'])
            selected_ext = st.selectbox("📄 파일 확장자", ext_options, key="ext_select")
        
        with col_opt2:
            sort_by = st.selectbox(
                "📊 정렬 기준",
                ["이름순", "날짜순 (오래된 순)", "날짜순 (최신 순)", "크기순 (작은 순)", "크기순 (큰 순)"]
            )
        
        with col_opt3:
            naming_type = st.selectbox(
                "🔤 파일명 형식",
                ["숫자 추가", "특정 문자 추가"]
            )
        
        # 특정 문자 입력란 (조건부 표시)
        if naming_type == "특정 문자 추가":
            custom_text = st.text_input("✍️ 추가할 문자", placeholder="예: 여행사진", key="custom_text")
        else:
            custom_text = None
    
    with col_right:
        folder_path_2 = st.text_input("📁 폴더 경로", key="folder2", placeholder="C:\\Users\\...")
        
        # 폴더가 지정되면 확장자 목록 추출
        if folder_path_2 and os.path.exists(folder_path_2):
            try:
                extensions = set(['모든 파일'])
                for root, dirs, files in os.walk(folder_path_2):
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if ext:
                            extensions.add(ext)
                
                st.session_state['ext_options'] = sorted(list(extensions))
                st.success(f"✅ {len(extensions)-1}개 확장자 발견")
            except:
                pass
    
    if st.button("🚀 파일명 변경 시작", key="rename_btn", use_container_width=True):
        if not folder_path_2 or not os.path.exists(folder_path_2):
            st.error("❌ 올바른 폴더 경로를 입력해주세요")
        elif naming_type == "특정 문자 추가" and not custom_text:
            st.error("❌ 추가할 문자를 입력해주세요")
        else:
            try:
                with st.spinner("파일명을 변경하는 중..."):
                    # 파일 수집
                    all_files = []
                    for root, dirs, files in os.walk(folder_path_2):
                        for file in files:
                            file_path = os.path.join(root, file)
                            ext = os.path.splitext(file)[1].lower()
                            
                            # 확장자 필터링
                            if selected_ext == '모든 파일' or ext == selected_ext:
                                all_files.append(file_path)
                    
                    if not all_files:
                        st.warning("⚠️ 조건에 맞는 파일이 없습니다")
                    else:
                        # 정렬
                        if sort_by == "이름순":
                            all_files.sort(key=lambda x: os.path.basename(x))
                        elif sort_by == "날짜순 (오래된 순)":
                            all_files.sort(key=lambda x: os.path.getmtime(x))
                        elif sort_by == "날짜순 (최신 순)":
                            all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                        elif sort_by == "크기순 (작은 순)":
                            all_files.sort(key=lambda x: os.path.getsize(x))
                        elif sort_by == "크기순 (큰 순)":
                            all_files.sort(key=lambda x: os.path.getsize(x), reverse=True)
                        
                        # ZIP 파일 생성
                        zip_buffer = io.BytesIO()
                        
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for idx, file_path in enumerate(all_files, 1):
                                ext = os.path.splitext(file_path)[1]
                                
                                # 새 파일명 생성
                                if naming_type == "숫자 추가":
                                    new_name = f"{idx:04d}_{os.path.basename(file_path)}"
                                else:  # 특정 문자 추가
                                    new_name = f"{custom_text}_{idx:04d}{ext}"
                                
                                # ZIP에 추가
                                zip_file.write(file_path, new_name)
                        
                        zip_buffer.seek(0)
                        
                        st.success(f"✅ 총 {len(all_files)}개 파일명 변경 완료!")
                        
                        # 다운로드 버튼
                        st.download_button(
                            label="📥 변경된 파일 다운로드",
                            data=zip_buffer.getvalue(),
                            file_name=f"이름변경_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                        
                        # 변경 결과 미리보기
                        with st.expander("📋 변경된 파일명 미리보기"):
                            for idx, file_path in enumerate(all_files[:50], 1):
                                ext = os.path.splitext(file_path)[1]
                                old_name = os.path.basename(file_path)
                                
                                if naming_type == "숫자 추가":
                                    new_name = f"{idx:04d}_{old_name}"
                                else:
                                    new_name = f"{custom_text}_{idx:04d}{ext}"
                                
                                st.text(f"{old_name} → {new_name}")
                            
                            if len(all_files) > 50:
                                st.text(f"... 외 {len(all_files) - 50}개")
            
            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")

# 사이드바 - 사용 안내
with st.sidebar:
    st.header("📖 사용 방법")
    
    st.markdown("""
    ### 🎯 기능 1: 파일 모으기
    1. 폴더 경로 입력
    2. '파일 모으기 시작' 클릭
    3. 압축 파일 다운로드
    
    ### 🎯 기능 2: 파일명 변경
    1. 폴더 경로 입력
    2. 확장자 & 정렬 기준 선택
    3. 파일명 형식 선택
    4. '파일명 변경 시작' 클릭
    5. 압축 파일 다운로드
    """)
    
    st.markdown("---")
    st.info("💡 원본 파일은 변경되지 않습니다. 새로운 압축 파일로 제공됩니다.")
    
    st.markdown("---")
    st.markdown("### ⚙️ 폴더 경로 찾는 법")
    st.markdown("""
    **Windows:**
    1. 폴더 열기
    2. 주소창 클릭
    3. 경로 복사
    
    **예시:**  
    `C:\\Users\\사용자명\\Documents\\내폴더`
    """)