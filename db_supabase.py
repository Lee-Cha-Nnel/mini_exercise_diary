import os
from supabase import create_client, Client
from collections import defaultdict

class WorkoutDB:
    def __init__(self):
        # 🌟 캡틴의 전용 클라우드 주소와 마스터키!
        SUPABASE_URL = "https://rgfcaoxggegxknsmwfzh.supabase.co"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnZmNhb3hnZ2VneGtuc213ZnpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMjQ2NjMsImV4cCI6MjA4NzYwMDY2M30.NGwtA0WREz7Dr1gVTZOyS5js4Y90XZjdoOPHLb0RqCo"
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # --- 1. 운동 일지 기능 ---
    def insert_record(self, date, exercise, set_num, weight, reps):
        data = {"date": date, "exercise": exercise, "set_num": set_num, "weight": weight, "reps": reps}
        self.supabase.table("workout_records").insert(data).execute()

    def get_records_by_date(self, date):
        response = self.supabase.table("workout_records").select("exercise, set_num, weight, reps").eq("date", date).order("exercise").order("set_num").execute()
        return [(item['exercise'], item['set_num'], item['weight'], item['reps']) for item in response.data]

    def delete_exercise_records(self, date, exercise):
        self.supabase.table("workout_records").delete().eq("date", date).eq("exercise", exercise).execute()

    # --- 2. 종목 관리 기능 ---
    def insert_exercise(self, name):
        try:
            self.supabase.table("exercises").insert({"name": name}).execute()
        except Exception:
            pass 

    def get_all_exercises(self):
        response = self.supabase.table("exercises").select("name").order("id").execute()
        return [item['name'] for item in response.data]

    def delete_exercise(self, name):
        self.supabase.table("exercises").delete().eq("name", name).execute()

    # --- 3. 메모장 기능 ---
    def save_note(self, title, content, note_id=None):
        if note_id:
            self.supabase.table("notes").update({"title": title, "content": content}).eq("id", note_id).execute()
        else:
            self.supabase.table("notes").insert({"title": title, "content": content}).execute()

    def get_all_notes(self):
        response = self.supabase.table("notes").select("id, title").order("id", desc=True).execute()
        return [(item['id'], item['title']) for item in response.data]

    def get_note_content(self, note_id):
        response = self.supabase.table("notes").select("title, content").eq("id", note_id).execute()
        if response.data:
            return (response.data[0]['title'], response.data[0]['content'])
        return ("", "")

    def delete_note(self, note_id):
        self.supabase.table("notes").delete().eq("id", note_id).execute()

    # --- 4. 📊 심층 분석 ---
    def get_volume_and_1rm_trend(self, exercise, start_date, end_date):
        response = self.supabase.table("workout_records").select("date, weight, reps").eq("exercise", exercise).gte("date", start_date).lte("date", end_date).execute()
        
        trend_data = defaultdict(lambda: {'vol': 0, 'max_1rm': 0})
        
        for row in response.data:
            d = row['date']
            w = row['weight']
            r = row['reps']
            vol = w * r
            onerm = w * (1.0 + r / 30.0)
            
            trend_data[d]['vol'] += vol
            if onerm > trend_data[d]['max_1rm']:
                trend_data[d]['max_1rm'] = onerm
                
        result = []
        for d in sorted(trend_data.keys()):
            result.append((d, trend_data[d]['vol'], trend_data[d]['max_1rm']))
        return result

    # --- 5. 🥗 식단 트래커 ---
    def insert_diet(self, date, meal_type, food_name, cal, carbs, pro, fat):
        data = {"date": date, "meal_type": meal_type, "food_name": food_name, "calories": cal, "carbs": carbs, "protein": pro, "fat": fat}
        self.supabase.table("diet_records").insert(data).execute()

    def get_diet_by_date(self, date):
        response = self.supabase.table("diet_records").select("id, meal_type, food_name, calories, carbs, protein, fat").eq("date", date).execute()
        return [(item['id'], item['meal_type'], item['food_name'], item['calories'], item['carbs'], item['protein'], item['fat']) for item in response.data]

    def delete_diet(self, record_id):
        self.supabase.table("diet_records").delete().eq("id", record_id).execute()

    # --- ⭐ 6. 오늘의 체중 기능 (방금 추가됨!) ---
    def save_weight(self, date_str, weight):
        """날짜별 체중 저장 (이미 있으면 덮어쓰기)"""
        data = {"date": date_str, "weight": weight}
        self.supabase.table("body_weight").upsert(data).execute()

    def get_weight(self, date_str):
        """날짜별 체중 불러오기 (없으면 0.0)"""
        res = self.supabase.table("body_weight").select("weight").eq("date", date_str).execute()
        if res.data:
            return res.data[0]['weight']
        return 0.0