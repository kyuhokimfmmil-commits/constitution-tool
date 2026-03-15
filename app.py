import streamlit as st
import re
import os

# ==========================================
# [설정] 비밀번호 및 버전 정보
# ==========================================
MY_PASSWORD = "leylab2026"  # 👈 여기서 원하는 비밀번호로 수정하세요!
MY_VERSION = "VERSION_260314" # 👈 오늘 날짜 버전명
# ==========================================

# 1. 페이지 세팅
st.set_page_config(page_title="이은영 헌법 통합검색 TOOL", layout="centered")

# --- 로그인 로직 시작 ---
def check_password():
    """비밀번호가 맞으면 True를 반환합니다."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # 로그인 화면 디자인
    st.markdown("""
        <div style='text-align: center; padding: 50px 0;'>
            <h2 style='color: #1d1d1f;'>🔒 보안 인증</h2>
            <p style='color: #86868b;'>이 프로그램은 승인된 사용자만 이용할 수 있습니다.</p>
        </div>
    """, unsafe_allow_html=True)
    
    password = st.text_input("비밀번호를 입력하세요", type="password")
    
    if st.button("접속하기"):
        if password == MY_PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ 비밀번호가 틀렸습니다.")
    return False

# 로그인 통과 못 하면 여기서 멈춤
if not check_password():
    st.stop()
# --- 로그인 로직 끝 ---

# 2. 디자인 스타일 적용 (나눔스퀘어 네오 & 보라색 테마)
st.markdown("""
    <style>
    /* 폰트 불러오기 (나눔스퀘어 네오) */
    @import url('https://hangeul.pstatic.net/hangeul_static/css/nanum-square-neo.css');
    
    html, body, [class*="css"], .stMarkdown, p, div, span { 
        font-family: 'NanumSquareNeo', sans-serif !important; 
        font-weight: 500; 
        color: #1d1d1f; 
    }
    
    /* 제목 전광판 스타일 */
    .title-signboard { 
        background-color: #ffffff; 
        padding: 35px 20px; 
        border-radius: 24px; 
        text-align: center; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.04); 
        margin-bottom: 25px; 
        margin-top: 20px; 
        border: 1px solid #f0f0f5;
    }
    
    /* [수정된 부분] 제목 폰트: 나눔스퀘어 네오 Heavy + 보라색 */
    .title-signboard h1 { 
        margin: 0; 
        font-family: 'NanumSquareNeo', sans-serif !important;
        font-size: 32px; 
        font-weight: 900 !important; /* Heavy 두께 */
        color: #6366f1; /* 세련된 보라색 */
        letter-spacing: -1.5px; 
    }
    
    /* 버전 태그도 보라색 톤으로 통일 */
    .version-tag { 
        display: inline-block; 
        margin-top: 12px; 
        padding: 5px 14px; 
        font-size: 12px; 
        font-weight: 800; 
        color: #6366f1; 
        background-color: #f0f1ff; 
        border-radius: 12px; 
    }
    
    .section-title { font-size: 14px; font-weight: 800 !important; color: #86868b; margin-bottom: 8px; margin-top: 20px; padding-left: 4px; }
    
    /* 검색 결과 박스 디자인 */
    div.stCode { background-color: #f8f8fa !important; border-radius: 16px !important; border: 1px solid #f0f0f5 !important; margin-bottom: 10px; }
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        background-color: #ffffff; 
        padding: 10px 20px 30px 20px; 
        border-radius: 24px; 
        box-shadow: 0 10px 40px rgba(99, 102, 241, 0.05); /* 박스에도 은은한 보라색 그림자 */
        border: 1px solid #f0f0f5 !important; 
        margin-bottom: 30px; 
    }
    </style>
""", unsafe_allow_html=True)

# 상단 제목 (로그인 후 보임)
st.markdown(f"""
    <div class="title-signboard">
        <h1>이은영 헌법 통합검색 TOOL</h1>
        <div class="version-tag">{MY_VERSION}</div>
    </div>
""", unsafe_allow_html=True)

# 3. 데이터 파싱 함수
def parse_block(text_block):
    try:
        parts = text_block.split('☞ 정답')
        if len(parts) < 2: return None
        
        question = re.sub(r'^0\.\s*', '', parts[0]).strip()
        full_answer_part = parts[1].strip()
        full_answer_part = re.sub(r'↑.*?↑|↓.*?↓', '', full_answer_part).strip()
        
        source_match = re.search(r'(\[[^\]]+\])', full_answer_part)
        
        if source_match:
            source = source_match.group(1).strip()
            clean_exp = full_answer_part[:source_match.start()].strip()
            
            # 불필요한 분류 꼬리표만 정밀 제거 (사례 보존)
            clean_exp = re.sub(r'(\n|^).*?(?:개념|의의|기출)\s*지문\s*$', '', clean_exp, flags=re.MULTILINE).strip()
            clean_exp = re.sub(r'(\n|^).*?(?:정리|기출)\s*$', '', clean_exp, flags=re.MULTILINE).strip()
            
            ans_exp_full = clean_exp + " " + source
        else:
            source = "시행처 없음"
            ans_exp_full = full_answer_part
            
        reference = "근거 확인 필요"
        ref_text_temp = re.sub(r'^\([○OX×]\)\s*', '', ans_exp_full)
        if '("' in ref_text_temp: 
            reference = ref_text_temp.split('("')[0].strip()
        elif '「' in ref_text_temp:
            match = re.search(r'(「.*?」\s*제\d+조(?:\([^\)]+\))?)', ref_text_temp)
            if match: reference = match.group(1).strip()
                
        if reference == "근거 확인 필요" or not reference:
            case_matches = re.findall(r'((?:대법원|헌재)?\s*\d{4}\.?\s*\d{1,2}\.?\s*\d{1,2}\.?\s*(?:선고|자)?\s*\d{2,4}[가-힣]{1,2}\d{1,5}|(?<!\d)\d{2,4}[가-힣]{1,2}\d{1,5})', ans_exp_full)
            if case_matches: reference = case_matches[-1].strip()
            else:
                law_matches = re.findall(r'([가-힣]+법\s*제\d+조(?:의\d+)?|헌법\s*제\d+조(?:의\d+)?)', ans_exp_full)
                if law_matches: reference = law_matches[-1].strip()

        return {"지문": question, "정답및해설": ans_exp_full, "판례번호": reference, "시행처": source}
    except Exception: return None

# 4. 검색창 및 결과 출력
search_query = st.text_input("🔍 검색어를 입력하세요")
db_path = "database.txt"

if os.path.exists(db_path):
    if search_query:
        with open(db_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        blocks = re.split(r'(?m)^0\.\s', content)
        results_found = 0
        
        for block in blocks:
            if not block.strip(): continue
            if search_query in block:
                parsed_data = parse_block("0. " + block)
                if parsed_data:
                    results_found += 1
                    with st.container(border=True):
                        st.markdown("<div class='section-title'>📝 지문</div>", unsafe_allow_html=True)
                        st.code(parsed_data['지문'], language="text")
                        
                        st.markdown("<div class='section-title'>✔️ 정답 및 해설</div>", unsafe_allow_html=True)
                        st.code(parsed_data['정답및해설'], language="text")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("<div class='section-title'>🏢 시행처</div>", unsafe_allow_html=True)
                            st.code(parsed_data['시행처'], language="text")
                        with col2:
                            st.markdown("<div class='section-title'>⚖️ 판례 / 조문 번호</div>", unsafe_allow_html=True)
                            st.code(parsed_data['판례번호'], language="text")
                            
        st.divider()
        if results_found == 0: st.warning("일치하는 검색 결과가 없습니다.")
        else: st.success(f"총 {results_found}개의 관련 지문을 찾았습니다.")
else:
    st.error("⚠️ 같은 폴더에 'database.txt' 파일이 없습니다.")
