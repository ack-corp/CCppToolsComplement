const vscode = require("vscode");
const { createMenu } = require("./menuAsJson");
const { deleteEntry } = require("./bridge");

const MENU_RESULT_BACK = Symbol("menuBack");
const MENU_RESULT_REFRESH = Symbol("menuRefresh");

async function pickProgram(workspaceFolder, pythonBin, pythonPathRoot) {
  const menu = await createMenu(workspaceFolder, pythonBin, pythonPathRoot);
  return runMenu(menu, null, {
    placeHolder: "Select a program",
    includeBack: false
  });
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

  return executeMenuNode(selected.node);
}

async function executeMenuNode(node) {
  if (typeof node.runner !== "function") {
    return MENU_RESULT_REFRESH;
  }

  const result = await node.runner(node.args);
  if (node.runner === deleteEntry) {
    return MENU_RESULT_BACK;
  }
  return result;
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
  pickProgram
};
