from srcs.script.v2.action.helper.deleteAllMakeFiles import (
    deleteAllMakeFiles,
    getManagedMakefilePaths,
)
from srcs.script.v2.action.helper.generateMakefile import (
    generateChildMakefiles,
    generateMakefile,
    generatedParentMakefiles,
)
from srcs.script.v2.action.helper.getRelSources import (
    getMainPath,
    getOutputPath,
    getRelSources,
    getRelativePath,
    getSource,
)
from srcs.script.v2.action.helper.utils import (
    compiler_var_key,
    getCompiler,
    getProgramNameFromMakefileName,
    read_entries,
)
