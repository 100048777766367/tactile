import math
import random
import json
import os

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-max(min(x, 500), -500)))

class SkinCell:
    def __init__(self, receptor_id, storage_dir="synapses"):
        self.id = receptor_id
        self.storage_path = os.path.join(storage_dir, f"{self.id}.json")
        self.os_dir = storage_dir
        
        self.sensitivity = 1.0 # Độ nhạy cảm thụ
        self.threshold = 0.5   # Ngưỡng kích hoạt an toàn
        self.last_stimulus = 0.0
        
        self.load_self()

    def load_self(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                self.sensitivity = data.get("sensitivity", 1.0)
                self.threshold = data.get("threshold", 0.5)
                return
            except Exception:
                pass

        # TỰ KHỞI SINH: Tạo độ nhạy và ngưỡng cảm thụ ngẫu nhiên
        self.sensitivity = random.uniform(0.8, 1.3)
        self.threshold = random.uniform(0.3, 0.7)
        self.save_self()

    # THỤ CẢM KÍCH THÍCH: Đo lường mức độ kích ứng cơ học/nhiệt độ
    def sense(self, physical_stimulus):
        self.last_stimulus = physical_stimulus
        # Cường độ kích hoạt = Sigmoid(Độ nhạy * (Kích thích - Ngưỡng))
        delta = self.sensitivity * (physical_stimulus - self.threshold)
        activation = sigmoid(delta * 5.0) # Khuếch đại phản ứng khi vượt ngưỡng
        return round(activation, 4)

    # ĐIỀU CHỈNH THÍCH NGHI SINH HỌC (Thích nghi khi va chạm nhiều / Nhạy cảm khi đau)
    def adapt_from_brain_gradient(self, grad, lr=0.05):
        # Não bảo "nhạy cảm hơn" hoặc "bớt đau lại"
        self.sensitivity += lr * grad * self.last_stimulus
        self.sensitivity = max(0.2, min(3.0, self.sensitivity))
        self.save_self()

    def save_self(self):
        os.makedirs(self.os_dir, exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump({"sensitivity": round(self.sensitivity, 4), "threshold": round(self.threshold, 4)}, f, indent=4)
