import pathlib

CREDENTIALS_PATH = pathlib.Path.home() / ".diffbot" / "credentials"


def load_token() -> str:
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"Credentials file not found at {CREDENTIALS_PATH}. "
            "Create one with: echo \"token=YOUR_TOKEN\" > ~/.diffbot/credentials && chmod 600 ~/.diffbot/credentials"
        )
    for line in CREDENTIALS_PATH.read_text().splitlines():
        line = line.strip()
        if line.startswith("token="):
            token = line[len("token="):].strip()
            if not token:
                raise ValueError("token= line is empty in ~/.diffbot/credentials")
            return token
    raise ValueError("No token= line found in ~/.diffbot/credentials")
