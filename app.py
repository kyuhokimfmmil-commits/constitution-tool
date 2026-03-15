import streamlit as st
import re
import os

# ==========================================
# [설정] 비밀번호 및 버전 정보 (로직 유지)
# ==========================================
MY_PASSWORD = "leylab2026"  
MY_VERSION = "VERSION_260314" 
# ==========================================

# 1. 페이지 세팅
st.set_page_config(page_title="이은영 헌법 통합검색 TOOL", layout="centered")

# --- 로그인 로직 (절대 불변) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True
    st.markdown("<div style='text-align: center; padding: 50px 0;'><h2>🔒 보안 인증</h2></div>", unsafe_allow_html=True)
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("접속하기"):
        if password == MY_PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ 비밀번호가 틀렸습니다.")
    return False

if not check_password():
    st.stop()

# 2. 디자인 스타일 적용 (제목 부분 대폭 업그레이드)
st.markdown("""
    <style>
    /* 나눔스퀘어 네오 폰트 강제 로드 */
    @font-face {
        font-family: 'NanumSquareNeoHeavy';
        src: url('https://hangeul.pstatic.net/hangeul_static/webfont/nanum-square-neo/NanumSquareNeo-eHv.eot');
        src: url('https://hangeul.pstatic.net/hangeul_static/webfont/nanum-square-neo/NanumSquareNeo-eHv.eot?#iefix') format('embedded-opentype'),
             url('https://hangeul.pstatic.net/hangeul_static/webfont/nanum-square-neo/NanumSquareNeo-eHv.woff2') format('woff2'),
             url('https://hangeul.pstatic.net/hangeul_static/webfont/nanum-square-neo/NanumSquareNeo-eHv.woff') format('woff'),
             url('https://hangeul.pstatic.net/hangeul_static/webfont/nanum-square-neo/NanumSquareNeo-eHv.ttf') format('truetype');
    }
    @import url('https://webfontworld.github.io/kopub/KoPubDotum.css');
    
    html, body, [class*="css"], .stMarkdown, p, div, span { 
        font-family: 'KoPubDotum', sans-serif !important; 
    }
    
    /* [업그레이드] 제목 전광판: 블랙 법전 & 애플 감성 */
    .title-signboard { 
        background-color: #1d1d1f; /* 애플 블랙 */
        background-image: linear-gradient(145deg, #1d1d1f 0%, #2c2c2e 100%); /* 미세한 그라데이션 */
        padding: 40px 20px; 
        border-radius: 24px; 
        text-align: center; 
        box-shadow: 0 20px 50px rgba(0,0,0,0.15); /* 깊은 그림자 */
        margin-bottom: 25px; 
        margin-top: 20px;
        border: 1px solid #3a3a3c; /* 미세한 테두리 */
        position: relative;
        overflow: hidden;
    }
    
    /* 법전 문양 백그라운드 효과 (패턴) */
    .title-signboard::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background-image: url('https://www.transparenttextures.com/patterns/dark-dot-2.png'); /* 미세한 도트 패턴 */
        opacity: 0.1;
        transform: rotate(10deg);
    }
    
    /* 제목 폰트: Heavy + 보라색 고정 (아이콘 포함) */
    .title-signboard h1 { 
        margin: 0 !important; 
        font-family: 'NanumSquareNeoHeavy', sans-serif !important;
        font-size: 32px !important; 
        font-weight: 900 !important; 
        color: #6366f1 !important; /* 선명한 인디고 보라색 */
        letter-spacing: -1.0px !important; 
        line-height: 1.3 !important;
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 12px; /* 아이콘과 간격 */
    }
    
    /* 제목 앞뒤 아이콘 스타일 */
    .title-icon {
        font-size: 36px;
        opacity: 0.8;
    }
    
    /* 버전 태그: 블랙 배경에 맞춘 스타일 */
    .version-tag { 
        display: inline-block; 
        margin-top: 16px; 
        padding: 6px 18px; 
        font-size: 13px; 
        font-weight: 800; 
        color: #ffffff; 
        background-color: rgba(99, 102, 241, 0.4); /* 연한 보라색 반투명 */
        border-radius: 20px; 
        position: relative;
    }
    
    .section-title { font-size: 14px; font-weight: 700; color: #86868b; margin-top: 20px; }
    div.stCode { background-color: #f5f5f7 !important; border-radius: 16px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #ffffff; padding: 10px 20px 30px 20px; border-radius: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.04); border: 1px solid #f0f0f5 !important; }
    </style>
""", unsafe_allow_html=True)

# 상단 제목 출력 (아이콘 추가)
st.markdown(f"""
    <div class="title-signboard">
        <h1>
            <span class="title-icon">⚖️</span> 이은영 헌법 통합검색 TOOL
            <span class="title-icon">📜</span> </h1>
        <div class="version-tag">{MY_VERSION}</div>
    </div>
""", unsafe_allow_html=True)

# 3. 데이터 파싱 및 검색 로직 (절대 불변)
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
            clean_exp = re.sub(r'(\n|^).*?(?:개념|의의|기출)\s*지문\s*$', '', clean_exp, flags=re.MULTILINE).strip()
            ans_exp_full = clean_exp + " " + source
        else:
            source = "시행처 없음"; ans_exp_full = full_answer_part
            
        reference = "근거 확인 필요"
        ref_text_temp = re.sub(r'^\([○OX×]\)\s*', '', ans_exp_full)
        if '("' in ref_text_temp: reference = ref_text_temp.split('("')[0].strip()
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
        if results_found == 0: st.warning("결과가 없습니다.")
else:
    st.error("database.txt 파일을 찾을 수 없습니다.")
