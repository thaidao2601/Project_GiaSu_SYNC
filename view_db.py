import sqlite3

# Kết nối vào database
conn = sqlite3.connect('sync_database.db')
cursor = conn.cursor()

print("--- DANH SÁCH TÀI KHOẢN (BẢNG USERS) ---")
users = cursor.execute('SELECT * FROM Users').fetchall()
for user in users:
    print(f"ID: {user[0]} | Email: {user[1]} | Mật khẩu: {user[2]} | Vai trò: {user[3]}")

print("\n--- HỒ SƠ CHI TIẾT (BẢNG PROFILES) ---")
profiles = cursor.execute('SELECT * FROM Profiles').fetchall()
for p in profiles:
    print(f"User_ID: {p[1]} | Tên: {p[2]} | Môn/Yêu cầu: {p[3] if p[3] else p[5]}")

# --- ĐÂY LÀ ĐOẠN CODE MỚI THÊM VÀO ---
print("\n--- LỜI MỜI KẾT NỐI (BẢNG CONNECTIONS) ---")
connections = cursor.execute('SELECT * FROM Connections').fetchall()
if len(connections) == 0:
    print(">> Hiện tại chưa có lời mời kết nối nào trong hệ thống.")
else:
    for c in connections:
        print(f"Mã kết nối: {c[0]} | Phụ huynh (ID: {c[1]}) ĐANG CHỜ GIA SƯ (ID: {c[2]}) | Trạng thái: {c[3]}")

conn.close()