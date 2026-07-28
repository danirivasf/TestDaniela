# Deploy — Getting This Running for Multiple People

The goal: build once, then let a teammate install everything by filling in a few secrets and clicking one button.

---

## Correction to earlier advice in this project

An earlier note in this project said Copilot Studio agents are UI-only and can't be created programmatically. **That was wrong.** The `pac copilot` command group is generally available, and Copilot Studio agents are stored as Dataverse `bot` records inside solutions. That means agents pack, version, export, and import through the same solution pipeline as flows.

Practical consequence: **the whole system is deployable from git.** No "build it by hand in every teammate's tenant."

Relevant commands (all GA):

| Command | Use |
|---|---|
| `pac copilot list` | List agents in an environment |
| `pac copilot create --displayName --schemaName --solution --templateFileName` | Create an agent from a template |
| `pac copilot pack --publisher-prefix` | Pack agent source into a solution component |
| `pac copilot publish --bot <id>` | Publish an agent |
| `pac copilot clone --bot <id>` | Pull an existing agent down to source |

---

## Division of labour — who can do what

Being precise here, because it determines the fastest path.

| Task | Can be automated from this repo | Notes |
|---|---|---|
| SharePoint libraries, columns, folders, views, lists | ✅ Yes | `deploy-sharepoint.yml`, or Claude via the `ms365` MCP server |
| Reading calendar / detecting recurring series / reading transcripts | ✅ Yes | Via `ms365` MCP — real `seriesMasterId` values, real transcripts to test against |
| Power Automate flows | ✅ Yes, once authored | Graph has no flow-authoring API, so **first version is built in the UI**, then exported to source and deployed everywhere after |
| Copilot Studio agents | ✅ Yes, once authored | Same pattern — author once, `pac copilot clone` to source, deploy via solution |
| Connections (Outlook/Teams/SharePoint per person) | ⚠️ Per-person | Each teammate authorizes their own. This is correct behaviour, not a limitation — nobody should inherit someone else's mailbox access |

The one-time manual step is authoring the first version of the flows and the agent. Everything after that is git.

---

## Recommended path

### Phase 0 — Provision SharePoint (30 min, once)

Two options.

**Option A — Claude via MCP (fastest, no PowerShell).** Complete the login in `MCP-SETUP.md`, then ask Claude to create the libraries, columns, folders, views, and lists per `sharepoint/document-libraries.md`, `metadata/schema.md`, and `meetings/meeting-series-model.md`. Direct Graph calls, no module install, immediate error feedback.

**Option B — GitHub Actions.** Set up the app registration below, then run the **Deploy SharePoint Structure** workflow. Better once you're deploying to more than one site.

Given the PowerShell trouble earlier in this project, **start with Option A.**

### Phase 1 — Author the flows and agent (2–4 hours, once)

In your own environment, following the guides in this repo:

1. `automation/step2-librarian-agent-flow.md` — email triage flow
2. `automation/copilot-studio-build-prompt.md` §2 — meeting intelligence flow, series-aware
3. `automation/copilot-studio-build-prompt.md` §1 — My Assistant agent

Build them **inside a solution** called `KMKnowledgeAutomation`, not in the default solution. This is the single most important choice in the whole process — components outside a solution can't be exported, and moving them later is painful.

Use **environment variables** for anything tenant-specific: `AnthropicApiKey`, `KMSiteUrl`, `ReviewChannelId`. Then a teammate changes values, not flow internals.

### Phase 2 — Export to git (15 min, once)

```bash
pac auth create --environment https://octaveint.crm4.dynamics.com
pac solution export --name KMKnowledgeAutomation --path out/KMKnowledgeAutomation.zip --managed false
pac solution unpack --zipfile out/KMKnowledgeAutomation.zip \
  --folder power-platform/solution-source/KMKnowledgeAutomation --packagetype Unmanaged
git add power-platform/ && git commit -m "Add KM solution source" && git push
```

The solution is now versioned. Diffs are reviewable, and rollback is a git revert.

Or flip `if: false` to `if: true` on the `export-back` job in `deploy-power-platform.yml` and let CI do it.

### Phase 3 — Teammate installs (10 min, per person)

1. Add three GitHub secrets (or use the org-level ones): `PP_APP_ID`, `PP_CLIENT_SECRET`, `PP_TENANT_ID`
2. Actions → **Deploy Power Platform Solution** → enter their environment URL → Run
3. In `make.powerautomate.com`, authorize their Outlook / Teams / SharePoint connections and turn the flows on
4. Set their `AnthropicApiKey` environment variable
5. Open Teams → My Assistant is there

Import as **managed** for teammates. Managed solutions can't be edited in place, which keeps everyone on the same version and makes updates clean.

---

## Required setup — one app registration

Both workflows need a service principal. Create it once.

### 1. Register the app

Entra admin center → App registrations → New registration → name `Octave KM Deploy`, single tenant.

Record the **Application (client) ID** and **Directory (tenant) ID**.

### 2. Certificate for SharePoint (PnP)

PnP needs **certificate** auth, not client secret. Client-secret auth for PnP uses legacy Azure ACS, which is SharePoint-only and being retired — any Graph-backed cmdlet (Teams, Planner, M365 Groups) fails under it.

```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 730 -nodes \
  -subj "/CN=OctaveKMDeploy"
openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem -passout pass:
base64 -w 0 cert.pfx > cert.b64
```

Upload `cert.pem` to the app registration under **Certificates & secrets → Certificates**.

API permissions → Microsoft Graph → **Application** permissions: `Sites.FullControl.All`, `User.Read.All`. Then **Grant admin consent**.

### 3. Client secret for Power Platform

Certificates & secrets → New client secret. Copy the value immediately; it's shown once.

In Power Platform admin center, add the service principal as a **System Administrator** in the target environment.

### 4. GitHub secrets

Settings → Secrets and variables → Actions:

| Secret | Value |
|---|---|
| `SP_CLIENT_ID` | Application (client) ID |
| `SP_TENANT` | `octaveint.onmicrosoft.com` |
| `SP_CERT_BASE64` | Contents of `cert.b64` |
| `SP_CERT_PASSWORD` | Blank if you used `-passout pass:` |
| `PP_APP_ID` | Same Application (client) ID |
| `PP_CLIENT_SECRET` | The client secret value |
| `PP_TENANT_ID` | Directory (tenant) ID (GUID) |

**Delete `key.pem`, `cert.pfx`, and `cert.b64` from your machine once uploaded.** Never commit them — the repo `.gitignore` blocks these extensions, but don't rely on that alone.

The Anthropic API key does **not** belong in GitHub secrets. It goes in a Power Platform environment variable, so it lives next to the flows that use it and each person can set their own.

---

## Answering the original question directly

> Can you establish MCPs with Copilot Studio, Outlook, Teams, SharePoint, OneDrive and do this purely in the cloud, or is something else needed?

**Cloud-only is achievable, with one caveat.** The `ms365` MCP server covers Outlook, Teams, SharePoint, OneDrive, Excel, To Do, and Planner through Graph — that's genuinely everything on your list, and it runs against the cloud with no local infrastructure. Copilot Studio is separately an MCP *client*, so it can consume MCP servers as tools (GA).

The caveat: **Power Automate flow authoring has no API.** Flows are the actual execution engine — the thing that runs at 8am and when email arrives. MCP can read and write your data, but it can't compose a flow. So the first build of each flow happens in the browser. After that, `pac` + GitHub Actions makes it repeatable forever.

> Can you run this from GitHub code that connects to everything and does everything, then I share it?

Yes — that's exactly the shape of `deploy-sharepoint.yml` + `deploy-power-platform.yml`. What has to exist first is the authored solution. There's no way around building v1 by hand; there's a very good way to never build v2 by hand.

**The genuinely simplest sequence:**
1. Do the MCP login (10 min) → I provision SharePoint directly, no PowerShell
2. You build the three automations in the UI once (2–4 hrs), inside a solution, using environment variables
3. `pac solution export` + `unpack` → commit (15 min)
4. Teammates: 3 secrets, 1 button, authorize connections (10 min each)

Step 2 is the real cost. Everything else is minutes.

---

## Update flow, after the first release

```
Edit flow/agent in your dev environment
        ↓
Run export-back job (or pac export + unpack locally)
        ↓
Commit + PR — the diff shows exactly what changed
        ↓
Merge
        ↓
Teammates re-run Deploy Power Platform Solution
```

Because managed imports overwrite cleanly, updates don't accumulate drift. The pattern also means the repo is the source of truth: if someone's environment breaks, reimport rather than debug.
