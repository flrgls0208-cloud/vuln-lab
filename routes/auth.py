import re
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__)
SPECIAL_CHARS = r"!@#$%^&*()\-_+=\[\]{};:'\",./?~|\\"
PASSWORD_PATTERN = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[' + re.escape(SPECIAL_CHARS) + r']).+$')


def is_valid_password(password):
    return bool(PASSWORD_PATTERN.match(password))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not username or not password or not confirm_password:
        flash('아이디와 비밀번호를 모두 입력해주세요.')
        return redirect(url_for('auth.register'))

    if password != confirm_password:
        flash('비밀번호가 일치하지 않습니다.')
        return redirect(url_for('auth.register'))

    if not is_valid_password(password):
        flash('비밀번호는 영문, 숫자, 특수문자를 모두 포함해야 합니다.')
        return redirect(url_for('auth.register'))

    existing = User.query.filter_by(username=username).first()
    if existing:
        flash('이미 존재하는 아이디입니다.')
        return redirect(url_for('auth.register'))

    # 비밀번호는 항상 해싱하여 저장 (평문 저장 방식은 더 이상 사용하지 않음)
    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, password=hashed_pw)

    # [참고/비교용] Phase 1 수준 취약 코드 - 비밀번호를 평문으로 저장 (현재는 사용하지 않음)
    # new_user = User(username=username, password=password)

    db.session.add(new_user)
    db.session.commit()

    flash('회원가입이 완료되었습니다. 로그인해주세요.')
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    user = User.query.filter_by(username=username).first()
    is_valid_password = False

    if user:
        # 비밀번호는 항상 해시로 검증 (평문 비교 방식은 더 이상 사용하지 않음)
        try:
            is_valid_password = check_password_hash(user.password, password)
        except ValueError:
            # DB에 예전 평문 데이터가 남아있는 경우를 대비한 예외 처리
            is_valid_password = False

        # [참고/비교용] Phase 1 수준 취약 코드 - 평문 비교 (현재는 사용하지 않음)
        # is_valid_password = (user.password == password)

    if user and is_valid_password:
        if user.session_id and session.get('user_id') != user.id:
            flash('이미 다른 기기에서 로그인 중입니다. 기존 로그인 세션이 우선 적용됩니다.')
            return redirect(url_for('auth.login'))

        new_session_id = str(uuid.uuid4())
        user.session_id = new_session_id
        db.session.commit()

        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['session_id'] = new_session_id
        
        flash(f'{user.username}님 환영합니다.')
        return redirect(url_for('index'))

    flash('아이디 또는 비밀번호가 올바르지 않습니다.')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.session_id = None
            db.session.commit()

    session.clear()
    return redirect(url_for('index'))