"""Template environment and registry freshness helpers."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from templateer.errors import RegistryError
from templateer.registry import TemplateRegistry, load_registry


@dataclass(frozen=True)
class _RegistrySignature:
    """Filesystem signature used to detect registry changes."""

    mtime_ns: int
    size: int
    inode: int | None
    digest: str


class TemplateEnv:
    """Runtime environment anchored to a project root.

    The environment lazily loads ``templates/registry.json`` and reloads it when
    the file signature changes.
    """

    def __init__(self, project_root: Path, clock: Callable[[], object] | None = None) -> None:
        self.project_root = Path(project_root)
        self.templates_dir = self.project_root / "templates"
        self.output_dir = self.project_root / "output"
        self.log_dir = self.project_root / "log"
        self.clock = clock

        self._cached_registry: TemplateRegistry | None = None
        self._cached_signature: _RegistrySignature | None = None

    @property
    def registry_path(self) -> Path:
        """Path to the authoritative template registry."""

        return self.templates_dir / "registry.json"

    def _path_for_message(self, path: Path) -> str:
        """Format paths relative to project root for user-facing messages."""

        try:
            return path.relative_to(self.project_root).as_posix()
        except ValueError:
            return str(path)

    def _current_signature(self) -> _RegistrySignature:
        try:
            stat = self.registry_path.stat()
            content = self.registry_path.read_bytes()
        except FileNotFoundError as exc:
            rel_path = self._path_for_message(self.registry_path)
            raise RegistryError(
                "registry file does not exist",
                path=rel_path,
                hint="run the registry build command to create templates/registry.json",
            ) from exc

        return _RegistrySignature(
            mtime_ns=stat.st_mtime_ns,
            size=stat.st_size,
            inode=getattr(stat, "st_ino", None),
            digest=hashlib.blake2b(content, digest_size=16).hexdigest(),
        )

    def _load_registry(self) -> TemplateRegistry:
        try:
            return load_registry(self.registry_path)
        except RegistryError as exc:
            context = dict(exc.context)
            raw_path = context.get("path")
            if isinstance(raw_path, str):
                context["path"] = self._path_for_message(Path(raw_path))
            raise RegistryError(exc.message, uri=exc.uri, action=exc.action, **context) from exc

    def get_registry(self) -> TemplateRegistry:
        """Return the current registry, reloading it if the file changed."""

        signature = self._current_signature()
        if self._cached_registry is None or signature != self._cached_signature:
            self._cached_registry = self._load_registry()
            self._cached_signature = signature

        return self._cached_registry

    def get_entry(self, template_id: str):
        """Resolve a template entry by ID from the fresh registry."""

        registry = self.get_registry()
        try:
            return registry.templates[template_id]
        except KeyError as exc:
            raise RegistryError(
                "template_id not found in registry",
                template_id=template_id,
                path=self._path_for_message(self.registry_path),
            ) from exc
