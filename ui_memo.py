from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
                             QLabel, QLineEdit, QTextEdit, QPushButton, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from db_supabase import WorkoutDB

class MemoWindow(QWidget):
    go_back_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = WorkoutDB()
        self.current_note_id = None # 현재 열려있는 노트의 ID
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #E8F0FE; font-family: 'Malgun Gothic';")
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(40, 50, 40, 50)
        main_layout.setSpacing(30)

        # 📚 왼쪽 카드 (노트 목록)
        left_card = QFrame()
        left_card.setStyleSheet("QFrame { background-color: white; border-radius: 20px; }")
        left_card.setGraphicsEffect(self.create_shadow())
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(25, 25, 25, 25)

        header_left = QHBoxLayout()
        self.back_btn = QPushButton("⬅️ 홈으로")
        self.back_btn.setStyleSheet("QPushButton { background: transparent; color: #3182CE; font-weight: bold; font-size: 18px; text-align: left; } QPushButton:hover { color: #2B6CB0; }")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.go_back_signal.emit)
        
        cal_title = QLabel("📚 내 노트 목록")
        cal_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A365D;")
        
        header_left.addWidget(self.back_btn)
        header_left.addStretch()
        header_left.addWidget(cal_title)
        left_layout.addLayout(header_left)
        left_layout.addSpacing(15)

        self.new_btn = QPushButton("➕ 새 노트 작성하기")
        self.new_btn.setStyleSheet("QPushButton { background-color: #EDF2F7; color: #2D3748; border-radius: 10px; padding: 12px; font-weight: bold; font-size: 15px; } QPushButton:hover { background-color: #E2E8F0; }")
        self.new_btn.setCursor(Qt.PointingHandCursor)
        self.new_btn.clicked.connect(self.clear_editor)
        left_layout.addWidget(self.new_btn)
        left_layout.addSpacing(10)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("QListWidget { border: 1px solid #E2E8F0; border-radius: 10px; padding: 5px; font-size: 16px; background-color: #F8FAFC; } QListWidget::item { padding: 10px; border-bottom: 1px solid #E2E8F0; } QListWidget::item:selected { background-color: #3182CE; color: white; border-radius: 5px; }")
        self.list_widget.itemClicked.connect(self.load_note)
        left_layout.addWidget(self.list_widget)

        # ✍️ 오른쪽 카드 (노트 작성/수정)
        right_card = QFrame()
        right_card.setStyleSheet("QFrame { background-color: white; border-radius: 20px; }")
        right_card.setGraphicsEffect(self.create_shadow())
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(30, 30, 30, 30)

        header_right = QHBoxLayout()
        self.right_title = QLabel('✍️ 노트 내용')
        self.right_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A365D;")
        
        self.del_btn = QPushButton("🗑️ 삭제")
        self.del_btn.setStyleSheet("QPushButton { background-color: transparent; color: #E53E3E; font-weight: bold; font-size: 15px; } QPushButton:hover { color: #C53030; }")
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.clicked.connect(self.delete_current_note)
        self.del_btn.hide() # 처음엔 숨겨둠

        header_right.addWidget(self.right_title)
        header_right.addStretch()
        header_right.addWidget(self.del_btn)
        right_layout.addLayout(header_right)
        right_layout.addSpacing(15)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("노트 제목을 입력하세요 (예: 자극 잘 오는 등 운동 루틴)")
        self.title_input.setStyleSheet("QLineEdit { border: 1px solid #CBD5E0; border-radius: 8px; padding: 12px; font-size: 18px; font-weight: bold; background-color: #F8FAFC; }")
        right_layout.addWidget(self.title_input)

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("자유롭게 꿀팁, 식단, 목표 등을 적어보세요!")
        self.content_input.setStyleSheet("QTextEdit { border: 1px solid #CBD5E0; border-radius: 8px; padding: 15px; font-size: 16px; background-color: #F8FAFC; }")
        right_layout.addWidget(self.content_input)

        self.save_btn = QPushButton('노트 저장하기')
        self.save_btn.setStyleSheet("QPushButton { background-color: #3182CE; color: white; border-radius: 15px; padding: 15px; font-weight: bold; font-size: 16px; margin-top: 10px; } QPushButton:hover { background-color: #2B6CB0; }")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_current_note)
        right_layout.addWidget(self.save_btn)

        main_layout.addWidget(left_card, 2)
        main_layout.addWidget(right_card, 3) 
        self.setLayout(main_layout)
        self.refresh_list()

    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setXOffset(0); shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 15))
        return shadow

    def refresh_list(self):
        self.list_widget.clear()
        notes = self.db.get_all_notes()
        for note_id, title in notes:
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, note_id) # 눈에 안보이게 ID값을 숨겨둠
            self.list_widget.addItem(item)

    def clear_editor(self):
        self.current_note_id = None
        self.title_input.clear()
        self.content_input.clear()
        self.del_btn.hide()
        self.list_widget.clearSelection()

    def load_note(self, item):
        self.current_note_id = item.data(Qt.UserRole)
        title, content = self.db.get_note_content(self.current_note_id)
        self.title_input.setText(title)
        self.content_input.setText(content)
        self.del_btn.show()

    def save_current_note(self):
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        if not title:
            title = "제목 없는 노트"
            
        self.db.save_note(title, content, self.current_note_id)
        self.refresh_list()
        self.clear_editor() # 저장 후 초기화

    def delete_current_note(self):
        if self.current_note_id:
            self.db.delete_note(self.current_note_id)
            self.refresh_list()
            self.clear_editor()