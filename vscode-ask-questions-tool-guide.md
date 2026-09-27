# How VS Code Copilot Chat Creates Interactive Dialog Boxes

## Overview

When GitHub Copilot presents you with an interactive dialog box (with selectable options and/or free-text input), it uses a **tool-based architecture** built on top of VS Code's native Quick Pick UI.

---

## How It Works

### The Chain of Execution

1. **The LLM (Copilot)** decides to call the 'ask_questions' tool and outputs a structured function call in JSON.
2. **The  VS Code Copilot Chat extension** intercepts that tool call and renders it as an interactive **Quick Pick widget** inside the chat panel.
3. **The user** sees the dialog, can select a predefined option or type free text.
4. **The user's response** is sent back to the LLM as the tool's return value, and the conversation continues.

### Tool Schema

The 'ask_questions' tool accepts:

| Parameter            | Type    | Description                                                 |
|----------------------|---------|-------------------------------------------------------------|
| 'header'             | string  | Short labe (max 12 chars), used as unique ID                |
| 'question'           | string  | Full question text displayed to the user                    |
| 'options'            | array   | Selectable choices ('label', 'description', 'recommended' ) |
| 'multiSelect'        | boolean | Allow multiple selections                                   |
| 'allowFreeformInput' | boolean | Allow the user to type custom text                          |

### Example Tool Calls (JSON)

```json
{
  "questions": [
    {
      "allowFreeformInput": true,
      "header": "Continue?",
      "options": [
        { "label": "Tell me more about VS Code extension APIs" },
        { "label": "Show me code for a custom Quick Pick dialog" },
        { "label": "I am done"
      ],
      "question": "What would you like to ask next? Type 'I am done' to finish."
    }
  ]
}
```

## Relevant VS Code APIs

| API                                       | Prpose                                          |
|-------------------------------------------|-------------------------------------------------|
| `vscode.lm.registerTool()`                | Registers a tool the LLM can call               |
| `vscode.window.createQuickPick()`         | Creates the interactive dialog with free in put |
| `vscode.window.showQuickPick()`           | Simple selection dialog                         |
| `vscode.window.showInputBox()`            | Free-text-only input                            |
| `contribures.chatTools` in `package.json` | Declares the tool schema for the LLM            |

---

## How to Manually Add This Feature (Custom Extension)

In this feature is ever removed from a future VS Code update, you can recreate it with a custom extension.

## Step 1: Scaffold a VS Code Extension

```bash
npm install -g yo generator-code
yo code
# Choose "New Extension (TypeScript)"
```

### Step 2: Register the Chat Tool in `package.json`

Add this to the `contributes` section:

```jason
{
  "contributes": {
    "chatTools": [
      {
        "name": "ask_questions",
        "description": "Present an interactive dialog to the user with options",
        "inputSchema": {
          "type": "object",
          "properties": {
            "questions": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "label": { "type": "string" },
                  "descriptions": { "type": "string" },
                  "recommend": { "type": "boolean" }
                },
                "required": ["label"]
              }
            },
            "multiSelect": { "type": "boolean", "default": false },
            "allowFreeformInput": { "type": "boolean", "default": false }
          },
          "required": ["header", "question"]
        }
      }
    ]
  }
} 

```

### Step 3: Implement the Tool in `src/extension.ts`

```typescript
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {

  // Register the ask_question tool
  const tool = vscode.lm.registerTool('ask_questions', {
    async invoke(
      options: vscode.LanguageModelToolInvocationOptions,
      token: vs.CancellationToken
    ): Promise<vscode.LanguageModelToolResults> {

      const input = options.input as {
        questions: Array<{
          header: string;
          question: string;
          options?: Array<{ label: string; description?: string; recommend?: boolean }>;
          multiSelect?: boolean
          allowFreeformInput?: boolean;
        }>;
      };

      const answers: Record<string, any> = {};

      for (const q of input.questions) {
        if (q.options && q.options.length > 0 {
          const items: vscode.QuickPickItem[] = q.options.map(o => ({
            label: o.label,
            description: o.description  || '',
            picked: o.recommend || false
          }));

          if (q.allowFreeformInput) {
            // Use createQuickPick for combined options + free-form input
            const result = await new Promise<{ selected: string[]; freeText: string | null }>((resolve) => {
              const picker = vscode.window.createQuickPick();
              picker.title = q.question;
              picker.placeholder = 'Select an option or type your answer...';
              picker.items = items;
              picker.canSelectMany = q.multiSelect || false;

              picker.onDidAccept(() => {
                const selected = picker.selectedItems.map(i => i.label)l
                const freeText = picker.value || null;
                picker.dispose();
                resolve({ selected, freeText });
              });

              picker.onDidHide(() => {
                picker.dispose();
                resolve({ selected: [], freeText: null });
              });

              token.onCancellationRequested(() => {
                picker.dispose();
                resolve({ selected: [], freeText: null });
              });jj

              picker.show();
            });

            answers[q.header] = result;

          } else if (q.multiSelect) {
            // Multi-select without free-form
            const selected = await vscode.window.showQuickPick(items, {
              title: q.question,
              placeHolder: 'Select one or more options...',
              canPickMany: true
            });
            answers[q.header] = {
              selected: selected?.map(s => s.label) || [],
              freeText: null
            };

          } else {
            // Single select
            const selected = await vscode.window.showQuickPick(items, {
              title: q.question,
              placeHolder: 'Select an options...'
            });
            answers[q.header] = {
              selected: selected ? [selected.label] : [],
              freeText: null
            };
          }
        } else {
          // No options - free text input only
          const text = await vscode.window.showInputBox({
            title: q.question,
            prompt = q.header
          });
          answers[q.header] = { selected: [], freeText: text || '' };
        }
      }

      return new vscode.LanguadeModelToolResult([
        new vscode.LanguageModelTextPart(JSON.stringify({ answers }))
      ]);
    }
  });

  context.subscriptions.push(tool);
}

export function deactivate() {}
```

### Step 4: Build and Install

```bash
# Install packaging tool
npm install -g @vscode/vsce

# pPackage the extension
vsce package

# Install the .vsix file
code --instlal-extension your-extension.-.0.0.1.vsix
```

### Step 5: Text

1. Open VS Code
2. Open Copilot Chat
3. The LLM should now be able to invoke your 'ask_questions' tool
4. You'll see interactive Quick Pick dialogs in your chat

--- ## Requirements

- **VS Code 1.96+** (for `vcode.lm.regusterTool` API)
- **GitHub Copilot Chat Extension** installed
- **Node.js 18+** for building the extension

## References

- [VS Code Language model Tool Calling Guide](https://code.visualstudio.com/api.extension-guides/language-model-tool-calling)
- [VS Code Extension API - QuickPick](https://code.visualstudio.com/api/references/vscode.api#QuickPick)
- [VS Code Chat Extensions](https://code.visualstudio.com/api/extension-guides/chat)
- [VS Code Extension Generator](https://code.visualstudio.com/api/get-started/your-first-extension)

