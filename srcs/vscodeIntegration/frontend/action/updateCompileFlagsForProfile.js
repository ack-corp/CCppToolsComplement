const { updateCompileFlagsForProfileHelper } = require("../bridge");
const { getMakefileConfigJson } = require("../utilsJson");
const { promptCompileFlagsForProfile } = require("./form/promptCompileFlagsForProfile");
const { generateAllMakefiles } = require("./utils");

async function updateCompileFlagsForProfile(args) {
  const [workspaceFolder, entryIndex, profileIndex, pythonBin, pythonPathRoot] = args;
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entry = entries[entryIndex];
  const profile = entry.compile_profiles[profileIndex];
  const compiler = profile.compiler;
  const extension = profile.ext;
  const currentFlags = profile.flags;
  const values = await promptCompileFlagsForProfile(compiler, extension, currentFlags);
  if (values === undefined) {
    return false;
  }
  const newFlags = values.compileFlags;
  await updateCompileFlagsForProfileHelper([
    workspaceFolder,
    entryIndex,
    profileIndex,
    newFlags,
    pythonBin,
    pythonPathRoot
  ]);
  await generateAllMakefiles([workspaceFolder, pythonBin, pythonPathRoot]);
  return true;
}

module.exports = {
  updateCompileFlagsForProfile
};
