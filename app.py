from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
# ĐÂY LÀ CHÌA KHÓA ĐỂ DÙNG SESSION (Bạn có thể gõ chữ gì cũng được)
app.secret_key = 'chuyen_gia_lap_trinh_sync_2026' 

def get_db_connection():
    conn = sqlite3.connect('sync_database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form['action']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        conn = get_db_connection()

        if action == 'register':
            confirm_password = request.form.get('confirm_password')
            full_name = request.form.get('full_name')
            
            # KIỂM TRA MẬT KHẨU CÓ KHỚP KHÔNG
            if password != confirm_password:
                return "<h1>Lỗi: Hai mật khẩu không khớp nhau!</h1> <a href='/login'>Thử lại</a>"

            try:
                # 1. Tạo tài khoản trong bảng Users
                cursor = conn.cursor()
                cursor.execute('INSERT INTO Users (email, password, role) VALUES (?, ?, ?)', (email, password, role))
                
                # Lấy số ID vừa được tự động tạo ra
                new_user_id = cursor.lastrowid 

                # 2. Tạo hồ sơ trong bảng Profiles
                if role == 'tutor':
                    subjects = request.form.get('subjects')
                    price = request.form.get('price')
                    cursor.execute('INSERT INTO Profiles (user_id, full_name, subjects, price) VALUES (?, ?, ?, ?)', (new_user_id, full_name, subjects, price))
                else:
                    experience = request.form.get('experience') # Dùng cột này lưu Yêu cầu của phụ huynh
                    cursor.execute('INSERT INTO Profiles (user_id, full_name, experience) VALUES (?, ?, ?)', (new_user_id, full_name, experience))

                conn.commit()
                conn.close()
                return "<h1>Đăng ký thành công tuyệt đối!</h1> <a href='/login'>Bấm vào đây để Đăng nhập</a>"
            except sqlite3.IntegrityError:
                conn.close()
                return "<h1>Lỗi: Email này đã được đăng ký!</h1> <a href='/login'>Thử lại</a>"

        elif action == 'login':
            # KỸ THUẬT JOIN: Tìm trong bảng Users, đồng thời nối với bảng Profiles để lấy Full Name
            query = '''
                SELECT Users.id, Users.role, Profiles.full_name 
                FROM Users 
                JOIN Profiles ON Users.id = Profiles.user_id 
                WHERE email = ? AND password = ? AND role = ?
            '''
            user = conn.execute(query, (email, password, role)).fetchone()
            conn.close()

            if user:
                # GHI NHỚ THÔNG TIN VÀO SESSION (PHIÊN LÀM VIỆC)
                session['user_id'] = user['id']
                session['full_name'] = user['full_name'] # Lưu đúng tên thật của họ
                session['role'] = user['role']

                if role == 'parent':
                    return redirect('/home_parent')
                else:
                    return redirect('/home_tutor')
            else:
                return "<h1>Sai thông tin đăng nhập!</h1> <a href='/login'>Thử lại</a>"

    return render_template('login.html')

@app.route('/home_parent')
def home_parent():
    if 'user_id' not in session or session['role'] != 'parent':
        return redirect('/login')

    parent_id = session['user_id']
    conn = get_db_connection()
    
    # 1. Lấy danh sách TẤT CẢ GIA SƯ
    query = '''
        SELECT Profiles.full_name, Profiles.subjects, Profiles.price, Users.id as tutor_id
        FROM Users 
        JOIN Profiles ON Users.id = Profiles.user_id 
        WHERE Users.role = 'tutor'
    '''
    tutors = conn.execute(query).fetchall()

    # 2. Lấy danh sách ID các Gia sư mà Phụ huynh này ĐÃ GỬI yêu cầu
    req_query = 'SELECT tutor_id FROM Connections WHERE parent_id = ?'
    requested_rows = conn.execute(req_query, (parent_id,)).fetchall()
    # Biến nó thành một danh sách đơn giản (VD: [1, 3]) để dễ kiểm tra ở HTML
    requested_tutors = [row['tutor_id'] for row in requested_rows]

    conn.close()

    # Truyền cả 2 danh sách sang file HTML
    return render_template('home_parent.html', tutors=tutors, requested_tutors=requested_tutors)

@app.route('/home_tutor')
def home_tutor():
    if 'user_id' not in session or session['role'] != 'tutor':
        return redirect('/login')

    tutor_id = session['user_id']
    conn = get_db_connection()
    
    # KỸ THUẬT: Lấy thông tin Phụ huynh (từ bảng Profiles) thông qua bảng Connections
    query = '''
        SELECT Connections.id as conn_id, Profiles.full_name, Profiles.experience, Connections.status
        FROM Connections
        JOIN Profiles ON Connections.parent_id = Profiles.user_id
        WHERE Connections.tutor_id = ?
    '''
    requests_list = conn.execute(query, (tutor_id,)).fetchall()
    conn.close()

    return render_template('home_tutor.html', requests=requests_list)

@app.route('/connect', methods=['POST'])
def connect():
    if 'user_id' not in session or session['role'] != 'parent':
        return redirect('/login')

    tutor_id = request.form.get('tutor_id')
    parent_id = session['user_id']
    conn = get_db_connection()
    
    existing = conn.execute('SELECT * FROM Connections WHERE parent_id = ? AND tutor_id = ?', (parent_id, tutor_id)).fetchone()
    if not existing:
        conn.execute('INSERT INTO Connections (parent_id, tutor_id, status) VALUES (?, ?, ?)', (parent_id, tutor_id, 'pending'))
        conn.commit()
    conn.close()
    
    # Tự động tải lại trang danh sách cực mượt
    return redirect('/home_parent') 

# THÊM MỚI: Đường dẫn xử lý Hủy kết nối
@app.route('/disconnect', methods=['POST'])
def disconnect():
    if 'user_id' not in session or session['role'] != 'parent':
        return redirect('/login')

    tutor_id = request.form.get('tutor_id')
    parent_id = session['user_id']
    conn = get_db_connection()
    
    # Xóa bản ghi trong Database
    conn.execute('DELETE FROM Connections WHERE parent_id = ? AND tutor_id = ?', (parent_id, tutor_id))
    conn.commit()
    conn.close()
    
    return redirect('/home_parent')

# THÊM MỚI: Đường dẫn xử lý việc Gia sư phản hồi yêu cầu
@app.route('/update_request', methods=['POST'])
def update_request():
    # Kiểm tra bảo mật: Phải là Gia sư mới được gọi chức năng này
    if 'user_id' not in session or session['role'] != 'tutor':
        return redirect('/login')

    # Lấy ID của lời mời kết nối và hành động (chấp nhận hay từ chối)
    conn_id = request.form.get('conn_id')
    action = request.form.get('action') 
    
    # Dịch hành động thành trạng thái để lưu vào Database
    new_status = 'accepted' if action == 'accept' else 'declined'
    
    conn = get_db_connection()
    # Cập nhật trạng thái của đúng cái lời mời đó
    conn.execute('UPDATE Connections SET status = ? WHERE id = ? AND tutor_id = ?', 
                 (new_status, conn_id, session['user_id']))
    conn.commit()
    conn.close()
    
    # Xong việc thì tải lại trang Gia sư
    return redirect('/home_tutor')

if __name__ == '__main__':
    app.run(debug=True)