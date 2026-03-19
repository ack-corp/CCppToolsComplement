/**
 * @typedef {import("../shared/prototype").CompileProfile} CompileProfile
 * @typedef {import("../shared/prototype").MakefileConfigEntry} MakefileConfigEntry
 */

const { getMakefileConfigJson } = require("./utilsJson");
const { getProgramNameFromEntry } = require("./bridge");

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

/**
 * @param {MakefileConfigEntry} makefileJsonObject
 * @returns {MenuNode[]}
 */
function createSubAction(makefileJsonObject) {
    const runArgsDescription =
        typeof makefileJsonObject.run_args === "string" && makefileJsonObject.run_args
            ? makefileJsonObject.run_args
            : "No args";
    const linkFlagsDescription =
        typeof makefileJsonObject.link_flags === "string" && makefileJsonObject.link_flags
            ? makefileJsonObject.link_flags
            : "(empty)";
    const compileProfiles = Array.isArray(makefileJsonObject.compile_profiles)
        ? makefileJsonObject.compile_profiles
        : [];

    return [
        new MenuNode(
            "Launch program",
            "Build if needed and start the debugger",
            prototypeLaunchProgram,
            [makefileJsonObject],
            []
        ),
        new MenuNode(
            "Set args",
            runArgsDescription,
            prototypeUpdateRunArgs,
            [makefileJsonObject],
            []
        ),
        new MenuNode(
            "Set compile flags",
            compileProfiles.length > 0 ? "Select the compile profile to edit" : "No compile profiles",
            null,
            [],
            compileProfiles.map((compileProfile) => new MenuNode(
                `${compileProfile.compiler} ${compileProfile.ext}`.trim(),
                typeof compileProfile.flags === "string" && compileProfile.flags ? compileProfile.flags : "(empty)",
                prototypeUpdateCompileFlagsForProfile,
                [makefileJsonObject, compileProfile],
                []
            ))
        ),
        new MenuNode(
            "Set link flags",
            linkFlagsDescription,
            prototypeUpdateLinkFlags,
            [makefileJsonObject],
            []
        ),
        new MenuNode(
            "Delete entry",
            "Remove this program entry from makefileConfig.json",
            prototypeDeleteEntry,
            [makefileJsonObject],
            []
        )
    ]
}

/**
 * @param {MakefileConfigEntry[]} makefileJsonObject
 * @returns {MenuNode[]}
 */
function createAction(makefileJsonObject) {
    const menuAction = []
    for (const entry of makefileJsonObject) {
        menuAction.push(new MenuNode(
            getProgramNameFromEntry(entry),
            "Options for: " + getProgramNameFromEntry(entry),
            null,
            [],
            createSubAction(entry)
        ))
    }
    return menuAction;
}

/**
 * @param {import("vscode").WorkspaceFolder} workspaceFolder
 * @param {string} pythonBin
 * @param {string} pythonPathRoot
 */
async function createMenu(workspaceFolder, pythonBin, pythonPathRoot) {
    /** @type {MakefileConfigEntry[]} */
    const makefileConfigJson = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
    const menu = createAction(makefileConfigJson);
    menu.push(
        new MenuNode(
            "Create new launch",
            "Add a new program entry and regenerate VS Code launch.json",
            prototypeCreateLaunch,
            [],
            []
        )
    );
    return menu;
}


/**
 * @param {MakefileConfigEntry} makefileJsonObject
 */
function prototypeLaunchProgram(makefileJsonObject) { }

/**
 * @param {MakefileConfigEntry} makefileJsonObject
 */
function prototypeUpdateRunArgs(makefileJsonObject) { }

/**
 * @param {MakefileConfigEntry} makefileJsonObject
 * @param {CompileProfile} compileProfile
 */
function prototypeUpdateCompileFlagsForProfile(makefileJsonObject, compileProfile) { }

/**
 * @param {MakefileConfigEntry} makefileJsonObject
 */
function prototypeUpdateLinkFlags(makefileJsonObject) { }

/**
 * @param {MakefileConfigEntry} makefileJsonObject
 */
function prototypeDeleteEntry(makefileJsonObject) { }

/**
 * Prototype for the top-level "Create new launch" action.
 */
function prototypeCreateLaunch() { }

module.exports = {
    MenuNode,
    createMenu,
    prototypeLaunchProgram,
    prototypeUpdateRunArgs,
    prototypeUpdateCompileFlagsForProfile,
    prototypeUpdateLinkFlags,
    prototypeDeleteEntry,
    prototypeCreateLaunch
};
