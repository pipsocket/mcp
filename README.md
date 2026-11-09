# Pipsocket MCP server

Connect AI apps to MetaTrader 5 accounts hosted by Pipsocket. Read and trade your accounts, and set up
TradingView alert hooks, from Claude, ChatGPT, Claude Code, Cursor or any other app that speaks the Model
Context Protocol (MCP).

```text
https://mcp.pipsocket.com/mcp
```

The server is hosted by Pipsocket: there is nothing to install or run. It's a remote server (Streamable
HTTP), so it works from apps on the web as well as desktop and command line apps, and your computer can be
off. This repository holds its entry for the [MCP Registry](https://registry.modelcontextprotocol.io)
([`server.json`](server.json)) and the setup steps below.

Full documentation: [MCP server](https://docs.pipsocket.com/mcp),
[MCP tools](https://docs.pipsocket.com/mcp-tools) and
[MCP retries and errors](https://docs.pipsocket.com/mcp-errors).

## How it works

- **Sign in with OAuth, no API key.** You add the URL to your app, sign in to Pipsocket in your browser,
  and tick what the app may do in each workspace. Nothing to paste.
- **One tool, one REST call.** The trading tools are the [REST API](https://docs.pipsocket.com/api/place-an-order),
  one tool per call. A tool sends exactly one request with your arguments as they are: nothing is
  adjusted, split, retried or confirmed on the way, and Pipsocket sets no risk limits of its own.
- **The answer is the REST answer**: its status, its `Retry-After` and its body. A `2xx` never means
  filled: the body's `state` says what happened.
- **Trades are safe to retry** with an `idempotency_key`, by the same rules as the REST API's
  `Idempotency-Key`. See [MCP retries and errors](https://docs.pipsocket.com/mcp-errors).

> [!WARNING]
> Pipsocket doesn't ask you to confirm a trade. Tools that change things are marked so, and your app
> decides whether to ask you first. Accounts may be live: check your app's permission settings before
> you let it trade.

## Connect an app

You need a Pipsocket account with a confirmed email address, in at least one workspace. Then add the
server in your app. The dashboard's sign-in page opens in your browser; if you're new, sign up from
there, and you can approve once your email address is confirmed.

### Claude

On the web or in Claude Desktop:

1. Open **Customize**, then **Connectors**. Click **+ Add**, then **Add custom connector**.
2. Name it **Pipsocket**, paste `https://mcp.pipsocket.com/mcp` and click **Continue**.
3. Under **Authentication**, choose **Sign in now**. Under **OAuth client**, choose **Register
   automatically**: Claude's default, its published identity, isn't accepted yet. Leave request headers
   empty and click **Add**.
4. Sign in to Pipsocket and [approve](#approve-workspaces-and-scopes). In a chat, turn Pipsocket on
   under **+**, **Connectors**.

On Team and Enterprise plans, an owner adds the connector in organization settings, and you click
**Connect**. Claude's own guide:
[custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

### ChatGPT

On the web:

1. Open **Plugins**. Click **+**, then **Add custom MCP server**.
2. Name it **Pipsocket**. Under **Connection**, paste `https://mcp.pipsocket.com/mcp`.
3. Set authentication to **OAuth**, read the warning, click **I understand and want to continue** and
   **Create as a plugin**, then install it.
4. Sign in to Pipsocket and [approve](#approve-workspaces-and-scopes). In a new chat, type **@** and
   pick Pipsocket.

Your plan and workspace settings decide whether you can add one. On Business, an owner or admin creates
it. OpenAI's guide: [add a custom MCP server](https://developers.openai.com/api/docs/guides/custom-mcp-server).

### Claude Code

Add the server, for all your projects:

```sh
claude mcp add --transport http --scope user pipsocket https://mcp.pipsocket.com/mcp
```

Then run `/mcp` in Claude Code, pick **pipsocket** and sign in to Pipsocket in your browser. Leave out
`--scope user` to add it to the current project only.

To share it with a project's team, use `--scope project`, which writes this to `.mcp.json` in the
project's root. Each person signs in with their own Pipsocket account.

```json
{
  "mcpServers": {
    "pipsocket": {
      "type": "http",
      "url": "https://mcp.pipsocket.com/mcp"
    }
  }
}
```

Claude Code's guide: [connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp).

### Cursor

Add the server to `~/.cursor/mcp.json` (every project) or `.cursor/mcp.json` in a project:

```json
{
  "mcpServers": {
    "pipsocket": {
      "url": "https://mcp.pipsocket.com/mcp"
    }
  }
}
```

If the file already has an `mcpServers` object, add the `pipsocket` entry to it. Cursor signs in with
OAuth by itself: sign in to Pipsocket in your browser and approve. Servers can be turned on and off
under **Customize** in Cursor's sidebar. Cursor's guide: [Model Context Protocol](https://cursor.com/docs/context/mcp).

### Any other app

1. Find where your app adds a **remote MCP server** or **custom connector**, usually in its settings
   under Connectors, Integrations or MCP.
2. Paste `https://mcp.pipsocket.com/mcp`. If it asks for a transport, pick **Streamable HTTP** (or
   HTTP). If it asks about sign-in, pick **OAuth** with automatic (dynamic) registration. Add no API key
   or headers.
3. Connect, sign in to Pipsocket and approve. Then ask it to call `list_accounts`.

## Approve workspaces and scopes

The approval page shows the app's name, marked **Unverified app** (any app can register itself), and the
host its answers go to. Check that host before you allow anything.

Below it is a grid: one row per workspace you're in, one column per scope the app asked for. Tick the
workspaces it may use and what it may do in each:

| Scope | Lets the app, in that workspace | Who can allow it |
| --- | --- | --- |
| **Read** | Read accounts, positions, orders, history, prices, hooks and alerts. Build alert messages and give you dashboard links. | Owners, admins and members |
| **Trade** | Place, change and close trades on every account in the workspace, which may be live. Engage and lift the kill switch. Resend a TradingView alert. | Owners and admins |
| **Manage** | Start, stop and restart accounts. Set up TradingView hooks, which trade when alerts arrive, and their symbol mappings. | Owners and admins |

- Ticking trade or manage ticks read in that row; unticking read clears the row.
- In a workspace where you're a member, trade and manage are greyed out.
- One connection covers up to 20 workspaces. Workspaces you make later aren't added: connect again to
  add one.

Then choose **Allow**. A call the connection can't make is refused with the workspace and scope it needs:
connect again from the app and tick that box.

Every tool, the scope it needs and what it calls: [MCP tools](https://docs.pipsocket.com/mcp-tools).

## Disconnect an app

Your connections are in the dashboard, under your name at the bottom of the sidebar, in **Connected
apps**. You can stop trade or manage in a workspace, remove a workspace, or **Revoke** the app
everywhere.

Account and hook tools stop at once. Trading tools can keep working for up to 5 minutes, the life of an
access token, and that includes lifting the kill switch. Ending a connection doesn't touch what it set
up: hooks it made keep trading when alerts arrive, and trades it placed stay open. To stop trading on
an account at once, engage the [kill switch](https://docs.pipsocket.com/api/kill-switch) from the
dashboard or the API, and revoke the connection too. Details:
[connected apps and revoking](https://docs.pipsocket.com/mcp#connected-apps-and-revoking).

## What isn't available over MCP

| | Instead |
| --- | --- |
| Connecting an account, or changing its MetaTrader 5 password | `connect_account_link` gives you a link to the dashboard's connect dialog, filled in. The password never goes through the app. |
| Removing an account | The dashboard |
| Revealing a hook's URL again | The dashboard (it asks for your password), or `rotate_hook_url` for a new one |
| Settling a request whose outcome is unknown | The dashboard |
| API keys, members, invitations, workspace settings, billing, Connected apps | The dashboard: an app can't widen its own access |
| Streams | Polling: MCP is request and answer. Use the [WebSocket stream](https://docs.pipsocket.com/websocket) from your own code. |

## For app builders

Everything a standard MCP client needs is discovered from a first, unauthenticated call.

- **Protocol**: MCP `2026-07-28`, and for apps that open with `initialize`, `2025-11-25` and
  `2025-06-18`. Every request is a `POST /mcp` with its own access token; there's no session, and
  answers are JSON (no event streams). `2025-03-26` isn't served. A request with an `Origin` header is
  refused, so the server can't be called from a web page.
- **Discovery**: a call without a token answers `401` with a `WWW-Authenticate` header naming
  `https://mcp.pipsocket.com/.well-known/oauth-protected-resource/mcp` and the scopes
  `read trade manage offline_access`. The authorization server is `https://app.pipsocket.com/api/auth`.
- **Registration**: dynamic client registration. Client ID metadata documents aren't accepted yet.
- **Authorization**: authorization code with PKCE (`S256`), naming
  `resource=https://mcp.pipsocket.com/mcp`. The person picks the scopes per workspace.
- **Tokens**: access tokens live 5 minutes. Refresh tokens live 30 days and rotate on every use, with no
  grace period: a refresh token used twice ends the connection. Bearer tokens only; DPoP isn't offered.

The full list, including how to handle a failed token request:
[for app builders](https://docs.pipsocket.com/mcp#for-app-builders).

## The registry entry

[`server.json`](server.json) is the server's entry in the official MCP Registry, under the name
`com.pipsocket/mcp`. CI checks it against the schema it names and with the registry's own validator.
[PUBLISHING.md](PUBLISHING.md) has the steps to publish a new version of the entry.

## Support

Questions about your account, or the server itself: [support@pipsocket.com](mailto:support@pipsocket.com).
Problems with these setup steps or the registry entry: open an issue in this repository.

## Licence

[MIT](LICENSE)

MetaTrader is a trademark of MetaQuotes Ltd. Pipsocket is not affiliated with MetaQuotes.
