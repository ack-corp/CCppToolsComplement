const vscode = require("vscode");
const globals = require("../globals");
const {
  updateJsonSourcesHelper,
  updateLinkFlagsHelper,
  updateCompileFlagsForProfileHelper
} = require("../bridge");
const { getMakefileConfigJson } = require("../utilsJson");
const { getProgramNameFromEntry, getLaunchConfiguration } = require("../utilsOthers");
const { promptFlagsForEntry } = require("./form/promptFlagsForEntry");
const { regenerateLaunchFiles } = require("./utils");

async function launchProgram(args) {
  const workspaceFolder = globals.workspaceFolder;
  const [entryIndex] = args;
  const status = await updateJsonSourcesHelper(entryIndex);
  if (status !== 0 && status !== 1) {
    throw new Error(`updateJsonSources returned unexpected exit code ${status}.`);
  }

  const entries = await getMakefileConfigJson();
  const entry = entries[entryIndex];
  if (!entry) {
    throw new Error(`Updated entry at index ${entryIndex} was not found in makefileConfig.json.`);
  }

  if (status === 1) {
    const flagsValues = await promptFlagsForEntry(entry);
    if (flagsValues === undefined) {
      return false;
    }

    await updateLinkFlagsHelper(entryIndex, flagsValues.linkFlags ?? "");

    const compileProfiles = Array.isArray(entry.compile_profiles) ? entry.compile_profiles : [];
    for (const [profileIndex] of compileProfiles.entries()) {
      await updateCompileFlagsForProfileHelper(
        entryIndex,
        profileIndex,
        flagsValues[`compileFlags_${profileIndex}`] ?? ""
      );
    }
  }

  await regenerateLaunchFiles(true);
  const launchConfig = getLaunchConfiguration(getProgramNameFromEntry(entry));
  const started = await vscode.debug.startDebugging(workspaceFolder, launchConfig);
  if (!started) {
    throw new Error("VSCode did not start the debugger.");
  }
  return true;
}

module.exports = {
  launchProgram
};
