import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import requests
import numpy as np

import matplotlib as mpl 
import matplotlib.pyplot as plt 
import matplotlib.font_manager as fm  
import matplotlib.ticker as ticker
from openpyxl import load_workbook

# 한글 폰트 설정
font_path = "./malgun.ttf"  # 또는 절대 경로로 설정 (예: C:/install/FINAL_APP/dashboard/malgun.ttf)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# 기본 경로 설정
file_dir = "./file"
file_url_template = "https://github.com/ucarsystem/driver_dashboard/file/인천%20개인별%20대시보드_{year}년{month}월.xlsx"

# 엑셀 파일 로드 함수
def load_excel(path):
    try:
        return pd.read_excel(path, sheet_name="매크로(운전자리스트)")
    except Exception as e:
        st.error(f"엑셀 파일 로드 오류: {e}")
        return None
    
    
# 📂 운수사 목록 불러오기
company_file = os.path.join(file_dir, "company_info.xlsx")
df_company = pd.read_excel(company_file, sheet_name="Sheet1", header=None) if os.path.exists(company_file) else pd.DataFrame()
company_list = df_company[0].dropna().tolist() if not df_company.empty else []
df_code = pd.read_excel(company_file, sheet_name="code") if os.path.exists(company_file) else pd.DataFrame()


# Streamlit UI 구성
st.title("🚗 운전자별 대시보드")
company_input = st.selectbox("운수사를 입력하세요", options=company_list, index=None)

user_id_input = st.text_input("운전자 ID를 입력하세요")
st.markdown("""
    <a href='https://driverid-xgkps9rbvh4iph8yrcvovb.streamlit.app/' target='_blank' 
    style='display: inline-block; padding: 10px 20px; background-color: green; color: white; font-weight: bold; 
    text-align: center; text-decoration: none; border-radius: 5px;'>내 ID를 모른다면? >> ID 조회하기</a>
""", unsafe_allow_html=True)
user_name_input = st.text_input("운전자 이름을 입력하세요")

year_input = st.text_input("년도를 입력하세요 (예: 25)")
month_input = st.text_input("월을 입력하세요 (예: 02)").zfill(2)


if st.button("조회하기") and company_input and user_id_input and user_name_input and year_input and month_input:
    file_name = f"인천 개인별 대시보드_{year_input}년{month_input}월.xlsx"
    file_path = os.path.join(file_dir, file_name)

    df = load_excel(file_path)

    # 조건 필터링
    filtered = df[
        (df["운수사"] == company_input) &
        (df["운전자이름"] == user_name_input) &
        (df["운전자ID"].astype(str) == user_id_input)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.success(f"✅ 운전자 {user_name_input} (ID: {user_id_input}) 정보 조회 성공")

        st.markdown("---")
        grade_color = {"S": "🟩", "A": "🟩", "B": "🟨", "C": "🟨", "D": "🟥", "F": "🟥"}
        grade = row["2502"]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("이달의 등급", f"{grade_color.get(grade, '')} {grade}")
        col2.metric("달성률", f"{round(row['이번달달성율'] * 100)}%")
        col3.metric("공회전", f"{round(row["이번달공회전비율(%)"] * 100)}%")
        col4.metric("급감속", f"{round(row['이번달급감속(회)/100km'], 2)}")

        compare_df = pd.DataFrame({
            "지표": ["달성률", "웜업률", "공회전률", "급감속"],
            "이달": [
                f"{round(row['이번달달성율'] * 100)}%",
                f"{round(row['이번달웜업비율(%)'] * 100, 1)}%",
                f"{round(row['이번달공회전비율(%)'] * 100, 1)}%",
                f"{round(row['이번달급감속(회)/100km'], 1)}%"
            ],
            "전월": [
                f"{round(row['전월달성율'] * 100)}%",
                f"{round(row['전월웜업비율(%)'] * 100, 1)}%",
                f"{round(row['전월공회전비율(%)'] * 100, 1)}%",
                f"{round(row['전월급감속(회)/100km'], 2)}%"
            ],  # 예시값
            "노선 평균": [
                f"{round(row['노선평균달성율'] * 100)}%",
                f"{round(row['노선평균웜업비율(%)'] * 100, 1)}%",
                f"{round(row['노선평균공회전비율(%)'] * 100, 1)}%",
                f"{round(row['노선평균급감속(회)/100km'], 2)}%"
            ],  # 예시값
        })
        st.dataframe(compare_df, hide_index=True)

        st.subheader("📊 이달 vs 노선 평균 그래프")
        labels = [
            "웜업률(%)", "공회전률(%)", "탄력운전률(%)",
            "연료소모율", "급가속(/100km)", "급감속(/100km)"
        ]
        driver_vals = [
            row["이번달웜업비율(%)"] * 100,
            row["이번달공회전비율(%)"] * 100,
            row["이번달탄력운전비율(%)"] * 100,
            row["이번달평균연료소모율"],
            row["이번달급가속(회)/100km"],
            row["이번달급감속(회)/100km"]
        ]
        avg_vals = [
            row["노선평균웜업비율(%)"] * 100,
            row["노선평균공회전비율(%)"] * 100,
            row["노선평균탄력운전비율(%)"] * 100,
            row["노선평균평균연료소모율"],
            row["노선평균급가속(회)/100km"],
            row["노선평균급감속(회)/100km"]
        ]

        fig, ax = plt.subplots(figsize=(8, 5))
        x = range(len(labels))
        ax.barh(x, driver_vals, height=0.4, label='운전자', align='center', color='#4B8BBE')
        ax.barh([i + 0.4 for i in x], avg_vals, height=0.4, label='노선 평균', align='center', color='#FFB347')
        ax.set_yticks([i + 0.2 for i in x])
        ax.set_yticklabels(labels, fontproperties=font_prop)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.invert_yaxis()
        ax.legend(prop=font_prop)
        ax.set_title("이달 수치 vs 노선 평균 비교", fontproperties=font_prop)
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("🗣️ 개인 맞춤 피드백")
        st.info(row["종함평가"])

        # 조건별 자동 피드백 생성
        st.markdown("### 📌 급감속/공회전 분석 피드백")
        break_ = row["이번달급가속(회)/100km"]
        idle = row["이번달공회전비율(%)"] * 100

        feedback_parts = []
        if break_ < row["노선평균급감속(회)/100km"]:
            feedback_parts.append("✅ 급가속 발생이 매우 적어 안전 운전에 기여하고 있습니다.")
        elif break_ < 80:
            feedback_parts.append("🟡 급가속이 다소 발생하고 있습니다. 부드러운 가속을 더 의식해 주세요.")
        else:
            feedback_parts.append("⚠️ 급가속 빈도가 높습니다. 정속 주행을 통해 안전·연비 개선이 필요합니다.")

        if idle > row["노선평균공회전비율(%)"]*100:
            feedback_parts.append("⚠️ 공회전 비율이 높습니다. 정차 시 시동 관리에 유의해 주세요.")
        elif idle > 40:
            feedback_parts.append("🟡 공회전이 평균보다 다소 높습니다. 불필요한 정차를 줄여주세요.")
        else:
            feedback_parts.append("✅ 공회전 관리가 잘 되고 있습니다.")

        st.success("\n".join(feedback_parts))

    else:
            st.warning("데이터를 불러오는 데 실패했습니다.")
else:
    st.warning("운수사, 운전자 ID, 운전자 이름을 입력하세요.")


