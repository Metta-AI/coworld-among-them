# Among Them Supporting Roles

Most policy authors only need the rules, play guide, player guide, and submit
guide. The supporting roles below are run by the Coworld platform around each
league episode. They are listed in the manifest so agents can understand what
will happen to an episode after policies play.

## Optimizer

The optimizer is an optional local workbench for improving policy code. It uses
the Coworld manifest, the public play guide, episode artifacts, and policy
templates to suggest or test policy changes. Policy authors do not need to run
the optimizer to submit to a league.

## Optimizer Inputs

The optimizer-facing manifest pages identify the game spec, public tutorial,
skill catalog, and policy-template registry used by the workbench. For Among
Them, the most important public inputs are:

- `coworld_manifest.json`: game config schema, variants, bundled images, and
  role metadata.
- `https://softmax.com/play_amongthem.md`: current public play and submission
  walkthrough.
- `players/SMART_BOT_GUIDE.md`: policy-improvement checklist for agents.

## Commissioner

The commissioner schedules league episodes and updates league placement. Among
Them currently uses the shared Coworld commissioner behavior: it creates
episodes for submitted policies, tracks placement matches, and moves policies
through league state.

## Reporter

The reporter turns episode artifacts into human-readable summaries. It reads
replays, results, logs, and role metadata, then emits report artifacts that are
useful for standings pages and debugging.

## Grader

The grader consumes episode artifacts and emits scalar scores or labels used by
the league and optimizer. For social-deduction games, useful grading signals
include win/loss, task progress, kills, reports, votes, survival, and whether a
policy stayed connected.

## Diagnoser

The diagnoser consumes a target policy and episode artifacts, then produces
advice for the agent improving that policy. Good diagnoser output points to a
specific failure mode, such as connection failure, bad navigation, missing task
execution, weak meeting behavior, or timeouts.
