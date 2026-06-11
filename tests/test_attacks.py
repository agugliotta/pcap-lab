import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.attacks import sqli, xss, idor, csrf, rce, lfi, cmdi
from generator.traffic import normal

BASE_URL = "http://testserver"

def test_sqli_structure():
    req, meta = sqli.generate(BASE_URL)
    assert meta["type"] == "SQLI"
    assert "payload" in meta
    assert req["url"].startswith(BASE_URL)

def test_xss_structure():
    req, meta = xss.generate(BASE_URL)
    assert meta["type"] == "XSS"
    assert "<" in meta["payload"] or "javascript" in meta["payload"]

def test_idor_structure():
    req, meta = idor.generate(BASE_URL)
    assert meta["type"] == "IDOR"
    assert meta["payload"].isdigit()

def test_csrf_structure():
    req, meta = csrf.generate(BASE_URL)
    assert meta["type"] == "CSRF"
    assert req["method"] == "POST"
    # CSRF usually has no token, but has referer/cookies
    assert "Referer" in req["headers"]

def test_rce_structure():
    req, meta = rce.generate(BASE_URL)
    assert meta["type"] == "RCE"
    assert "payload" in meta
    assert req["url"].startswith(BASE_URL)

def test_lfi_structure():
    req, meta = lfi.generate(BASE_URL)
    assert meta["type"] == "LFI"
    assert "payload" in meta
    assert req["url"].startswith(BASE_URL)
    assert "params" in req
    assert "file" in req["params"]

def test_cmdi_structure():
    req, meta = cmdi.generate(BASE_URL)
    assert meta["type"] == "CMDI"
    assert "payload" in meta
    assert req["url"].startswith(BASE_URL)

def test_normal_traffic():
    req = normal.generate(BASE_URL)
    assert req["method"] == "GET"
    assert req["url"].startswith(BASE_URL)
    assert "User-Agent" in req["headers"]
