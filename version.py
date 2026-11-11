"""
version.py — Motor y Fuente Única de Verdad (SSOT) de Versionado Semántico
==========================================================================
Implementación estricta de Semantic Versioning 2.0.0 (https://semver.org/).

Cumplimiento de las 11 Reglas de la Especificación SemVer 2.0.0:
- Regla 1 (API Pública): Declarada formalmente en `PUBLIC_API_DECLARATION`.
- Regla 2 (Formato X.Y.Z): Enteros no negativos sin ceros a la izquierda (`MAJOR.MINOR.PATCH`).
- Regla 3 (Inmutabilidad): Una vez publicada una versión, su contenido no se modifica; cualquier
  cambio posterior requiere incrementar la versión.
- Regla 4 (Fase 0.y.z): Desarrollo inicial; se incrementa `MINOR` ante nuevas capacidades o
  reestructuraciones arquitectónicas y `PATCH` ante correcciones compatibles.
- Reglas 6, 7 y 8: Incrementos deterministas de `PATCH`, `MINOR` y `MAJOR`.
- Reglas 9, 10 y 11: Soporte completo para identificadores `pre-release` (`-alpha.1`, `-rc.1`),
  `build metadata` (`+20261111.sha`) y cálculo formal de precedencia SemVer 2.0.0.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Dict, List, Optional, Tuple, Union

SEMVER_SPEC_VERSION: str = "2.0.0"
SEMVER_SPEC_URL: str = "https://semver.org/spec/v2.0.0.html"

# Expresión regular oficial de Semantic Versioning 2.0.0 (https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string)
SEMVER_2_0_0_REGEX = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

# Regla 1 de SemVer 2.0.0: Declaración explícita de la API Pública de JullBrain
PUBLIC_API_DECLARATION: Dict[str, List[str]] = {
    "package_domains": [
        "jullbrain.dpk_framework",
        "jullbrain.transforms",
        "jullbrain.granite",
        "jullbrain.security",
        "jullbrain.retrieval",
        "jullbrain.runtime",
        "jullbrain.interfaces",
    ],
    "dpk_contracts": [
        "AbstractIBMTransform",
        "TransformResult",
        "LegalHierarchyTransform",
        "MetadataFrontmatterTransform",
        "ForensicValidatorTransform",
        "GraniteGuardianTransform",
        "IBMDataPrepPipeline",
    ],
    "rest_endpoints": [
        "GET /",
        "GET /health",
        "GET /api/v1/status",
        "GET /api/v1/security/vault",
        "POST /api/v1/query",
        "POST /api/v1/upload",
        "GET /api/v1/notebooks",
        "POST /api/v1/notebooks",
        "DELETE /api/v1/notebooks/{notebook_id}",
        "POST /api/v1/pipeline/action",
    ],
    "cli_flags": [
        "--full",
        "--web",
        "--qa",
        "--post",
        "--embed",
        "--test",
        "--clean",
        "--audit",
        "--single-file",
    ],
}


@total_ordering
@dataclass(frozen=True)
class SemanticVersion:
    """
    Representación inmutable y verificable de una versión conforme a SemVer 2.0.0.
    Implementa validación gramatical (Regla 2, 9, 10), incrementos (Reglas 6-8) y
    comparación de precedencia estricta (Regla 11).
    """

    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    def __post_init__(self) -> None:
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise ValueError("Los componentes MAJOR, MINOR y PATCH deben ser enteros no negativos (SemVer Regla 2).")
        rendered = self._format_str()
        if not SEMVER_2_0_0_REGEX.match(rendered):
            raise ValueError(f"Versión inválida según la gramática BNF de SemVer 2.0.0: '{rendered}'")

    def _format_str(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            base += f"-{self.prerelease}"
        if self.build:
            base += f"+{self.build}"
        return base

    def __str__(self) -> str:
        return self._format_str()

    @property
    def tuple_xyz(self) -> Tuple[int, int, int]:
        """Retorna la tupla `(major, minor, patch)`."""
        return (self.major, self.minor, self.patch)

    @property
    def git_tag(self) -> str:
        """Retorna la etiqueta Git canónica con prefijo `v` (ej. `v0.3.0`)."""
        return f"v{self}"

    @classmethod
    def parse(cls, version_str: str) -> "SemanticVersion":
        """Analiza y valida una cadena SemVer 2.0.0 (acepta prefijo opcional `v` para tags Git)."""
        cleaned = version_str.strip()
        if cleaned.startswith(("v", "V")):
            cleaned = cleaned[1:]
        match = SEMVER_2_0_0_REGEX.match(cleaned)
        if not match:
            raise ValueError(f"La cadena '{version_str}' no cumple con Semantic Versioning 2.0.0 (https://semver.org/).")
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            prerelease=match.group("prerelease"),
            build=match.group("buildmetadata"),
        )

    @classmethod
    def is_valid(cls, version_str: str) -> bool:
        """Verifica si una cadena cumple estrictamente con la especificación SemVer 2.0.0."""
        return bool(SEMVER_2_0_0_REGEX.match(version_str.strip()))

    # ── Reglas 6, 7 y 8: Incrementos de Versión ──

    def bump_major(self) -> "SemanticVersion":
        """Regla 8: Incrementa MAJOR cuando hay cambios incompatibles en la API pública y reinicia MINOR y PATCH a 0."""
        return SemanticVersion(self.major + 1, 0, 0)

    def bump_minor(self) -> "SemanticVersion":
        """Regla 7: Incrementa MINOR cuando se añade funcionalidad compatible con versiones anteriores y reinicia PATCH a 0."""
        return SemanticVersion(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "SemanticVersion":
        """Regla 6: Incrementa PATCH cuando se introducen únicamente correcciones de errores compatibles."""
        return SemanticVersion(self.major, self.minor, self.patch + 1)

    def with_prerelease(self, prerelease: Optional[str]) -> "SemanticVersion":
        """Regla 9: Asigna o limpia el identificador de pre-lanzamiento (ej. `alpha.1`, `rc.1`)."""
        return SemanticVersion(self.major, self.minor, self.patch, prerelease=prerelease, build=self.build)

    def with_build(self, build: Optional[str]) -> "SemanticVersion":
        """Regla 10: Asigna o limpia los metadatos de compilación (ej. `20261111.sha`)."""
        return SemanticVersion(self.major, self.minor, self.patch, prerelease=self.prerelease, build=build)

    # ── Regla 11: Precedencia SemVer 2.0.0 ──

    def _precedence_key(self) -> Tuple[int, int, int, int, Tuple[Tuple[int, Union[int, str]], ...]]:
        """
        Calcula la clave de precedencia según las Reglas 10 y 11 de SemVer 2.0.0:
        - `build` metadata NO afecta la precedencia.
        - Una versión normal tiene mayor precedencia que una pre-release (`1.0.0-alpha < 1.0.0`).
        - Los identificadores numéricos tienen menor precedencia que los alfanuméricos.
        """
        if self.prerelease is None:
            return (self.major, self.minor, self.patch, 1, ())
        parts: List[Tuple[int, Union[int, str]]] = []
        for token in self.prerelease.split("."):
            if token.isdigit():
                parts.append((0, int(token)))
            else:
                parts.append((1, token))
        return (self.major, self.minor, self.patch, 0, tuple(parts))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self._precedence_key() == other._precedence_key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self._precedence_key() < other._precedence_key()


# ── Versión Activa del Sistema (Fuente Única de Verdad) ──
CURRENT_SEMVER = SemanticVersion(major=0, minor=3, patch=0)

__version__: str = str(CURRENT_SEMVER)
__version_info__: Tuple[int, int, int] = CURRENT_SEMVER.tuple_xyz
__git_tag__: str = CURRENT_SEMVER.git_tag


def get_version_metadata() -> Dict[str, object]:
    """Devuelve el descriptor completo de versión SemVer 2.0.0 para telemetría local y API REST."""
    return {
        "version": __version__,
        "version_info": list(__version_info__),
        "git_tag": __git_tag__,
        "semver_spec": SEMVER_SPEC_VERSION,
        "semver_url": SEMVER_SPEC_URL,
        "is_initial_development": CURRENT_SEMVER.major == 0,
        "public_api_domains": len(PUBLIC_API_DECLARATION["package_domains"]),
    }
