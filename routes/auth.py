from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User
from extensions import db
import os

auth_bp = Blueprint('auth', __name__)

# SECURITY_LEVEL: 추후 Phase별로 보안 강도를 다르게 적용하기 위한 스위치
# level 1 = 취약 버전 (평문 비밀번호 저장/비교), level 2 이상 = 해싱 적용 예정
SECURITY_LEVEL = os.getenv('SECURITY_LEVEL', '1')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        flash('아이디와 비밀번호를 모두 입력해주세요.')
        return redirect(url_for('auth.register'))

    existing = User.query.filter_by(username=username).first()
    if existing:
        flash('이미 존재하는 아이디입니다.')
        return redirect(url_for('auth.register'))

    # SECURITY_LEVEL 1: 실습 목적으로 비밀번호를 평문으로 저장
    new_user = User(username=username, password=password)
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

    # SECURITY_LEVEL 1: 평문 비교 (해시 검증은 다음 단계에서 추가 예정)
    if user and user.password == password:
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        flash(f'{user.username}님 환영합니다.')
        return redirect(url_for('index'))

    flash('아이디 또는 비밀번호가 올바르지 않습니다.')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))