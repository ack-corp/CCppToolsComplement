const { showFormBox } = require("../../graphic/boxes/formBox");

async function promptFlagsForEntry(entry) {
  const compileProfiles = Array.isArray(entry?.compile_profiles) ? entry.compile_profiles : [];
  return showFormBox({
    panelType: "ccppToolsComplement.createLaunchFlagsForm",
    title: "Set build flags",
    description: "Provide linker flags and compile flags for each detected profile.",
    fields: [
      {
        name: "linkFlags",
        label: `Link flags (${entry.link_compiler})`,
        type: "textarea",
        presetValue: typeof entry.link_flags === "string" ? entry.link_flags : "",
        regexValidator: "^[\\s\\S]*$",
        helpText: "Exact linker flags string."
      },
      ...compileProfiles.map((profile, profileIndex) => ({
        name: `compileFlags_${profileIndex}`,
        label: `${profile.compiler} ${profile.ext}`.trim(),
        type: "textarea",
        presetValue: typeof profile.flags === "string" ? profile.flags : "",
        regexValidator: "^[\\s\\S]*$",
        helpText: "Exact compile flags string for this profile."
      }))
    ]
  });
}

module.exports = {
  promptFlagsForEntry
};
