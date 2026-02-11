# Greeting template

A minimal template that demonstrates variable interpolation and one optional field.

## Example input JSON

```json
{
  "name": "Ada",
  "title": "Engineer"
}
```

## Expected rendered output

```text
Hello Ada!
(Engineer)
```

If `title` is omitted, only the greeting line is rendered.
