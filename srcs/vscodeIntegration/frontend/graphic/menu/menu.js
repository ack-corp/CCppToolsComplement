const vscode = require("vscode");
const { createMenu } = require("./playMenu");
const { createGearMenu } = require("./gearMenu");
const { launchProgram } = require("../../action/launchProgram");

async function pickProgram() {
  const loadMenu = () => createMenu();
  await runMenu(loadMenu, "Select a program");
}

async function pickGearMenu() {
  const loadMenu = () => createGearMenu();
  await runMenu(loadMenu, "More options");
}

function getMenuItems(currentMenu, includeBack) {
  const items = currentMenu.menuNodes.map((node) => ({
    label: node.label,
    description: node.description,
    node
  }));
  if (includeBack) {
    items.push({
      label: "Back",
      description: "Return to the previous menu",
      node: null
    });
  }
  return items;
}

async function runMenu(loadMenu, rootPlaceHolder = "Select a program") {
  let menuStack = createMenuStack(await loadMenu(), rootPlaceHolder);
  let shouldExitMenu = false;
  while (!shouldExitMenu && menuStack.length > 0) {
    const currentMenu = getCurrentMenu(menuStack);
    const items = getMenuItems(currentMenu, canGoBack(menuStack));
    const selected = await pickQuickPickItem(items, currentMenu.placeHolder);
    if (!selected) {
      return;
    }
    if (!selected.node) {
      goBack(menuStack);
    } else if (hasSubMenu(selected.node)) {
      openSubMenu(menuStack, selected.node);
    } else {
      const actionResult = await executeMenuNode(selected.node);
      if (actionResult.refreshMenu) {
        menuStack = createMenuStack(await loadMenu(), rootPlaceHolder);
      }
      shouldExitMenu = actionResult.shouldExitMenu;
    }
  }
}

function createMenuStack(rootMenuNodes, rootPlaceHolder) {
  return [{
    menuNodes: rootMenuNodes,
    placeHolder: rootPlaceHolder
  }];
}

function getCurrentMenu(menuStack) {
  return menuStack[menuStack.length - 1];
}

function canGoBack(menuStack) {
  return menuStack.length > 1;
}

function goBack(menuStack) {
  menuStack.pop();
}

function hasSubMenu(node) {
  return Array.isArray(node.sub) && node.sub.length > 0;
}

function openSubMenu(menuStack, node) {
  menuStack.push({
    menuNodes: node.sub,
    placeHolder: node.label
  });
}

async function executeMenuNode(node) {
  if (typeof node.runner !== "function") {
    return { shouldExitMenu: false, refreshMenu: false };
  }
  await node.runner(node.args);
  return {
    shouldExitMenu: node.runner === launchProgram,
    refreshMenu: node.runner !== launchProgram
  };
}

async function pickQuickPickItem(items, placeHolder) {
  return vscode.window.showQuickPick(items, {
    placeHolder
  });
}

module.exports = {
  pickProgram,
  pickGearMenu,
  runMenu
};
