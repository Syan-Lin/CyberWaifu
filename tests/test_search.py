"""Run with: python -m unittest discover -s tests -v

Uses real LangChain messages and the normal Waifu caller with a scripted Brain.
No model, QQ account, GPU, or search credentials are needed.
"""
import configparser
import io
import json
import os
import runpy
import sys
import tempfile
import types
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from email.message import Message
from http.client import IncompleteRead
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from waifu.ParallelSearch import ParallelSearch
from waifu.Thoughts import Search
from waifu.Waifu import Waifu


ROOT = Path(__file__).resolve().parents[1]
QUESTION = '请查询 Python 最新版本的文档'
RESULT = {'results': [{'title': 'Python documentation',
                       'url': 'https://docs.python.org/3.10/',
                       'excerpts': ['Python 3.10 documentation and tutorials.']}],
          'session_id': 'server-echo', 'search_id': 'search-fixture'}


class ScriptedBrain:
    """Only model inference and memory retrieval are replaced."""
    def __init__(self, *args, **kwargs):
        self.llm = self
        self.received = []

    def get_num_tokens_from_messages(self, messages):
        return len(messages) * 10

    def get_num_tokens(self, text):
        return len(text) // 4

    def extract_memory(self, text):
        return [], []

    def think_nonstream(self, messages):
        return 'Python 最新 版本 文档'

    def think(self, messages):
        self.received.append(messages)
        return 'Scripted reply using context: ' + '\n'.join(
            m.content for m in messages if 'untrusted web context' in m.content)


class Response(io.BytesIO):
    def __init__(self, payload, content_type='application/json', session_id=None):
        super().__init__(payload)
        self.headers = Message()
        self.headers['Content-Type'] = content_type
        if session_id is not None:
            self.headers['MCP-Session-Id'] = session_id


class Wire:
    def __init__(self, tool_result=None, sse=False, failure=None):
        self.requests = []
        self.tool_result = tool_result or {'structuredContent': RESULT}
        self.sse = sse
        self.failure = failure
        self.transport_sessions = set()

    def __call__(self, request, timeout):
        payload = json.loads(request.data)
        self.requests.append((request, timeout, payload))
        method = payload['method']
        session = request.get_header('Mcp-session-id')
        if method == 'initialize':
            assert session is None
            session = str(uuid.uuid4())
            self.transport_sessions.add(session)
            result = {'protocolVersion': ParallelSearch.PROTOCOL}
        else:
            assert session in self.transport_sessions
            if method == 'notifications/initialized':
                return Response(b'', session_id=session)
            elif method == 'tools/list':
                result = {'tools': [{'name': 'web_search'}]}
            else:
                if self.failure:
                    raise self.failure
                result = self.tool_result
        reply = {'jsonrpc': '2.0', 'id': payload['id'], 'result': result}
        raw = json.dumps(reply).encode()
        if self.sse:
            return Response(b': keepalive\n\ndata: ' + raw + b'\n\n', 'text/event-stream', session)
        return Response(raw, session_id=session)

    @property
    def calls(self):
        return [payload['params']['arguments'] for _, _, payload in self.requests
                if payload['method'] == 'tools/call']


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        old_cwd = os.getcwd()
        os.chdir(self.directory.name)
        self.addCleanup(os.chdir, old_cwd)

    def waifu(self, **kwargs):
        return Waifu(ScriptedBrain(), 'Helpful chatbot', 'test', 'user',
                     use_emoji=False, use_emoticon=False, **kwargs)

    def test_normal_caller_consumes_sourced_context_and_headers(self):
        wire = Wire()
        with patch('waifu.ParallelSearch.urlopen', wire):
            bot = self.waifu(use_search=True)
            reply = bot.ask(QUESTION)
        self.assertEqual(bot.search.provider, 'parallel')
        self.assertIn('Python 3.10 documentation', reply)
        self.assertIn('https://docs.python.org/3.10/', reply)
        self.assertIn('from Parallel', reply)
        self.assertNotIn('from Google', reply)
        self.assertEqual([p['method'] for _, _, p in wire.requests],
                         ['initialize', 'notifications/initialized', 'tools/list', 'tools/call'])
        self.assertEqual([p.get('id') for _, _, p in wire.requests], [1, None, 2, 3])
        self.assertEqual(len(wire.transport_sessions), 1)
        transport_session = next(iter(wire.transport_sessions))
        self.assertNotEqual(transport_session, bot.search_session_id)
        for request, timeout, payload in wire.requests:
            self.assertEqual(request.full_url, 'https://search.parallel.ai/mcp')
            self.assertEqual(request.get_header('User-agent'), ParallelSearch.USER_AGENT)
            self.assertEqual(request.get_header('Mcp-protocol-version'), ParallelSearch.PROTOCOL)
            self.assertIn('text/event-stream', request.get_header('Accept'))
            self.assertIsNone(request.get_header('Authorization'))
            self.assertEqual(timeout, 15)
            if payload['method'] != 'initialize':
                self.assertEqual(request.get_header('Mcp-session-id'), transport_session)
        self.assertEqual(wire.calls[0]['session_id'], bot.search_session_id)
        self.assertEqual(wire.calls[0]['search_queries'], ['Python 最新 版本 文档'])
        self.assertEqual(wire.calls[0]['objective'], 'Python 最新 版本 文档')
        self.assertNotIn('model_name', wire.calls[0])  # No guessed model identifier.

    def test_sse_and_legacy_text_content(self):
        wire = Wire({'content': [{'type': 'text', 'text': json.dumps(RESULT)}]}, sse=True)
        with patch('waifu.ParallelSearch.urlopen', wire):
            self.assertIn('Python 3.10', self.waifu(use_search=True).ask(QUESTION))

    def test_disabled_default_and_short_messages_make_no_request(self):
        with patch('waifu.ParallelSearch.urlopen') as transport:
            bot = self.waifu()
            bot.ask(QUESTION)
            self.assertFalse(hasattr(bot, 'search'))
            bot = self.waifu(use_search=True)
            bot.ask('你好')
            transport.assert_not_called()
        config = configparser.ConfigParser()
        config.read(ROOT / 'template.ini', encoding='utf-8')
        self.assertFalse(config.getboolean('Thoughts', 'use_search'))

    def test_saved_serper_credentials_and_explicit_overrides(self):
        self.assertEqual(Search(ScriptedBrain(), 'configured-key').provider, 'serper')
        with patch.dict(os.environ, {'SERPER_API_KEY': 'environment-key'}):
            selected = Search(ScriptedBrain())
            self.assertEqual(selected.provider, 'serper')
            self.assertEqual(selected.search.serper_api_key, 'environment-key')
            self.assertEqual(Search(ScriptedBrain(), provider='parallel').provider, 'parallel')
        explicit = Search(ScriptedBrain(), 'configured-key', 'parallel')
        self.assertEqual(explicit.provider, 'parallel')
        with self.assertRaises(ValueError):
            Search(ScriptedBrain(), provider='unknown')
        with self.assertRaises(ValueError):
            Search(ScriptedBrain(), provider='serper')

    def test_serper_behavior_and_no_fallback_on_failure(self):
        bot = self.waifu(use_search=True, search_api='saved-key')
        with patch('waifu.ParallelSearch.urlopen') as parallel:
            with patch.object(type(bot.search.search), 'run', return_value='x' * 500):
                question, answer = bot.search.think(QUESTION)
                self.assertEqual(len(answer), 256)
                reply = bot.ask(QUESTION)
                self.assertIn('from Google', reply)
            with patch.object(type(bot.search.search), 'run', side_effect=RuntimeError('Serper failed')):
                with self.assertRaisesRegex(RuntimeError, 'Serper failed'):
                    bot.ask(QUESTION)
            parallel.assert_not_called()
        self.assertEqual((bot.search.search.gl, bot.search.search.hl, bot.search.search.k),
                         ('cn', 'zh-cn', 20))

    def test_timeouts_quota_tool_errors_and_retry_keep_conversation(self):
        bot = self.waifu(use_search=True)
        session = bot.search_session_id
        failures = [TimeoutError('timed out'), IncompleteRead(b'', 100), HTTPError(ParallelSearch.URL, 429,
                    'anonymous quota', {}, io.BytesIO(b'free-tier quota exceeded'))]
        for failure in failures:
            wire = Wire(failure=failure)
            with self.subTest(failure=str(failure)), patch('waifu.ParallelSearch.urlopen', wire):
                reply = bot.ask(QUESTION)
                self.assertNotIn('untrusted web context', reply)
                self.assertEqual(wire.calls[0]['session_id'], session)
        wire = Wire({'isError': True, 'content': [{'type': 'text', 'text': 'Quota exceeded'}]})
        with patch('waifu.ParallelSearch.urlopen', wire):
            self.assertNotIn('untrusted web context', bot.ask(QUESTION))
        wire = Wire()
        with patch('waifu.ParallelSearch.urlopen', wire):
            self.assertIn('Python 3.10', bot.ask(QUESTION))
        self.assertEqual(wire.calls[0]['session_id'], session)

    def test_cancellation_propagates(self):
        bot = self.waifu(use_search=True)
        wire = Wire(failure=KeyboardInterrupt())
        with patch('waifu.ParallelSearch.urlopen', wire), self.assertRaises(KeyboardInterrupt):
            bot.ask(QUESTION)

    def test_explicit_parallel_failure_never_uses_saved_serper_key(self):
        with patch('waifu.Thoughts.GoogleSerperAPIWrapper') as serper:
            bot = self.waifu(use_search=True, search_api='saved-key', search_provider='parallel')
            with patch('waifu.ParallelSearch.urlopen', Wire(failure=TimeoutError())):
                self.assertNotIn('untrusted web context', bot.ask(QUESTION))
            serper.assert_not_called()

    def test_malformed_response_and_rpc_error_do_not_enter_context(self):
        for body in (b'not json', b'{"jsonrpc":"2.0","id":1,"error":{"code":-32600}}',
                     b'{"jsonrpc":"2.0","id":999,"result":{}}'):
            with self.subTest(body=body), patch('waifu.ParallelSearch.urlopen',
                    side_effect=lambda *a, **kw: Response(body)):
                self.assertNotIn('untrusted web context', self.waifu(use_search=True).ask(QUESTION))
        for result in ({'structuredContent': {'results': {}}}, {'content': []}):
            with patch('waifu.ParallelSearch.urlopen', Wire(result)):
                self.assertNotIn('untrusted web context', self.waifu(use_search=True).ask(QUESTION))

    def test_context_is_bounded_and_preserves_source_urls(self):
        data = {'results': RESULT['results'] * 10}
        data['results'] = [dict(item, excerpts=['x' * 10000]) for item in data['results']]
        wire = Wire({'structuredContent': data})
        with patch('waifu.ParallelSearch.urlopen', wire):
            question, context = self.waifu(use_search=True).search.think(QUESTION)
        self.assertLessEqual(len(context), 1024)
        self.assertEqual(context.count('https://docs.python.org/3.10/'), 2)
        wire = Wire({'structuredContent': {'results': [{'url': 'file:///etc/passwd'}]}})
        with patch('waifu.ParallelSearch.urlopen', wire):
            self.assertNotIn('untrusted web context', self.waifu(use_search=True).ask(QUESTION))

    def test_conversation_ids_follow_waifu_not_shared_client(self):
        first, second = self.waifu(use_search=True), self.waifu(use_search=True)
        second.search.search = first.search.search  # The transport may be cached/shared.
        self.assertNotEqual(first.search_session_id, second.search_session_id)
        uuid.UUID(first.search_session_id)
        wire = Wire()
        with patch('waifu.ParallelSearch.urlopen', wire):
            first.ask(QUESTION)
            second.ask(QUESTION)
            first.ask(QUESTION)
            with ThreadPoolExecutor(max_workers=2) as pool:
                list(pool.map(lambda bot: bot.ask(QUESTION), [first, second]))
            new_chat = self.waifu(use_search=True)
            new_chat.ask(QUESTION)
        ids = [c['session_id'] for c in wire.calls]
        # Each operation gets a separate transport session, even on one client.
        transport_ids = [r.get_header('Mcp-session-id') for r, _, p in wire.requests
                         if p['method'] == 'tools/call']
        self.assertEqual(len(set(transport_ids)), 6)
        self.assertFalse(set(transport_ids).intersection(ids))
        self.assertEqual(ids[:3], [first.search_session_id, second.search_session_id,
                                  first.search_session_id])
        self.assertCountEqual(ids[3:5], [first.search_session_id, second.search_session_id])
        self.assertEqual(ids[5], new_chat.search_session_id)
        self.assertNotIn(ids[5], ids[:5])

    def test_main_loads_legacy_and_explicit_config_through_real_waifu(self):
        def module(name, **attrs):
            obj = types.ModuleType(name)
            obj.__dict__.update(attrs)
            return obj

        class Callback:
            def __init__(self, *args): pass
            def register(self, bot): pass

        captured = []
        def bot_loop(callback, bot, *args):
            captured.append(bot)
            bot.ask(QUESTION)

        stubs = {
            'waifu.llm.GPT': module('waifu.llm.GPT', GPT=ScriptedBrain),
            'waifu.llm.Claude': module('waifu.llm.Claude', Claude=ScriptedBrain),
            'waifu.StreamCallback': module('waifu.StreamCallback', WaifuCallback=Callback),
            'tts.TTS': module('tts.TTS', TTS=lambda *args: object()),
            'tts.edge.edge': module('tts.edge.edge', speak=lambda *args: None),
            'qqbot.qqbot': module('qqbot.qqbot', make_qq_bot=bot_loop),
        }
        Path('presets/charactor').mkdir(parents=True)
        Path('presets/charactor/test.txt').write_text('Helpful chatbot', encoding='utf-8')
        Path('presets/emoticon').mkdir()
        for provider in (None, 'parallel'):
            config = configparser.ConfigParser()
            config.read(ROOT / 'template.ini', encoding='utf-8')
            config['CyberWaifu'].update(charactor='test', memory='')
            config.remove_section('Thoughts_Emoticon')
            config.add_section('Thoughts_Emoticon')
            config['Thoughts'].update(use_search='True', use_emoticon='False',
                                      use_qqface='False', use_emoji='False')
            if provider is None:
                config.remove_option('Thoughts', 'search_provider')
                config.remove_section('Thoughts_GoogleSerperAPI')
            else:
                config['Thoughts']['search_provider'] = provider
                config['Thoughts_GoogleSerperAPI']['api'] = 'preserved-but-overridden'
            with open('config.ini', 'w', encoding='utf-8') as file:
                config.write(file)
            with patch.dict(sys.modules, stubs), patch('waifu.ParallelSearch.urlopen', Wire()):
                runpy.run_path(str(ROOT / 'main.py'), run_name='__main__')
            self.assertEqual(captured[-1].search.provider, 'parallel')
            self.assertTrue(any('Python 3.10' in m.content
                                for m in captured[-1].brain.received[-1]))


if __name__ == '__main__':
    unittest.main()
