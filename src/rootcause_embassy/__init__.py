"""Legacy import name: ``rootcause_embassy`` is an alias of ``replypen_embassy``.

Every ``rootcause_embassy[.sub]`` module object IS its ``replypen_embassy`` twin (one entry in
``sys.modules``), so classes, exceptions and module state are shared and ``isinstance``/``except``
hold across both names. New code imports ``replypen_embassy``.
"""

from __future__ import annotations

import importlib
import pkgutil
import sys

import replypen_embassy as _target
from replypen_embassy import *  # noqa: F403  (static re-export for type checkers)
from replypen_embassy import __all__ as __all__

for _info in pkgutil.iter_modules(_target.__path__):
    sys.modules[f"{__name__}.{_info.name}"] = importlib.import_module(
        f"{_target.__name__}.{_info.name}"
    )
sys.modules[__name__] = _target
