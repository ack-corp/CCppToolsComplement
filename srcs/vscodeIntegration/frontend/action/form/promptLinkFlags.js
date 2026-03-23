const { showFormBox } = require("../../graphic/boxes/formBox");

async function promptLinkFlags(linkCompiler, currentLinkFlags) {
  return showFormBox({
    panelType: "ccppToolsComplement.linkFlagsForm",
    title: "Update link flags",
    description: `Edit the link flags used by ${linkCompiler}.`,
    fields: [
      {
        name: "linkFlags",
        label: "Link flags",
        type: "textarea",
        presetValue: currentLinkFlags,
        regexValidator: "^[\\s\\S]*$",
        helpText: "Use the exact linker flags string stored in makefileConfig.json."
      }
    ]
  });
}

module.exports = {
  promptLinkFlags
};
