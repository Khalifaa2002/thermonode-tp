"""Vérifie le démarrage de la passerelle sans lancer de services externes."""

import runpy
from unittest.mock import Mock


def test_main_uses_the_configured_database_and_http_port(monkeypatch, tmp_path):
    database = str(tmp_path / "gateway.sqlite")
    monkeypatch.setenv("DB_PATH", database)
    monkeypatch.setenv("HTTP_PORT", "8088")
    handler_factory = Mock()
    health_server = Mock()
    mqtt_factory = Mock()
    monkeypatch.setattr("gateway.handler.Handler", handler_factory)
    monkeypatch.setattr("gateway.health.start_health_server", health_server)
    monkeypatch.setattr("gateway.mqtt_client.GatewayMqtt", mqtt_factory)

    runpy.run_module("gateway.__main__", run_name="__main__")

    handler_factory.assert_called_once_with(database)
    health_server.assert_called_once_with(handler_factory.return_value, 8088)
    mqtt_factory.assert_called_once_with(handler_factory.return_value)
    mqtt_factory.return_value.run_forever.assert_called_once_with()
