"""VoiceStudio Standalone Launcher.

Run with:
    python run.py
"""

import sys
import webbrowser
from VoiceStudio.config import config
from VoiceStudio.db.connection import DatabaseManager
from VoiceStudio.db.repository import VoiceProfileRepository
from VoiceStudio.db.schema import init_schema
from VoiceStudio.presets import seed_preset_voices


BANNER = r"""
 __      __   _            ____  _             _ _       
 \ \    / /  (_)          / ____|| |           | (_)      
  \ \  / /__  _  ___ ___ | (___  | |_ _   _  __| |_  ___  
   \ \/ / _ \| |/ __/ _ \ \___ \ | __| | | |/ _` | |/ _ \ 
    \  / (_) | | (_|  __/ ____) || |_| |_| | (_| | | (_) |
     \/ \___/|_|\___\___||_____/  \__|\__,_|\__,_|_|\___/ 
                                                          
 >> Autonomous Neural Voice Cloning & Audio Production Studio
 >> Pure Python | Local-First | CPU-Optimized | EBU R128 Compliant
"""


def bootstrap():
    print(BANNER)
    print("[*] Initializing local directories...")
    config.ensure_directories()

    print("[*] Verifying SQLite database and seeding factory voice presets...")
    db = DatabaseManager(config.db_path)
    with db.get_connection() as conn:
        init_schema(conn)

    profile_repo = VoiceProfileRepository(db)
    presets = seed_preset_voices(profile_repo)
    print(f"[+] Loaded {len(presets)} voice profiles ready for generation.")

    host = "127.0.0.1"
    port = 8000
    studio_url = f"http://{host}:{port}"
    print(f"\n[+] VoiceStudio Interface ready: {studio_url}")
    print("[+] Press Ctrl+C in terminal to stop the studio server.\n")

    try:
        import uvicorn
        uvicorn.run("VoiceStudio.api.server:app", host=host, port=port, log_level="info")
    except ImportError:
        print("[ERROR] uvicorn is required to run the server. Run: pip install uvicorn")
        sys.exit(1)


if __name__ == "__main__":
    bootstrap()
