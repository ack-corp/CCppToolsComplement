const vscode = require("vscode");
const { promptSetMoreOptions } = require("./form/promptSetMoreOptions");

async function setMoreOption() {
  const values = await promptSetMoreOptions();
  if (values === undefined) {
    return false;
  }

  vscode.window.showInformationMessage("More options saved for preview.");
  return true;
}

module.exports = {
  setMoreOption
};
