# Skill: JIRA Access

## Trigger
Before ANY JIRA interaction — reading tickets, searching issues, browsing
boards, or any Atlassian API call.

## Connection

JIRA is accessed via the official Atlassian MCP server (`mcp.atlassian.com`),
configured in `.mcp.json` at project root. Auth is OAuth via browser login
to the Scopely Atlassian workspace.

### Setup (if Atlassian MCP is not yet connected)

1. **Configure `.mcp.json`** at project root. The server MUST be nested under
   the `mcpServers` key:

   ```json
   {
     "mcpServers": {
       "atlassian": {
         "type": "http",
         "url": "https://mcp.atlassian.com/v1/mcp"
       }
     }
   }
   ```

2. **Restart Claude Code** so it picks up the new MCP config.

3. **Complete OAuth login.** On restart, Claude Code detects the Atlassian
   server and opens the browser for Scopely Atlassian OAuth. Log in and
   authorize.

4. **Verify.** After auth, Atlassian MCP tools should appear in the tool
   list. Use `/mcp` to check server status.

### Troubleshooting

- **Tools not appearing after restart:** Check that `.mcp.json` uses the
  `mcpServers` wrapper key, not bare server entries at root level.
- **OAuth doesn't trigger:** Restart Claude Code again.
- **Auth expired:** Restart Claude Code — it will re-trigger the OAuth flow.

## Hard Rules

1. **STRICTLY READ-ONLY.** Never create, update, delete, move, transition,
   assign, comment on, edit, link, or in any way modify any JIRA ticket,
   issue, epic, sprint, board, filter, component, version, label, field,
   workflow, or any other JIRA object. This is absolute — no exceptions,
   even if the user asks. If the user explicitly requests a mutation,
   **refuse and explain this rule.** The only permitted override is if the
   user explicitly revokes this rule in this conversation.

2. **No sharing of JIRA content.** Never share, forward, post, copy, or
   transmit any JIRA ticket content, attachments, comments, descriptions,
   or metadata to any channel, service, person, or system other than
   directly to the user in this conversation. This includes:
   - No posting JIRA content to Slack (any channel)
   - No including JIRA content in emails or messages
   - No uploading JIRA content to Drive, GCS, or any external service
   - No embedding JIRA content in shared documents or presentations
   
   **Exception:** The user may explicitly approve sharing specific JIRA
   content to a specific destination on a per-instance basis. General
   approval does not carry over — each sharing action requires its own
   explicit approval.

3. **Scopely Atlassian workspace only.** Never connect to, read from, or
   interact with any non-Scopely Atlassian instance.

4. **Permitted read operations:** Viewing tickets, searching issues,
   browsing boards/sprints, reading comments and descriptions, listing
   projects — all read-only operations are allowed for context gathering
   and analysis support.

5. **No bulk data extraction.** Do not scrape, export, or bulk-download
   JIRA data. Query what you need for the current analysis, nothing more.

6. **NEVER touch permissions.** Never change, add, remove, grant, revoke,
   or in any way alter permissions on any JIRA project, ticket, board,
   filter, or any other object. This is absolute — no exceptions.
