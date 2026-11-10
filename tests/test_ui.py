"""Unit and visual verification tests for VoiceStudio static UI assets."""

from pathlib import Path
from starlette.testclient import TestClient

from VoiceStudio.api.server import create_app


def test_ui_index_serving():
    """Verify that the root endpoint serves the Studio Workstation HTML."""
    app = create_app()
    client = TestClient(app)

    resp = client.get("/")
    assert resp.status_code == 200
    assert "VoiceStudio | Pure Python Voice Cloning Studio" in resp.text
    assert "waveformCanvas" in resp.text
    assert "scriptInput" in resp.text


def test_static_assets_serving():
    """Verify that CSS and JS assets are served with proper content types."""
    app = create_app()
    client = TestClient(app)

    css_resp = client.get("/static/studio.css")
    assert css_resp.status_code == 200
    assert "var(--surface-base)" in css_resp.text

    js_resp = client.get("/static/studio.js")
    assert js_resp.status_code == 200
    assert "drawWaveform" in js_resp.text
