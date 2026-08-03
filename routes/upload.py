from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import os

upload_bp = Blueprint('upload', __name__)

# lfi.py가 os.path.join('files', ...)로 파일을 읽으므로, 업로드 저장 위치도 동일한 files/ 디렉토리로 맞춤
# (업로드한 파일을 LFI 라우트로 그대로 읽어올 수 있게 하기 위한 의도적 연결)
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'files')


def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.')
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped


@upload_bp.route('/', methods=['GET'])
@login_required
def upload_form():
    files = os.listdir(UPLOAD_DIR) if os.path.isdir(UPLOAD_DIR) else []
    return render_template('upload.html', files=files)


@upload_bp.route('/', methods=['POST'])
@login_required
def upload_file():
    f = request.files.get('file')

    if not f or f.filename == '':
        flash('업로드할 파일을 선택해주세요.')
        return redirect(url_for('upload.upload_form'))

    # 실습 목적:
    # 1) 확장자 화이트리스트 검증 없음 -> 임의의 실행 가능 파일(.py, .php 등) 업로드 가능
    # 2) secure_filename() 미적용 -> 파일명에 경로 조작 문자(../ 등)가 있으면 업로드 루트 밖에 쓰일 수 있음
    filename = f.filename
    save_path = os.path.join(UPLOAD_DIR, filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    f.save(save_path)

    flash(f'"{filename}" 업로드 완료.')
    return redirect(url_for('upload.upload_form'))


@upload_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # 실습 목적: send_from_directory 대신 직접 경로 결합 -> filename에 ../ 포함 시 Path Traversal 가능
    # (읽는 대상 디렉토리가 files/ 이므로 lfi.py의 /api/v1/view?file= 로도 동일 파일에 접근 가능)
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, 'rb') as fp:
        data = fp.read()
    return data
