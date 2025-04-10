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
def load_excel(path, sheetname):
    try:
        return pd.read_excel(path, sheet_name=sheetname)
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
input_yyyymm = f"{year_input}{month_input}"

if st.button("조회하기") and company_input and user_id_input and user_name_input and year_input and month_input:
    file_name = f"인천 개인별 대시보드_{year_input}년{month_input}월.xlsx"
    file_path = os.path.join(file_dir, file_name)

    df = load_excel(file_path, "매크로(운전자리스트)")
    df_vehicle = load_excel(file_path, "차량+운전자별")
    df_monthly = load_excel(file_path, "운전자별")
    df_daily = load_excel(file_path, "일별)차량+운전자")

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

        #값 정의
        #이번달
        this_grade = row["2502"] #등급
        this_percent = row['이번달달성율']
        this_warm = row['이번달웜업비율(%)']
        this_idle = row["이번달공회전비율(%)"] 
        this_break = row['이번달급감속(회)/100km']
        this_line = row['주운행노선']
        this_bus = row['주운행차량']

        #전월
        last_grade = row['전월등급']
        last_percent = row['전월달성율']
        last_warm = row['전월웜업비율(%)']
        last_idle = row["전월공회전비율(%)"] 
        last_break = row['전월급감속(회)/100km']

        #노선평균
        ave_grade = row['노선평균등급']
        ave_percent = row['노선평균달성율']
        ave_warm = row['노선평균웜업비율(%)']
        ave_idle = row["노선평균공회전비율(%)"] 
        ave_break = row['노선평균급감속(회)/100km']

        #다음달
        next_month = 1 if int(month_input) == 12 else int(month_input)+1 


        grade_color = {"S": "🟩", "A": "🟩", "B": "🟨", "C": "🟨", "D": "🟥", "F": "🟥"}
        grade_target = "C" if this_grade in ["F", "D"] else "B" if this_grade == "C" else "A" if this_grade == "B" else "S"
        grade_text_color = "green" if this_grade in ["S", "A"] else "#FFD700" if this_grade in ["B", "C"] else "red"

        # 🚌 추가 정보: 대표 차량 및 노선
        st.markdown(f"""
        <div style='display: flex; align-items: center;'>
            <img src='https://img.icons8.com/color/48/bus.png' style='margin-right: 10px;'>
            <div>
                <div><strong>대표 차량:</strong> {this_bus}</div>
                <div><strong>노선:</strong> {this_line}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div style='font-size: 20px; font-weight: bold;'>이달의 등급</div><div style='font-size: 28px; font-weight: bold; color: {grade_text_color};'>{grade_color.get(this_grade, '')} {this_grade}</div>", unsafe_allow_html=True)
        col2.metric("달성률", f"{round(row['이번달달성율'] * 100)}%")
        col3.metric("공회전", f"{round(this_idle * 100)}%")
        col4.metric("급감속", f"{round(this_break, 2)}")

        st.markdown("---")


        #st.markdown("### <📝종합 평가>")
        st.subheader("🗣️ 개인 맞춤 피드백")
        break_text = f"""
        <br>
        <p style='font-size: 22px; font-style: italic;'>
        <b>{next_month}</b>월에는, <b>급감속</b>을 줄여봅시다.<br>
        이번달 급감속 <b>{round(this_break, 2)}</b> 급감속은 <b>매탕 1회 미만!</b><br>
        이것만 개선해도 연비 5% 개선, 
        <span style='color: green; font-weight: bold;'>{grade_target}등급</span>까지 도달 목표!!
        </p>"""

        idle_text = f"""
        <br>
        <p style='font-size: 22px; font-style: italic;'>
        <b>{next_month}</b>월에는, <b>공회전</b>을 줄여봅시다.<br>
        이번달 공회전 <b>{round(this_idle * 100)}%</b> 공회전은 <b>5분 미만!</b><br>
        이것만 개선해도 연비 5% 개선, 
        <span style='color: green; font-weight: bold;'>{grade_target}등급</span>까지 도달 목표!!
        </p>"""

        additional_text = idle_text if this_break <5 else  break_text

        st.markdown(f"""
        <div style='background-color: rgba(211, 211, 211, 0.3); padding: 10px; border-radius: 5px;'>
        {additional_text}
        </div>
        """, unsafe_allow_html=True)


        st.markdown("---")
        st.subheader("🚦 운전 습관 핵심 지표 비교")
        compare_df = pd.DataFrame({
            "지표": ["달성률(%)", "웜업률(%)", "공회전률(%)", "급감속(회/100km)"],
            "이달": [
                f"{round(this_percent * 100)}%",
                f"{round(this_warm * 100, 1)}%",
                f"{round(this_idle * 100, 1)}%",
                f"{round(this_break, 1)}%"
            ],
            "전월": [
                f"{round(last_percent * 100)}%",
                f"{round(last_warm * 100, 1)}%",
                f"{round(last_idle * 100, 1)}%",
                f"{round(last_break, 2)}"
            ],  # 예시값
            "노선 평균": [
                f"{round(ave_percent * 100)}%",
                f"{round(ave_warm * 100, 1)}%",
                f"{round(ave_idle * 100, 1)}%",
                f"{round(ave_break, 2)}"
            ],  # 예시값
        })
        st.dataframe(compare_df, hide_index=True)

        st.subheader("📊 이달 vs 노선 평균 그래프")
        labels = [
            "웜업률(%)", "공회전률(%)", "탄력운전률(%)",
            "연료소모율", "급가속(/100km)", "급감속(/100km)"
        ]
        driver_vals = [
            this_warm * 100,
            this_idle * 100,
            row["이번달탄력운전비율(%)"] * 100,
            row["이번달평균연료소모율"],
            row["이번달급가속(회)/100km"],
            this_break
        ]
        avg_vals = [
            ave_warm * 100,
            ave_idle * 100,
            row["노선평균탄력운전비율(%)"] * 100,
            row["노선평균평균연료소모율"],
            row["노선평균급가속(회)/100km"],
            ave_break
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
        st.subheader("📈 전월 대비 개선 여부")
        def get_prev_yyyymm(yyyymm):
            y, m = int(yyyymm[:2]), int(yyyymm[2:])
            if m == 1:
                return f"{y - 1 if y > 0 else 99}12"
            else:
                return f"{y:02d}{m - 1:02d}"
            
        prev_yyyymm = get_prev_yyyymm(input_yyyymm)
        df_prev = df_monthly[
            (df_monthly['운수사'] == company_input) &
            (df_monthly['운전자ID'].astype(str) == user_id_input) &
            (df_monthly['운전자이름'] == user_name_input)
        ]

        prev_row = df_prev[df_prev['년월'] == int(prev_yyyymm)]
        curr_row = df_prev[df_prev['년월'] == int(input_yyyymm)]

        if not prev_row.empty and not curr_row.empty:
            prev = prev_row.iloc[0]
            curr = curr_row.iloc[0]
            compare = pd.DataFrame({
                "지표": ["달성률", "웜업률", "공회전률", "탄력운전률", "급감속"],
                "전월": [
                    round(last_percent * 100),
                    round(last_warm* 100, 2),
                    round(last_idle * 100, 2),
                    round(row['전월탄력운전비율(%)'] * 100, 2),
                    round(last_break, 2)
                ],
                "이달": [
                    round(this_percent* 100),
                    round(this_warm * 100, 2),
                    round(this_idle* 100, 2),
                    round(row['이번달탄력운전비율(%)'] * 100, 2),
                    round(this_break, 2)
                ]
            })
            compare['변화'] = compare['이달'] - compare['전월']
            st.dataframe(compare, hide_index=True)

        st.markdown("---")
        st.subheader("🚘 차량별 운전 비교")
        df_vehicle_filtered = df_vehicle[
            (df_vehicle['운수사'] == company_input) &
            (df_vehicle['운전자ID'].astype(str) == user_id_input) &
            (df_vehicle['운전자이름'] == user_name_input) &
            (df_vehicle['년월'] == int(input_yyyymm))
        ].sort_values(by="주행거리(km)", ascending=False).head(5)

        if not df_vehicle_filtered.empty:
            st.dataframe(df_vehicle_filtered[["노선번호", "차량번호4", "주행거리(km)", "웜업비율(%)", "공회전비율(%)", "급감속(회)/100km", "등급"]].reset_index(drop=True))

        st.markdown("---")

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

        st.markdown("<br>".join(feedback_parts), unsafe_allow_html=True)

        # 📅 일별 달성률 및 등급 표시
        st.markdown("---")
        st.subheader("📅 일별 달성률 및 등급")
        df_daily_filtered = df_daily[
            (df_daily['운수사'] == company_input) &
            (df_daily['운전자ID'].astype(str) == user_id_input) &
            (df_daily['운전자이름'] == user_name_input)
        ]
        if not df_daily_filtered.empty:
            grouped = df_daily_filtered.groupby('DATE')['가중평균달성율'].sum().reset_index()
            def calc_grade(score):
                score *= 100
                if score >= 100:
                    return "S"
                elif score >= 95:
                    return "A"
                elif score >= 90:
                    return "B"
                elif score >= 85:
                    return "C"
                elif score >= 80:
                    return "D"
                elif score >= 65:
                    return "F"
                else:
                    return ""

            grouped['달성률값'] = (grouped['가중평균달성율'] * 100).round(0)
            grouped['등급'] = grouped['가중평균달성율'].apply(calc_grade)
            grouped['날짜'] = pd.to_datetime(grouped['DATE'])
            grouped['날짜표시'] = grouped['날짜'].dt.strftime('%y/%m/%d (%a)')

            for _, row_ in grouped.iterrows():
                rate = int(row_['달성률값'])
                grade = row_['등급']
                grade_color = "green" if grade in ["S", "A"] else "#FFD700" if grade in ["B", "C"] else "red"
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding: 6px 0;'>
                    <div style='flex: 1;'>{row_['날짜표시']}</div>
                    <div style='flex: 1; text-align: center;'>{rate}%</div>
                    <div style='flex: 1; text-align: right; color: {grade_color}; font-weight: bold;'>{grade}</div>
                </div>
                """, unsafe_allow_html=True)

            # 🔹 등급 그래프 시각화
            st.markdown("#### 📊 일별 등급 추이 그래프")
            fig2, ax2 = plt.subplots(figsize=(8, 3))
            ax2.plot(grouped['날짜'], grouped['달성률값'], marker='o', linestyle='-', color='green')
            ax2.set_xticks(grouped['날짜'])
            ax2.set_xticklabels(grouped['날짜표시'], rotation=45, fontsize=8, fontproperties=font_prop)
            ax2.set_ylabel('달성률 (%)', fontproperties=font_prop)
            ax2.set_title('일별 달성률 추이', fontproperties=font_prop)
            ax2.grid(True, linestyle='--', alpha=0.5)
            st.pyplot(fig2)

            # 🔹 주간 평균 요약
            st.markdown("#### 📅 주간 평균 요약")
            grouped['week'] = grouped['날짜'].dt.isocalendar().week
            weekly_avg = grouped.groupby('week')['달성률값'].mean().reset_index()
            weekly_avg.columns = ['주차', '평균 달성률']
            weekly_avg['평균 달성률'] = weekly_avg['평균 달성률'].round(1)
            st.dataframe(weekly_avg, hide_index=True)

    else:
            st.warning("운수사, 운전자 ID, 운전자 이름을 확인해주세요.")
else:
    st.warning("운수사, 운전자 ID, 운전자 이름을 입력하세요.")


