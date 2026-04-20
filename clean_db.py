import sqlite3

# Kết nối vào database
conn = sqlite3.connect('sync_database.db')
cursor = conn.cursor()

# 1. Xoá toàn bộ lịch sử kết nối
cursor.execute('DELETE FROM Connections')

# 2. Reset lại bộ đếm ID (để lần sau có kết nối mới, ID lại bắt đầu từ 1)
cursor.execute('UPDATE sqlite_sequence SET seq = 0 WHERE name = "Connections"')

conn.commit()
conn.close()

print("Đã dọn sạch lịch sử kết nối! Các tài khoản Gia sư và Phụ huynh vẫn được giữ nguyên. Sẵn sàng đẩy lên Github!")