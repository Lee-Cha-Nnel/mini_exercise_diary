from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QFrame, QGraphicsDropShadowEffect, QDateEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QColor

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from db_supabase import WorkoutDB

# 한글 폰트 깨짐 방지 세팅
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class AnalysisWindow(QWidget):
    go_back_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = WorkoutDB()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #E8F0FE; font-family: 'Malgun Gothic';")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # 🌟 상단: 뒤로가기 및 제목
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("⬅️ 홈으로")
        self.back_btn.setStyleSheet("QPushButton { background: transparent; color: #3182CE; font-weight: bold; font-size: 18px; text-align: left; } QPushButton:hover { color: #2B6CB0; }")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.go_back_signal.emit)
        
        title = QLabel("📊 심층 분석 대시보드")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1A365D;")
        
        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addSpacing(80) 
        main_layout.addLayout(header_layout)

        # 🌟 하단: 그래프 영역
        graph_card = QFrame()
        graph_card.setStyleSheet("QFrame { background-color: white; border-radius: 15px; }")
        graph_card.setGraphicsEffect(self.create_shadow())
        graph_layout = QVBoxLayout(graph_card)
        graph_layout.setContentsMargins(20, 20, 20, 20)

        # ==========================================
        # 🎛️ 기간 및 종목 컨트롤 패널 (새로 추가된 필터 구역)
        # ==========================================
        control_layout = QHBoxLayout()
        
        # 1. 기간 프리셋 (옵션 1)
        control_layout.addWidget(QLabel("📅 기간:"))
        self.period_selector = QComboBox()
        self.period_selector.addItems(["최근 1주일", "최근 1개월", "최근 3개월", "전체 기간", "직접 지정"])
        self.period_selector.setCurrentIndex(1) # 기본값: 최근 1개월
        self.period_selector.setStyleSheet("padding: 8px; font-size: 14px; border-radius: 5px; border: 1px solid #CBD5E0;")
        self.period_selector.currentIndexChanged.connect(self.update_date_range)
        control_layout.addWidget(self.period_selector)

        # 2. 시작/종료 달력 (옵션 2)
        self.start_date_edit = QDateEdit()
        self.end_date_edit = QDateEdit()
        for date_edit in [self.start_date_edit, self.end_date_edit]:
            date_edit.setCalendarPopup(True)
            date_edit.setStyleSheet("padding: 8px; font-size: 14px; border-radius: 5px; border: 1px solid #CBD5E0;")
            
        control_layout.addWidget(self.start_date_edit)
        control_layout.addWidget(QLabel("~"))
        control_layout.addWidget(self.end_date_edit)
        
        control_layout.addSpacing(20)

        # 3. 종목 선택 및 조회 버튼
        control_layout.addWidget(QLabel("📌 종목:"))
        self.exercise_selector = QComboBox()
        self.exercise_selector.setStyleSheet("padding: 8px; font-size: 14px; border-radius: 5px; border: 1px solid #CBD5E0; min-width: 130px;")
        control_layout.addWidget(self.exercise_selector)
        
        self.draw_btn = QPushButton("📈 조회하기")
        self.draw_btn.setStyleSheet("background-color: #3182CE; color: white; padding: 8px 20px; border-radius: 8px; font-weight: bold; font-size: 14px;")
        self.draw_btn.setCursor(Qt.PointingHandCursor)
        self.draw_btn.clicked.connect(self.draw_graph)
        control_layout.addWidget(self.draw_btn)
        
        control_layout.addStretch()
        graph_layout.addLayout(control_layout)

        # Matplotlib 캔버스 준비
        self.figure, self.ax1 = plt.subplots(figsize=(9, 5))
        self.ax2 = self.ax1.twinx()
        self.canvas = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas)

        main_layout.addWidget(graph_card, 1)
        self.setLayout(main_layout)
        
        # 초기 날짜 세팅 (최근 1개월)
        self.update_date_range()

    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setXOffset(0); shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 15))
        return shadow

    def load_exercises(self):
        self.exercise_selector.clear()
        self.exercise_selector.addItems(self.db.get_all_exercises())

    def update_date_range(self):
        """콤보박스 선택에 따라 시작/종료 날짜를 자동으로 바꿔줍니다."""
        idx = self.period_selector.currentIndex()
        today = QDate.currentDate()
        self.end_date_edit.setDate(today)

        if idx == 0: # 1주일
            self.start_date_edit.setDate(today.addDays(-7))
        elif idx == 1: # 1개월
            self.start_date_edit.setDate(today.addMonths(-1))
        elif idx == 2: # 3개월
            self.start_date_edit.setDate(today.addMonths(-3))
        elif idx == 3: # 전체 기간
            self.start_date_edit.setDate(QDate(2000, 1, 1))

        # '직접 지정'이 아니면 달력을 못 만지게 잠금 (편의성)
        is_custom = (idx == 4)
        self.start_date_edit.setReadOnly(not is_custom)
        self.end_date_edit.setReadOnly(not is_custom)

    def draw_graph(self):
        ex = self.exercise_selector.currentText()
        if not ex: return

        # 선택된 날짜 구간 가져오기
        start_str = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_str = self.end_date_edit.date().toString("yyyy-MM-dd")

        self.ax1.clear()
        self.ax2.clear()

        # DB에서 해당 구간 데이터만 뽑아오기
        data = self.db.get_volume_and_1rm_trend(ex, start_str, end_str)
        
        if not data:
            self.ax1.text(0.5, 0.5, f"선택하신 기간({start_str} ~ {end_str}) 내에\n해당 종목의 기록이 없습니다.", 
                          ha='center', va='center', fontsize=14, color='gray')
        else:
            # X축(날짜) 텍스트 명확하게 표시 ('MM-DD' 형식)
            dates = [d[0][-5:] for d in data] 
            volumes = [d[1] for d in data]
            onerms = [round(d[2], 1) for d in data]

            bars = self.ax1.bar(dates, volumes, color='#E2E8F0', edgecolor='#CBD5E0', label='총 볼륨 (kg)', width=0.5)
            self.ax1.set_ylabel('총 볼륨 (kg)', color='#718096', fontweight='bold', fontsize=12)
            self.ax1.tick_params(axis='y', labelcolor='#718096')
            self.ax1.set_ylim(0, max(volumes) * 1.3)
            
            lines = self.ax2.plot(dates, onerms, marker='o', color='#E53E3E', linewidth=3, markersize=8, label='추정 1RM (kg)')
            self.ax2.set_ylabel('추정 1RM (kg)', color='#E53E3E', fontweight='bold', fontsize=12)
            self.ax2.tick_params(axis='y', labelcolor='#E53E3E')
            
            for i, v in enumerate(onerms):
                self.ax2.text(i, v + (max(onerms)*0.02), f"{v}kg", ha='center', va='bottom', color='#C53030', fontweight='bold')

            # 🌟 X축 설명 텍스트 (사용자가 쉽게 이해하도록)
            self.ax1.set_xlabel('운동한 날짜 (월-일)', fontweight='bold', fontsize=11, color='#4A5568')
            self.ax1.set_title(f"🚀 '{ex}' 성장 퍼포먼스", fontsize=16, fontweight='bold', pad=20)
            self.ax1.grid(axis='y', linestyle='--', alpha=0.3)
            
            lines_1, labels_1 = self.ax1.get_legend_handles_labels()
            lines_2, labels_2 = self.ax2.get_legend_handles_labels()
            self.ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

        self.figure.tight_layout()
        self.canvas.draw()