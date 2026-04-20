-- 1. BẢNG USERS (Lưu thông tin tài khoản đăng nhập)
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Mã ID tự động tăng (1, 2, 3...)
    email TEXT UNIQUE NOT NULL,           -- Email bắt buộc có và không được trùng nhau
    password TEXT NOT NULL,               -- Mật khẩu
    role TEXT NOT NULL                    -- Vai trò (sẽ lưu chữ 'parent' hoặc 'tutor')
);

-- 2. BẢNG PROFILES (Lưu hồ sơ chi tiết để hiển thị lên thẻ)
CREATE TABLE Profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,                      -- Khóa ngoại: Liên kết để biết hồ sơ này của User nào
    full_name TEXT NOT NULL,              -- Họ và tên
    subjects TEXT,                        -- Môn học (VD: Toán, Tiếng Anh...)
    price TEXT,                           -- Mức lương/Học phí đề xuất
    experience TEXT,                      -- Kinh nghiệm (dành cho gia sư) hoặc Yêu cầu (dành cho phụ huynh)
    FOREIGN KEY(user_id) REFERENCES Users(id) 
);

-- 3. BẢNG CONNECTIONS (Lưu lịch sử các lần bấm nút "Kết nối")
CREATE TABLE Connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER,                    -- Mã ID của phụ huynh gửi yêu cầu
    tutor_id INTEGER,                     -- Mã ID của gia sư nhận yêu cầu
    status TEXT DEFAULT 'pending',        -- Trạng thái: Mặc định là 'pending' (Đang chờ)
    FOREIGN KEY(parent_id) REFERENCES Users(id),
    FOREIGN KEY(tutor_id) REFERENCES Users(id)
);