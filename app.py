import streamlit as st
import re
import os
import urllib.parse

# ==========================================
# [설정] 비밀번호 및 버전 정보
# ==========================================
MY_PASSWORD = "leylab2026"  
MY_VERSION = "VERSION_260504" 
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

# 2. 디자인 스타일 적용 (원본 유지 + 하이라이트 + 링크 스타일)
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
    
    div.stCode { background-color: #f5f5f7 !important; border-radius: 16px !important; border: none !important; margin-bottom: 10px !important; }
    div.stCode pre, div.stCode code { 
        font-family: 'KoPubDotum', sans-serif !important; 
        white-space: pre-wrap !important; 
        word-break: break-all !important; 
        color: #1d1d1f !important; 
        font-size: 15px !important; 
        line-height: 1.7 !important; 
        background-color: transparent !important;
    }
    div.stCode pre { padding: 22px !important; }
    
    .highlight-x {
        background-color: #FFD580 !important;
        color: #000000 !important;
        padding: 20px !important;
        border-radius: 16px !important;
        font-size: 15px !important;
        line-height: 1.7 !important;
        font-weight: 600 !important;
        border: 2px solid #FFB347 !important;
        margin-bottom: 10px !important;
        white-space: pre-wrap !important;
        word-break: break-all !important;
    }

    /* 판례 링크 전용 스타일 */
    .court-search-link {
        display: block !important;
        background-color: #f5f5f7 !important;
        padding: 22px !important;
        border-radius: 16px !important;
        text-decoration: none !important;
        color: #6366f1 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border: 1px dashed #6366f1 !important;
        text-align: center !important;
    }
    .court-search-link:hover {
        background-color: #eeefff !important;
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

# 3. 데이터 파싱 함수 (원본 유지)
def parse_block(text_block):
    try:
        parts = text_block.split('☞ 정답')
        if len(parts) < 2: return None
        question = re.sub(r'^0\.\s*', '', parts[0]).strip()
        full_answer_part = parts[1].strip()
        is_wrong_statement = False
        if re.search(r'\([☓X]\)', full_answer_part):
            is_wrong_statement = True
        full_answer_part = re.sub(r'↑.*?↑|↓.*?↓', '', full_answer_part).strip()
        source_match = re.search(r'(\[[^\]]+\])', full_answer_part)
        if source_match:
            source = source_match.group(1).strip()
            clean_exp = full_answer_part[:source_match.start()].strip()
            ans_exp_full = clean_exp + " " + source
        else:
            source = "시행처 없음"
            ans_exp_full = full_answer_part
        reference = "근거 확인 필요"
        ref_text_temp = re.sub(r'^\([○OX×]\)\s*', '', ans_exp_full)
        case_matches = re.findall(r'((?:대법원|헌재)?\s*\d{4}\.?\s*\d{1,2}\.?\s*\d{1,2}\.?\s*(?:선고|자)?\s*\d{2,4}[가-힣]{1,2}\d{1,5}|(?<!\d)\d{2,4}[가-힣]{1,2}\d{1,5})', ans_exp_full)
        if case_matches: reference = case_matches[-1].strip()
        return {"지문": question, "정답및해설": ans_exp_full, "판례번호": reference, "시행처": source, "오답여부": is_wrong_statement}
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
                        if parsed_data['오답여부']:
                            st.markdown(f"<div class='highlight-x'>{parsed_data['지문']}</div>", unsafe_allow_html=True)
                        else:
                            st.code(parsed_data['지문'], language="text")
                            
                        st.markdown("<div class='section-title'>✔️ 정답 및 해설</div>", unsafe_allow_html=True)
                        st.code(parsed_data['정답및해설'], language="text")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("<div class='section-title'>🏢 시행처</div>", unsafe_allow_html=True)
                            st.code(parsed_data['시행처'], language="text")
                        with col2:
                            st.markdown("<div class='section-title'>⚖️ 판례 / 조문 번호 (클릭 시 자동검색)</div>", unsafe_allow_html=True)
                            p_num = parsed_data['판례번호']
                            
                            if p_num and p_num != "근거 확인 필요":
                                # [핵심] 지능형 판례검색 결과 페이지로 즉시 연결되는 파라미터 적용
                                encoded_p_num = urllib.parse.quote(p_num)
                                # 헌재 사이트의 검색 수행 URL 구조 적용
                                court_search_url = f"https://isearch.ccourt.go.kr/search.do?searchText={encoded_p_num}"
                                
                                st.markdown(f"""
                                    <a href="{court_search_url}" target="_blank" class="court-search-link">
                                        🔗 {p_num} (검색 결과 보기)
                                    </a>
                                """, unsafe_allow_html=True)
                            else:
                                st.code(p_num, language="text")
                                
        if results_found == 0: st.warning("결과가 없습니다.")
        else: st.success(f"총 {results_found}개의 관련 지문을 찾았습니다.")
else: st.error("database.txt 파일을 찾을 수 없습니다.")
