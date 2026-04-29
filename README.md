# 🏠 Automação Residencial com MQTT, HiveMQ e Node-RED

Projeto de simulação de automação residencial usando MQTT, broker HiveMQ, um Codespace e Node-RED via FlowFuse. A ideia é ver o fluxo completo: dados chegam pelo MQTT, o Node-RED organiza e atualiza a interface, e um botão envia comandos de volta.

---

## 📐 Visão Geral

```
[Codespace - Mosquitto]         [HiveMQ Broker]         [FlowFuse - Node-RED]
  mosquitto_pub           →    broker.hivemq.com    →    Recebe/subscreve tópicos
  simulador.py            →    (broker público)     →    Processa mensagens
  mosquitto_sub           ←                         ←    Envia comandos
                                                           ↓
                                                     [Dashboard /ui]
                                                     Gauge de brilho
                                                     Status da lâmpada
                                                     Botão de controle
```

O sistema funciona com comunicação `publish/subscribe` (MQTT), o que ajuda bastante quando vários clientes precisam trocar informações sem ficar dependente de chamadas “um para o outro”.

### Como pensamos as decisões

**Por que MQTT no lugar de HTTP?**
MQTT é bem leve e foi feito para cenários IoT. Em vez de a cada passo existir uma requisição/resposta, ele mantém a troca por tópicos, então o Node-RED consegue consumir e reagir a mensagens assim que elas aparecem.

**Por que usar HiveMQ público?**
O `broker.hivemq.com` atende como um broker MQTT gratuito e público. Assim, não precisa montar infraestrutura própria só para testar o fluxo.

**Por que separar `/status` e `/cmd`?**
Separar os caminhos deixa o “sentido” bem claro:
- `/status` — eventos dos “dispositivos” chegando ao sistema
- `/cmd` — comandos saindo do sistema para os “dispositivos”

Na prática, isso reduz confusão e ajuda no debug quando algo não atualiza como esperado.

---

## 📡 Tópicos MQTT

| Tópico | Entra/Sai | Exemplo de payload |
|---|---|---|
| `casa/sala/lampada/status` | Codespace → Node-RED | `{"ligada": true, "brilho": 80}` |
| `casa/sala/tomada/status` | Codespace → Node-RED | `{"ligada": false, "consumo_w": 0}` |
| `casa/sala/lampada/cmd` | Node-RED → Codespace | `{"acao": "ligar", "brilho": 90}` |
| `casa/sala/tomada/cmd` | Node-RED → Codespace | `{"acao": "desligar"}` |

---

## 🧰 Tecnologias utilizadas

| Ferramenta | Papel no projeto |
|---|---|
| GitHub Codespace | Ambiente para testes e simulação |
| Mosquitto Clients | Publicar/escutar via terminal |
| Python + paho-mqtt | Simulador dos “sensores” |
| HiveMQ | Broker MQTT público |
| FlowFuse | Node-RED hospedado na nuvem |
| node-red-dashboard | UI do dashboard |

---

## 🚀 Como executar

### Pré-requisitos

- GitHub Codespace configurado
- Conta no FlowFuse com instância Node-RED ativa
- `mosquitto-clients` instalado
- `paho-mqtt` instalado

### 1. Instalar dependências no Codespace

```bash
sudo apt-get update && sudo apt-get install -y mosquitto-clients
pip install paho-mqtt
```

### 2. Iniciar o simulador Python

```bash
python simulador.py
```

O simulador envia valores aleatórios a cada 3 segundos para os tópicos de status.
Quando recebe comando no tópico `casa/sala/lampada/cmd`, ele também aplica o estado recebido (por exemplo, brilho enviado pelo dashboard).

### 3. Publicar manualmente pelo Mosquitto (opcional)

```bash
# Status da lâmpada
mosquitto_pub -h broker.hivemq.com -p 1883 \
  -t "casa/sala/lampada/status" \
  -m '{"ligada": true, "brilho": 85}'

# Comando de controle
mosquitto_pub -h broker.hivemq.com -p 1883 \
  -t "casa/sala/lampada/cmd" \
  -m '{"acao": "ligar"}'

# Ver tudo que acontece na casa
mosquitto_sub -h broker.hivemq.com -p 1883 -t "casa/sala/#"
```

### 4. Importar dashboard padrão no Node-RED

O arquivo `dashboard_padrao_flow.json` já está pronto para uso com os mesmos tópicos MQTT do projeto.

Para iniciar localmente com um comando simples:

```bash
npm run dashboard
```

No editor do Node-RED:
1. Menu ☰ → **Import**
2. Selecione `dashboard_padrao_flow.json`
3. Clique em **Import** e depois em **Deploy**

Link local do dashboard (funcionando):
- [http://127.0.0.1:1880/ui](http://127.0.0.1:1880/ui)

Editor do Node-RED:
- [http://127.0.0.1:1880](http://127.0.0.1:1880)


### 5. Testar com o Web Client do HiveMQ

Acesse `http://www.hivemq.com/demos/websocket-client/` e conecte usando:
- **Host:** `broker.hivemq.com`
- **Port:** `8884`
- **SSL:** ligado

---

## 🔄 Fluxo no Node-RED

```
[mqtt in]  →  [json]  →  [function: atualiza estado]  →  [ui_gauge]
                                                    →  [ui_text]

[ui_button +10%]  →  [function: incrementa brilho]  →  [mqtt out]
                                                     →  [ui_gauge]
                                                     →  [ui_text]
```

### Blocos utilizados

- **mqtt in** — subscreve `casa/sala/lampada/status`
- **json** — transforma o payload string em objeto
- **function (atualiza estado)** — consolida brilho/status e guarda estado atual
- **ui_gauge** — mostra brilho em gauge (0–100%)
- **ui_text** — mostra estado da lâmpada (incluindo porcentagem)
- **ui_button** — aumenta o brilho em passos de 10%
- **function (incrementa brilho)** — atualiza a UI e monta o payload do comando
- **mqtt out** — publica em `casa/sala/lampada/cmd`

---

## 📊 Como fica na prática

### Atualização do dashboard
Com o simulador rodando, o gauge de brilho e o status da lâmpada são atualizados automaticamente a cada 3 segundos.

### Envio de comando
Quando você clica em **"Aumentar brilho (+10%)"** no dashboard, o brilho sobe 10% na interface (até o limite de 100%) e o Node-RED publica um comando como `{"acao": "ligar", "brilho": 90}` em `casa/sala/lampada/cmd`. A outra ponta pode ser observada via `mosquitto_sub` (no Codespace) ou pelo próprio simulador Python.

### Duas formas de alimentar o sistema
- **Via Codespace (Mosquitto):** usar `mosquitto_pub` direto no terminal
- **Via HiveMQ Web Client:** interface web publicando no mesmo tópico

---

## 📁 Arquivos

```
/
├── simulador.py       # Simulador de sensores em Python
├── dashboard_padrao_flow.json  # Fluxo pronto para importar no Node-RED
└── README.md                  # Documentação do projeto
```

---

## 👤 Autor

Lucas Valente, RA: 1965387
João Pedro Koga, RA: 1977891