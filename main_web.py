import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta
from db_supabase import WorkoutDB

# ==========================================
# 0. 기본 세팅 (화면 및 DB)
# ==========================================
st.set_page_config(page_title="나만의 운동일지", page_icon="💪", layout="centered")

# 한글 폰트 설정 (그래프 깨짐 방지)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# DB 연결 (새로고침할 때마다 DB를 여러 번 부르지 않게 캐싱)
@st.cache_resource
def get_db():
    return WorkoutDB()
db = get_db()

# ==========================================
# 1. 📱 사이드바 메뉴
# ==========================================
st.sidebar.title("📌 메뉴")
page = st.sidebar.radio("이동할 탭을 선택하세요:", 
                        ["💪 운동 일지", "📊 심층 분석", "🥗 식단 트래커", "📝 필기 노트", "⚙️ 설정 및 종목"])

# ==========================================
# 2. 💪 운동 일지 화면
# ==========================================
if page == "💪 운동 일지":
    st.title("💪 오늘 운동 기록하기")
    
    col1, col2 = st.columns(2)
    record_date = col1.date_input("📅 날짜", date.today())
    selected_ex = col2.selectbox("📌 종목", db.get_all_exercises())
    
    c1, c2, c3 = st.columns(3)
    weight = c1.number_input("무게 (kg)", min_value=0.0, step=2.5, value=60.0)
    reps = c2.number_input("횟수", min_value=1, step=1, value=10)
    set_num = c3.number_input("세트", min_value=1, step=1, value=1)
    
    if st.button("💾 이 세트 저장하기", use_container_width=True, type="primary"):
        db.insert_record(record_date.strftime("%Y-%m-%d"), selected_ex, set_num, weight, reps)
        st.success(f"{selected_ex} {set_num}세트 ({weight}kg x {reps}회) 저장 완료! 🔥")
        
    st.divider()
    
    st.subheader("📝 오늘 완료한 운동")
    today_records = db.get_records_by_date(record_date.strftime("%Y-%m-%d"))
    if today_records:
        df = pd.DataFrame(today_records, columns=["종목", "세트", "무게(kg)", "횟수"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        del_ex = st.selectbox("🗑️ 기록 삭제할 종목 선택", df['종목'].unique())
        if st.button("해당 종목 기록 전체 삭제"):
            db.delete_exercise_records(record_date.strftime("%Y-%m-%d"), del_ex)
            st.rerun() 
    else:
        st.info("아직 오늘 기록된 운동이 없습니다. 얼른 쇠질하러 가시죠!")

# ==========================================
# 3. 📊 심층 분석 화면
# ==========================================
elif page == "📊 심층 분석":
    st.title("📊 데이터 심층 분석")
    st.write("나의 점진적 과부하를 눈으로 확인하세요!")
    
    selected_ex = st.selectbox("📌 분석할 종목", db.get_all_exercises())
    
    col1, col2 = st.columns(2)
    start_date = col1.date_input("시작일", date.today() - timedelta(days=30))
    end_date = col2.date_input("종료일", date.today())
        
    if st.button("📈 그래프 조회하기", use_container_width=True, type="primary"):
        data = db.get_volume_and_1rm_trend(selected_ex, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        if not data:
            st.warning("선택하신 기간 내에 기록이 없습니다.")
        else:
            dates = [d[0][-5:] for d in data]
            volumes = [d[1] for d in data]
            onerms = [round(d[2], 1) for d in data]

            fig, ax1 = plt.subplots(figsize=(8, 4))
            ax2 = ax1.twinx()
            
            ax1.bar(dates, volumes, color='#E2E8F0', width=0.5, label='총 볼륨 (kg)')
            ax1.set_ylabel('총 볼륨 (kg)', color='#718096', fontweight='bold')
            max_vol = max(volumes)
            ax1.set_ylim(0, 100 if max_vol == 0 else max_vol * 1.3)
            
            ax2.plot(dates, onerms, marker='o', color='#E53E3E', linewidth=3, markersize=6, label='추정 1RM (kg)')
            ax2.set_ylabel('추정 1RM (kg)', color='#E53E3E', fontweight='bold')
            for i, v in enumerate(onerms):
                ax2.text(i, v + (max(onerms)*0.03), f"{v}kg", ha='center', va='bottom', color='#C53030', fontweight='bold', fontsize=9)

            ax1.set_title(f"'{selected_ex}' 성장 퍼포먼스", fontsize=14, fontweight='bold', pad=15)
            ax1.grid(axis='y', linestyle='--', alpha=0.3)
            
            lines_1, labels_1 = ax1.get_legend_handles_labels()
            lines_2, labels_2 = ax2.get_legend_handles_labels()
            ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
            
            st.pyplot(fig)

# ==========================================
# 4. 🥗 식단 트래커 화면 (체중 및 단백질 가이드 완벽 연동!)
# ==========================================
elif page == "🥗 식단 트래커":
    st.title("🥗 식단 & 매크로 트래커")
    
    goal_cal, goal_carbs, goal_pro, goal_fat = 2500, 300, 150, 70
    record_date = st.date_input("📅 날짜 선택", date.today())
    date_str = record_date.strftime("%Y-%m-%d")

    # ⭐ 체중 기록 섹션
    with st.expander("⚖️ 오늘의 체중 기록", expanded=True):
        current_weight = db.get_weight(date_str)
        col_w1, col_w2 = st.columns([3, 1])
        with col_w1:
            # 안전장치: 체중이 없으면 0.0으로 표시
            new_weight = st.number_input("현재 체중 (kg)", value=float(current_weight) if current_weight else 0.0, step=0.1, format="%.1f")
        with col_w2:
            st.write("") # 패딩용
            st.write("") 
            if st.button("저장", use_container_width=True):
                db.save_weight(date_str, new_weight)
                st.success("완료!")
                st.rerun() # 새로고침하면 아래 단백질 로직에서 즉시 반영됨!

    # 🚀 핵심: 체중 기반 단백질 목표치 자동 계산
    if current_weight and current_weight > 0:
        daily_min = current_weight * 1.2
        daily_max = current_weight * 2.0
        meal_min = current_weight * 0.3
        meal_max = current_weight * 0.4
        
        goal_pro = int(daily_min) # 목표치를 일일 최소 권장량으로 덮어쓰기!
        pro_guide_text = f"💡 체중({current_weight}kg) 기준 1일 권장량: **{daily_min:.0f}~{daily_max:.0f}g** | 1회: **{meal_min:.0f}~{meal_max:.0f}g**"
    else:
        goal_pro = 150 # 기본값 유지
        pro_guide_text = "💡 윗칸에 체중을 입력하고 [저장]을 누르면 단백질 권장량이 자동 계산됩니다."

    # DB에서 오늘 먹은 음식 가져오기
    records = db.get_diet_by_date(date_str)
    tot_cal = sum([r[3] for r in records])
    tot_carbs = sum([r[4] for r in records])
    tot_pro = sum([r[5] for r in records])
    tot_fat = sum([r[6] for r in records])
    
    st.subheader("🔥 오늘의 영양 달성도")
    st.write(f"**총 칼로리:** {tot_cal} / {goal_cal} kcal")
    st.progress(min(1.0, tot_cal / goal_cal) if goal_cal > 0 else 0)
    
    st.write(f"**탄수화물:** {tot_carbs} / {goal_carbs} g")
    st.progress(min(1.0, tot_carbs / goal_carbs) if goal_carbs > 0 else 0)
    
    # 🚀 웹사이트에도 단백질 안내 문구 띄우기
    st.write(f"**단백질:** {tot_pro} / {goal_pro} g")
    st.info(pro_guide_text) # 예쁜 파란색 박스로 안내 문구 출력
    st.progress(min(1.0, tot_pro / goal_pro) if goal_pro > 0 else 0)
    
    st.write(f"**지방:** {tot_fat} / {goal_fat} g")
    st.progress(min(1.0, tot_fat / goal_fat) if goal_fat > 0 else 0)
    
    st.divider()
    
    st.subheader("🍽️ 음식 추가하기")
    col1, col2 = st.columns([1, 2])
    meal_type = col1.selectbox("식사", ["아침", "점심", "저녁", "간식", "보충제"])
    food_name = col2.text_input("음식명 (예: 닭가슴살 100g)")
    
    c1, c2, c3, c4 = st.columns(4)
    cal = c1.number_input("칼로리", min_value=0, step=10)
    carbs = c2.number_input("탄(g)", min_value=0, step=1)
    pro = c3.number_input("단(g)", min_value=0, step=1)
    fat = c4.number_input("지(g)", min_value=0, step=1)
    
    if st.button("➕ 식단 추가", use_container_width=True, type="primary"):
        if food_name:
            db.insert_diet(date_str, meal_type, food_name, cal, carbs, pro, fat)
            st.success("음식이 추가되었습니다!")
            st.rerun()
        else:
            st.warning("음식 이름을 적어주세요!")

    if records:
        df_diet = pd.DataFrame(records, columns=["ID", "식사", "음식명", "칼로리", "탄", "단", "지"]).drop(columns=["ID"])
        st.dataframe(df_diet, use_container_width=True, hide_index=True)

# ==========================================
# 5. 📝 필기 노트 화면
# ==========================================
elif page == "📝 필기 노트":
    st.title("📝 헬스장 깨달음 노트")
    
    new_title = st.text_input("제목")
    new_content = st.text_area("내용")
    if st.button("💾 노트 저장하기", type="primary"):
        if new_title:
            db.save_note(new_title, new_content)
            st.success("노트가 저장되었습니다!")
            st.rerun()
            
    st.divider()
    st.subheader("📚 내 노트 목록")
    notes = db.get_all_notes()
    for note_id, title in notes:
        with st.expander(f"📌 {title}"):
            full_note = db.get_note_content(note_id)
            st.write(full_note[1]) 
            if st.button("🗑️ 삭제", key=f"del_{note_id}"):
                db.delete_note(note_id)
                st.rerun()

# ==========================================
# 6. ⚙️ 설정 및 종목 화면
# ==========================================
elif page == "⚙️ 설정 및 종목":
    st.title("⚙️ 운동 종목 관리")
    st.write("나만의 운동 루틴에 맞춰 종목을 추가/삭제하세요.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ 종목 추가")
        new_ex = st.text_input("새로운 운동 이름")
        if st.button("추가하기"):
            db.insert_exercise(new_ex)
            st.success(f"'{new_ex}' 추가 완료!")
            st.rerun()
            
    with col2:
        st.subheader("🗑️ 종목 삭제")
        exercises = db.get_all_exercises()
        del_ex = st.selectbox("삭제할 운동 이름", exercises)
        if st.button("삭제하기"):
            db.delete_exercise(del_ex)
            st.warning(f"'{del_ex}' 삭제 완료!")
            st.rerun()