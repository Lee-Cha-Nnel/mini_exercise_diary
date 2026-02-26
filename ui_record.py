from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QCalendarWidget, 
                             QLabel, QSpinBox, QPushButton, 
                             QFrame, QGraphicsDropShadowEffect, QScrollArea, QStackedWidget)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QColor
from db_supabase import WorkoutDB

class SetRow(QWidget):
    def __init__(self, set_num, prev_weight=0, prev_reps=0):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)

        self.set_label = QLabel(f"{set_num}세트")
        self.set_label.setStyleSheet("font-weight: bold; color: #4A5568; font-size: 14px; width: 45px;")
        
        inner_style = "background-color: white; border: 1px solid #CBD5E0; border-radius: 5px; padding: 3px; font-size: 14px;"
        
        self.weight_input = QSpinBox()
        self.weight_input.setRange(0, 500)
        self.weight_input.setValue(prev_weight)
        self.weight_input.setSuffix(' kg')
        self.weight_input.setStyleSheet(inner_style)
        
        self.reps_input = QSpinBox()
        self.reps_input.setRange(1, 100)
        self.reps_input.setValue(prev_reps)
        self.reps_input.setSuffix(' 개') 
        self.reps_input.setStyleSheet(inner_style)

        self.del_btn = QPushButton("❌")
        self.del_btn.setStyleSheet("background-color: transparent; font-size: 12px; padding: 0px;")
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.clicked.connect(self.delete_self)

        layout.addWidget(self.set_label)
        layout.addWidget(self.weight_input)
        layout.addWidget(self.reps_input)
        layout.addWidget(self.del_btn)
        self.setLayout(layout)

    def delete_self(self):
        self.setParent(None)
        self.deleteLater()

class ExerciseBlock(QFrame):
    def __init__(self, exercise_name):
        super().__init__()
        self.exercise_name = exercise_name
        self.set_count = 0
        self.initUI()

    def initUI(self):
        self.setStyleSheet("QFrame { background-color: #F8FAFC; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 8px; padding: 8px; }")
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5) 
        self.main_layout.setSpacing(5) 
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5) 
        name_label = QLabel(f"💪 {self.exercise_name}")
        name_label.setStyleSheet("font-weight: bold; color: #2C3E50; font-size: 16px; border: none; padding: 0px;")
        
        block_del_btn = QPushButton("종목 삭제")
        block_del_btn.setStyleSheet("background-color: #FED7D7; color: #C53030; border-radius: 5px; padding: 4px 8px; font-size: 12px; font-weight: bold; border: none;")
        block_del_btn.setCursor(Qt.PointingHandCursor)
        block_del_btn.clicked.connect(self.delete_block)
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(block_del_btn)
        self.main_layout.addLayout(header_layout)

        self.sets_layout = QVBoxLayout()
        self.sets_layout.setSpacing(2) 
        self.main_layout.addLayout(self.sets_layout)

        add_set_btn = QPushButton("➕ 세트 추가")
        add_set_btn.setStyleSheet("background-color: #E2E8F0; color: #4A5568; border-radius: 5px; padding: 6px; font-size: 13px; font-weight: bold; border: none; margin-top: 5px;")
        add_set_btn.setCursor(Qt.PointingHandCursor)
        add_set_btn.clicked.connect(self.add_set)
        self.main_layout.addWidget(add_set_btn)

        self.setLayout(self.main_layout)
        self.add_set() 

    def add_set(self):
        self.set_count += 1
        prev_w, prev_r = 0, 0
        
        if self.sets_layout.count() > 0:
            last_widget = self.sets_layout.itemAt(self.sets_layout.count() - 1).widget()
            if isinstance(last_widget, SetRow):
                prev_w = last_widget.weight_input.value()
                prev_r = last_widget.reps_input.value()

        set_row = SetRow(self.set_count, prev_w, prev_r)
        self.sets_layout.addWidget(set_row)

    def delete_block(self):
        self.setParent(None)
        self.deleteLater()


class RecordWindow(QWidget):
    go_back_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = WorkoutDB()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #E8F0FE; font-family: 'Malgun Gothic';")
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(40, 50, 40, 50)
        main_layout.setSpacing(30)

        # 🗓️ 왼쪽 카드
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
        
        cal_title = QLabel("🗓️ 날짜 선택")
        cal_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A365D;")
        
        header_left.addWidget(self.back_btn)
        header_left.addStretch()
        header_left.addWidget(cal_title)
        left_layout.addLayout(header_left)
        left_layout.addSpacing(15)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("QCalendarWidget QWidget { background-color: white; } QCalendarWidget QAbstractItemView:enabled { font-size: 14px; selection-background-color: #3182CE; selection-color: white; border-radius: 5px; }")
        self.calendar.clicked[QDate].connect(self.on_date_clicked)
        left_layout.addWidget(self.calendar)
        left_layout.addStretch()

        # 📝 오른쪽 카드
        right_card = QFrame()
        right_card.setStyleSheet("QFrame { background-color: white; border-radius: 20px; }")
        right_card.setGraphicsEffect(self.create_shadow())
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()
        self.right_title = QLabel('📋 날짜 선택 대기 중...')
        self.right_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A365D;")
        
        self.toggle_btn = QPushButton('➕ 새 운동 추가')
        self.toggle_btn.setStyleSheet("QPushButton { background-color: #EDF2F7; color: #2D3748; border-radius: 15px; padding: 10px 18px; font-weight: bold; font-size: 15px; } QPushButton:hover { background-color: #E2E8F0; }")
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_mode)

        header_layout.addWidget(self.right_title)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_btn)
        right_layout.addLayout(header_layout)
        right_layout.addSpacing(15)

        self.stacked_widget = QStackedWidget()

        # [보기 모드]
        self.view_page = QWidget()
        view_layout = QVBoxLayout(self.view_page)
        view_layout.setContentsMargins(0, 0, 0, 0)
        
        self.view_scroll = QScrollArea()
        self.view_scroll.setWidgetResizable(True)
        self.view_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.view_content = QWidget()
        self.view_content.setStyleSheet("background-color: transparent;")
        self.view_records_layout = QVBoxLayout(self.view_content)
        self.view_records_layout.setAlignment(Qt.AlignTop)
        self.view_scroll.setWidget(self.view_content)
        view_layout.addWidget(self.view_scroll)
        self.stacked_widget.addWidget(self.view_page)

        # [추가 모드]
        self.add_page = QWidget()
        add_layout = QVBoxLayout(self.add_page)
        add_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tags_layout = QHBoxLayout()
        add_layout.addLayout(self.tags_layout)
        self.load_tags() 

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.blocks_layout = QVBoxLayout(self.scroll_content)
        self.blocks_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        add_layout.addWidget(self.scroll_area)

        self.save_btn = QPushButton('선택한 운동 모두 저장하기')
        self.save_btn.setStyleSheet("QPushButton { background-color: #3182CE; color: white; border-radius: 20px; padding: 15px; font-weight: bold; margin-top: 15px; font-size: 16px; } QPushButton:hover { background-color: #2B6CB0; }")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_workout)
        add_layout.addWidget(self.save_btn)
        
        self.stacked_widget.addWidget(self.add_page)
        right_layout.addWidget(self.stacked_widget)

        main_layout.addWidget(left_card, 5)
        main_layout.addWidget(right_card, 6) 
        self.setLayout(main_layout)
        self.on_date_clicked(QDate.currentDate())

    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setXOffset(0); shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 15))
        return shadow

    def load_tags(self):
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()
        
        exercises = self.db.get_all_exercises()
        for ex in exercises:
            btn = QPushButton(ex)
            btn.setStyleSheet("QPushButton { background-color: #E2E8F0; color: #2D3748; border-radius: 12px; padding: 8px 12px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #CBD5E0; }")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, e=ex: self.add_exercise_block(e))
            self.tags_layout.addWidget(btn)
        self.tags_layout.addStretch()

    def toggle_mode(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0:
            self.stacked_widget.setCurrentIndex(1)
            self.right_title.setText(f'💪 {self.selected_date} 운동 추가')
            self.toggle_btn.setText('📋 기록 보기')
        else:
            self.stacked_widget.setCurrentIndex(0)
            self.right_title.setText(f'📋 {self.selected_date} 완료한 운동')
            self.toggle_btn.setText('➕ 새 운동 추가')

    def on_date_clicked(self, date):
        self.selected_date = date.toString('yyyy-MM-dd')
        self.stacked_widget.setCurrentIndex(0)
        self.right_title.setText(f'📋 {self.selected_date} 완료한 운동')
        self.toggle_btn.setText('➕ 새 운동 추가')
        self.load_records()

    def add_exercise_block(self, exercise_name):
        block = ExerciseBlock(exercise_name)
        self.blocks_layout.addWidget(block)

    def load_records(self):
        for i in reversed(range(self.view_records_layout.count())):
            widget = self.view_records_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        records = self.db.get_records_by_date(self.selected_date)
        if not records:
            empty_label = QLabel("저장된 기록이 없습니다.\n\n우측 상단의 [➕ 새 운동 추가] 버튼을 눌러보세요!")
            empty_label.setStyleSheet("color: #718096; font-size: 16px; margin-top: 20px;") 
            self.view_records_layout.addWidget(empty_label)
            return

        grouped_records = {}
        for r in records:
            ex_name, set_num, weight, reps = r
            if ex_name not in grouped_records:
                grouped_records[ex_name] = []
            grouped_records[ex_name].append((set_num, weight, reps))

        for ex_name, sets in grouped_records.items():
            card = QFrame()
            # 🌟 보기 모드 카드의 전체적인 패딩을 15->10, 하단 여백을 12->8로 축소
            card.setStyleSheet("QFrame { background-color: #F8FAFC; border-radius: 10px; border: 1px solid #E2E8F0; padding: 10px; margin-bottom: 8px; }")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(5, 5, 5, 5) # 🌟 내부 여백 타이트하게 세팅
            card_layout.setSpacing(2) # 🌟 줄과 줄 사이 간격을 확 줄였습니다!
            
            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 4) # 🌟 제목과 세트 내용 사이의 간격도 좁혔습니다.
            title = QLabel(f"✔️ {ex_name}")
            title.setStyleSheet("font-weight: bold; color: #2C3E50; font-size: 17px; border: none; padding: 0px;") 
            
            del_btn = QPushButton("🗑️ 이 운동 지우기")
            del_btn.setStyleSheet("background-color: transparent; color: #E53E3E; font-size: 13px; font-weight: bold; border: none; padding: 0px;") 
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.clicked.connect(lambda checked, e=ex_name: self.delete_record_from_db(e))

            header.addWidget(title)
            header.addStretch()
            header.addWidget(del_btn)
            card_layout.addLayout(header)

            for s_num, w, r in sets:
                set_label = QLabel(f"    - {s_num}세트: {w}kg x {r}개")
                # 🌟 불필요한 위아래 마진(margin-top)을 완전히 날려버렸습니다!
                set_label.setStyleSheet("color: #4A5568; font-size: 15px; border: none; margin-top: 0px; padding: 0px;") 
                card_layout.addWidget(set_label)
            
            self.view_records_layout.addWidget(card)

    def delete_record_from_db(self, exercise_name):
        self.db.delete_exercise_records(self.selected_date, exercise_name)
        self.load_records() 

    def save_workout(self):
        blocks_to_save = []
        for i in range(self.blocks_layout.count()):
            item = self.blocks_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if isinstance(widget, ExerciseBlock):
                    blocks_to_save.append(widget)
                    
        for widget in blocks_to_save:
            exercise = widget.exercise_name
            actual_set_num = 1
            for j in range(widget.sets_layout.count()):
                set_item = widget.sets_layout.itemAt(j).widget()
                if isinstance(set_item, SetRow):
                    weight = set_item.weight_input.value()
                    reps = set_item.reps_input.value()
                    self.db.insert_record(self.selected_date, exercise, actual_set_num, weight, reps)
                    actual_set_num += 1
                    
            widget.delete_block()
                
        self.load_records()
        self.toggle_mode()