# Greeting template

A minimal template that demonstrates variable interpolation and one optional field.

## Example input JSON objects (`examples/sample_inputs.jsonl`)

```json
{"name":"Ada"}
{"name":"Grace","title":"Rear Admiral"}
```

## Expected rendered output

For `{"name":"Ada"}`:

```text
Hello Ada!
```

For `{"name":"Grace","title":"Rear Admiral"}`:

```text
Hello Grace!
(Rear Admiral)
```

## Generation directories

- `gen/` stores timestamped outputs for `mpt generate --template-id greeting`.
- `examples/` stores `sample_inputs.jsonl` and timestamped outputs from `mpt generate-examples --template-id greeting`.
