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
        /* 메인 영역만 18px 적용 (사이드바 제외) */
        .main html, .main body, .main [class*="css"] {
            font-size: 18px !important;
        }
        .main h1 { font-size: 24px !important; margin-top: 0 !important; margin-bottom: 0.2rem !important; }
        .main h2 { font-size: 21px !important; margin-top: 0 !important; margin-bottom: 0.2rem !important; }
        .main h3 { font-size: 18px !important; margin-top: 0 !important; margin-bottom: 0.2rem !important; }
        .main h4 { font-size: 16px !important; margin-top: 0 !important; margin-bottom: 0.2rem !important; }
        .main h5 { font-size: 9px !important; margin-top: 0.3rem !important; margin-bottom: 0.1rem !important; font-weight: bold !important; }
        .main h6 { font-size: 8px !important; margin-top: 0.1rem !important; margin-bottom: 0.1rem !important; line-height: 1.3 !important; }
        .main p, .main span, .main div { font-size: 18px !important; margin-top: 0 !important; margin-bottom: 0 !important; }
        .main button { font-size: 18px !important; margin: 0 !important; }
        .main input { font-size: 18px !important; }
        .main textarea { font-size: 18px !important; }
        .main label { font-size: 18px !important; }
        .main .stMetric { font-size: 18px !important; }
        .main .stMetricDelta { font-size: 18px !important; }
        
        /* 사이드바용 작은 폰트 스타일 */
        section[data-testid="stSidebar"] h5 { 
            font-size: 9px !important; 
            margin-top: 0.3rem !important; 
            margin-bottom: 0.1rem !important; 
            font-weight: bold !important; 
            line-height: 1.2 !important;
        }
        section[data-testid="stSidebar"] h6 { 
            font-size: 8px !important; 
            margin-top: 0.1rem !important; 
            margin-bottom: 0.1rem !important; 
            line-height: 1.3 !important;
            font-weight: normal !important;
        }
        
        /* 사이드바 항목 간격 거의 0으로 */
        section[data-testid="stSidebar"] > div {
            padding-top: 0.2rem;
            padding-bottom: 0.2rem;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 0.2rem !important;
            padding-bottom: 0.2rem !important;
        }
        section[data-testid="stSidebar"] .element-container {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
            padding-bottom: 0 !important;
            padding-top: 0 !important;
        }
        section[data-testid="stSidebar"] hr {
            margin-top: 0.2rem !important;
            margin-bottom: 0.2rem !important;
        }
        section[data-testid="stSidebar"] h2 {
            margin-top: 0 !important;
            margin-bottom: 0.2rem !important;
            padding-top: 0 !important;
        }
        section[data-testid="stSidebar"] h3 {
            margin-top: 0 !important;
            margin-bottom: 0.1rem !important;
            padding-top: 0 !important;
        }
        section[data-testid="stSidebar"] ul, 
        section[data-testid="stSidebar"] ol {
            margin-top: 0 !important;
            margin-bottom: 0.2rem !important;
            padding-top: 0 !important;
        }
        section[data-testid="stSidebar"] li {
            margin-bottom: 0.1rem !important;
        }
        
        /* 메인 영역 항목 간격 최소화 */
        .main .block-container {
            padding-top: 0.5rem;
        }
        .element-container {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
            padding-bottom: 0 !important;
            padding-top: 0 !important;
        }
        
        /* 탭 간격 줄이기 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.2rem;
            margin-bottom: 0.3rem !important;
        }
        
        /* 파일 업로더 상단 간격 제거 */
        [data-testid="stFileUploader"] {
            margin-top: 0 !important;
            margin-bottom: 0.2rem !important;
            padding-top: 0 !important;
        }
        
        /* 텍스트와 헤더 간격 최소화 */
        .main h1 {
            margin-bottom: 0.2rem !important;
            margin-top: 0 !important;
        }
        .main h2 {
            margin-top: 0.2rem !important;
            margin-bottom: 0.2rem !important;
        }
        
        /* 마크다운 요소 간격 제거 */
        .stMarkdown {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
            padding-bottom: 0 !important;
            padding-top: 0 !important;
        }
        .stMarkdown p {
            margin-bottom: 0.1rem !important;
            margin-top: 0 !important;
        }
        
        /* 버튼 간격 제거 */
        .stButton {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        .stButton > button {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        
        /* 컬럼 간격 줄이기 */
        [data-testid="column"] {
            padding: 0 0.2rem !important;
        }
        
        /* 모든 div 간격 최소화 */
        div.row-widget {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
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
            st.session_state['visitor_date'] = today
            st.session_state['visitor_count'] = 1
        else:
            st.session_state['visitor_count'] += 1

# 페이지 로드 시 방문자 카운팅
init_visitor_count()

# 고정된 헤더 초기화
if 'show_panel' not in st.session_state:
    st.session_state['show_panel'] = False

if 'posts' not in st.session_state:
    st.session_state['posts'] = []

st.title("📁 컴퓨터 정리의 기본")

# 왼쪽 사이드바
with st.sidebar:
    # 홈으로 버튼
    st.markdown("""
        <a href="https://webexcel-wqqus7hhrxvn59tn3f6knp.streamlit.app/" target="_self" style="text-decoration: none;">
            <button style="width: 100%; padding: 10px; background-color: #FF4B4B; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: 500; margin-bottom: 5px;">
                🏠 홈으로
            </button>
        </a>
    """, unsafe_allow_html=True)
    
    # 방문자 수 (첫 번째 줄)
    st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px 20px; border-radius: 8px; text-align: center; margin-bottom: 5px; margin-top: 5px;">
            <span style="font-size: 16px;">👥 오늘 방문자: <strong style="font-size: 22px;">{st.session_state['visitor_count']}</strong></span>
        </div>
    """, unsafe_allow_html=True)
    
    # 의견게시판 버튼 (두 번째 줄)
    if st.button("💬 의견게시판", use_container_width=True, key="sidebar_toggle"):
        st.session_state['show_panel'] = not st.session_state['show_panel']
    
    st.markdown("---")
    
    # 사용 방법 섹션 - h5, h6 HTML 태그 사용
    st.markdown("<h5>📖 사용 방법</h5>", unsafe_allow_html=True)
    
    st.markdown("<h5>🎯 기능 1: 파일 모으기</h5>", unsafe_allow_html=True)
    st.markdown("<h6>1. ZIP 파일 업로드</h6>", unsafe_allow_html=True)
    st.markdown("<h6>2. '파일 모으기 시작' 클릭</h6>", unsafe_allow_html=True)
    st.markdown("<h6>3. 압축 파일 다운로드</h6>", unsafe_allow_html=True)
    
    st.markdown("<h5>🎯 기능 2: 파일명 변경</h5>", unsafe_allow_html=True)
    st.markdown("<h6>1. ZIP 파일 업로드</h6>", unsafe_allow_html=True)
    st.markdown("<h6>2. 확장자 & 정렬 기준 선택</h6>", unsafe_allow_html=True)
    st.markdown("<h6>3. 파일명 형식 선택</h6>", unsafe_allow_html=True)
    st.markdown("<h6>4. '파일명 변경 시작' 클릭</h6>", unsafe_allow_html=True)
    st.markdown("<h6>5. 압축 파일 다운로드</h6>", unsafe_allow_html=True)
    
    st.markdown("<h5>🎯 기능 3: 압축파일 자동 해제</h5>", unsafe_allow_html=True)
    st.markdown("<h6>1. ZIP 파일 업로드</h6>", unsafe_allow_html=True)
    st.markdown("<h6>2. 옵션 선택</h6>", unsafe_allow_html=True)
    st.markdown("<h6>3. '압축파일 해제 시작' 클릭</h6>", unsafe_allow_html=True)
    st.markdown("<h6>4. 처리된 파일 다운로드</h6>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<div style="background-color:#d1ecf1; border-left:4px solid #0c5460; padding:8px; border-radius:4px; margin:5px 0;"><p style="font-size:16px; margin:0; color:#0c5460;">💡 원본 파일은 변경되지 않습니다. 새로운 압축 파일로 제공됩니다.</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<p style="font-size:20px; font-weight:bold; margin-bottom:5px;">📝 팁</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:16px; margin:2px 0;">• 사용자 폴더를 압축한 후 업로드하세요<br>• 모든 작업은 메모리에서 이루어집니다<br>• 다운로드한 ZIP 파일을 원하는 위치에서 압축 해제하세요</p>', unsafe_allow_html=True)

# 의견남기기 패널
if st.session_state['show_panel']:
    with st.expander("💬 의견남기기", expanded=True):
        st.subheader("✍️ 의견 작성")
        author_name = st.text_input("이름", placeholder="이름을 입력하세요", key="panel_name")
        author_email = st.text_input("이메일 (선택)", placeholder="이메일을 입력하세요", key="panel_email")
        
        post_content = st.text_area("의견", placeholder="수정 의견이나 개선사항을 작성해주세요", height=100, key="panel_content")
        
        col1, col2 = st.columns([3, 1])
        with col1:
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
        with col2:
            if st.button("❌ 닫기", use_container_width=True):
                st.session_state['show_panel'] = False
                st.rerun()
        
        # 게시판 목록
        st.markdown("---")
        st.subheader("📋 등록된 의견")
        
        if len(st.session_state['posts']) == 0:
            st.info("📝 아직 의견이 없습니다.")
        else:
            for idx, post in enumerate(st.session_state['posts'][:10]):
                with st.container(border=True):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.write(f"**{post['name']}**")
                        st.caption(f"📅 {post['date']}")
                        st.write(post['content'][:100] + "..." if len(post['content']) > 100 else post['content'])
                    with col2:
                        if st.button("🗑️", key=f"panel_delete_{idx}", help="삭제"):
                            st.session_state['posts'].pop(idx)
                            st.rerun()
            
            if len(st.session_state['posts']) > 10:
                st.info(f"... 외 {len(st.session_state['posts']) - 10}개")

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