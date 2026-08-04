import os
from flask import Flask, render_template, session, redirect, url_for, flash
from dotenv import load_dotenv
from extensions import db
from models import User

# 1. 환경변수 로드
load_dotenv()

app = Flask(__name__)

# 2. DB 및 환경변수 설정
db_user = os.getenv('DB_USER', 'root')
db_pw = os.getenv('DB_PASSWORD', '0000')
db_host = os.getenv('DB_HOST', '192.168.111.40')        
db_port = os.getenv('DB_PORT', '3306')
db_name = os.getenv('DB_NAME', 'myapp_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')

# 3. SQLAlchemy 초기화
db.init_app(app)

# 4. Blueprint 모듈 불러오기 및 등록
from routes.lfi import lfi_bp
from routes.auth import auth_bp
from routes.board import board_bp
from routes.upload import upload_bp

app.register_blueprint(lfi_bp, url_prefix='/api/v1')
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(board_bp, url_prefix='/board')
app.register_blueprint(upload_bp, url_prefix='/upload')

# 5. DB 테이블 자동 생성
with app.app_context():
    import models
    db.create_all()
    print("[*] Database connected and tables checked.")

# 6. 중복 로그인 검증 미들웨어 (모든 요청 전 실행)
@app.before_request
def check_single_session():
    user_id = session.get('user_id')
    current_session_id = session.get('session_id')

    if user_id and current_session_id:
        user = User.query.get(user_id)
        if not user or user.session_id != current_session_id:
            session.clear()
            flash('중복 로그인은 허용되지 않습니다. 이미 로그인된 세션이 우선 적용됩니다.')
            return redirect(url_for('auth.login'))

# 7. 메인 라우트
@app.route('/')
def index():
    from models import Dsboard
    latest_posts = Dsboard.query.order_by(Dsboard.id.desc()).limit(3).all()
    return render_template('index.html', latest_posts=latest_posts)



if __name__ == '__main__':
    print("[*] Starting Server")
    app.run(host='0.0.0.0', port=5000, debug=True)