# Skill: Slack Access

## Trigger
Before ANY Slack interaction — reading or writing messages.

## Connection

Slack is accessed via the official Slack MCP server (`mcp.slack.com/mcp`),
configured in `.mcp.json` at project root. Auth is OAuth via browser login
to the Scopely workspace.

### Setup (if Slack MCP is not yet connected)

1. **Configure `.mcp.json`** at project root. The server MUST be nested under
   the `mcpServers` key — Claude Code ignores top-level server entries:

   ```json
   {
     "mcpServers": {
       "slack": {
         "type": "http",
         "url": "https://mcp.slack.com/mcp",
         "oauth": {
           "clientId": "1601185624273.8899143856786",
           "callbackPort": 3118
         }
       }
     }
   }
   ```

2. **Restart Claude Code** so it picks up the new MCP config.

3. **Complete OAuth login.** On restart, Claude Code detects the Slack server
   and opens the browser for Scopely Slack OAuth. Log in and authorize.

4. **Verify.** After auth, Slack MCP tools (e.g., `slack_list_channels`,
   `slack_send_message`) should appear in the tool list. Use `/mcp` to
   check server status.

### Troubleshooting

- **Tools not appearing after restart:** Check that `.mcp.json` uses the
  `mcpServers` wrapper key, not bare server entries at root level.
- **OAuth doesn't trigger:** Ensure `callbackPort` (3118) is not blocked.
  Try restarting Claude Code again.
- **Auth expired:** Restart Claude Code — it will re-trigger the OAuth flow.

## Hard Rules

1. **Scopely workspace only.** Never connect to, read from, or post to any
   non-Scopely Slack workspace.

2. **Whitelisted channels only.** Only read from or write to channels on
   this list. No exceptions. No DMs, no other channels.

   ### Whitelisted Channels
   - `#tophat-mgv-ai-analyst-test`

3. **Never post without explicit instruction.** Do not send messages, replies,
   or reactions unless the user specifically asks. Reading is allowed for
   context gathering.

4. **No data exfiltration.** Never paste query results, data exports, file
   contents, credentials, or analysis outputs into Slack unless the user
   explicitly asks. Subject to Rules 19–21 in CLAUDE.md (Scopely boundaries,
   no outbound transfer, no external sharing).

5. **No file uploads unless asked.** Do not attach or upload files to Slack
   channels without explicit instruction.

6. **Adding channels.** To whitelist a new channel, the user must explicitly
   ask. Update the list above in this file when they do.
