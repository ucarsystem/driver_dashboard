import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import io
import base64
import requests
import numpy as np
from PIL import Image, ImageOps
import math
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
# 각 파일 위치
company_file = os.path.join(file_dir, "company_info.xlsx")
id_check_file = os.path.join(file_dir, "인천ID.xlsx")
main_path = os.path.join(file_dir, "인천 운전자별.xlsx")
day_path = os.path.join(file_dir, "인천 일별데이터.xlsx")
car_path = os.path.join(file_dir, "인천 차량별.xlsx")

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

# ── 엑셀 로드 & 필터
df_driver = load_excel(main_path, "운전자별")
df_day = load_excel(day_path, "일별)차량+운전자")
df_car = load_excel(car_path, "차량별데이터")

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

# 운수사 선택박스
company_list = ["운수사를 선택하세요"] + company_list[1:]
company_input = st.selectbox(
    "운수사를 입력하세요",
    options=company_list,
    index=0  # 기본으로 안내 문구 선택되게
)

# 운전자ID 입력칸
user_id_input = st.text_input("운전자 ID를 입력하세요", value=st.session_state.get("user_id_input", ""))

# 조회할 년월 
year_month = "2508" 

# '조회하기' 버튼 눌렀을때만 데이터 조회되게끔 하기위해
조회버튼_클릭 = st.button("조회하기")


if 조회버튼_클릭 :
    if not user_id_input.strip():
        st.warning("운전자 ID를 입력해주세요.")
    else:
        try:
            user_id = int(user_id_input)
        except ValueError:
            st.warning("운전자 ID는 숫자여야 합니다.")

        else:
            # 필터링 실행
            filtered = df_driver[
                (df_driver["운수사"] == company_input) &
                (df_driver["운전자ID"] == user_id) &
                (df_driver["년월"] == int(year_month))
            ]

            # 조회 결과
            st.write("필터링 결과:")

            if filtered.empty:
                st.warning("조건에 맞는 데이터가 없습니다.")
            else:
                row = filtered.iloc[0]
                st.success(f"✅ {company_input} 운수사, ID {user_id_input} 데이터 조회 완료")

                st.markdown("---")

                #값 정의
                route_number = row['노선번호']         # 1) 상단 표: 노선번호
                this_grade = row['등급']              # 2) 진행링: 등급
                this_percent = int(row['가중달성율']*100)        # 2) 진행링: 달성률

                # 제목
                st.markdown("""
                <h2 style='text-align: center;'>나의 ECO 주행성과, 이번 달엔 어땠을까요?</h2>
                """, unsafe_allow_html=True)

                st.markdown("---")


                # 기본 정보

                #왼쪽: 이름/ID / 가운데: 등급 원형 / 오른쪽: 달성율
                st.markdown(f"""
                <table style='width: 100%; table-layout: fixed; text-align: center; font-size: 16px; border-collapse: collapse; border: none;'>
                <tr>
                    <td><b>사원ID</b><br>{user_id_input}님</td>
                    <td><b>소속운수사</b><br>{company_input}</td>
                    <td><b>노선</b><br>{route_number}번</td>
                </tr>
                </table>
                """, unsafe_allow_html=True)

                @st.cache_data(show_spinner=False)
                def draw_grade_progress_ring_base64(
                    grade,               # 등급
                    achieved_pct,         # 현재 달성률(%)
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
                    
                    """
                    등급에 따라 링 색상, 라벨 텍스트 다르게 표시
                    """
                    # --- 1. 등급별 링 색상 ---
                    color_map = {
                        "S": "#2e7d32",  # 녹색
                        "A": "#2e7d32",  # 녹색
                        "B": "#1F4AA0",  # 남색
                        "C": "#1F4AA0",  # 남색
                        "D": "#CA0000",  # 적색
                        "F": "#CA0000",  # 적색
                    }
                    prog_color = color_map.get(str(grade).upper(), "#2e7d32")

                    # --- 2. 등급별 라벨 ---
                    label_map = {
                        "S": "최우수",
                        "A": "우수",
                        "B": "양호",
                        "C": "중립",
                        "D": "노력",
                        "F": "초보",
                    }
                    label = label_map.get(str(grade).upper(), "")


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
                    prog_wedge = patches.Wedge((cx, cy), r, -90, -90+angle, width=r-inner_r,
                                            facecolor=prog_color, linewidth=0, antialiased=True)
                    ax.add_patch(prog_wedge)

                    # --- 텍스트: 등급(녹색), 나머지 검정 ---
                    text_color = "#000000"      # 검정

                    ax.text(cx, cy + r*0.46, f"{grade}등급({label})",
                            ha="center", va="center", fontsize=18,
                            color=prog_color, fontweight="bold")

                    ax.text(cx, cy, f"{int(round(value))}%",
                            ha="center", va="center", fontsize=54,
                            color=text_color, fontweight="bold")

                    ax.text(cx, cy - r*0.40, "예상 월 인센티브",
                            ha="center", va="center", fontsize=14, color=text_color)

                    ax.text(cx, cy - r*0.60, f"{int(incentive_won):,}원",
                            ha="center", va="center", fontsize=24, color=text_color, fontweight="bold")


                    # 투명 배경 PNG → base64
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches=None, transparent=True)
                    buf.seek(0)
                    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
                    plt.close(fig)
                    return image_base64


                # --- 여기서부터는 페이지에 출력하는 부분 (기존 테이블 레이아웃 유지) ---

                # 값정의
                grade = this_grade
                achieved_pct = this_percent   # 현재 달성률
                max_pct = 120       # 총 120%를 링 100%로 간주
                incentive_won = 280000 # 인센티브 금액 (추후 변경)

                # 다음 등급 달성까지 안내문구 함수
                def get_notice_text(grade, achieved_pct):
                    g = str(grade).upper()
                    if g == "S":
                        return "*S등급 달성중입니다. 이대로 경제운전 달인이 되어주세요!"
                    elif g == "A":
                        return f"*다음 S등급까지 {100 - achieved_pct:.0f}% 남았습니다."
                    elif g == "B":
                        return f"*다음 A등급까지 {95 - achieved_pct:.0f}% 남았습니다."
                    elif g == "C":
                        return f"*다음 B등급까지 {90 - achieved_pct:.0f}% 남았습니다."
                    elif g in ["D", "F"]:
                        return f"*C등급까지 {85 - achieved_pct:.0f}% 남았습니다."
                    else:
                        return ""

                notice_text = get_notice_text(this_grade, this_percent)

                circle_base64 = draw_grade_progress_ring_base64(
                    grade=grade, achieved_pct=achieved_pct,
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

                ##일별/월별 달성률 팝업

                #월별 달성률 및 등급

                df_monthly = df_driver[
                (df_driver['운수사'] == company_input) &
                (df_driver['운전자ID'] == int(user_id_input)) &
                (df_driver['등급'] != "이상")
            ]

                # 결과 데이터 가공
                df_result = df_monthly[['년월', '가중달성율', '등급']].copy()

                # 안전하게 숫자 변환 (NaN이 있는 경우에도 오류 발생 안 함)
                df_result['년월'] = pd.to_numeric(df_result['년월'], errors='coerce')
                # NaN 값 제거
                df_result = df_result.dropna(subset=['년월'])
                # 월 추출 후 "월" 붙이기
                df_result['월'] = df_result['년월'].astype(int).astype(str).str[-2:] + "월"
                df_result['달성률'] = (df_result['가중달성율']*100).astype(int)

                # 최종 출력 컬럼 순서
                df_result = df_result[['월', '달성률', '등급']]

                # Altair용 등급 색상 매핑
                등급색상 = alt.Scale(
                    domain=["S", "A", "B", "C", "D", "F"],
                    range=["#0a860a", "#0a860a", "#007bff", "#007bff", "#CA0000", "#CA0000"]
                )

                with st.expander("📊 월별 달성률 보기", expanded=True):

                    # 막대 차트
                    bar = alt.Chart(df_result).mark_bar().encode(
                        x=alt.X("월", title="월", axis=alt.Axis(labelAngle=0)),  # ⬅️ 제목 명시!
                        y=alt.Y("달성률", scale=alt.Scale(domain=[0, 120]), title="달성률"),
                        color=alt.Color("등급", scale=등급색상),
                        tooltip=["월", "달성률", "등급"]
                    )

                    text = alt.Chart(df_result).mark_text(
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

                def generate_calendar_html_v2(data, year, month):
                    # 요일 색상 및 스타일 설정
                    day_color = {0: "red", 6: "blue"}  # 일요일, 토요일
                    grade_color = {
                        "S": "#0a860a",  # 초록
                        "A": "#0a860a",  # 초록
                        "B": "#007bff",  # 파랑
                        "C": "#007bff",  # 파랑
                        "D": "#CA0000",  # 빨강
                        "F": "#CA0000",  # 빨강
                    }

                    # 테이블 헤더
                    html = [f"""
                    <style>
                    .calendar-container {{
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        padding: 10px;
                        background-color: white;
                        overflow-x: auto;  /* 모바일 가로 스크롤 대비 */
                    }}
                    table.calendar {{
                        border-collapse: collapse;
                        width: 100%;
                        table-layout: fixed;  /* 💡 균일한 열 폭 보장 */
                        text-align: center;
                        font-size: 16px;
                    }}
                    table.calendar th {{
                        padding: 6px;
                        background-color: #f5f5f5;
                        font-size: 16px;
                    }}
                    table.calendar td {{
                        padding: 8px 4px;
                        height: 85px;
                        vertical-align: top;
                        word-wrap: break-word;
                    }}
                    @media (max-width: 480px) {{
                        table.calendar {{
                            font-size: 13px;
                        }}
                        table.calendar td {{
                            padding: 6px 2px;
                            height: 75px;
                        }}
                    }}
                    </style>
                    <div class="calendar-container">
                    <table class="calendar">
                        <thead>
                            <tr>
                                <th style='color:red;'>일</th>
                                <th>월</th>
                                <th>화</th>
                                <th>수</th>
                                <th>목</th>
                                <th>금</th>
                                <th style='color:blue;'>토</th>
                            </tr>
                        </thead>
                        <tbody>
                    """]

                    cal = calendar.Calendar(firstweekday=6)  # 일요일 시작
                    month_days = cal.monthdayscalendar(year, month)

                    for week in month_days:
                        html.append("<tr>")
                        for i, day in enumerate(week):
                            color = day_color.get(i, "black")
                            td_style = f"color:{color}; border:1px solid #eee; vertical-align:top;"

                            if day == 0:
                                html.append(f'<td style="{td_style}"></td>')
                            else:
                                if day in data:
                                    g = data[day]["grade"]
                                    p = data[day]["percent"]
                                    c = grade_color.get(g, "black")
                                    html.append(
                                        f'<td style="{td_style}">'
                                        f'<div style="font-weight:bold;">{day}</div>'
                                        f'<div style="font-weight:bold; font-size:12px; color:{c}">{g}등급</div>'
                                        f'<div style="font-size:13px; margin-top:2px; color:{c}">({p}%)</div>'
                                        f'</td>'
                                    )
                                else:
                                    html.append(
                                        f'<td style="{td_style}">'
                                        f'<div style="font-weight:bold;">{day}</div>'
                                        f'</td>'
                                    )
                        html.append("</tr>")
                    html.append("</tbody></table></div>")
                    return "".join(html)
                    
                def calc_grade(percent):
                    if percent >= 100:
                        return "S"
                    elif percent >= 95:
                        return "A"
                    elif percent >= 90:
                        return "B"
                    elif percent >= 85:
                        return "C"
                    elif percent >= 80:
                        return "D"
                    else:
                        return "F"
                    
                #월
                month_int = int(year_month[-2:])

                #조건 필터링
                day_filtered = df_day[
                    (df_day["운수사"] == company_input) &
                    (df_day["운전자ID"] == user_id) &
                    (df_day["월"] == month_int) &
                    (df_day["최종평가"] == "최종")
                ]

                # ✅ 일자별 가중평균달성율 합산
                day_grouped = day_filtered.groupby("일")["가중평균달성율"].sum().reset_index()
                day_grouped["일"] = day_grouped["일"].astype(int)
                day_grouped["달성률"] = (day_grouped["가중평균달성율"] * 100).astype(int)
                day_grouped["등급"] = day_grouped["달성률"].apply(calc_grade)

                # ✅ calendar_data 생성
                calendar_data = {
                    row["일"]: {
                        "grade": row["등급"],
                        "percent": row["달성률"]
                    }
                    for _, row in day_grouped.iterrows()}

                calendar_html = generate_calendar_html_v2(calendar_data, 2025, month_int)

                with st.expander(f"📅 {month_int}월 일별 달성률 보기", expanded=True):
                    st.markdown(calendar_html, unsafe_allow_html=True)

                st.markdown("---")

                ### 인센티브 바그래프 ###

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

                st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center; font-weight:700; font-size:20px;'>- 인천시 전체 운전자 중 -</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{img_city}' style='width:100%; max-width:560px;'></div>", unsafe_allow_html=True)

                # 2) 운수사 전체 운전자 중 (예: 최하위 1,000원, 최상위 80,000원, 내 위치 20,000원)
                img_company = draw_rank_bar(min_value=1_000, max_value=80_000, current_value=20_000)

                st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center; font-weight:700; font-size:20px;'>- 운수사 전체 운전자 중 -</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{img_company}' style='width:100%; max-width:560px;'></div>", unsafe_allow_html=True)

                # 3) 동일노선 운전자 중 (예: 최하위 10,000원, 최상위 60,000원, 내 위치 20,000원)
                img_route = draw_rank_bar(min_value=10_000, max_value=60_000, current_value=20_000)

                st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center; font-weight:700; font-size:20px;'>- 동일노선 운전자 중 -</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{img_route}' style='width:100%; max-width:560px;'></div>", unsafe_allow_html=True)

                # 노선 순위 추출 (인천 차량별.xlsx 데이터 사용>df_car)
                # 1. 조건 정의 (참고용)
                # int(year_month) # 년월
                # company_input #운수사
                # route_number # 주노선

                # 2. 노선별 가중달성률 합산 및 순위 계산
                route_rank_df = (
                    df_car[df_car["년월"] == int(year_month)]
                    .groupby(["년월", "운수사", "노선번호"])["노선내가중달성률"]
                    .sum()
                    .reset_index()
                    .sort_values(by="노선내가중달성률", ascending=False)
                )

                # 3. 순위 부여 (1위가 가장 높은 달성률)
                route_rank_df["순위"] = route_rank_df["노선내가중달성률"].rank(method="min", ascending=False).astype(int)

                # 4. 전체 노선 개수
                total_routes = route_rank_df.shape[0]

                # 5. 해당 운수사의 특정 노선 찾기
                target_row = route_rank_df[
                    (route_rank_df["운수사"] == company_input) &
                    (route_rank_df["노선번호"] == route_number)
                ]

                # 6. 결과 텍스트 생성
                if not target_row.empty:
                    this_rank = target_row.iloc[0]["순위"]
                    markdown_text = f"""
                    <div class='line-grade'>
                        <b>📌 참고)</b> 노선별 순위 >> <b>{route_number}번 노선: {this_rank}위</b> (인천 전체 {total_routes}개 노선 중)
                    </div>
                    """
                    st.markdown(markdown_text, unsafe_allow_html=True)
                else:
                    st.markdown("")

                st.markdown("---")

                ### 항목별 위치 ###
                st.markdown("### 📍 항목별 위치", unsafe_allow_html=True)

                # --- 퍼센트 전용 바그래프(좌: 최하위/우: 최상위) ---
                @st.cache_data(show_spinner=False)
                def draw_rank_bar_pct(
                    value_pct: float,                # 내 위치(%)
                    min_pct: float = 0.0,
                    max_pct: float = 100.0,
                    width=6.0, height=1.10, dpi=220,
                    bar_left=0.12, bar_right=0.88, bar_y=0.55,
                    segments=6,
                    line_color="#9AA3AB",            # 점선 색
                    tick_color="#9AA3AB",            # 눈금 색
                    left_label_color="#E53935",      # 최하위(빨강)
                    right_label_color="#1F4AA0",     # 최상위(파랑)
                    marker_color="#1F4AA0",          # 삼각형/내 위치 텍스트
                    text_color="#2B2F33",
                    bg="white",
                    outside_gap=0.02,                # 바와 라벨 간격
                    end_tick_len=0.085,              # 양끝 긴 눈금 길이
                    mid_tick_len=0.032,              # 중간 눈금 길이
                    pad_x=0.07                       # 좌우 여백(텍스트 잘림 방지)
                ):
                    mn, mx = float(min_pct), float(max_pct)
                    v = float(value_pct)
                    span = max(mx - mn, 1e-6)
                    frac = max(0.0, min(1.0, (v - mn) / span))
                    x_cur = bar_left + (bar_right - bar_left) * frac

                    fig = plt.figure(figsize=(width, height), dpi=dpi, facecolor=bg)
                    ax = fig.add_axes([0, 0, 1, 1], facecolor=bg)
                    ax.set_xlim(-pad_x, 1 + pad_x); ax.set_ylim(0, 1); ax.axis("off")

                    # 점선 바
                    ax.hlines(bar_y, bar_left, bar_right, colors=line_color,
                            linestyles=(0, (6, 6)), linewidth=2.0, zorder=1)

                    # 양끝 긴 눈금
                    ax.vlines(bar_left,  bar_y-end_tick_len, bar_y+end_tick_len, colors=tick_color, linewidth=1.8, zorder=2)
                    ax.vlines(bar_right, bar_y-end_tick_len, bar_y+end_tick_len, colors=tick_color, linewidth=1.8, zorder=2)

                    # 중간 눈금
                    for i in range(1, segments):
                        x = bar_left + (bar_right - bar_left) * (i / segments)
                        ax.vlines(x, bar_y-mid_tick_len, bar_y+mid_tick_len, colors=tick_color, linewidth=1.2, zorder=2)

                    # 좌/우 라벨(바 밖)
                    ax.text(bar_left - outside_gap,  bar_y+0.10, "최하위", ha="right", va="center", fontsize=12, color=left_label_color)
                    ax.text(bar_right + outside_gap, bar_y+0.10, "최상위", ha="left",  va="center", fontsize=12, color=right_label_color)

                    # 내 위치 마커/텍스트
                    ax.plot([x_cur], [bar_y+0.02], marker="v", markersize=10, color=marker_color, zorder=3)
                    ax.text(x_cur, bar_y-0.26, f"내 위치 ({int(round(v))}%)", ha="center", va="center",
                            fontsize=12, color=marker_color)

                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches=None, pad_inches=0.05, facecolor=bg)
                    buf.seek(0)
                    img64 = base64.b64encode(buf.read()).decode("utf-8")
                    plt.close(fig)
                    return img64
                

                # 데이터 정의 (인천 운전자별.xlsx의 운전자별 시트)
                
                # 1) 사용할 컬럼들 정의

                metric_map = {
                    "웜업비율(%)": "월업(관리, 환경)",
                    "공회전비율(%)": "공회전(관리, 환경)",
                    "급가속(회)/100km": "급가속(안전, 경제)",
                    "급감속(회)/100km": "급감속(안전, 경제)"
                    # ,
                    # "평균속도": "평균속도(안전, 경제)" # 평균속도 최상위,최하위 기준 정하면 추가하기
                }

                # 2) 데이터 정의
                # 월별 데이터(전체 운전자별 항목별 비율 구하기위한 데이터)
                month_data = df_driver[df_driver["년월"] == int(year_month)].copy()

                # 오류 방지를 위해 문자열 -> 숫자변환
                for col in metric_map.keys():
                    month_data[col] = pd.to_numeric(month_data[col], errors='coerce')

                # 내 데이터
                my_row = month_data[
                    (month_data["운수사"] == company_input) &
                    (month_data["운전자ID"] == user_id)]
                
                
                # 3) 백분율 계산 함수 (값이 낮을수록 우수 → 높은 퍼센트)
                def get_percentile_reversed(df, col, value):
                    df_sorted = df[col].dropna().sort_values().reset_index(drop=True)
                    total = len(df_sorted)
                    if total == 0:
                        return None # 비교 대상 없음
                    rank = (df_sorted > value).sum() + 1
                    percentile = round(rank / total * 100)
                    return percentile
                
                # 4) 결과 추출
                items = []

                if not my_row.empty:
                    for col, label in metric_map.items():
                        try:
                            val = float(my_row.iloc[0][col])  # .iloc[0]로 Series 에러 방지
                            percentile = get_percentile_reversed(month_data, col, val)
                            if percentile is not None:
                                items.append((label, percentile))
                            else:
                                items.append((label, "-"))  # 데이터가 없는 경우
                        except Exception as e:
                            items.append((label, "-"))  # 에러 처리 (예: NaN 등)

                # 최종 출력 (제목, 바그래프)
                for idx, (title, pct) in enumerate(items):
                    # 제목(가운데 정렬, 굵게)
                    st.markdown(f"<div style='text-align:center; font-weight:700; font-size:20px;'>{title}</div>", unsafe_allow_html=True)

                    # 바그래프
                    img64 = draw_rank_bar_pct(pct, min_pct=0, max_pct=100)
                    st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{img64}' style='width:100%; max-width:560px;'></div>", unsafe_allow_html=True)

                    # 항목 사이 구분선
                    if idx < len(items) - 1:
                        st.markdown("<hr style='border:0; border-top:1px solid #d9dbe0; margin:8px 0 14px 0;'>", unsafe_allow_html=True)




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
