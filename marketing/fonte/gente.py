# Gera os 3 posts humanizados no MESMO padrão (foto real em cima, painel de cor embaixo)
POSTS = [
    dict(file='Gente-Esforco.dc.html', title='AZOVAH · Eu faço tudo certo', blob='d0f9cbe4306e18344a8707141548cbcc', pos='30% 30%',
         bg='#ffb238', ink='#2a1600', sub='#4a2c00', accent='#b3261e', cta_bg='#2a1600', cta_ink='#ffffff', chip='TRABALHO E DINHEIRO',
         quote='“Eu faço tudo certo. Por que nada muda?”',
         h1='Não é falta de esforço. <em>É vibração.</em>',
         body='Números que se repetem no seu nome criam o mesmo bloqueio. A numerologia cabalística mostra onde está.',
         cta='Calcule grátis na bio'),
    dict(file='Gente-Casal.dc.html', title='AZOVAH · O mesmo padrão no amor', blob='0645271d3eb3e51b612198224fcfc7ce', pos='50% 25%',
         bg='#0e3b3a', ink='#ffffff', sub='#c9ece4', accent='#ff9a7a', cta_bg='#ff8a6b', cta_ink='#0e3b3a', chip='AMOR',
         quote='“Muda a pessoa. A briga é sempre a mesma.”',
         h1='O padrão não está no outro. <em>Está nos números.</em>',
         body='A Compatibilidade do AZOVAH mostra onde vocês se unem e onde se atritam.',
         cta='Descubra na bio'),
    dict(file='Gente-Noite.dc.html', title='AZOVAH · A decisão que não deixa dormir', blob='017fed9647796f29d600fd7e84fd122b', pos='60% 30%',
         bg='#14185a', ink='#ffffff', sub='#c8cbff', accent='#ffd36b', cta_bg='#ffd36b', cta_ink='#14185a', chip='DECISÕES',
         quote='“Mais uma noite sem dormir. É a hora certa?”',
         h1='Sua vida anda em ciclos. <em>Saiba em qual você está.</em>',
         body='O ano pessoal e o Calendário do AZOVAH mostram o melhor momento para decidir.',
         cta='Calcule na bio'),
]
TPL = r'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:{accent}}}a:hover{{color:{ink}}}
.foto{{background-image:url(/_blob/{blob});background-size:cover;background-position:{pos}}}
.h1 em{{font-style:italic;color:{accent}}}
</style>
</helmet>
<div style="width:1080px;height:1350px;position:relative;overflow:hidden;box-sizing:border-box;font-family:Inter,sans-serif;background:{bg};color:{ink}">
  <div class="foto" role="img" aria-label="Foto de pessoas" style="position:absolute;left:0;top:0;width:1080px;height:780px"></div>
  <div style="position:absolute;left:0;top:0;width:1080px;height:780px;background:linear-gradient(180deg,rgba(0,0,0,.45) 0%,rgba(0,0,0,0) 26%,rgba(0,0,0,0) 60%,rgba(0,0,0,.35) 100%)"></div>
  <div style="position:absolute;left:56px;top:52px;right:56px;display:flex;align-items:center;justify-content:space-between">
    <span style="font:900 38px Inter,sans-serif;letter-spacing:.06em;color:#ffffff">AZOVAH</span>
    <span style="padding:12px 22px;border-radius:999px;background:{bg};color:{ink};font:800 24px Inter,sans-serif;letter-spacing:.08em">{chip}</span>
  </div>
  <div style="position:absolute;left:56px;right:56px;top:612px;padding:30px 36px;border-radius:30px;background:#ffffff;box-shadow:0 30px 60px -24px rgba(0,0,0,.55)">
    <p style="margin:0;font:400 italic 50px/1.12 'DM Serif Display',Georgia,serif;color:#1a1a1a">{quote}</p>
  </div>
  <div style="position:absolute;left:56px;right:56px;top:830px;bottom:56px;display:flex;flex-direction:column;gap:22px">
    <h1 class="h1" style="margin:0;font:400 76px/1.02 'DM Serif Display',Georgia,serif;letter-spacing:-.01em;color:{ink}">{h1}</h1>
    <p style="margin:0;font:600 34px/1.32 Inter,sans-serif;color:{sub}">{body}</p>
    <div style="margin-top:auto;display:flex;align-items:center;justify-content:space-between;gap:20px">
      <span style="display:flex;align-items:center;gap:16px;padding:24px 36px;border-radius:999px;background:{cta_bg};color:{cta_ink};font:900 34px Inter,sans-serif;white-space:nowrap">{cta} <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg></span>
      <span style="font:800 28px Inter,sans-serif;color:{sub}">@azovah</span>
    </div>
  </div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1080,"height":1350}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
for p in POSTS:
    open('/home/claude/criativos_az/project/' + p['file'], 'w').write(TPL.format(**p))
    print(p['file'])
