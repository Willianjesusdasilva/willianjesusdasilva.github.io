{
"nome": "ECU Suplementar Universal com ESP32",
"tags": [
"automotivo",
"esp32",
"ecu",
"piggyback",
"injecao",
"boost",
"lambda",
"can",
"kline",
"eletronica"
],
"status": "ideia"
}

ECU Suplementar Universal com ESP32

1. Visão geral

A proposta consiste no desenvolvimento de uma ECU suplementar universal baseada em ESP32, destinada a adicionar novas funções de controle a motores que continuam utilizando sua ECU original.

O objetivo não é inicialmente substituir a ECU OEM.

A ECU original permanece responsável pelas funções essenciais do motor:

sincronismo;

ignição;

injeção principal;

marcha lenta;

partida;

controle de temperatura;

comunicação com outros módulos;

estratégias de proteção originais.

O módulo ESP32 funciona paralelamente à ECU original, recebendo informações sobre o funcionamento do motor e controlando dispositivos adicionais.

A arquitetura conceitual é:

                   MOTOR
                     │
        ┌────────────┼─────────────┐
        │            │             │
       RPM          MAP           TPS
        │            │             │
        └────────────┼─────────────┘
                     │
                     ▼
              ┌────────────┐
              │   ESP32    │
              │            │
              │ ECU AUX.   │
              └──────┬─────┘
                     │
          ┌──────────┼───────────┐
          │          │           │
          ▼          ▼           ▼
       INJETOR     BOOST      SISTEMAS
      AUXILIAR     CONTROL     AUXILIARES

2. Motivação

Veículos modificados frequentemente atingem um ponto no qual a ECU original continua funcionando adequadamente, mas passa a limitar determinadas modificações.

Alguns exemplos:

necessidade de combustível adicional;

controle de pressão de turbo;

injeção de água/metanol;

leitura de wideband;

controle de dispositivos auxiliares;

datalog;

estratégias de proteção adicionais.

Uma ECU standalone pode resolver esses problemas, porém normalmente envolve:

custo elevado;

novo chicote;

nova calibração completa;

perda de algumas funções OEM;

dificuldade de integração com câmbio automático;

integração com painel e outros módulos.

A proposta é criar uma camada intermediária.

ECU ORIGINAL
     +
ECU SUPLEMENTAR

A ECU suplementar adiciona recursos sem assumir inicialmente o controle completo do motor.

3. Objetivo principal

Criar uma plataforma eletrônica universal capaz de:

observar o funcionamento do motor;

processar sensores em tempo real;

aplicar mapas configuráveis;

controlar dispositivos adicionais;

registrar dados;

aplicar estratégias de proteção;

comunicar-se com computador ou celular.

A plataforma deve ser adaptável a diferentes veículos.

4. Unidade de processamento

O controlador inicial proposto é o ESP32.

Características interessantes para a aplicação:

processamento rápido;

múltiplos timers;

ADC;

PWM;

interrupções;

SPI;

I²C;

UART;

Wi-Fi;

Bluetooth;

baixo custo;

grande disponibilidade.

O ESP32 não seria conectado diretamente aos atuadores automotivos.

Entre o microcontrolador e o veículo existiria uma camada eletrônica de condicionamento e potência.

VEÍCULO
   │
   ▼
PROTEÇÃO / CONDICIONAMENTO
   │
   ▼
ESP32
   │
   ▼
DRIVERS DE POTÊNCIA
   │
   ▼
ATUADORES

5. Entradas previstas

5.1 RPM

O RPM é uma das principais referências do sistema.

Possíveis fontes:

sinal de rotação;

bobina;

sensor de comando;

sensor de virabrequim;

sinal fornecido pela ECU;

CAN;

K-Line, quando a latência permitir.

O sinal deve passar por condicionamento elétrico antes de chegar ao ESP32.

5.2 MAP / pressão de turbo

Um sensor MAP dedicado pode permitir que a ECU suplementar conheça pressão atmosférica, vácuo, pressão positiva e evolução do boost.

MAP
 │
 ▼
0 – 5 V
 │
 ▼
condicionamento
 │
 ▼
ADC
 │
 ▼
ESP32

A pressão pode ser utilizada como eixo de mapas e também como mecanismo de proteção.

5.3 TPS

A posição do acelerador permite identificar a solicitação do motorista.

RPM > limite
AND
TPS > limite
AND
MAP > limite

→ habilitar estratégia

5.4 Wideband

Uma entrada para sonda wideband externa permitiria monitorar a mistura do motor.

Wideband
   │
   │ saída analógica
   ▼
0 – 5 V
   │
   ▼
ESP32
   │
   ▼
Lambda

A leitura de lambda seria particularmente importante para estratégias de proteção.

5.5 Temperaturas

Entradas adicionais poderiam monitorar:

temperatura do líquido de arrefecimento;

temperatura do ar de admissão;

temperatura do óleo;

temperatura do combustível;

EGT.

6. Controle de injetor suplementar

Uma das primeiras aplicações práticas da ECU seria controlar um ou mais injetores adicionais.

ESP32
  │
  │ comando
  ▼
DRIVER
  │
  ▼
INJETOR

O ESP32 não deve alimentar diretamente o injetor.

O estágio de potência deve ser projetado de acordo com o tipo de injetor utilizado.

6.1 Injetores de alta impedância

Para injetores de alta impedância, o estágio de saída pode utilizar um driver automotivo apropriado ou estágio de potência equivalente.

O ESP32 determina:

momento de acionamento;

frequência;

duty cycle;

tempo de abertura.

6.2 Injetores de baixa impedância

Uma possível evolução do projeto seria implementar controle Peak & Hold.

ABERTURA
   │
   ▼
corrente elevada
   │
   ▼
injetor abre rapidamente
   │
   ▼
corrente reduzida
   │
   ▼
injetor permanece aberto

7. Estratégia de combustível

A quantidade de combustível suplementar poderia ser definida por mapas.

Uma primeira versão poderia utilizar:

RPM × MAP

RPM

0.5 bar

1.0 bar

1.5 bar

2500

0%

5%

10%

3500

3%

10%

20%

4500

5%

15%

30%

5500

8%

20%

40%

6500

10%

25%

50%

Os valores representam apenas uma estrutura conceitual de mapa.

A calibração real dependeria do motor, combustível, injetor e preparação utilizados.

8. Correção por lambda

Uma evolução posterior seria permitir correções baseadas na leitura da wideband.

Lambda alvo
     │
     ├─────────────┐
     │             │
     ▼             ▼
Lambda medida    diferença
                   │
                   ▼
             correção limitada
                   │
                   ▼
             combustível
             suplementar

O sistema poderia realizar pequenas correções dentro de limites definidos.

9. Controle de boost

Outra função possível é controlar uma válvula de boost.

ESP32
  │
 PWM
  │
  ▼
DRIVER
  │
  ▼
SOLENOIDE
  │
  ▼
WASTEGATE

Isso permitiria substituir um controlador puramente mecânico por controle eletrônico configurável.

O boost poderia depender de:

RPM × TPS;

RPM × marcha;

RPM × velocidade.

Isso permitiria estratégias como menos pressão em primeira marcha, aumento progressivo de pressão, boost diferente por marcha e redução automática de pressão em condição insegura.

10. Controle de água/metanol

Uma saída adicional poderia controlar um sistema de injeção de água/metanol.

Possíveis variáveis:

MAP;

RPM;

TPS;

temperatura do ar;

lambda.

MAP > X
AND
RPM > Y
AND
TPS > Z

→ habilita água/metanol

O sistema também poderia monitorar nível do reservatório, pressão da linha e corrente da bomba.

11. Estratégias de proteção

Uma das principais vantagens da ECU suplementar seria funcionar também como um módulo independente de proteção.

Possíveis proteções incluem mistura pobre, pressão excessiva, temperatura elevada e falha da wideband.

Exemplo:

boost alto
+
lambda acima do limite
+
tempo > tolerância

→ proteção

Os níveis de resposta poderiam incluir:

aviso;

redução de boost;

desativação do combustível suplementar;

estado de failsafe.

A estratégia exata dependeria da aplicação e deveria evitar criar uma condição mais perigosa do que a falha original.

12. Comunicação CAN

Uma evolução importante seria adicionar transceiver CAN.

CAN-H ─┐
       ├─ CAN TRANSCEIVER ─ ESP32
CAN-L ─┘

Isso permitiria obter dados disponíveis na rede do veículo sem instalar sensores duplicados.

Exemplos:

RPM;

TPS;

temperatura;

velocidade;

marcha;

torque solicitado.

13. Comunicação K-Line

Para veículos mais antigos, uma interface K-Line também poderia ser implementada.

K-Line
   │
   ▼
Transceiver
   │
   ▼
UART
   │
   ▼
ESP32

A K-Line seria particularmente interessante para diagnóstico, telemetria e aquisição de parâmetros de baixa frequência.

14. Wi-Fi e interface Web

O Wi-Fi integrado do ESP32 permitiria criar uma interface de configuração sem cabos.

ESP32
  │
Wi-Fi
  │
  ▼
Browser

Possíveis telas:

Dashboard
Maps
Sensors
Outputs
Protections
Logs
Configuration

O dashboard poderia apresentar RPM, MAP, TPS, lambda, duty do injetor, boost target, temperaturas e estado das proteções.

15. Bluetooth

Bluetooth poderia ser utilizado para configuração, telemetria, aplicativo móvel e diagnóstico.

16. Datalog

O sistema deveria possuir capacidade de registrar dados.

timestamp
rpm
map
tps
lambda
iat
ect
injector_duty
boost_target
boost_actual
protection_state

Os logs poderiam ser armazenados em memória, cartão SD ou enviados via Wi-Fi.

17. Arquitetura modular

A proposta deve evitar que a ECU fique presa a um único veículo.

┌──────────────────────────┐
│         ESP32            │
├──────────────────────────┤
│ Core                     │
│ Maps                     │
│ Protections              │
│ Datalog                  │
├──────────────────────────┤
│ Inputs                   │
│ Outputs                  │
│ CAN                      │
│ K-Line                   │
│ Wi-Fi                    │
└──────────────────────────┘

As particularidades de cada veículo poderiam ficar em configurações separadas.

18. Hardware modular

Também seria possível separar fisicamente algumas funções.

MAIN BOARD
    │
    ├── Sensor Board
    ├── Injector Driver
    ├── Boost Driver
    ├── CAN
    └── K-Line

Isso permitiria construir versões diferentes utilizando o mesmo firmware base.

19. Alimentação automotiva

O ambiente elétrico automotivo não deve ser tratado como uma fonte de 12 V ideal.

O módulo precisa considerar:

inversão de polaridade;

transientes;

ruído elétrico;

variação de tensão;

queda de tensão durante partida;

interferência produzida por bobinas e injetores.

12–14 V veículo
      │
      ▼
proteções
      │
      ▼
filtro
      │
      ▼
regulador
      │
      ▼
5 V / 3.3 V
      │
      ▼
ESP32

20. Isolamento entre lógica e potência

A placa deve separar claramente sinais e potência.

ESP32
   │
   ▼
DRIVER
   │
   ▼
MOSFET / DRIVER AUTOMOTIVO
   │
   ▼
ATUADOR

21. Primeira versão mínima

O MVP poderia possuir:

Entradas

RPM;

MAP;

TPS;

wideband.

Saídas

1 injetor suplementar;

1 saída PWM para boost.

Comunicação

Wi-Fi.

Software

mapa RPM × MAP;

datalog;

limites de segurança.

             RPM
              │
MAP ──────────┤
              │
TPS ───────► ESP32
              │
Wideband ─────┤
              │
         ┌────┴────┐
         │         │
         ▼         ▼
      Injector   Boost
       Driver    Driver

22. Segunda versão

Posteriormente poderiam ser adicionados:

CAN;

K-Line;

cartão SD;

múltiplos injetores;

controle Peak & Hold;

EGT;

água/metanol;

múltiplos mapas;

boost por marcha;

correção por lambda;

aplicativo móvel.

23. Possível evolução para ECU completa

A arquitetura também poderia servir como plataforma de aprendizado para uma ECU mais completa.

ECU suplementar
       │
       ▼
controle combustível
       │
       ▼
controle boost
       │
       ▼
aquisição avançada
       │
       ▼
controle ignição
       │
       ▼
sincronismo crank/cam
       │
       ▼
ECU standalone

Entretanto, o objetivo inicial deve permanecer limitado:

adicionar funcionalidades sem substituir a ECU original.

24. Princípio de projeto

A ECU OEM continua fazendo aquilo que já faz bem, enquanto o módulo ESP32 adiciona apenas as funções necessárias para a preparação.

Isso reduz a necessidade de reproduzir imediatamente toda a complexidade de uma ECU automotiva moderna.

25. Possíveis aplicações

A plataforma poderia ser utilizada em:

motores turbo antigos;

projetos turbo;

veículos com ECU difícil de modificar;

projetos experimentais;

aquisição de dados;

sistemas auxiliares de combustível;

gerenciamento eletrônico de boost.

26. Objetivo de longo prazo

O objetivo final seria criar uma plataforma aberta, barata, modular e configurável, situada conceitualmente entre um controlador auxiliar simples e uma ECU standalone.

A plataforma poderia assumir somente as funções que cada projeto necessita.

27. Resumo

A proposta da ECU Suplementar Universal com ESP32 consiste em utilizar um microcontrolador moderno para adicionar recursos de gerenciamento eletrônico a veículos que continuam utilizando sua ECU original.

             VEÍCULO
                │
                ▼
             SENSORES
                │
                ▼
        CONDICIONAMENTO
                │
                ▼
          ┌───────────┐
          │   ESP32   │
          └─────┬─────┘
                │
      ┌─────────┼──────────┐
      │         │          │
      ▼         ▼          ▼
 Combustível   Boost    Auxiliares
      │         │          │
      └─────────┼──────────┘
                │
                ▼
              MOTOR

Com comunicação adicional:

           ESP32
        ┌────┼────┐
        │    │    │
       CAN K-Line Wi-Fi
                  │
                  ▼
            Web / Celular

A primeira meta seria construir uma versão mínima capaz de:

ler RPM + MAP + TPS + lambda → consultar mapas → controlar injeção suplementar → registrar dados → executar proteções.

A partir dessa base, novas funções poderiam ser adicionadas de forma modular.