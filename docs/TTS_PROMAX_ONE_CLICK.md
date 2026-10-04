# TTS PROMAX — khởi động Colab bằng một ô

Mở `notebooks/TTS_PROMAX_One_Click.ipynb` trong Colab, chọn GPU T4 và bấm nút chạy của ô **Khởi động TTS PROMAX**. Cấp quyền Google Drive nếu được hỏi. Chờ các bước hoàn tất, rồi bấm link mở app.

Launcher kết nối Drive, cập nhật nhánh main từ repo của người dùng, cài thư viện, build giao diện, tải model và kiểm tra backend. Khi app đang chạy, chạy lại ô chỉ mở lại app để không ngắt công việc. Muốn áp dụng code mới, dừng công việc và khởi động lại phiên Colab trước.

Model tự tải: OmniVoice (TTS đa ngôn ngữ), faster-whisper large-v3 (nhận dạng giọng nói), NLLB-200 distilled 600M (dịch thuật). Model nằm trong `MyDrive/TTS_PROMAX/models`; dữ liệu/output trong `MyDrive/TTS_PROMAX/data`, giống notebook cũ. Các engine hoặc model có điều khoản riêng vẫn cài thêm khi cần. Tải model không đồng nghĩa nạp tất cả vào VRAM; backend giữ cách nạp hiện tại.

Chỉ bản web do launcher build với `VITE_TTS_PROMAX_QUICK_START=1` mới bỏ màn hình thiết lập, và chỉ khi `/setup/status` xác nhận các model bắt buộc đã có. Backend và logic TTS giữ nguyên. Các lựa chọn analytics, watermark và lịch sử không bị đổi.

Để dùng ngay với repo đã xuất bản, launcher tự áp dụng chỉnh sửa nhỏ vào bản mã nguồn tạm ở Colab trước khi build. Không cần tải ZIP mã nguồn. Chỉnh sửa đó không được đẩy lên GitHub tự động. Khi giao diện upstream thay đổi ngoài mẫu đã biết, launcher dừng với lỗi để tránh bỏ qua kiểm tra sai.

Launcher tự tạo và lưu **PROMAX Natural Conversations** vào thư viện qua API thiết kế giọng có sẵn của app. Đặc tính: nam trẻ, cao độ vừa, giọng Anh Mỹ, phong cách hội thoại. Đây là giọng thiết kế riêng theo phong cách trong ảnh, không phải bản sao giọng Mark của ElevenLabs và chưa được đối chiếu với mẫu âm thanh.

Lần đầu, OmniVoice tạo một mẫu WAV làm hồ sơ giọng; những lần sau API dùng lại hồ sơ và mẫu đã lưu trên Drive, không tạo bản trùng. Nếu tạo giọng lỗi, launcher báo lỗi và có thể chạy lại ô để thử lại. Trong app, chọn **Hồ sơ đã lưu → PROMAX Natural Conversations**, nhập kịch bản, chọn ngôn ngữ và tạo âm thanh. Không cần khóa ElevenLabs. Chất lượng khi đọc ngôn ngữ khác cần nghe thử.

Notebook chỉ có một ô code, không chạy các demo video. Drive cần quyền của tài khoản người dùng; Colab vẫn có thể ngắt phiên. Thời gian đầu phụ thuộc tốc độ cài thư viện, tải model và tạo mẫu giọng. Ô startup không giữ GPU nóng liên tục.

Kiểm tra tại máy phát triển: cài frontend theo lockfile, build web bật chế độ Colab, typecheck renderer, 601 kiểm tra Python (launcher, archetype, locale, version) và 2 kiểm tra SetupGate. Chưa chạy notebook trên phiên Colab/GPU thực tế; quyền trình duyệt Colab bị từ chối, vì vậy chưa tạo hoặc nghe thử giọng trên GPU.
