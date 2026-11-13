# OpenCode: preserve another server and add M10

OpenCode v2.3.0 uses `providers`, `package` and `settings`. Older releases can use a different schema; do not blindly apply the older `provider`/`npm` example.

Add a new provider named `m10quorum`; retain all existing providers and the existing default model:

```json
{
  "providers": {
    "m10quorum": {
      "name": "M10 Quorum",
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": {
        "baseURL": "http://SERVER_IP:9000/v1",
        "apiKey": "{file:~/.config/opencode/m10-api-key}",
        "timeout": 300000,
        "encoding": "none"
      },
      "models": {
        "quorum-fast": {
          "name": "M10 - one expert",
          "limit": {"context": 8192, "input": 6144, "output": 1024},
          "capabilities": {"tools": false, "input": ["text"], "output": ["text"]}
        },
        "quorum": {
          "name": "M10 - adaptive review",
          "limit": {"context": 8192, "input": 6144, "output": 1024},
          "capabilities": {"tools": false, "input": ["text"], "output": ["text"]}
        },
        "quorum-deep": {
          "name": "M10 - full review, slow",
          "limit": {"context": 8192, "input": 6144, "output": 1024},
          "capabilities": {"tools": false, "input": ["text"], "output": ["text"]}
        }
      }
    }
  }
}
```

Store the API key in that separate file with mode 600. Do not commit it. Select `m10quorum/quorum-fast` in `/models`, or pass `-m m10quorum/quorum-fast`.

For a client previously configured with a much larger context, use a dedicated profile with a short dialogue agent. The tested M10-only profile disables automatic compaction to avoid inheriting a compaction reserve intended for a much larger model. On the original workstation, the launcher is:

```sh
m10-opencode
m10-opencode run 'Explique une jointure SQL simplement.'
m10-opencode -m m10quorum/quorum
```

The launcher selects a separate profile for that process. Ordinary `opencode` keeps the other server/default. Review/synthesis waits for expert responses before emitting the consolidated answer; its SSE chunks are not immediate token streaming. `quorum-fast` streams from its selected runtime directly.

This is a dialogue integration. Reliable filesystem editing, tools and autonomous development through the small models have not been validated.

References: [custom providers](https://opencode.ai/docs/providers), [file-based credentials](https://opencode.ai/docs/config), [models](https://opencode.ai/docs/models/).

The tested dialogue profile is in `opencode/opencode-m10.example.json`. Its tool/skill restrictions, short system prompt and disabled automatic compaction apply only to that M10 profile. Long conversations still need to stay within the runtime context or start a new chat. Do not apply this profile globally over another server's settings.
