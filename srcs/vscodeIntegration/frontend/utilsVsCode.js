const path = require("path");
const globals = require("./globals");

function getPathFromWorkspace(relativePath) {
  return path.join(globals.workspaceFolder.uri.fsPath, relativePath);
}

module.exports = {
  getPathFromWorkspace
};
