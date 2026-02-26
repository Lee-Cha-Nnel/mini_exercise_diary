from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QLineEdit, QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from db_supabase import WorkoutDB

class ExerciseManager(QWidget):
    go_back_signal = pyqtSignal() # 🌟 메인으로 돌아가는 신호기

    def __init__(self):
        super().__init__()
        self.db = WorkoutDB()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #E8F0FE; font-family: 'Malgun Gothic';")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 40, 30, 40)
        
        # 🌟 상단 헤더 (뒤로가기 버튼 & 제목)
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("⬅️ 홈으로")
        self.back_btn.setStyleSheet("QPushButton { background: transparent; color: #3182CE; font-weight: bold; font-size: 15px; text-align: left; } QPushButton:hover { color: #2B6CB0; }")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.go_back_signal.emit)
        
        title = QLabel("⚙️ 운동 종목 관리")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1A365D;")
        
        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title)
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)

        # 🌟 하얀색 메인 카드 (리플렉틀리 감성)
        content_card = QFrame()
        content_card.setStyleSheet("QFrame { background-color: white; border-radius: 20px; }")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setXOffset(0); shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 15))
        content_card.setGraphicsEffect(shadow)
        
        content_layout = QVBoxLayout(content_card)
        content_layout.setContentsMargins(30, 30, 30, 30)

        # 종목 리스트
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: #F8FAFC; border: 1px solid #CBD5E0; border-radius: 10px; padding: 10px; font-size: 15px;")
        self.load_list()
        content_layout.addWidget(self.list_widget)
        content_layout.addSpacing(15)

        # 종목 추가 입력칸 & 버튼
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("새 종목 (예: 런지, 풀업)")
        self.input_field.setStyleSheet("padding: 12px; border-radius: 10px; border: 1px solid #CBD5E0; background: #F8FAFC; font-size: 14px;")
        
        self.add_btn = QPushButton("종목 추가")
        self.add_btn.setStyleSheet("background-color: #3182CE; color: white; padding: 12px 20px; border-radius: 10px; font-weight: bold; font-size: 14px;")
        self.add_btn.clicked.connect(self.add_exercise)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.add_btn)
        content_layout.addLayout(input_layout)

        # 삭제 버튼
        self.del_btn = QPushButton("선택한 종목 삭제하기")
        self.del_btn.setStyleSheet("background-color: #E53E3E; color: white; padding: 15px; border-radius: 10px; font-weight: bold; font-size: 14px; margin-top: 10px;")
        self.del_btn.clicked.connect(self.delete_exercise)
        content_layout.addWidget(self.del_btn)

        main_layout.addWidget(content_card)
        self.setLayout(main_layout)

    def load_list(self):
        self.list_widget.clear()
        exercises = self.db.get_all_exercises()
        self.list_widget.addItems(exercises)

    def add_exercise(self):
        name = self.input_field.text().strip()
        if name:
            self.db.insert_exercise(name)
            self.input_field.clear()
            self.load_list()

    def delete_exercise(self):
        selected = self.list_widget.currentItem()
        if selected:
            self.db.delete_exercise(selected.text())
            self.load_list()