from dataclasses import dataclass
from typing import Any


@dataclass
class CompileProfile:
    ext: str = ""
    compiler: str = ""
    flags: str = ""

    def setExt(self, ext: str) -> None:
        self.ext = ext

    def setCompiler(self, compiler: str) -> None:
        self.compiler = compiler

    def setFlags(self, flags: str) -> None:
        self.flags = flags

    def toJsonObject(self) -> dict[str, str]:
        return {
            "ext": self.ext,
            "compiler": self.compiler,
            "flags": self.flags,
        }

    @classmethod
    def fromJsonObject(cls, data: Any) -> "CompileProfile":
        return cls(
            ext=str(data.get("ext", "")),
            compiler=str(data.get("compiler", "")),
            flags=str(data.get("flags", "")),
        )
