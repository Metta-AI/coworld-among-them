import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sidecar.providers import create_provider


class NativeLlmTest(unittest.TestCase):
    def test_native_endpoint_and_model_precede_local_provider(self):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                requests.append((self.path, dict(self.headers), body))
                response = json.dumps({
                    'content': [
                        {'type': 'text', 'text': 'native reply'},
                        {'type': 'tool_use', 'id': 'call-1', 'name': 'submit_hypothesis',
                         'input': {'suspects': [], 'confidence': 'low', 'key_evidence': []}},
                    ],
                    'usage': {'input_tokens': 10, 'output_tokens': 3},
                }).encode()
                self.send_response(200)
                self.send_header('Content-Length', str(len(response)))
                self.end_headers()
                self.wfile.write(response)

            def log_message(self, *_args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        endpoint = f'http://127.0.0.1:{server.server_port}'
        try:
            with patch.dict(os.environ, {
                'COWORLD_LLM_ENDPOINT': endpoint,
                'COWORLD_LLM_MODEL': 'anthropic/claude-sonnet-4.6',
                'ANTHROPIC_API_KEY': 'local-key-must-not-be-sent',
            }):
                response = create_provider('bedrock:retired-model').complete(
                    'rules', [{'role': 'user', 'content': 'state'}]
                )
                self.assertEqual(response.text, 'native reply')
                self.assertEqual(response.input_tokens, 10)
                import importlib.util
                wrapper = Path(__file__).resolve().parents[2] / "players/mod_talks/cogames/amongthem_policy.py"
                spec = importlib.util.spec_from_file_location("native_mod_talks", wrapper)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                with patch.dict(os.environ, {
                    'MODTALKS_PROVIDER_OPENAI': '1',
                    'CLAUDE_CODE_USE_BEDROCK': '1',
                    'MODTALKS_LLM_MODEL': 'retired-model',
                }):
                    controller = module._build_llm_controller()
                    self.assertTrue(controller.enabled)
                    decision = json.loads(controller.complete(role=0, kind='hypothesis', context_json='{}'))
                    self.assertEqual(decision['confidence'], 'low')
                    self.assertEqual(controller._model, 'anthropic/claude-sonnet-4.6')

                if 'AMONG_NATIVE_PROBE' in os.environ:
                    subprocess.run([os.environ['AMONG_NATIVE_PROBE'], endpoint], check=True)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
        for path, headers, body in requests:
            self.assertEqual(path, '/v1/messages')
            self.assertEqual(body['model'], 'anthropic/claude-sonnet-4.6')
            self.assertNotIn('anthropic_version', body)
            self.assertNotIn('x-api-key', headers)
            self.assertNotIn('Authorization', headers)
