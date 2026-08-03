from flask_sqlalchemy import SQLAlchemy

# app.py, models.py, routes/*.py가 모두 이 파일에서 db를 가져오도록 통일
# (models.py나 routes에서 'from app import db'를 하면, 특히 python app.py로 직접 실행할 때
#  app.py 자신이 다시 통째로 import되면서 순환 참조가 발생함 -> 이를 원천 차단)
db = SQLAlchemy()