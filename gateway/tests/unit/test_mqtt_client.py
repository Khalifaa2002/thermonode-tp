"""Vérifie les interactions MQTT avec une doublure du client Paho."""

from collections import Counter
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from gateway.frame import Frame
from gateway.mqtt_client import GatewayMqtt


@pytest.fixture
def mqtt_dependencies(monkeypatch):
    monkeypatch.delenv("MQTT_USER", raising=False)
    monkeypatch.delenv("MQTT_PASSWORD", raising=False)
    client = Mock()
    monkeypatch.setattr("gateway.mqtt_client.mqtt.Client", Mock(return_value=client))
    handler = SimpleNamespace(on_data=Mock(), on_alert=None, metrics=Counter())
    return handler, client


def test_mqtt_subscribes_and_forwards_received_telemetry(mqtt_dependencies):
    handler, client = mqtt_dependencies
    gateway = GatewayMqtt(handler, host="broker.test", port=1884)

    gateway.run_forever()
    client.reconnect_delay_set.assert_called_once_with(1, 10)
    client.connect.assert_called_once_with("broker.test", 1884, keepalive=30)
    client.loop_forever.assert_called_once_with(retry_first_connection=True)
    client.username_pw_set.assert_not_called()

    client.on_connect(client, None, None, 0)
    client.subscribe.assert_called_once_with("thermonode/+/data")
    client.on_message(client, None, SimpleNamespace(payload=b'{"temp":25.5}'))
    handler.on_data.assert_called_once_with('{"temp":25.5}')


def test_mqtt_uses_environment_settings_and_publishes_alerts(monkeypatch, mqtt_dependencies):
    handler, client = mqtt_dependencies
    monkeypatch.setenv("MQTT_HOST", "configured.test")
    monkeypatch.setenv("MQTT_PORT", "1885")
    monkeypatch.setenv("MQTT_USER", "test-user")
    monkeypatch.setenv("MQTT_PASSWORD", "test-password")

    gateway = GatewayMqtt(handler)
    assert (gateway.host, gateway.port) == ("configured.test", 1885)
    client.username_pw_set.assert_called_once_with("test-user", "test-password")

    handler.on_alert(Frame("TN01", 1, 10, 70.5, "ALERT"))
    client.publish.assert_called_once()
    topic, payload = client.publish.call_args.args
    assert topic == "supervision/alerts"
    assert json.loads(payload) == {"id": "TN01", "temp": 70.5, "t": 10}


def test_mqtt_counts_processing_errors(mqtt_dependencies):
    handler, client = mqtt_dependencies
    handler.on_data.side_effect = RuntimeError("erreur simulée")
    GatewayMqtt(handler, host="broker.test", port=1884)

    client.on_message(client, None, SimpleNamespace(payload=b"test"))

    assert handler.metrics["errors"] == 1
