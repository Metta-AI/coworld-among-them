import
  std/[os, parseopt, strutils],
  bitworld/runtime,
  sim, server

proc limitText(value: int): string =
  ## Returns a readable text value for a numeric limit.
  if value > 0:
    $value
  else:
    "infinite"

proc echoStartupConfig(config: GameConfig, address: string, port: int) =
  ## Prints the effective startup config without token secrets.
  echo "Among Them config: host=", address,
    " port=", port,
    " seed=", config.seed,
    " minPlayers=", config.minPlayers,
    " slots=", config.slots.len,
    " maxTicks=", config.maxTicks.limitText(),
    " maxGames=", config.maxGames.limitText(),
    " map=", config.mapPath

when isMainModule:
  var
    address = cogameHost()
    port = cogamePort()
    configJson = ""
    configPath = pathFromCogameEnv(CogameConfigUriEnv)
    mapPath = ""
    saveReplayPath = outputPathFromCogameEnv(CogameSaveReplayUriEnv, "replay.bitreplay")
    loadReplayPath = pathFromCogameEnv(CogameLoadReplayUriEnv)
    saveScoresPath = outputPathFromCogameEnv(CogameResultsUriEnv, "scores.json")
    logUri = getEnv(CogameLogUriEnv)
    replayServerMode = false
    messageCooldown = -1
  for kind, key, val in getopt():
    case kind
    of cmdLongOption:
      case key
      of "address":
        address = val
      of "port":
        port = parseInt(val)
      of "config":
        configJson = val
      of "config-file":
        configPath = val
      of "map":
        mapPath = val
      of "save-replay":
        saveReplayPath = val
      of "load-replay":
        loadReplayPath = val
      of "save-scores":
        saveScoresPath = val
      of "log-uri":
        logUri = val
      of "message-cooldown":
        messageCooldown = max(0, parseInt(val))
      else: discard
    else: discard
  var config = defaultGameConfig()
  if configPath.len > 0:
    config.update(readFile(configPath))
  if configJson.len > 0:
    config.update(configJson)
  if mapPath.len > 0:
    config.mapPath = mapPath
  if messageCooldown >= 0:
    config.messageCooldownTicks = messageCooldown
  replayServerMode = loadReplayPath.len > 0
  config.echoStartupConfig(address, port)
  echo "Using map file: " & config.mapPath
  if configPath.len > 0:
    echo "Using config file: " & configPath
  if loadReplayPath.len > 0:
    echo "Using replay load file: " & loadReplayPath
  if saveReplayPath.len > 0:
    echo "Using replay save file: " & saveReplayPath
  if saveScoresPath.len > 0:
    echo "Using results save file: " & saveScoresPath
  if logUri.len > 0:
    echo "Using game log URI: " & logUri
  echo "starting among_them on ", address, ":", port
  runServerLoop(
    address,
    port,
    config,
    saveReplayPath,
    loadReplayPath,
    saveScoresPath,
    replayServerMode,
    logUri
  )
