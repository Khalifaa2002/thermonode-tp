"""ENF-05 : mémorisation et retransmission après coupure du broker."""
import time
import pytest

pytestmark = pytest.mark.integration


@pytest.mark.timeout(180)
def test_ENF05_buffered_measures_are_resent_after_broker_outage(
    node, broker, gateway
):
    # Attendre une première trame valide.
    gateway.wait_for_frames(min_count=1, timeout_s=30)

    n0 = len(gateway.frames)
    last_seq_before = gateway.frames[-1]["seq"]

    # Forcer une véritable coupure de liaison sur le simulateur.
    node.inject_link_state(False)
    time.sleep(2)

    # Arrêter également le broker.
    broker.stop()
    gateway.wait_until_disconnected(timeout_s=15)

    # Produire des mesures pendant la coupure.
    node.inject_measures([25.1] * 30)
    time.sleep(65)

    # Redémarrer le broker.
    broker.start()

    # Rétablir la liaison du simulateur.
    node.inject_link_state(True)

    # Attendre les trames retransmises.
    frames = gateway.wait_for_frames(min_count=n0 + 6, timeout_s=30)

    # Vérifier que le diagnostic MQTT a bien observé des trames en buffer.
    gateway.wait_until_max_buffered(3, timeout_s=15)
    print(f"Maximum de trames observées dans le buffer : {gateway.max_buffered}")

    new_seqs = [
        frame["seq"]
        for frame in frames
        if frame["seq"] > last_seq_before
    ]

    print(f"Séquences reçues après reconnexion : {new_seqs}")
    assert len(new_seqs) >= 6, (
        f"Moins de 6 trames retransmises : {new_seqs}"
    )

    expected = list(
        range(last_seq_before + 1, last_seq_before + 1 + len(new_seqs))
    )

    assert new_seqs == expected, (
        f"Trames manquantes ou doublons : reçues={new_seqs}, "
        f"attendues={expected}"
    )
