# Working in this repo

A ROS 2 Jazzy training course: slides in `slides/`, exercises in `exercises/`, lecture demos in
`examples/`, a student starter in `templates/`, and one finished snapshot per module in `solutions/`.
Only `examples/` and `src/` build; `solutions/`, `templates/` and `slides/` carry `COLCON_IGNORE`.

How to *write* a slide lives in [`slides/README.md`](slides/README.md). This file is about how to
know you have not broken anything.

## Before you say you are done

Run whichever of these your change touches. None is optional for its trigger.

| You changed…                                        | Run                                                              |
| --------------------------------------------------- | ---------------------------------------------------------------- |
| anything under `examples/`                          | `colcon test; colcon test-result --verbose` from the repo root   |
| anything under `solutions/module_N/`                | copy `solutions/module_7/*` into a scratch `src/`, build, `colcon test` |
| any file a slide quotes (see list below)            | `python3 slides/check_snippets.py` — CI fails on a mismatch      |
| any `slides/*.md`                                   | render that deck to PDF and **look at the changed page**         |
| `.github/workflows/slides.yml`                      | `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/slides.yml'))"` |

Slides quote source files verbatim, so editing a package can break a deck you never opened. Which
files are quoted right now:

```bash
grep -ho 'src: [^#]*' slides/*.md | sed 's/src: //' | sort -u
```

Marp does not report overflow. Text past the bottom of a slide only shows in the rendered PDF, so
after editing a slide, render it and inspect the page (`pdftoppm -f N -l N -r 100 -png deck.pdf out`).
Keep prose paragraphs on one source line — a newline inside a paragraph becomes a `<br>`.

## Solutions are duplicated snapshots — keep them in sync

`solutions/module_N/` is the finished package *after* module N, so later modules contain byte-identical
copies of earlier files. Edit one copy, propagate to the rest, then confirm with `md5sum`:

- `turtlebot_py_controller/laser_controller.py` — identical in modules 4–7 (2 and 3 differ)
- `turtlebot_py_controller/rotate_action_server.py` — identical in modules 5–7
- `turtlebot_interfaces/action/RotateToAngle.action` — identical in modules 4–7
- `launch/laser_controller.launch.py` — modules 3–5 start `laser_controller` only; 6–7 add `obstacle_locator`

## Environment facts that cost time to rediscover

- **PDF/PPTX cannot build in the dev container** — no browser. HTML builds fine. To render PDFs
  locally, `npx @puppeteer/browsers install chrome@stable` inside `slides/` (gitignored) and set
  `CHROME_PATH`. Run **one** `marp` at a time; concurrent processes share a profile directory and hang.
  `--browser-timeout 0` makes such a hang infinite — keep the default while iterating.
- `npm` is not installed in the container; `slides/node_modules/.bin/marp` works directly.
- The Gazebo diff-drive plugin **latches the last `/cmd_vel`**. Stopping a publisher does not stop
  the robot; publish an explicit zero. This is also why `laser_controller` sends one zero before
  going quiet on `enable_motion(false)`.
- `/scan` from `ros_gz_bridge` is **reliable**, not best-effort. 360 rays, index 0 straight ahead,
  5 Hz. `/odom` is ~50 Hz. `/cmd_vel` is `TwistStamped` — plain `Twist` publishes without error and
  does nothing.
- `ros2 run` forks the node as a child, so killing the wrapper leaves it running and holding pipes.
  Use `start_new_session=True` + `os.killpg` in harnesses, and write output to files, not pipes.
- `pkill -f <pattern>` matches the shell that runs it if the pattern appears anywhere in that
  command line — including a later `marp` or `ros2` invocation in the same string. Kill in a
  separate command, or use `"[m]arp"`-style patterns.
- The repo's default `GITHUB_TOKEN` is read-only. Release upload needs the explicit
  `permissions: contents: write` on the job in `slides.yml`; do not remove it.

## Sync points

If you change a fact about the simulation (rates, types, topic names), the same fact appears in
`README.md` ("Facts about the simulation"), `exercises/module_1.md`, and `slides/04-tools.md`.
