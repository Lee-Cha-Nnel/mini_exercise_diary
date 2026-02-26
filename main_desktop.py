import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui_record import RecordWindow
from ui_manage import ExerciseManager
from ui_memo import MemoWindow
from ui_analysis import AnalysisWindow
from ui_diet import DietWindow # 🌟 식단 UI 불러오기!

class AppController(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('나만의 운동일지') 
        self.resize(1100, 750) 

        self.stacked_widget = QStackedWidget()

        self.home_page = self.create_home_page()
        self.stacked_widget.addWidget(self.home_page)

        self.record_page = RecordWindow()
        self.stacked_widget.addWidget(self.record_page)
        self.record_page.go_back_signal.connect(self.go_home)

        self.manage_page = ExerciseManager()
        self.stacked_widget.addWidget(self.manage_page)
        self.manage_page.go_back_signal.connect(self.go_home)

        self.memo_page = MemoWindow()
        self.stacked_widget.addWidget(self.memo_page)
        self.memo_page.go_back_signal.connect(self.go_home)

        self.analysis_page = AnalysisWindow()
        self.stacked_widget.addWidget(self.analysis_page)
        self.analysis_page.go_back_signal.connect(self.go_home)

        # 🌟 [인덱스 5] 식단 관리 화면 추가
        self.diet_page = DietWindow()
        self.stacked_widget.addWidget(self.diet_page)
        self.diet_page.go_back_signal.connect(self.go_home)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def create_home_page(self):
        page = QWidget()
        page.setStyleSheet("background-color: #E8F0FE; font-family: 'Malgun Gothic';")
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 60, 40, 60)
        
        title = QLabel('❄️ 나만의 운동일지 ❄️') 
        title.setAlignment(Qt.AlignCenter)
        font = QFont(); font.setPointSize(34); font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #1A365D; margin-top: 40px;")
        layout.addWidget(title)
        layout.addSpacing(40)

        # 💪 운동 일지 작성
        btn_start = QPushButton('💪 일지 작성하기')
        btn_start.setMinimumHeight(80) 
        btn_start.setStyleSheet("QPushButton { background-color: #3182CE; color: white; border-radius: 40px; font-size: 24px; font-weight: bold; } QPushButton:hover { background-color: #2B6CB0; }")
        btn_start.setCursor(Qt.PointingHandCursor)
        btn_start.clicked.connect(self.go_to_record)
        layout.addWidget(btn_start)
        layout.addSpacing(20)

        # 📊 심층 분석
        btn_analysis = QPushButton('📊 데이터 심층 분석')
        btn_analysis.setMinimumHeight(70) 
        btn_analysis.setStyleSheet("QPushButton { background-color: #DD6B20; color: white; border-radius: 35px; font-size: 20px; font-weight: bold; } QPushButton:hover { background-color: #C05621; }")
        btn_analysis.setCursor(Qt.PointingHandCursor)
        btn_analysis.clicked.connect(self.go_to_analysis)
        layout.addWidget(btn_analysis)
        layout.addSpacing(20)

        # 🥗 식단 트래커 (초록색 신규 버튼!)
        btn_diet = QPushButton('🥗 식단 & 매크로 트래커')
        btn_diet.setMinimumHeight(70) 
        btn_diet.setStyleSheet("QPushButton { background-color: #48BB78; color: white; border-radius: 35px; font-size: 20px; font-weight: bold; } QPushButton:hover { background-color: #38A169; }")
        btn_diet.setCursor(Qt.PointingHandCursor)
        btn_diet.clicked.connect(self.go_to_diet)
        layout.addWidget(btn_diet)
        layout.addSpacing(20)

        # 하단: 노트 & 설정 
        bottom_btn_layout = QHBoxLayout()
        
        btn_memo = QPushButton('📝 필기 노트')
        btn_memo.setMinimumHeight(70) 
        btn_memo.setStyleSheet("QPushButton { background-color: #4A5568; color: white; border-radius: 35px; font-size: 18px; font-weight: bold; } QPushButton:hover { background-color: #2D3748; }")
        btn_memo.setCursor(Qt.PointingHandCursor)
        btn_memo.clicked.connect(self.go_to_memo)

        btn_manage = QPushButton('⚙️ 종목 관리')
        btn_manage.setMinimumHeight(70) 
        btn_manage.setStyleSheet("QPushButton { background-color: #A0AEC0; color: white; border-radius: 35px; font-size: 18px; font-weight: bold; } QPushButton:hover { background-color: #718096; }")
        btn_manage.setCursor(Qt.PointingHandCursor)
        btn_manage.clicked.connect(self.go_to_manage)

        bottom_btn_layout.addWidget(btn_memo)
        bottom_btn_layout.addWidget(btn_manage)
        
        layout.addLayout(bottom_btn_layout)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def go_to_record(self):
        self.record_page.load_tags() 
        self.stacked_widget.setCurrentIndex(1)

    def go_to_manage(self):
        self.manage_page.load_list() 
        self.stacked_widget.setCurrentIndex(2)

    def go_to_memo(self):
        self.memo_page.refresh_list()
        self.stacked_widget.setCurrentIndex(3)

    def go_to_analysis(self):
        self.analysis_page.load_exercises()
        self.stacked_widget.setCurrentIndex(4)

    def go_to_diet(self): # 🌟 식단 창으로 이동
        self.diet_page.load_diet_data()
        self.stacked_widget.setCurrentIndex(5)

    def go_home(self):
        self.stacked_widget.setCurrentIndex(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AppController()
    ex.show()
    sys.exit(app.exec_())