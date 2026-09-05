# Authoring the slides

Lecture slides are plain Markdown rendered with [Marp](https://marp.app), one file per lecture
module; one `---` per slide. Everything below runs from this directory.

```bash
npm ci                           # once
npm run preview                  # live-reload server at http://localhost:8080
npm run build                    # HTML + PDF + PPTX into build/
python3 check_snippets.py        # verify code blocks against the packages; --fix rewrites line ranges
```

In VS Code, the *Marp for VS Code* extension gives an inline preview.

`npm run build:pdf` and `build:pptx` need a real browser, which the dev container does not have.
Inside the container, build HTML only, or fetch a standalone Chrome once:

```bash
npx @puppeteer/browsers install chrome@stable          # ~390 MB, gitignored
export CHROME_PATH="$PWD/chrome/linux-*/chrome-linux64/chrome"
```

Run one deck at a time. Concurrent `marp` processes share a browser profile directory and will
hang against each other; that is also why `build:pptx` passes `--parallel 1` in `package.json`.

## Conventions

- Code is always a fenced block, never a screenshot. Use `bash` for commands the student types,
  `console` for command + output, `python` / `yaml` / `xml` for source.
- Source snippets are copied **verbatim** from the packages in this repo. Every code slide carries an
  HTML comment naming the file and line range, e.g.
  `<!-- src: examples/ros2_examples/ros2_examples/topics/minimal_publisher.py#L13-L27 -->`.
  Methods lifted from inside a class are dedented by a uniform amount; nothing else changes.
  `check_snippets.py` verifies every block, and CI runs it on every push.
- Two columns: wrap in `<div class="cols">` with two child `<div>`s
  (`cols wide-left` / `cols wide-right` for 3:2 splits).
- Section dividers: `<!-- _class: divider -->`. Title slide: `<!-- _class: title -->`.
- Per-delivery values (`{{ CITY }}`, `{{ DATE }}`) live on the title slide only.
- Speaker notes go in an HTML comment at the end of the slide.
- **A slide has a fixed height and Marp will not warn you when you exceed it.** Text simply runs off
  the bottom edge, past the footer, and only shows up in the rendered PDF. After adding anything to a
  slide — especially a column that already looks full — render that deck and look at the page.
- Prose paragraphs go on **one source line**. A newline inside a paragraph becomes a `<br>`, so
  hand-wrapped source produces ragged lines and wastes vertical space, which is how slides overflow.

## Changing a file that a slide quotes

`check_snippets.py` compares each `<!-- src: -->` block against the live file, so editing a package
under `examples/`, `templates/` or `solutions/` can break a deck you never opened. After such an
edit:

```bash
python3 check_snippets.py        # from this directory
```

If a block moved but its content is unchanged, `--fix` rewrites the line ranges. If the content
itself changed, update the slide text to match.

These files are currently quoted by the decks:

```bash
grep -ho 'src: [^#]*' *.md | sed 's/src: //' | sort -u
```
