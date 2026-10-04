"""TTS PROMAX one-click Colab launcher; also embedded into the notebook."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.parse

REPO_URL = 'https://github.com/nguyentienvien912-hue/TTS-PROMAX.git'
REPO_DIR = Path('/content/TTS-PROMAX')
PORT = 3900
BUN = Path('/root/.bun/bin/bun')
STORAGE = Path('/content/drive/MyDrive/TTS_PROMAX')
START_LOG = Path('/content/tts_promax_startup.log')
BACKEND_LOG = Path('/content/omnivoice_backend.log')
PID_FILE = Path('/content/tts_promax_backend.pid')
PRESET_ID = 'a_1c2c6d18f8'
PRESET_NAME = 'PROMAX Natural Conversations'

def ensure_preset_voice():
    """Use the existing idempotent designer; reference WAV and profile live in Drive.

    This is an original designed voice, not the ElevenLabs Mark recording.
    Never import a gallery preview or bypass the synthetic-audio pipeline.
    """
    stage('Chuẩn bị giọng ' + PRESET_NAME + ' (nam trẻ, giọng Mỹ)…')
    query = urllib.parse.urlencode({'name': PRESET_NAME})
    request = urllib.request.Request(
        f'http://127.0.0.1:{PORT}/archetypes/{PRESET_ID}/use?{query}',
        data=b'', method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=900) as response:
            profile = json.load(response)
        if not profile.get('profile_id') or not profile.get('name'):
            raise ValueError('Backend không trả về hồ sơ giọng hợp lệ.')
    except Exception as error:
        raise RuntimeError(
            'Chưa tạo được giọng có sẵn. Chạy lại ô khởi động để thử lại; '
            'không cần xóa model hoặc dữ liệu Drive. Chi tiết: ' + str(error)
        ) from error
    stage('Giọng đã có trong Hồ sơ đã lưu: ' + profile['name'])
    return profile

def stage(message):
    print('\n' + message, flush=True)

def run(command, cwd=None, env=None):
    with START_LOG.open('ab') as log:
        result = subprocess.run(command, cwd=cwd, env=env, stdout=log,
                                stderr=subprocess.STDOUT)
    if result.returncode:
        tail = '\n'.join(START_LOG.read_text(errors='replace').splitlines()[-45:])
        raise RuntimeError('Khởi động bị lỗi. Nhật ký: ' + str(START_LOG) + '\n' + tail)

def get_json(path):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{PORT}' + path, timeout=8) as response:
            return json.load(response)
    except Exception:
        return None

def open_app():
    from google.colab import output
    stage('TTS PROMAX đã sẵn sàng. Bấm đường link dưới đây để vào app.')
    stage('Giữ phiên Colab này kết nối trong lúc làm việc.')
    output.serve_kernel_port_as_window(PORT)

def prepare_colab_ui():
    """Support the already-published repo without requiring a manual ZIP update."""
    path = REPO_DIR / 'electron/src/renderer/src/components/setup-gate.tsx'
    text = path.read_text(encoding='utf8')
    marker = 'VITE_TTS_PROMAX_QUICK_START'
    if marker not in text:
        old = 'const completed = setupWasCompleted();'
        replacement = '''// Opt-in web build; launcher already verified model readiness.
    const completed = setupWasCompleted() ||
      (__WEB_DEPLOYMENT__ && import.meta.env.VITE_TTS_PROMAX_QUICK_START === '1' &&
       status.data.models_ready === true);'''
        if text.count(old) != 1:
            raise RuntimeError('Mã nguồn màn hình thiết lập đã thay đổi; cần cập nhật launcher.')
        path.write_text(text.replace(old, replacement), encoding='utf8')
    # Track the one temporary patch so git updates can safely restore only it.
    (REPO_DIR / '.colab-ui-patch').write_text('1')

def main():
    if not shutil.which('nvidia-smi'):
        raise RuntimeError('Chọn Thời gian chạy > Thay đổi loại thời gian chạy > T4 GPU, rồi chạy lại.')
    stage('1/7 — Kết nối Google Drive…')
    from google.colab import drive
    drive.mount('/content/drive')
    for name in ('data', 'models'):
        (STORAGE / name).mkdir(parents=True, exist_ok=True)
    os.environ.update({
        'OMNIVOICE_DATA_DIR': str(STORAGE / 'data'),
        'OMNIVOICE_CACHE_DIR': str(STORAGE / 'models'),
        'HF_HOME': str(STORAGE / 'models'),
        'HF_HUB_CACHE': str(STORAGE / 'models'),
        'TORCH_HOME': str(STORAGE / 'models'),
        'HF_TOKEN_PATH': '/content/tts_promax_hf_token',
        'UV_HTTP_TIMEOUT': '300',
    })
    if get_json('/health'):
        # A live backend must not be replaced while jobs might be running.
        status = get_json('/setup/status')
        if status and status.get('models_ready'):
            stage('App đang chạy. Mở lại phiên hiện tại, không cài lại.')
            ensure_preset_voice()
            open_app()
            return
        raise RuntimeError('Một backend đang chạy nhưng chưa sẵn sàng. Dừng công việc rồi khởi động lại phiên Colab.')
    # Stop only a backend recorded by this launcher and positively identified.
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text())
        cmdline = Path(f'/proc/{pid}/cmdline')
        if cmdline.exists():
            command = cmdline.read_bytes().decode(errors='replace')
            proc_cwd = Path(f'/proc/{pid}/cwd').resolve()
            if 'uvicorn' in command and proc_cwd == REPO_DIR.resolve():
                os.kill(pid, 15)
                time.sleep(2)
                if cmdline.exists():
                    raise RuntimeError('Backend cũ chưa dừng. Khởi động lại phiên Colab rồi chạy ô này.')

    stage('2/7 — Lấy phiên bản TTS PROMAX mới nhất từ GitHub…')
    if (REPO_DIR / '.git').is_dir():
        origin = subprocess.check_output(['git', 'remote', 'get-url', 'origin'],
                                         cwd=REPO_DIR, text=True).strip()
        if origin.removesuffix('.git') != REPO_URL.removesuffix('.git'):
            raise RuntimeError('Thư mục đang thuộc repo khác. Hãy dùng phiên Colab mới.')
        patch_marker = REPO_DIR / '.colab-ui-patch'
        if patch_marker.exists():
            # Only restore the exact source file temporarily patched by us.
            run(['git', 'restore', '--', 'electron/src/renderer/src/components/setup-gate.tsx'], cwd=REPO_DIR)
            patch_marker.unlink()
        run(['git', 'pull', '--ff-only', 'origin', 'main'], cwd=REPO_DIR)
    else:
        run(['git', 'clone', '--depth', '1', '--branch', 'main', REPO_URL, str(REPO_DIR)])
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO_DIR, text=True).strip()
    print('Phiên bản:', revision[:8])
    state_file = REPO_DIR / '.colab-install-state.json'
    state = {'revision': revision, 'python': sys.version, 'launcher': 2}
    try:
        installed = json.loads(state_file.read_text()) == state
    except (OSError, ValueError):
        installed = False

    stage('3/7 — Chuẩn bị thư viện và công cụ âm thanh…')
    if not installed:
        run(['apt-get', '-qq', 'update'])
        run(['apt-get', '-qq', 'install', '-y', 'ffmpeg', 'libsndfile1', 'unzip'])
        if not BUN.exists():
            run(['bash', '-c', "curl -fsSL https://bun.sh/install | bash -s 'bun-v1.4.2'"])
        os.environ['PATH'] = str(BUN.parent) + os.pathsep + os.environ['PATH']
        if not shutil.which('uv'):
            run([sys.executable, '-m', 'pip', 'install', '-q', 'uv'])
        run(['uv', 'pip', 'install', '--system', '--no-cache', '--constraint',
             'deploy/torch-constraints.txt', '.'], cwd=REPO_DIR)
        (REPO_DIR / '.venv').mkdir(exist_ok=True)
        run([sys.executable, str(REPO_DIR / 'scripts/setup.py')], cwd=REPO_DIR)
    os.environ['PATH'] = str(BUN.parent) + os.pathsep + os.environ['PATH']
    run([sys.executable, '-c',
         "import torch, torchaudio, uvicorn, transformers; "
         "from omnivoice.models.omnivoice import OmniVoice; "
         "from transformers import HiggsAudioV2TokenizerModel; "
         "assert torch.cuda.is_available(), 'CUDA is not available'"], cwd=REPO_DIR)

    stage('4/7 — Chuẩn bị giao diện để vào thẳng studio…')
    prepare_colab_ui()
    dist = REPO_DIR / 'frontend/dist/index.html'
    if not installed or not dist.is_file():
        run([str(BUN), 'install', '--frozen-lockfile'], cwd=REPO_DIR)
        build_env = os.environ.copy()
        build_env['VITE_TTS_PROMAX_QUICK_START'] = '1'
        run([str(BUN), 'run', 'build:web'], cwd=REPO_DIR, env=build_env)

    stage('5/7 — Tự tải model TTS, nhận dạng giọng nói và dịch thuật vào Drive…')
    # Fresh interpreter: no stale Colab-kernel imports or old HF cache constants.
    model_code = '''from huggingface_hub import snapshot_download
for repo in ('k2-fsa/OmniVoice', 'Systran/faster-whisper-large-v3', 'facebook/nllb-200-distilled-600M'):
    print('Preparing', repo, flush=True)
    snapshot_download(repo)
'''
    run([sys.executable, '-c', model_code], cwd=REPO_DIR)
    state_file.write_text(json.dumps(state))

    stage('6/7 — Khởi động và kiểm tra backend trên GPU…')
    env = os.environ.copy()
    env.update({'OMNIVOICE_SERVER_MODE': '1', 'PYTHONUNBUFFERED': '1'})
    with BACKEND_LOG.open('ab') as log:
        proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'main:app',
                                 '--app-dir', 'backend', '--host', '127.0.0.1',
                                 '--port', str(PORT)], cwd=REPO_DIR, env=env,
                                stdout=log, stderr=subprocess.STDOUT)
    PID_FILE.write_text(str(proc.pid))
    deadline = time.monotonic() + 360
    ready = None
    while time.monotonic() < deadline and proc.poll() is None:
        health = get_json('/health')
        ready = get_json('/setup/status') if health else None
        if ready and ready.get('models_ready'):
            break
        time.sleep(3)
    if not ready or not ready.get('models_ready'):
        tail = '\n'.join(BACKEND_LOG.read_text(errors='replace').splitlines()[-45:])
        raise RuntimeError('Backend chưa sẵn sàng. Gửi ảnh phần lỗi này:\n' + tail)
    ensure_preset_voice()
    stage('7/7 — Hoàn tất. Dữ liệu và model lưu tại MyDrive/TTS_PROMAX.')
    open_app()

if __name__ == '__main__':
    main()
