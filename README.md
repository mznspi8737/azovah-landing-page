# AZOVAH · Landing page e checkout

Página de vendas do AZOVAH Numerologia e a página de pagamento ligada a ela.

## Estrutura

```
Main.dc.html     Landing page (arquivo do editor de design onde ela é publicada hoje)
canvas.json      Configuração do editor (tamanho da página)
assets/          Vídeos do tour, pôsteres e imagens do topo
checkout/        Página de pagamento
  src.html       Fonte
  build.py       Monta checkout/index.html (embute a logo e a prévia do e-mail)
  index.html     Versão pronta para publicar
```

## Seções da landing page

Topo, 16 módulos em quatro grupos, tour em vídeo (computador e iPhone), depoimentos ilustrativos, matriz de planos e serviços (Sistema, Licença profissional e Atendimentos personalizados) e perguntas frequentes.

## Mídia

As imagens e vídeos aparecem no HTML como `/_blob/...`, porque ficam hospedados junto com a página publicada. As cópias locais estão em `assets/`:

| Arquivo | Uso |
|---|---|
| `tour4_d.mp4`, `poster4_d.jpg` | Tour do sistema no computador |
| `tour4_m.mp4`, `poster4_m.jpg` | Tour do sistema no iPhone |
| `hero_bg.jpg` | Fundo do topo |
| `hero_desk.webp`, `hero_mob.webp` | Telas do sistema no topo |

Para hospedar em domínio próprio, troque os endereços `/_blob/...` pelos arquivos de `assets/`.

## Checkout

```bash
python3 checkout/build.py
```

Links dos planos: `checkout/index.html?plano=mensal|semestral|anual`. Sem servidor configurado, roda em modo demonstração (não cobra nada). O servidor de pagamento e acesso fica no repositório do sistema (`azovah-numerologia`, pasta `server/`).

## Pendências

- Número de WhatsApp para os botões "Consultar" da matriz de planos.
- Depoimentos reais autorizados no lugar dos 30 ilustrativos (que hoje têm aviso visível).
- Gateway de pagamento configurado no servidor.

## Licença

Código proprietário. Todos os direitos reservados.

## Nova landing page (site/) · 26/11/2026

`site/index.html` é a versão nova, pronta para publicar no servidor: copie a pasta `site/` inteira (com `assets/`).

- Topo com hora ao vivo, data, dia universal e previsão do tempo (Open-Meteo, sem chave; cidade pelo fuso horário do visitante e botão "Usar minha localização").
- Código de barras vertical no canto do topo, com a data de hoje reduzida.
- "Experimente agora": calcula Expressão, Motivação, Impressão, Destino, arcano atual e ano pessoal no próprio navegador (`assets/engine.js`, o mesmo motor do sistema).
- Gráficos ao vivo: triângulo da vida, números principais, ciclos, momentos, lições, ano pessoal dos próximos 9 anos, força de cada número e linha do tempo dos arcanos.
- Tour novo em vídeo (`tour5_d.mp4`, `tour5_m.mp4`) com o visual atual e a Matriz triângulo.
- 17 módulos com filtro, Monte sua assinatura com opções reais, Matriz, depoimentos ilustrativos, planos com seletor, garantia de 7 dias (CDC), FAQ, botão de WhatsApp, barra fixa no celular e voltar ao topo.

`Main.dc.html` continua sendo a versão anterior, do editor de design.
