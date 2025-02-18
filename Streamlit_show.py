import streamlit as st
import json
import time


record_path = r"C:\Users\spd-d\OneDrive\Desktop\Camera_project\version_6\record.env"
show_path = r"C:\Users\spd-d\OneDrive\Desktop\Camera_project\version_6\show.env"
# ฟังก์ชันเพื่อดึงข้อมูลจากไฟล์ show.env
def get_data_from_file():
    try:
        with open(show_path, 'r') as f:
            data = f.read()
            return json.loads(data)  # แปลงข้อมูล JSON เป็น dictionary
    except Exception:
        return None

# ฟังก์ชันเพื่อรีเซ็ตข้อมูลในไฟล์ show.env
def reset_data_in_file():
    try:
        with open(show_path, 'w') as f:
            f.write("")  # เขียนข้อมูลว่าง
        st.success("Data has been reset successfully.")
    except Exception as e:
        st.error(f"Error resetting files: {e}")

# ฟังก์ชันลบ Invoice
def delete_invoice():
    try:
        with open(record_path, 'w') as f:
            f.write("")  # เขียนข้อมูลว่าง
        with open(show_path, 'w') as f:
            f.write("")  # เขียนข้อมูลว่าง
        return True  # ส่งผลลัพธ์สำเร็จ
    except Exception as e:
        st.error(f"Error updating file: {e}")
        return False  # ส่งผลลัพธ์ล้มเหลว

# ตั้งค่า page config
st.set_page_config(page_title="QRcode Scanner", layout="wide")

# ใช้ CSS ในการจัดตำแหน่ง title ให้อยู่กลาง
st.markdown(
    """
    <style>
    .title {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ตั้งค่า title
st.markdown('<h1 class="title">QRcode Scanner</h1>', unsafe_allow_html=True)

# กำหนดคีย์สำหรับ session_state
keys = ["Invoice_Master", "Total_Master", "Count", "Model", "Status_msg", "Status_conveyor"]
if "data" not in st.session_state:
    st.session_state["data"] = {key: "-" for key in keys}
if "show_delete_code" not in st.session_state:
    st.session_state["show_delete_code"] = False  # ตั้งค่าเริ่มต้น

# ช่องว่างสำหรับแสดงข้อมูล real-time
col1, col2 = st.columns(2)
with col1:
    invoice_number_placeholder = st.empty()
    counting_placeholder = st.empty()
with col2:
    total_master_placeholder = st.empty()
    status_conveyor_placeholder = st.empty()
status_msg_placeholder = st.empty()
# ปุ่ม Reset และ Delete
col_1, col_2 = st.columns([8, 2])



with col_2:
    if st.button("Reset Data dashboard"):
        reset_data_in_file()

    
    # ตัวแปรสถานะ
    if "confirm" not in st.session_state:
        st.session_state.confirm = False

    # สร้างปุ่มยืนยัน
    if st.button("Delete Invoice"):
        st.session_state.confirm = True

    # หากผู้ใช้กดปุ่มยืนยัน
    if st.session_state.confirm:
        # แสดงข้อความแจ้งเตือนเพื่อยืนยันความมั่นใจ
        st.warning("Are you sure to continue?")
        col11, col22 = st.columns(2)
        msg = ""
        with col11:
            if st.button("yes, continue"):
                print("yes")
                if delete_invoice():
                    msg = "success!"
                else:
                    msg = "error to delete invoice!"
                st.session_state.confirm = False  # รีเซ็ตสถานะ
        with col22:
            if st.button("no, not continue"):
                print("no")
                msg = "cancled!"
                st.session_state.confirm = False  # รีเซ็ตสถานะ
        if msg == "":
            pass
        elif msg == "ดำเนินการสำเร็จ!":
            st.success(msg)
        else:
            st.info(msg)
# อัปเดตข้อมูลแบบ real-time
while True:
    # ดึงข้อมูลจากไฟล์ show.env
    data_from_file = get_data_from_file()

    # ถ้ามีข้อมูลจากไฟล์ ให้ใช้ข้อมูลนั้น
    if data_from_file:
        st.session_state["data"].update(data_from_file)
    else:
        # ถ้าไม่มีข้อมูลจากไฟล์ ให้ตั้งค่าเป็น '-'
        st.session_state["data"] = {key: "-" for key in keys}
    # ดึงค่าสีจาก JSON (ถ้ามี)
    msg_color = st.session_state['data'].get("msg_color", "black")
    msg_bg = st.session_state['data'].get("msg_bg", "white")

    status = st.session_state['data']['Status_conveyor']
    status_color = "green" if status == "run" else "red" if status == "stop" else "white"
    # แสดงข้อมูลที่อัปเดต
    with col1:
        invoice_number_placeholder.markdown(
            f"<div style='font-size: 40px; font-weight: bold;'><p><b>Invoice number: </b>{st.session_state['data']['Invoice_Master']}</p></div>",
            unsafe_allow_html=True)
        
        counting_placeholder.markdown(
            f"<div style='font-size: 40px; font-weight: bold;'><p><b>Counting: </b>{st.session_state['data']['Count']}</p></div>",
            unsafe_allow_html=True)

        

    with col2:
        total_master_placeholder.markdown(
            f"<div style='font-size: 40px; font-weight: bold;'><p><b>Total master: </b>{st.session_state['data']['Total_Master']}</p></div>",
            unsafe_allow_html=True)
        
        status_conveyor_placeholder.markdown(
            f"""
            <div style='font-size: 40px; font-weight: bold;'>
                <p><b>Status conveyor: </b>
                <span style='background-color: {status_color}; color: white; padding: 5px; border-radius: 3px;'>{status}</span>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    status_msg_placeholder.markdown(
            f"<div style='font-size: 40px; font-weight: bold;'><p><b>Status msg: </b><span style='color: {msg_color}; background-color: {msg_bg}; padding: 5px 10px; border-radius: 5px;'>{st.session_state['data']['Status_msg']}</span></p></div>",
            unsafe_allow_html=True)
    time.sleep(0.2)  # รอ 0.5 วินาทีเพื่อดึงข้อมูลใหม่
