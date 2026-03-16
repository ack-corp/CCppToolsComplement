# Test Usage

Run commands from the project root.

## Integration test for script generation

`test/script/main.py` exercises the full script pipeline against the sample C programs in `test/cProgram`.

Run it with:

```bash
python3 test/script/main.py
```

What it does:
- removes generated artifacts from `.vscode/` and `test/cProgram/`
- updates `test/cProgram/subfolder/header.h`
- runs `srcs.script.generateJson` for both sample programs
- runs `srcs.script.generateMakefileFromJson`
- builds and executes both generated programs
- checks the runtime output for two successive passes
- runs `srcs.script.generateVscodeIntegrationFromJson`

Files used by the test:
- `test/cProgram/main1.c`
- `test/cProgram/main2.c`
- `test/cProgram/one.c`
- `test/cProgram/subfolder/two.c`
- `test/cProgram/subfolder/header.h`

The test is intended as an end-to-end validation of:
- source discovery
- JSON generation
- Makefile generation
- rebuild behavior after a header change
- VSCode task and launch generation
