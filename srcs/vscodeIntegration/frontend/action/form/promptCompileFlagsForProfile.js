const { showFormBox } = require("../../graphic/boxes/formBox");

async function promptCompileFlagsForProfile(compiler, extension, currentFlags) {
  return showFormBox({
    panelType: "ccppToolsComplement.compileFlagsForm",
    title: "Update compile flags",
    description: `Edit the compile flags for ${compiler} ${extension}`.trim(),
    fields: [
      {
        name: "compileFlags",
        label: `${compiler} ${extension}`.trim(),
        type: "textarea",
        presetValue: currentFlags,
        regexValidator: "^[\\s\\S]*$",
        helpText: "Use the exact compile flags string stored in makefileConfig.json."
      }
    ]
  });
}

module.exports = {
  promptCompileFlagsForProfile
};
