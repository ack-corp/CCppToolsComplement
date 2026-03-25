from pathlib import Path
from typing import Any
from models.MakefileConfigEntry.CompileProfile import CompileProfile
from models.Exeption.exceptionJsonErrorsList import JsonErrorsList, JsonValidationError


class MakefileConfigEntry:
    def __init__(self) -> None:
        self._output_makefile = ""
        self._compile_profiles: list[CompileProfile] = []
        self._link_compiler = ""
        self._link_flags = ""
        self._run_args = ""
        self._bin_name = ""
        self._rel_sources: list[str] = []
        self._obj_expr = ""

    @property
    def output_makefile(self) -> str:
        return self._output_makefile

    @property
    def compile_profiles(self) -> list[CompileProfile]:
        return self._compile_profiles

    @property
    def link_compiler(self) -> str:
        return self._link_compiler

    @property
    def link_flags(self) -> str:
        return self._link_flags

    @property
    def run_args(self) -> str:
        return self._run_args

    @property
    def bin_name(self) -> str:
        return self._bin_name

    @property
    def rel_sources(self) -> list[str]:
        return self._rel_sources

    @property
    def obj_expr(self) -> str:
        return self._obj_expr

    def __repr__(self) -> str:
        return (
            f"MakefileConfigEntry(output_makefile={self.output_makefile!r}, "
            f"compile_profiles={self.compile_profiles!r}, "
            f"link_compiler={self.link_compiler!r}, "
            f"link_flags={self.link_flags!r}, "
            f"run_args={self.run_args!r}, "
            f"bin_name={self.bin_name!r}, "
            f"rel_sources={self.rel_sources!r}, "
            f"obj_expr={self.obj_expr!r})"
        )

    def _addValidationError(self, errors: JsonErrorsList | None, message: str) -> None:
        if errors is None:
            raise JsonValidationError([message])
        errors.add(message)

    def setOutputMakefile(self, output_makefile: Any, errors: JsonErrorsList | None = None) -> None:
        if not isinstance(output_makefile, str) or not output_makefile.strip():
            self._addValidationError(errors, "Makefile config entry 'output_makefile' must be a non-empty string.")
            return
        self._output_makefile = output_makefile

    def setCompileProfiles(self, compile_profiles: Any, errors: JsonErrorsList | None = None) -> None:
        if not isinstance(compile_profiles, list):
            self._addValidationError(errors, "Makefile config entry 'compile_profiles' must be a list.")
            return

        validated_profiles: list[CompileProfile] = []
        for profile_index, profile in enumerate(compile_profiles):
            if isinstance(profile, CompileProfile):
                validated_profiles.append(profile)
                continue
            try:
                validated_profiles.append(CompileProfile.fromJsonObject(profile))
            except JsonValidationError as error:
                if errors is None:
                    raise
                errors.extend(
                    [
                        f"compile_profiles[{profile_index}]: {message}"
                        for message in error.errors
                    ]
                )

        self._compile_profiles = validated_profiles
        if errors is not None and not errors.isEmpty():
            return

        compilers = {profile.compiler for profile in self._compile_profiles if profile.compiler}
        if "g++" in compilers:
            self.setLinkCompiler("g++")
        elif "gcc" in compilers:
            self.setLinkCompiler("gcc")
        elif self._compile_profiles:
            self.setLinkCompiler(self._compile_profiles[0].compiler)
        else:
            self.setLinkCompiler("")

    def setLinkCompiler(self, link_compiler: Any, errors: JsonErrorsList | None = None) -> None:
        if not isinstance(link_compiler, str) or not link_compiler.strip():
            self._addValidationError(errors, "Makefile config entry 'link_compiler' must be a non-empty string.")
            return
        self._link_compiler = link_compiler

    def setLinkFlags(self, link_flags: Any, errors: JsonErrorsList | None = None) -> None:
        if not isinstance(link_flags, str):
            self._addValidationError(errors, "Makefile config entry 'link_flags' must be a string.")
            return
        self._link_flags = link_flags

    def setRunArgs(self, run_args: Any, errors: JsonErrorsList | None = None) -> None:
        if not isinstance(run_args, str):
            self._addValidationError(errors, "Makefile config entry 'run_args' must be a string.")
            return
        self._run_args = run_args

    def setBinName(self, bin_name: Any, errors: JsonErrorsList | None = None) -> None:
        if not isinstance(bin_name, str) or not bin_name.strip():
            self._addValidationError(errors, "Makefile config entry 'bin_name' must be a non-empty string.")
            return
        self._bin_name = bin_name

    def setRelSources(
        self,
        rel_sources: Any,
        errors: JsonErrorsList | None = None,
        rebuild_derived_fields: bool = True,
    ) -> None:
        if not isinstance(rel_sources, list):
            self._addValidationError(errors, "Makefile config entry 'rel_sources' must be a list of strings.")
            return

        validated_rel_sources: list[str] = []
        for rel_source_index, rel_source in enumerate(rel_sources):
            if not isinstance(rel_source, str) or not rel_source.strip():
                self._addValidationError(errors, f"rel_sources[{rel_source_index}] must be a non-empty string.")
                continue
            validated_rel_sources.append(rel_source)

        self._rel_sources = validated_rel_sources
        if rebuild_derived_fields and (errors is None or errors.isEmpty()):
            self.setCompileProfiles(self._buildCompileProfilesFromRelSources())
            self.setObjExpr(self._buildObjExprFromRelSources())

    def setObjExpr(self, obj_expr: Any, errors: JsonErrorsList | None = None) -> None:
        if not isinstance(obj_expr, str) or not obj_expr.strip():
            self._addValidationError(errors, "Makefile config entry 'obj_expr' must be a non-empty string.")
            return
        self._obj_expr = obj_expr

    def _getFlagsByCompiler(self) -> dict[str, str]:
        return {profile.compiler: profile.flags for profile in self._compile_profiles if profile.compiler}

    def _getCompilersByExt(self) -> dict[str, str]:
        compilers_by_ext: dict[str, str] = {}
        for source in self._rel_sources:
            ext = Path(source).suffix
            if not ext or ext in compilers_by_ext:
                continue
            compilers_by_ext[ext] = self._getCompiler(ext)
        return compilers_by_ext

    def _getCompiler(self, ext: str) -> str:
        if ext == ".c":
            return "gcc"
        if ext in {".cpp", ".cc", ".cxx"}:
            return "g++"
        raise ValueError(f"Unsupported main extension: {ext}")

    def _buildCompileProfilesFromRelSources(self) -> list[CompileProfile]:
        flags_by_compiler = self._getFlagsByCompiler()
        compilers_by_ext = self._getCompilersByExt()
        compile_profiles: list[CompileProfile] = []
        for ext, compiler in compilers_by_ext.items():
            profile = CompileProfile()
            profile.setExt(ext)
            profile.setCompiler(compiler)
            profile.setFlags(flags_by_compiler.get(compiler, ""))
            compile_profiles.append(profile)
        return compile_profiles

    def _buildObjExprFromRelSources(self) -> str:
        obj_tokens: list[str] = []
        for source in self._rel_sources:
            if "." in source:
                obj_tokens.append(source.rsplit(".", 1)[0] + ".o")
            else:
                obj_tokens.append(source + ".o")
        return " ".join(obj_tokens)

    def addCompileProfile(self, compile_profile: CompileProfile) -> None:
        self.setCompileProfiles([*self._compile_profiles, compile_profile])

    def addRelSource(self, rel_source: str) -> None:
        self.setRelSources([*self._rel_sources, rel_source])

    def toJsonObject(self) -> dict[str, Any]:
        return {
            "output_makefile": self.output_makefile,
            "compile_profiles": [
                compile_profile.toJsonObject()
                for compile_profile in self.compile_profiles
            ],
            "link_compiler": self.link_compiler,
            "link_flags": self.link_flags,
            "run_args": self.run_args,
            "bin_name": self.bin_name,
            "rel_sources": self.rel_sources,
            "obj_expr": self.obj_expr,
        }

    @classmethod
    def _getObjectFromJson(cls, data: Any, errors: JsonErrorsList) -> dict[str, Any]:
        if not isinstance(data, dict):
            errors.add("Makefile config entry must be a JSON object.")
            return {}
        return data

    @classmethod
    def fromJsonObject(cls, data: Any) -> "MakefileConfigEntry":
        errors = JsonErrorsList()
        json_object = cls._getObjectFromJson(data, errors)
        if not errors.isEmpty():
            raise JsonValidationError(errors.errors)

        entry = cls()
        entry.setOutputMakefile(json_object.get("output_makefile"), errors)
        entry.setCompileProfiles(json_object.get("compile_profiles"), errors)
        entry.setLinkCompiler(json_object.get("link_compiler"), errors)
        entry.setLinkFlags(json_object.get("link_flags"), errors)
        entry.setRunArgs(json_object.get("run_args"), errors)
        entry.setBinName(json_object.get("bin_name"), errors)
        entry.setRelSources(json_object.get("rel_sources"), errors, rebuild_derived_fields=False)
        entry.setObjExpr(json_object.get("obj_expr"), errors)
        if not errors.isEmpty():
            raise JsonValidationError(errors.errors)

        return entry
