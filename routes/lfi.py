import os
from flask import Blueprint, request
from urllib.parse import unquote
from werkzeug.utils import secure_filename

lfi_bp = Blueprint('lfi', __name__)


@lfi_bp.route('/view')
def view_file():
    target = request.args.get('file', 'notice.txt')

    # 현재 적용된 방어 로직 (Phase 2 수준)
    # URL 디코딩을 한 번만 수행한 뒤 '../'를 반복 제거하지만,
    # 이중 URL 인코딩(예: %252e%252e%252f)을 쓰면 여전히 우회 가능함 (의도적으로 유지)
    decoded_target = unquote(target)
    clean_target = decoded_target
    while '../' in clean_target:
        clean_target = clean_target.replace('../', '')
    file_path = os.path.join('files', clean_target)

    # [참고/비교용] Phase 1 수준 취약 코드 - '../'를 한 번만 치환해서 '....//' 로 손쉽게 우회 가능 (현재는 사용하지 않음)
    # clean_target = target.replace('../', '')
    # file_path = os.path.join('files', clean_target)

    # [참고/비교용] Phase 3 수준 방어 코드 - 화이트리스트 기반으로 완전히 차단, 우회 불가 (현재는 사용하지 않음)
    # safe_target = secure_filename(target)
    # if safe_target not in ['notice.txt', 'schedule.txt', 'form.txt']:
    #     return "Access Denied: 허용되지 않은 파일입니다.", 403
    # file_path = os.path.join('files', safe_target)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f"<pre>{f.read()}</pre>"
    except Exception as e:
        return f"File not found or error: {str(e)}", 404