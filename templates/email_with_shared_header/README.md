# Email template with shared header

This template includes a reusable shared header partial and then renders the email body.

## Example input JSON

```json
{
  "from_name": "Templateer Bot",
  "from_email": "bot@example.com",
  "to_name": "Ada Lovelace",
  "to_email": "ada@example.com",
  "subject": "Welcome!",
  "body": "Thanks for trying Templateer. Let us know if you have any questions."
}
```

## Expected rendered output

```text
From: Templateer Bot <bot@example.com>
To: Ada Lovelace <ada@example.com>
Subject: Welcome!

Hello Ada Lovelace,

Thanks for trying Templateer. Let us know if you have any questions.

Best,
Templateer Bot
```
