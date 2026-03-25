from typing import Any
from models.Exeption.exceptionJsonErrorsList import JsonErrorsList, JsonValidationError


class CompileProfile:
    def __init__(self) -> None:
        self._ext = ""
        self._compiler = ""
        self._flags = ""

    @property
    def ext(self) -> str:
        return self._ext

    @property
    def compiler(self) -> str:
        return self._compiler

    @property
    def flags(self) -> str:
        return self._flags

    def __repr__(self) -> str:
        return (
            f"CompileProfile(ext={self.ext!r}, "
            f"compiler={self.compiler!r}, flags={self.flags!r})"
        )

    def _addValidationError(self, errors: JsonErrorsList | None, message: str) -> None:
        if errors is None:
            raise JsonValidationError([message])
        errors.add(message)

    def setExt(self, ext: Any, errors: JsonErrorsList | None = None) -> None:
        if not isinstance(ext, str) or not ext.strip():
            self._addValidationError(errors, "Compile profile 'ext' must be a non-empty string.")
            return
        if not ext.startswith("."):
            self._addValidationError(errors, "Compile profile 'ext' must start with '.'.")
            return
        self._ext = ext

    def setCompiler(self, compiler: Any, errors: JsonErrorsList | None = None) -> None:
        if not isinstance(compiler, str) or not compiler.strip():
            self._addValidationError(errors, "Compile profile 'compiler' must be a non-empty string.")
            return
        self._compiler = compiler

    def setFlags(self, flags: Any, errors: JsonErrorsList | None = None) -> None:
        if not isinstance(flags, str):
            self._addValidationError(errors, "Compile profile 'flags' must be a string.")
            return
        self._flags = flags

    def toJsonObject(self) -> dict[str, str]:
        return {
            "ext": self.ext,
            "compiler": self.compiler,
            "flags": self.flags,
        }

    @classmethod
    def _getObjectFromJson(cls, data: Any, errors: JsonErrorsList) -> dict[str, Any]:
        if not isinstance(data, dict):
            errors.add("Compile profile must be a JSON object.")
            return {}
        return data

    @classmethod
    def fromJsonObject(cls, data: Any) -> "CompileProfile":
        errors = JsonErrorsList()
        json_object = cls._getObjectFromJson(data, errors)
        if not errors.isEmpty():
            raise JsonValidationError(errors.errors)

        compile_profile = cls()
        compile_profile.setExt(json_object.get("ext"), errors)
        compile_profile.setCompiler(json_object.get("compiler"), errors)
        compile_profile.setFlags(json_object.get("flags"), errors)
        if not errors.isEmpty():
            raise JsonValidationError(errors.errors)

        return compile_profile
