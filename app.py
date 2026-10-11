import streamlit as st
import cv2
import numpy as np

st.title("🥚 โปรแกรมสแกนคัดแยกเบอร์ไข่")
st.write("ถ่ายรูปไข่ หรืออัปโหลดรูป เพื่อคัดแยกเบอร์ไข่ทันที")

# สร้างปุ่มเปิดกล้องถ่ายสด หรือเลือกรูปจากมือถือ
img_file = st.camera_input("กดถ่ายรูปไข่ตรงนี้")

if img_file is not None:
    # อ่านไฟล์รูปจากกล้องมือถือ
    bytes_data = img_file.getvalue()
    cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # แปลงภาพและตรวจจับขอบ
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)

    # ค้นหารูปร่างของไข่
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(c)
        (x, y), (w_px, h_px), angle = rect

        # แปลงพิกเซลเป็นมิลลิเมตร (ปรับตามระยะกล้องมือถือได้)
        pixels_per_mm = 10 
        width_mm = w_px / pixels_per_mm
        length_mm = h_px / pixels_per_mm

        if width_mm > length_mm:
            width_mm, length_mm = length_mm, width_mm

        # คัดแยกเบอร์ไข่ (1 ถึง 6)
        if width_mm >= 47 and length_mm >= 60:
            egg_grade = "🥚 ไข่เบอร์ 1 (ขนาดใหญ่พิเศษ)"
        elif width_mm >= 45 and length_mm >= 57:
            egg_grade = "🥚 ไข่เบอร์ 2 (ขนาดใหญ่)"
        elif width_mm >= 43 and length_mm >= 54:
            egg_grade = "🥚 ไข่เบอร์ 3 (ขนาดกลาง)"
        elif width_mm >= 41 and length_mm >= 51:
            egg_grade = "🥚 ไข่เบอร์ 4 (ขนาดเล็ก)"
        elif width_mm >= 39 and length_mm >= 48:
            egg_grade = "🥚 ไข่เบอร์ 5 (ขนาดเล็กมาก)"
        else:
            egg_grade = "🥚 ไข่เบอร์ 6 (ขนาดจิ๋ว)"

        # แสดงผลลัพธ์หน้าเว็บมือถือ
        st.success(f"ผลการคัดแยก: {egg_grade}")
        st.info(f"ความกว้าง: {width_mm:.1f} มม. | ความยาว: {length_mm:.1f} มม.")
    else:
        st.error("ไม่พบไข่ในรูป กรุณาถ่ายใหม่อีกครั้ง")
