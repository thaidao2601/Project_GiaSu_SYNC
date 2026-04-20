import sqlite3

# 1. Tạo kết nối đến file cơ sở dữ liệu. 
# Nếu file này chưa tồn tại, Python sẽ tự động tạo mới nó.
connection = sqlite3.connect('sync_database.db')

# 2. Mở và đọc nội dung của "bản vẽ" setup.sql
with open('setup.sql', 'r', encoding='utf-8') as file:
    sql_script = file.read()

# 3. Tạo một 'cursor' (con trỏ) để chạy các lệnh SQL
cursor = connection.cursor()
cursor.executescript(sql_script)

# 4. Lưu lại các thay đổi và đóng kết nối
connection.commit()
connection.close()

print("Khởi tạo Database thành công! Cửa nhà kho đã mở.")