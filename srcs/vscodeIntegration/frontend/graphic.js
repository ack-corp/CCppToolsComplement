const vscode = require("vscode");
const { createMenu } = require("./menuAsJson");
const { createLaunch, deleteEntry } = require("./bridge");

const CREATE_LAUNCH_ACTION = "ccppToolsComplement.createLaunch";
const MENU_RESULT_BACK = Symbol("menuBack");
const MENU_RESULT_REFRESH = Symbol("menuRefresh");

async function pickProgram(workspaceFolder, pythonBin, pythonPathRoot) {
  const menu = await createMenu(workspaceFolder, pythonBin, pythonPathRoot);
  const selected = await pickMenuNode(menu, "Select a program");

  if (selected.runner === createLaunch) {
    return CREATE_LAUNCH_ACTION;
  }

  return menu.indexOf(selected);
}

async function handleProgramActions(workspaceFolder, entryIndex, pythonBin, pythonPathRoot) {
  while (true) {
    const menu = await createMenu(workspaceFolder, pythonBin, pythonPathRoot);
    const entryNode = menu[entryIndex];

    if (!entryNode || entryNode.runner === createLaunch) {
      throw new Error("Selected program no longer exists in makefileConfig.json.");
    }

    const result = await runMenu(entryNode.sub, {
      workspaceFolder,
      entryIndex,
      pythonBin,
      pythonPathRoot
    }, {
      placeHolder: `Select an action for ${entryNode.label}`,
      includeBack: true,
      backLabel: "Back",
      backDescription: "Return to the program list"
    });

    if (result === MENU_RESULT_BACK) {
      return null;
    }

    if (result && result !== MENU_RESULT_REFRESH) {
      return result;
    }
  }
}

async function runMenu(menuNodes, context, options) {
  const items = menuNodes.map((node) => ({
    label: node.label,
    description: node.description,
    node
  }));

  if (options.includeBack) {
    items.push({
      label: options.backLabel,
      description: options.backDescription,
      node: null
    });
  }

  const selected = await pickQuickPickItem(items, options.placeHolder);

  if (!selected.node) {
    return MENU_RESULT_BACK;
  }

  if (Array.isArray(selected.node.sub) && selected.node.sub.length > 0) {
    const childResult = await runMenu(selected.node.sub, context, {
      placeHolder: selected.node.label,
      includeBack: true,
      backLabel: "Back",
      backDescription: "Return to the previous menu"
    });
    return childResult === MENU_RESULT_BACK ? MENU_RESULT_REFRESH : childResult;
  }

  return executeMenuNode(selected.node, context);
}

async function executeMenuNode(node, context) {
  if (typeof node.runner !== "function") {
    throw new Error(`Unsupported menu action '${node.label}'.`);
  }

  const result = await node.runner(node.args);
  if (node.runner === deleteEntry) {
    return MENU_RESULT_BACK;
  }
  return result;
}

async function pickMenuNode(menuNodes, placeHolder) {
  const items = menuNodes.map((node) => ({
    label: node.label,
    description: node.description,
    node
  }));
  const selected = await pickQuickPickItem(items, placeHolder);
  return selected.node;
}

async function pickQuickPickItem(items, placeHolder) {
  const selected = await vscode.window.showQuickPick(items, {
    placeHolder
  });

  if (!selected) {
    throw new Error("Menu selection was cancelled.");
  }

  return selected;
}

module.exports = {
  CREATE_LAUNCH_ACTION,
  pickProgram,
  handleProgramActions
};
