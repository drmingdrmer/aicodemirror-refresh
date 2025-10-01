# aicodemirror-refresh

Automatically manages [AiCodeMirror](https://www.aicodemirror.com/register?invitecode=Q101D2) credit resets via GitHub Actions.

[AiCodeMirror](https://www.aicodemirror.com/register?invitecode=Q101D2) 中国境内 一站式Vibe Coding:
- 支持 Claude Code Sonnet 4.5
- 支持 OpenAI Codex
- 每天免费额度 2000 积分
- 5000+ 用户
- 全网价格最低


## Setup

1. Fork this repo

2. Get your cookies from `www.aicodemirror.com`

   Use [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) extension to export cookies. Format:
   ```
   __Host-authjs.csrf-token=...;__Secure-authjs.callback-url=...;__Secure-authjs.session-token=...;acw_tc=...
   ```

3. Set the above cookie string to `AICODEMIRROR_COOKIES` secret in GitHub repo settings so workflows can access your account.

   Navigate to: `https://github.com/<your_user_name>/aicodemirror-refresh/settings/secrets/actions`

   ![](https://github.com/user-attachments/assets/e32420c6-11b5-46b8-b3a2-41b0083a1852)

## Workflows

- **Daily Refresh**: Runs at 20:00 UTC daily, resets credits
- **Hourly Status**: Runs every hour, checks status without resetting

Both workflows support manual triggering.


## Manual Usage

```bash
python aicode.py refresh  # Reset credits if available
python aicode.py status   # Check status without resetting
python aicode.py check    # Check status and log to credits_history.ndjson
```
