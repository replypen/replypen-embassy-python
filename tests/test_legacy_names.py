"""Installed customer code imports ``rootcause_embassy``: it must be ``replypen_embassy``."""

from __future__ import annotations

import pkgutil
import subprocess
import sys

import replypen_embassy

LEGACY_FIRST = """
import rootcause_embassy, rootcause_embassy.chat, rootcause_embassy.errors
from rootcause_embassy import Claims, Widget, mint_embed_token, widget_tag_html
from rootcause_embassy.errors import Misconfigured
import replypen_embassy, replypen_embassy.chat, replypen_embassy.errors
assert rootcause_embassy is replypen_embassy
assert rootcause_embassy.chat is replypen_embassy.chat
assert Claims is replypen_embassy.Claims and Widget is replypen_embassy.Widget
assert Misconfigured is replypen_embassy.Misconfigured
try:
    replypen_embassy.mint_embed_token("", Claims(project="p"))
except Misconfigured:
    pass
assert isinstance(replypen_embassy.Claims(), Claims)
token = mint_embed_token("s", Claims(project="p", external_id="e", kind="k", origin="https://a.b"))
tag = widget_tag_html(Widget(base_url="https://x.y", project="p", token=token))
assert tag.startswith("<script")
"""


def test_legacy_package_is_the_same_module_tree() -> None:
    import rootcause_embassy

    assert rootcause_embassy is replypen_embassy
    for info in pkgutil.iter_modules(replypen_embassy.__path__):
        legacy = sys.modules[f"rootcause_embassy.{info.name}"]
        assert legacy is sys.modules[f"replypen_embassy.{info.name}"]


def test_legacy_import_first_in_fresh_interpreter() -> None:
    subprocess.run([sys.executable, "-c", LEGACY_FIRST], check=True)
