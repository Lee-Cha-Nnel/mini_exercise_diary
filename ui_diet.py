from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QLineEdit, QSpinBox, QFrame, QGraphicsDropShadowEffect, 
                             QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QColor

from db_supabase import WorkoutDB

class DietWindow(QWidget):
    go_back_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = WorkoutDB()
        # 🎯 내 목표치 설정
        self.goal_cal = 2500
        self.goal_carbs = 300
        self.goal_pro = 150
        self.goal_fat = 70
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #F7FAFC; font-family: 'Malgun Gothic';")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(15)

        # --- 상단 헤더 (체중 입력창 추가됨) ---
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("⬅️ 홈으로")
        self.back_btn.setStyleSheet("QPushButton { background: transparent; color: #48BB78; font-weight: bold; font-size: 18px; text-align: left; }")
        self.back_btn.clicked.connect(self.go_back_signal.emit)
        
        # 날짜 선택기
        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setStyleSheet("padding: 8px; font-size: 18px; font-weight: bold; border-radius: 5px; border: 2px solid #48BB78;")
        self.date_picker.dateChanged.connect(self.load_diet_data)

        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()
        
        # 중앙 타이틀
        title_lbl = QLabel("🥗 식단 & 매크로 트래커")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #276749;")
        header_layout.addWidget(title_lbl)
        
        header_layout.addSpacing(40) # 타이틀과 체중 사이 간격

        # ⭐ 오늘의 체중 입력 섹션 (캡틴의 요청 위치!)
        weight_lbl = QLabel("⚖️ 공복 체중")
        weight_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #4A5568;")
        self.inp_weight = QLineEdit()
        self.inp_weight.setPlaceholderText("0.0")
        self.inp_weight.setFixedWidth(60)
        self.inp_weight.setStyleSheet("padding: 5px; border-radius: 5px; border: 1px solid #CBD5E0;")
        self.inp_weight.setAlignment(Qt.AlignCenter)
        
        self.btn_weight_save = QPushButton("확인")
        self.btn_weight_save.setStyleSheet("background-color: #4A5568; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;")
        self.btn_weight_save.clicked.connect(self.save_weight_data)

        header_layout.addWidget(weight_lbl)
        header_layout.addWidget(self.inp_weight)
        header_layout.addWidget(self.btn_weight_save)

        header_layout.addStretch()
        header_layout.addWidget(self.date_picker)
        main_layout.addLayout(header_layout)

        # 🌟 게이지 바 영역
        gauge_card = QFrame()
        gauge_card.setStyleSheet("QFrame { background-color: white; border-radius: 15px; }")
        gauge_card.setGraphicsEffect(self.create_shadow())
        gauge_layout = QVBoxLayout(gauge_card)
        gauge_layout.setContentsMargins(20, 20, 20, 20)

        self.cal_bar = self.create_bar("#ED8936")
        self.carbs_bar = self.create_bar("#4299E1")
        self.pro_bar = self.create_bar("#48BB78")
        self.fat_bar = self.create_bar("#ECC94B")

        self.lbl_cal = QLabel(f"🔥 총 칼로리: 0 / {self.goal_cal} kcal")
        self.lbl_carbs = QLabel(f"🍚 탄수화물: 0 / {self.goal_carbs} g")
        self.lbl_pro = QLabel(f"🍗 단백질: 0 / {self.goal_pro} g")
        self.lbl_fat = QLabel(f"🥑 지방: 0 / {self.goal_fat} g")

        for lbl in [self.lbl_cal, self.lbl_carbs, self.lbl_pro, self.lbl_fat]:
            lbl.setStyleSheet("font-weight: bold; font-size: 14px; color: #2D3748;")

        gauge_layout.addWidget(self.lbl_cal); gauge_layout.addWidget(self.cal_bar)
        gauge_layout.addWidget(self.lbl_carbs); gauge_layout.addWidget(self.carbs_bar)
        gauge_layout.addWidget(self.lbl_pro); gauge_layout.addWidget(self.pro_bar)
        gauge_layout.addWidget(self.lbl_fat); gauge_layout.addWidget(self.fat_bar)
        main_layout.addWidget(gauge_card)

        # 입력 폼
        input_layout = QHBoxLayout()
        self.combo_meal = QComboBox()
        self.combo_meal.addItems(["아침", "점심", "저녁", "간식", "보충제"])
        self.combo_meal.setStyleSheet("padding: 8px; font-size: 14px;")
        
        self.inp_food = QLineEdit()
        self.inp_food.setPlaceholderText("음식 이름 (예: 닭가슴살 100g)")
        self.inp_food.setStyleSheet("padding: 8px; font-size: 14px;")

        self.spin_cal = self.create_spin("kcal")
        self.spin_carbs = self.create_spin("탄(g)")
        self.spin_pro = self.create_spin("단(g)")
        self.spin_fat = self.create_spin("지(g)")

        btn_add = QPushButton("➕ 추가")
        btn_add.setStyleSheet("background-color: #48BB78; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        btn_add.clicked.connect(self.add_food)

        input_layout.addWidget(self.combo_meal)
        input_layout.addWidget(self.inp_food, 2)
        input_layout.addWidget(self.spin_cal)
        input_layout.addWidget(self.spin_carbs)
        input_layout.addWidget(self.spin_pro)
        input_layout.addWidget(self.spin_fat)
        input_layout.addWidget(btn_add)
        main_layout.addLayout(input_layout)

        # 테이블
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["ID", "분류", "음식 이름", "칼로리", "탄수화물", "단백질", "지방", "삭제"])
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: white; border-radius: 10px;")
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)
        self.load_diet_data()

    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15); shadow.setXOffset(0); shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 20))
        return shadow

    def create_bar(self, color):
        bar = QProgressBar()
        bar.setFixedHeight(18)
        bar.setStyleSheet(f"QProgressBar {{ border: 1px solid #E2E8F0; border-radius: 8px; background-color: #EDF2F7; text-align: center; color: transparent; }}"
                          f"QProgressBar::chunk {{ background-color: {color}; border-radius: 8px; }}")
        bar.setValue(0)
        return bar

    def create_spin(self, suffix):
        spin = QSpinBox()
        spin.setRange(0, 2000)
        spin.setSuffix(f" {suffix}")
        spin.setStyleSheet("padding: 8px; font-size: 14px;")
        return spin

    # --- ⭐ 체중 저장 함수 ---
    def save_weight_data(self):
        date = self.date_picker.date().toString("yyyy-MM-dd")
        try:
            val = float(self.inp_weight.text())
            self.db.save_weight(date, val)
            QMessageBox.information(self, "성공", f"{date} 체중이 저장되었습니다!")
        except ValueError:
            QMessageBox.warning(self, "경고", "체중을 숫자로 입력해주세요!")

    def add_food(self):
        date = self.date_picker.date().toString("yyyy-MM-dd")
        meal = self.combo_meal.currentText()
        food = self.inp_food.text()
        if not food: return
        cal = self.spin_cal.value()
        carbs = self.spin_carbs.value()
        pro = self.spin_pro.value()
        fat = self.spin_fat.value()

        self.db.insert_diet(date, meal, food, cal, carbs, pro, fat)
        self.inp_food.clear()
        self.spin_cal.setValue(0); self.spin_carbs.setValue(0); self.spin_pro.setValue(0); self.spin_fat.setValue(0)
        self.load_diet_data()

    def load_diet_data(self):
        date = self.date_picker.date().toString("yyyy-MM-dd")
        
        # ⭐ 체중 불러오기 추가
        weight = self.db.get_weight(date)
        self.inp_weight.setText(str(weight) if weight > 0 else "")

        records = self.db.get_diet_by_date(date)
        self.table.setRowCount(0)
        tot_cal, tot_carbs, tot_pro, tot_fat = 0, 0, 0, 0

        for row, record in enumerate(records):
            r_id, meal, food, cal, carbs, pro, fat = record
            tot_cal += cal; tot_carbs += carbs; tot_pro += pro; tot_fat += fat
            
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(r_id)))
            self.table.setItem(row, 1, QTableWidgetItem(meal))
            self.table.setItem(row, 2, QTableWidgetItem(food))
            self.table.setItem(row, 3, QTableWidgetItem(f"{cal} kcal"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{carbs} g"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{pro} g"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{fat} g"))
            
            del_btn = QPushButton("❌")
            del_btn.setStyleSheet("color: red; border: none; font-size: 16px;")
            del_btn.clicked.connect(lambda _, r=r_id: self.delete_record(r))
            self.table.setCellWidget(row, 7, del_btn)

        self.cal_bar.setValue(int(min(100, (tot_cal / self.goal_cal) * 100)))
        self.carbs_bar.setValue(int(min(100, (tot_carbs / self.goal_carbs) * 100)))
        self.pro_bar.setValue(int(min(100, (tot_pro / self.goal_pro) * 100)))
        self.fat_bar.setValue(int(min(100, (tot_fat / self.goal_fat) * 100)))

        self.lbl_cal.setText(f"🔥 총 칼로리: {tot_cal} / {self.goal_cal} kcal")
        self.lbl_carbs.setText(f"🍚 탄수화물: {tot_carbs} / {self.goal_carbs} g")
        self.lbl_pro.setText(f"🍗 단백질: {tot_pro} / {self.goal_pro} g")
        self.lbl_fat.setText(f"🥑 지방: {tot_fat} / {self.goal_fat} g")

    def delete_record(self, record_id):
        self.db.delete_diet(record_id)
        self.load_diet_data()