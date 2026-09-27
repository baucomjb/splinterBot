# VS Code Copilot Ask Questions Dialog - Setup, Testing & Troubleshooting

## Prerequisites

- ** VS Code 1.96+**
- **Node.js 18+** (only needed if building a custom extension)
- **GitHub accont** with Copilot access

---

## Step 1: Install Required Extension

1. Open VS Code
2. Go to Extensions sidebar ('Ctrl+Shift+x')
3. Search for and install:
    - **GitHub Copilot** (publisher: GitHub)
    - **GitHub Copilot Chat** (publisher: GitHub)
4. Sign into your GitHub account when prompted

---

## Step 2: Enagle Agent Mode

The interactive dialog boxes only work in **Agent mode**, not regular Chat mode.

1. Open the Chat panel ('Ctrl+Shift+1' or click the Copilot icon in the sidebar)
2. At the top of the chat panel, look for the **mode selector dropdown**
3. Switch from "Chat" or "Edit" to **"Agent"**

> **Note:** Agent mode allows Copilot to use tools like 'ask_questions', run terminal commands, edit files, etc.

---

## Step 3: Test the Dialog Box

1. Open Copilot Chat in Agent mode
2. Type a prompt that encourages Copilot to ask clarifying questions, for example:
   ---
   Ask me what progamming language I want to use, then ask me what kind of project I want to build. Use dialog boxes.
   ---
3. You should see an interactive Quick Pick widget appear with selectable options and/or a free-text input field

---

## Step 4: Verify it's Working

### Check VS Code Version

Open a terminal and run:

'''bash
code --version
'''

Ensure the version is **1.96 or higher**.

### Check Extensions Are Installed and Enabled

Open a terminal and run:

'''bash
code --list-extensions --show-versions | grep -i copilot
'''

You should see both:

'''
GitHub.copilot@<version>
GitHub.copilot-chat@<version>
'''

### Check Inside VS Code

1. Go to Extensions sidebar ('Ctrl+Shift+X')
2. Search "GitHub Copilot Chat"
3. Confirm it shows **"Disable"** button (meaning it's currently enabled)
4. If it shows **"Enable"**, click it to enable

### Check Tools are Enabled in Settings

1. Open Settings ('Ctrl+,")
2. Search for 'chat.tools.enabled'
3. Make sure it is **checked / true**

Or check in 'settings.json' ('Ctrl+shift+P' + "Preferences: Open User Settings (JSON)"):

'''json
{
    "chat.tools.enabled": true
}
'''

---

## Troubleshooting

### Dialog Box Not Appearing

| Issue | Fix |
|------|------|
| Not in Agent mode | Switch to Agent mode in the chat panel mode selector |
| Copilot Chat not installed | Install from Extensions marketplace |
| Copilot Chat disabled | Enable it in the Extensions sidebar |
| VS Code version too old | Update VS Code to 1.96+ |
| Tools disabled in settings | Set 'chat.tools.enabled' to 'true' |

### Checking Logs for Errors

1. Press 'Ctrl+Shift+P'
2. Select **"Output: Show Output Channel"**
3. From the dropdown, select **"Github Copilot Chat"**
4. Look for error messages related to tool invocation

### Reload Window

If things look correct but still don't work:

1. Press 'Ctrl+Shift+P'
2. Select **"Developer: Reload Window"**
3. Try again after reload

### Full Reset (Last Resort)

1. Disable GitHub Copilot Chat extension
2. Disable GitHub Copilot extension
3. Restart VS Code
4. Re-enable both extensions
5. Restart VS Code again
6. Test in Agent mode

---

## Quick Reference

| Action | How |
|--------|-----|
| Open Chat | 'Ctrl+Shift+I' |
| Switch to Agent mode | Mode selector dropdown at top of chat panel |
|Open Extensions | 'Ctrl+Shift+X' |
| Reload Window | 'Ctrl+Shift+P -> "Developer: Reload Window" |
| Check VS Code version | 'code --version' in terminal |
| Check extensions | 'code --list-extensions --show-versions \| grep copilot |
| View Copilot logs | 'Ctrl+Shift+P -> "Output: Show Output Channel" -> "GitHub Copilot Chat" |
