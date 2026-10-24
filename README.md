# Repentina · Apple Developer Academy PUCPR

Visualização da rodada liberada, com busca por nome e entradas, saídas e permanências por time.

## Liberar uma rodada

1. Entre no GitHub com uma conta autorizada.
2. Abra **Actions → Liberar rodada ou fechar página → Run workflow**.
3. Mantenha o branch `main`, escolha de **0 a 4** e clique em **Run workflow**.
4. Aguarde a execução ficar verde. Peça aos participantes que recarreguem a página.

[Controle de rodadas](https://github.com/apple-developer-academy-pucpr/repentina/actions/workflows/change-round.yml)

[Site dos participantes](https://apple-developer-academy-pucpr.github.io/repentina/)

A rodada 0 mostra a formação inicial. As rodadas 1 a 4 mostram as trocas previstas no planejamento. Liberar uma rodada não recalcula os times.

## Acesso administrativo

O GitHub exige permissão de escrita no repositório para executar o workflow. Não existe painel `/admin` público, senha no JavaScript ou credencial no site. Administradores devem ser pessoas de confiança: quem pode modificar workflows pode acessar os secrets.

## Dados

O backup completo não está neste repositório. As projeções mínimas são configuradas nos secrets `ROUND_0` a `ROUND_4`. O workflow recebe apenas a rodada selecionada e publica somente seu HTML. Uma rodada já publicada pode ter sido copiada por visitantes. Não adicione backups ou dados pessoais ao histórico Git.

A publicação não é instantânea. Uma execução com erro mantém a publicação anterior; consulte o status antes de anunciar a troca.

## Fechar a página

No mesmo workflow, selecione **Fechar página** e execute. Após a conclusão, o site exibe apenas uma mensagem de indisponibilidade, sem nomes ou dados dos candidatos no HTML. Essa opção não carrega secrets das rodadas. Para reabrir, escolha uma rodada de 0 a 4. Fechar não apaga cópias que visitantes já tenham salvo.

## Atualização automática e cache

O HTML não incorpora dados dos participantes. Ele consulta `current.json` com
`cache: no-store` e uma chave de atualização, e verifica o estado a cada 15
segundos. A implantação fechada publica apenas `{"closed": true}` nesse arquivo.
A página limpa dados ao detectar fechamento ou falha na consulta. Ao voltar a
uma aba em segundo plano, oculta os dados e verifica o estado novamente.

A implantação ainda precisa concluir e propagar no GitHub Pages. Abas que
carregaram a implementação antiga precisam ser recarregadas uma vez. Nenhuma
alteração pode revogar cópias que alguém já salvou.
