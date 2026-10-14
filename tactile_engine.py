import json
import time
import os
from cells.skin_cell import SkinCell

class TactileEngine:
    def __init__(self):
        # 2 Tế bào thụ cảm: 1 đo Áp suất va chạm, 1 đo Nhiệt độ / Cơn đau
        self.mechanoreceptor = SkinCell("s_pressure")
        self.nociceptor = SkinCell("s_pain")

    # 1. CHIỀU XUÔI: CHẠM VÀO THẾ GIỚI -> PHÁT XUNG XÚC GIÁC & CƠN ĐAU
    def feel_and_emit(self, stimulus_data):
        pressure_raw = stimulus_data.get("pressure", 0.2)     # [0.0: nhẹ nhàng -> 1.0: đè nén cực mạnh]
        temperature_raw = stimulus_data.get("temperature", 37.0) # Nhiệt độ thực tế tính bằng độ C

        # Chuẩn hóa nhiệt độ sang thang đo [0.0, 1.0] (Nguy hiểm khi > 50 độ C)
        temp_normalized = min(1.0, max(0.0, (temperature_raw - 20.0) / 80.0))

        # 2 Tế bào da thụ cảm
        touch_intensity = self.mechanoreceptor.sense(pressure_raw)
        pain_level = self.nociceptor.sense(temp_normalized)

        features = [touch_intensity, pain_level]
        timestamp = int(time.time())

        packet_forward = {
            "contract": "bodhi.tactile.v1",
            "source": "tactile_skin",
            "timestamp": timestamp,
            "features": features,
            "raw_metrics": {
                "pressure": pressure_raw,
                "temperature_celsius": temperature_raw
            }
        }

        with open("synapse_forward.json", "w") as f:
            json.dump(packet_forward, f, indent=4)

        print("-" * 50)
        print(f"🩸 [LÀN DA CẢM NHẬN] Va chạm: {pressure_raw} | Nhiệt độ: {temperature_raw}°C")
        print(f"   Xung Thần Kinh -> [Tiếp xúc: {touch_intensity}, Cơn đau (Loss): {pain_level}]")
        if pain_level > 0.8:
            print("🚨 [CẢNH BÁO TỐI NGUY] ĐAU ĐỚN CỰC ĐẠI! NGUY CƠ BỎNG HOẶC DẬP NÁT MÔ!")
        print("-" * 50)
        return packet_forward

    # 2. CHIỀU NGƯỢC (SPLIT LEARNING): NÃO PHẢN HỒI ĐIỀU CHỈNH NGƯỠNG ĐAU
    def absorb_brain_feedback(self, backward_file="verified_backward.json"):
        if not os.path.exists(backward_file):
            print("🍃 [MÔI TRƯỜNG TĨNH] Chưa có xung đạo hàm phản hồi từ Não.")
            return

        try:
            with open(backward_file, "r") as f:
                data = json.load(f)
            grads = data.get("gradients_for_eye", [0.0, 0.0])
            print(f"⚡ [NHẬN ĐẠO HÀM TỪ NÃO] Gradient = {grads}")

            self.mechanoreceptor.adapt_from_brain_gradient(grads[0])
            self.nociceptor.adapt_from_brain_gradient(grads[1])
            print("🔧 [TIẾN HÓA] Da đã tự điều chỉnh lại ngưỡng cảm thụ và độ nhạy cảm đau!")
        except Exception as e:
            print(f"⚠️ Lỗi đọc xung đạo hàm: {e}")

if __name__ == "__main__":
    skin = TactileEngine()
    skin.absorb_brain_feedback()

    # Thử nghiệm một kích thích vật lý nguy hiểm: Chạm vào vật nóng 85°C kèm áp suất mạnh
    kich_thich_nguy_hiem = {
        "pressure": 0.85,
        "temperature": 85.0
    }
    skin.feel_and_emit(kich_thich_nguy_hiem)
