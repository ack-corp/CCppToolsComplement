const { updateLinkFlagsHelper } = require("../bridge");
const { getMakefileConfigJson } = require("../utilsJson");
const { promptLinkFlags } = require("./form/promptLinkFlags");
const { generateAllMakefiles } = require("./utils");

async function updateLinkFlags(args) {
  const [workspaceFolder, entryIndex, pythonBin, pythonPathRoot] = args;
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entry = entries[entryIndex];
  const currentLinkFlags = entry.link_flags;
  const linkCompiler = entry.link_compiler;
  const values = await promptLinkFlags(linkCompiler, currentLinkFlags);
  if (values === undefined) {
    return false;
  }
  const newFlags = values.linkFlags;
  await updateLinkFlagsHelper([workspaceFolder, entryIndex, newFlags, pythonBin, pythonPathRoot]);
  await generateAllMakefiles([workspaceFolder, pythonBin, pythonPathRoot]);
  return true;
}

module.exports = {
  updateLinkFlags
};
