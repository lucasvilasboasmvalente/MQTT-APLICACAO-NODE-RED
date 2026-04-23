import paho.mqtt.client as mqtt
import json, time, random

BROKER = "broker.hivemq.com"
PORT = 1883

client = mqtt.Client()
client.connect(BROKER, PORT)

# Escuta comandos
def on_message(client, userdata, msg):
    cmd = json.loads(msg.payload)
    print(f"Comando recebido: {cmd}")

client.subscribe("casa/sala/+/cmd")
client.on_message = on_message
client.loop_start()

while True:
    # Publica status da lâmpada
    payload_lamp = json.dumps({
        "ligada": random.choice([True, True, False]),
        "brilho": random.randint(40, 100)
    })
    client.publish("casa/sala/lampada/status", payload_lamp)

    # Publica status da tomada
    payload_tom = json.dumps({
        "ligada": True,
        "consumo_w": round(random.uniform(0, 150), 1)
    })
    client.publish("casa/sala/tomada/status", payload_tom)

    print(f"Publicado: {payload_lamp}")
    time.sleep(3)