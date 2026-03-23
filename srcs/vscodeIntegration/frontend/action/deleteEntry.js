const { deleteEntryHelper, deleteAllMakefiles } = require("../bridge");
const { generateAllMakefiles } = require("./utils");

async function deleteEntry(args) {
  const [workspaceFolder, , pythonBin, pythonPathRoot] = args;
  await deleteEntryHelper(args);
  await deleteAllMakefiles([workspaceFolder, pythonBin, pythonPathRoot]);
  await generateAllMakefiles([workspaceFolder, pythonBin, pythonPathRoot]);
}

module.exports = {
  deleteEntry
};
