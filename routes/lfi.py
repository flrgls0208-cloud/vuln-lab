import os
from flask import Blueprint, request
from urllib.parse import unquote
from werkzeug.utils import secure_filename

lfi_bp = Blueprint('lfi', __name__)

@lfi_bp.route('/view')
def view_file():
    target = request.args.get('file', 'notice.txt')
    level = os.getenv("SECURITY_LEVEL", "1")

    # [Phase 1] 단순 필터링: ....// 우회 가능
    if level == "1":
        clean_target = target.replace('../', '')
        file_path = os.path.join('files', clean_target)

    # [Phase 2] 반복 제거 로직: %252e%252e%252f (이중 인코딩) 우회 가능
    elif level == "2":
        decoded_target = unquote(target) 
        clean_target = decoded_target
        while '../' in clean_target:
            clean_target = clean_target.replace('../', '')
        file_path = os.path.join('files', clean_target)

    # [Phase 3] 화이트리스트 기반 완벽 방어
    else:
        safe_target = secure_filename(target)
        if safe_target not in ['notice.txt', 'schedule.txt', 'form.txt']:
            return "🛡️ [Phase 3] Access Denied: 허용되지 않은 파일입니다.", 403
        file_path = os.path.join('files', safe_target)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f"<pre>{f.read()}</pre>"
    except Exception as e:
        return f"File not found or error: {str(e)}", 404