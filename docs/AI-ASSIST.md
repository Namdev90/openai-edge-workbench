# Report assistance

## Works immediately

After installation finishes, choose **Built-in guidance** and **Get guidance**. This reads recorded outcomes and returns plain-language review points on your computer. It requires no key, account, network or model download. It is rule-based guidance, not a local language model, and applies no repair.

## Three optional public AI connections

These services are listed in [public-apis/public-apis](https://github.com/public-apis/public-apis#machine-learning). Their own documentation was checked on 10 October 2026; a directory's “free” label alone is not sufficient. Current availability, regions, account terms and limits can change.

| Service | Requested model | Free-access boundary | Official reference |
| --- | --- | --- | --- |
| Groq | `openai/gpt-oss-20b` | Free Plan account/key; 30 requests/minute, 1,000/day, 8,000 tokens/minute and 200,000/day at review time. Account limits apply. Do not upgrade the account for this flow. | [Limits](https://console.groq.com/docs/rate-limits), [models](https://console.groq.com/docs/models) |
| Google Gemini | `gemini-3.8-flash` | Free-tier project **without linked billing**; actual quotas are shown in AI Studio. Unpaid content may be used for training and human review. A paid project can charge for the same model. | [Pricing](https://ai.google.dev/gemini-api/docs/pricing), [billing](https://ai.google.dev/gemini-api/docs/billing), [terms](https://ai.google.dev/gemini-api/terms) |
| OpenRouter | `openrouter/free` | Free router selects zero-cost models. Free accounts without purchased credits currently allow 20 requests/minute and 50/day; failed attempts count. Provider availability varies. | [Free router](https://openrouter.ai/docs/guides/routing/routers/free-router), [limits](https://openrouter.ai/docs/api/reference/limits) |

## Connect through the dashboard

Open **Optional cloud AI**, choose a service, and obtain a free-tier key from that provider's account screen. Paste it into the password field and press **Connect**. The field clears; the server holds the key only while this dashboard is open. No terminal command, repository secret or configuration file is required. Account creation and free-tier eligibility are controlled by the provider.

Press **Preview summary**. Review the exact excerpt, confirm that it can be sent to the selected provider, and confirm you are using its free-tier account with billing disabled where applicable. Press **Ask AI** for one request. Changing provider/report invalidates the preview and resets consent. No automatic model request occurs during installation or guidance.

For advanced users, existing `GROQ_API_KEY`, `GEMINI_API_KEY` and `OPENROUTER_API_KEY` environment values can also be reused. Keys are never returned in metadata, saved to disk, browser storage or installation reports. Quit normally to release the session.

## What leaves the computer

The excerpt contains allowlisted operation IDs and static names, statuses/counts, recognized version strings, selected verification states, doctor warning/failure counts and migration counts. It excludes raw command output, messages, filenames, paths, credentials, configuration, project names and account identities. Simulation blocks cloud requests.

Requests use fixed HTTPS endpoints and models, with no redirect, arbitrary prompt/URL, retry, tool execution or provider fallback. Only one job runs, with a 45-second deadline, 512 KiB response limit and 2,048-token output budget. Truncated, rejected or quota-limited answers remain unavailable; they do not trigger a second call. OpenRouter requests deny data collection and fallbacks, which can reduce available providers.

Cloud responses are displayed as unverified advice, never executable actions. Workbench does not independently prove your account's billing configuration or guarantee that free-provider limits remain unchanged. Offline protocol fixtures are tested; successful authenticated inference requires your own intentional request and is separate evidence.
