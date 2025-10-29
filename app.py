import streamlit as st
import zipfile
import io
from datetime import datetime
import os
import json

st.set_page_config(page_title="컴퓨터 정리의 기본", layout="wide", page_icon="📁")

# 폰트 크기 조정 및 고정 헤더 스타일
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-size: 18px !important;
        }
        h1 { font-size: 24px !important; }
        h2 { font-size: 21px !important; }
        h3 { font-size: 18px !important; }
        p, span, div { font-size: 18px !important; }
        button { font-size: 18px !important; }
        input { font-size: 18px !important; }
        textarea { font-size: 18px !important; }
        label { font-size: 18px !important; }
        .stMetric { font-size: 18px !important; }
        .stMetricDelta { font-size: 18px !important; }
        
        /* 고정 헤더 스타일 */
        .fixed-header {
            position: fixed;
            top: 70px;
            right: 20px;
            z-index: 999;
            background-color: white;
            padding: 15px 25px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            display: flex;
            gap: 15px;
            align-items: center;
            border: 1px solid #e0e0e0;
        }
        
        .fixed-header-button {
            background-color: #FF4B4B;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
        }
        
        .fixed-header-button:hover {
            background-color: #FF3333;
        }
        
        .visitor-count {
            background-color: #f0f2f6;
            padding: 8px 16px;
            border-radius: 5px;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

# 방문자 카운팅 기능
def init_visitor_count():
    """방문자 수 초기화"""
    if 'visitor_date' not in st.session_state:
        st.session_state['visitor_date'] = datetime.now().date()
        st.session_state['visitor_count'] = 1
    else:
        today = datetime.now().date()
        if st.session_state['visitor_date'] != today:
            # 새로운 날짜면 카운트 리셋
            st.session_state['visitor_date'] = today
            st.session_state['visitor_count'] = 1
        else:
            # 같은 날이면 카운트 증가
            st.session_state['visitor_count'] += 1

# 페이지 로드 시 방문자 카운팅
init_visitor_count()

# 고정된 헤더 (HTML로 생성)
if 'show_panel' not in st.session_state:
    st.session_state['show_panel'] = False

st.markdown(f"""
    <div class="fixed-header">
        <div class="visitor-count">
            👥 오늘 방문자: <strong>{st.session_state['visitor_count']}</strong>
        </div>
    </div>
""", unsafe_allow_html=True)

# 의견남기기 버튼 (스크롤 가능한 위치에 배치)
col1, col2 = st.columns([5, 1])
with col2:
    if st.button("💬 의견남기기", key="toggle_panel_top"):
        st.session_state['show_panel'] = not st.session_state['show_panel']

st.title("📁 컴퓨터 정리의 기본")

# 왼쪽 사이드바 - 사용 안내
with st.sidebar:
    st.header("📖 사용 방법")
    
    st.markdown("""
    ### 🎯 기능 1: 파일 모으기
    1. ZIP 파일 업로드
    2. '파일 모으기 시작' 클릭
    3. 압축 파일 다운로드
    
    ### 🎯 기능 2: 파일명 변경
    1. ZIP 파일 업로드
    2. 확장자 & 정렬 기준 선택
    3. 파일명 형식 선택
    4. '파일명 변경 시작' 클릭
    5. 압축 파일 다운로드
    
    ### 🎯 기능 3: 압축파일 자동 해제
    1. ZIP 파일 업로드
    2. 옵션 선택
    3. '압축파일 해제 시작' 클릭
    4. 처리된 파일 다운로드
    """)
    
    st.markdown("---")
    st.info("💡 원본 파일은 변경되지 않습니다. 새로운 압축 파일로 제공됩니다.")
    
    st.markdown("---")
    st.markdown("### 📝 팁")
    st.markdown("""
    - 사용자 폴더를 압축한 후 업로드하세요
    - 모든 작업은 메모리에서 이루어집니다
    - 다운로드한 ZIP 파일을 원하는 위치에서 압축 해제하세요
    """)

tab1, tab2, tab3 = st.tabs(["📂 모든 파일 한 곳에 모으기", "✏️ 파일명 일괄 수정", "📦 압축파일 자동 해제"])

# ==================== 기능 1: 파일 모으기 ====================
with tab1:
    st.header("📂 폴더 내 모든 파일을 한 폴더에 놓기")
    st.markdown("ZIP 파일을 업로드하면 모든 파일을 한 곳에 모아서 다시 압축해드립니다.")
    
    # 파일 업로드 버튼의 가로폭을 2배로 (3칸 중 2칸 사용)
    col_upload, col_empty = st.columns([2, 1])
    with col_upload:
        uploaded_zip = st.file_uploader("📁 ZIP 파일 업로드", type="zip", key="uploader_tab1")
    
    if uploaded_zip and st.button("🚀 파일 모으기 시작", key="collect_btn", use_container_width=True):
        try:
            with st.spinner("파일을 수집하는 중..."):
                # 업로드된 ZIP 파일 읽기
                input_zip = zipfile.ZipFile(uploaded_zip)
                
                # 모든 파일 추출 (폴더 제외)
                all_files = [f for f in input_zip.namelist() if not f.endswith('/')]
                
                if not all_files:
                    st.warning("⚠️ ZIP 파일에 파일이 없습니다")
                else:
                    # 결과 ZIP 생성
                    output_zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(output_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as output_zip:
                        file_counter = {}
                        
                        for file_name in all_files:
                            # 파일명만 추출 (경로 제거)
                            base_file_name = file_name.split('/')[-1]
                            
                            # 중복 처리
                            if base_file_name in file_counter:
                                file_counter[base_file_name] += 1
                                name, ext = os.path.splitext(base_file_name)
                                final_name = f"{name}_{file_counter[base_file_name]}{ext}"
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
                    
                    # 처음으로 버튼
                    if st.button("🔄 처음으로", use_container_width=True, key="reset1"):
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ 오류 발생: {str(e)}")

# ==================== 기능 2: 파일명 일괄 수정 ====================
with tab2:
    st.header("✏️ 폴더 내 모든 파일들의 제목 수정")
    st.markdown("ZIP 파일을 업로드한 후 옵션을 선택하고 실행하세요")
    
    # 파일 업로드 버튼의 가로폭을 2배로 (3칸 중 2칸 사용)
    col_upload, col_empty = st.columns([2, 1])
    with col_upload:
        uploaded_zip_2 = st.file_uploader("📁 ZIP 파일 업로드", type="zip", key="uploader_tab2")
    
    if uploaded_zip_2:
        # ZIP 파일 읽기
        input_zip_2 = zipfile.ZipFile(uploaded_zip_2)
        all_files_in_zip = [f for f in input_zip_2.namelist() if not f.endswith('/')]
        
        # 확장자 추출
        extensions = set(['모든 파일'])
        for file_name in all_files_in_zip:
            ext = os.path.splitext(file_name)[1].lower()
            if ext:
                extensions.add(ext)
        
        st.success(f"✅ {len(extensions)-1}개 확장자 발견")
        
        # 옵션 설정
        col_opt1, col_opt2, col_opt3 = st.columns([1, 1, 1])
        
        with col_opt1:
            selected_ext = st.selectbox("📄 파일 확장자", sorted(list(extensions)))
        
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
        custom_text = None
        if naming_type == "특정 문자 추가":
            custom_text = st.text_input("✍️ 추가할 문자", placeholder="예: 여행사진")
        
        if st.button("🚀 파일명 변경 시작", key="rename_btn", use_container_width=True):
            if naming_type == "특정 문자 추가" and not custom_text:
                st.error("❌ 추가할 문자를 입력해주세요")
            else:
                try:
                    with st.spinner("파일명을 변경하는 중..."):
                        # 확장자 필터링
                        filtered_files = []
                        for file_name in all_files_in_zip:
                            ext = os.path.splitext(file_name)[1].lower()
                            if selected_ext == '모든 파일' or ext == selected_ext:
                                filtered_files.append(file_name)
                        
                        if not filtered_files:
                            st.warning("⚠️ 조건에 맞는 파일이 없습니다")
                        else:
                            # 파일 정보 추출 (정렬을 위해)
                            file_info = []
                            for file_name in filtered_files:
                                file_content = input_zip_2.read(file_name)
                                file_size = len(file_content)
                                # 수정 시간은 ZIP에서 직접 가져오기
                                file_info.append({
                                    'name': file_name,
                                    'content': file_content,
                                    'size': file_size
                                })
                            
                            # 정렬
                            if sort_by == "이름순":
                                file_info.sort(key=lambda x: x['name'].split('/')[-1])
                            elif sort_by == "크기순 (작은 순)":
                                file_info.sort(key=lambda x: x['size'])
                            elif sort_by == "크기순 (큰 순)":
                                file_info.sort(key=lambda x: x['size'], reverse=True)
                            
                            # 결과 ZIP 생성
                            output_zip_buffer = io.BytesIO()
                            preview_list = []
                            
                            with zipfile.ZipFile(output_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as output_zip:
                                for idx, file_info_item in enumerate(file_info, 1):
                                    original_name = file_info_item['name'].split('/')[-1]
                                    ext = os.path.splitext(original_name)[1]
                                    
                                    # 새 파일명 생성
                                    if naming_type == "숫자 추가":
                                        new_name = f"{idx:04d}_{original_name}"
                                    else:  # 특정 문자 추가
                                        new_name = f"{custom_text}_{original_name}"
                                    
                                    # ZIP에 추가
                                    output_zip.writestr(new_name, file_info_item['content'])
                                    preview_list.append((original_name, new_name))
                            
                            output_zip_buffer.seek(0)
                            
                            st.success(f"✅ 총 {len(file_info)}개 파일명 변경 완료!")
                            
                            # 다운로드 버튼
                            st.download_button(
                                label="📥 변경된 파일 다운로드",
                                data=output_zip_buffer.getvalue(),
                                file_name=f"이름변경_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                            
                            # 변경 결과 미리보기
                            with st.expander("📋 변경된 파일명 미리보기"):
                                for old_name, new_name in preview_list[:50]:
                                    st.text(f"{old_name} → {new_name}")
                                
                                if len(preview_list) > 50:
                                    st.text(f"... 외 {len(preview_list) - 50}개")
                            
                            # 처음으로 버튼
                            if st.button("🔄 처음으로", use_container_width=True, key="reset2"):
                                st.rerun()
                
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")

# ==================== 기능 3: 압축파일 자동 해제 ====================
with tab3:
    st.header("📦 폴더 내 모든 압축파일 자동 해제")
    st.markdown("ZIP 파일을 업로드하면 내부의 모든 압축파일(.zip, .rar, .7z 등)을 해제하고 원본 압축파일을 제거합니다.")
    
    # 파일 업로드 버튼의 가로폭을 2배로 (3칸 중 2칸 사용)
    col_upload, col_empty = st.columns([2, 1])
    with col_upload:
        uploaded_zip_3 = st.file_uploader("📁 ZIP 파일 업로드", type="zip", key="uploader_tab3")
    
    if uploaded_zip_3:
        st.info("💡 압축파일 해제 옵션을 선택하고 시작 버튼을 눌러주세요")
        
        # 옵션
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            keep_original = st.checkbox("원본 압축파일 보관", value=False)
        with col_opt2:
            nested_extract = st.checkbox("중첩된 압축파일도 해제", value=True)
        
        if st.button("🚀 압축파일 해제 시작", key="extract_btn", use_container_width=True):
            try:
                with st.spinner("압축파일을 해제하는 중..."):
                    # 업로드된 ZIP 파일 읽기
                    input_zip_3 = zipfile.ZipFile(uploaded_zip_3)
                    all_files = input_zip_3.namelist()
                    
                    # 압축파일 확장자 리스트
                    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}
                    
                    # 모든 파일 추출하기
                    extracted_files = {}
                    archive_files = []
                    
                    for file_path in all_files:
                        if file_path.endswith('/'):
                            continue
                        
                        file_content = input_zip_3.read(file_path)
                        file_name = file_path.split('/')[-1]
                        file_ext = os.path.splitext(file_name)[1].lower()
                        
                        if file_ext in archive_extensions:
                            archive_files.append((file_name, file_content, file_ext))
                        else:
                            extracted_files[file_name] = file_content
                    
                    # 압축파일 해제
                    total_extracted = 0
                    
                    for archive_name, archive_content, archive_ext in archive_files:
                        try:
                            # ZIP 파일만 처리 (다른 형식은 바이너리로 저장)
                            if archive_ext == '.zip':
                                archive_buffer = io.BytesIO(archive_content)
                                try:
                                    extracted_zip = zipfile.ZipFile(archive_buffer)
                                    for inner_file in extracted_zip.namelist():
                                        if not inner_file.endswith('/'):
                                            inner_content = extracted_zip.read(inner_file)
                                            inner_file_name = inner_file.split('/')[-1]
                                            
                                            # 중복 처리
                                            if inner_file_name in extracted_files:
                                                base_name, ext = os.path.splitext(inner_file_name)
                                                counter = 1
                                                new_name = f"{base_name}_{counter}{ext}"
                                                while new_name in extracted_files:
                                                    counter += 1
                                                    new_name = f"{base_name}_{counter}{ext}"
                                                extracted_files[new_name] = inner_content
                                            else:
                                                extracted_files[inner_file_name] = inner_content
                                            
                                            total_extracted += 1
                                            
                                            # 중첩된 압축파일도 해제할지 확인
                                            if nested_extract:
                                                inner_ext = os.path.splitext(inner_file_name)[1].lower()
                                                if inner_ext == '.zip':
                                                    try:
                                                        nested_buffer = io.BytesIO(inner_content)
                                                        nested_zip = zipfile.ZipFile(nested_buffer)
                                                        for nested_file in nested_zip.namelist():
                                                            if not nested_file.endswith('/'):
                                                                nested_content = nested_zip.read(nested_file)
                                                                nested_file_name = nested_file.split('/')[-1]
                                                                
                                                                if nested_file_name in extracted_files:
                                                                    base_name, ext = os.path.splitext(nested_file_name)
                                                                    counter = 1
                                                                    new_name = f"{base_name}_{counter}{ext}"
                                                                    while new_name in extracted_files:
                                                                        counter += 1
                                                                        new_name = f"{base_name}_{counter}{ext}"
                                                                    extracted_files[new_name] = nested_content
                                                                else:
                                                                    extracted_files[nested_file_name] = nested_content
                                                                
                                                                total_extracted += 1
                                                    except:
                                                        pass
                                    
                                    # 원본 압축파일 보관하지 않음 (기본값)
                                    if not keep_original and archive_name in extracted_files:
                                        del extracted_files[archive_name]
                                
                                except:
                                    # 손상된 ZIP 파일이면 그냥 저장
                                    if keep_original:
                                        extracted_files[archive_name] = archive_content
                            else:
                                # ZIP이 아닌 다른 압축파일은 그냥 저장
                                if keep_original:
                                    extracted_files[archive_name] = archive_content
                        except:
                            if keep_original:
                                extracted_files[archive_name] = archive_content
                    
                    # 원본 압축파일도 해제하지 않을 경우 제거
                    if not keep_original:
                        for archive_name, _, _ in archive_files:
                            if archive_name in extracted_files:
                                del extracted_files[archive_name]
                    
                    # 결과 ZIP 생성
                    output_zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(output_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as output_zip:
                        for file_name, file_content in extracted_files.items():
                            output_zip.writestr(file_name, file_content)
                    
                    output_zip_buffer.seek(0)
                    
                    st.success(f"✅ 압축파일 해제 완료! ({len(archive_files)}개 압축파일 해제, {total_extracted}개 파일 추출)")
                    
                    # 다운로드 버튼
                    st.download_button(
                        label="📥 처리된 파일 다운로드",
                        data=output_zip_buffer.getvalue(),
                        file_name=f"압축해제_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                    
                    # 결과 미리보기
                    with st.expander("📋 처리된 파일 목록"):
                        for i, file_name in enumerate(sorted(extracted_files.keys())[:100], 1):
                            st.text(f"{i}. {file_name}")
                        if len(extracted_files) > 100:
                            st.text(f"... 외 {len(extracted_files) - 100}개")
                    
                    # 처음으로 버튼
                    if st.button("🔄 처음으로", use_container_width=True, key="reset3"):
                        st.rerun()
            
            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")

# ==================== 의견남기기 패널 ====================
st.markdown("""
<style>
    .right-panel {
        position: fixed;
        right: 20px;
        top: 150px;
        width: 350px;
        max-height: 80vh;
        overflow-y: auto;
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# 게시판 데이터 초기화
if 'posts' not in st.session_state:
    st.session_state['posts'] = []

# 의견남기기 패널
if st.session_state['show_panel']:
    with st.expander("💬 의견남기기", expanded=True):
        st.subheader("✍️ 의견 작성")
        author_name = st.text_input("이름", placeholder="이름을 입력하세요", key="panel_name")
        author_email = st.text_input("이메일 (선택)", placeholder="이메일을 입력하세요", key="panel_email")
        
        post_content = st.text_area("의견", placeholder="수정 의견이나 개선사항을 작성해주세요", height=100, key="panel_content")
        
        if st.button("📤 의견 제출", use_container_width=True, key="panel_submit"):
            if not author_name or not post_content:
                st.error("❌ 이름과 의견을 입력해주세요")
            else:
                new_post = {
                    'name': author_name,
                    'email': author_email if author_email else "비공개",
                    'content': post_content,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                st.session_state['posts'].insert(0, new_post)
                st.success("✅ 의견이 등록되었습니다!")
                st.rerun()
        
        # 게시판 목록
        st.markdown("---")
        st.subheader("📋 등록된 의견")
        
        if len(st.session_state['posts']) == 0:
            st.info("📝 아직 의견이 없습니다.")
        else:
            for idx, post in enumerate(st.session_state['posts'][:5]):  # 최근 5개만 표시
                with st.container(border=True):
                    st.write(f"**{post['name']}**")
                    st.write(f"📅 {post['date']}")
                    st.caption(post['content'][:50] + "..." if len(post['content']) > 50 else post['content'])
                    
                    if st.button("🗑️", key=f"panel_delete_{idx}", help="삭제"):
                        st.session_state['posts'].pop(idx)
                        st.rerun()
            
            if len(st.session_state['posts']) > 5:
                st.info(f"... 외 {len(st.session_state['posts']) - 5}개")