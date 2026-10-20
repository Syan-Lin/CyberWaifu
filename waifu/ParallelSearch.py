"""Small synchronous client for Parallel's anonymous, stateless HTTP MCP endpoint.

Uses the standard library to keep compatibility with the existing Python 3.10
and LangChain dependencies. Conversation identity is supplied by Waifu, never
stored on the transport.
"""
import json
from http.client import HTTPException
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class ParallelSearchError(Exception):
    """Search is unavailable; the conversation can continue without web context."""


class ParallelSearch:
    URL = 'https://search.parallel.ai/mcp'
    USER_AGENT = 'CyberWaifu/1.0 (+https://github.com/Syan-Lin/CyberWaifu)'
    PROTOCOL = '2025-03-26'
    MAX_RESPONSE = 1024 * 1024

    def __init__(self, timeout=15):
        self.timeout = timeout

    def _post(self, method, params, request_id=1):
        payload = {'jsonrpc': '2.0', 'method': method, 'params': params}
        if request_id is not None:
            payload['id'] = request_id
        request = Request(self.URL, data=json.dumps(payload).encode('utf-8'), headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'User-Agent': self.USER_AGENT,
            'MCP-Protocol-Version': self.PROTOCOL,
        })
        try:
            with urlopen(request, timeout=self.timeout) as response:
                if request_id is None:
                    return None
                if response.headers.get_content_type() == 'text/event-stream':
                    reply = self._read_event(response, request_id)
                else:
                    raw = response.read(self.MAX_RESPONSE + 1)
                    if len(raw) > self.MAX_RESPONSE:
                        raise ParallelSearchError('MCP response is too large')
                    reply = json.loads(raw)
            if (not isinstance(reply, dict) or reply.get('jsonrpc') != '2.0'
                    or reply.get('id') != request_id):
                raise ParallelSearchError('Invalid MCP response')
            if 'error' in reply:
                raise ParallelSearchError('MCP request failed')
            if not isinstance(reply.get('result'), dict):
                raise ParallelSearchError('Invalid MCP result')
            return reply['result']
        except (URLError, OSError, HTTPException, ValueError, TypeError) as error:
            raise ParallelSearchError('Parallel search request failed: ' + str(error)) from error

    def _read_event(self, response, request_id):
        """Read the matching SSE event without waiting for a persistent stream to close."""
        data = []
        size = 0
        while size <= self.MAX_RESPONSE:
            line = response.readline(self.MAX_RESPONSE + 1)
            size += len(line)
            if size > self.MAX_RESPONSE:
                break
            if line in (b'\n', b'\r\n', b''):
                if data:
                    event = json.loads('\n'.join(data))
                    if isinstance(event, dict) and event.get('id') == request_id:
                        return event
                    data = []
                if not line:
                    break
            elif line.startswith(b'data:'):
                data.append(line[5:].decode('utf-8').strip())
        raise ParallelSearchError('Missing or oversized MCP event')

    def run(self, question, session_id=None):
        # The endpoint is stateless: initialize each operation rather than cache
        # mutable transport/session state across concurrent conversations.
        initialized = self._post('initialize', {
            'protocolVersion': self.PROTOCOL,
            'capabilities': {},
            'clientInfo': {'name': 'CyberWaifu', 'version': '1.0'},
        })
        if initialized.get('protocolVersion') != self.PROTOCOL:
            raise ParallelSearchError('Unsupported MCP protocol version')
        self._post('notifications/initialized', {}, request_id=None)
        tools = self._post('tools/list', {}).get('tools', [])
        if not isinstance(tools, list) or not any(
                isinstance(tool, dict) and tool.get('name') == 'web_search' for tool in tools):
            raise ParallelSearchError('MCP web_search tool is unavailable')
        arguments = {'objective': question, 'search_queries': [question]}
        if session_id is not None:
            arguments['session_id'] = session_id
        result = self._post('tools/call', {'name': 'web_search', 'arguments': arguments})
        if result.get('isError'):
            raise ParallelSearchError('Parallel web_search returned an error')
        data = result.get('structuredContent')
        if data is None:
            try:
                data = json.loads(next(block['text'] for block in result.get('content', [])
                                       if block.get('type') == 'text'))
            except (ValueError, TypeError, KeyError, StopIteration, AttributeError) as error:
                raise ParallelSearchError('Invalid search content') from error
        if not isinstance(data, dict) or not isinstance(data.get('results'), list):
            raise ParallelSearchError('Invalid search results')
        return self._context(data['results'])

    @staticmethod
    def _context(results):
        """Keep a small sourced context without truncating source URLs."""
        entries = []
        remaining = 1024
        for result in results:
            if not isinstance(result, dict):
                continue
            url = result.get('url', '')
            if not isinstance(url, str) or len(url) > 512:
                continue
            try:
                parsed = urlsplit(url)
                if parsed.scheme not in ('http', 'https') or not parsed.netloc:
                    continue
            except ValueError:
                continue
            title = result.get('title') or ''
            excerpts = result.get('excerpts') or []
            if not isinstance(title, str) or not isinstance(excerpts, list):
                continue
            header = f'{title[:80]}\n{url}\n'
            if len(header) >= remaining:
                continue
            excerpt = ' '.join(text for text in excerpts if isinstance(text, str))
            entry = header + excerpt[:min(256, remaining - len(header))]
            entries.append(entry)
            remaining -= len(entry) + 2
            if len(entries) == 2:
                break
        return '\n\n'.join(entries)
