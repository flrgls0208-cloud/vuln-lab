import os
from functools import wraps

# 현재 보안 레벨 (1: Vulnerable, 2: Detectable, 3: Hardened)
CURRENT_PHASE = int(os.getenv("SECURITY_LEVEL", "1"))

def apply_secure_code(secure_func):
    """Phase 3(Hardened)일 때만 방어 로직(secure_func)을 실행하고, Phase 1/2에서는 취약한 로직 실행"""
    def decorator(vuln_func):
        @wraps(vuln_func)
        def wrapper(*args, **kwargs):
            if CURRENT_PHASE == 3:
                return secure_func(*args, **kwargs)
            else:
                return vuln_func(*args, **kwargs)
        return wrapper
    return decorator