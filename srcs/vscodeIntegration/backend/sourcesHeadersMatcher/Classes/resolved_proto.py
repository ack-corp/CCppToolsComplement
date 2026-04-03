from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ResolvedProto:
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    macros: list[str] = field(default_factory=list)
    structs: list[str] = field(default_factory=list)
    typedefs: list[str] = field(default_factory=list)

    def get_by_type(self, proto_type: str) -> list[str]:
        if proto_type == "class":
            return self.classes
        if proto_type == "function":
            return self.functions
        if proto_type == "macro":
            return self.macros
        if proto_type == "struct":
            return self.structs
        if proto_type == "typedef":
            return self.typedefs
        raise KeyError(f"Unknown proto type '{proto_type}'.")
