# Email template with shared header

This template includes a reusable shared header partial and then renders the email body.

## Example input JSON objects (`examples/sample_inputs.jsonl`)

```json
{"from_name":"Templateer Bot","from_email":"bot@example.com","to_name":"Ada Lovelace","to_email":"ada@example.com","subject":"Welcome!","body":"Thanks for trying Templateer."}
{"from_name":"Support Team","from_email":"support@example.com","to_name":"Grace Hopper","to_email":"grace@example.com","subject":"Follow-up","body":"We received your request and will reply shortly."}
```

## Expected rendered output shape

Each output includes:

1. Shared header (`From`, `To`, `Subject`) from `templates/_shared/header.mako`
2. Greeting line (`Hello <name>,`)
3. Body content and signature

## Generation directories

- `gen/` stores timestamped outputs for `mpt generate --template-id email_with_shared_header`.
- `examples/` stores `sample_inputs.jsonl` and timestamped outputs from `mpt generate-examples --template-id email_with_shared_header`.
