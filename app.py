import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import requests
import numpy as np
from PIL import Image, ImageOps
import matplotlib as mpl 
import matplotlib.pyplot as plt 
import matplotlib.font_manager as fm  
import matplotlib.ticker as ticker
from openpyxl import load_workbook
import calendar
import datetime

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


# Streamlit UI 구성🚍
st.title("🚍 운전자별 대시보드")
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
    df_cert_24 = load_excel(file_path, "24년 명단")
    df_cert_25 = load_excel(file_path, "25년 후보자")

    # 조건 필터링
    filtered = df[
        (df["운수사"] == company_input) &
        (df["운전자이름"] == user_name_input) &
        (df["운전자ID"].astype(str) == user_id_input)
    ]

    #등급함수
    def calc_grade(score):
        score *= 100
        if score >= 100: return "S"
        elif score >= 95: return "A"
        elif score >= 90: return "B"
        elif score >= 85: return "C"
        elif score >= 80: return "D"
        elif score >= 65: return "F"
        else: return ""

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
        grade_text_color = "green" if this_grade in ["S", "A"] else "orange" if this_grade in ["B", "C"] else "red"

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

        # 인증 현황🏅
        st.markdown("---")
        st.subheader("🏆나의 인증 현황")


        st.markdown(f"<div style='background-color: rgba(211, 211, 211, 0.3); padding: 10px; border-radius: 5px; margin-bottom: 20px;'> 4분기 모두 우수인증자 수여 시 그랜드슬림 달성!", unsafe_allow_html=True)

        from calendar import month_abbr
        df_cert_25_summary = df_monthly[
            (df_monthly['운수사'] == company_input) &
            (df_monthly['운전자ID'].astype(str) == user_id_input) &
            (df_monthly['운전자이름'] == user_name_input)&
            (df_monthly['년월'].astype(str).str.startswith("25"))
        ]

        medal_url = "https://raw.githubusercontent.com/ucarsystem/driver_dashboard/main/medal.png"
        medal_black_url = "https://raw.githubusercontent.com/ucarsystem/driver_dashboard/main/medal_black.png"

        # 분기/월 전처리
        df_cert_25_summary['년'] = df_cert_25_summary['년월'].astype(str).str[:2].astype(int)
        df_cert_25_summary['월'] = df_cert_25_summary['년월'].astype(str).str[2:].astype(int)
        df_cert_25_summary['분기'] = df_cert_25_summary['월'].apply(lambda m: (m - 1) // 3 + 1)

        # 분기별 평균: 각 분기에 해당하는 월의 평균
        quarter_avg = (
            df_cert_25_summary
            .groupby(['년', '분기'])
            .agg({'가중달성율': 'mean'})
            .reset_index()
        )

        quarter_avg['등급'] = quarter_avg['가중달성율'].apply(calc_grade)

        grouped_month = df_cert_25_summary[['년', '월', '등급']].copy()
        grouped_month = grouped_month.rename(columns={'등급': '월별등급'})

        # 24년 인증 확인
        is_cert_24 = not df_cert_24[
            (df_cert_24['운수사'] == company_input) &
            (df_cert_24['성명'] == user_name_input) &
            (df_cert_24['아이디'].astype(str) == user_id_input)
        ].empty

        if is_cert_24:
            medal_24 = (
                "<div style='width: 180px; height: 180px; text-align: center; border: 2px solid #888; border-radius: 10px; padding: 10px; margin-bottom: 30px;'>"
                "<div style='font-size: 15px; font-weight: bold;'>🏅24년 우수인증자🏅</div>"
                f"<img src='{medal_url}' width='100'>"
                "</div>"
            )
        st.markdown(medal_24, unsafe_allow_html=True)

        cert_grid = "<div style='display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-start;'>"

        # 현재 날짜 기준으로 현재 연도/월 확인
        now = datetime.datetime.now()
        current_year = int(str(now.year)[-2:])  # 25
        current_month = now.month
        current_quarter = (current_month - 1) // 3 + 1

        for q_idx, q_row in quarter_avg.iterrows():
            year, quarter, avg_score, grade = q_row['년'], int(q_row['분기']), q_row['가중달성율'], q_row['등급']
            quarter_title = f"{year}년 {quarter}분기"

            months_in_quarter = grouped_month[
                (grouped_month['년'] == year) & 
                (grouped_month['월'].between((quarter - 1) * 3 + 1, quarter * 3))
            ]

            if year < current_year or (year == current_year and quarter < current_quarter):
                if avg_score >= 0.95:
                    medal = f"<img src='{medal_url}' width='100'>"
                else:
                    medal = (
                        f"<img src='{medal_black_url}' width='100'>"
                        f"<div style='font-weight:bold;'>{grade}({avg_score*100:.0f}%)</div>"
                    )
            else:
                medal = (
                    f"<img src='{medal_black_url}' width='100'>"
                    f"<div style='font-size: 13px;'>진행중...({avg_score*100:.0f}%)</div>"
                )

            # 월별 박스를 가로 배치하기 위한 container 추가
            month_boxes = "".join([
                "<div style='margin: 15px; text-align: center; display: inline-block;'>"
                f"<div style='font-size: 16px; font-weight: bold;'>{m_row['월']}월</div>"
                f"<div style='font-size: 24px;'>{'🥇' if m_row['월별등급'] in ['S', 'A'] else m_row['월별등급']}</div>"
                "</div>"
                for _, m_row in months_in_quarter.iterrows()
            ])

            cert_grid += (
                "<div style='width: 200px; text-align: center; border: 1px solid #ccc; border-radius: 10px; padding: 10px;'>"
                f"<div style='font-size: 15px; font-weight: bold;'>{quarter_title}</div>"
                f"{medal}"
                f"<div style='margin-top: 15px; display: flex; justify-content: center;'>{month_boxes}</div>"
                "</div>"
            )

        cert_grid += "</div>"
        st.markdown(cert_grid, unsafe_allow_html=True)


        # for q_idx, q_row in quarter_avg.iterrows():
        #     year, quarter, avg_score, grade = q_row['년'], int(q_row['분기']), q_row['가중달성율'], q_row['등급']
        #     quarter_title = f"{year}년 {quarter}분기"

        #     months_in_quarter = grouped_month[(grouped_month['년'] == year) & (grouped_month['월'].between((quarter - 1) * 3 + 1, quarter * 3))]
            
        #     month_boxes = "".join([
        #         "<div style='width: 60px; height: 70px; text-align: center;'>"
        #         f"<div style='font-size: 12px; font-weight: bold;'>{m_row['월']}월</div>"
        #         f"<div style='font-size: 18px;'>{'🥇' if m_row['월별등급'] in ['S', 'A'] else m_row['월별등급']}</div>"
        #         "</div>"
        #         for _, m_row in months_in_quarter.iterrows()
        #     ])

        #     if year < current_year or (year == current_year and quarter < current_quarter):
        #         # 이미 지난 분기
        #         if avg_score >= 1.0:
        #             medal = f"<img src='{medal_url}' width='100'>"
        #         else:
        #             medal = (
        #                 f"<img src='{medal_black_url}' width='100'>"
        #                 f"<div style='font-weight:bold;'>{grade}({avg_score*100:.0f}%)</div>"
        #             )
        #     else:
        #         # 현재 분기 또는 미래
        #         medal = (
        #             f"<img src='{medal_black_url}' width='80'>"
        #             f"<div style='font-size: 13px;'>진행중...<br>({avg_score*100:.0f}%)</div>"
        #         )

        #     cert_grid += (
        #         "<div style='width: 150px; height: 150px; text-align: center; border: 1px solid #ccc; border-radius: 10px; padding: 10px;'>"
        #         f"<div style='font-size: 15px; font-weight: bold;'>{quarter_title}</div>"
        #         f"{medal}"
        #         f"{month_boxes}"
        #         "</div>"
        #     )

        # cert_grid += "</div>"
        # st.markdown(cert_grid, unsafe_allow_html=True)

        # 📅 일별 달성률 및 등급 표시
        st.markdown("---")
        st.subheader("📅 일별 등급 스탬프")
        df_daily_filtered = df_daily[
            (df_daily['운수사'] == company_input) &
            (df_daily['운전자ID'].astype(str) == user_id_input) &
            (df_daily['운전자이름'] == user_name_input)
        ]
        if not df_daily_filtered.empty:
            grouped = df_daily_filtered.groupby('DATE')['가중평균달성율'].sum().reset_index()

            grouped['달성률값'] = (grouped['가중평균달성율'] * 100).round(0)
            grouped['등급'] = grouped['가중평균달성율'].apply(calc_grade)
            grouped['날짜'] = pd.to_datetime(grouped['DATE'])


            # 📅 달력형 등급 표시
            import calendar
            year = grouped['날짜'].dt.year.iloc[0]
            month = grouped['날짜'].dt.month.iloc[0]
            grade_map = grouped.set_index(grouped['날짜'].dt.day)['등급'].to_dict()
            cal = calendar.Calendar()
            month_days = cal.monthdayscalendar(year, month)

            calendar_rows = []
            for week in month_days:
                low = []
                for i, day in enumerate(week):
                    if day == 0:
                        low.append("<td style='height: 80px;'></td>")
                    else:
                        grade = grade_map.get(day, "")
                        if grade in ["S", "A"]:
                            emoji = "<div style='font-size: 30px;'>🎖️</div>"
                            label = ""
                        elif grade in ["B", "C"]:
                            emoji = f"<div style='font-size: 30px;'>🎖️</div><div style='color: orange; font-size: 18px; font-weight: bold;'>{grade}</div>"
                        elif grade in ["D", "F"]:
                            emoji = f"<div style='font-size: 30px;'>🎖️</div><div style='color: red; font-size: 18px; font-weight: bold;'>{grade}</div>"
                        else:
                            emoji = f"<span style='font-weight: bold; font-size: 20px;'>"  "</span>"
                        color = "red" if i == 0 else "black"
                        low.append(f"""
                            <td style='padding: 8px; border: 1px solid #ccc; color: {color}; height: 80px;'>
                                <div style='font-size: 16px; font-weight: bold;'>{day}</div>
                                {emoji}
                            </td>""")
                calendar_rows.append("<tr>" + "".join(low) + "</tr>")

            html = """
            <table style='border-collapse: collapse; margin: auto; background-color: #fff;'>
            <tr style='background-color: #f2f2f2;'>
                <th style='color: red; width: 80px;'>일</th><th style='width: 80px;'>월</th><th style='width: 80px;'>화</th><th style='width: 80px;'>수</th><th style='width: 80px;'>목</th><th style='width: 80px;'>금</th><th style='width: 80px;'>토</th>
            </tr>
            """ + "".join(calendar_rows) + "</table>"
            # <table style='border-collapse: collapse; width: 100%; text-align: center; background-color: #f0f5ef;'>
            # <tr style='background-color: #e0e0e0;'>
            #     <th style='color: red;'>일</th><th>월</th><th>화</th><th>수</th><th>목</th><th>금</th><th>토</th>
            # </tr>
            # """ + "".join(calendar_rows) + "</table>"

            st.markdown(html, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🗣️ 개인 맞춤 피드백")

        #급감속 멘트
        break_text = f"""
        <br>
        <p style='font-size: 22px; font-style: italic;'>
        <b>{next_month}</b>월에는, <b>급감속</b>을 줄여봅시다.<br>
        이번달 급감속 <b>{round(this_break, 2)}</b> 급감속은 <b>매탕 1회 미만!</b><br>
        이것만 개선해도 연비 5% 개선, 
        <span style='color: green; font-weight: bold;'>{grade_target}등급</span>까지 도달 목표!!
        </p>"""

        #공회전멘트
        idle_text = f"""
        <br>
        <p style='font-size: 22px; font-style: italic;'>
        <b>{next_month}</b>월에는, <b>공회전</b>을 줄여봅시다.<br>
        이번달 공회전 <b>{round(this_idle * 100)}%</b> 공회전은 <b>5분 미만!</b><br>
        이것만 개선해도 연비 5% 개선, 
        <span style='color: green; font-weight: bold;'>{grade_target}등급</span>까지 도달 목표!!
        </p>"""

        #급감속이 5보다 작으면 공회전관리멘트 보여주기
        additional_text = idle_text if this_break <5 else  break_text

        st.markdown(f"""
        <div style='background-color: rgba(211, 211, 211, 0.3); padding: 10px; border-radius: 5px;'>
        {additional_text}
        </div>
        """, unsafe_allow_html=True)


        st.markdown("---")
        st.subheader("🚦 운전 습관 핵심 지표 비교 🚦")
        compare_df = pd.DataFrame({
            "지표": ["달성률(%)", "웜업률(%)", "공회전률(%)", "급감속(회/100km)"],
            "이달": [
                f"{round(this_percent * 100)}%",
                f"{round(this_warm * 100, 1)}%",
                f"{round(this_idle * 100, 1)}%",
                f"{round(this_break, 2)}"
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

        st.write("""
        <style>
        td span {
            font-size: 13px;
        }
        table td {
            white-space: nowrap !important;
            text-align: center;
            vertical-align: middle;
        }
        </style>
        """, unsafe_allow_html=True)
        st.write(compare_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        st.markdown("---")
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

        # 조건에 따른 색상 정의
        def get_color(i, d, a):
            good_if_higher = (i == 2)  # 탄력운전률만 높을수록 좋음
            if (good_if_higher and d >= a) or (not good_if_higher and d <= a):
                return '#C8E6C9'  # 연한 녹색
            else:
                return '#2E7D32'  # 진한 녹색 (기준보다 나쁠 때)

        colors = [get_color(i, d, a) for i, (d, a) in enumerate(zip(driver_vals, avg_vals))]

        fig, ax = plt.subplots(figsize=(9, 5))
        x = range(len(labels))
        bar_width = 0.4

        bars1 = ax.barh(x, driver_vals, height=bar_width, label='운전자', align='center', color=colors)
        bars2 = ax.barh([i + bar_width for i in x], avg_vals, height=bar_width, label='노선 평균', align='center', color='#FFE08C')

        # 값 표시
        for i, (d, a) in enumerate(zip(driver_vals, avg_vals)):
            ax.text(d + 0.8, i, f"{d:.1f}", va='center', fontsize=10, fontweight='bold', color='black')
            ax.text(a + 0.8, i + bar_width, f"{a:.1f}", va='center', fontsize=10, fontweight='bold', color='black')

        # 라벨 및 제목 스타일 조정
        ax.set_yticks([i + bar_width / 2 for i in x])
        ax.set_yticklabels(labels, fontproperties=font_prop, fontsize=11)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.invert_yaxis()
        ax.legend(prop=font_prop)
        ax.set_title("이달 수치 vs 노선 평균 비교", fontsize=15, fontweight='bold', fontproperties=font_prop)
        ax.set_axisbelow(True)
        ax.grid(True, axis='x', linestyle='--', alpha=0.4)

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
                "지표": ["달성률(%)", "웜업률(%)", "공회전률(%)", "탄력운전률(%)", "급감속"],
                "전월": [
                    round(last_percent * 100, 0),
                    round(last_warm* 100, 2),
                    round(last_idle * 100, 2),
                    round(row['전월탄력운전비율(%)'] * 100, 2),
                    round(last_break, 2)
                ],
                "이달": [
                    round(this_percent* 100, 0),
                    round(this_warm * 100, 2),
                    round(this_idle* 100, 2),
                    round(row['이번달탄력운전비율(%)'] * 100, 2),
                    round(this_break, 2)
                ]
            })
            compare['변화'] = compare['이달'] - compare['전월']
            st.write("""
            <style>
            td span {
                font-size: 13px;
            }
            table td {
                white-space: nowrap !important;
                text-align: center;
                vertical-align: middle;
            }
            </style>
            """, unsafe_allow_html=True)
            st.write(compare.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("---")
        
        st.subheader("🚘 차량별 요약")
        df_vehicle_filtered = df_vehicle[
            (df_vehicle['운수사'] == company_input) &
            (df_vehicle['운전자ID'].astype(str) == user_id_input) &
            (df_vehicle['운전자이름'] == user_name_input) &
            (df_vehicle['년월'] == int(input_yyyymm))
        ].sort_values(by="주행거리(km)", ascending=False).head(5)

        if not df_vehicle_filtered.empty:
            df_vehicle_display = df_vehicle_filtered.copy()
            df_vehicle_display["주행거리(km)"] = df_vehicle_display["주행거리(km)"].apply(lambda x: f"{int(x):,} km")
            df_vehicle_display["웜업비율(%)"] = df_vehicle_display["웜업비율(%)"].apply(lambda x: f"{x * 100:.2f}%")
            df_vehicle_display["공회전비율(%)"] = df_vehicle_display["공회전비율(%)"].apply(lambda x: f"{x * 100:.2f}%")
            df_vehicle_display["급감속(회)/100km"] = df_vehicle_display["급감속(회)/100km"].apply(lambda x: f"{x:.2f}")
            df_vehicle_display["연비(km/m3)"] = df_vehicle_display["연비(km/m3)"].apply(lambda x: f"{x:.2f}")

            def format_grade(g):
                color = "green" if g in ["S", "A"] else "orange" if g in ["B", "C"] else "red"
                return f"<span style='color:{color}; font-weight:bold'>{g}</span>"

            df_vehicle_display["등급"] = df_vehicle_display["등급"].apply(format_grade)

            df_vehicle_display = df_vehicle_display[["노선번호", "차량번호4", "주행거리(km)", "웜업비율(%)", "공회전비율(%)", "급감속(회)/100km", "연비(km/m3)", "등급"]]

            df_vehicle_display = df_vehicle_display.rename(columns={
                "노선번호" : "노선",
                "차량번호4": "차량번호",
                "주행거리(km)" : "주행거리",
                "웜업비율(%)" : "웜업률(%)", 
                "공회전비율(%)" : "공회전율(%)",
                "연비(km/m3)": "연비"
            })

            st.write("""
            <style>
            td span {
                font-size: 13px;
            }
            table td {
                white-space: nowrap !important;
                text-align: center;
                vertical-align: middle;
            }
            </style>
            """, unsafe_allow_html=True)

            st.write(df_vehicle_display.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("---")

        # 조건별 자동 피드백 생성
        st.markdown("### 📌 사고위험/공회전 분석 피드백")
        break_ = row["이번달급가속(회)/100km"]
        idle = row["이번달공회전비율(%)"] * 100

        feedback_parts = []
        if break_ < row["노선평균급감속(회)/100km"]:
            feedback_parts.append("✅ 사고위험 발생이 매우 적어 안전 운전에 기여하고 있습니다.")
        elif break_ < 80:
            feedback_parts.append("🟡 사고위험이 다소 발생하고 있습니다. ")
        else:
            feedback_parts.append("⚠️ 사고위험 지수가 높습니다. 매탕 급감속 횟수 1회씩만 줄여보세요.")

        if idle > row["노선평균공회전비율(%)"]*100:
            feedback_parts.append("⚠️ 공회전 비율이 높습니다. 정차 시 시동 관리에 유의해 주세요.")
        elif idle > 40:
            feedback_parts.append("🟡 공회전이 평균보다 다소 높습니다. 불필요한 정차를 줄여주세요.")
        else:
            feedback_parts.append("✅ 공회전 관리가 잘 되고 있습니다.")

        st.markdown("<br>".join(feedback_parts), unsafe_allow_html=True)

    else:
            st.warning("운수사, 운전자 ID, 운전자 이름을 확인해주세요.")
else:
    st.warning("운수사, 운전자 ID, 운전자 이름을 입력하세요.")


