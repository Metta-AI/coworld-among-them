import std/[json, os]
import ../[llm_provider, types]

putEnv("COWORLD_LLM_ENDPOINT", paramStr(1))
putEnv("COWORLD_LLM_MODEL", "anthropic/claude-sonnet-4.6")
putEnv("ANTHROPIC_API_KEY", "local-key-must-not-be-sent")
let provider = newLlmProvider("bedrock", "retired-model")
let completion = provider.complete(RoleCrewmate, lckHypothesis, "{}")
doAssert not completion.errored
