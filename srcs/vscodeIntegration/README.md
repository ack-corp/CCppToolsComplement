# VSCode Extension

This folder contains the VSCode extension for the project.

## What it does

The command `CCppToolsComplement: Generate and Debug Current File`:
- runs the bundled `srcs.script.generateJson` Python module in an integrated terminal so you can answer the prompts
- runs the bundled `srcs.script.generateMakefileFromJson`
- runs the bundled `srcs.script.generateVscodeIntegrationFromJson`
- finds the generated debug configuration that matches the current C or C++ file
- starts the debugger with that generated configuration

The command is also exposed from the editor title when a `c` or `cpp` file is active.

## Package the extension

From this folder:

```bash
npm install -g @vscode/vsce
vsce package
```

This produces a `.vsix` file that can be installed in VSCode.

## Notes

- The extension depends on `ms-vscode.cpptools`.
- The default Python executable is `python3`.
- You can change it through the `ccppToolsComplement.pythonPath` setting.
- The packaged extension now includes its Python scripts under `bundled/`, so it no longer depends on sibling files outside the extension folder.
