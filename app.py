import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
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
import datetime
import altair as alt

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

#24년 인증제
medal_filepath = os.path.join(file_dir, "인증제.xlsx")
cert_24_all = load_excel(medal_filepath, "24년 명단")
cert_25_all = load_excel(medal_filepath, "25년 명단")


# Streamlit UI 구성🚍
# 제목
st.markdown("""
<h2 style='text-align: center;'>나의 ECO 주행성과, 이번 달엔 어땠을까요?</h1>
""", unsafe_allow_html=True)

# 기본 정보

def draw_grade_circle(grade="A", label="우수", percent="95%"):
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.add_patch(patches.Circle((0.5, 0.5), 0.48, color='green'))
    
    ax.text(0.5, 0.6, f"{grade}등급", ha='center', va='center', fontsize=16, color='white', fontweight='bold')
    ax.text(0.5, 0.4, f"({label})", ha='center', va='center', fontsize=10, color='white')

    ax.axis("off")
    st.pyplot(fig)

#----------------------------예시1----------------------------
#왼쪽: 이름/ID / 가운데: 등급 원형 / 오른쪽: 달성율
col1, col2, col3 = st.columns([1.5, 1.5, 1.5])

with col1:
    st.markdown("**사원ID**<br/>1587님", unsafe_allow_html=True)
with col2:
    st.markdown("**소속운수사**<br/>강화교통", unsafe_allow_html=True)
with col3:
    st.markdown("**노선**<br/>800번", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.5])
with col1:
    draw_grade_circle(grade="A", label="우수", percent="95%")

with col2:
    st.markdown("""
    <div style='line-height: 1.6; font-size: 24x;'>
        <b>달성율</b><br/>
        <span style='font-size: 24px; color: black;'><b>95%</b></span><br/><br/>
        <span style='color: red;'>* 다음 S등급까지 5% 남았습니다.</span><br/>
    </div>
    """, unsafe_allow_html=True)

#----------------------------예시2----------------------------
# st.markdown("""
# <div style='border:1px solid #ccc; border-radius:10px; padding:20px;'>
#     <h2 style='color: green;'>S 등급 <span style='font-size:16px;'>(최우수)</span></h2>
#     <p>달성율: <b>95%</b></p>
#     <p style='color:orange;'>* 다음 S등급까지 5% 남았습니다.</p>
# </div>
# """, unsafe_allow_html=True)
# 참고치 팝업
with st.expander("📌 참고치 보기"):
                st.markdown("""
                **등급 기준표**  
                - S : 95% 이상  
                - A : 90~95%  
                - B : 85~90%  
                - C : 80~85%  
                - D : 75~80%  
                - F : 70~75%
                """)
if "show_graph" not in st.session_state:
    st.session_state.show_graph = False

# if st.button("📊 일별/월별 달성률 보기"):
#     st.session_state.show_graph = not st.session_state.show_graph

# if st.session_state.show_graph:
#     st.markdown("#### 월별 달성률 추이")
#     st.bar_chart([70, 75, 80, 85, 92])  # 예시 데이터

# if st.button("📌 팝업으로 보기"):
#     with st.modal("등급 기준 팝업창"):
#         st.markdown("### 등급별 설명")
#         st.write("- S: 95% 이상\n- A: 90~95% ...")

#일별/월별 달성률 팝업
# 예시 데이터 (월별)
data = pd.DataFrame({
    "월": ["1월", "2월", "3월", "4월", "5월", "6월"],
    "달성률": [81.2, 86.4, 89.1, 91.8, 94.2, 96.7],
    "등급": ["D", "C", "C", "B", "A", "S"]
})

with st.expander("📊 월별 달성률 보기", expanded=False):
    st.subheader("월별 달성률 변화")

    chart = alt.Chart(data).mark_bar().encode(
        x="월",
        y=alt.Y("달성률", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color("등급", scale=alt.Scale(
            domain=["S", "A", "B", "C", "D", "F"],
            range=["#4CAF50", "#8BC34A", "#FFEB3B", "#FFC107", "#FF5722", "#F44336"]
        )),
        tooltip=["월", "달성률", "등급"]
    ).properties(height=300)

    st.altair_chart(chart, use_container_width=True)

# 일별 데이터 팝업
def generate_calendar_html(data, year, month):
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)

    grade_color = {
        "S": "green", "A": "green",
        "B": "orange", "C": "orange",
        "D": "red", "F": "red"
    }

    html = "<table style='border-collapse: collapse; margin: auto;'>"
    html += """
        <tr>
        <th style='color:red'>일</th><th>월</th><th>화</th>
        <th>수</th><th>목</th><th>금</th><th>토</th></tr>
    """

    for week in month_days:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td style='padding:15px;'></td>"
            else:
                grade = data.get(day, "")
                color = grade_color.get(grade, "black")
                html += f"""
                <td style='padding:15px; text-align:center; border:1px solid #ccc'>
                    <div style='font-weight:bold;'>{day}</div>
                    <div style='font-size:24px; color:{color}'>{grade}</div>
                </td>
                """
        html += "</tr>"
    html += "</table>"
    return html
data = {
    1: "A", 2: "B", 3: "C", 4: "A", 5: "S",
    6: "F", 7: "B", 8: "C", 9: "A", 10: "A",
    11: "D", 12: "C", 13: "S", 14: "B", 15: "C"
}
calendar_html = generate_calendar_html(data, 2025, 6)

with st.expander("📅 이번달 일별 달성률 보기"):
    st.markdown(calendar_html, unsafe_allow_html=True)

# 항목별 그래프수치표시
def draw_gauge(my_position, prev_position, avg_position, title):
    labels = ['하위', '40%', '30%', '20%', '10%', '상위']
    x = [0, 1, 2, 3, 4, 5]

    fig, ax = plt.subplots(figsize=(10, 1.5))
    ax.hlines(0, 0, 5, color='lightgray', linewidth=10)
    ax.plot(my_position, 0, marker='^', color='black', markersize=12, label='내 위치')
    ax.plot(prev_position, 0, marker='v', color='gray', markersize=12, label='전달 위치')
    ax.plot(avg_position, 0, marker='o', color='green', markersize=12, label='전체 평균')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_yticks([])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.6), ncol=3)
    ax.set_xlim(-0.5, 5.5)
    ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
    st.markdown(f"#### {title}")
    st.pyplot(fig)


def draw_rank_bar(title, my_percent):
    fig, ax = plt.subplots(figsize=(6, 1.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    ax.hlines(0.5, 0, 100, colors='lightgray')
    
    # 5등분 점선
    for x in [0, 20, 40, 60, 80, 100]:
        ax.vlines(x, 0.45, 0.55, colors='gray', linestyles='dotted')
    
    # 위치 점 표시
    ax.plot(my_percent, 0.5, 'o', color='black', markersize=12)
    
    # 라벨 표시
    ax.text(0, 0.7, '하위', ha='left', va='center', fontsize=10)
    ax.text(100, 0.7, '상위', ha='right', va='center', fontsize=10)
    ax.text(my_percent, 0.2, f"내 위치: {my_percent:.1f}%", ha='center', fontsize=10, color='black')
    
    # 스타일링
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_yticks([])
    ax.set_title(title, fontsize=13)
    ax.axis('off')
    st.pyplot(fig)

st.markdown("### 📍 나의 경제운전 위치(달성율 기준)", unsafe_allow_html=True)

# 예시 값
my_rank_incheon = 30.2  # 인천시 전체 순위 백분율
my_rank_company = 45.0  # 운수사 내 순위 백분율
my_rank_route = 55.0    # 동일노선 내 순위 백분율

draw_rank_bar("▶ 인천시 전체 운전자 중", my_rank_incheon)
draw_rank_bar("▶ 운수사 전체 운전자 중", my_rank_company)
draw_rank_bar("▶ 동일노선 운전자 중", my_rank_route)

# 노선 순위 참고
st.markdown("""
<div style='font-size: 14px; color: gray; margin-top:10px;'>
    <b>📌 참고)</b> 노선별 순위 >> <b>302번 노선:</b> 54위 (인천 전체 540개 노선 중)
</div>
""", unsafe_allow_html=True)

# 경제운전 위치 - 퍼센트 기준 바
st.markdown("""
<h3>📍 항목별 경제운전 위치</h3>
""", unsafe_allow_html=True)

def draw_percent_bar(label, my_percent, prev_percent, avg_percent):
    fig, ax = plt.subplots(figsize=(6, 1))
    ax.set_xlim(0, 100)
    ax.axvline(my_percent, color='red', label='나의 위치')
    ax.axvline(prev_percent, color='black', linestyle='--', label='전달 나의 위치')
    ax.axvline(avg_percent, color='green', linewidth=8, alpha=0.4, label='전체 평균')
    ax.set_yticks([])
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_title(label)
    ax.legend(loc='upper right')
    st.pyplot(fig)

st.markdown("<h4>달성율</h4>", unsafe_allow_html=True)
draw_percent_bar("달성율", my_percent=45, prev_percent=42, avg_percent=50)

st.markdown("<h4>공회전율</h4>", unsafe_allow_html=True)
draw_percent_bar("공회전율", my_percent=20, prev_percent=30, avg_percent=22)

st.markdown("<h4>평균속도</h4>", unsafe_allow_html=True)
draw_percent_bar("평균속도", my_percent=27, prev_percent=25, avg_percent=28)

st.markdown("<h4>급감속</h4>", unsafe_allow_html=True)
draw_percent_bar("급감속", my_percent=30, prev_percent=32, avg_percent=28)

st.markdown("<h4>급가속</h4>", unsafe_allow_html=True)
draw_percent_bar("급가속", my_percent=18, prev_percent=20, avg_percent=15)

st.markdown("<h4>과속</h4>", unsafe_allow_html=True)
draw_percent_bar("과속", my_percent=90, prev_percent=92, avg_percent=88)


# # 예시 호출
# st.markdown("그래프수치표시")
# draw_gauge(my_position=3, prev_position=4, avg_position=2, title="급감속")

