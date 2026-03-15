import streamlit as st
import re
import os

# 1. 페이지 및 테마 세팅
st.set_page_config(page_title="이은영 헌법 통합검색 TOOL", layout="centered")
st.markdown("""
    <style>
    @import url('https://webfontworld.github.io/kopub/KoPubDotum.css');
    
    html, body, [class*="css"], .stMarkdown, p, div, span { 
        font-family: 'KoPubDotum', 'KoPub 돋움체', sans-serif !important; 
        font-weight: 500; 
        color: #1d1d1f; 
    }
    
    .title-signboard { background-color: #ffffff; padding: 30px 20px; border-radius: 24px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.04); margin-bottom: 20px; margin-top: 20px; }
    .title-signboard h1 { margin: 0; font-size: 26px; font-weight: 700 !important; color: #1d1d1f; letter-spacing: -1px; }
    .version-tag { display: inline-block; margin-top: 12px; padding: 5px 14px; font-size: 12px; font-weight: 700; color: #0066cc; background-color: #e5f0ff; border-radius: 12px; }
    
    .section-title { font-size: 14px; font-weight: 700 !important; color: #86868b; margin-bottom: 8px; margin-top: 20px; padding-left: 4px; }
    
    div.stCode { background-color: #f5f5f7 !important; border-radius: 16px !important; border: none !important; margin-bottom: 10px; }
    div.stCode pre, div.stCode code { 
        font-family: 'KoPubDotum', 'KoPub 돋움체', sans-serif !important; 
        white-space: pre-wrap !important; 
        word-break: break-all !important; 
        color: #1d1d1f !important; 
        font-size: 15px !important; 
        line-height: 1.7 !important; 
        background-color: transparent !important;
    }
    div.stCode pre { padding: 22px !important; padding-right: 60px !important; }
    
    div.stCode button, [data-testid="stCodeBlock"] button {
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        background-color: #ffffff; 
        padding: 10px 20px 30px 20px; 
        border-radius: 24px; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.04); 
        border: 1px solid #f0f0f5 !important; 
        margin-bottom: 30px; 
    }
    </style>
""", unsafe_allow_html=True)

# 2. 상단 제목
st.markdown("""
    <div class="title-signboard">
        <h1>이은영 헌법 통합검색 TOOL</h1>
        <div class="version-tag">VERSION_STABLE_V4</div>
    </div>
""", unsafe_allow_html=True)

# 3. 텍스트 분리 및 정밀 클리닝
def parse_block(text_block):
    try:
        parts = text_block.split('☞ 정답')
        if len(parts) < 2: return None
        
        question = re.sub(r'^0\.\s*', '', parts[0]).strip()
        full_answer_part = parts[1].strip()
        
        # [1] 화살표 문구들(↑...↑, ↓...↓) 제거
        full_answer_part = re.sub(r'↑.*?↑|↓.*?↓', '', full_answer_part).strip()
        
        # [2] 시행처 대괄호([]) 위치 찾기
        source_match = re.search(r'(\[[^\]]+\])', full_answer_part)
        
        if source_match:
            source = source_match.group(1).strip()
            clean_exp = full_answer_part[:source_match.start()].strip()
            
            # [핵심 수정] '사례'는 남기고, '개념 지문', '의의 지문', '기출 지문' 등만 타격
            # 해설 끝부분에 있는 불필요한 분류 꼬리표만 제거합니다.
            clean_exp = re.sub(r'(\n|^).*?(?:개념|의의|기출)\s*지문\s*$', '', clean_exp, flags=re.MULTILINE).strip()
            clean_exp = re.sub(r'(\n|^).*?(?:정리|기출)\s*$', '', clean_exp, flags=re.MULTILINE).strip()
            
            ans_exp_full = clean_exp + " " + source
        else:
            source = "시행처 없음"
            ans_exp_full = full_answer_part
            
        reference = "근거 확인 필요"
        
        # 판례/조문 번호 추출 로직 (안정화 버전 유지)
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