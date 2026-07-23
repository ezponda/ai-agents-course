# Setup: Install and Run n8n

This chapter walks you through installing and running n8n.

**Three options (choose one):**
1. **Command Line** (recommended) — install once with npm, then launch anytime by typing `n8n`
2. **Docker** — for containerized environments
3. **n8n Cloud** — no installation, runs in browser

---

## Option 1: Command Line (Recommended)

Install n8n once with npm, then launch it from anywhere by typing `n8n`. Works the same way on Mac and Windows.

### Step 1: Install Node.js

n8n runs on **Node.js**, a program that lets your computer run JavaScript applications. You need version **20.19 (LTS) or newer** — n8n no longer supports Node 18.

First, check if you already have it. Open your terminal:

- **Mac:** open **Terminal** (Cmd + Space, type "Terminal", Enter)
- **Windows:** open **PowerShell** (Windows key, type "PowerShell", Enter)

Then run:

```bash
node --version
```

If you see `v20.19.0` or higher, skip to Step 2. Otherwise, install Node.js using the instructions for your operating system below.

#### Install on Mac

You have two options. **Option A (Homebrew)** is recommended if you plan to install more developer tools later; **Option B (installer)** is simpler if this is your first time.

**Option A — Homebrew (recommended for developers):**

[Homebrew](https://brew.sh/) is a free package manager for Mac — think of it as an "app store" for command-line tools. It lets you install and update programs like Node.js, Git, Python, etc. with a single command.

1. Install Homebrew by pasting this into Terminal and pressing Enter (it will ask for your Mac password):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   When it finishes, follow any "Next steps" instructions it prints (usually two commands to add Homebrew to your PATH).
2. Install Node.js:
   ```bash
   brew install node
   ```

**Option B — Official installer (easiest, no extra tools):**

1. Go to [nodejs.org](https://nodejs.org/).
2. Click the big **LTS** download button (it auto-detects macOS).
3. Open the downloaded `.pkg` file and follow the installer. Accept all defaults.
4. Close and reopen Terminal.

Verify it worked:
```bash
node --version
```

You should see `v20.x.x` (or `v22.x.x` / `v24.x.x` — all LTS lines work).

#### Install on Windows

Windows doesn't have Homebrew. Use the official installer — it's the standard way.

1. Go to [nodejs.org](https://nodejs.org/).
2. Click the big **LTS** download button (it auto-detects Windows).
3. Open the downloaded `.msi` file to start the installer.
4. Click **Next** through each screen and **accept all defaults**. In particular:
   - Leave **"Add to PATH"** checked (it's on by default) — this is what makes `node` and `npm` available from PowerShell.
   - You do **not** need to check "Automatically install the necessary tools" (that box is for native C++ builds; n8n doesn't need it).
5. Click **Install** and wait for it to finish.
6. **Close and reopen PowerShell** (this is important — PowerShell only picks up the new `node` command in a fresh window).

Verify it worked:
```powershell
node --version
```

You should see `v20.x.x` (or `v22.x.x` / `v24.x.x` — all LTS lines work).

> **Alternative for Windows:** if you prefer a package manager similar to Homebrew, Windows has [**winget**](https://learn.microsoft.com/en-us/windows/package-manager/winget/) built in. Run `winget install OpenJS.NodeJS.LTS` in PowerShell and it installs Node.js for you. Close and reopen PowerShell afterwards.

### Step 2: Install n8n

In your terminal (Terminal on Mac, PowerShell on Windows), run:

```bash
npm install -g n8n
```

- `npm` is the **Node Package Manager** — it comes bundled with Node.js.
- `-g` means "install globally" so you can run `n8n` from any folder.

The first install takes 1–3 minutes and downloads a lot of packages. This is normal. You only need to do this once.

### Step 3: Launch n8n

From now on, whenever you want to use n8n, open a terminal and type:

```bash
n8n
```

Press **Enter**. After a few seconds you'll see a message like:

```
Editor is now accessible via:
http://localhost:5678
```

Open that URL in your browser (Chrome, Firefox, Safari, Edge — any modern browser works).

To **stop** n8n, go back to the terminal and press `Ctrl + C`. To **launch it again later**, open a terminal and type `n8n` once more. Keep the terminal window open while you're using n8n — closing it stops the app.

### Step 4: Create Account

On first launch, n8n asks you to create a local account (email + password). This is stored on your machine only; it's not sent anywhere.

You're ready to build!

**Official guide:** [docs.n8n.io/hosting/installation/npm](https://docs.n8n.io/hosting/installation/npm/)

---

## Option 2: Docker

For containerized environments.

### Step 1: Install Docker

Download Docker Desktop: [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)

### Step 2: Run n8n

Open your terminal and run:

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

### Step 3: Open n8n

Go to: **http://localhost:5678**

**Official guide:** [docs.n8n.io/hosting/installation/docker](https://docs.n8n.io/hosting/installation/docker/)

---

## Option 3: n8n Cloud

If you don't want to install anything, use n8n Cloud. It runs entirely in your browser.

1. Go to **[n8n.io/cloud](https://n8n.io/cloud/)**
2. Sign up for a free trial
3. Start building immediately

**Note:** The free trial has execution limits. For unlimited testing while learning, use the Command Line or Docker options.

**Official guide:** [docs.n8n.io/hosting](https://docs.n8n.io/hosting/)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `n8n` command not found | Ensure Node.js 20.19+ (LTS) is installed (`node --version`) and reinstall n8n with `npm install -g n8n`. On Windows, close and reopen PowerShell after installing Node.js. |
| `npm install -g n8n` fails with permission error | On Mac/Linux, avoid using `sudo`. Instead, use a Node.js version manager like `nvm` so global installs don't need admin rights. |
| `unsupported engine` warning during install | You're on an older Node. Upgrade to Node 20 LTS or newer (n8n no longer supports Node 18). |
| Port 5678 already in use | Close other apps using that port, or restart n8n. On Docker, map a different port: `-p 8080:5678`. |
| Docker command not found | Make sure Docker Desktop is installed and running |
| Cannot connect to localhost:5678 | Wait a few seconds after starting n8n; check the terminal for errors |

### Docker-Specific Issues

| Issue | Solution |
|-------|----------|
| `Cannot connect to the Docker daemon` | Docker Desktop must be **running** (not just installed). Open Docker Desktop and wait until the engine is ready (green icon in taskbar). |
| Container exits immediately | Use `-it` flags (interactive + TTY). Without them, the container may stop right away: `docker run -it --rm ...` |
| Data lost after restarting the container | You must include the volume flag `-v n8n_data:/home/node/.n8n`. Without it, all workflows and credentials are lost when the container stops. |
| Workflows can't reach OpenRouter / SerpAPI | **DNS issue inside the container.** Try restarting Docker Desktop. On Linux, you may need `--network host` instead of `-p 5678:5678`. On Mac/Windows, Docker's default networking usually works. |
| `bind: address already in use` (port 5678) | Another container or app is using port 5678. Stop it with `docker stop n8n` or use a different port: `-p 8080:5678` (then open `localhost:8080`). |
| Permission denied on volume (Linux) | Add `--user $(id -u):$(id -g)` to the `docker run` command, or fix the volume permissions: `sudo chown -R 1000:1000 /path/to/n8n_data`. |
| Can't import workflow from a local file | Files on your computer are **not visible** inside the container. Either: (1) use **Import from URL** with a GitHub raw link, or (2) mount the folder: `-v /path/to/files:/files` and import from `/files/` inside n8n. |
| n8n is slow or crashes in Docker | Increase Docker's memory limit. Go to **Docker Desktop → Settings → Resources** and set memory to at least **2 GB**. |

---

## Next Steps

Once n8n is running, proceed to the **Quick Start** chapter to build your first AI workflow from scratch!
