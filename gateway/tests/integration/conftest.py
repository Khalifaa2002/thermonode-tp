"""Fixtures d'intégration : pilotent l'environnement ci/compose.test.yaml (broker, gateway, node-sim).
Exécution : docker compose -f ci/compose.test.yaml up -d --build --wait ; puis pytest tests/integration."""
import json, os, subprocess, threading, time
from pathlib import Path
import pytest
import paho.mqtt.client as mqtt

ROOT = Path(__file__).resolve().parents[3]
COMPOSE = ["docker", "compose", "-f", str(ROOT / "ci" / "compose.test.yaml")]
SCENARIO = ROOT / "tests" / "scenarios" / "current.csv"
MQTT_HOST = os.environ.get("MQTT_HOST", "localhost")
GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8000")

class Broker:
    def stop(self):  subprocess.run(COMPOSE + ["stop", "broker"], check=True)
    def start(self):
        subprocess.run(COMPOSE + ["start", "broker"], check=True)
        time.sleep(1)


class Node:
    """Écrit dans le scénario lu en continu par node-sim (une ligne = une mesure)."""
    def __init__(self, listener):
        self.listener = listener
    def inject_measures(self, temps):
        with SCENARIO.open("a") as f:
            f.write("".join(f"{t}\n" for t in temps))
    def inject_link_state(self, connected):
        """Force la liaison du simulateur : CONN:0 ou CONN:1."""
        state = 1 if connected else 0
        with SCENARIO.open("a") as f:
            f.write(f"CONN:{state}\n")
    def inject_command(self, obj):
        with SCENARIO.open("a") as f:
            f.write("CMD:" + json.dumps(obj, separators=(",", ":")) + "\n")
    def wait_until_buffered(self, n, timeout_s=60):
        t0 = time.time()
        while time.time() - t0 < timeout_s:
            if self.listener.buffered >= n:
                return
            time.sleep(0.2)
        raise AssertionError(f"tampon {self.listener.buffered} < {n} après {timeout_s} s")


class Listener:
    """Abonné MQTT avec réabonnement automatique après reconnexion."""

    def __init__(self):
        self.frames, self.acks, self.buffered = [], [], 0
        self.max_buffered = 0
        self.connected = threading.Event()

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="it-listener"
        )

        # Limiter le délai entre les tentatives de reconnexion.
        self.client.reconnect_delay_set(
            min_delay=1,
            max_delay=5
        )

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on

        self.client.connect(MQTT_HOST, 1883)
        self.client.loop_start()

        if not self.connected.wait(timeout=15):
            raise RuntimeError(
                "Listener : connexion initiale au broker impossible"
            )

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            return

        result, _ = client.subscribe([
            ("thermonode/+/data", 0),
            ("thermonode/+/diag", 0),
            ("thermonode/+/ack", 0)
        ])

        if result == mqtt.MQTT_ERR_SUCCESS:
            self.connected.set()

    def _on_disconnect(
        self, client, userdata, disconnect_flags, reason_code, properties
    ):
        self.connected.clear()

    def _on(self, client, userdata, msg):
        p = msg.payload.decode(errors="replace")

        if msg.topic.endswith("/data"):
            try:
                self.frames.append(json.loads(p))
            except ValueError:
                pass

        elif msg.topic.endswith("/diag"):
            self.buffered = json.loads(p).get("buffered", 0)
            self.max_buffered = max(self.max_buffered, self.buffered)

        else:
            self.acks.append(p)

    def wait_for_frames(self, min_count, timeout_s):
        t0 = time.time()

        while time.time() - t0 < timeout_s:
            if len(self.frames) >= min_count:
                return list(self.frames)

            time.sleep(0.2)

        raise AssertionError(
            f"{len(self.frames)} trames < {min_count} après {timeout_s} s"
        )

    def wait_until_disconnected(self, timeout_s=15):
        deadline = time.time() + timeout_s

        while time.time() < deadline:
            if not self.connected.is_set():
                return
            time.sleep(0.1)

        raise AssertionError(
            f"Listener toujours connecté après {timeout_s} secondes"
        )

    def wait_until_connected(self, timeout_s=15):
        if not self.connected.wait(timeout=timeout_s):
            raise AssertionError(
                f"Listener non reconnecté après {timeout_s} secondes"
            )

    def wait_until_max_buffered(self, n, timeout_s=15):
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            if self.max_buffered >= n:
                return
            time.sleep(0.1)
        raise AssertionError(
            f"Maximum du buffer observé : {self.max_buffered}, attendu : au moins {n}"
        )

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()


@pytest.fixture(scope="session")
def env():
    SCENARIO.write_text("# scénario courant (écrit par les tests)\n25.0\n")
    subprocess.run(COMPOSE + ["up", "-d", "--build", "--wait"], check=True)
    yield
    subprocess.run(COMPOSE + ["down"], check=False)


@pytest.fixture
def gateway(env):
    l = Listener(); yield l; l.close()

@pytest.fixture
def broker(env):
    return Broker()

@pytest.fixture
def node(env, gateway):
    return Node(gateway)
