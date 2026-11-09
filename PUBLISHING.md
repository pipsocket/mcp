# Publishing to the MCP Registry

[`server.json`](server.json) is published to the official
[MCP Registry](https://registry.modelcontextprotocol.io) under the name `com.pipsocket/mcp`. The
registry proves the right to publish under `com.pipsocket/` by a DNS record on `pipsocket.com`, so
publishing needs the signing key that matches that record. It is done by hand, not from CI, and the key
never goes into this repository.

The registry's own guides: [quickstart](https://modelcontextprotocol.io/registry/quickstart),
[authentication](https://modelcontextprotocol.io/registry/authentication) and
[remote servers](https://modelcontextprotocol.io/registry/remote-servers). The registry is in preview
and says its data may be reset.

## Every release

1. Change `server.json` and raise `version`. A version can be published only once, and a published
   version can't be changed.
2. Open a pull request. CI checks the file against the schema named in its `$schema` and with the
   registry's validator. Merge it.
3. From an up to date checkout of `main`, sign in and publish:

   ```sh
   mcp-publisher login dns --domain pipsocket.com --private-key "$PRIVATE_KEY_HEX"
   mcp-publisher publish
   ```

   `PRIVATE_KEY_HEX` is the signing key in hex (below). Set it in your shell from your password
   manager, never in a file in this repository.
4. Check the entry:

   ```sh
   curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=com.pipsocket/mcp"
   ```

Install `mcp-publisher` from the registry's
[GitHub releases](https://github.com/modelcontextprotocol/registry/releases) or with
`brew install mcp-publisher`.

## The signing key

Made once, by a person who keeps it in a password manager. Whoever holds it can publish anything under
`com.pipsocket/`. Use OpenSSL 3 (macOS's own `openssl` can't make Ed25519 keys).

```sh
openssl genpkey -algorithm Ed25519 -out key.pem
```

The DNS proof is a TXT record on the apex of `pipsocket.com` (not on a subdomain) holding the public key.
This prints it:

```sh
PUBLIC_KEY="$(openssl pkey -in key.pem -pubout -outform DER | tail -c 32 | base64)"
echo "pipsocket.com. IN TXT \"v=MCPv1; k=ed25519; p=${PUBLIC_KEY}\""
```

And this prints the private key in hex, for `mcp-publisher login`:

```sh
openssl pkey -in key.pem -noout -text | grep -A3 "priv:" | tail -n +2 | tr -d ' :\n'
```

When the key is replaced, remove the old TXT record. The registry accepts a sign-in from any key
published in a TXT record, so an old record left in place keeps the old key able to publish.
