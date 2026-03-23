const { updateRunArgsHelper } = require("../bridge");
const { getMakefileConfigJson } = require("../utilsJson");
const { promptRunArgs } = require("./form/promptRunArgs");
const { regenerateLaunchFiles } = require("./utils");

async function updateRunArgs(args) {
  const [workspaceFolder, entryIndex, pythonBin, pythonPathRoot] = args;
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entry = entries[entryIndex];
  const currentRunArgs = entry.run_args;
  const values = await promptRunArgs(currentRunArgs);
  if (values === undefined) {
    return false;
  }
  const newArgs = values.runArgs;
  await updateRunArgsHelper([workspaceFolder, entryIndex, newArgs, pythonBin, pythonPathRoot]);
  await regenerateLaunchFiles([workspaceFolder, pythonBin, pythonPathRoot], true);
  return true;
}

module.exports = {
  updateRunArgs
};
