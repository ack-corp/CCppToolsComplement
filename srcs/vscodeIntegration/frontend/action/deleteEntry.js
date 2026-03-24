const { deleteEntryHelper, deleteAllMakefiles } = require("../bridge");
const { generateAllMakefiles } = require("./utils");

async function deleteEntry(args) {
  const [entryIndex] = args;
  await deleteEntryHelper(entryIndex);
  await deleteAllMakefiles();
  await generateAllMakefiles();
}

module.exports = {
  deleteEntry
};
