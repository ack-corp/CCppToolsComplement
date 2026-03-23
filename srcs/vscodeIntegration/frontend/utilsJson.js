const fs = require("fs");
const path = require("path");
const { verifyJson } = require("./bridge");
const { getPathFromWorkspace } = require("./utilsVsCode");

const CONFIG_REL_PATH = path.join(".vscode", "makefileConfig.json");

function readJsonFile(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    throw new Error(`Unable to read JSON file '${filePath}'.`);
  }
}

async function getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot) {
  const configPath = getPathFromWorkspace(CONFIG_REL_PATH);
  if (!fs.existsSync(configPath)) {
    return [];
  }
  const status = await verifyJson([workspaceFolder, pythonBin, pythonPathRoot], false);
  if (status !== 0) {
    throw new Error(`Config file '${configPath}' contain errors.`);
  }
  return readJsonFile(configPath);
}

module.exports = {
  getMakefileConfigJson,
  readJsonFile
};
