# EDL69 Streamlit Mobile Web Application

แอปพลิเคชันค้นหารายการยาหลักแห่งชาติ 2569 (Essential Drug List 2026) พัฒนาด้วย **Streamlit** ออกแบบสำหรับการใช้งานบนอุปกรณ์มือถือ (Mobile-Friendly Web App)

## คุณสมบัติเด่น (Features)
1. **🔍 ค้นหายาข้ามหมวดหมู่ (Global Search)**: พิมพ์ชื่อยา สารสำคัญ หรือเงื่อนไข เพื่อค้นหายาจากทุกหมวดอวัยวะ (17 กลุ่ม) ได้พร้อมกันทันที
2. **📁 เรียกดูตามระบบอวัยวะ (Browse Mode)**: เลือกตาม Organ System (กลุ่มยา 1 - 17) และ Subgroup (หมวดยาย่อย)
3. **🏷️ สัญลักษณ์แสดงประเภทบัญชียา (Category Badges)**:
   - `b`: บัญชียาพื้นฐาน (Basic list)
   - `s`: บัญชียาทางเลือก (Supplemental list)
   - `ex`: บัญชียาเฉพาะโรค (Exclusive list)
   - `R1`: ยาโครงการพิเศษ 1 (Restricted list 1)
   - `R2`: ยาควบคุมการสั่งใช้เป็นพิเศษ 2 (Restricted list 2)
4. **⚠️ คำเตือนและเงื่อนไขการใช้ยา**: แสดงหมายเหตุ และเงื่อนไขการใช้งานของยาแต่ละรายการ
5. **📱 Mobile-Optimized Design**: ออกแบบด้วย Dark Mode Theme ชัดเจนสบายตา และปรับการแสดงผลสำหรับสมาร์ตโฟน

## วิธีการติดตั้งและเริ่มใช้งาน (Run Locally)

### 1. เปิด Virtual Environment และติดตั้ง Dependencies
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. รันแอปพลิเคชัน Streamlit
```bash
streamlit run app.py
```
แอปพลิเคชันจะเปิดในเว็บเบราว์เซอร์ที่ `http://localhost:8501`
