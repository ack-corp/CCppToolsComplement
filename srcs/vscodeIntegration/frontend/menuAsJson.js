function prototypeLaunchProgram() { }
function prototypeUpdateRunArgs() { }
function prototypeUpdateCompileFlagsForProfile() { }
function prototypeUpdateLinkFlags() { }

const PROGRAM_ACTION_MENU = [
    {
        label: "Launch program",
        description: "Build if needed and start the debugger",
        runner: prototypeLaunchProgram,
        args: [],
        sub: []
    },
    {
        label: "Set args",
        description: "Current run arguments",
        runner: prototypeUpdateRunArgs,
        args: [],
        sub: []
    },
    {
        label: "Set compile flags",
        description: "Select the compile profile to edit",
        runner: null,
        args: [],
        sub: [
            {
                label: "Compile profile",
                description: "Current flags for this profile",
                runner: prototypeUpdateCompileFlagsForProfile,
                sub: []
            }
        ]
    },
    {
        label: "Set link flags",
        description: "Current link flags",
        runner: prototypeUpdateLinkFlags,
        args: [],
        sub: []
    }
];

const PROGRAM_ACTION = [
    {
        label: "",
        description: "",
        runner: null,
        args: [],
        sub: PROGRAM_ACTION_MENU
    }
]

module.exports = {
    PROGRAM_ACTION_MENU,
    prototypeLaunchProgram,
    prototypeUpdateRunArgs,
    prototypeUpdateCompileFlagsForProfile,
    prototypeUpdateLinkFlags
};
