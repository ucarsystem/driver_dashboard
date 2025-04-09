import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import requests
import matplotlib.font_manager as fm
import numpy as np

import matplotlib as mpl 
import matplotlib.pyplot as plt 
import matplotlib.font_manager as fm  
from openpyxl import load_workbook


# 기본 경로 설정
file_dir = "./file"
file_url_template = "https://github.com/ucarsystem/driver_dashboard/file/인천%20개인별%20대시보드_{year}년{month}월.xlsx"

# 엑셀 파일 로드 함수
def load_excel(path):
    try:
        return pd.read_excel(path, sheet_name="최종(개인별)", header=None)
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
        grade_color = {"S": "🟪", "A": "🟦", "B": "🟩", "C": "🟨", "D": "🟥", "F": "⬛"}
        grade = row["2502"]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("이달의 등급", f"{grade_color.get(grade, '')} {grade}")
        col2.metric("달성률", f"{round(row['이번달달성율'] * 100)}%")
        col3.metric("연료소모율", f"{round(row['이번달평균연료소모율'], 2)}")
        col4.metric("탄력운전률", f"{round(row['이번달탄력운전비율(%)'] * 100, 1)}%")

        st.markdown("---")
        st.subheader("📊 운전 습관 항목별 비교")
        indicators = {
            "웜업률(%)": row["이번달웜업비율(%)"] * 100,
            "공회전률(%)": row["이번달공회전비율(%)"] * 100,
            "탄력운전률(%)": row["이번달탄력운전비율(%)"] * 100,
            "급가속(/100km)": row["이번달급가속(회)/100km"],
            "급감속(/100km)": row["이번달급감속(회)/100km"],
        }

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(list(indicators.keys()), list(indicators.values()), color='skyblue')
        ax.set_xlabel('수치')
        ax.set_title('운전자 주요 지표')
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("🗣️ 개인 맞춤 피드백")
        feedback = row["종함평가"]
        st.info(feedback)

    else:
            st.warning("데이터를 불러오는 데 실패했습니다.")
else:
    st.warning("운수사, 운전자 ID, 운전자 이름을 입력하세요.")


