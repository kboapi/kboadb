import os
from tabulate import tabulate

# กำหนดเส้นทางไฟล์ที่ใช้ในการเก็บชื่ออุปกรณ์
FILE_PATH = 'devices.txt'

# ฟังก์ชันเพิ่มชื่ออุปกรณ์ใหม่หรือบันทึกในไฟล์ (แบบต่อท้าย)
def create_device(name_device):
    with open(FILE_PATH, 'a') as file:  # เปิดไฟล์ในโหมด 'a' (append) เพื่อเพิ่มข้อมูลใหม่
        file.write(f"{name_device}\n")
    print(f"อุปกรณ์ '{name_device}' ถูกเพิ่มเรียบร้อยแล้ว.")

# ฟังก์ชันสำหรับการอ่านชื่ออุปกรณ์ทั้งหมดจากไฟล์
def read_devices():
    try:
        with open(FILE_PATH, 'r') as file:
            print("\n-- รายชื่ออุปกรณ์ทั้งหมด --")
            lines = file.readlines()
            if not lines:
                print("ยังไม่มีชื่ออุปกรณ์ที่บันทึกไว้.")
            else:
                # ใช้ tabulate เพื่อแสดงตารางสวยงาม
                table_data = [[index + 1, line.strip()] for index, line in enumerate(lines)]
                print(tabulate(table_data, headers=["ลำดับ", "ชื่ออุปกรณ์"], tablefmt="grid"))
    except FileNotFoundError:
        print("ยังไม่มีอุปกรณ์บันทึกในไฟล์.")

# ฟังก์ชันแก้ไขชื่ออุปกรณ์โดยระบุหมายเลขบรรทัด
def update_device(line_number, new_name_device):
    try:
        with open(FILE_PATH, 'r') as file:
            lines = file.readlines()

        if 1 <= line_number <= len(lines):  # ตรวจสอบว่าหมายเลขบรรทัดถูกต้องหรือไม่
            lines[line_number - 1] = f"{new_name_device}\n"  # แก้ไขข้อมูลในบรรทัดที่ระบุ
            with open(FILE_PATH, 'w') as file:
                file.writelines(lines)
            print(f"อุปกรณ์ในบรรทัดที่ {line_number} ถูกอัปเดตเป็น '{new_name_device}' เรียบร้อยแล้ว.")
        else:
            print(f"ไม่พบอุปกรณ์ในบรรทัดที่ {line_number}.")
    except FileNotFoundError:
        print("ไฟล์ไม่พบ ไม่สามารถอัปเดตอุปกรณ์ได้.")

# ฟังก์ชันลบชื่ออุปกรณ์โดยระบุหมายเลขบรรทัด
def delete_device(line_number):
    try:
        with open(FILE_PATH, 'r') as file:
            lines = file.readlines()

        if 1 <= line_number <= len(lines):  # ตรวจสอบว่าหมายเลขบรรทัดถูกต้องหรือไม่
            del lines[line_number - 1]  # ลบข้อมูลในบรรทัดที่ระบุ
            with open(FILE_PATH, 'w') as file:
                file.writelines(lines)
            print(f"อุปกรณ์ในบรรทัดที่ {line_number} ถูกลบเรียบร้อยแล้ว.")
        else:
            print(f"ไม่พบอุปกรณ์ในบรรทัดที่ {line_number}.")
    except FileNotFoundError:
        print("ไม่พบไฟล์ ไม่สามารถลบอุปกรณ์ได้.")

# ฟังก์ชันค้นหาอุปกรณ์จากชื่อ
def search_device(query):
    try:
        with open(FILE_PATH, 'r') as file:
            lines = file.readlines()
            print(f"\n-- ผลการค้นหาอุปกรณ์ '{query}' --")
            found = False
            results = []
            for index, line in enumerate(lines, start=1):
                if query in line:
                    results.append([index, line.strip()])
                    found = True
            if found:
                print(tabulate(results, headers=["ลำดับ", "ชื่ออุปกรณ์"], tablefmt="grid"))
            else:
                print(f"ไม่พบอุปกรณ์ '{query}'.")
    except FileNotFoundError:
        print("ไม่พบไฟล์ ไม่สามารถค้นหาอุปกรณ์ได้.")

# ฟังก์ชันรันไฟล์ callback.py
def run_callback():
    try:
        print("กำลังรันไฟล์ callback.py...")
        os.system('python3 callback.py')  # เรียกใช้ callback.py
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการรัน callback.py: {e}")

# ฟังก์ชันหลักสำหรับแสดงเมนูและดำเนินการต่าง ๆ
def main():
    while True:
        print("\n-- ตัวเลือกการจัดการอุปกรณ์ --")
        print("1. เพิ่มชื่ออุปกรณ์")
        print("2. ดูรายชื่ออุปกรณ์ทั้งหมด")
        print("3. แก้ไขชื่ออุปกรณ์")
        print("4. ลบชื่ออุปกรณ์")
        print("5. ค้นหาชื่ออุปกรณ์")
        print("6. รันไฟล์ callback.py")  # เพิ่มตัวเลือกใหม่
        print("7. ออกจากโปรแกรม")

        choice = input("กรุณาเลือกหมายเลขตัวเลือก: ")

        if choice == '1':
            name_device = input("กรุณากรอกชื่ออุปกรณ์: ")
            create_device(name_device)
        elif choice == '2':
            read_devices()
        elif choice == '3':
            line_number = int(input("กรุณากรอกหมายเลขบรรทัดที่ต้องการแก้ไข: "))
            new_name_device = input("กรอกชื่ออุปกรณ์ใหม่: ")
            update_device(line_number, new_name_device)
        elif choice == '4':
            line_number = int(input("กรุณากรอกหมายเลขบรรทัดที่ต้องการลบ: "))
            delete_device(line_number)
        elif choice == '5':
            query = input("กรุณากรอกชื่ออุปกรณ์ที่ต้องการค้นหา: ")
            search_device(query)
        elif choice == '6':
            run_callback()  # เรียกใช้ฟังก์ชันรัน callback.py
        elif choice == '7':
            print("กำลังออกจากโปรแกรม...")
            break
        else:
            print("กรุณาเลือกหมายเลขตัวเลือกที่ถูกต้อง.")

if __name__ == "__main__":
    main()
