import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.attacks.sqli import SQLIAttack
from generator.attacks.xss import XSSAttack
from generator.attacks.idor import IDORAttack
from generator.attacks.csrf import CSRFAttack
from generator.attacks.rce import RCEAttack
from generator.attacks.lfi import LFIAttack
from generator.attacks.cmdi import CMDIAttack
from generator.traffic import normal

BASE_URL = "http://testserver"

def test_sqli_structure():
    attack = SQLIAttack()
    req, meta = attack.generate(BASE_URL)
    assert meta["type"] == "SQLI"
    assert "payload" in meta
    assert req["url"].startswith(BASE_URL)

def test_xss_structure():
    attack = XSSAttack()
    req, meta = attack.generate(BASE_URL)
    assert meta["type"] == "XSS"
    assert "<" in meta["payload"] or "javascript" in meta["payload"]

def test_idor_structure():
    attack = IDORAttack()
    req, meta = attack.generate(BASE_URL)
    assert meta["type"] == "IDOR"
    assert meta["payload"].isdigit()

def test_csrf_structure():
    attack = CSRFAttack()
    req, meta = attack.generate(BASE_URL)
    assert meta["type"] == "CSRF"
    assert req["method"] == "POST"
    # CSRF usually has no token, but has referer/cookies
    assert "Referer" in req["headers"]

def test_rce_structure():
    attack = RCEAttack()
    req, meta = attack.generate(BASE_URL)
    assert meta["type"] == "RCE"
    assert "payload" in meta
    assert req["url"].startswith(BASE_URL)

def test_lfi_structure():
    attack = LFIAttack()
    req, meta = attack.generate(BASE_URL)
    assert meta["type"] == "LFI"
    assert "payload" in meta
    assert req["url"].startswith(BASE_URL)
    assert "params" in req
    assert "file" in req["params"]

def test_cmdi_structure():
    attack = CMDIAttack()
    req, meta = attack.generate(BASE_URL)
    assert meta["type"] == "CMDI"
    assert "payload" in meta
    assert req["url"].startswith(BASE_URL)

def test_normal_traffic():
    req = normal.generate(BASE_URL)
    assert req["method"] == "GET"
    assert req["url"].startswith(BASE_URL)
    assert "User-Agent" in req["headers"]
