# PLANO — "Consulte frete por CEP" + banner novo (Site Lira Fraldas)

> Plano de execução auto-contido. Um agente em contexto novo executa só com este arquivo.
> Repo: `lira-fraldas-site` (`~/projetos/lira-fraldas-site`, GitHub `Audex-dev/lira-fraldas-site`).
> Deploy: **Cloudflare Pages** projeto `lira-fraldas`, branch de PRODUÇÃO = **`main`** (`npx wrangler pages deploy . --project-name=lira-fraldas --branch=main`; branch≠main vira PREVIEW!). Home = `index.html` (= Loja Prática).
> Canônica: `[[Site Lira Fraldas]]`. Fecha/avança o `[[PENDENCIAS]]` **P-235** (frete dinâmico por bairro). Criado 2026-07-04 pelo CEO.

## 1. Objetivo (pedido do John)
Na loja, adicionar **"Consulte frete por CEP"**: o cliente digita o CEP → resolvemos o **bairro** (via ViaCEP) → buscamos o valor na **nossa tabela** (que o Bosco mandou no grupo) → mostramos a taxa (ou "grátis acima de R$X", ou "retirada/consultar"). O site já tem gancho pronto pro frete dinâmico (P-235); aqui plugamos a tabela + o lookup por CEP e integramos ao carrinho.

## 2. Tabela de frete (fonte: Bosco, WhatsApp 2026-07-04 — literal)
> Salva em `~/.../scratchpad/lira-lista-bairros-frete.txt`. Fortaleza/CE. **Normalizar** (UPPER + sem acento) na comparação, porque o ViaCEP devolve o bairro com grafia/acentos diferentes.

- **GRÁTIS acima de R$30,00:** Mucuripe, Vicente Pinzon, Cais do Porto, Varjota, Serviluz
- **GRÁTIS acima de R$50,00:** Papicu, Gengibre*
- **R$5,00:** Aldeota, De Lourdes, Meireles, Praia do Futuro 1
- **R$6,00:** Alto da Balança, Aerolândia, Cidade 2000, Cocó, Centro, Guararapes, Dionísio Torres, Joaquim Távora, Praia de Iracema, Manoel Dias Branco, São João do Tauape
- **R$8,00:** Caça e Pesca, Praia do Futuro 2
- **R$10,00:** Bairro de Fátima, Edson Queiroz, Luciano Cavalcante, Salinas
- **R$12,00:** Álvaro Weyne, Amadeu Furtado, Ancuri, Antônio Bezerra, Barroso, Barra do Ceará, Bela Vista, Benfica, Bom Jardim, Bom Sucesso, Cambeba, Cajazeiras, Canindezinho, Carlito Pamplona, Castelão, Cidade dos Funcionários, Conjunto Ceará, Conjunto Palmeiras, Cristo Redentor, Coaçu, Curió, Damas, Demócrito Rocha, Dias Macedo, Dom Lustosa, Ellery, Farias Brito, Floresta, Genibaú, Granja Portugal, Granja Lisboa, Guajiru, Henrique Jorge, Itaoca, Jacarecanga, Jardim América, Jardim Guanabara, Jangurussu, José Bonifácio, Jóquei Clube, João XXIII, José Walter, Lagoa Redonda, Messejana, Modubim, Monte Castelo, Montese, Passaré, Padre Andrade, Parquelândia, Parque Araxá, Parque Dois Irmãos, Parque Iracema, Parque São José, Parreão, Pirambu, Pici, Planalto Ayrton Senna, Presidente Kennedy, Quintino Cunha, Rodolfo Teófilo, Sapiranga, Serrinha, Siqueira, Vila Pery, Vila Velha, Vila União

## 3. ⚠️ A CONFIRMAR com o Bosco ANTES de codar (perguntas)
1. **Taxa dos bairros "grátis acima de 30/50" quando o pedido é ABAIXO do limite** — qual valor? (a barra atual do site diz "a partir de R$10 · grátis ≥ R$30"; confirmar o valor-base desses bairros.)
2. **Bairro fora da lista** → é **retirada na loja**? "consultar no WhatsApp"? não entrega? (definir a mensagem/comportamento.)
3. **"GENGIBRE"** (na faixa grátis≥50) — não é bairro conhecido de Fortaleza; confirmar grafia/real.
4. **"Praia do Futuro 1/2"** e **"Cidade 2000"** — o ViaCEP costuma devolver "Praia do Futuro" (sem 1/2) e nomes variados; definir como mapear (pode exigir seleção manual do sub-bairro).

## 4. Fases

### Fase 0 — Modelar a tabela (dado)
- Criar `fretes.js` (`window.LIRA_FRETE`) com: mapa `bairroNormalizado → { taxa:Number|null, gratisAcima:Number|null }`. Helper `normalizar(s)` (UPPER, `normalize('NFD')` sem diacríticos, trim). Gerar do §2. Cidade fixa = Fortaleza (ignorar CEP de outras cidades → "consultar").

### Fase 1 — UI "Consulte frete por CEP" (na Loja Prática / `index.html`)
1. Campo **CEP** (máscara 00000-000) + botão **"Consultar frete"** — no topo da barra de frete e/ou no carrinho.
2. Ao consultar: `fetch('https://viacep.com.br/ws/<cep>/json/')` → pega `bairro`, `localidade`, `uf`. Se `erro` ou `uf!=CE`/`localidade!=Fortaleza` → "Não entregamos nesse endereço / consulte no WhatsApp".
3. `normalizar(bairro)` → match no `LIRA_FRETE`. Resultado:
   - taxa fixa → "Frete: R$X,00 para <BAIRRO>".
   - grátisAcima → se subtotal ≥ limite → "Frete GRÁTIS 🎉"; senão → "Frete R$<base> — grátis acima de R$<limite> (faltam R$Y)".
   - bairro sem match → comportamento do §3.2.
4. Se o ViaCEP não devolver bairro (alguns CEPs), pedir o **bairro manual** (dropdown com os bairros da tabela) como fallback.
5. **Integrar ao carrinho:** guardar o frete escolhido (localStorage) e somar no total; recalcular a regra grátis-acima quando o subtotal mudar. Incluir bairro+frete na mensagem do pedido do WhatsApp.

### Fase 2 — Banner de capa novo
- Substituir o banner de capa atual pelo enviado pelo Bosco: `~/.../scratchpad/lira-banner-novo.jpg` (1280×721). Copiar pra `~/projetos/lira-fraldas-site/` (ex.: `banner-capa.jpg`) e trocar a referência no `index.html` (procurar o `<img>`/`background` do hero atual). Otimizar (webp/compress) se pesar.

### Fase 3 — Deploy + verificação
- `npx wrangler pages deploy . --project-name=lira-fraldas --branch=main --commit-dirty=true`.
- Verificar `https://lira-fraldas.pages.dev/` (=produção) e `https://lirafraldas.com.br/`: banner novo + consulta de frete funcionando (testar CEPs de bairros de cada faixa + um fora da lista).
- Commit no repo (gate de push do John).

## 5. Riscos
- **ViaCEP × grafia da tabela** — a normalização resolve a maioria; casos como "Praia do Futuro 1/2", "Cidade 2000", sub-bairros exigem regra/fallback manual (§3.4, §4-4).
- ViaCEP fora do ar / rate-limit → ter fallback (dropdown de bairro).
- Regra grátis-acima depende do subtotal atual → recalcular no carrinho, não só na consulta.

## 6. Gates
Sem credencial nova (ViaCEP é público). Deploy = Cloudflare Pages (branch main). Gate de push do John. **Confirmar o §3 com o Bosco antes de finalizar as regras.**
