"""Monta o checkout: checkout/index.html a partir de src.html.

Uso:  python3 checkout/build.py
Embute a logo (logo.b64) e a prévia do e-mail de boas-vindas (email-boas-vindas.html).
O modelo oficial do e-mail fica no repositório do sistema, em server/emails/boas-vindas.html.
"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(AQUI, 'src.html'), encoding='utf-8').read()
logo = open(os.path.join(AQUI, 'logo.b64')).read().strip()
mail = open(os.path.join(AQUI, 'email-boas-vindas.html'), encoding='utf-8').read()
s = s.replace('__LOGO__', logo).replace('__MAIL__', json.dumps(mail).replace('</', '<\\/'))
open(os.path.join(AQUI, 'index.html'), 'w', encoding='utf-8').write(s)
print(f'checkout/index.html: {len(s)//1024} KB')
