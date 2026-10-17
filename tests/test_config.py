from __future__ import annotations

import pytest

from replypen_embassy import Config
from replypen_embassy.errors import Misconfigured

FETCH = "https://app.replypen.com/actions/script"
ENV_SUFFIXES = (
    "ACTION_SECRET",
    "FETCH_URL",
    "TRIGGER_URL",
    "SENT_MESSAGE_URL",
    "API_BASE_URL",
    "API_KEY",
    "CHAT_SECRET",
    "CHAT_PROJECT",
    "CHAT_BASE_URL",
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for suffix in ENV_SUFFIXES:
        monkeypatch.delenv(f"REPLYPEN_{suffix}", raising=False)
        monkeypatch.delenv(f"ROOTCAUSE_{suffix}", raising=False)


def test_config_validation_fails_closed() -> None:
    with pytest.raises(Misconfigured, match=r"Secret is required \(REPLYPEN_ACTION_SECRET\)"):
        Config(fetch_url=FETCH)
    with pytest.raises(Misconfigured, match=r"placeholder.*REPLYPEN_FETCH_URL"):
        Config(secret="secret")
    with pytest.raises(Misconfigured, match="placeholder"):
        Config(secret="secret", fetch_url="https://rootcause.invalid/actions/script")
    with pytest.raises(Misconfigured, match="TotalDeadline"):
        Config(secret="secret", fetch_url=FETCH, timeout=23)
    with pytest.raises(Misconfigured, match="byte caps"):
        Config(secret="secret", fetch_url=FETCH, max_body_bytes=0)
    with pytest.raises(Misconfigured, match="APIBaseURL"):
        Config(secret="secret", fetch_url=FETCH, api_key="rcor_x")
    with pytest.raises(Misconfigured, match="ChatProject"):
        Config(secret="secret", fetch_url=FETCH, chat_secret="chat")
    with pytest.raises(Misconfigured, match="must differ"):
        Config(
            secret="secret",
            fetch_url=FETCH,
            chat_secret="secret",
            chat_project="demo",
        )


def test_config_env_fallback_and_explicit_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROOTCAUSE_ACTION_SECRET", "from-env")
    monkeypatch.setenv("ROOTCAUSE_FETCH_URL", FETCH)
    monkeypatch.setenv("ROOTCAUSE_TRIGGER_URL", "https://app.replypen.com/analyses/demo")
    config = Config()
    assert config.secret == "from-env"
    assert config.trigger_url.endswith("/analyses/demo")
    assert Config(secret="explicit").secret == "explicit"


@pytest.mark.parametrize("suffix", ENV_SUFFIXES)
def test_replypen_env_wins_over_legacy_rootcause_env(
    monkeypatch: pytest.MonkeyPatch, suffix: str
) -> None:
    def value(kind: str) -> str:
        return f"https://{kind}.example/x" if suffix.endswith("URL") else f"{kind}-{suffix}"

    for base, val in (
        ("ACTION_SECRET", "action-secret"),
        ("FETCH_URL", FETCH),
        ("API_BASE_URL", "https://app.replypen.com"),
        ("API_KEY", "key"),
        ("CHAT_SECRET", "chat-secret"),
        ("CHAT_PROJECT", "demo"),
    ):
        monkeypatch.setenv(f"REPLYPEN_{base}", val)
    field = suffix.lower().removeprefix("action_")
    monkeypatch.setenv(f"REPLYPEN_{suffix}", value("new"))
    monkeypatch.setenv(f"ROOTCAUSE_{suffix}", value("legacy"))
    assert getattr(Config(), field) == value("new")
    monkeypatch.setenv(f"REPLYPEN_{suffix}", "")
    assert getattr(Config(), field) == value("legacy")


def test_reverse_secret_map_is_exclusive_and_validated() -> None:
    project_id = "11111111-1111-1111-1111-111111111111"
    with pytest.raises(Misconfigured, match="exactly one"):
        Config(secret="secret", secrets={project_id: "other"}, fetch_url=FETCH)
    with pytest.raises(Misconfigured, match="non-empty"):
        Config(secrets={}, fetch_url=FETCH)
    with pytest.raises(Misconfigured, match="project UUID"):
        Config(secrets={"not-a-project": "secret"}, fetch_url=FETCH)
    with pytest.raises(Misconfigured, match="non-blank"):
        Config(secrets={project_id: "  "}, fetch_url=FETCH)
    config = Config(secrets={project_id.upper(): "secret"}, fetch_url=FETCH)
    assert config.map_mode
    assert config.secret_for_project(project_id) == "secret"
    assert config.secret_for_project("22222222-2222-2222-2222-222222222222") is None


def test_chat_secret_cannot_equal_any_reverse_secret_in_map() -> None:
    with pytest.raises(Misconfigured, match="must differ"):
        Config(
            secrets={"11111111-1111-1111-1111-111111111111": "map-secret"},
            fetch_url=FETCH,
            chat_secret="map-secret",
            chat_project="demo",
        )
