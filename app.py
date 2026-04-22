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

# 2. 디자인 스타일 적용 (줄바꿈 버그 수정본)
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
    
    .title-signboard h1 { 
        margin: 0 !important; 
        font-family: 'NanumSquareNeo', sans-serif !important;
        font-size: 32px !important; 
        font-weight: 900 !important; 
        color: #1d1d1f !important; 
        letter-spacing: -1.0px !important;
        display: flex !important; justify-content: center !important; align-items: center !important; gap: 15px !important;
    }
    
    .version-tag { 
        display: inline-block !important; 
        margin-top: 18px !important; 
        padding: 6px 18px !important; 
        font-size: 13px !important; 
        font-weight: 800 !important; 
        color: #6366f1 !important; 
        background-color: #f0f1ff !important; 
        border-radius: 20px !important; 
    }
    
    .section-title { font-size: 14px !important; font-weight: 700 !important; color: #86868b !important; margin-top: 20px !important; padding-left: 4px !important; }
    
    /* [중요] 모든 코드 박스 줄바꿈 강제 설정 */
    div.stCode { background-color: #f5f5f7 !important; border-radius: 16px !important; border: none !important; margin-bottom: 10px !important; }
    div.stCode pre { 
        padding: 22px !important; 
        white-space: pre-wrap !important; 
        word-break: break-all !important; 
    }
    div.stCode code { 
        font-family: 'KoPubDotum', sans-serif !important; 
        color: #1d1d1f !important; 
        font-size: 15px !important; 
        line-height: 1.7 !important; 
    }

    /* 오답 지문용 주황색 하이라이트 (복사 버튼 유지형) */
    .wrong-answer div[data-testid="stCodeBlock"] pre {
        background-color: #FFD580 !important; 
        border: 2px solid #FFB347 !important;
    }
    .wrong-answer div[data-testid="stCodeBlock"] code {
        font-weight: 800 !important;
        color: #000000 !important;
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

# 3. 데이터 파싱 함수
def parse_block(text_block):
    try:
        parts = text_block.split('☞ 정답')
        if len(parts) < 2: return None
        
        question = re.sub(r'^0\.\s*', '', parts[0]).strip()
        ans_part = parts[1].strip()
        
        # 오답 여부 판별 (님이 주신 특수문자 포함)
        is_wrong = False
        if any(mark in ans_part[:15] for mark in ['(☓)', '(X)', '(x)', '(×)']):
            is_wrong = True

        ans_part = re.sub(r'↑.*?↑|↓.*?↓', '', ans_part).strip()
        source_match = re.search(r'(\[[^\]]+\])', ans_part)
        source = source_match.group(1).strip() if source_match else "시행처 없음"
        
        ref_text = re.sub(r'^\([○OX☓×]\)\s*', '', ans_part)
        reference = "근거 확인 필요"
        case_matches = re.findall(r'((?:대법원|헌재)?\s*\d{4}\.?\s*\d{1,2}\.?\s*\d{1,2}\.?\s*(?:선고|자)?\s*\d{2,4}[가-힣]{1,2}\d{1,5})', ref_text)
        if case_matches: reference = case_matches[-1].strip()

        return {"q": question, "ans": ans_part, "ref": reference, "src": source, "wrong": is_wrong}
    except: return None

# 4. 검색 및 출력
query = st.text_input("🔍 검색어를 입력하세요")
if os.path.exists("database.txt") and query:
    with open("database.txt", 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = re.split(r'(?m)^0\.\s', content)
    found = 0
    for b in blocks:
        if not b.strip() or query not in b: continue
        d = parse_block("0. " + b)
        if d:
            found += 1
            with st.container(border=True):
                st.markdown("<div class='section-title'>📝 지문</div>", unsafe_allow_html=True)
                if d['wrong']:
                    st.markdown('<div class="wrong-answer">', unsafe_allow_html=True)
                    st.code(d['q'], language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.code(d['q'], language="text")
                
                st.markdown("<div class='section-title'>✔️ 정답 및 해설</div>", unsafe_allow_html=True)
                st.code(d['ans'], language="text")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("<div class='section-title'>🏢 시행처</div>", unsafe_allow_html=True)
                    st.code(d['src'], language="text")
                with c2:
                    st.markdown("<div class='section-title'>⚖️ 판례 / 조문 번호</div>", unsafe_allow_html=True)
                    st.code(d['ref'], language="text")
    if found == 0: st.warning("결과가 없습니다.")
    else: st.success(f"총 {found}개의 관련 지문을 찾았습니다.")
else:
    st.error("데이터베이스 파일이 없거나 검색어가 없습니다.")
