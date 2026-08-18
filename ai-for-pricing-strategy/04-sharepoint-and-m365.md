# Automating communications on a SharePoint page

This was one of your three named goals, and it's the one the source resource list
helps with least — that list is almost entirely about models and agents, not about
Microsoft 365 integration. So here's the actual path.

## The honest framing

**Roughly 80% of this problem is Microsoft plumbing, and 20% is AI.** The AI part —
drafting an update from source data and checking it against a rubric — is a few hours
of prompt work. The rest is authentication, permissions, and getting content onto a
page in a governed tenant. Budget accordingly, and don't be surprised when the
interesting part finishes first.

The corollary: talk to whoever administers your tenant early. Permission grants for
SharePoint write access are usually an approval conversation, not a technical
obstacle, and it's the long-lead item.

## Three ways to write to SharePoint, in order of practicality

### 1. Power Automate — start here
The lowest-friction option in a Microsoft shop, and the one your IT function is most
likely to already permit.

- Triggers on a schedule, a list item change, or an approval response.
- Has first-class SharePoint actions (create/update list items, update page content,
  post to a page's news feed).
- Has a built-in **Approvals** connector — which is exactly the human gate Blueprint 5
  needs, with no custom UI to build.
- Can call an external HTTP endpoint, so your AI drafting step can live wherever you
  like and Power Automate just orchestrates.
- If your tenant has Copilot Studio / AI Builder available, some of the drafting can
  live inside the flow itself.

**Recommended shape:** a Python script (or a small hosted function) does the data
pull, the calculator math, the LLM draft, and the rubric check — then hands the
finished draft to Power Automate, which handles approval routing and publishing.
This keeps your logic in version control and testable, and uses Power Automate only
for the parts it's genuinely good at.

### 2. Microsoft Graph API — for full control
Direct REST access to SharePoint pages, lists, and document libraries.

- More capable and scriptable than Power Automate; also more setup.
- Needs an Entra ID (Azure AD) app registration with delegated or application
  permissions such as `Sites.ReadWrite.All` — which is a broad grant that an admin
  will reasonably want to scope down. Ask for the narrowest permission that works,
  ideally restricted to specific sites.
- Page-authoring endpoints (`/sites/{id}/pages`) let you create and publish modern
  pages programmatically.
- Choose this when Power Automate's actions can't express what you need, or when you
  want the whole pipeline in one codebase.

### 3. SharePoint lists as the data layer — the underrated option
Rather than generating prose onto a page, write **structured data to a SharePoint
list** and let a page render it with out-of-the-box list web parts.

Advantages worth taking seriously:
- Far easier to write to, and far easier to correct when something's wrong.
- The data stays queryable and sortable instead of being frozen into paragraphs.
- Version history and per-item permissions come free.
- No risk of the model garbling prose on a page executives read.

For a recurring pricing-metrics or competitive-tracker update, this is very often the
better design, and it's the one people skip because "generate the page" sounds more
impressive. A list plus a short generated summary paragraph gets you most of the value
at a fraction of the risk.

## What's available in this environment right now

This session has a **Microsoft 365 connector** attached, exposing tools for:
`sharepoint_search`, `sharepoint_folder_search`, `outlook_email_search`,
`outlook_calendar_search`, `chat_message_search`, `teams_list_chats`,
`find_meeting_availability`, and resource reading.

Two things follow:

- **These are read/search tools.** They're excellent for the *gather* step — finding
  the existing page, pulling prior updates to match tone, locating source documents.
  Useful immediately, with no setup.
- **There is no write tool here.** Publishing to a page needs Power Automate or Graph,
  per the options above. Don't plan around a write capability that isn't present.

An **Aha connector** is also configured but **not authorised** in this session, so its
tools are unavailable. If roadmap data from Aha is an input to your pricing or
strategy comms, authorising it is worth doing — via claude.ai connector settings, or
`claude mcp` / `/mcp` in an interactive session. It can't be done from a
non-interactive session like this one.

## A concrete first version

Deliberately unambitious, because it's the version that actually ships:

1. **Manual trigger.** No schedule yet.
2. **Python script** pulls the source numbers, runs the calculator, drafts the update,
   and checks it against a written rubric (figures match source, required sections
   present, under the word limit, no forward-looking commitments).
3. **Writes the draft to a file** and posts it to a Teams channel — or emails it to
   yourself.
4. **You paste it into SharePoint** for the first month.

Then automate step 4 once you're confident in the output, and step 1 once you're
confident in step 4. Automating publication before you trust the content is how these
projects get shut down after one bad post.

## Security notes

- **Never put credentials in the repo.** Use environment variables or a secret store;
  in Power Automate use a connection reference, not a pasted token.
- **Request the narrowest Graph permission that works**, scoped to specific sites where
  your tenant supports it.
- **Pricing data is sensitive.** Confirm what your policy allows before sending
  discount floors, customer names, or win-loss data to any external API. This is a
  question to ask before you build, because the answer may change the architecture.
- **Log what gets published, and by which run.** When someone asks why the page says
  what it says, you want an audit trail.
