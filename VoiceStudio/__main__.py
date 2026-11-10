"""Package entrypoint when executed as 'python -m VoiceStudio'."""

import sys
from VoiceStudio.cli import main

if __name__ == "__main__":
    sys.exit(main())
