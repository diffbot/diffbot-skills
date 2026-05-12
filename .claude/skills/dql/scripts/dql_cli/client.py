import json
import pathlib
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from .credentials import load_token

DQL_ENDPOINT = "https://kg.diffbot.com/kg/v3/dql"
ONTOLOGY_ENDPOINT = "https://kg.diffbot.com/kg/ontology"


@dataclass
class DQLRequest:
    query: str
    size: int = 10
    from_: int = 0
    format: str = "json"
    filter: Optional[str] = None
    exportspec: Optional[str] = None
    extra: Dict[str, str] = field(default_factory=dict)

    def to_params(self, token: str) -> List[tuple]:
        params: List[tuple] = [("token", token), ("query", self.query), ("size", str(self.size))]
        if self.from_:
            params.append(("from", str(self.from_)))
        if self.format and self.format != "json":
            params.append(("format", self.format))
        if self.filter:
            params.append(("filter", self.filter))
        if self.exportspec:
            params.append(("exportspec", self.exportspec))
        for k, v in self.extra.items():
            params.append((k, v))
        return params


def _build_url(req: DQLRequest, token: str) -> str:
    return f"{DQL_ENDPOINT}?{urllib.parse.urlencode(req.to_params(token))}"


def _fetch_bytes(url: str, timeout: int = 60) -> bytes:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"HTTP {e.code} from DQL API: {body[:500]}") from None


def execute_json(req: DQLRequest, token: Optional[str] = None) -> Dict[str, Any]:
    token = token or load_token()
    url = _build_url(req, token)
    return json.loads(_fetch_bytes(url))


def execute_raw(req: DQLRequest, token: Optional[str] = None) -> bytes:
    token = token or load_token()
    url = _build_url(req, token)
    return _fetch_bytes(url)


def execute_parallel(reqs: Sequence[DQLRequest], token: Optional[str] = None, workers: int = 8) -> List[Dict[str, Any]]:
    token = token or load_token()
    urls = [_build_url(r, token) for r in reqs]
    with ThreadPoolExecutor(max_workers=min(workers, max(1, len(urls)))) as ex:
        bodies = list(ex.map(_fetch_bytes, urls))
    return [json.loads(b) for b in bodies]


def refresh_ontology(dest: pathlib.Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(_fetch_bytes(ONTOLOGY_ENDPOINT))
