# MCP Setup — Connecting to Microsoft 365

This repo ships a `.mcp.json` at the root. Anyone who clones the repo and opens it in Claude Code gets the same M365 connections, so the setup is reproducible without passing credentials around.

---

## What's wired up

| Server | What it gives you | Auth | Verified |
|---|---|---|---|
| `ms365` | Outlook mail, Calendar, Teams (chats, meetings, transcripts, recordings), SharePoint sites & lists, OneDrive, Excel, To Do, Planner, Contacts, Search — ~300 tools | Device code / OAuth | `@softeria/ms-365-mcp-server` v0.134.x on npm, actively maintained |
| `microsoft-learn` | Official Microsoft docs search + fetch (`microsoft_docs_search`, `microsoft_docs_fetch`, `microsoft_code_sample_search`) | None | `https://learn.microsoft.com/api/mcp`, public, free |

`--org-mode` is **required** — it's in the config already. Without it you only get personal-Microsoft-account scope, which means no Teams, no SharePoint, no shared mailboxes.

---

## One-time login

```bash
npx -y @softeria/ms-365-mcp-server --org-mode --login
```

This runs a device-code flow: it prints a code, you open the URL, sign in with your Octave account, done. Tokens cache in your OS credential store (with a file fallback), so you log in once per machine.

Verify and inspect:
```bash
npx -y @softeria/ms-365-mcp-server --org-mode --verify-login
npx -y @softeria/ms-365-mcp-server --org-mode --list-permissions
```

Then restart Claude Code. Run `/mcp` to confirm `ms365` shows as connected.

### If your tenant blocks the default app registration

Some tenants require admin consent before a third-party app can request Graph scopes. If login fails with a consent error, register your own app and point the server at it:

1. Entra admin center → App registrations → New registration
2. Name: `Octave KM MCP`, single tenant, redirect URI type **Public client/native**
3. API permissions → Microsoft Graph → **Delegated**, add: `Mail.Read`, `Mail.ReadWrite`, `Calendars.Read`, `Files.ReadWrite.All`, `Sites.ReadWrite.All`, `Chat.Read`, `ChannelMessage.Read.All`, `OnlineMeetings.Read`, `OnlineMeetingTranscript.Read.All`, `Tasks.ReadWrite`, `User.Read`
4. Grant admin consent
5. Add the app's client ID to your local environment:

```bash
export MS365_MCP_CLIENT_ID="<your-app-client-id>"
export MS365_MCP_TENANT_ID="octaveint.onmicrosoft.com"
```

Don't put the client ID in `.mcp.json` if you'd rather not commit it — the server reads it from the environment either way.

### Useful env vars

| Var | Use |
|---|---|
| `MS365_MCP_ORG_MODE` | Alternative to the `--org-mode` flag |
| `MS365_MCP_CLIENT_ID` | Your own app registration |
| `MS365_MCP_TENANT_ID` | Defaults to `common`; set to your tenant to avoid the account picker |
| `READ_ONLY` | Set to `1` while exploring, so nothing can be modified by accident |
| `ENABLED_TOOLS` | Narrow the ~300 tools to a subset (regex) |

Tool presets are also available via `--preset`: `mail`, `calendar`, `files`, `work`, `excel`, `tasks`, `teams`, `outlook`, `onedrive`, `all`. Narrowing helps — 300 tools is a lot of context.

**Start read-only.** For a first pass over your real mailbox and SharePoint:
```bash
READ_ONLY=1 npx -y @softeria/ms-365-mcp-server --org-mode
```

---

## What MCP does and doesn't get you here

Worth being precise, because it determines who does what.

**MCP gives me (Claude) the ability to:**
- Read your calendar and detect which meetings are recurring — including pulling the real `seriesMasterId` values that the series model depends on
- Read Teams meeting transcripts and test the series-aware prompt against actual transcripts
- Create SharePoint libraries, columns, folders, and list items directly — no PowerShell needed
- Read your inbox to validate the triage classification rules against real email
- Write the series overview and state files into SharePoint

**MCP does not give me the ability to:**
- Create Power Automate flows — the Graph API has no endpoint for authoring flows
- Configure a Copilot Studio agent through the UI

For those two, see `DEPLOY.md` — `pac` CLI plus GitHub Actions covers them, and it turns out Copilot Studio agents *are* programmatically deployable, which is a correction to earlier advice in this project.

---

## Security

- Never commit tokens or client secrets. `.mcp.json` here holds only a tenant name, which is not a secret.
- The token cache lives in your OS credential store, not in the repo.
- Every teammate authenticates as themselves, so the connection carries their own permissions — nobody inherits access they didn't already have.
- If a token is ever exposed: `npx -y @softeria/ms-365-mcp-server --logout`, then revoke sessions in Entra.

---

## Also relevant: Copilot Studio can consume MCP servers

Copilot Studio is a **general-availability MCP client**. In Copilot Studio: **Tools → Add a tool → Model Context Protocol**. It wraps the server as a Power Platform custom connector and auto-syncs when the server's tool list changes.

- Transport: **Streamable HTTP** (SSE is deprecated)
- Auth: none (dev only), API key, or OAuth 2.0 / Entra ID with per-user auth and Conditional Access

This matters for a later phase: you could expose the series-state logic as its own MCP server and have the Copilot Studio agent call it directly, instead of reimplementing the state round-trip inside Power Automate. Not needed for v1 — noting it because it's the cleaner long-term shape.

There is also an official Microsoft path (Agent 365 / Work IQ remote MCP endpoints for Mail, Calendar, Teams, SharePoint) but it is **preview**, requires a Microsoft 365 Copilot license, and is designed to be registered through the M365 admin center rather than dropped into a local config. Deliberately not in `.mcp.json` for that reason.
