const { runPythonModuleTask } = require("./pythonRunner");

const PYTHON_MODULE_PREFIX = "srcs.script";

async function generateJson(args) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.generateJson`,
    true
  );
}

async function verifyJson(args, throwOnError = true) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  return runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.verifyJson`,
    false,
    throwOnError
  );
}

async function generateMakefile(args) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.generateMakefile`,
    false
  );
}

async function generateVscodeIntegration(args) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.generateVscodeIntegration`,
    false
  );
}

async function deleteEntryHelper(args) {
  const [workspaceFolder, entryIndex, pythonBin, pythonPathRoot] = args;
  if (!Number.isInteger(entryIndex) || entryIndex < 0) {
    throw new Error("Selected program index is invalid.");
  }
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.deleteEntry`,
    false,
    true,
    [String(entryIndex)]
  );
}

async function updateRunArgsHelper(args) {
  const [workspaceFolder, entryIndex, newArgs, pythonBin, pythonPathRoot] = args;
  if (!Number.isInteger(entryIndex) || entryIndex < 0) {
    throw new Error("Selected program index is invalid.");
  }
  if (typeof newArgs !== "string") {
    throw new Error("New run arguments must be a string.");
  }
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.updateRunArgs`,
    false,
    true,
    [String(entryIndex), newArgs]
  );
}

async function deleteAllMakefiles(args) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.deleteAllMakeFiles`,
    false
  );
}

module.exports = {
  generateJson,
  verifyJson,
  generateMakefile,
  generateVscodeIntegration,
  deleteEntryHelper,
  updateRunArgsHelper,
  deleteAllMakefiles
};
