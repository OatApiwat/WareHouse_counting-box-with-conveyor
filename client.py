import socket
import pymssql
import json
import os
import shutil
import time
SERVER_IP = "169.254.52.155"
SERVER_PORT = 5001
record_path = r"C:\Users\spd-d\OneDrive\Desktop\Camera_project\version_6\record.env"
show_path = r"C:\Users\spd-d\OneDrive\Desktop\Camera_project\version_6\show.env"

global conv_status,out_conveyer_status,active_clients_list
conv_status = 'run'
out_conveyer_status = 'ok'

def split_data(data):
    global conv_status,out_conveyer_status #7 common
    count = get_count_from_env(record_path) #3 common
    # print("count: ",count)
    print("TCP_data: ",data)
    star_part = data.split('**')
    star_count = data.count('**')
    if count == 0:
        # case read 2 barcode
        if star_count == 1:
            for idx, part in enumerate(star_part):
                comma_part = part.split(';;;')
                if idx == 0:
                    print("This is 2 barcode frist box")
                    out_barcode = comma_part[1]
                    qr_code = out_barcode.split()
                    invoice_number = qr_code[1].split()[0] #1
                    box_total = int(qr_code[3].split()[0]) #2
                    model = qr_code[6].split()[0] #4
                    box_number = int((qr_code[2].split())[0]) #5
                    if conv_status == 'run':
                        error_msg = f"Read success {box_number}/{box_total} and set {invoice_number} to be master" #6
                        msg_color = 'white' #8
                        msg_bg = 'green' #9
                        conv_status = 'run' #7
                        out_conveyer_status = 'ok' #10
                        record_env(qr_code,invoice_number,box_total,count,model,box_number)
                    elif(conv_status == 'stop'):
                        error_msg = f"Conveyer not working for frist box" #6
                        msg_color = 'white' #8
                        msg_bg = 'red' #9
                        conv_status = 'stop' #7
                        out_conveyer_status = 'ng' #10
                        insert_abnormal(out_barcode,'',box_number,0,model,error_msg)
        elif(star_count == 0):
            comma_part = star_part[0].split(';;;')
            comma_count = star_part[0].count(';;;')
            # case read 1 barcode
            if comma_count > 0 :
                out_barcode = comma_part[1]
                qr_code = out_barcode.split()
                tab_count = len(qr_code)
                if tab_count>=4:
                    data_2 = qr_code[2].split()[0]
                    data_3 = qr_code[3].split()[0]
                else:
                    data_2 = 'a'
                    data_3 = 'a'
                
                if tab_count > 6 and data_2.isdigit() and data_3.isdigit():
                    print("This is out barcode  frist box")
                    invoice_number = qr_code[1].split()[0] #1
                    box_total = int(qr_code[3].split()[0]) #2
                    model = qr_code[6].split()[0] #4
                    box_number = int((qr_code[2].split())[0]) #5
                    if conv_status == 'run':
                        error_msg = f"Read success {box_number}/{box_total} and set {invoice_number} to be master" #6
                        msg_color = 'white' #8
                        msg_bg = 'green' #9
                        conv_status = 'run' #7
                        out_conveyer_status = 'ok' #10
                        record_env(qr_code,invoice_number,box_total,count,model,box_number)
                    elif(conv_status == 'stop'):
                        error_msg = f"Conveyer not working for frist box" #6
                        msg_color = 'white' #8
                        msg_bg = 'red' #9
                        conv_status = 'stop' #7
                        out_conveyer_status = 'ng' #10
                        insert_abnormal('','','',0,'',error_msg)
                elif tab_count >2 :
                    print("This is in barcode  frist box")
                    invoice_number = '' #1
                    box_total = '' #2
                    model = '' #4
                    box_number = '' #5
                    if conv_status == 'run':
                        error_msg = f"Cannot read frist box" #6
                        msg_color = 'white' #8
                        msg_bg = 'red' #9
                        conv_status = 'stop' #7
                        out_conveyer_status = 'ng' #10
                    elif(conv_status == 'stop'):
                        error_msg = f"Conveyer not working for frist box" #6
                        msg_color = 'white' #8
                        msg_bg = 'red' #9
                        conv_status = 'stop' #7
                        out_conveyer_status = 'ng' #10
                    insert_abnormal('','',box_number,0,model,error_msg)
            # case NoRead
            elif(comma_part[0] == 'NoRead'):
                print("This is in NoRead  frist box")
                invoice_number = '' #1
                box_total = '' #2
                model = '' #4
                box_number = '' #5
                if conv_status == 'run':
                    error_msg = f"Cannot read frist box" #6
                    msg_color = 'white' #8
                    msg_bg = 'red' #9
                    conv_status = 'stop' #7
                    out_conveyer_status = 'ng' #10
                elif(conv_status == 'stop'):
                    error_msg = f"Conveyer not working for frist box" #6
                    msg_color = 'white' #8
                    msg_bg = 'red' #9
                    conv_status = 'stop' #7
                    out_conveyer_status = 'ng' #10
                insert_abnormal('','',box_number,0,model,error_msg)
        # case run
            elif(comma_part[0] == 'run'):
                print("This is run frist box")
                invoice_number = '' #1
                box_total = '' #2
                model = '' #4
                if get_status_msg_from_file(show_path) == '' or get_status_msg_from_file(show_path).startswith("Conveyer is stoping"):
                    error_msg = f"Conveyer is running for frist box" #6
                    msg_bg = 'green' #9
                else:
                    error_msg = get_status_msg_from_file(show_path) #6
                    msg_bg = get_msg_bg_from_file(show_path) #9
                box_number = '' #5
                msg_color = 'white' #8
                conv_status = 'run' #7
                out_conveyer_status = 'ok' #10
        # case stop
            elif(comma_part[0] == 'stop'):
                print("This is stop frist box")
                invoice_number = '' #1
                box_total = '' #2
                model = '' #4
                if get_status_msg_from_file(show_path) == '' or get_status_msg_from_file(show_path).startswith("Conveyer is running"):
                    error_msg = f"Conveyer is stoping for frist box" #6
                    msg_bg = 'red' #9
                else:
                    error_msg = get_status_msg_from_file(show_path) #6
                    msg_bg = get_msg_bg_from_file(show_path) #9
                box_number = '' #5
                msg_color = 'white' #8
                conv_status = 'stop' #7
                out_conveyer_status = '--' #10
            else:
                print("This is other frist box")
                invoice_master = '' #1
                total_master = '' #2
                model = '' #4
                box_number = '' #5
                error_msg = f"Comunication invalid for frist box with {comma_part[0]}" #6
                msg_color = 'white' #8
                msg_bg = 'red' #9
                conv_status = 'stop' #7
                out_conveyer_status = 'ng' #10
                insert_abnormal('','',box_number,0,model,error_msg)
    elif count > 0:
        # case read 2 barcode
        if star_count == 1:
            for idx, part in enumerate(star_part):
                comma_part = part.split(';;;')
                if idx == 0:
                    print("This is 2 barcode second box")
                    out_barcode = comma_part[1]
                    qr_code = out_barcode.split()
                    invoice_number = qr_code[1].split()[0] #1
                    box_total = int(qr_code[3].split()[0]) #2
                    model = qr_code[6].split()[0] #4
                    box_number = int((qr_code[2].split())[0]) #5
                    invoice_master = get_invoice_master(record_path)
                    total_master = get_total_master(record_path)
                    old_box_number = get_box_number(record_path)
                    if(invoice_number == invoice_master and count < total_master):
                        if(check_env(invoice_number, box_number,record_path)): #ถ้าไม่มีใน record.env
                            if conv_status == 'run':
                                error_msg = f"Read success {box_number}/{total_master}" #6
                                msg_color = 'white' #8
                                msg_bg = 'green' #9
                                conv_status = 'run' #7
                                out_conveyer_status = 'ok' #10
                                record_env(qr_code,invoice_number,box_total,count,model,box_number)
                            elif(conv_status == 'stop'):
                                error_msg = f"Conveyer not working after {old_box_number}/{total_master}" #6
                                msg_color = 'white' #8
                                msg_bg = 'red' #9
                                conv_status = 'stop' #7
                                out_conveyer_status = 'ng' #10
                                insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
                        else:
                            if conv_status == 'run':
                                error_msg = f"Duplicated box {box_number}/{total_master}" #6
                                msg_color = 'black' #8
                                msg_bg = 'yellow' #9
                                conv_status = 'run' #7
                                out_conveyer_status = 'nm' #10
                                insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
                            elif(conv_status == 'stop'):
                                error_msg = f"Conveyer not working after {old_box_number}/{total_master}" #6
                                msg_color = 'white' #8
                                msg_bg = 'red' #9
                                conv_status = 'stop' #7
                                out_conveyer_status = 'ng' #10
                                insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
                    elif(invoice_number != invoice_master and count < total_master):
                        if conv_status == 'run':
                            error_msg = f"Invoice not Match after {old_box_number}/{total_master}" #6
                            msg_color = 'white' #8
                            msg_bg = 'red' #9
                            conv_status = 'stop' #7
                            out_conveyer_status = 'ng' #10
                            insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
                        elif(conv_status == 'stop'):
                            error_msg = f"Conveyer not working after {old_box_number}/{total_master}" #6
                            msg_color = 'white' #8
                            msg_bg = 'red' #9
                            conv_status = 'stop' #7
                            out_conveyer_status = 'ng' #10
                            insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
        elif(star_count == 0):
            comma_part = star_part[0].split(';;;')
            comma_count = star_part[0].count(';;;')
            # case read 1 barcode
            if comma_count > 0 :
                out_barcode = comma_part[1]
                qr_code = out_barcode.split()
                tab_count = len(qr_code)
                if tab_count>=4:
                    data_2 = qr_code[2].split()[0]
                    data_3 = qr_code[3].split()[0]
                else:
                    data_2 = 'a'
                    data_3 = 'a'
                if tab_count > 6 and data_2.isdigit() and data_3.isdigit():
                    print("This is out barcode second box")
                    invoice_number = qr_code[1].split()[0] #1
                    box_total = int(qr_code[3].split()[0]) #2
                    model = qr_code[6].split()[0] #4
                    box_number = int((qr_code[2].split())[0]) #5
                    invoice_master = get_invoice_master(record_path)
                    total_master = get_total_master(record_path)
                    old_box_number = get_box_number(record_path)
                    if(invoice_number == invoice_master and count < total_master):
                        if(check_env(invoice_number, box_number,record_path)): #ถ้าไม่มีใน record.env
                            if conv_status == 'run':
                                error_msg = f"Read success {box_number}/{total_master}" #6
                                msg_color = 'white' #8
                                msg_bg = 'green' #9
                                conv_status = 'run' #7
                                out_conveyer_status = 'ok' #10
                                record_env(qr_code,invoice_number,box_total,count,model,box_number)
                            elif(conv_status == 'stop'):
                                error_msg = f"Conveyer not working after {old_box_number}/{total_master}" #6
                                msg_color = 'white' #8
                                msg_bg = 'red' #9
                                conv_status = 'stop' #7
                                out_conveyer_status = 'ng' #10
                                insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
                        else:
                            if conv_status == 'run':
                                error_msg = f"Duplicated box {box_number}/{total_master}" #6
                                msg_color = 'black' #8
                                msg_bg = 'yellow' #9
                                conv_status = 'run' #7
                                out_conveyer_status = 'nm' #10
                                insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
                            elif(conv_status == 'stop'):
                                error_msg = f"Conveyer not working after {old_box_number}/{total_master}" #6
                                msg_color = 'white' #8
                                msg_bg = 'red' #9
                                conv_status = 'stop' #7
                                out_conveyer_status = 'ng' #10
                                insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
                    elif(invoice_number != invoice_master and count < total_master):
                        if conv_status == 'run':
                            error_msg = f"Invoice not Match after {old_box_number}/{total_master}" #6
                            msg_color = 'white' #8
                            msg_bg = 'red' #9
                            conv_status = 'stop' #7
                            out_conveyer_status = 'ng' #10
                            insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
                        elif(conv_status == 'stop'):
                            error_msg = f"Conveyer not working after {old_box_number}/{total_master}" #6
                            msg_color = 'white' #8
                            msg_bg = 'red' #9
                            conv_status = 'stop' #7
                            out_conveyer_status = 'ng' #10
                            insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
                elif tab_count >2 :
                    print("This is in barcode  second box")
                    invoice_master = get_invoice_master(record_path) #1
                    total_master = get_total_master(record_path) #2
                    model = get_model(record_path) #4
                    box_number = get_box_number(record_path) #5
                    if conv_status == 'run':
                        error_msg = f"Cannot read after {box_number}/{total_master}" #6
                        msg_color = 'white' #8
                        msg_bg = 'red' #9
                        conv_status = 'stop' #7
                        out_conveyer_status = 'ng' #10
                        insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
                    elif(conv_status == 'stop'):
                        error_msg = f"Conveyer not working after {box_number}/{total_master}" #6
                        msg_color = 'white' #8
                        msg_bg = 'red' #9
                        conv_status = 'stop' #7
                        out_conveyer_status = 'ng' #10
                        insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg)
        # case NoRead
            elif(comma_part[0] == 'NoRead'):
                print("This is in NoRead second box")
                invoice_master = get_invoice_master(record_path) #1
                total_master = get_total_master(record_path) #2
                model = get_model(record_path) #4
                box_number = get_box_number(record_path) #5
                if conv_status == 'run':
                    error_msg = f"Cannot read after {box_number}/{total_master}" #6
                    msg_color = 'white' #8
                    msg_bg = 'red' #9
                    conv_status = 'stop' #7
                    out_conveyer_status = 'ng' #10
                    insert_abnormal('',invoice_master,'',total_master,model,error_msg)
                elif(conv_status == 'stop'):
                    error_msg = f"Conveyer not working after {box_number}/{total_master}" #6
                    msg_color = 'white' #8
                    msg_bg = 'red' #9
                    conv_status = 'stop' #7
                    out_conveyer_status = 'ng' #10
                    insert_abnormal('',invoice_master,'',total_master,model,error_msg)
        # case run
            elif(comma_part[0] == 'run'):
                print("This is run frist box")
                invoice_master = get_invoice_master(record_path) #1
                total_master = get_total_master(record_path) #2
                model = get_model(record_path) #4
                box_number = get_box_number(record_path) #5
                if get_status_msg_from_file(show_path) == '' or get_status_msg_from_file(show_path).startswith("Conveyer is stoping"):
                    error_msg = f"Conveyer is running last box is {box_number}/{total_master}" #6
                    msg_bg = 'green' #9
                else:
                    error_msg = get_status_msg_from_file(show_path) #6
                    msg_bg = get_msg_bg_from_file(show_path) #9
                msg_color = 'white' #8
                
                conv_status = 'run' #7
                out_conveyer_status = 'ok' #10
        # case stop
            elif(comma_part[0] == 'stop'):
                print("This is stop second box")
                invoice_master = get_invoice_master(record_path) #1
                total_master = get_total_master(record_path) #2
                model = get_model(record_path) #4
                box_number = get_box_number(record_path) #5
                if get_status_msg_from_file(show_path) == '' or get_status_msg_from_file(show_path).startswith("Conveyer is running"):
                    error_msg = f"Conveyer is stoping last box is {box_number}/{total_master}" #6
                    msg_bg = 'red' #9
                else:
                    error_msg = get_status_msg_from_file(show_path) #6
                    msg_bg = get_msg_bg_from_file(show_path) #9
                msg_color = 'white' #8
                
                conv_status = 'stop' #7
                out_conveyer_status = '--' #10
            else:
                print("This is other second box")
                invoice_master = get_invoice_master(record_path) #1
                total_master = get_total_master(record_path) #2
                model = get_model(record_path) #4
                box_number = get_box_number(record_path) #5
                error_msg = f"Comunication invalid last box is {box_number}/{total_master} with {comma_part[0]}" #6
                msg_color = 'white' #8
                msg_bg = 'red' #9
                conv_status = 'stop' #7
                out_conveyer_status = 'ng' #10
                insert_abnormal('','',box_number,0,model,error_msg)
    
    count = get_count_from_env(record_path)
    total_master = get_total_master(record_path)
    
    # print("count: ",count)
    if count <=0:
        invoice_master = ''
        total_master_show = ''
        total_master = 0
        count_show = ''
        model = ''
        model_show = ''
        box_number = 0
        box_number_show = ''
        if error_msg == "Loading sucess!":
            error_msg = ''
            msg_bg = 'white'
    else:
        invoice_master = get_invoice_master(record_path)
        total_master_show = get_total_master(record_path)
        box_number_show = get_box_number(record_path)
        count_show = f"{count}/{total_master}"
        model_show = get_model(record_path)
    if(count >= total_master and count != 0):
        record_to_store(record_path)
        # time.sleep(0.1)
        if not (record_to_db(record_path)):
            record_to_store(record_path)
            error_msg = "cannot save to database,Save at storage" #6
            msg_color = 'white' #8
            msg_bg = 'yellow' #9
        else:
            error_msg = "Loading sucess!" #6
            msg_color = 'white' #8
            msg_bg = 'green' #9
        delete_from_env(record_path)
        time.sleep(0.2)
    save_to_show(invoice_master,total_master_show,count_show,model_show,box_number_show,error_msg,conv_status,msg_color,msg_bg,show_path)
    return out_conveyer_status

def get_count_from_env(path):
    try:
        with open(path, "r") as file:
            count_in_env = sum(1 for _ in file)  # นับจำนวนบรรทัดในไฟล์
            # print("count_in_env: ",count_in_env)
        return count_in_env
    except FileNotFoundError:
        return 0  # ถ้าไฟล์ไม่มีอยู่ให้คืนค่า 0

def get_invoice_master(path):
    # print("call: get_invoice_master()")
    try:
        with open(path, "r") as file:
            # อ่านบรรทัดทั้งหมดแล้วเลือกบรรทัดสุดท้าย
            lines = file.readlines()
            if lines:
                last_line = lines[-1].strip()  # ดึงบรรทัดสุดท้าย
                # แยกข้อมูลด้วย ' | ' แล้วแปลงเป็น dictionary
                record_data = dict(item.split("=") for item in last_line.split(" | "))
                # ตรวจสอบและแปลง Invoice_Master ถ้ามีค่า
                invoice_master = record_data.get("Invoice_Master", "").strip()
                if invoice_master:
                    # แยกค่าจากสตริงถ้ามีการแสดงเป็นลิสต์
                    invoice_master = invoice_master.strip('[]').split(',')
                print("invoice_master", invoice_master[0])
                return invoice_master[0] if invoice_master else ''
            else:
                return ''  # ถ้าไฟล์ว่าง
    except FileNotFoundError:
        return ''  # ถ้าไฟล์ไม่มี ให้คืนค่าเริ่มต้น
    except Exception as e:
        print(f"Error: {e}")
        return ''  # ในกรณีที่เกิดข้อผิดพลาดอื่นๆ

def get_total_master(path):
    # print("call: get_total_master()")
    try:
        with open(record_path, "r") as file:
            # อ่านบรรทัดทั้งหมดแล้วเลือกบรรทัดสุดท้าย
            lines = file.readlines()
            if lines:
                last_line = lines[-1].strip()  # ดึงบรรทัดสุดท้าย
                # แยกข้อมูลด้วย ' | ' แล้วแปลงเป็น dictionary
                record_data = dict(item.split("=") for item in last_line.split(" | "))
                # ใช้ eval() เพื่อแปลงเป็น list หรือ dictionary
                total_master = int(record_data.get("Total_Master", "[]").strip())
                return total_master
            else:
                return 0  # ถ้าไฟล์ว่าง
    except FileNotFoundError:
        return 0  # ถ้าไฟล์ไม่มี ให้คืนค่าเริ่มต้น
    except Exception as e:
        print(f"Error: {e}")
        return 0  # ในกรณีที่เกิดข้อผิดพลาดอื่นๆ

def get_model(path):
    # print("call: get_model()")
    try:
        with open(path, "r") as file:
            # อ่านบรรทัดทั้งหมดแล้วเลือกบรรทัดสุดท้าย
            lines = file.readlines()
            if lines:
                last_line = lines[-1].strip()  # ดึงบรรทัดสุดท้าย
                # แยกข้อมูลด้วย ' | ' แล้วแปลงเป็น dictionary
                record_data = dict(item.split("=") for item in last_line.split(" | "))
                # ตรวจสอบและแปลง Invoice_Master ถ้ามีค่า
                model = record_data.get("Model", "").strip()
                if model:
                    # แยกค่าจากสตริงถ้ามีการแสดงเป็นลิสต์
                    model = model.strip('[]').split(',')
                print("model", model[0])
                return model[0] if model else ''
            else:
                return ''  # ถ้าไฟล์ว่าง
    except FileNotFoundError:
        return ''  # ถ้าไฟล์ไม่มี ให้คืนค่าเริ่มต้น
    except Exception as e:
        print(f"Error: {e}")
        return ''  # ในกรณีที่เกิดข้อผิดพลาดอื่นๆ

def get_box_number(path):
    # print("call: get_box_number()")
    try:
        with open(record_path, "r") as file:
            # อ่านบรรทัดทั้งหมดแล้วเลือกบรรทัดสุดท้าย
            lines = file.readlines()
            if lines:
                last_line = lines[-1].strip()  # ดึงบรรทัดสุดท้าย
                # แยกข้อมูลด้วย ' | ' แล้วแปลงเป็น dictionary
                record_data = dict(item.split("=") for item in last_line.split(" | "))
                # ใช้ eval() เพื่อแปลงเป็น list หรือ dictionary
                box_number = int(record_data.get("Box_number", "[]").strip())
                return box_number
            else:
                return 0  # ถ้าไฟล์ว่าง
    except FileNotFoundError:
        return 0  # ถ้าไฟล์ไม่มี ให้คืนค่าเริ่มต้น
    except Exception as e:
        print(f"Error: {e}")
        return 0  # ในกรณีที่เกิดข้อผิดพลาดอื่นๆ

def get_status_msg_from_file(file_path):
    try:
        # เปิดไฟล์และอ่านบรรทัดสุดท้าย
        with open(file_path, 'r') as file:
            lines = file.readlines()
            last_line = lines[-1].strip()  # เอาบรรทัดสุดท้ายและลบช่องว่างที่ไม่จำเป็น

        # แปลงข้อมูล JSON ในบรรทัดสุดท้ายเป็น Python dictionary
        data = json.loads(last_line)

        # ดึงค่า 'Status_msg'
        status_msg = data.get("Status_msg", '')

        return status_msg

    except Exception as e:
        print(f"Error reading file: {e}")
        return ''

def get_msg_bg_from_file(file_path):
    try:
        # เปิดไฟล์และอ่านบรรทัดสุดท้าย
        with open(file_path, 'r') as file:
            lines = file.readlines()
            last_line = lines[-1].strip()  # เอาบรรทัดสุดท้ายและลบช่องว่างที่ไม่จำเป็น

        # แปลงข้อมูล JSON ในบรรทัดสุดท้ายเป็น Python dictionary
        data = json.loads(last_line)

        # ดึงค่า 'msg_bg'
        msg_bg = data.get("msg_bg", 'red')

        return msg_bg

    except Exception as e:
        return f"Error reading file: {e}"

def record_env(barcode,invoice_number,box_total,count,model,box_number):
    # print("call: record_env()")
    record_data = {
        "Out_qrcode":barcode,
        "Invoice_Master":invoice_number,
        "Total_Master":box_total,
        "Count":count,
        "Model":model,
        "Box_number":box_number,
    }
        # แปลง record_data เป็นข้อความ 1 บรรทัดโดยใช้ ' | ' เป็นตัวคั่น
    record_line = " | ".join(f"{key}={value}" for key, value in record_data.items())

    # บันทึกข้อมูลลงไฟล์ record.env (append โหมด "a" ไม่ลบของเก่า)
    with open(record_path, "a") as file:
        file.write(record_line + "\n")  # เพิ่มข้อมูลใหม่ใน 1 บรรทัดแล้วขึ้นบรรทัดใหม่
    return True

def insert_abnormal(out_barcode,invoice_master,box_number,total_master,model,error_msg):
    # print("call: insert_abnormal()")
    qrcode_abnormal = ", ".join(out_barcode.split())  # แปลง list เป็น string
    invoice_abnormal = str(invoice_master)  
    box_number_abnormal = str(box_number)  
    box_total_abnormal = str(total_master if total_master >= 0 else 0)
    model_abnormal = str(model)  
    error_abnormal = str(error_msg)  
    # print(
    # f"QR Code Abnormal: {qrcode_abnormal}, "
    # f"Invoice Abnormal: {invoice_abnormal}, "
    # f"Box Number Abnormal: {box_number_abnormal}, "
    # f"Box Total Abnormal: {box_total_abnormal}, "
    # f"Model Abnormal: {model_abnormal}, "
    # f"Error Abnormal: {error_abnormal}")

    try:
        # เชื่อมต่อกับ SQL Server
        conn = pymssql.connect(
            server='127.0.0.1',  # IP หรือชื่อเซิร์ฟเวอร์
            user='sa',            # ชื่อผู้ใช้
            password='sa@admin',  # รหัสผ่าน
            database='QRcode_db'  # ชื่อฐานข้อมูล
        )
        cursor = conn.cursor()

        # สร้างคำสั่ง SQL เพื่อ insert ข้อมูล
        sql = '''INSERT INTO ABnormal_tb (QRcode, Invoice_master, Box_number, Box_Total, Model,Abnormal_case)
                 VALUES (%s, %s, %s, %s, %s, %s)'''
        
        # ทำการ execute คำสั่ง SQL พร้อมกับข้อมูลที่ต้องการ insert
        cursor.execute(sql, (qrcode_abnormal, invoice_abnormal, box_number_abnormal, box_total_abnormal, model_abnormal,error_abnormal))
        
        # Commit การเปลี่ยนแปลง
        conn.commit()

        print("Data inserted to ABnormal_tb successfully")

    except pymssql.Error as e:
        print(f"Error: {e}")

    finally:
        # ปิดการเชื่อมต่อ
        cursor.close()
        conn.close()

def record_to_db(path):
    # print("call : record_to_db()")
    try:
        # เปิดไฟล์ record.env และอ่านข้อมูล
        with open(path, "r") as file:
            iter = 0
            for line in file:
                # ตรวจสอบว่า line มีข้อมูลหรือไม่
                iter = iter+1
                invoice_master_show = get_invoice_master(record_path)
                total_master_show = get_total_master(record_path)
                count_show = get_count_from_env(record_path)
                model_show = get_model(record_path)
                box_number_show = get_box_number(record_path)
                error_msg = f'Loading {iter}/{count_show}'
                msg_color = 'white'
                msg_bg = 'blue'
                if line.strip():  # ข้ามบรรทัดที่ว่าง
                    # แยกข้อมูลในแต่ละบรรทัด
                    record_data = dict(item.split("=") for item in line.strip().split(" | "))

                    # ตรวจสอบว่าข้อมูลสำคัญในไฟล์เป็นข้อมูลที่เราต้องการ
                    qrcode = record_data.get('Out_qrcode', '')
                    invoice_number = record_data.get('Invoice_Master', '').strip("[]").replace("'", "")
                    box_number = record_data.get('Box_number', '').strip("[]").replace("'", "")
                    box_total = record_data.get('Total_Master', '').strip("[]").replace("'", "")
                    model = record_data.get('Model', '').strip("[]").replace("'", "")

                    # เรียกฟังก์ชันเพื่อ insert ข้อมูลลงฐานข้อมูล
                    if(not insert_into_camera_db(qrcode, invoice_number, box_number, box_total, model)):
                        print("insert db error")
                        return False
                save_to_show(invoice_master_show,total_master_show,count_show,model_show,box_number_show,error_msg,conv_status,msg_color,msg_bg,show_path)
                print(f"save: {iter}")
            return  True #True
    except FileNotFoundError:
        print("File not found: record.env")
    except Exception as e:
        print(f"Error reading file: {e}")

def insert_into_camera_db(qrcode, invoice_number, box_number, box_total, model):
    try:
        # เชื่อมต่อกับ SQL Server
        conn = pymssql.connect(
            server='127.0.0.1',  # IP หรือชื่อเซิร์ฟเวอร์
            user='sa',            # ชื่อผู้ใช้
            password='sa@admin',  # รหัสผ่าน
            database='QRcode_db'  # ชื่อฐานข้อมูล
        )
        cursor = conn.cursor()

        # สร้างคำสั่ง SQL เพื่อ insert ข้อมูล
        sql = '''INSERT INTO Camera_tb (QRcode, Invoice_number, Box_number, Box_Total, Model)
                    VALUES (%s, %s, %s, %s, %s)'''
        
        # ทำการ execute คำสั่ง SQL พร้อมกับข้อมูลที่ต้องการ insert
        cursor.execute(sql, (qrcode, invoice_number, box_number, box_total, model))
        
        # Commit การเปลี่ยนแปลง
        conn.commit()

        print("Data inserted successfully")
        return True

    except pymssql.Error as e:
        return False
        print(f"Error: {e}")

    finally:
        # ปิดการเชื่อมต่อ
        cursor.close()
        conn.close()

def record_to_store(path):
    # print("call: record_to_store()")
    invoice_master = get_invoice_master(path)
    try:
    # สร้างชื่อไฟล์ใหม่
        destination_folder = r"C:\Users\spd-d\OneDrive\Desktop\Camera_project\version_6\store"
        os.makedirs(destination_folder, exist_ok=True)  # สร้างโฟลเดอร์ถ้ายังไม่มี
        destination_path = os.path.join(destination_folder, f"{invoice_master}_store.env")

        # ตรวจสอบว่าไฟล์ต้นทางมีอยู่หรือไม่
        if not os.path.exists(path):
            print(f"Error: Source file '{path}' does not exist.")
            return

        # คัดลอกข้อมูลจาก record.env ไปยังไฟล์ใหม่
        shutil.copy(record_path, destination_path)
        print(f"File '{destination_path}' created successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

def sent_data_to_IoT(conn,out_convey_status):
    # print(active_clients_list)
    for client in active_clients_list:
        try:
            client.sendall(out_convey_status.encode())  # ส่งข้อมูลไปยัง client
        except (ConnectionResetError, BrokenPipeError):
            # หากส่งไม่ได้ก็ลบ client นั้นออก
            active_clients_list.remove(client)
    print(f"call: sent_data_to_IoT() sent {out_convey_status} to IoT")

def save_to_show(invoice_master_value,total_master_show,count_show,model_value,box_number_show,error_msg,conv_msg,msg_color,msg_bg,show_path):
    # print("call: save_to_show()")
    json_show = {
        "Invoice_Master": invoice_master_value,
        "Total_Master": total_master_show,
        "Count": count_show,
        "Model": model_value,  # model ไม่ถูกใช้งานในโค้ดเดิม
        "Box_number": box_number_show,
        "Status_msg": error_msg,
        "Status_conveyor": conv_msg,
        "msg_color": msg_color,   # เพิ่ม msg_color
        "msg_bg": msg_bg,         # เพิ่ม msg_bg
    }
    json_data = json.dumps(json_show)
    # กำหนด path ของไฟล์
    if not is_data_exists(show_path, json_data):
        with open(show_path, 'w') as f:
            f.write(json_data)
        print("Data saved to show.env")
    else:
        print("Data already exists, not saving again")

def is_data_exists(file_path, data):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            file_data = f.read()
            # เปรียบเทียบข้อมูลในไฟล์กับข้อมูลใหม่
            return file_data == data
    return False

def check_env(invoice_number, box_number,record_path):
    # print("call: check_env()")
    try:
        with open(record_path, "r") as file:
            for line in file:
                # แปลงข้อมูลเป็น dictionary
                record_data = dict(item.split("=") for item in line.strip().split(" | "))

                # แปลงค่าจาก string ให้เป็น list (ถ้าข้อมูลมีหลายตัวอักษรให้ใช้ .split())
                record_invoice = record_data.get("Invoice_Master", "").strip()
                record_box = record_data.get("Box_number", "").strip()
                # เปรียบเทียบค่า
                if str(record_invoice) == str(invoice_number) and int(record_box) == (box_number):
                    return False #False  # พบข้อมูลที่ตรงกัน

        return True  # ไม่พบข้อมูลที่ตรงกัน
    except FileNotFoundError:
        return False  # หากไฟล์ไม่มีอยู่ ให้คืนค่า False

def delete_from_env(record_path):
    # print("call: delete_from_env")
    try:
        # เปิดไฟล์ในโหมด "w" (write) เพื่อเขียนทับข้อมูลเป็นค่าว่าง
        with open(record_path, "w") as file:
            pass  # ไม่ต้องเขียนอะไรลงไป (ทำให้ไฟล์ว่างเปล่า)
        # return True
    except Exception as e:
        print(f"Error: {e}")

def connect_to_server():
    while True:
        try:
            # time.sleep(1)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER_IP, SERVER_PORT))
            print(f"[CONNECTED] to Server {SERVER_IP}:{SERVER_PORT}")
            return client
        except:
            print("[RECONNECTING] Server not available. Retrying in 1 seconds...")
            time.sleep(1)

server_socket = connect_to_server()


while True:
    try:
        data = server_socket.recv(1024)
        if not data:
            print("[DISCONNECTED] Server connection lost.")
            server_socket = connect_to_server()
            continue

        received_value = data.decode('utf-8')
        print(f"[RECEIVED] {received_value}")
        out = split_data(received_value)
        print(f"[sent] {out}")
        server_socket.sendall(f"{out}\n".encode('utf-8'))
        print("-----------------------------------")

    except:
        server_socket = connect_to_server()