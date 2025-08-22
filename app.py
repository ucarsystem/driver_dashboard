import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import io
import base64
import requests
import numpy as np
from PIL import Image, ImageOps
import matplotlib as mpl 
import matplotlib.pyplot as plt 
import matplotlib.patches as patches
import matplotlib.font_manager as fm  
import matplotlib.ticker as ticker
from openpyxl import load_workbook
import calendar
import streamlit.components.v1 as components
import datetime
import altair as alt
from io import BytesIO
from textwrap import dedent

# 한글 폰트 설정
# font_path = "./malgun.ttf"  # 또는 절대 경로로 설정 (예: C:/install/FINAL_APP/dashboard/malgun.ttf)
# font_prop = fm.FontProperties(fname=font_path)
# plt.rcParams['font.family'] = font_prop.get_name()
# plt.rcParams['axes.unicode_minus'] = False

font_path = os.path.join(os.path.dirname(__file__), 'malgun.ttf')
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# st.set_page_config(layout="wide")

# 🌈 라이트 모드 강제 적용 CSS
st.markdown("""
    <style>
    body, .stApp {
        background-color: white !important;
        color: black !important;
    }
    
    /*입력창 placeholder 대비 강화*/
    input::placeholder {
        color: #666 !important;
        opacity: 1 !important;
    }
    
    /* 기본 버튼 스타일 수정 */
    button[kind="primary"], .stButton > button {
        background-color: transparent !important;
        color: #222 !important;
        border: 2px solid #666 !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }

    /* 모바일에서 제목 크기 축소 */
    @media screen and (max-width: 480px) {
        h1, h2, h3, h4 {
            font-size: 20px !important;
        }
        p, td, span, li, .markdown-text-container {
            font-size: 13px !important;   
        }

    /* 반응형 등급+달성율 */
    .grade-flex-container {
        display: inline-flex !important;  /* 핵심: inline-flex로 강제 */
        flex-direction: row !important;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin: 20px 0;
        width: auto !important;  /* Streamlit 기본 block 방지 */
        max-width: 100%;
    }
            
    .grade-flex-container img {
        width: 180px;
    }
    
    .grade-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
            
    .grade-text p {
        margin: 0;
        font-size: 16px;
    }

    .grade-text .main {
        font-size: 22px;
        font-weight: bold;
    }

    .grade-text .sub {
        font-size: 13px;
        color: red;
    }
    /* 📱 모바일: 이미지 작게, 텍스트 크게 */
    @media screen and (max-width: 480px) {
        .grade-flex-container img {
            width: 120px !important;
        }
        .grade-text p {
            font-size: 18px !important;
        }
        .grade-text .main {
            font-size: 24px !important;
        }
        .grade-text .sub {
            font-size: 15px !important;
        }
    }
/*여기서부터*/
    .grade-wrapper {
        display: flex;
        flex-direction: row !important;  /* 항상 가로로 정렬 */
        align-items: center;
        gap: 20px;
        justify-content: center;
        margin-top: 10px;
        margin-bottom: 20px;
        flex-wrap: nowrap;
    }
    /* 텍스트 영역 */
    .grade-content {
        display: flex;
        flex-direction: column;
        justify-content: center;
        font-size: 14px;
        text-align: left;
    }
    
    /* 이미지 크기 - 반응형 */
    .grade-wrapper img {
        width: 180px;
    }

    @media (max-width: 480px) {
        .grade-wrapper {
            justify-content: start;
        }
            
        .grade-wrapper img {
            width: 180px;
        }
        
        .grade-content {
            font-size: 16px;
        }
    }
/*여기까지*/
            
    /* 노선 순위표시 */
    .line-grade {
        font-size: 20px; 
        color: gray; 
        margin-top:10px;
    }
    
    @media (max-width: 480px) {
        .line-grade{
            font-size: 12px
        }
    }
    </style>
""", unsafe_allow_html=True)


# 기본 경로 설정
file_dir = "./file"
company_file = os.path.join(file_dir, "company_info.xlsx")
id_check_file = os.path.join(file_dir, "인천ID.xlsx")
file_url_template = "https://github.com/ucarsystem/driver_dashboard/file/인천%20개인별%20대시보드_{year}년{month}월.xlsx"

# 엑셀 파일 로드 함수
def load_excel(path, sheetname):
    try:
        return pd.read_excel(path, sheet_name=sheetname)
    except Exception as e:
        st.error(f"엑셀 파일 로드 오류: {e}")
        return None
    
# 📂 운수사 목록 불러오기
df_company = pd.read_excel(company_file, sheet_name="Sheet1", header=None) if os.path.exists(company_file) else pd.DataFrame()
company_list = df_company[0].dropna().tolist() if not df_company.empty else []
df_code = pd.read_excel(company_file, sheet_name="code") if os.path.exists(company_file) else pd.DataFrame()


# Streamlit UI 구성🚍
st.set_page_config(page_title="나의 ECO 주행성과 보러가기")

st.markdown("""
    <style>
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
    }
    .stTextInput input {
        background-color: white !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

company_list = ["운수사를 선택하세요"] + company_list[1:]
# company_input = st.selectbox("운수사를 입력하세요", options=company_list, index=company_list.index(st.session_state.get("company_input", company_list[0])) if "company_input" in st.session_state else None)
company_input = st.selectbox(
    "운수사를 입력하세요",
    options=company_list,
    index=0  # 기본으로 안내 문구 선택되게
)
user_id_input = st.text_input("운전자 ID를 입력하세요", value=st.session_state.get("user_id_input", ""))
조회버튼 = st.button("조회하기")


# 제목
st.markdown("""
<h2 style='text-align: center;'>나의 ECO 주행성과, 이번 달엔 어땠을까요?</h2>
""", unsafe_allow_html=True)

st.markdown("---")

# 기본 정보

#왼쪽: 이름/ID / 가운데: 등급 원형 / 오른쪽: 달성율
st.markdown("""
<table style='width: 100%; table-layout: fixed; text-align: center; font-size: 16px; border-collapse: collapse; border: none;'>
  <tr>
    <td><b>사원ID</b><br>1587님</td>
    <td><b>소속운수사</b><br>강화교통</td>
    <td><b>노선</b><br>800번</td>
  </tr>
</table>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def draw_grade_progress_ring_base64(
    grade="A",               # 등급
    label="등급",            # 등급 라벨 (예: "우수")
    achieved_pct=95,         # 현재 달성률(%)
    max_pct=120,             # 링 100%로 환산하는 최대치(%)
    incentive_won=280000,    # 예상 월 인센티브(원)
    figsize=(4.5, 4.5),        # 카드 비율 (두 번째 이미지 느낌)
    ring_width=0.12,         # 링 두께 (반지름 대비)
    bg_color="#ffffff",      # 카드 배경
    fg_base="#e6e7ea",       # 미채움 링 색
    cmap_name="RdYlGn",      # 진행 링 색상(낮음=적, 높음=초록)
    start_angle=-90,
    dpi=200,
):
    # 안전 처리
    max_pct = max(1e-6, float(max_pct))
    value = max(0.0, float(achieved_pct))
    frac = min(value / max_pct, 1.0)   # 0~1
    angle = 360.0 * frac

    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect("equal")
    ax.axis("off")

    # 둥근 카드 배경
    card = patches.FancyBboxPatch(
        (0.02, 0.06), 0.96, 0.88,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        linewidth=0.0, facecolor=bg_color)
    ax.add_patch(card)

    # 링 위치/크기
    cx, cy = 0.50, 0.50    # 세로 중앙으로 이동
    r = 0.42               # 원 크기
    inner_r = r * (1 - ring_width)

    # 기본(미채움) 링
    base_wedge = patches.Wedge((cx, cy), r, 0, 360, width=r-inner_r,
                               facecolor=fg_base, linewidth=0)
    ax.add_patch(base_wedge)

    # 진행 링 (12시부터 시계 방향)
    cmap = mpl.cm.get_cmap(cmap_name)
    prog_color = cmap(frac)
    prog_wedge = patches.Wedge((cx, cy), r, -90, -90+angle, width=r-inner_r,
                               facecolor=prog_color, linewidth=0, antialiased=True)
    ax.add_patch(prog_wedge)

    # --- 텍스트: 등급(녹색), 나머지 검정 ---
    grade_color = "#2e7d32"     # 녹색
    text_color = "#000000"      # 검정

    ax.text(cx, cy + r*0.46, f"{grade} {label}",
        ha="center", va="center", fontsize=20,
        color=grade_color, fontweight="bold")

    ax.text(cx, cy, f"{int(round(value))}%",
            ha="center", va="center", fontsize=54,
            color=text_color, fontweight="bold")

    ax.text(cx, cy - r*0.40, "예상 월 인센티브",
            ha="center", va="center", fontsize=14, color=text_color)

    ax.text(cx, cy - r*0.60, f"{int(incentive_won):,}원",
            ha="center", va="center", fontsize=24,
            color=text_color, fontweight="bold")


    # 투명 배경 PNG → base64
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches=None, transparent=True)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return image_base64


# --- 여기서부터는 페이지에 출력하는 부분 (기존 테이블 레이아웃 유지) ---

# 예시 값
grade = "A"
label = "등급"      # 또는 "우수"
achieved_pct = 95   # 현재 달성률
max_pct = 120       # 총 120%를 링 100%로 간주
incentive_won = 280000

# S 등급까지 남은 퍼센트(예: 100%를 S 기준으로 가정)
remain_to_S = max(0, 100 - achieved_pct)
notice_text  = f"* 다음 S등급까지 {remain_to_S}% 남았습니다." if remain_to_S > 0 else "* S등급 달성!"

circle_base64 = draw_grade_progress_ring_base64(
    grade=grade, label=label, achieved_pct=achieved_pct,
    max_pct=max_pct, incentive_won=incentive_won
)

# 이미지 한 줄 전용 + 아래 문구(검정색)
st.markdown(f"""
<div style="width:100%; text-align:center;">
  <img src="data:image/png;base64,{circle_base64}" style="width:420px; max-width:92vw;">
  <div style="margin-top:10px; color:#000000; font-size:20px;">{notice_text}</div>
</div>
""", unsafe_allow_html=True)

# 단순 줄바꿈
st.markdown("<br><br>", unsafe_allow_html=True)

# 참고치 팝업
with st.expander("📌 상세보기"):
                st.markdown("""
                <div style="font-size:15px; line-height:1.6;">
                
                <div style="margin:15px;">
                <span style="font-size:17px;"><b>금월 나의 인센티브 (1개월 추정)</b></span><br>
                - 예상 기여액 : 2,800,000원<br>
                - 예상 배분액 : 280,000원<br>
                <span style="font-size:15px; color:gray;">(현재의 실적으로 1개월 추정)</span>
                </div>

                <hr style="border: 0.5px solid #ccc;">
                            
                <div style="margin:15px;">
                <span style="font-size:17px;"><b>등급 참고치</b></span><br>
                - 최우수 S : 100% 이상<br>  
                - 우  수 A : 95~100%<br>  
                - 양  호 B : 90~95%<br>  
                - 중  립 C : 85~90%<br>  
                - 노  력 D : 80~85%<br>  
                - 초  보 F : 65~80%<br>
                  이 하 / 평가불가
                </div>
                
                <hr style="border: 0.2px solid #ccc;">
                            
                <div style="margin:15px;">
                <span style="font-size:17px;"><b>달성률 참고치</b></span><br>
                최하위 75% ~ 최상위 100% 이상<br>
                <span style="font-size:15px; color:gray;">* 75% 미만은 연료절감 참여 전 수치</span>
                </div>
                </div>
                """, 
                unsafe_allow_html= True)

if "show_graph" not in st.session_state:
    st.session_state.show_graph = False

#일별/월별 달성률 팝업
# 예시 데이터 (월별)
data = pd.DataFrame({
    "월": ["1월", "2월", "3월", "4월", "5월", "6월", "7월(예상)"],
    "달성률": [92, 97, 89.1, 91.8, 82.4, 100, 95],
    "등급": ["B", "A", "C", "B", "D", "S", "A"]
})

# Altair용 등급 색상 매핑
등급색상 = alt.Scale(
    domain=["S", "A", "B", "C", "D", "F"],
    range=["#0a860a", "#0a860a", "#007bff", "#007bff", "#CA0000", "#CA0000"]
)

with st.expander("📊 월별 달성률 보기", expanded=True):

    # 막대 차트
    bar = alt.Chart(data).mark_bar().encode(
        x=alt.X("월", title="월", axis=alt.Axis(labelAngle=0)),  # ⬅️ 제목 명시!
        y=alt.Y("달성률", scale=alt.Scale(domain=[0, 120]), title="달성률"),
        color=alt.Color("등급", scale=등급색상),
        tooltip=["월", "달성률", "등급"]
    )

    text = alt.Chart(data).mark_text(
        dy=-10,
        fontWeight="bold",
        fontSize=14,
    ).encode(
        x="월",
        y="달성률",
        text="등급",
        color=alt.Color("등급", scale=등급색상, legend=None)
    )

    chart = alt.layer(bar, text).properties(
        width=500,
        height=300
    ).configure_view(
        fill='white'  # 바탕 흰색 고정
    ).configure_axisX(
        labelColor='black',
        titleColor='black',
        tickColor='black'
    ).configure_axisY(
        labelColor='black',
        titleColor='black',
        tickColor='black'
    ).configure(
        background='white'  # 전체 배경 색상 고정!
    )   

    st.altair_chart(chart, use_container_width=True)


# 일별 데이터 팝업
def generate_calendar_html_v2(data, year, month):
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)

    grade_color = {
        "S": "#0a860a",  # 진초록
        "A": "#0a860a",
        "B": "#007bff",  # 파랑
        "C": "#007bff",
        "D": "#CA0000",
        "F": "#CA0000"
    }

    # 공통 인라인 스타일
    wrap_style = "max-width:100%; overflow-x:auto; margin:0 auto;"
    table_style = (
        "table-layout:fixed; width:100%; min-width:660px; "
        "border-collapse:collapse; font-family:'Malgun Gothic', sans-serif;"
    )
    thtd_style = (
        "width:14.2857%; border:1px solid #aaa; padding:4px; "
        "text-align:center; vertical-align:top;"
    )
    th_style = thtd_style + "background:#f0f0f0; font-weight:bold; font-size:15px;"
    td_style = thtd_style + "height:80px; font-size:13px;"

    # 텍스트 스타일용 클래스 (모바일에서만 크기 줄일 거라 class를 같이 넣어둡니다)
    day_cls = "cal-day"
    grade_cls = "cal-grade"
    pct_cls = "cal-pct"

    # day_style = "font-weight:bold;"
    # grade_style = "font-weight:bold; font-size:18px;"
    # pct_style = "font-size:15px; margin-top:2px;"

    # ✅ 모바일(<=480px)일 때만 min-width 해제 + 폰트/높이 축소 (스크롤 제거)
    mobile_css = """
    <style>
    @media (max-width: 480px) {
      .calwrap table { min-width: 0 !important; width: 100% !important; }
      .calwrap th, .calwrap td { padding: 2px !important; height: 60px !important; }
      .calwrap .cal-grade { font-size: 14px !important; }
      .calwrap .cal-pct   { font-size: 12px !important; }
      .calwrap .cal-day   { font-size: 12px !important; }
    }
    </style>
    """

    html = []
    html.append(mobile_css)  # 모바일 오버라이드 CSS 추가
    html.append(f'<div class="calwrap" style="{wrap_style}">')
    html.append(f'<table style="{table_style}">')
    html.append("<tr>")
    html.append(f'<th style="{th_style}color:red">일</th>')
    for h in ["월","화","수","목","금"]:
        html.append(f'<th style="{th_style}">{h}</th>')
    html.append(f'<th style="{th_style}color:blue">토</th>')
    html.append("</tr>")

    for week in month_days:
        html.append("<tr>")
        for day in week:
            if day == 0:
                html.append(f'<td style="{td_style}"></td>')
            else:
                if day in data:
                    g = data[day]["grade"]
                    p = data[day]["percent"]
                    c = grade_color.get(g, "black")
                    html.append(
                        f'<td style="{td_style}">'
                        f'<div class="{day_cls}" style="font-weight:bold;">{day}</div>'
                        f'<div class="{grade_cls}" style="font-weight:bold; font-size:18px; color:{c}">{g}등급</div>'
                        f'<div class="{pct_cls}"   style="font-size:15px; margin-top:2px; color:{c}">({p}%)</div>'
                        f'</td>'
                    )
                else:
                    html.append(
                        f'<td style="{td_style}">'
                        f'<div class="{day_cls}" style="font-weight:bold;">{day}</div>'
                        f'</td>'
                    )
        html.append("</tr>")
    html.append("</table></div>")
    return "".join(html)
    

calendar_data = {
    2: {"grade": "S", "percent": 100},
    3: {"grade": "A", "percent": 96},
    4: {"grade": "B", "percent": 91},
    5: {"grade": "S", "percent": 101},
    9: {"grade": "S", "percent": 100},
    10: {"grade": "A", "percent": 96},
    11: {"grade": "C", "percent": 89},
    16: {"grade": "B", "percent": 91},
    18: {"grade": "A", "percent": 96},
    19: {"grade": "S", "percent": 101},
    20: {"grade": "S", "percent": 100},
    23: {"grade": "S", "percent": 101},
    24: {"grade": "A", "percent": 96},
    25: {"grade": "C", "percent": 89},
    30: {"grade": "S", "percent": 100},
}
calendar_html = generate_calendar_html_v2(calendar_data, 2025, 7)

with st.expander("📅 7월 일별 달성률 보기", expanded=True):
    st.markdown(calendar_html, unsafe_allow_html=True)

st.markdown("---")

# --- rank bar 생성 함수 ---
@st.cache_data(show_spinner=False)
def draw_rank_bar(
    min_value: int,
    max_value: int,
    current_value: int,
    width=6.0, height=1.15, dpi=220,
    bar_left=0.12, bar_right=0.88, bar_y=0.55,
    segments=6,
    line_color="#9AA3AB",      # 점선 색
    tick_color="#9AA3AB",      # 눈금 색
    label_color="#2B2F33",     # 좌/우 라벨 색
    marker_color="#1F4AA0",    # 삼각형 마커/내 위치 텍스트 색
    bg="white",
    # ⬇️ 새 파라미터
    outside_gap=0.02,          # 바에서 라벨까지 간격(좌/우 동일)
    end_tick_len=0.08,         # 양 끝(좌/우) 긴 눈금 길이
    mid_tick_len=0.03,         # 중간 눈금 길이
    pad_x = 0.06               # 좌우 여백 (텍스트 잘림 방지용)
):
    """
    최하위~최상위 사이 점선 바에 현재 값을 삼각형으로 표시한 이미지를 base64로 반환.
    """
    # 안전 처리
    min_v = float(min_value); max_v = float(max_value)
    cur_v = float(current_value); span = max(max_v - min_v, 1e-6)

    # figure
    fig = plt.figure(figsize=(width, height), dpi=dpi, facecolor=bg)
    ax = fig.add_axes([0, 0, 1, 1], facecolor=bg)
    # ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    # 👇 좌우로 여유를 줘서 바깥 라벨이 잘리지 않게 함
    ax.set_xlim(-pad_x, 1 + pad_x)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # 점선 바
    ax.hlines(y=bar_y, xmin=bar_left, xmax=bar_right,
              colors=line_color, linestyles=(0, (6, 6)), linewidth=2.0, zorder=1)
    
    # 끝(좌/우) 긴 눈금
    ax.vlines(x=bar_left,  ymin=bar_y-end_tick_len, ymax=bar_y+end_tick_len,
              colors=tick_color, linewidth=1.8, zorder=2)
    ax.vlines(x=bar_right, ymin=bar_y-end_tick_len, ymax=bar_y+end_tick_len,
              colors=tick_color, linewidth=1.8, zorder=2)

    # 눈금 (segments 등분)
    for i in range(1, segments):
        x = bar_left + (bar_right - bar_left) * (i / segments)
        ax.vlines(x=x, ymin=bar_y-mid_tick_len, ymax=bar_y+mid_tick_len,
                  colors=tick_color, linewidth=1.2, zorder=2)

    # 좌/우 라벨
    # 왼쪽: 텍스트 오른쪽 정렬(ha='right')로 바 왼쪽 밖에 붙임
    ax.text(bar_left - outside_gap, bar_y+0.10, "최하위",
            ha="right", va="center", fontsize=12, color=label_color)
    ax.text(bar_left - outside_gap, bar_y-0.14, f"{min_v:,.0f}원",
            ha="right", va="center", fontsize=12, color=label_color)

    # 오른쪽: 텍스트 왼쪽 정렬(ha='left')로 바 오른쪽 밖에 붙임
    ax.text(bar_right + outside_gap, bar_y+0.10, "최상위",
            ha="left", va="center", fontsize=12, color=label_color)
    ax.text(bar_right + outside_gap, bar_y-0.14, f"{max_v:,.0f}원",
            ha="left", va="center", fontsize=12, color=label_color)

    # 현재 값 위치
    frac = max(0.0, min(1.0, (cur_v - min_v) / span))
    x_cur = bar_left + (bar_right - bar_left) * frac

    # 삼각형 마커
    ax.plot([x_cur], [bar_y+0.02], marker="v", markersize=10,
            color=marker_color, zorder=3)

    # "내 위치 : …원" (바 아래)
    ax.text(x_cur, bar_y-0.26, f"내 위치 : {cur_v:,.0f}원",
            ha="center", va="center", fontsize=12, color=marker_color)

    # 저장 → base64
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches=None, pad_inches=0.05, facecolor=bg)
    buf.seek(0)
    img64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return img64


# ----------------- 화면 출력 예시 -----------------
st.markdown("### 📍 나의 경제운전 위치(인센티브 기준)", unsafe_allow_html=True)

# 1) 인천시 전체 운전자 중 (예: 최하위 1,000원, 최상위 100,000원, 내 위치 20,000원)
img_city = draw_rank_bar(min_value=1_000, max_value=100_000, current_value=20_000)

st.markdown("<div style='font-weight:700; font-size:18px;'>▼ 인천시 전체 운전자 중</div>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{img_city}' style='width:100%; max-width:560px;'></div>", unsafe_allow_html=True)

# 2) 운수사 전체 운전자 중 (예: 최하위 1,000원, 최상위 80,000원, 내 위치 20,000원)
img_company = draw_rank_bar(min_value=1_000, max_value=80_000, current_value=20_000)

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='font-weight:700; font-size:18px;'>▼ 운수사 전체 운전자 중</div>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{img_company}' style='width:100%; max-width:560px;'></div>", unsafe_allow_html=True)

# 3) 동일노선 운전자 중 (예: 최하위 10,000원, 최상위 60,000원, 내 위치 20,000원)
img_route = draw_rank_bar(min_value=10_000, max_value=60_000, current_value=20_000)

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='font-weight:700; font-size:18px;'>▼ 동일노선 운전자 중</div>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{img_route}' style='width:100%; max-width:560px;'></div>", unsafe_allow_html=True)


# 노선 순위 참고
st.markdown("""
<div class='line-grade'>
    <b>📌 참고)</b> 노선별 순위 >> <b>302번 노선: 54위</b> (인천 전체 540개 노선 중)
</div>
""", unsafe_allow_html=True)

st.markdown("---")


st.markdown("""
<h3>📍 항목별 경제운전 위치</h3>
""", unsafe_allow_html=True)

metrics = [
    {"name": "달성률", "my": 90, "prev": 85, "avg": 85, "min": 60, "max": 130, "reverse": False},
    {"name": "공회전율", "my": 20, "prev": 30, "avg": 25, "min": 10, "max": 50, "reverse": True},
    {"name": "평균속도", "my": 26, "prev": 28, "avg": 25, "min": 10, "max": 60, "reverse": False}
]

fig, axes = plt.subplots(nrows=len(metrics), figsize=(5, 5))
# fig, axes = plt.subplots(len(metrics), 1, figsize=(5, 3), constrained_layout=True) * len(metrics)

for i, metric in enumerate(metrics):
    ax = axes[i]

    min_val = metric['min']
    max_val = metric['max']

    # 여백 비율
    margin_ratio = 0.05
    plot_min = min_val - (max_val - min_val) * margin_ratio
    plot_max = max_val + (max_val - min_val) * margin_ratio

    # 좋음/나쁨 위치 계산
    if metric['reverse']:  # 공회전율
        bad_side = max_val
        good_side = min_val
    else:  # 달성률, 평균속도
        bad_side = min_val
        good_side = max_val

    # 표시
    ax.axvline(metric['my'], color='red', label='나의 위치', linewidth=2)
    ax.axvline(metric['prev'], color='black', linestyle='--', label='전달 나의 위치')
    ax.axvspan(metric['avg'] - 2, metric['avg'] + 2, color='lightgreen', label='전체 평균')

    ax.set_xlim(plot_min, plot_max)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_title(metric['name'], fontsize=10, pad=15)

    # 나쁨 / 좋음 표 밖 표시
    gap_factor = 0.07  # 커질수록 더 멀리
    if metric['reverse']:  # 공회전율: 작을수록 좋음
        ax.text(max_val + (max_val - min_val) * gap_factor, 0.5, '나쁨', ha='left', va='center', fontsize=10, color='red', fontweight='bold', rotation=90)
        ax.text(min_val - (max_val - min_val) * gap_factor, 0.5, '좋음', ha='right', va='center', fontsize=10, color='blue', fontweight='bold', rotation=90)
    else:  # 달성률, 평균속도
        ax.text(min_val - (max_val - min_val) * gap_factor, 0.5, '나쁨', ha='right', va='center', fontsize=10, color='red', fontweight='bold', rotation=90)
        ax.text(max_val + (max_val - min_val) * gap_factor, 0.5, '좋음', ha='left', va='center', fontsize=10, color='blue', fontweight='bold', rotation=90)

    # 범례는 첫 번째 그래프에만
    if i == 0:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.9), ncol=3, fontsize=8, frameon=False)
    else:
        ax.legend().remove()

plt.tight_layout()
st.pyplot(fig)

st.markdown("---")  # 구분선

# 개인별 성과금(충남고려)
st.markdown("""
<h3>나의 성과와 보상 (충남고속 대상)</h3>
""", unsafe_allow_html=True)

html = dedent("""
<div style="border:1px solid #ddd; padding:20px; border-radius:10px; background-color:#f9f9f9; margin-top:30px;">
  <h4 style="margin:0 0 8px 0;">1. 나의 보상</h4>
  <ul style="line-height:1.8; background-color:yellow; list-style-type:none; padding-left:0; font-size:20px;">
    <li>나의 리워드 보상: <b>1,000원</b> <span style="color:gray;">(예상)</span></li>
  </ul>

  <h4 style="margin:16px 0 8px 0;">2. 나의 성과</h4>
  <ul style="line-height:1.8; list-style-type:none; padding-left:0; font-size:16px;">
    <li>연료절감액: <b>65,000원</b></li>
    <li>온실가스 배출량 감소: <b>00톤 CO₂</b><br/>
      <span style="color:gray;">(🌳 나무 100그루 심는 효과)</span>
    </li>
    <li>사고위험감소: <b>00% 감소</b></li>
  </ul>
</div>
""")

st.markdown(html, unsafe_allow_html=True)

st.markdown("---")  # 구분선

# ✨ 슬로건
st.markdown("""
<div style='text-align: center; font-size: 20px; font-weight: bold; color: #2E7D32;'>
    🌿 오늘도 경제운전, 내일은 더 안전하게! 🌿
</div>
""", unsafe_allow_html=True)

# ▶️ 교육 영상 버튼
st.markdown("""
<div style='text-align: center; margin-top: 20px;'>
    <a href='https://www.youtube.com/watch?v=tIJCvwWXGpE' target='_blank'>
        <button style='padding: 10px 25px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 8px; cursor: pointer;'>
            🎥 교육 동영상 보러가기
        </button>
    </a>
</div>
""", unsafe_allow_html=True)
