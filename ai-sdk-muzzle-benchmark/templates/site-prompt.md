# Kujo AI SDK Website Build Benchmark Prompt

Return a single JSON object and no markdown.

The JSON must use this shape:

```json
{
  "ack": "kujo-ai-sdk-app-build-v1",
  "summary": "one short sentence",
  "files": {
    "public/index.php": "...",
    "public/assets/css/styles.css": "...",
    "public/assets/js/app.js": "...",
    "README.md": "..."
  },
  "verification": ["php -l public/index.php", "manual browser check"]
}
```

Build a compact PHP website app for a fictional agency called "Northstar Digital Works".

Requirements:

- Use HTML, CSS, JavaScript, and PHP.
- The first page must be `public/index.php`.
- Include a hero, services section, small work/portfolio section, and contact form.
- The PHP contact form must validate name, email, and message.
- The JavaScript must enhance the form with client-side validation and a visible success or error state.
- The CSS must be responsive and polished without external assets or CDNs.
- Keep all code self-contained in the files listed above.
- Avoid database, Composer, npm, package managers, external APIs, and build steps.
- Keep the app small enough to review quickly.

The response is used for benchmarking. Be deterministic, concise, and complete.

