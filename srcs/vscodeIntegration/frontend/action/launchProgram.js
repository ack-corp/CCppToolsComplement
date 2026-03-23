const vscode = require("vscode");
const { getProgramNameFromEntry, getLaunchConfiguration } = require("../utilsOthers");

async function launchProgram(args) {
  const [workspaceFolder, entry] = args;
  const launchConfig = getLaunchConfiguration(workspaceFolder, getProgramNameFromEntry(entry));
  const started = await vscode.debug.startDebugging(workspaceFolder, launchConfig);
  if (!started) {
    throw new Error("VSCode did not start the debugger.");
  }
  return true;
}

module.exports = {
  launchProgram
};
