import json
import random
import time

import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883

TOPIC_CMD = "casa/sala/+/cmd"
TOPIC_LAMP_STATUS = "casa/sala/lampada/status"
TOPIC_TOMADA_STATUS = "casa/sala/tomada/status"

lamp_state = {"ligada": True, "brilho": 70}


def clamp_brilho(valor):
    return max(0, min(100, int(valor)))


def on_message(_client, _userdata, msg):
    """Recebe comandos enviados no tópico de /cmd e imprime no terminal."""
    cmd = json.loads(msg.payload)
    if msg.topic == "casa/sala/lampada/cmd":
        acao = cmd.get("acao")
        if acao == "desligar":
            lamp_state["ligada"] = False
        elif acao == "ligar":
            lamp_state["ligada"] = True

        if "brilho" in cmd:
            try:
                lamp_state["brilho"] = clamp_brilho(cmd["brilho"])
            except (TypeError, ValueError):
                pass

    print(f"Comando recebido em {msg.topic}: {cmd}")


def main():
    client = mqtt.Client()
    client.connect(BROKER, PORT)

    # Escuta comandos publicados em qualquer device/acao
    client.subscribe(TOPIC_CMD)
    client.on_message = on_message
    client.loop_start()

    while True:
        # Simula pequenas variações no brilho quando a lâmpada está ligada.
        if lamp_state["ligada"]:
            lamp_state["brilho"] = clamp_brilho(
                lamp_state["brilho"] + random.randint(-4, 4)
            )
        else:
            lamp_state["brilho"] = 0

        # Publica status da lâmpada
        payload_lamp = json.dumps(
            {
                "ligada": lamp_state["ligada"],
                "brilho": lamp_state["brilho"],
            }
        )
        client.publish(TOPIC_LAMP_STATUS, payload_lamp)

        # Publica status da tomada
        payload_tomada = json.dumps(
            {
                "ligada": True,
                "consumo_w": round(random.uniform(0, 150), 1),
            }
        )
        client.publish(TOPIC_TOMADA_STATUS, payload_tomada)

        print(f"Publicado: {payload_lamp}")
        time.sleep(3)


if __name__ == "__main__":
    main()