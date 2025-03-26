import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import requests
import matplotlib.font_manager as fm
import numpy as np
import matplotlib as mpl 
import matplotlib.pyplot as plt 

# 한글 폰트 설정
font_path = fm.findfont(fm.FontProperties(family='Malgun Gothic'))
plt.rc('font', family=fm.FontProperties(fname=font_path).get_name())
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

# 운전자 정보 추출 함수
def get_driver_info(path, code, month_code, info):
    try:
        df = pd.read_excel(path, sheet_name="운전자별")
        key = code + str(month_code)
        row = df[df.iloc[:, 1] == key]
        if row.empty:
            return "-"
        col_map = {"달성율": 22, "등급": 23, "웜업": 39, "공회전": 40, "급가속": 43, "급감속": 44}
        return row.iloc[0, col_map.get(info, -1)] if col_map.get(info) else "-"
    except:
        return "-"
    
# 📂 운수사 목록 불러오기
company_file = os.path.join(file_dir, "company_info.xlsx")
df_company = pd.read_excel(company_file, sheet_name="Sheet1", header=None) if os.path.exists(company_file) else pd.DataFrame()
company_list = df_company[0].dropna().tolist() if not df_company.empty else []
df_code = pd.read_excel(company_file, sheet_name="code") if os.path.exists(company_file) else pd.DataFrame()


# Streamlit UI 구성
st.title("🚗 운전자별 대시보드")

#운수사목록
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

            # df_final.iloc[5, 33] = company_input  # AH6 운수사
            # df_final.iloc[5, 34] = user_id_input  # AI6 운전자id
            # df_final.iloc[5, 35] = user_name_input  # AJ6 운전자명
            # 데이터 가져오기 (데이터 정의)
            final_code = f"{company_input}{user_id_input}{user_name_input}" #AK6 운수사&운전자id&운전자명
            df_final.iloc[5, 33:36] = [company_input, user_id_input, user_name_input]

            # 년월 코드
            this_code = df_final.iloc[2,52] #이번년월
            past_code1 = df_final.iloc[23,50] #저번달년월
            past_code2 = df_final.iloc[22,50] #2달전년월

            user_grade = get_driver_info(file_path, final_code, this_code, "등급") #이번달 등급

            #user_grade = df_final.iloc[11, 33]  # AH12 이달의 등급

            #차량+운전자별 시트 (차량별항목별수치)
            df_vehicle = pd.read_excel(file_path, sheet_name = "차량+운전자별", header=None)
            search_key = final_code+str(this_code)
            vehicle_data = df_vehicle[df_vehicle.iloc[:, 37] == search_key].iloc[:, [4,5,6,12,38,39,42,43,14,32,33]].reset_index(drop=True)
            vehicle_columns = df_final.iloc[17, 39:50].tolist() #차량별 항목별 수치
            vehicle_data.columns = vehicle_columns  # AN18:AX28

            # matched_rows = df_vehicle[df_vehicle.iloc[:,37]==search_key]

            # #추출할 열
            # selected_cols = [4,5,6,12,38,39,42,43,14,32,33]

            # # 선택한 열만 추출
            # vehicle_data = matched_rows.iloc[:, selected_cols].reset_index(drop=True)
            # vehicle_columns = df_final.iloc[17, 39:50].tolist() #차량별 항목별 수치

            # vehicle_data = df_final.iloc[18:28, 39:50].copy()
            # vehicle_data.columns = vehicle_columns  # AN18:AX28

            # route_stats = pd.concat([df_final.iloc[5:7, 40:41], df_final.iloc[5:7, 42:46]], axis=1)  # AN6:AT7 노선평균
            # route_stats.columns = ['달성율', '웜업', '공회전', '급가속', '급감속']

            # monthly_comparison = df_final.iloc[10:12, 39:45]  # AN11:AT12 전월비교
            # calendar_data = df_final.iloc[6:16, 51:57]  # AZ7:AF16 달력데이터
            # grade_trend = df_final.iloc[22:25, 51:57]  # AZ23:BB25 월별등급 및 달성율
            
            #운수사코드.운수사
            code_row = df_code[df_code["운수사"] == company_input]
            code_company = code_row.iloc[0]["운수사최종코드"] if not code_row.empty else "-"
            # code_company = df_final.iloc[19, 35] #운수사코드.운수사 

            #출력시작
            st.markdown("<hr style='border:3px solid orange'>", unsafe_allow_html=True)
            
            #프로필
            col1, col2 = st.columns([1, 3], gap='large')
            with col1 :
                st.image("프로필.png" if os.path.exists("프로필.png") else "https://via.placeholder.com/150", width=150)

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

            st.markdown("### <📝종합 평가>")

            #전달등급
            past_grade1 = get_driver_info(file_path, final_code, past_code1, "등급")
            #전전달등급
            past_grade2 = get_driver_info(file_path, final_code, past_code2, "등급")
            # ap11 = df_final.iloc[10, 41]  # AP11(전달등급)
            # ap12 = df_final.iloc[11, 41]  # AP12(이번달등급)
            this_month = int(month_input) #이번달
            past_month1 = 12 if this_month == 1 else this_month - 1 #저번달
            next_month = 1 if this_month == 12 else this_month +1 #다음달
            past_month2 = 12 if past_month1 == 1 else past_month1 - 1 #저번달

            # ba5 = df_final.iloc[4, 52]  # BA5(이번달)
            # bc5 = df_final.iloc[4, 54]  # BC5(전달)
            percent_format = lambda val: "-" if val == "-" else f"{round(val * 100, 0)}%"
            past_percent1 = percent_format(get_driver_info(file_path, final_code, past_code1, "달성율"))
            this_percent = percent_format(get_driver_info(file_path, final_code, this_code, "달성율"))
            past_percent2 = percent_format(get_driver_info(file_path, final_code, past_code2, "달성율"))

            value_format = lambda val, unit="": "-" if val == "-" else f"{round(float(val),2)}{unit}"
            #전달 공회전
            past_idle = value_format(get_driver_info(file_path, final_code, past_code1, "공회전"), "%")
            #전달 급감속
            past_sa = value_format(get_driver_info(file_path, final_code, past_code1, "급감속"))

            #이번달 공회전
            this_idle = value_format(get_driver_info(file_path, final_code, this_code, "공회전"), "%")
            #이번달 급감속
            this_sa = value_format(get_driver_info(file_path, final_code, this_code, "급감속"))

            if past_grade1 in ['이상', '-']:
                evaluation_text = f"""
                <div>
                <p style='font-size: 15px;'>
                    ● 연비등급: {this_month}월 (<b>{user_grade}</b>)등급 <br>
                    ● 목표달성율: {this_month}월 ({this_percent}) <br>
                    ● 공회전: {this_month}월 ({this_idle}) <br>
                    <b><span style='background-color: yellow;'>● 급감속: {this_month}월 ({this_sa})회/100km당  </span></b> <br>
                </p>
                </div>"""
            else:
                evaluation_text = f"""
                <div>
                <p style='font-size: 15px;'>
                    ● 연비등급: {past_month1}월 (<b>{past_grade1}</b>)등급 -> {this_month}월 (<b>{user_grade}</b>)등급 <br>  
                    ● 목표달성율: {past_month1}월 ({past_percent1}) -> {this_month}월 ({this_percent})  <br>
                    ● 공회전: {past_month1}월 ({past_idle}) -> {this_month}월 ({this_idle}) <br>
                    <b><span style='background-color: yellow;'>● 급감속: {past_month1}월 ({past_sa})회/100km당 -> {this_month}월 ({this_sa})회/100km당  </span></b><br>
                </p>
                </div>"""

            st.markdown(evaluation_text, unsafe_allow_html=True)
            
            # 추가 조건에 따른 멘트 생성
            grade_target = "C" if user_grade in ["F", "D"] else "B" if user_grade == "C" else "A" if user_grade == "B" else "S"
            grade_color = "green" if grade_target in ["S", "A"] else "#003366" if grade_target in ["B", "C"] else "red"

            additional_text = f"""
            <br>
            <p style='font-size: 22px; font-style: italic;'>
            <b>{next_month}</b>월에는, <b>급감속</b>을 줄여봅시다.<br>
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
                color = "green" if val in ["S", "A"] else "#003366" if val in ["C", "D"] else "red"
                return f'color: {color}; font-weight: bold'
            
            st.dataframe(vehicle_data.style.applymap(highlight_grade, subset=["등급"])\
            .applymap(lambda x: 'background-color: yellow' if x else '', subset=['급감속'])\
            .set_table_styles([
                {'selector': 'th', 'props': [('font-weight', 'bold'), ('color', 'black'), ('text-align', 'center')]},
                {'selector': 'td', 'props': [('text-align', 'center')]}
            ]), hide_index=True)


            st.subheader("📊 노선 내 나의 수치")

            # route_avg = [98, 1.0, 41.2, 0.41, 15.24]  # 노선 평균 (AO6, AQ6, AR6, AS6, AT6)
            # my_stats = [87, 0.7, 39.5, 0.32, 30.57]  # 내 수치 (AO7, AQ7, AR7, AS7, AT7)
            # labels = ["달성율", "웜업", "공회전", "급가속", "급감속"]
            # x = np.arange(len(labels))
            # fig, ax = plt.subplots(figsize=(12, 3))  # 가로로 길게 설정
            # bar_width = 0.35  # 막대 너비 조정
            # colors = ["gray", "darkblue"]  # 노선 평균 (회색), 내 수치 (남색)

            # # 노선 평균 (회색)
            # bars1 = ax.bar(x - bar_width/2, route_avg, bar_width, label="노선평균", color=colors[0])

            # # 내 수치 (남색)
            # bars2 = ax.bar(x + bar_width/2, my_stats, bar_width, label="내 수치", color=colors[1])

            # # 상단에 수치 추가
            # for bar1, bar2, value1, value2 in zip(bars1, bars2, route_avg, my_stats):
            #     ax.text(bar1.get_x() + bar1.get_width()/2, bar1.get_height(), f"{value1:.1f}", ha='center', va='bottom', fontsize=10, color="black")
            #     ax.text(bar2.get_x() + bar2.get_width()/2, bar2.get_height(), f"{value2:.1f}", ha='center', va='bottom', fontsize=10, color="black")

            # # 그래프 설정
            # ax.set_xticks(x)
            # ax.set_xticklabels(labels, fontsize=12)
            # ax.legend()
            # ax.spines['top'].set_visible(False)
            # ax.spines['right'].set_visible(False)

            # # Streamlit에서 그래프 표시
            # st.pyplot(fig)
            
            image_path1 = os.path.join("노선내수치", f"{year_input}{month_input}/{code_company}/{user_name_input}({user_id_input}).png")
                # 이미지 불러오기
            if os.path.exists(image_path1):
                st.image(image_path1, caption=f"{user_name_input}({user_id_input})님의 노선 내 수치", use_container_width=True)
            else:
                st.warning(f"이미지 파일을 찾을 수 없습니다: {image_path1}")

            
            st.subheader(f"📉 {past_month1}월 vs {this_month}월 비교") #전월 vs 이번월

                # g2 폴더 내 AK6 이름의 PNG 파일 경로
            image_path2 = os.path.join("전월비교", f"{year_input}{month_input}/{code_company}/{user_name_input}({user_id_input}).png")

                # 이미지 불러오기
            if os.path.exists(image_path2):
                st.image(image_path2, caption=f"{user_name_input}({user_id_input})님의 전월대비 수치 비교", use_container_width=True)
            else:
                st.warning(f"이미지 파일을 찾을 수 없습니다: {image_path2}")


            
            st.subheader(f"📅 나만의 등급 달력_{this_month}월")
                # g3 폴더 내 AK6 이름의 PNG 파일 경로
            image_path3 = os.path.join("달력이미지", f"{year_input}{month_input}/{code_company}/{user_name_input}({user_id_input}).png")

                # 이미지 불러오기
            if os.path.exists(image_path3):
                st.image(image_path3, caption=f"{user_name_input}({user_id_input})님의 이번달 등급 달력", use_container_width=True)
            else:
                st.warning(f"이미지 파일을 찾을 수 없습니다: {image_path3}")
            
            
            st.subheader("📊 월별 등급 추이")

            #값 정의

            # paste_grade1 = df_final.iloc[22, 52] # 전전월 등급
            # paste_grade2 = df_final.iloc[23, 52] # 전전월 등급
            # this_grade = df_final.iloc[24, 52] # 이번월 등급
            # # paste_percent1 = f"{round(df_final.iloc[22, 53] * 100)}%" #전전월 달성율
            # paste_percent2 = f"{round(df_final.iloc[23, 53] * 100)}%" #전월 달성율
            # this_percent = f"{round(df_final.iloc[24, 53] * 100)}%" #이번달 달성율

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
                    <div style='font-size: 18px; font-weight: bold;'>1{this_month}월</div>
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
        st.warning("해당 기간에 운전자님의 데이터가 없습니다.")
else:
    st.warning("운수사, 운전자 ID, 운전자 이름을 입력하세요.")
