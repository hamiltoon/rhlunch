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
```

## Example Output

```
🍽️  Lunch Menu for Tuesday, November 04, 2025
======================================================================

📍 Gourmedia
----------------------------------------
🥬 Vegetarian:
  • Böff ala Lindström med skysås, Pepparotscreme, stekt potatis
🥩 Meat:
  • Stekt rimmad fläsk med löksås/Cowboy bönor samt kokt potatis

📍 Filmhuset
----------------------------------------
🥩 Meat:
  • Coq au vin på kycklinglårfilé L med rött vin, champinjoner, rökt sidfläsk och potatispuré
  • Asiatisk fiskgryta med scampi, ingefära, lime, koriander, chili och jasminris

📍 Karavan
----------------------------------------
🥬 Vegetarian:
  • Långbakad rotselleri serveras med sojamajo och rostad potatis toppad med friterad puriolök
🥩 Meat:
  • Raggmunk med stekt fläsk och lingon
```

## License

MIT License - see LICENSE file for details.
