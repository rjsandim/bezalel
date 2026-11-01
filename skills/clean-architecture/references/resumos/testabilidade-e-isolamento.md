# Testabilidade e isolamento de infraestrutura

[Voltar ao mapa de fontes](../fontes.md)

Cópias dos resumos selecionados de *Clean Architecture*, em português. Os números indicam a posição física das páginas no PDF de origem. Os textos abaixo estão incluídos integralmente nesta skill.

Leia apenas a página ou exemplo relevante. Busque pelo título ou por `Página NNNN` para localizar um trecho.

## Conteúdo

- [Página 0167 — O objeto humilde separa o difícil de testar](#pagina-0167)
- [Página 0168 — O apresentador prepara tudo para uma visualização simples](#pagina-0168)
- [Página 0169 — Objetos humildes no banco e nas interfaces de serviço](#pagina-0169)
- [Página 0192 — Testes são componentes externos da arquitetura](#pagina-0192)
- [Página 0193 — Testabilidade evita testes frágeis e rigidez](#pagina-0193)
- [Página 0194 — A API de testes protege a evolução estrutural](#pagina-0194)
- [Página 0200 — Misturar software e firmware torna mudanças perigosas](#pagina-0200)
- [Página 0201 — A HAL define serviços na linguagem da aplicação](#pagina-0201)
- [Página 0202 — Abstrações da aplicação escondem detalhes do processador](#pagina-0202)
- [Página 0203 — Tipos padronizados preservam portabilidade](#pagina-0203)
- [Página 0205 — A OSAL protege a aplicação do sistema operacional](#pagina-0205)
- [Página 0206 — Interfaces tornam camadas substituíveis e testáveis](#pagina-0206)
- [Página 0207 — Esconder variações de hardware evita condicionais repetidas](#pagina-0207)

<a id="pagina-0167"></a>

## Página 0167 — O objeto humilde separa o difícil de testar

O capítulo 23 apresenta o padrão Humble Object como meio de reconhecer e proteger fronteiras arquiteturais. Sua técnica divide comportamentos em dois módulos: um conserva a parte difícil de testar, reduzida ao essencial; outro reúne a lógica que pode ser testada facilmente. Interfaces gráficas ilustram o problema, pois verificar a tela diretamente é complicado, embora boa parte de seu comportamento seja simples de validar. A solução introduzida divide essas responsabilidades entre Presenter e View. O texto relaciona esse padrão aos apresentadores usados na arquitetura limpa do capítulo anterior.

---

<a id="pagina-0168"></a>

## Página 0168 — O apresentador prepara tudo para uma visualização simples

A View é o objeto humilde: transfere informações para a interface sem processá-las. O Presenter, testável, formata datas, moedas, tabelas e rótulos e preenche um ViewModel com textos, booleanos e enumerações. Indicadores como valor negativo em vermelho ou botão desabilitado também ficam prontos nesse modelo. Essa divisão evidencia como testabilidade pode orientar fronteiras arquiteturais. A página introduz ainda gateways de banco entre interactors e persistência: interfaces polimórficas oferecem operações adequadas às necessidades da aplicação, como obter sobrenomes de usuários que acessaram após uma data, sem expor SQL ao caso de uso.

---

<a id="pagina-0169"></a>

## Página 0169 — Objetos humildes no banco e nas interfaces de serviço

A implementação de um gateway usa SQL ou outro mecanismo para obter os dados exigidos, funcionando como objeto humilde. Os interactors preservam a lógica de aplicação e podem ser testados com substitutos desses gateways. O autor argumenta que ORMs seriam mais precisamente mapeadores de dados, pois conectam tabelas a estruturas de dados, e os situa na camada do banco. O padrão também aparece nos serviços: adaptadores convertem estruturas simples em mensagens externas, e listeners fazem a conversão inversa. A conclusão associa fronteiras, dados simples e separação entre comportamentos fáceis e difíceis de testar.

---

<a id="pagina-0192"></a>

## Página 0192 — Testes são componentes externos da arquitetura

O capítulo 28 afirma que testes pertencem ao sistema e participam de sua arquitetura. Em vez de discutir classificações como unitário, integração, aceitação ou BDD, considera que todos têm posição arquitetural equivalente. São elementos concretos e detalhados cujas dependências apontam para o código testado. Por isso, podem ser entendidos como o círculo mais externo: nenhum componente de produção deve depender deles, enquanto eles dependem dos componentes internos. Essa perspectiva vale tanto para pequenos testes de TDD quanto para suítes maiores construídas com ferramentas de aceitação.

---

<a id="pagina-0193"></a>

## Página 0193 — Testabilidade evita testes frágeis e rigidez

Testes costumam ser implantados separadamente e apoiam o desenvolvimento, não a operação, mas continuam exigindo desenho arquitetural. Quando se acoplam fortemente ao sistema, mudanças pequenas podem quebrar centenas de verificações e desencorajar melhorias. O exemplo são testes de regras de negócio que navegam pela interface: alterações no login ou na sequência de páginas afetam muitos deles. A orientação é não depender de elementos voláteis e permitir testar regras sem a interface gráfica. Uma API de testes específica pode evitar recursos caros, contornar restrições próprias do uso normal e colocar o sistema em estados adequados à verificação.

---

<a id="pagina-0194"></a>

## Página 0194 — A API de testes protege a evolução estrutural

A API de testes deve separar a estrutura da suíte da estrutura da aplicação. Manter uma classe de teste para cada classe de produção e métodos espelhados pode criar forte acoplamento, tornando refatorações custosas. O isolamento permite que testes fiquem mais concretos e específicos enquanto o código de produção se torna mais abstrato e geral. Como a API pode oferecer capacidades especiais, suas partes perigosas devem ficar em componente implantável separado quando houver risco de exposição em produção. A conclusão reforça que testes mal integrados ao desenho tornam-se frágeis, difíceis de manter e sujeitos ao abandono.

---

<a id="pagina-0200"></a>

## Página 0200 — Misturar software e firmware torna mudanças perigosas

A figura 29.1 apresenta três camadas: software, firmware e hardware. A fronteira física entre código e equipamento é evidente, mas não impede que conhecimento do hardware se espalhe por toda a aplicação, como sugere a figura 29.2. Sem controle sobre o que cada módulo pode conhecer, mudanças de requisitos, correções e trocas de equipamento tornam-se difíceis. A mistura de software e firmware é tratada como antipadrão: pequenas alterações podem produzir efeitos imprevistos e exigir regressão completa. Sem testes externos automatizados, a repetição manual tende a degradar a qualidade da verificação.

---

<a id="pagina-0201"></a>

## Página 0201 — A HAL define serviços na linguagem da aplicação

As figuras 29.3 e 29.4 contrastam a fronteira difusa entre software e firmware com uma separação explícita por uma camada de abstração de hardware, a HAL. Sua API deve atender às necessidades do software acima dela. Enquanto o firmware grava bytes em flash, a aplicação pode precisar apenas salvar e recuperar pares nome/valor. A HAL oferece esse serviço sem revelar se o armazenamento usa flash, disco, nuvem ou outra tecnologia. O início de outro exemplo relaciona um LED a um bit GPIO, preparando a distinção entre operações de hardware e intenção do produto.

---

<a id="pagina-0202"></a>

## Página 0202 — Abstrações da aplicação escondem detalhes do processador

Uma HAL pode oferecer ligar um LED, mas uma operação como indicar bateria fraca expressa melhor a necessidade do produto e esconde a associação a GPIO. Camadas podem conter novas camadas, ajustadas aos níveis de abstração. Essa separação permite testar o software fora do equipamento final. O texto alerta que compiladores especializados acrescentam palavras-chave e acessos diretos a registradores, portas e temporizadores, fazendo o código deixar de ser C portátil. O uso desses recursos deve ficar restrito a poucos arquivos. A página começa um cabeçalho fictício da família ACME para examinar dependências de tipos específicas da plataforma.

---

<a id="pagina-0203"></a>

## Página 0203 — Tipos padronizados preservam portabilidade

O cabeçalho ACME varia os tipos inteiros conforme o processador e rejeita ambientes desconhecidos. Incluí-lo diretamente espalha dependências da ferramenta e pode produzir tamanhos errados em testes fora do alvo. O autor recomenda usar stdint.h; se o compilador não o fornecer, é possível criar uma adaptação local que converta os tipos específicos para nomes padronizados como uint32_t. Assim, os detalhes ficam concentrados e o software permanece independente do processador. A página introduz depois uma função de saída serial que usa extensões de C, lembrando que parte do firmware necessariamente conhece os periféricos concretos.

---

<a id="pagina-0205"></a>

## Página 0205 — A OSAL protege a aplicação do sistema operacional

Usar diretamente o sistema operacional pode tornar sua substituição onerosa: mudanças comerciais do fornecedor, queda de qualidade ou novas necessidades podem exigir outra plataforma. A migração envolve diferenças semânticas de recursos e primitivas, além de nomes de funções. A figura 29.5 mostra o sistema operacional entre software e firmware; a figura 29.6 acrescenta a OSAL entre aplicação e sistema operacional e mantém a HAL abaixo dele. A OSAL pode apenas adaptar nomes em alguns casos ou agrupar várias funções em outros. Seu papel é impedir que dependências específicas da plataforma se espalhem pela aplicação.

---

<a id="pagina-0206"></a>

## Página 0206 — Interfaces tornam camadas substituíveis e testáveis

Uma OSAL permite migrar de RTOS implementando um contrato conhecido, em vez de alterar grande quantidade de lógica. Também pode concentrar repetições e oferecer mecanismos comuns, como troca de mensagens entre threads, sem necessariamente gerar grande sobrecarga. Seus pontos de substituição permitem testes fora do hardware e do sistema operacional alvo. O texto recomenda interfaces em todas as camadas: cabeçalhos devem expor apenas funções e tipos necessários aos clientes, ocultando detalhes internos. A compatibilidade com printf ilustra substituição de implementações. Ao final, começa a discussão de condicionais de compilação para diferentes plataformas.

---

<a id="pagina-0207"></a>

## Página 0207 — Esconder variações de hardware evita condicionais repetidas

O autor relata uma aplicação de telecomunicações com milhares de ocorrências de uma condição de compilação que identificava a versão da placa. Essa repetição viola o princípio de não duplicar conhecimento e espalha a dependência do hardware. Com uma HAL, o tipo de equipamento pode ficar oculto e a implementação correta ser selecionada pelo vinculador ou em execução. A conclusão reforça que sistemas embarcados também se beneficiam dos princípios gerais de projeto. Transformar todo o código em firmware e permitir testes apenas no alvo prejudica a vida útil do produto. A página termina com referências e notas.
