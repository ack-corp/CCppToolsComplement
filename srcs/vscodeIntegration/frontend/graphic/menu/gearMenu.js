const { setMoreOption } = require("../../action/setMoreOption");

class MenuNode {
  constructor(label, description, runner = null, args = [], sub = []) {
    if (runner && sub.length > 0) {
      throw new Error("A menu entry cannot define both a runner and a submenu.");
    }
    this.label = label;
    this.description = description;
    this.runner = runner;
    this.args = args;
    this.sub = sub;
  }
}

async function createGearMenu() {
  return [
    new MenuNode(
      "Set more option",
      "Configure hidden suffixes and fake camel case behavior",
      setMoreOption,
      [],
      []
    )
  ];
}

module.exports = {
  createGearMenu
};
