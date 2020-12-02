from pathlib import Path  # Python 3.6+ only

# load env
env_path = Path('.env')
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)

# registy router first
import app.api.index
import app.api.admin