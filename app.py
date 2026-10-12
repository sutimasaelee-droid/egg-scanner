import streamlit as st
import cv2
import numpy as np

st.title("🥚 โปรแกรมสแกนคัดแยกเบอร์ไข่ (โหมดฟิกซ์ระยะมาตรฐาน)")
st.write("วางไข่ไว้ในจุดที่กำหนด (ระยะห่างกล้อง ~20 ซม.) สามารถวางได้ทุกมุม แล้วกดถ่ายรูปได้เลย")

# เปิดกล้องถ่ายรูปผ่านมือถือหรือแท็บเล็ต
img_file = st.camera_input("กดถ่ายรูปไข่ตรงนี้")

if img_file is not None:
    # อ่านไฟล์รูปภาพจากกล้อง
    bytes_data = img_file.getvalue()
    cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # 1. แปลงภาพเป็น Grayscale และเบลอเพื่อลดจุดรบกวน
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 2. ใช้ Otsu's Thresholding เพื่อแยกตัวไข่ออกจากพื้นหลังอย่างแม่นยำ
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 3. ค้นหารูปร่างขอบเขตของไข่
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        # เลือกคอนทัวร์ที่มีขนาดใหญ่ที่สุด (ตัวไข่)
        c = max(contours, key=cv2.contourArea)
        
        # กรองขนาดขั้นต่ำ ป้องกันจับโดนเศษฝุ่นหรือวัตถุเล็กๆ บนโต๊ะ
        if cv2.contourArea(c) > 800:  
            # คำนวณกรอบสี่เหลี่ยมขั้นต่ำ (รองรับไข่ทุกมุมเอียง ซ้าย ขวา กลับหัว)
            rect = cv2.minAreaRect(c)
            (x, y), (w_px, h_px), angle = rect

            # ==========================================================
            # 📌 ค่าสเกลสำหรับระยะฟิกซ์ 20 ซม. 
            # ==========================================================
            pixels_per_mm = 8.5 

            width_mm = w_px / pixels_per_mm
            length_mm = h_px / pixels_per_mm

            # จัดระเบียบให้ด้านที่แคบกว่าเป็นความกว้าง ด้านที่ยาวกว่าเป็นความยาวเสมอ
            if width_mm > length_mm:
                width_mm, length_mm = length_mm, width_mm

            # 4. เกณฑ์การคัดแยกเบอร์ไข่มาตรฐาน
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

            # แสดงผลลัพธ์ความสำเร็จบนหน้าจอเว็บ
            st.success(f"ผลการคัดแยก: {egg_grade}")
            st.info(f"📏 ขนาดที่วัดได้ - ความกว้าง: {width_mm:.1f} มม. | ความยาว: {length_mm:.1f} มม.")
        else:
            st.error("ไม่พบวัตถุขนาดใหญ่พอ กรุณาวางไข่ให้อยู่กลางกล้องในระยะที่กำหนด")
    else:
        st.error("ไม่พบไข่ในรูป กรุณาถ่ายใหม่อีกครั้ง")
