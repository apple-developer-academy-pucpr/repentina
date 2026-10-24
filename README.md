# Repentina · Apple Developer Academy PUCPR

Visualização da rodada liberada, com busca por nome e entradas, saídas e permanências por time.

## Liberar uma rodada

1. Entre no GitHub com uma conta autorizada.
2. Abra **Actions → Liberar rodada → Run workflow**.
3. Mantenha o branch `main`, escolha de **0 a 4** e clique em **Run workflow**.
4. Aguarde a execução ficar verde. Peça aos participantes que recarreguem a página.

[Controle de rodadas](https://github.com/apple-developer-academy-pucpr/team-changes/actions/workflows/change-round.yml)

[Site dos participantes](https://apple-developer-academy-pucpr.github.io/team-changes/)

A rodada 0 mostra a formação inicial. As rodadas 1 a 4 mostram as trocas previstas no planejamento. Liberar uma rodada não recalcula os times.

## Acesso administrativo

O GitHub exige permissão de escrita no repositório para executar o workflow. Não existe painel `/admin` público, senha no JavaScript ou credencial no site. Administradores devem ser pessoas de confiança: quem pode modificar workflows pode acessar os secrets.

## Dados

O backup completo não está neste repositório. As projeções mínimas são configuradas nos secrets `ROUND_0` a `ROUND_4`. O workflow recebe apenas a rodada selecionada e publica somente seu HTML. Uma rodada já publicada pode ter sido copiada por visitantes. Não adicione backups ou dados pessoais ao histórico Git.

A publicação não é instantânea. Uma execução com erro mantém a publicação anterior; consulte o status antes de anunciar a troca.
