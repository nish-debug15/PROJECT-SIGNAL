# SETUP.md — SIGNAL local environment

Team: Nishit Patel, Jaineesh Patel, Vanshaj Garg

## 1. Core tools (all 3 machines)

| Tool | Minimum | Check |
|------|---------|-------|
| Python | 3.10+ | `python --version` |
| Node | 18+ | `node --version` |
| Git | any | `git --version` |

## 2. Google Cloud / Gemini access

- Go to **Google AI Studio** (aistudio.google.com) → create a free API key → this is your `GEMINI_API_KEY`.
- Each team member generates their **own** key for dev.
- Use one shared key only for the final deployed demo build.

## 3. Backend setup

```bash
# From repo root
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### ADK sanity check

```bash
# Set your API key
$env:GEMINI_API_KEY="your_key_here"          # PowerShell
# or
export GEMINI_API_KEY=your_key_here           # bash

# Run the hello agent
adk run agents/hello_agent
```

Type something, get a Gemini response back. If this doesn't work, fix it before touching SIGNAL code.

## 4. Frontend setup (Vanshaj)

```bash
cd frontend
npm install
npm run dev
```

Should render a blank Bengaluru map at http://localhost:3000.

## 5. Environment variables

Copy `.env.example` to `.env` and fill in your key:
```
GEMINI_API_KEY=your_key_here
MCP_SERVER_URL=http://localhost:8000
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

## 6. Branch strategy

- `main` — protected, no direct pushes
- `feature/<block-name>` — each person works here
- PR + quick review before merge into main

## 7. GTFS data

Download Bengaluru BMTC GTFS static feed → unzip into `mcp_server/data/`.
If BMTC feed access is flaky, use any public GTFS feed for dev.

## 8. Confirm before Block 0 starts

- [ ] All 3 people can run `adk run` locally and get a response
- [ ] MCP server person has GTFS data downloaded and can load it
- [ ] Frontend person has Next.js + Leaflet rendering a blank Bengaluru map
- [ ] Repo exists, all 3 have push access, branch strategy agreed
