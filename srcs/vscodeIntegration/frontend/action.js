const vscode = require("vscode");
const { generateJson, generateMakefile, generateVscodeIntegration, deleteEntryHelper, updateRunArgsHelper, deleteAllMakefiles } = require("./bridge");
const { getMakefileConfigJson } = require("./utilsJson");
const { getProgramNameFromEntry, getLaunchConfiguration } = require("./utilsOthers");

async function createLaunch(args) {
  await generateJson(args);
  await regenerateLaunchFiles(args, true);
}

async function launchProgram(args) {
  const [workspaceFolder, entry] = args;
  const launchConfig = getLaunchConfiguration(workspaceFolder, getProgramNameFromEntry(entry));
  const started = await vscode.debug.startDebugging(workspaceFolder, launchConfig);
  if (!started) {
    throw new Error("VSCode did not start the debugger.");
  }
  return true;
}

async function deleteEntry(args) {
  await deleteEntryHelper(args);
  await deleteAllMakefiles(args);
  await generateAllMakefiles(args);
}

async function generateAllMakefiles(args) {
  await generateMakefile(args);
}

async function regenerateLaunchFiles(args, regenerateMakefiles) {
  if (regenerateMakefiles) {
    await generateMakefile(args);
  }
  await generateVscodeIntegration(args);
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function buildRunArgsWebviewHtml(initialValue) {
  const escapedValue = escapeHtml(initialValue);
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Update run arguments</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: var(--vscode-editor-background);
      --fg: var(--vscode-editor-foreground);
      --muted: var(--vscode-descriptionForeground);
      --border: var(--vscode-panel-border);
      --input-bg: var(--vscode-input-background);
      --input-fg: var(--vscode-input-foreground);
      --input-border: var(--vscode-input-border);
      --button-bg: var(--vscode-button-background);
      --button-fg: var(--vscode-button-foreground);
      --button-hover: var(--vscode-button-hoverBackground);
      --secondary-bg: var(--vscode-button-secondaryBackground);
      --secondary-fg: var(--vscode-button-secondaryForeground);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: radial-gradient(circle at top, color-mix(in srgb, var(--bg) 88%, transparent), var(--bg));
      color: var(--fg);
      font: 15px/1.5 Georgia, "Times New Roman", serif;
    }

    .shell {
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 32px;
    }

    .panel {
      width: min(720px, 100%);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 24px;
      background: color-mix(in srgb, var(--bg) 94%, black 6%);
      box-shadow: 0 22px 60px rgba(0, 0, 0, 0.28);
    }

    h1 {
      margin: 0 0 8px;
      font-size: 28px;
      line-height: 1.1;
    }

    p {
      margin: 0 0 18px;
      color: var(--muted);
    }

    textarea {
      width: 100%;
      min-height: 180px;
      resize: vertical;
      border-radius: 12px;
      border: 1px solid var(--input-border);
      background: var(--input-bg);
      color: var(--input-fg);
      padding: 14px 16px;
      font: 14px/1.5 Consolas, "Liberation Mono", monospace;
    }

    .actions {
      display: flex;
      gap: 12px;
      justify-content: flex-end;
      margin-top: 18px;
    }

    button {
      border: 0;
      border-radius: 999px;
      padding: 10px 18px;
      cursor: pointer;
      font: inherit;
    }

    .secondary {
      background: var(--secondary-bg);
      color: var(--secondary-fg);
    }

    .primary {
      background: var(--button-bg);
      color: var(--button-fg);
    }

    .primary:hover { background: var(--button-hover); }
  </style>
</head>
<body>
  <div class="shell">
    <div class="panel">
      <h1>Update run arguments</h1>
      <p>Edit the argument string passed to the generated launch configuration.</p>
      <textarea id="runArgs" spellcheck="false">${escapedValue}</textarea>
      <div class="actions">
        <button class="secondary" id="cancel" type="button">Cancel</button>
        <button class="primary" id="save" type="button">Save</button>
      </div>
    </div>
  </div>
  <script>
    const vscode = acquireVsCodeApi();
    const textarea = document.getElementById("runArgs");
    const save = document.getElementById("save");
    const cancel = document.getElementById("cancel");

    textarea.focus();
    textarea.setSelectionRange(0, textarea.value.length);

    save.addEventListener("click", () => {
      vscode.postMessage({ type: "submit", value: textarea.value });
    });

    cancel.addEventListener("click", () => {
      vscode.postMessage({ type: "cancel" });
    });

    window.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        save.click();
      }
      if (event.key === "Escape") {
        event.preventDefault();
        cancel.click();
      }
    });
  </script>
</body>
</html>`;
}

function promptTextInput(title, prompt, value = "") {
  return new Promise((resolve) => {
    const panel = vscode.window.createWebviewPanel(
      "ccppToolsComplement.inputBox",
      title,
      vscode.ViewColumn.Active,
      {
        enableScripts: true,
        retainContextWhenHidden: false
      }
    );

    let settled = false;
    const settle = (result) => {
      if (settled) {
        return;
      }
      settled = true;
      messageDisposable.dispose();
      disposeDisposable.dispose();
      panel.dispose();
      resolve(result);
    };

    panel.webview.html = buildRunArgsWebviewHtml(value);

    const messageDisposable = panel.webview.onDidReceiveMessage((message) => {
      if (!message || typeof message !== "object") {
        return;
      }
      if (message.type === "submit") {
        settle(typeof message.value === "string" ? message.value : "");
      } else if (message.type === "cancel") {
        settle(undefined);
      }
    });

    const disposeDisposable = panel.onDidDispose(() => {
      settle(undefined);
    });
  });
}

async function updateRunArgs(args) {
  const [workspaceFolder, entryIndex, pythonBin, pythonPathRoot] = args;
  if (!Number.isInteger(entryIndex) || entryIndex < 0) {
    throw new Error("Selected program index is invalid.");
  }

  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entry = entries[entryIndex];
  if (!entry) {
    throw new Error(`Entry index ${entryIndex} is out of range.`);
  }

  const currentRunArgs = typeof entry.run_args === "string" ? entry.run_args : "";
  const newArgs = await promptTextInput(
    "Update run arguments",
    "Enter the new program arguments",
    currentRunArgs
  );

  if (newArgs === undefined) {
    return false;
  }

  await updateRunArgsHelper([workspaceFolder, entryIndex, newArgs, pythonBin, pythonPathRoot]);
  await regenerateLaunchFiles([workspaceFolder, pythonBin, pythonPathRoot], true);
  return true;
}

async function updateCompileFlagsForProfile(args) {
  // TODO
}

async function updateLinkFlags(args) {
  // TODO
}

module.exports = {
  createLaunch,
  launchProgram,
  deleteEntry,
  updateRunArgs,
  updateCompileFlagsForProfile,
  updateLinkFlags
};
