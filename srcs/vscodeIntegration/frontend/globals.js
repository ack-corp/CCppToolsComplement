const vscode = require("vscode");
const fs = require("fs");
const path = require("path");

function getWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders;
  if (!folders || folders.length === 0) {
    throw new Error("Open the project as a VSCode workspace before using CCppToolsComplement.");
  }
  return folders[0];
}

function getExtentionAbsolutePath(extensionContext, relativePath) {
  if (!extensionContext || !extensionContext.extensionPath) {
    throw new Error("Extension install path is unavailable.");
  }
  const fullPath = path.join(extensionContext.extensionPath, relativePath);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`Bundled Python resources not found at '${fullPath}'.`);
  }
  return fullPath;
}

function setGlobals(context) {
  module.exports.workspaceFolder = getWorkspaceFolder();
  module.exports.pythonBin = vscode.workspace.getConfiguration("ccppToolsComplement").get("pythonPath", "python3");
  module.exports.pythonPathRoot = getExtentionAbsolutePath(context, "backend");
}

module.exports = {
  workspaceFolder: null,
  pythonBin: null,
  pythonPathRoot: null,
  getWorkspaceFolder,
  getExtentionAbsolutePath,
  setGlobals
};
