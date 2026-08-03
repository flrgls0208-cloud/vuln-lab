import os
from flask import Flask, render_template
from dotenv import load_dotenv
from extensions import db

# 1. 환경변수 로드
load_dotenv()

app = Flask(__name__)

# 2. DB 및 환경변수 설정 (기본값 도커용 'db' 설정)
db_user = os.getenv('DB_USER', 'root')
db_pw = os.getenv('DB_PASSWORD', '0000')
db_host = os.getenv('DB_HOST', 'db')        # 로컬 파이썬 실행 시 .env에서 localhost로 제어
db_port = os.getenv('DB_PORT', '3306')
db_name = os.getenv('DB_NAME', 'myapp_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_LEVEL'] = os.getenv('SECURITY_LEVEL', '1')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')

# 3. SQLAlchemy 초기화 (순환 참조 방지)
db.init_app(app)

# 4. Blueprint 모듈 불러오기 및 등록 (초기화 이후에 모듈을 가져옵니다)
from routes.lfi import lfi_bp
from routes.auth import auth_bp
from routes.board import board_bp
from routes.upload import upload_bp

app.register_blueprint(lfi_bp, url_prefix='/api/v1')
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(board_bp, url_prefix='/board')
app.register_blueprint(upload_bp, url_prefix='/upload')

# 5. DB 테이블 자동 생성 (models 모듈로드)
with app.app_context():
    import models  # User, Post 등의 DB 모델이 정의된 파일
    db.create_all()
    print("[*] Database connected and tables checked.")

# 6. 메인 라우트
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print(f"[*] Starting Target Server in PHASE: {os.getenv('SECURITY_LEVEL', '1')}")
    app.run(host='0.0.0.0', port=5000, debug=True)