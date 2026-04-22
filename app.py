import streamlit as st
import re
import os

# ==========================================
# [설정] 비밀번호 및 버전 정보
# ==========================================
MY_PASSWORD = "leylab2026"  
MY_VERSION = "VERSION_260422_HYPER" 
# ==========================================

# 1. 페이지 세팅
st.set_page_config(page_title="이은영 헌법 통합검색 TOOL", layout="centered")

# --- 로그인 로직 ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    st.markdown("<div style='text-align: center; padding: 50px 0;'><h2>🔒 보안 인증</h2></div>", unsafe_allow_html=True)
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("접속하기"):
        if password == MY_PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("❌ 비밀번호가 틀렸습니다.")
    st.stop()

# 2. 디자인 스타일 적용 (줄바꿈 및 가독성 100% 보장)
st.markdown("""
    <style>
    @import url('https://webfontworld.github.io/kopub/KoPubDotum.css');
    @import url('https://hangeul.pstatic.net/hangeul_static/css/nanum-square-neo.css');
    
    html, body, [class*="css"], .stMarkdown, p, div, span { font-family: 'KoPubDotum', sans-serif !important; }
    
    .title-signboard { 
        background-color: #ffffff; background-image: radial-gradient(#d1d1d6 0.8px, transparent 0.8px);
        background-size: 12px 12px; padding: 45px 20px; border-radius: 24px; text-align: center; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.05); margin-bottom: 30px; border: 1px solid #f0f0f5;
    }
    
    .section-title { font-size: 14px; font-weight: 700; color: #86868b; margin-top: 20px; padding-left: 4px; }
    
    /* [핵심] 지문 출력 박스 - 줄바꿈 강제 및 배경색 고정 */
    .q-box {
        padding: 22px; border-radius: 16px; font-size: 15px; line-height: 1.7;
        white-space: pre-wrap; word-wrap: break-word; word-break: break-all;
        margin-bottom: 10px; font-family: 'KoPubDotum', sans-serif !important;
    }
    .q-normal { background-color: #f5f5f7; color: #1d1d1f; }
    .q-wrong { background-color: #FFD580 !important; color: #000000 !important; border: 2px solid #FFB347; font-weight: 800; }

    div[data-testid="stVerticalBlockBorderWrapper"] { 
        background-color: #ffffff; padding: 10px 20px 30px 20px; border-radius: 24px; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.04); border: 1px solid #f0f0f5; margin-bottom: 30px; 
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="title-signboard"><h1>⚖️ 이은영 헌법 통합검색 TOOL ⚖️</h1><div class="version-tag">{MY_VERSION}</div></div>', unsafe_allow_html=True)

# 3. 데이터 파싱 함수 (오답 판별 로직 최강화)
def parse_block(text_block):
    try:
        parts = text_block.split('☞ 정답')
        if len(parts) < 2: return None
        question = re.sub(r'^0\.\s*', '', parts[0]).strip()
        ans_exp = parts[1].strip()
        
        # 님이 주신 특수문자 (☓)를 포함한 모든 X 기호 정밀 매칭
        is_wrong = False
        head = ans_exp[:15]
        if any(x in head for x in ['(☓)', '(X)', '(x)', '(×)', '☓', 'X', 'x']):
            is_wrong = True

        ans_exp = re.sub(r'↑.*?↑|↓.*?↓', '', ans_exp).strip()
        source_match = re.search(r'(\[[^\]]+\])', ans_exp)
        source = source_match.group(1).strip() if source_match else "시행처 없음"
        
        ref_text = re.sub(r'^\([○OX☓×]\)\s*', '', ans_exp)
        reference = "근거 확인 필요"
        case_m = re.findall(r'((?:대법원|헌재)?\s*\d{4}\.?\s*\d{1,2}\.?\s*\d{1,2}\.?\s*(?:선고|자)?\s*\d{2,4}[가-힣]{1,2}\d{1,5})', ref_text)
        if case_m: reference = case_m[-1].strip()

        return {"q": question, "ans": ans_exp, "ref": reference, "src": source, "wrong": is_wrong}
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
                # 지문 출력: X면 주황색 박스, O면 회색 박스 / 복사 버튼 대용으로 st.text_area 활용
                if d['wrong']:
                    st.markdown(f"<div class='q-box q-wrong'>{d['q']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='q-box q-normal'>{d['q']}</div>", unsafe_allow_html=True)
                
                # [복사 기능 보장] 하단 버튼이나 해설 부분은 st.code 유지
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
elif not os.path.exists("database.txt"): st.error("database.txt가 없습니다.")
