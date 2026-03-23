const { showFormBox } = require("../../graphic/boxes/formBox");

async function promptRunArgs(currentRunArgs) {
  return showFormBox({
    panelType: "ccppToolsComplement.runArgsForm",
    title: "Update run arguments",
    description: "Edit the argument string passed to the generated launch configuration.",
    fields: [
      {
        name: "runArgs",
        label: "Run arguments",
        type: "textarea",
        presetValue: currentRunArgs,
        regexValidator: "^[\\s\\S]*$",
        helpText: "Use the exact argument string that should be forwarded to the program."
      }
    ]
  });
}

module.exports = {
  promptRunArgs
};
