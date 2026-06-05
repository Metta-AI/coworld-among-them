# How To Make An Among Them Coworld Player

This guide explains how to write a policy for the uploaded Among Them Coworld.
You do not need a source checkout to compete: package a player process in a
Linux Docker image, connect to the runner-supplied player websocket, play one
assigned slot, then submit the uploaded image to an Among Them league.

For the public starter policy and tournament walkthrough, use:

- <https://softmax.com/play_amongthem.md>
- `players/how_to_submit_coworld_policy.md`

If docs, commands, runtime behavior, logs, or replays disagree while you build
the player, preserve the evidence and file a GitHub issue. Use
<https://github.com/Metta-AI/coworld-among-them/issues> for game docs,
protocol, runtime, logs, or replays, and
<https://github.com/Metta-AI/coworld/issues> for the Softmax play prompt or
Coworld CLI. Include the command, league/Coworld ids, links to logs or replays,
and the smallest repro.

## Runtime Contract

In a Coworld episode, the runner starts one policy container per slot. Each
policy receives:

```text
COWORLD_PLAYER_WS_URL=ws://<game-service>:8080/player?slot=<slot>&token=<token>
```

Existing source bots in this repository read the older
`COGAMES_ENGINE_WS_URL` alias. Current runners set both names to the same URL.
Use the URL exactly as supplied.

Your player image can be written in any language. It must:

1. open the player websocket;
2. read Bitscreen v1 framebuffer packets;
3. infer enough game state to choose actions;
4. send valid button and chat packets;
5. keep running until the game ends or the runner stops the container.

Protocol references:

- Bitscreen player protocol: <https://github.com/Metta-AI/bitworld/blob/master/docs/bitscreen_v1.md>
- Global/replay viewer protocol: <https://github.com/Metta-AI/bitworld/blob/master/docs/sprite_v1.md>
- Public play guide: <https://softmax.com/play_amongthem.md>
- Coworld spec: <https://github.com/Metta-AI/metta/blob/main/packages/coworld/src/coworld/COWORLD_README.md>

## What The Player Sees

Among Them policy players do not receive structured JSON game state. They see a
small framebuffer and must recover useful state from pixels:

- movement phase, meeting phase, result screens, and game over;
- own position, role, color, and alive/dead state;
- visible task icons and task completion timing;
- visible bodies and nearby players;
- voting slots, cursor, votes, chat speakers, and chat text.

This is why source references matter. The stronger local bots are mostly
perception and control code, not high-level strategy.

## Source References

- `players/evidencebot_v2.nim`: stronger source-level visual bot.
- `players/nottoodumb/nottoodumb.nim`: smaller baseline visual bot.
- `players/ivotewell/ivotewell.nim`: bundled policy used by current Coworld
  smoke episodes.
- `players/evidencebot_strategy.md`: notes on the evidencebot design.
- `sim.nim`: game constants, task stations, movement, voting, and rendering.
- `tools/quick_run`: local source runner for games, human clients, and bots.

Do not assume these files exist in a hosted policy image unless you copy them
into the image.

## Container Shape

A minimal Python image looks like:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY player.py .

CMD ["python", "/app/player.py"]
```

Build for the platform used by Coworld jobs:

```sh
docker buildx build --platform linux/amd64 -t my-among-them-policy:latest --load .
coworld upload-policy my-among-them-policy:latest --name my-policy
```

Attach runtime secrets at upload time with `--secret-env` or `--use-bedrock`.
Do not bake API keys into the image.

## Local Source Run

Source-level runs are useful for debugging protocol and behavior, but they are
not the public submission contract.

Start the game server:

```sh
nim r among_them.nim --address:0.0.0.0 --port:2000 --config:'{"minPlayers":1,"imposterCount":0,"tasksPerPlayer":1}'
```

Run a source bot from another shell:

```sh
COGAMES_ENGINE_WS_URL='ws://localhost:2000/player?slot=0&token=' \
nim r players/nottoodumb/nottoodumb.nim -- --name nottoodumb
```

Or use `quick_run` from the repository root:

```sh
nim r tools/quick_run among_them --connect --bots:evidencebot_v2:8 --address:localhost --port:2000
```

## Player Loop

Keep the runtime loop simple and observable:

```text
websocket frame
  -> Bitscreen decoder
  -> perception state
  -> goal selection
  -> movement/input controller
  -> websocket input packet
```

Log phase, position, current goal, action button state, vote target, and major
events. If a league episode fails, the logs should explain whether the policy
failed to connect, lost localization, got stuck, or made a bad strategic
choice.

## Common Mistakes

| Symptom | Cause | Fix |
| --- | --- | --- |
| Works locally but not in league | Hardcoded localhost, slot, or token | Use the runner-supplied websocket URL exactly. |
| Bot moves but never completes tasks | Action is tapped while moving | Stop inside the task rectangle and hold action. |
| Policy cannot call an LLM | Secret only existed on your laptop | Re-upload with `--secret-env` or `--use-bedrock`. |
| Image runs locally but not in production | Built only for arm64 | Rebuild with `docker buildx build --platform linux/amd64 --load`. |
| Votes are random | Voting UI parsing is unstable | Log parsed slots, alive/dead status, cursor, votes, and chat. |

Start with a policy that connects, moves, and completes tasks. Add reporting,
voting, imposter behavior, memory, and LLM calls only after the basic loop
survives complete episodes.
