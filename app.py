import streamlit as st
import re
import os

# ==========================================
# [설정] 비밀번호 및 버전 정보
# ==========================================
MY_PASSWORD = "leylab2026"  
MY_VERSION = "VERSION_260422" 
# ==========================================

# 1. 페이지 세팅
st.set_page_config(page_title="이은영 헌법 통합검색 TOOL", layout="centered")

# --- 로그인 로직 (불변) ---
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

# 2. 디자인 스타일 적용 (기존 스타일 보존 및 하이라이트 강화)
st.markdown("""
    <style>
    @import url('https://webfontworld.github.io/kopub/KoPubDotum.css');
    @import url('https://hangeul.pstatic.net/hangeul_static/css/nanum-square-neo.css');
    
    html, body, [class*="css"], .stMarkdown, p, div, span { 
        font-family: 'KoPubDotum', sans-serif !important; 
    }
    
    .title-signboard { 
        background-color: #ffffff !important;
        background-image: radial-gradient(#d1d1d6 0.8px, transparent 0.8px) !important;
        background-size: 12px 12px !important;
        padding: 45px 20px !important; 
        border-radius: 24px !important; 
        text-align: center !important; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.05) !important; 
        margin-bottom: 30px !important; 
        border: 1px solid #f0f0f5 !important;
    }
    
    .section-title { font-size: 14px !important; font-weight: 700 !important; color: #86868b !important; margin-top: 20px !important; padding-left: 4px !important; }
    
    /* 기본 코드 박스 디자인 */
    div.stCode { background-color: #f5f5f7 !important; border-radius: 16px !important; border: none !important; margin-bottom: 10px !important; }
    div.stCode pre { padding: 22px !important; white-space: pre-wrap !important; word-break: break-all !important; }
    div.stCode code { 
        font-family: 'KoPubDotum', sans-serif !important; 
        color: #1d1d1f !important; 
        font-size: 15px !important; 
        line-height: 1.7 !important; 
    }

    /* [긴급 수정] 오답 지문용 하이라이트 - 억지로 주황색 주입 */
    .highlight-x-box div[data-testid="stCodeBlock"] pre {
        background-color: #FFD580 !important; 
        border: 2px solid #FFB347 !important;
    }
    .highlight-x-box div[data-testid="stCodeBlock"] code {
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        background-color: #ffffff !important; 
        padding: 10px 20px 30px 20px !important; 
        border-radius: 24px !important; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.04) !important; 
        border: 1px solid #f0f0f5 !important; 
        margin-bottom: 30px !important; 
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="title-signboard">
        <h1>⚖️ 이은영 헌법 통합검색 TOOL ⚖️</h1>
        <div class="version-tag">{MY_VERSION}</div>
    </div>
""", unsafe_allow_html=True)

# 3. 데이터 파싱 함수 (오답 판별 로직 보완)
def parse_block(text_block):
    try:
        parts = text_block.split('☞ 정답')
        if len(parts) < 2: return None
        
        question = re.sub(r'^0\.\s*', '', parts[0]).strip()
        ans_exp_full = parts[1].strip()
        
        # [정밀 타격] 님이 주신 특수문자 (☓)를 포함하여 앞부분에서 오답 여부 체크
        is_wrong = False
        head_text = ans_exp_full[:20] # 앞부분 20자 내에서 판별
        if '(☓)' in head_text or '(X)' in head_text or '(x)' in head_text or '(×)' in head_text:
            is_wrong = True

        ans_exp_full = re.sub(r'↑.*?↑|↓.*?↓', '', ans_exp_full).strip()
        source_match = re.search(r'(\[[^\]]+\])', ans_exp_full)
        source = source_match.group(1).strip() if source_match else "시행처 없음"
        
        # 레퍼런스 추출 로직 보존
        reference = "근거 확인 필요"
        ref_temp = re.sub(r'^\([○OX☓×]\)\s*', '', ans_exp_full)
        case_matches = re.findall(r'((?:대법원|헌재)?\s*\d{4}\.?\s*\d{1,2}\.?\s*\d{1,2}\.?\s*(?:선고|자)?\s*\d{2,4}[가-힣]{1,2}\d{1,5})', ref_temp)
        if case_matches: reference = case_matches[-1].strip()

        return {"지문": question, "해설": ans_exp_full, "번호": reference, "처": source, "오답": is_wrong}
    except: return None

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
            if not block.strip() or search_query not in block: continue
            data = parse_block("0. " + block)
            if data:
                results_found += 1
                with st.container(border=True):
                    st.markdown("<div class='section-title'>📝 지문</div>", unsafe_allow_html=True)
                    
                    if data['오답']:
                        # 오답일 때만 전용 클래스 적용
                        st.markdown('<div class="highlight-x-box">', unsafe_allow_html=True)
                        st.code(data['지문'], language="text")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.code(data['지문'], language="text")
                        
                    st.markdown("<div class='section-title'>✔️ 정답 및 해설</div>", unsafe_allow_html=True)
                    st.code(data['해설'], language="text")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("<div class='section-title'>🏢 시행처</div>", unsafe_allow_html=True)
                        st.code(data['처'], language="text")
                    with c2:
                        st.markdown("<div class='section-title'>⚖️ 판례 / 조문 번호</div>", unsafe_allow_html=True)
                        st.code(data['번호'], language="text")
        
        if results_found == 0: st.warning("결과가 없습니다.")
        else: st.success(f"총 {results_found}개의 관련 지문을 찾았습니다.")
else: st.error("database.txt 파일을 찾을 수 없습니다.")
