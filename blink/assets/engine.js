// Motor de cálculo - Numerologia Cabalística
// Tabela oficial: 1 A I Q J Y | 2 B K R | 3 C G L S | 4 D M T | 5 E H N | 6 U V W X Ç | 7 O Z | 8 F P
// Sinais: ' e ´ +2 | ~ +3 | ^ e º +7 | ` e ¨ x2
(function (root) {
  const TABELA = {
    A: 1, I: 1, Q: 1, J: 1, Y: 1,
    B: 2, K: 2, R: 2,
    C: 3, G: 3, L: 3, S: 3,
    D: 4, M: 4, T: 4,
    E: 5, H: 5, N: 5,
    U: 6, V: 6, W: 6, X: 6,
    O: 7, Z: 7,
    F: 8, P: 8,
  };
  const VOGAIS = new Set(['A', 'E', 'I', 'O', 'U', 'Y']);
  const MESTRES = [11, 22];
  // Harmonia conjugal pelo número da Missão: vibra com, atrai, oposto, muito oposto, passivo
  const HARMONIA = {
    1: { vibra: [9], atrai: [4, 8], oposto: [6, 7], muitoOposto: [], passivo: [2, 3, 5] },
    2: { vibra: [8], atrai: [7, 9], oposto: [5], muitoOposto: [], passivo: [1, 3, 4, 6] },
    3: { vibra: [7], atrai: [5, 6, 9], oposto: [4, 8], muitoOposto: [], passivo: [1, 2] },
    4: { vibra: [6], atrai: [1, 8], oposto: [3, 5], muitoOposto: [], passivo: [2, 7, 9] },
    5: { vibra: [5], atrai: [3, 9], oposto: [2, 4], muitoOposto: [6], passivo: [1, 7, 8] },
    6: { vibra: [4], atrai: [3, 7, 9], oposto: [1, 8], muitoOposto: [5], passivo: [2] },
    7: { vibra: [3], atrai: [2, 6], oposto: [1, 9], muitoOposto: [], passivo: [4, 5, 8] },
    8: { vibra: [2], atrai: [1, 4], oposto: [3, 6], muitoOposto: [], passivo: [5, 7, 9] },
    9: { vibra: [1], atrai: [2, 3, 5, 6], oposto: [7], muitoOposto: [], passivo: [4, 8] },
  };
  const DIVIDA_POR_NUMERO = { 4: 13, 5: 14, 7: 16, 1: 19 };

  function somaDigitos(n) {
    return String(n).split('').reduce((s, d) => s + Number(d), 0);
  }
  function reduzir(n, manterMestre) {
    while (n > 9 && !(manterMestre && MESTRES.includes(n))) n = somaDigitos(n);
    return n;
  }

  // Converte o nome numa lista de letras com valor
  function letrasDoNome(nome) {
    const out = [];
    const txt = nome.normalize('NFC');
    for (const ch of txt) {
      if (ch === "'" || ch === '’') {
        // apóstrofo soma 2 à letra anterior
        if (out.length) { out[out.length - 1].valor += 2; out[out.length - 1].sinais.push("'"); }
        continue;
      }
      if (ch === 'º' || ch === '°') {
        if (out.length) { out[out.length - 1].valor += 7; out[out.length - 1].sinais.push('º'); }
        continue;
      }
      // números no nome (empresas, marcas): valem o próprio número; contam como consoante (Impressão) e entram no triângulo. O zero não tem vibração e é ignorado.
      if (/[1-9]/.test(ch)) { out.push({ letra: ch, base: ch, valor: +ch, vogal: false, sinais: [], numero: true }); continue; }
      const up = ch.toUpperCase();
      if (up === 'Ç') { out.push({ letra: ch.toUpperCase(), base: 'Ç', valor: 6, vogal: false, sinais: ['ç'] }); continue; }
      const nfd = up.normalize('NFD');
      const base = nfd[0];
      if (!(base in TABELA)) continue; // espaços, hífens etc.
      let valor = TABELA[base];
      const sinais = [];
      for (const m of nfd.slice(1)) {
        if (m === '́') { valor += 2; sinais.push('´'); }
        else if (m === '̃') { valor += 3; sinais.push('~'); }
        else if (m === '̂') { valor += 7; sinais.push('^'); }
        else if (m === '̊') { valor += 7; sinais.push('º'); }
        else if (m === '̀') { valor *= 2; sinais.push('`'); }
        else if (m === '̈') { valor *= 2; sinais.push('¨'); }
      }
      out.push({ letra: up, base, valor, vogal: VOGAIS.has(base), sinais });
    }
    return out;
  }

  function digitosData(d, m, a) {
    return somaDigitos(String(d) + String(m) + String(a));
  }

  function montarTriangulo(linhaBase) {
    const linhas = [linhaBase.slice()];
    while (linhas[linhas.length - 1].length > 1) {
      const ant = linhas[linhas.length - 1];
      const nova = [];
      for (let i = 0; i < ant.length - 1; i++) nova.push(reduzir(ant[i] + ant[i + 1], false));
      // Regra do vértice: quando o último par soma 11, o triângulo termina em 11 (não reduz para 2)
      if (ant.length === 2 && ant[0] + ant[1] === 11) nova[0] = 11;
      linhas.push(nova);
    }
    return linhas;
  }

  function sequenciasNegativas(linhas) {
    const achadas = [];
    linhas.forEach((linha, li) => {
      let i = 0;
      while (i < linha.length) {
        let j = i;
        while (j + 1 < linha.length && linha[j + 1] === linha[i]) j++;
        if (j - i + 1 >= 3) achadas.push({ linha: li + 1, inicio: i, tamanho: j - i + 1, numero: linha[i], seq: String(linha[i]).repeat(j - i + 1) });
        i = j + 1;
      }
    });
    return achadas;
  }

  // Arcanos do triângulo: cada par vizinho da 1ª linha forma um arcano (ex.: 4 e 1 = 41).
  // São (letras - 1) arcanos e cada um rege 90 / nº de arcanos anos.
  function arcanosDoTriangulo(base, idadeExata) {
    const qtd = Math.max(1, base.length - 1);
    const dur = 90 / qtd;
    const periodos = [];
    for (let i = 0; i < qtd; i++) {
      const a = base[i], b = base.length > 1 ? base[i + 1] : base[0];
      periodos.push({ indice: i, arcano: a * 10 + b, de: i * dur, ate: (i + 1) * dur });
    }
    const atual = idadeExata == null ? null : periodos.find(p => idadeExata >= p.de && idadeExata < p.ate) || null;
    return { duracao: dur, quantidade: qtd, periodos, atual };
  }

  // Datas dos arcanos (convenção usual da numerologia cabalística): período = floor(duração x 365) dias;
  // início = nascimento + n períodos; fim = início + anos/meses/dias da duração no calendário.
  function difCalendario(a, b) {
    let y = b.getFullYear() - a.getFullYear(), m = b.getMonth() - a.getMonth(), d = b.getDate() - a.getDate();
    if (d < 0) { m--; d += new Date(b.getFullYear(), b.getMonth(), 0).getDate(); }
    if (m < 0) { y--; m += 12; }
    return { anos: y, meses: m, dias: d };
  }
  function somarCalendario(dt, c) {
    const r = new Date(dt); r.setFullYear(r.getFullYear() + c.anos); r.setMonth(r.getMonth() + c.meses); r.setDate(r.getDate() + c.dias); return r;
  }
  const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  function datarArcanos(arc, nasc, hoje) {
    // Duração em anos inteiros: datas em anos de calendário (convenção usual)
    if (Math.abs(arc.duracao - Math.round(arc.duracao)) < 1e-9) {
      const anos = Math.round(arc.duracao);
      arc.duracaoCalendario = { anos, meses: 0, dias: 0 };
      arc.periodos.forEach(p => {
        const ini = new Date(nasc); ini.setFullYear(nasc.getFullYear() + p.indice * anos);
        const fim = new Date(nasc); fim.setFullYear(nasc.getFullYear() + (p.indice + 1) * anos);
        p.inicio = iso(ini); p.fim = iso(fim);
      });
      const h0 = iso(hoje);
      arc.atual = arc.periodos.find(p => h0 >= p.inicio && h0 < p.fim) || null;
      return arc;
    }
    const dias = Math.floor(arc.duracao * 365);
    const fim1 = new Date(nasc.getTime() + dias * 864e5);
    const cal = difCalendario(nasc, fim1);
    arc.duracaoCalendario = cal;
    arc.periodos.forEach(p => {
      const ini = new Date(nasc.getTime() + p.indice * dias * 864e5);
      p.inicio = iso(ini); p.fim = iso(somarCalendario(ini, cal));
    });
    const h = iso(hoje);
    arc.atual = arc.periodos.find(p => h >= p.inicio && h < (arc.periodos[p.indice + 1]?.inicio || p.fim)) || null;
    return arc;
  }

  function idadeEm(nasc, hoje) {
    let idade = hoje.getFullYear() - nasc.getFullYear();
    const m = hoje.getMonth() - nasc.getMonth();
    if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) idade--;
    return idade;
  }

  function calcular(nome, dataISO, hoje) {
    hoje = hoje || new Date();
    const [a, m, d] = dataISO.split('-').map(Number);
    const nasc = new Date(a, m - 1, d);
    const letras = letrasDoNome(nome);
    if (!letras.length) throw new Error('Nome sem letras válidas');

    const somaVog = letras.filter(l => l.vogal).reduce((s, l) => s + l.valor, 0);
    const somaCons = letras.filter(l => !l.vogal).reduce((s, l) => s + l.valor, 0);
    const somaTot = somaVog + somaCons;

    const motivacao = reduzir(somaVog, true) || 1;   // regra: sem vogais (0) vale 1
    const impressao = reduzir(somaCons, false) || 1; // regra: sem consoantes (0) vale 1
    const expressao = reduzir(somaTot, true);

    const somaData = digitosData(d, m, a);
    const destino = reduzir(somaData, true);
    const missao = reduzir(destino + expressao, true);
    const talentoOculto = reduzir(motivacao + expressao, true);
    const psiquico = reduzir(d, false);

    // Lições cármicas e tendências ocultas (valores das letras reduzidos)
    const valoresReduzidos = letras.map(l => reduzir(l.valor, false));
    const contagem = {};
    for (let i = 1; i <= 9; i++) contagem[i] = 0;
    valoresReduzidos.forEach(v => contagem[v]++);
    const licoes = Object.keys(contagem).map(Number).filter(n => contagem[n] === 0);
    const tendencias = Object.keys(contagem).map(Number).filter(n => contagem[n] > 3);
    const respostaSubconsciente = 9 - licoes.length;

    // Dívidas cármicas: dia 13/14/16/19 e Destino, Motivação ou Expressão iguais a 4, 5, 7 ou 1
    const dividas = new Set();
    if ([13, 14, 16, 19].includes(d)) dividas.add(d);
    [destino, motivacao, expressao].forEach(n => { if (DIVIDA_POR_NUMERO[n]) dividas.add(DIVIDA_POR_NUMERO[n]); });

    // Ciclos de vida, desafios e momentos decisivos
    const dR = reduzir(d, true), mR = reduzir(m, true), aR = reduzir(somaDigitos(a), true);
    const destinoSimples = reduzir(destino, false);
    const fim1 = 37 - destinoSimples;
    const ciclos = [
      { numero: mR, de: 0, ate: fim1 },
      { numero: reduzir(d, false), de: fim1, ate: fim1 + 27 },
      { numero: aR, de: fim1 + 27, ate: null },
    ];
    const ds = reduzir(d, false), ms = reduzir(m, false), as = reduzir(somaDigitos(a), false);
    const des1 = Math.abs(ds - ms), des2 = Math.abs(ds - as);
    const desafios = { primeiro: des1, segundo: des2, principal: Math.abs(des1 - des2) };
    const md1 = reduzir(d + m, true), md2 = reduzir(d + a, true);
    const md3 = reduzir(md1 + md2, true), md4 = reduzir(m + a, true);
    const momentos = [
      { numero: md1, de: 0, ate: fim1 },
      { numero: md2, de: fim1, ate: fim1 + 9 },
      { numero: md3, de: fim1 + 9, ate: fim1 + 18 },
      { numero: md4, de: fim1 + 18, ate: null },
    ];

    // Ano pessoal (conta o ano do último aniversário)
    const aniversarioPassou = (hoje.getMonth() + 1 > m) || (hoje.getMonth() + 1 === m && hoje.getDate() >= d);
    const anoRef = aniversarioPassou ? hoje.getFullYear() : hoje.getFullYear() - 1;
    const anoPessoal = reduzir(reduzir(d, false) + reduzir(m, false) + somaDigitos(anoRef), false);

    const idade = idadeEm(nasc, hoje);
    const idadeExata = (hoje - nasc) / (365.2425 * 864e5);
    const mesPessoal = reduzir(anoPessoal + reduzir(hoje.getMonth() + 1, false), false);
    const diaPessoal = reduzir(mesPessoal + reduzir(hoje.getDate(), false), false);
    const missaoSimples = reduzir(missao, false);
    const harmonia = HARMONIA[missaoSimples];

    // Triângulos
    const base = valoresReduzidos;
    const somaDM = reduzir(ds + ms, false);
    const tri = {
      basico: base,
      pessoal: base.map(v => reduzir(v + ds, false)),
      social: base.map(v => reduzir(v + ms, false)),
      destino: base.map(v => reduzir(v + somaDM, false)),
    };
    const triangulos = {};
    for (const k of Object.keys(tri)) {
      const linhas = montarTriangulo(tri[k]);
      triangulos[k] = {
        linhas,
        final: linhas[linhas.length - 1][0],
        sequencias: sequenciasNegativas(linhas),
        arcanos: datarArcanos(arcanosDoTriangulo(tri[k], idadeExata), new Date(a, m - 1, d, 12), new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate(), 12)),
      };
    }

    return {
      entrada: { nome, data: dataISO, idade, idadeExata, anoReferencia: anoRef },
      letras,
      somas: { vogais: somaVog, consoantes: somaCons, total: somaTot, data: somaData },
      grauAscensao: somaVog === somaCons ? 'equilíbrio' : (somaVog > somaCons ? 'retrocesso' : 'ascensão'),
      numeros: { motivacao, impressao, expressao, destino, missao, talentoOculto, psiquico, anoPessoal, mesPessoal, diaPessoal, respostaSubconsciente },
      brutos: { motivacao: somaVog, impressao: somaCons, expressao: somaTot, destino: somaData, missao: destino + expressao, talentoOculto: motivacao + expressao, psiquico: d },
      harmonia: { base: missaoSimples, ...harmonia },
      licoes, tendencias, dividas: [...dividas].sort((x, y) => x - y), contagem,
      ciclos, desafios, momentos,
      triangulos,
    };
  }

  const api = { calcular, letrasDoNome, reduzir, montarTriangulo, TABELA };
  if (typeof module !== 'undefined') module.exports = api; else root.Numerologia = api;
})(typeof window !== 'undefined' ? window : globalThis);
