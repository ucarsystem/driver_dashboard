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

# 한글 폰트 설정
font_path = fm.findfont(fm.FontProperties(family='Malgun Gothic'))
font_prop = fm.FontProperties(fname=font_path)
plt.rc('font', family=font_prop.get_name())  # Windows의 경우
plt.rc('axes', unicode_minus=False)


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

    if os.path.exists(file_path):
        df_final = load_excel(file_path)

        if df_final is not None:

            df_final.iloc[5, 33] = company_input  # AH6 운수사
            df_final.iloc[5, 34] = user_id_input  # AI6 운전자id
            df_final.iloc[5, 35] = user_name_input  # AJ6 운전자명

            final_code = f"{company_input}{user_id_input}{user_name_input}" #AK6 운수사&운전자id&운전자명

            # 년월 코드
            this_code = df_final.iloc[2,52] #이번년월
            past_code1 = df_final.iloc[23,50] #저번달년월
            past_code2 = df_final.iloc[22,50] #2달전년월

            user_grade = df_final.iloc[24, 52]

            user_grade = df_final.iloc[11, 33]  # AH12 이달의 등급
            #user_summary = df_final.iloc[5, 4]  # AH16 종합평가
            vehicle_columns = df_final.iloc[17, 39:50].tolist() #차량별 항목별 수치
            vehicle_data = df_final.iloc[18:28, 39:50].copy()
            vehicle_data.columns = vehicle_columns  # AN18:AX28

            route_stats = pd.concat([df_final.iloc[5:7, 40:41], df_final.iloc[5:7, 42:46]], axis=1)  # AN6:AT7
            route_stats.columns = ['달성율', '웜업', '공회전', '급가속', '급감속']

            monthly_comparison = df_final.iloc[10:12, 39:45]  # AN11:AT12
            calendar_data = df_final.iloc[6:16, 51:57]  # AZ7:AF16
            grade_trend = df_final.iloc[22:25, 51:57]  # AZ23:BB25

            #운수사코드.운수사
            code_row = df_code[df_code["운수사"] == company_input]
            code_company = code_row.iloc[0]["운수사최종코드"] if not code_row.empty else "-"
            # code_company = df_final.iloc[19, 35] #운수사코드.운수사 
    
            st.markdown("<hr style='border:3px solid orange'>", unsafe_allow_html=True)

            # 출력 시작
            col1, col2 = st.columns([1, 3], gap='large')

            with col1 :
                if os.path.exists("프로필.png"):
                    st.image("프로필.png", width=150)
                else:
                    st.image("https://via.placeholder.com/150", width=150)

            with  col2:
                color = "green" if user_grade in ['S', 'A'] else "#003366" if user_grade in ['C', 'D'] else "red"
                st.markdown(f"""
                <div style='font-size: 24px; font-weight: bold;'>
                    <b>{user_name_input}({user_id_input})</b><br>
                    <span style='font-size: 22px;'>소속: <b>{company_input}</b></span><br>
                    <span style='color: {color}; font-size: 60px; font-weight: bold;'>{user_grade}</span><br>
                    <small style='font-size: 20px;'>이달의 등급</small>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # <div>
        #     <b>{user_name_input}({user_id_input})</b><br>
        #     소속: <b>{company_input}</b><br>
        #     <span style='color: {'green' if user_grade in ['S', 'A'] else 'blue' if user_grade in ['C', 'D'] else 'red'}; font-size: 50px; font-weight: bold;'>{user_grade}</span><br>
        #     <small>이달의 등급</small>
        # </div>""", unsafe_allow_html=True) 

            st.markdown("### <📝종합 평가>")
    #st.markdown(f"<p style='font-size: 18px;'>{user_summary}</p>", unsafe_allow_html=True)

            ap11 = df_final.iloc[10, 41]  # AP11(전달등급)
            ap12 = df_final.iloc[11, 41]  # AP12(이번달등급)
            ba5 = df_final.iloc[4, 52]  # BA5(이번달)
            bc5 = df_final.iloc[4, 54]  # BC5(전달)
            ao11 = df_final.iloc[10, 40]  # AO11(전달달성율)
            ao12 = df_final.iloc[11, 40]  # AO12(이번달달성율)
            as11 = df_final.iloc[10, 44]  # AS11(전달급가속)
            as12 = df_final.iloc[11, 44]  # AS12(이번달급가속)
            at11 = df_final.iloc[10, 45]  # AT11(전달급감속)
            at12 = df_final.iloc[11, 45]  # AT12(이번달급감속)

            if ap11 in ['이상', '-']:
                evaluation_text = f"""
                <div>
                <p style='font-size: 15px;'>
                    ● 연비등급: {ba5}월 (<b>{ap12}</b>)등급 <br>
                    ● 목표달성율: {ba5}월 ({round(ao12 * 100, 0)}%) <br>
                    ● 급가속: {ba5}월 ({round(as12, 2)})회/100km당 <br>
                    <b><span style='background-color: yellow;'>● 급감속: {ba5}월 ({round(at12, 2)})회/100km당  </span></b> <br>
                </p>
                </div>"""
            else:
                evaluation_text = f"""
                <div>
                <p style='font-size: 15px;'>
                    ● 연비등급: {bc5}월 (<b>{ap11}</b>)등급 -> {ba5}월 (<b>{ap12}</b>)등급 <br>  
                    ● 목표달성율: {bc5}월 ({round(ao11 * 100, 0)}%) -> {ba5}월 ({round(ao12 * 100, 0)}%)  <br>
                    ● 급가속: {bc5}월 ({round(as11, 2)})회/100km당 -> {ba5}월 ({round(as12, 2)})회/100km당  <br>
                    <b><span style='background-color: yellow;'>● 급감속: {bc5}월 ({round(at11, 2)})회/100km당 -> {ba5}월 ({round(at12, 2)})회/100km당  </span></b><br>
                </p>
                </div>"""
            st.markdown(evaluation_text, unsafe_allow_html=True)
    
            # 추가 조건에 따른 멘트 생성
            grade_target = "C" if ap12 in ["F", "D"] else "B" if ap12 == "C" else "A" if ap12 == "B" else "S"
            grade_color = "green" if grade_target in ["S", "A"] else "blue" if grade_target in ["B", "C"] else "red"

            additional_text = f"""
            <br>
            <p style='font-size: 22px; font-style: italic;'>
            <b>{ba5+1}</b>월에는, <b>급감속</b>을 줄여봅시다.<br>
            급감속은 <b>매탕 1회 미만!</b><br>
            이것만 개선해도 연비 5% 개선, 
            <span style='color: {grade_color}; font-weight: bold;'>{grade_target}등급</span>까지 도달 목표!!
            </p>
            """

    #st.markdown(additional_text, unsafe_allow_html=True) 

            st.markdown(f"""
            <div style='background-color: rgba(211, 211, 211, 0.3); padding: 10px; border-radius: 5px;'>
            {additional_text}
            </div>
            """, unsafe_allow_html=True)
            

            #구분선
            st.markdown("<hr style='border:1px solid #ddd'>", unsafe_allow_html=True)


            st.subheader("🚛 차량별 항목별 수치")
            expected_columns = ["운수사", "노선", "차량번호", "주행거리", "웜업", "공회전", "급가속", "연비", "달성율", "등급"]
                
            vehicle_data = vehicle_data.dropna(how='all').reset_index(drop=True)
            vehicle_data["주행거리"] = vehicle_data["주행거리"].astype(float).apply(lambda x: f"{x:,.0f}")
            vehicle_data["웜업"] = vehicle_data["웜업"].astype(float).apply(lambda x: f"{x:.2f}%")
            vehicle_data["공회전"] = vehicle_data["공회전"].astype(float).apply(lambda x: f"{x:.2f}%")
            vehicle_data["급가속"] = vehicle_data["급가속"].astype(float).apply(lambda x: f"{x:.2f}")
            vehicle_data["급감속"] = vehicle_data["급감속"].astype(float).apply(lambda x: f"{x:.2f}")
            vehicle_data["연비"] = vehicle_data["연비"].astype(float).apply(lambda x: f"{x:.2f}")
            vehicle_data["달성율"] = vehicle_data["달성율"].astype(float).apply(lambda x: f"{x * 100:.0f}%")

            def highlight_grade(val):
                color = "green" if val in ["S", "A"] else "blue" if val in ["C", "D"] else "red"
                return f'color: {color}; font-weight: bold'
            
            st.dataframe(vehicle_data.style.applymap(highlight_grade, subset=["등급"])\
            .applymap(lambda x: 'background-color: yellow' if x else '', subset=['급감속'])\
            .set_table_styles([
                {'selector': 'th', 'props': [('font-weight', 'bold'), ('color', 'black'), ('text-align', 'center')]},
                {'selector': 'td', 'props': [('text-align', 'center')]}
            ]), hide_index=True)

            this_month = int(month_input) #이번달
            past_month1 = 12 if this_month == 1 else this_month - 1 #저번달
            next_month = 1 if this_month == 12 else this_month +1 #다음달
            past_month2 = 12 if past_month1 == 1 else past_month1 - 1 #저번달

            
            st.subheader("📊 노선 내 나의 수치")

        # g1 폴더 내 AK6 이름의 PNG 파일 경로
            image_path = os.path.join("노선내비교", f"{year_input}{month_input}/{code_company}/{user_name_input}({user_id_input}).png")

                # 이미지 불러오기
            if os.path.exists(image_path):
                st.image(image_path, caption=f"{user_name_input}({user_id_input})님의 노선 내 수치", use_container_width=True)
            else:
                st.warning(f"이미지 파일을 찾을 수 없습니다: {image_path}")

            
            st.subheader(f"📉 {past_month1}월 vs {this_month}월 비교")

                # g2 폴더 내 AK6 이름의 PNG 파일 경로
            image_path2 = os.path.join("전월대비", f"{year_input}{month_input}/{code_company}/{user_name_input}({user_id_input}).png")

                # 이미지 불러오기
            if os.path.exists(image_path):
                st.image(image_path2, caption=f"{user_name_input}({user_id_input})님의 전월대비 수치 비교", use_container_width=True)
            else:
                st.warning(f"이미지 파일을 찾을 수 없습니다: {image_path2}")


    
            st.subheader(f"📅 나만의 등급 달력_{this_month}월")

        # g3 폴더 내 AK6 이름의 PNG 파일 경로
            image_path3 = os.path.join("달력이미지", f"{year_input}{month_input}/{code_company}/{user_name_input}({user_id_input}).png")

                # 이미지 불러오기
            if os.path.exists(image_path3):
                st.image(image_path3, caption=f"{user_name_input}({user_id_input})님의 이번달 등급 달력", width=600)
            else:
                st.warning(f"이미지 파일을 찾을 수 없습니다: {image_path3}")
            
            
            st.subheader("📊 월별 등급 추이")

    #값 정의
            past_grade1 = df_final.iloc[10, 41]
            past_grade2 = df_final.iloc[22, 52]
            past_percent2 = f"{round(df_final.iloc[22, 53] * 100)}%" #전전월 달성율
            past_percent1 = f"{round(df_final.iloc[23, 53] * 100)}%" #전월 달성율
            this_percent = f"{round(df_final.iloc[24, 53] * 100)}%" #이번달 달성율

            grade_values = [past_grade2, past_grade1, user_grade]

            #등급별 색깔 함수
            def get_grade_color(grade):
                return "green" if grade in ["S","A"] else "#003366" if grade in ["B", "C"] else "red"


            grade_trend_html = f"""
            <div style='display: flex; align-items: center; justify-content: center; gap: 25px;'>
                <div style='background-color: #E0E0E0; padding: 30px; border-radius: 15px; text-align: center; width: 150px; box-shadow: 3px 3px 5px rgba(0,0,0,0.1);'>
                    <div style='font-size: 18px; font-weight: bold;'>{past_month2}월</div>
                    <div style='font-size: 32px; font-weight: bold; color: {get_grade_color(grade_values[0])};'>{grade_values[0]}</div>
                    <div style='font-size: 18px;'>{past_percent2}</div>
                </div>
                <div style='background-color: #BDBDBD; padding: 30px; border-radius: 15px; text-align: center; width: 150px; box-shadow: 3px 3px 5px rgba(0,0,0,0.1);'>
                    <div style='font-size: 18px; font-weight: bold;'>{past_month1}월</div>
                    <div style='font-size: 32px; font-weight: bold; color: {get_grade_color(grade_values[1])};'>{grade_values[1]}</div>
                    <div style='font-size: 18px;'>{past_percent1}</div>
                </div>
                <div style='background-color: #FFEB3B; padding: 30px; border-radius: 15px; text-align: center; width: 150px; box-shadow: 3px 3px 5px rgba(0,0,0,0.1);'>
                    <div style='font-size: 18px; font-weight: bold;'>{this_month}월</div>
                    <div style='font-size: 32px; font-weight: bold; color: {get_grade_color(grade_values[2])};'>{grade_values[2]}</div>
                    <div style='font-size: 18px;'>{this_percent}</div>
                </div>
            </div>
        """
        st.markdown(grade_trend_html, unsafe_allow_html=True)

        # 추가 간격 적용
        st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    else:
            st.warning("데이터를 불러오는 데 실패했습니다.")
else:
    st.warning("운수사, 운전자 ID, 운전자 이름을 입력하세요.")


