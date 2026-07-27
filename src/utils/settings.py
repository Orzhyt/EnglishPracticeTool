import json
from pathlib import Path

_CONFIG_DIR = Path.home() / ".ept"
_CONFIG_FILE = _CONFIG_DIR / "settings.json"

_DEFAULTS = {
    "api_key": "",
    "api_url": "https://api.openai.com/v1",
    "model_name": "gpt-4o",
}


class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = dict(_DEFAULTS)
            cls._instance._load()
        return cls._instance

    def _load(self):
        if _CONFIG_FILE.exists():
            try:
                saved = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
                self._data.update(saved)
            except Exception:
                pass

    def _save(self):
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        _CONFIG_FILE.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @property
    def api_key(self) -> str:
        return self._data["api_key"]

    @api_key.setter
    def api_key(self, value: str):
        self._data["api_key"] = value
        self._save()

    @property
    def api_url(self) -> str:
        return self._data["api_url"]

    @api_url.setter
    def api_url(self, value: str):
        self._data["api_url"] = value
        self._save()

    @property
    def model_name(self) -> str:
        return self._data["model_name"]

    @model_name.setter
    def model_name(self, value: str):
        self._data["model_name"] = value
        self._save()

    def update(self, api_key: str, api_url: str, model_name: str):
        self._data["api_key"] = api_key
        self._data["api_url"] = api_url
        self._data["model_name"] = model_name
        self._save()
