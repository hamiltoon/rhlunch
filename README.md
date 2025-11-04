# RHLunch

A simple command-line tool to get lunch menus from multiple Stockholm restaurants (Gourmedia, Filmhuset, Karavan).

## 🥱 Easiest way to run

Install Homebrew (you probably already have this). Run:

```bash
brew install uv
```

Then just run:

```bash
uvx --from git+https://github.com/engdahl/rhlunch lunch
```

Voila, lunch is served!

```
🍽️  Lunch Menu for Friday, October 31, 2025
==================================================

🥬 Vegetarian Options:
  • Sheperds pie vegan,svamp,sojafärs,pumpa samt persiljeyoghurt

🥩 Meat Options:
  • Tonkatsukyckling med chilibearnaise,kålsallad samt stekt sesampotatis
```

---

## 🧩 Installation

Follow these steps to set up **Python**, **pip**, and a **virtual environment** on your system.  
These instructions cover **macOS**, **Windows**, and **Linux**.

---

### 🐍 1. Check if Python is already installed

Open a terminal (or PowerShell on Windows) and run:

```bash
python --version
```

or

```bash
python3 --version
```

If the version is **3.8+**, you can skip to **step 2** or **step 3**, depending on your preferred way of running python apps.

---

### 🍎 macOS

#### Option A — Recommended (using Homebrew)

1. [Install Homebrew](https://brew.sh) if you don’t already have it:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python
   ```
3. Confirm installation:
   ```bash
   python3 --version
   pip3 --version
   ```

#### Option B — Direct download

You can also download the latest Python installer from [python.org/downloads](https://www.python.org/downloads/).

---

### 🪟 Windows

1. Go to [python.org/downloads](https://www.python.org/downloads/windows/).
2. Download the latest **Windows installer**.
3. Run the installer and **check the box** that says:
   ```
   Add Python to PATH
   ```
4. Confirm installation:
   ```powershell
   python --version
   pip --version
   ```

---

### 🐧 Linux (Debian/Ubuntu)

1. Update your package list:
   ```bash
   sudo apt update
   ```
2. Install Python and pip:
   ```bash
   sudo apt install -y python3 python3-pip
   ```
3. Confirm installation:
   ```bash
   python3 --version
   pip3 --version
   ```

_(For Fedora or Arch, use `dnf` or `pacman` accordingly.)_

---

### 🧱 2. Create a Virtual Environment

It’s good practice to isolate project dependencies in a virtual environment.

From your project root:

```bash
python3 -m venv .venv
```

Activate it:

- **macOS / Linux:**

  ```bash
  source .venv/bin/activate
  ```

- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate
  ```

When active, your prompt should look like this:

```
(.venv) $
```

To deactivate:

```bash
deactivate
```

---

### 📦 3. Clone/Install project from Github

### From GitHub

```bash
pip install git+https://github.com/engdahl/rhlunch.git
```

### From source

```bash
git clone https://github.com/engdahl/rhlunch.git
cd rhlunch
pip install -e .
```

This installs the `lunch` command globally on your system.

**Requirements:**

- Python 3.8 or higher

### 🍽️ 4. Usage

Get today's lunch menu:

```bash
lunch
```

Show only vegetarian options:

```bash
lunch -v
```

Show only meat options:

```bash
lunch -m
```

Show only fish options:

```bash
lunch -f
```

Show only a specific restaurant:

```bash
lunch -r gourmedia
lunch -r filmhuset
lunch -r karavan
```

Show the whole week menu:

```bash
lunch -w
```

Enable debug logging to troubleshoot issues:

```bash
lunch -d
```

Combine options:

```bash
lunch -r filmhuset -v    # Show only Filmhuset vegetarian options
lunch -w -m              # Show weekly menu, meat only
lunch -f -r karavan      # Show only fish from Karavan
```

## Example Output

```
  🍽️  LUNCH MENU  •  Tuesday, November 04, 2025

  📍  FILMHUSET
      ──────────────────────────────────────────────────────────────────────────

                                  🥬  Vegetarian

          Indisk vegetarisk curry med aubergine, bönor och spenat serveras med jasminris

                                     🐟  Fish

          Asiatisk fiskgryta med scampi, ingefära, lime, koriander, chili och jasminris

                                     🥩  Meat

          Coq au vin på kycklinglårfilé med rött vin, champinjoner och potatispuré

  📍  KARAVAN
      ──────────────────────────────────────────────────────────────────────────

                                  🥬  Vegetarian

          Långbakad rotselleri serveras med sojamajo och rostad potatis

                                     🐟  Fish

          Fisk ala bombay serveras basmatiris

                                     🥩  Meat

          Raggmunk med stekt fläsk och lingon
```

## 🤖 MCP Server (AI Assistant Integration)

RHLunch includes an MCP (Model Context Protocol) server that allows AI assistants like Claude to directly query lunch menus.

### What is MCP?

MCP is an open standard that enables AI assistants to securely connect to external data sources and tools. By running RHLunch as an MCP server, you can ask your AI assistant questions like "What's for lunch today?" and get live menu data.

### Setup with GitHub Copilot in VS Code

**Requirements:**
- VS Code 1.99 or later
- GitHub Copilot & Copilot Chat extensions installed
- Install `uv`: `brew install uv` (macOS) or see [uv installation docs](https://github.com/astral-sh/uv)

**Option A - Workspace Configuration (Recommended)**

Create a `.vscode/mcp.json` file in your workspace root:

```json
{
  "servers": {
    "rhlunch": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/engdahl/rhlunch.git",
        "rhlunch-mcp"
      ]
    }
  }
}
```

**Option B - Using VS Code UI**

1. Open Copilot Chat (click the chat icon in the title bar)
2. Click the tools 🔧 icon at the bottom of the chat view
3. Scroll down and click **"Add More Tools..."**
4. Add the MCP server configuration

**Restart VS Code** to load the MCP server.

Once configured, you can ask Copilot in chat mode:
- "What's for lunch today at the restaurants?"
- "Show me vegetarian options"

### Setup with Claude Code

Claude Code will automatically detect the `.mcp.json` file in this repository and load the RHLunch MCP server. No manual configuration needed!

The [.mcp.json](.mcp.json) file configures the server to run via `uvx`, which automatically handles installation:

```json
{
  "mcpServers": {
    "rhlunch": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/engdahl/rhlunch.git",
        "rhlunch-mcp"
      ]
    }
  }
}
```

### Setup with Claude Desktop

Add the following configuration to your Claude Desktop settings file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "rhlunch": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/engdahl/rhlunch.git",
        "rhlunch-mcp"
      ]
    }
  }
}
```

**Requirements:**

- Install `uv` first: `brew install uv` (macOS) or see [uv installation docs](https://github.com/astral-sh/uv)

Then **restart Claude Desktop** to load the MCP server.

### Development & Testing

Test the MCP server locally using the MCP Inspector:

```bash
# Install dependencies
pip install -e .

# Run MCP inspector
npx @modelcontextprotocol/inspector uvx --from git+https://github.com/engdahl/rhlunch.git rhlunch-mcp
```

### Available MCP Tools

Once configured, Claude can use these tools:

- **`list_restaurants()`** - Get a list of all available restaurants
- **`get_daily_menu()`** - Get today's lunch menu
  - Optional parameters: `restaurant`, `vegetarian_only`, `fish_only`, `meat_only`, `target_date`
- **`get_weekly_menu()`** - Get the weekly lunch menu
  - Optional parameters: `restaurant`, `vegetarian_only`, `fish_only`, `meat_only`

### Example Prompts for Claude

Once the MCP server is configured, you can ask Claude:

- "What's for lunch today?"
- "Show me the vegetarian options at Filmhuset"
- "What's the weekly menu at Karavan?"
- "Are there any fish dishes available today?"

## License

MIT License - see LICENSE file for details.
