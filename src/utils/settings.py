import json
from pathlib import Path

_CONFIG_DIR = Path.home() / ".ept"
_CONFIG_FILE = _CONFIG_DIR / "settings.json"

_DEFAULTS = {
    "api_key": "",
    "api_url": "https://api.openai.com/v1",
    "model_name": "gpt-4o",
    "cosyvoice_repo_dir": "",
    "cosyvoice_model_dir": "",
    "prompt_male_wav": "",
    "prompt_female_wav": "",
    "tts_output_dir": "",
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

    @property
    def cosyvoice_repo_dir(self) -> str:
        return self._data["cosyvoice_repo_dir"]

    @cosyvoice_repo_dir.setter
    def cosyvoice_repo_dir(self, value: str):
        self._data["cosyvoice_repo_dir"] = value
        self._save()

    @property
    def cosyvoice_model_dir(self) -> str:
        return self._data["cosyvoice_model_dir"]

    @cosyvoice_model_dir.setter
    def cosyvoice_model_dir(self, value: str):
        self._data["cosyvoice_model_dir"] = value
        self._save()

    @property
    def prompt_male_wav(self) -> str:
        return self._data["prompt_male_wav"]

    @prompt_male_wav.setter
    def prompt_male_wav(self, value: str):
        self._data["prompt_male_wav"] = value
        self._save()

    @property
    def prompt_female_wav(self) -> str:
        return self._data["prompt_female_wav"]

    @prompt_female_wav.setter
    def prompt_female_wav(self, value: str):
        self._data["prompt_female_wav"] = value
        self._save()

    @property
    def tts_output_dir(self) -> str:
        return self._data["tts_output_dir"]

    @tts_output_dir.setter
    def tts_output_dir(self, value: str):
        self._data["tts_output_dir"] = value
        self._save()

    def update(self, api_key: str, api_url: str, model_name: str):
        self._data["api_key"] = api_key
        self._data["api_url"] = api_url
        self._data["model_name"] = model_name
        self._save()

    def update_tts(
        self,
        cosyvoice_repo_dir: str,
        cosyvoice_model_dir: str,
        prompt_male_wav: str,
        prompt_female_wav: str,
        tts_output_dir: str,
    ):
        self._data["cosyvoice_repo_dir"] = cosyvoice_repo_dir
        self._data["cosyvoice_model_dir"] = cosyvoice_model_dir
        self._data["prompt_male_wav"] = prompt_male_wav
        self._data["prompt_female_wav"] = prompt_female_wav
        self._data["tts_output_dir"] = tts_output_dir
        self._save()
