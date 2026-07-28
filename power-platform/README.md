# Power Platform Solution Source

This is where the exported Power Automate flows and Copilot Studio agents live as version-controlled source.

```
power-platform/
├── deployment-settings.json          ← per-environment bindings (no secrets)
├── solution-source/
│   └── KMKnowledgeAutomation/        ← created by `pac solution unpack`
│       ├── Other/Solution.xml
│       ├── Workflows/                ← Power Automate flows as .json
│       └── bots/                     ← Copilot Studio agents
└── README.md
```

`solution-source/` is empty until the first export. Populate it once you've authored v1:

```bash
pac auth create --environment https://octaveint.crm4.dynamics.com

pac solution export \
  --name KMKnowledgeAutomation \
  --path out/KMKnowledgeAutomation.zip \
  --managed false

pac solution unpack \
  --zipfile out/KMKnowledgeAutomation.zip \
  --folder power-platform/solution-source/KMKnowledgeAutomation \
  --packagetype Unmanaged
```

Then commit. From that point the repo is the source of truth and `deploy-power-platform.yml` can install the whole system into any environment.

## Solution contents

| Component | Type | Purpose |
|---|---|---|
| `My Assistant` | Copilot Studio agent | Daily briefing in Teams + series retrieval Q&A |
| `KM Meeting Intelligence` | Copilot Studio agent | Series-aware meeting summarization |
| `KM \| Email → Classify & Store` | Cloud flow | Email triage + attachment routing |
| `KM \| Meeting → Series Classify` | Cloud flow | Transcript → series state round-trip |
| `KM \| Daily Brief` | Cloud flow | 8am scheduled trigger |
| `KM-Sub \| Log to Tracking Table` | Child flow | Shared logging |
| `KM-Sub \| Route to Teams Review` | Child flow | Shared low-confidence approval card |
| 9 environment variables | Config | See `deployment-settings.json` |
| 5 connection references | Config | Outlook, SharePoint, Teams, Excel, OneDrive |

## Rules

**Author inside the solution, never the default solution.** Components in the default solution can't be exported. Moving them later is possible but tedious — get this right the first time.

**Everything tenant-specific goes in an environment variable.** No hardcoded site URLs, channel IDs, or API keys inside flow definitions. This is what lets one solution serve every teammate.

**Never commit a populated `km_AnthropicApiKey`.** It stays empty in git; the value is set per-environment after import.

**Child flows must live in the same solution as their parents,** or the parent breaks on import in a new environment.
