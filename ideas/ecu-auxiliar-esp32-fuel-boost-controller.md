{
  "nome": "ECU Auxiliar ESP32 — Fuel & Boost Controller",
  "tags": [
    "automotivo",
    "esp32",
    "ecu",
    "piggyback",
    "injecao-suplementar",
    "boost-control",
    "mac-3-vias",
    "nanopro",
    "wideband",
    "me3.8",
    "1.8t"
  ],
  "status": "ideia"
}

# ECU Auxiliar ESP32 — Fuel & Boost Controller

## 1. Visão geral

O projeto propõe uma ECU auxiliar baseada em ESP32 para atuar em paralelo com a ECU original do veículo, sem substituí-la.

A ECU OEM permanece responsável pelo funcionamento normal do motor, enquanto o ESP32 assume duas funções suplementares:

1. controle de combustível adicional por meio de um injetor High-Z de aproximadamente 100 lb/h;
2. controle eletrônico de boost por meio de uma válvula MAC 3 vias.

O sistema utiliza a leitura de lambda fornecida por uma FuelTech Nano PRO e permite selecionar a pressão-alvo pelo celular através de uma interface Wi-Fi.

A arquitetura conceitual é:

```text
                         A3 / ME3.8
                             │
                      continua original
                             │
                 ┌───────────┴───────────┐
                 │                       │
          4 bicos originais          ignição etc.


                    SISTEMA AUXILIAR

MAP ─────────────┐
RPM ─────────────┤
TPS ─────────────┼────────────► ESP32
Nano PRO λ ──────┘                │
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             CONTROLE COMBUSTÍVEL        CONTROLE BOOST
                    │                           │
               mapa RPM×MAP                boost target
                    │                           │
               lambda trim                 closed-loop
                    │                           │
                    ▼                           ▼
            DRIVER INJETOR                DRIVER PWM
                    │                           │
                    ▼                           ▼
              BICO ~100 lb                  MAC 3 VIAS
                                                │
                                                ▼
                                             WASTEGATE
```

---

# 2. Objetivo

O objetivo é criar uma plataforma auxiliar capaz de ampliar a capacidade de preparação de um motor turbo sem substituir a ECU OEM.

A ECU original continua responsável por:

- sincronismo;
- ignição;
- injeção principal;
- marcha lenta;
- partida;
- estratégias OEM;
- integração com câmbio e painel.

O ESP32 acrescenta:

- combustível suplementar;
- correção limitada por lambda;
- controle eletrônico de boost;
- seleção de pressão pelo celular;
- datalog;
- failsafes.

---

# 3. Combustível suplementar

A primeira versão utiliza um único injetor High-Z de aproximadamente 100 lb/h.

O injetor atua como quinto bico e fornece apenas o combustível adicional necessário sob alta carga.

```text
ESP32
  │
  ▼
driver
  │
  ▼
injetor ~100 lb/h
  │
  ▼
admissão
```

O ESP32 não deve alimentar diretamente o injetor.

---

# 4. Estratégia base de combustível

A quantidade de combustível suplementar é definida por um mapa principal baseado em:

```text
RPM × MAP
```

O mapa fornece o pulso-base do injetor auxiliar.

Exemplo conceitual:

| RPM | 0.5 bar | 0.8 bar | 1.0 bar | 1.2 bar | 1.5 bar |
|---:|---:|---:|---:|---:|---:|
| 2500 | 0 | 0 | 0 | 0 | 0 |
| 3000 | 0 | 0 | 5 | 8 | 10 |
| 3500 | 0 | 5 | 8 | 12 | 15 |
| 4000 | 0 | 8 | 12 | 16 | 20 |
| 4500 | 0 | 10 | 15 | 20 | 25 |
| 5000 | 0 | 12 | 18 | 24 | 30 |
| 5500 | 0 | 15 | 20 | 28 | 35 |
| 6000 | 0 | 15 | 22 | 30 | 40 |

Os valores são apenas ilustrativos.

---

# 5. Lambda pela Nano PRO

A FuelTech Nano PRO continua sendo responsável pela leitura e controle da sonda wideband.

O ESP32 recebe apenas a saída correspondente à lambda.

```text
Sonda wideband
      │
      ▼
 FuelTech Nano PRO
      │
      ▼
 saída de lambda
      │
      ▼
 condicionamento
      │
      ▼
    ESP32
```

---

# 6. Correção por lambda

A lambda não substitui o mapa-base.

O controle é dividido em:

```text
MAPA BASE
    +
TRIM DE LAMBDA
```

Arquitetura:

```text
RPM + MAP
    │
    ▼
pulso base
    │
    ├───────────────┐
    │               │
    │          lambda medida
    │               │
    │               ▼
    │          correção limitada
    │               │
    └───────┬───────┘
            ▼
       pulso final
            │
            ▼
         injetor
```

A correção deve possuir limites configuráveis para impedir que uma leitura incorreta tenha autoridade total sobre o combustível.

---

# 7. TPS

O TPS funciona como condição adicional de habilitação.

Exemplo:

```text
RPM > mínimo
AND
MAP > mínimo
AND
TPS > mínimo

→ combustível suplementar habilitado
```

---

# 8. Controle eletrônico de boost

O ESP32 também controla uma válvula MAC 3 vias instalada no circuito da wastegate.

Arquitetura:

```text
ESP32
  │
 PWM
  │
  ▼
driver
  │
  ▼
MAC 3 vias
  │
  ▼
wastegate
```

A pressão de base continua sendo determinada mecanicamente pela mola da wastegate.

O controle eletrônico atua somente acima desse nível.

---

# 9. Boost target

O usuário não precisa configurar diretamente o duty-cycle da MAC durante o uso normal.

A interface trabalha com uma pressão-alvo.

Exemplo:

```text
BOOST TARGET

0.8 bar
1.0 bar
1.2 bar
1.5 bar
```

O ESP32 converte o target em atuação da MAC.

---

# 10. Seleção pelo celular

O ESP32 cria uma interface Web acessível por Wi-Fi.

```text
ESP32
  │
 Wi-Fi
  │
  ▼
celular / notebook
  │
  ▼
browser
```

A tela principal pode apresentar:

```text
RPM
Boost atual
Boost target
Lambda atual
Lambda alvo
TPS
Duty do injetor
Duty da MAC
Status do sistema
```

E também botões de modo:

```text
[ 0.8 BAR ]
[ 1.0 BAR ]
[ 1.2 BAR ]
[ 1.5 BAR ]
```

---

# 11. Modos configuráveis

Em vez de somente valores numéricos, o usuário pode definir perfis.

Exemplo:

```text
BASE       0.6 bar
RUA        0.8 bar
SPORT      1.0 bar
RACE       1.2 bar
FULL       1.5 bar
```

Cada modo pode armazenar também:

- boost target;
- limite de RPM;
- limite de lambda;
- combustível suplementar máximo;
- agressividade do closed-loop;
- limite de duty da MAC.

---

# 12. Closed-loop de boost

O controle compara:

```text
boost target
versus
boost atual
```

Arquitetura:

```text
Boost target
     │
     ▼
 controlador
     │
     ▼
 duty MAC
     │
     ▼
 wastegate
     │
     ▼
 turbo
     │
     ▼
 MAP
     │
     └────────► feedback
```

O duty da MAC é ajustado continuamente para aproximar a pressão medida da pressão-alvo.

---

# 13. Controle base + correção

Assim como no combustível, o boost pode trabalhar em duas camadas:

```text
MAPA BASE DE DUTY
       +
CORREÇÃO CLOSED-LOOP
```

Isso evita exigir que o algoritmo de feedback faça todo o trabalho sozinho.

---

# 14. Mapa base da MAC

Pode existir uma tabela:

```text
RPM × boost target → duty base
```

Exemplo conceitual:

| RPM | 0.8 bar | 1.0 bar | 1.2 bar | 1.5 bar |
|---:|---:|---:|---:|---:|
| 2500 | 15 | 20 | 25 | 30 |
| 3000 | 20 | 25 | 30 | 35 |
| 3500 | 25 | 30 | 35 | 40 |
| 4000 | 28 | 35 | 40 | 45 |
| 4500 | 30 | 38 | 45 | 50 |
| 5000 | 30 | 40 | 48 | 55 |
| 5500 | 30 | 40 | 50 | 58 |
| 6000 | 28 | 38 | 48 | 55 |

Os números são exclusivamente ilustrativos.

---

# 15. Integração entre boost e combustível

Boost e combustível não devem ser tratados como sistemas totalmente independentes.

Quando a pressão aumenta:

```text
MAP ↑
```

automaticamente:

```text
combustível suplementar ↑
```

O ESP32 conhece simultaneamente:

- pressão atual;
- pressão-alvo;
- lambda;
- combustível suplementar;
- duty da MAC.

Isso permite criar estratégias coordenadas.

---

# 16. Proteção por mistura pobre

Se o motor estiver sob alta carga e a lambda ultrapassar o limite permitido:

```text
BOOST alto
+
lambda pobre
+
tempo > tolerância

→ proteção
```

A reação pode ser progressiva.

### Estágio 1

```text
warning
```

### Estágio 2

```text
reduzir boost target
```

### Estágio 3

```text
MAC → failsafe
```

A wastegate então retorna à condição mecânica definida pela mola.

---

# 17. Proteção de overboost

Se:

```text
MAP > limite absoluto
```

o ESP32 deve reduzir imediatamente a autoridade da MAC.

Conceitualmente:

```text
OVERBOOST
   │
   ▼
MAC → estado seguro
   │
   ▼
pressão retorna em direção
à mola da wastegate
```

---

# 18. Failsafe da MAC

O sistema deve ser projetado de forma que a perda de controle eletrônico resulte na condição mais conservadora possível.

O conceito é:

```text
ESP32 desligado
ou
driver desligado
ou
failsafe ativo
        │
        ▼
MAC sem comando
        │
        ▼
wastegate opera pela mola
```

A pressão mecânica da mola funciona como boost-base.

---

# 19. Fail-safe de lambda

Se a leitura da Nano PRO for inválida:

```text
LAMBDA ERROR
      │
      ▼
closed-loop de combustível OFF
      │
      ▼
boost target limitado
      │
      ▼
modo seguro
```

Uma falha de wideband não deve permitir a continuação automática no modo de maior pressão.

---

# 20. Fail-safe de MAP

Se o MAP apresentar falha:

```text
MAP inválido
     │
     ▼
boost control OFF
     │
     ▼
MAC estado seguro
```

Como o MAP também é utilizado pelo mapa de combustível suplementar, o sistema deve desabilitar ou limitar a suplementação de acordo com a estratégia de segurança definida.

---

# 21. Limite de duty do injetor

O ESP32 deve acompanhar o duty-cycle do injetor auxiliar.

Exemplo:

```text
duty < warning
→ normal

duty > warning
→ alerta

duty > limite
→ limitar boost
```

Isso permite impedir que o turbo continue aumentando a demanda de combustível quando o quinto bico já estiver próximo da capacidade definida.

---

# 22. Integração de proteção

Uma vantagem importante de controlar combustível e boost no mesmo processador é poder criar uma relação direta:

```text
combustível insuficiente
          │
          ▼
       boost ↓
```

Em vez de simplesmente registrar uma condição perigosa.

---

# 23. Máquina de estados

O firmware pode possuir:

```text
OFF
 │
 ▼
ARMED
 │
 ▼
ACTIVE
 │
 ├──► WARNING
 │
 ├──► DERATE
 │
 └──► FAILSAFE
```

### OFF

Sistema desativado.

### ARMED

Sensores válidos e aguardando carga.

### ACTIVE

Controle de combustível e boost ativo.

### WARNING

Alguma variável próxima do limite.

### DERATE

Pressão-alvo reduzida automaticamente.

### FAILSAFE

MAC vai para estado seguro e estratégias suplementares são limitadas ou interrompidas.

---

# 24. Dashboard mobile

Exemplo conceitual:

```text
┌─────────────────────────────┐
│      ESP32 AUX ECU          │
│                             │
│ RPM          5840           │
│ Boost        1.31 bar       │
│ Target       1.50 bar       │
│ Lambda       0.80           │
│ Lambda alvo  0.80           │
│ TPS          100%           │
│ Aux Injector 37%            │
│ MAC Duty     61%            │
│                             │
│ BOOST MODE                  │
│                             │
│ [0.8] [1.0] [1.2] [1.5]    │
│                             │
│ Status: ACTIVE              │
└─────────────────────────────┘
```

---

# 25. Configuração avançada

A interface Web também pode permitir:

```text
Fuel Map
Boost Map
Lambda Target
Boost Target
MAP calibration
TPS calibration
RPM input
Injector calibration
MAC frequency
MAC base duty
Safety limits
Datalog
```

---

# 26. Datalog

O sistema deve registrar:

```text
timestamp
rpm
map
boost_target
boost_error
mac_duty
tps
lambda
lambda_target
lambda_error
injector_base
lambda_trim
injector_final
injector_duty
system_state
selected_mode
```

Isso permite reconstruir o comportamento de uma puxada.

---

# 27. Hardware mínimo

A primeira versão da ECU auxiliar necessita de:

```text
ESP32
sensor MAP
entrada RPM
entrada TPS
entrada Nano PRO
driver para injetor High-Z
driver para MAC 3 vias
alimentação automotiva
proteções elétricas
```

---

# 28. Entradas

```text
INPUT 1 → RPM
INPUT 2 → MAP
INPUT 3 → TPS
INPUT 4 → Nano PRO lambda
```

Possíveis expansões:

```text
INPUT 5 → IAT
INPUT 6 → pressão de combustível
INPUT 7 → temperatura combustível
INPUT 8 → botão físico de emergência
```

---

# 29. Saídas

Primeira versão:

```text
OUTPUT 1 → injetor auxiliar ~100 lb/h
OUTPUT 2 → MAC 3 vias
```

Possíveis expansões:

```text
OUTPUT 3 → água/metanol
OUTPUT 4 → bomba auxiliar
OUTPUT 5 → LED / buzzer
OUTPUT 6 → relé failsafe
```

---

# 30. Pressão de combustível

Uma evolução importante é adicionar sensor de pressão de combustível.

Isso permitiria comparar:

```text
pressão combustível
versus
pressão coletor
```

e calcular pressão diferencial real sobre o injetor.

O sistema poderia então detectar:

```text
fuel pressure drop
```

e automaticamente reduzir boost.

---

# 31. Controle baseado em pressão diferencial

Com sensor de combustível:

```text
ΔP injector =
fuel pressure - manifold pressure
```

O ESP32 pode utilizar essa informação para corrigir o cálculo de vazão do injetor auxiliar.

---

# 32. Limitação do quinto bico

A maior limitação física da primeira arquitetura continua sendo a distribuição de combustível entre os cilindros.

Um único injetor fornece a vazão total, mas não mede a parcela que cada cilindro recebe.

```text
lambda geral correta
≠
lambda individual necessariamente correta
```

A posição e direção do injetor suplementar devem ser estudadas com atenção.

---

# 33. Evolução para port injection

Caso a distribuição do único bico se torne limitante:

```text
ESP32
 │
 ├── injector 1
 ├── injector 2
 ├── injector 3
 └── injector 4
```

O restante da plataforma pode ser mantido:

- Nano PRO;
- boost control;
- MAC;
- mapas;
- Wi-Fi;
- dashboard;
- datalog;
- failsafes.

---

# 34. Roadmap

## V0 — Bancada

Validar:

```text
ESP32
+
driver de injetor
+
driver MAC
+
MAP simulado
+
RPM simulado
+
lambda simulada
```

---

## V1 — Fuel Controller

Instalar no veículo:

```text
ESP32
+
MAP
+
RPM
+
TPS
+
Nano PRO
+
1 × injetor ~100 lb/h
```

---

## V2 — Boost Controller

Adicionar:

```text
MAC 3 vias
+
driver PWM
+
boost target
+
seleção pelo celular
```

---

## V3 — Closed-loop e safety

Adicionar:

```text
lambda trim
boost closed-loop
overboost
lean protection
sensor failure
derate automático
```

---

## V4 — Pressão de combustível

Adicionar sensor e proteção por pressão diferencial.

---

## V5 — Port Injection

Evoluir de um único bico suplementar para quatro canais individuais.

---

# 35. Arquitetura final pretendida

```text
                         NANO PRO
                             │
                             │ lambda
                             ▼
MAP ──────────┐         ┌───────────┐
RPM ──────────┼────────►│           │
TPS ──────────┤         │   ESP32   │
Fuel P ───────┘         │  AUX ECU  │
                       └─────┬─────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
           FUEL CONTROL              BOOST CONTROL
                │                         │
                ▼                         ▼
         injector ~100 lb             MAC 3 vias
                │                         │
                ▼                         ▼
              motor                   wastegate
                │                         │
                └──────────┬──────────────┘
                           ▼
                        resposta
                           │
                           ▼
                        sensores
```

---

# 36. Princípio central

A filosofia final do sistema é:

> A ME3.8 permanece responsável por operar o motor. O ESP32 adiciona combustível e controla a pressão de turbo como uma camada suplementar independente, monitorada pela wideband e protegida por estratégias próprias de failsafe.

Isso cria uma plataforma intermediária entre um controlador simples de quinto bico e uma ECU standalone.

---

# 37. Resumo

A ECU auxiliar será composta inicialmente por:

```text
ME3.8 ORIGINAL
       │
       └────► motor OEM


                 +

Nano PRO ────────┐
MAP ─────────────┤
RPM ─────────────┼────► ESP32 AUX ECU
TPS ─────────────┘          │
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
              FUEL                  BOOST
                 │                     │
          driver High-Z           driver PWM
                 │                     │
                 ▼                     ▼
          bico ~100 lb            MAC 3 vias
                 │                     │
                 └──────────┬──────────┘
                            ▼
                          MOTOR
```

O usuário poderá selecionar a pressão de turbo pelo celular, enquanto o ESP32 gerencia:

- boost target;
- duty da MAC;
- combustível suplementar;
- correção por lambda;
- overboost;
- proteção por mistura pobre;
- redução automática de pressão;
- datalog;
- failsafe.

A primeira versão mantém a ECU original intacta e utiliza a eletrônica auxiliar apenas onde a preparação necessita de capacidade adicional.
