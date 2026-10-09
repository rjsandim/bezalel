# Proveniência e diferenças

Versão comum preparada em 9 de outubro de 2026, por autorização do usuário,
a partir das variantes locais `~/.agents/skills/vps-deploy/` e
`~/.claude/skills/vps-deploy/`. Os originais permanecem intactos. Esta versão é
uma adaptação revisada, não uma cópia byte a byte nem a certificação de um deploy.

| Tema | Variante Agents | Variante Claude | Versão comum |
|---|---|---|---|
| Autenticação | Variável de ambiente e leitura automática de um item local do Keychain | Valor literal em exemplos de cabeçalhos | Somente referência a `COOLIFY_API_TOKEN`; o usuário fornece o segredo ao processo |
| Escopo | Seção explícita de autorização e segurança | Menos explícito | Projeto e operação precisam estar identificados; mudanças destrutivas exigem autorização específica |
| Destino | Instalação específica embutida | Mesma instalação específica embutida | Configuração local independente em `.bezalel` por projeto |
| Inventário | Serviços, identificadores e caminhos internos | Serviços, identificadores e caminhos internos | Removidos, sem substituição por valores reais |
| Recuperação | Orientações de alteração direta e remoção de volumes | Orientações semelhantes | Retiradas como padrão; diagnóstico e preservação precedem ações destrutivas |
| Procedimentos | Dependem de uma instalação e versão específicas | Dependem de uma instalação e versão específicas | Exigem conferência da versão e do mecanismo suportado no ambiente autorizado |

Também foram removidos endereços reais, nomes de pessoas/organizações, detalhes
da máquina e identificadores do cofre local. Nenhum valor sensível consta neste
registro. O literal antigo foi tratado como segredo por instrução do usuário;
sua validade não foi testada. Não houve cópia de credenciais, rotação, criação
de acesso, conexão com servidores, deploy ou push.

Os hashes de origem no `inventory.json` da raiz permitem identificar os arquivos
consultados sem reproduzir seu conteúdo. Os testes da nova versão cobrem apenas
a configuração local e a prevenção de exposição acidental nas mensagens. Não
atestam autenticação, permissões, disponibilidade ou compatibilidade operacional
com uma instalação real do Coolify.
