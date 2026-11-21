"""Vérifie les réponses HTTP de la passerelle sans dépendre de Docker."""

from contextlib import closing
from http.client import HTTPConnection
from types import SimpleNamespace

import pytest

from gateway.health import start_health_server


@pytest.fixture(scope="module")
def health_port():
    handler = SimpleNamespace(metrics={"frames_stored": 1, "frames_received": 2})
    server = start_health_server(handler, port=0)
    try:
        yield server.server_port
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.parametrize(
    "path, status, body",
    [
        ("/health", 200, b"ok"),
        ("/metrics", 200, b"gateway_frames_received 2\ngateway_frames_stored 1\n"),
        ("/unknown", 404, b""),
    ],
)
def test_health_server_returns_expected_response(health_port, path, status, body):
    with closing(HTTPConnection("127.0.0.1", health_port, timeout=3)) as client:
        client.request("GET", path)
        with client.getresponse() as response:
            assert response.status == status
            assert response.read() == body
