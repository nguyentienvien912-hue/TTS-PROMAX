# TTS PROMAX — báo cáo bàn giao

Đã đổi tên hiển thị ở giao diện 21 ngôn ngữ, tiêu đề trang, tray, tên sản phẩm đóng gói, chẩn đoán và bảng theme. Dark theme mặc định: nền xanh đen, violet, chữ sáng; favicon đổi màu cùng bảng màu. Không sửa cấu trúc JSX, vị trí, kích thước hoặc luồng thao tác. Các theme khác vẫn chọn được.

## Kiểm tra
- Cài thư viện với bun 1.4.2 và frozen lockfile: đạt.
- Kiểm tra locale: 21 files đạt; 1681 khóa renderer có đủ; không thiếu bản dịch.
- Typecheck renderer và main: đạt.
- Build web production: đạt (Vite 8.3.0, chạy với Bun và configLoader native để tránh lỗi công cụ Windows trong môi trường này).
- Chạy máy chủ web local: HTTP 200, tiêu đề TTS PROMAX và các asset đầu trang trả 200. Chưa kiểm tra tương tác trực quan trong trình duyệt.
- Tương phản chữ chính, chữ phụ và nút chính: đều > 4.5:1.
- Notebook: mọi code cell kiểm tra cú pháp Python đạt; đường cache đồng nhất với backend; build dùng Electron web hiện tại; upload ZIP tùy chỉnh thay vì clone upstream chưa sửa.
- So sánh với ZIP GitHub: toàn bộ backend, engine, package/module, dependencies và lockfiles không thay đổi.
- Build Electron và Vitest: bị chặn bởi EPERM khi môi trường mở tiến trình phụ; chưa xác nhận đạt.
- Chưa chạy Colab/GPU hoặc tạo audio thật: không có phiên Colab/GPU được kết nối. Notebook chứa health check và cell tạo WAV/phát audio để xác nhận tại Colab.
- Build web còn cảnh báo chunk lớn/dynamic import của upstream; không sửa logic để xử lý cảnh báo.

## Dùng trên Colab
Mở TTS_PROMAX_Colab.ipynb ở Google Colab, chọn GPU, chạy các cell setup theo thứ tự và tải TTS_PROMAX_source.zip khi được hỏi. Drive mặc định lưu tại MyDrive/TTS_PROMAX/{data,models}. Chạy cell mở app rồi smoke test TTS. Các cell feature tour là tùy chọn. Những chức năng phụ thuộc OS desktop cần chạy bản Electron.

Đây là bản mã nguồn tùy chỉnh cục bộ; chưa push lên GitHub hay tạo fork. Giữ nguyên giấy phép/ghi công upstream.

## Các file sửa/thêm
- `electron/src/renderer/src/i18n/locales/ar.json`
- `electron/src/renderer/src/i18n/locales/de.json`
- `electron/src/renderer/src/i18n/locales/en.json`
- `electron/src/renderer/src/i18n/locales/es.json`
- `electron/src/renderer/src/i18n/locales/fr.json`
- `electron/src/renderer/src/i18n/locales/hi.json`
- `electron/src/renderer/src/i18n/locales/id.json`
- `electron/src/renderer/src/i18n/locales/it.json`
- `electron/src/renderer/src/i18n/locales/ja.json`
- `electron/src/renderer/src/i18n/locales/ko.json`
- `electron/src/renderer/src/i18n/locales/nl.json`
- `electron/src/renderer/src/i18n/locales/pl.json`
- `electron/src/renderer/src/i18n/locales/pt.json`
- `electron/src/renderer/src/i18n/locales/ru.json`
- `electron/src/renderer/src/i18n/locales/sv.json`
- `electron/src/renderer/src/i18n/locales/th.json`
- `electron/src/renderer/src/i18n/locales/tr.json`
- `electron/src/renderer/src/i18n/locales/uk.json`
- `electron/src/renderer/src/i18n/locales/vi.json`
- `electron/src/renderer/src/i18n/locales/zh-CN.json`
- `electron/src/renderer/src/i18n/locales/zh-TW.json`
- `electron/src/renderer/index.html`
- `electron/src/main/blank-window-guard.ts`
- `electron/src/main/index.ts`
- `electron/electron-builder.config.mjs`
- `electron/src/renderer/src/lib/themes/t3-palettes.ts`
- `electron/src/renderer/src/lib/themes/tauri-palette.ts`
- `electron/src/renderer/src/features/settings/diagnostics-settings.tsx`
- `electron/src/renderer/src/components/report-bug.tsx`
- `electron/src/renderer/src/components/app-shell/sponsor-inquiry.tsx`
- `electron/src/renderer/src/styles/t3-theme.css`
- `notebooks/TTS_PROMAX_Colab.ipynb`
- `docs/TTS_PROMAX_COLAB.md`
- `electron/public/favicon.svg`
