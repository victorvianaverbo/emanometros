# Press Control — Especificação Completa de Layout

## Linguagem Visual Aprovada

```
Paleta:
  --navy:          #0A1628
  --navy-light:    #152238
  --steel-blue:    #1E3A5F
  --electric-blue: #0078D4
  --cyan:          #00B4D8
  --amber:         #F59E0B
  --slate-50:      #F8FAFC
  --slate-100:     #F1F5F9
  --slate-200:     #E2E8F0
  --slate-400:     #94A3B8
  --slate-600:     #475569
  --slate-900:     #0F172A
  --whatsapp:      #25D366
  --success:       #10B981
  --danger:        #EF4444

Fontes:
  Display: 'Plus Jakarta Sans', 800/700/600
  Body:    'DM Sans', 400/500
  Mono:    'JetBrains Mono', 400/500

Container: max-width 1280px, padding 0 32px
Border-radius: 6px (sm), 10px (md), 14px (lg), 20px (xl), 100px (full)
```

---

## Seção 1: Topbar

### Arquétipo e Constraints
- Arquétipo: Balanced (Density-Based)
- Constraints: High Contrast (Cor), Texto Typewriter (Tipografia)
- Justificativa: Barra de informação precisa ser lida rápido. Contraste alto garante visibilidade, texto rotativo mantém engajamento sem ocupar espaço.

### Conteúdo
3 mensagens rotativas (troca a cada 4s com fade):
1. "Personalizamos manômetros com sua logo — solicite um orçamento"
2. "Envio para todo Brasil — frete grátis MG acima de R$300"
3. "Atendimento técnico especializado via WhatsApp"

### Layout
- Full width, posição fixa acima da navbar
- Altura: 36px
- Display: flex, align-items center, justify-content center
- gap: 8px entre ícone e texto

### Tipografia
- Fonte: var(--font-body) DM Sans
- Tamanho: 0.75rem (12px)
- Peso: 500
- Letter-spacing: 0.02em
- Cor: #FFFFFF

### Cores
- Background: var(--electric-blue) #0078D4
- Texto: #FFFFFF
- Ícone (seta/ponto): rgba(255,255,255,0.6)

### Animações
- Troca de mensagens: fade out 400ms ease → fade in 400ms ease
- Intervalo: 4000ms
- Pausa ao hover

### Responsividade
- Mobile: font-size 0.65rem, padding 0 16px, height 32px
- Mensagens mais curtas mobile: "Personalize com logo" | "Frete grátis MG" | "Atendimento WhatsApp"

---

## Seção 2: Navbar (APROVADA — manter como está)

Referência: index.html linhas 31-46 + style.css .navbar
- Fixa, top: 36px (abaixo da topbar), backdrop-filter blur(20px)
- Altura: 72px
- Logo: "e" cyan + "Manômetros" branco, Plus Jakarta Sans 600
- CTA WhatsApp: #25D366, border-radius 100px

---

## Seção 3: Hero (APROVADO — manter como está)

Referência: index.html linhas 52-145 + style.css .hero
- Arquétipo: Split Assimétrico
- Constraints: Noise Texture, Headline >150px, Gradiente Linear
- Gauge SVG animado à direita com specs flutuantes
- 4 diferenciais inline em grid 2x2
- Stats bar inferior
- min-height: 100vh, padding-top: 108px (topbar 36 + navbar 72)

---

## Seção 4: Barra de Confiança (APROVADA — manter como está)

Referência: index.html linhas 148-171 + style.css .trust
- Fundo branco, border-bottom 1px slate-200
- 5 itens com ícones SVG stroke #0078D4
- DM Sans 500, 0.85rem, cor slate-600

---

## Seção 5: Categorias

### Arquétipo e Constraints
- Arquétipo: Bento Box (Grid-Based)
- Constraints: Hover Lift (Interação), Gradiente Linear (Cor), Clip-path Section (Layout)
- Justificativa: Bento box cria hierarquia visual — a categoria principal (Manômetros) ocupa espaço maior, mostrando que é o core do negócio. As demais têm peso igual. Hover lift dá feedback tátil industrial.

### Conteúdo
- Label: "Explore por Categoria"
- Título: "Encontre o instrumento certo para sua operação"
- 4 categorias + 1 acessórios (ver copy.md seção 5)

### Layout
```
Desktop (1280px):
┌─────────────────────┬────────────┐
│                     │ Manovac.   │
│   MANÔMETROS        ├────────────┤
│   (card grande)     │ Vacuôm.    │
├──────────┬──────────┼────────────┤
│ Termôm.  │ Acessór. │            │
└──────────┴──────────┘            │
                                    (esta célula não existe)

Correção — Grid real:
grid-template-columns: 1fr 1fr 1fr
grid-template-rows: auto auto

Card 1 - Manômetros: grid-column 1/2, grid-row 1/3 (ocupa 2 rows)
Card 2 - Manovacuômetros: grid-column 2/3, grid-row 1/2
Card 3 - Vacuômetros: grid-column 3/4, grid-row 1/2
Card 4 - Termômetros: grid-column 2/3, grid-row 2/3
Card 5 - Acessórios: grid-column 3/4, grid-row 2/3
```
- Container: max-width 1280px
- Padding seção: 96px 0
- Gap entre cards: 20px
- Background seção: var(--slate-50) #F8FAFC

### Card de Categoria
```
Estrutura interna:
- Padding: 32px
- Border-radius: 14px
- Background: #FFFFFF
- Border: 1px solid var(--slate-200)
- Overflow: hidden
- Position: relative

Conteúdo:
- Ícone SVG no topo (32x32, stroke var(--electric-blue), stroke-width 2)
  - Manômetros: gauge/manometer
  - Manovacuômetros: gauge com seta dupla (±)
  - Vacuômetros: gauge com seta para baixo
  - Termômetros: termômetro industrial
  - Acessórios: chave/ferramenta
- Nome da categoria: Plus Jakarta Sans 700, 1.3rem, var(--slate-900), margin-top 16px
- Descrição: DM Sans 400, 0.85rem, var(--slate-600), line-height 1.6, margin-top 8px, max 2 linhas
- Link "Ver Produtos →": DM Sans 600, 0.8rem, var(--electric-blue), margin-top 16px
- Contagem (no card grande): JetBrains Mono 500, 0.7rem, var(--slate-400)

Card grande (Manômetros):
- min-height: 340px
- Background: linear-gradient(135deg, var(--navy) 0%, var(--steel-blue) 100%)
- Nome: cor #FFFFFF, font-size 1.6rem
- Descrição: cor var(--slate-400)
- Link: cor var(--cyan)
- Ícone: stroke var(--cyan)
- Elemento decorativo: gauge outline SVG grande (opacity 0.05) no canto inferior direito, 200x200px
```

### Cores
- Card normal: bg #FFFFFF, border #E2E8F0
- Card Manômetros: bg gradient navy → steel-blue, border rgba(0,180,216,0.15)
- Hover card normal: border transparent, shadow 0 20px 60px rgba(10,22,40,0.08)
- Hover card Manômetros: shadow 0 20px 60px rgba(0,120,212,0.15)

### Animações
- Entrada: fade-up 800ms ease-out, stagger 100ms entre cards, trigger at 20% viewport (IntersectionObserver)
- Hover: translateY(-6px) 350ms cubic-bezier(0.25, 0.46, 0.45, 0.94)
- Link "→": translateX(4px) no hover, 200ms ease

### Responsividade
- Tablet (≤1024px): grid-template-columns 1fr 1fr, card Manômetros ocupa 1 col 2 rows
- Mobile (≤768px): grid-template-columns 1fr, todos os cards full width, card Manômetros min-height 200px
- Mobile: gap 12px

---

## Seção 6: Produtos em Destaque

### Arquétipo e Constraints
- Arquétipo: Balanced (Density-Based)
- Constraints: Hover Scale (Interação), Stagger (Movimento), Selective Color (Cor)
- Justificativa: Grid balanceado para catálogo — o foco é nos produtos, não na composição. Hover scale dá feedback de interatividade. Stagger na entrada cria ritmo. Cor seletiva destaca badges e CTAs sem poluir.

### Conteúdo
- Label: "Catálogo"
- Título: "Produtos em Destaque"
- Subtítulo: "Instrumentos rigorosamente selecionados e testados para sua operação"
- Link: "Ver todos os produtos →"
- 8 ProductCards (ver copy.md seção 6)

### Layout
```
Header:
- Display: flex, justify-content space-between, align-items flex-end
- Label acima do título
- Link "Ver todos →" alinhado à direita

Grid de produtos:
- grid-template-columns: repeat(4, 1fr)
- gap: 20px
- margin-top: 48px
```
- Container: max-width 1280px
- Padding seção: 96px 0
- Background seção: #FFFFFF

### ProductCard (componente reutilizável)
```
Estrutura:
┌──────────────────────────┐
│ [Badge]          ← absolute top-right
│                          │
│    ┌──────────────┐      │
│    │  FOTO 1:1    │      │ ← aspect-ratio 1/1, bg slate-50
│    │  do produto  │      │    object-fit contain, padding 16px
│    └──────────────┘      │
│                          │
│ CATEGORIA               │ ← label mono
│ Nome do Produto          │ ← título
│ (max 2 linhas)           │
│                          │
│ 100mm | Inox | 1/2"      │ ← specs mono
│                          │
│ ┌──────────────────────┐ │
│ │ Pedir Orçamento  💬  │ │ ← CTA WhatsApp
│ └──────────────────────┘ │
└──────────────────────────┘

Medidas:
- Padding: 0 (imagem vai edge-to-edge no topo)
- Padding conteúdo: 0 20px 20px 20px
- Border-radius: 14px
- Background: #FFFFFF
- Border: 1px solid var(--slate-200)
- Overflow: hidden

Imagem:
- Aspect-ratio: 1/1
- Background: var(--slate-50) #F8FAFC
- Padding interno: 20px
- Object-fit: contain
- Placeholder: ícone de manômetro SVG outline (opacity 0.15) se sem imagem

Badge (absolute):
- Position: absolute, top 12px, right 12px
- Padding: 4px 12px
- Border-radius: 100px
- Font: JetBrains Mono 500, 0.65rem
- Letter-spacing: 0.04em
- "Pronta Entrega": bg rgba(16,185,129,0.1), color #10B981, border 1px solid rgba(16,185,129,0.2)
- "Sob Consulta": bg rgba(245,158,11,0.1), color #F59E0B, border 1px solid rgba(245,158,11,0.2)

Categoria label:
- Font: JetBrains Mono 500, 0.65rem
- Color: var(--electric-blue) #0078D4
- Text-transform: uppercase
- Letter-spacing: 0.1em
- Margin-top: 16px

Nome:
- Font: Plus Jakarta Sans 700, 1rem
- Color: var(--slate-900) #0F172A
- Line-height: 1.3
- Margin-top: 6px
- Display: -webkit-box, -webkit-line-clamp 2, overflow hidden

Specs:
- Font: JetBrains Mono 400, 0.75rem
- Color: var(--slate-400) #94A3B8
- Margin-top: 8px
- White-space: nowrap, overflow hidden, text-overflow ellipsis

CTA WhatsApp:
- Margin-top: 16px
- Width: 100%
- Padding: 12px 16px
- Background: var(--whatsapp) #25D366
- Color: #FFFFFF
- Font: DM Sans 600, 0.8rem
- Border-radius: 10px
- Display: flex, align-items center, justify-content center, gap 8px
- Ícone WhatsApp SVG 16x16 à direita
- Hover: background var(--whatsapp-dark) #1DA851, translateY(-1px), shadow 0 4px 16px rgba(37,211,102,0.3)
- Transition: all 250ms ease
```

### Cores
- Card hover: border transparent, shadow 0 12px 40px rgba(10,22,40,0.06), translateY(-4px)
- Imagem hover: scale(1.05) 400ms ease

### Animações
- Entrada cards: fade-up 600ms ease-out, stagger 80ms, trigger at 15% viewport
- Badge "Pronta Entrega": pulse sutil no dot (se adicionado)
- Hover card: translateY(-4px) + shadow, 300ms cubic-bezier(0.25, 0.46, 0.45, 0.94)
- Hover imagem: scale(1.05) 400ms ease (dentro do overflow hidden)

### Responsividade
- Tablet (≤1024px): grid-template-columns repeat(3, 1fr)
- Mobile (≤768px): grid-template-columns repeat(2, 1fr), gap 12px
- Mobile (≤420px): grid-template-columns 1fr (single column)
- Mobile: ProductCard nome font-size 0.9rem, specs font-size 0.7rem
- Mobile: CTA padding 10px 12px, font-size 0.75rem

---

## Seção 7: Por Que Escolher a Press Control (APROVADA — manter como está)

Referência: index.html linhas 175-240 + style.css .why
- Arquétipo: Grid Assimétrico
- Constraints: Hover Lift, Gradiente Linear, Noise Texture
- 4 cards, card 01 (Personalização) em destaque dark
- Ícones industriais: manômetro, caixa, capacete, paquímetro
- Background: var(--slate-50)

---

## Seção 8: CTA B2B

### Arquétipo e Constraints
- Arquétipo: Contained Center (Focus-Based)
- Constraints: Gradiente Mesh (Cor), Noise Texture (Efeitos Especiais), Hover Glow (Interação)
- Justificativa: Foco central único — a mensagem B2B precisa ser direta e impactante. Gradiente mesh é sofisticado (não linear genérico). Noise adiciona textura metálica. Glow no botão chama atenção.

### Conteúdo
- Label: "Para empresas"
- Título: "Compra em Volume?"
- Subtítulo: "Condições especiais para revendedores e indústrias. Solicite um orçamento personalizado."
- CTA: "Solicitar Orçamento" → WhatsApp
- Sub-CTA: "ou ligue: (31) 99972-8693"

### Layout
- Full width
- Padding: 80px 0
- Container interno: max-width 720px, text-align center
- Elementos empilhados verticalmente com gaps

### Tipografia
- Label: JetBrains Mono 500, 0.75rem, uppercase, letter-spacing 0.12em, var(--cyan)
- Título: Plus Jakarta Sans 800, clamp(2rem, 4vw, 3rem), #FFFFFF, letter-spacing -0.03em
- Subtítulo: DM Sans 400, 1rem, var(--slate-400), line-height 1.6, max-width 520px, margin 0 auto
- Sub-CTA: DM Sans 400, 0.85rem, var(--slate-400)

### Cores
- Background: linear-gradient(135deg, var(--navy) 0%, #0d2847 50%, var(--steel-blue) 100%)
- Noise overlay: opacity 0.04
- Borda superior: 1px solid rgba(0,180,216,0.1)
- Borda inferior: 1px solid rgba(0,180,216,0.1)

### CTA Button
- Padding: 16px 40px
- Background: var(--electric-blue) #0078D4
- Color: #FFFFFF
- Font: DM Sans 700, 1rem
- Border-radius: 10px
- Margin-top: 32px
- Hover: background #0063b1, shadow 0 0 30px rgba(0,120,212,0.4), translateY(-2px)
- Transition: all 300ms ease

### Elementos Decorativos
- 2 linhas horizontais finas (1px, rgba(0,180,216,0.1)) acima e abaixo do conteúdo, max-width 200px, margin auto
- Elemento subtle: gradient orb (radial-gradient circular, cyan opacity 0.05) atrás do título, 300x300px, blur 100px

### Animações
- Entrada: fade-up 800ms ease-out, trigger at 30% viewport
- Título: delay 0ms, subtítulo delay 150ms, botão delay 300ms
- Orb: float lento (translateY ±10px, 6s ease-in-out infinite)

### Responsividade
- Mobile: padding 60px 20px
- Mobile: título clamp(1.6rem, 6vw, 2.5rem)

---

## Seção 9: Depoimentos

### Arquétipo e Constraints
- Arquétipo: Card Stack (Layer-Based)
- Constraints: Hover Slide (Interação), Stagger (Movimento), Glassmorphism (Efeitos Especiais)
- Justificativa: Cards empilhados criam profundidade e confiança (muitas vozes concordando). Hover slide revela mais do depoimento. Glassmorphism sutil adiciona modernidade.

### Conteúdo
- Label: "O que nossos clientes dizem"
- Título: "A parceria certa para sua operação não parar"
- 3 depoimentos (ver copy.md seção 9)

### Layout
```
Desktop:
- Container: max-width 1280px
- Header à esquerda (max-width 400px)
- Cards à direita em grid 1fr 1fr 1fr com offset vertical

┌──────────────────────────────────────────────┐
│ Label              │ Card 1  │ Card 2 │ Card 3 │
│ Título             │ (normal)│(+16px) │(normal)│
│                    │         │ offset │        │
└──────────────────────────────────────────────┘

Display: grid, grid-template-columns: 1fr 2fr
Gap: 48px entre header e cards
Cards grid: grid-template-columns repeat(3, 1fr), gap 20px
Card 2: margin-top 24px (offset visual)
```
- Padding seção: 96px 0
- Background: #FFFFFF

### Card de Depoimento
```
- Padding: 32px
- Background: var(--slate-50)
- Border: 1px solid var(--slate-200)
- Border-radius: 14px
- Position: relative

Conteúdo:
- Aspas decorativas: " (caractere tipográfico)
  Font: Plus Jakarta Sans 800, 4rem, var(--slate-200), position absolute, top 16px, left 24px, line-height 1
- Texto do depoimento: DM Sans 400, 0.9rem, var(--slate-600), line-height 1.7, position relative (z-index 1)
- Separador: linha 32px x 2px, var(--electric-blue), margin 20px 0
- Nome: Plus Jakarta Sans 600, 0.85rem, var(--slate-900)
- Cargo/Empresa: DM Sans 400, 0.75rem, var(--slate-400)
```

### Animações
- Entrada: fade-up 600ms ease-out, stagger 150ms entre cards, trigger at 20% viewport
- Card 2 delay extra de 100ms (por causa do offset)
- Hover: translateY(-4px), border-color rgba(0,120,212,0.2), shadow 0 12px 40px rgba(10,22,40,0.06)
- Transition: all 350ms ease

### Responsividade
- Tablet (≤1024px): grid single column (header em cima, cards embaixo), cards grid 3 cols
- Mobile (≤768px): cards grid 1 col, sem offset no card 2
- Mobile: card padding 24px, aspas font-size 3rem

---

## Seção 10: Blog Preview

### Arquétipo e Constraints
- Arquétipo: Editorial (Typography-Based)
- Constraints: Hover Reveal (Interação), Fade Up (Movimento), Imagem com Overlay (Mídia)
- Justificativa: Seção de conteúdo pede tratamento editorial. Hover reveal mostra excerpt no card. Overlay nas imagens cria consistência visual mesmo com imagens de qualidade variável.

### Conteúdo
- Label: "Conteúdo Técnico"
- Título: "Artigos para quem trabalha com instrumentação"
- 3 artigos (ver copy.md seção 10)

### Layout
```
Desktop:
- Container: max-width 1280px
- Header centralizado: text-align center, max-width 600px, margin 0 auto
- Grid de artigos: grid-template-columns repeat(3, 1fr), gap 24px, margin-top 48px
```
- Padding seção: 96px 0
- Background: var(--slate-50)

### Card de Artigo
```
- Border-radius: 14px
- Background: #FFFFFF
- Border: 1px solid var(--slate-200)
- Overflow: hidden

Imagem:
- Aspect-ratio: 16/9
- Background: var(--navy) (placeholder, sem imagem real por enquanto)
- Overlay: linear-gradient(to top, rgba(10,22,40,0.6) 0%, transparent 50%)
- Ícone central (placeholder): SVG outline de artigo/livro, 48x48, stroke rgba(255,255,255,0.15)

Conteúdo (padding 24px):
- Categoria tag: JetBrains Mono 500, 0.65rem, var(--electric-blue), uppercase, letter-spacing 0.1em
  Tags: "Guia Técnico" | "Manutenção" | "Normas"
- Título: Plus Jakarta Sans 700, 1.05rem, var(--slate-900), line-height 1.3, margin-top 8px
  Display: -webkit-box, -webkit-line-clamp 2
- Excerpt: DM Sans 400, 0.8rem, var(--slate-600), line-height 1.6, margin-top 8px
  Display: -webkit-box, -webkit-line-clamp 2
- Link "Ler artigo →": DM Sans 600, 0.8rem, var(--electric-blue), margin-top 16px
  Hover: translateX(4px), color var(--cyan)
```

### Animações
- Entrada: fade-up 600ms ease-out, stagger 120ms, trigger at 20% viewport
- Hover card: translateY(-4px), shadow 0 12px 40px rgba(10,22,40,0.06)
- Hover imagem: scale(1.05), overlay opacity diminui levemente
- Link "→": translateX(4px) 200ms ease

### Responsividade
- Tablet (≤1024px): grid 2 cols (3o artigo hidden ou full-width abaixo)
- Mobile (≤768px): grid 1 col, scroll horizontal opcional

---

## Seção 11: CTA Final

### Arquétipo e Constraints
- Arquétipo: Hero Dominante (Focus-Based)
- Constraints: Gradiente Linear (Cor), Noise Texture (Efeitos Especiais), Scale In (Movimento)
- Justificativa: Encerramento com impacto. Mesmo tratamento visual do hero para criar bookend. Gradiente e noise mantêm consistência com o topo da página.

### Conteúdo
- Título: "Pronto para Elevar o Nível de Controle dos Seus Processos?"
- Subtítulo: "Explore nosso catálogo completo ou fale agora mesmo com um de nossos especialistas."
- CTA Principal: "Falar com Especialista" → WhatsApp (verde)
- CTA Secundário: "Ver Catálogo" → scroll to #categorias (outline)

### Layout
- Full width
- Padding: 96px 0
- Text-align: center
- Container interno: max-width 700px, margin 0 auto

### Tipografia
- Título: Plus Jakarta Sans 800, clamp(1.8rem, 3.5vw, 2.5rem), #FFFFFF, letter-spacing -0.03em, line-height 1.15
- Subtítulo: DM Sans 400, 1rem, var(--slate-400), line-height 1.6, margin-top 16px
- Botões: margin-top 32px, gap 16px entre botões

### Cores
- Background: linear-gradient(135deg, var(--navy) 0%, var(--steel-blue) 100%)
- Noise overlay: opacity 0.035
- Borda superior: 1px solid rgba(255,255,255,0.06)

### Botões
CTA Principal (WhatsApp):
- Padding: 16px 32px
- Background: var(--whatsapp) #25D366
- Color: #FFFFFF
- Font: DM Sans 700, 0.95rem
- Border-radius: 10px
- Ícone WhatsApp SVG 18x18
- Hover: bg #1DA851, shadow 0 8px 30px rgba(37,211,102,0.3), translateY(-2px)

CTA Secundário:
- Padding: 16px 32px
- Background: transparent
- Color: #FFFFFF
- Border: 1px solid rgba(255,255,255,0.2)
- Font: DM Sans 600, 0.95rem
- Border-radius: 10px
- Hover: bg rgba(255,255,255,0.05), border-color rgba(255,255,255,0.4)

### Animações
- Entrada: fade-up 800ms ease-out, trigger at 30% viewport
- Título delay 0ms, subtítulo 150ms, botões 300ms

### Responsividade
- Mobile: padding 60px 20px, botões flex-direction column, width 100%

---

## Seção 12: Footer

### Arquétipo e Constraints
- Arquétipo: Dense (Density-Based)
- Constraints: Monocromático (Cor), Hover Underline (Interação)
- Justificativa: Footer é denso por natureza — muita informação em pouco espaço. Tratamento monocromático em navy mantém subordinação visual ao conteúdo principal. Hover underline sutil para links.

### Layout
```
Desktop:
┌─────────────────────────────────────────────┐
│ FOOTER PRINCIPAL (padding 64px 0)           │
│                                             │
│ [Logo +     [Produtos]  [Instit.]  [Contato]│
│  Descrição]                                 │
│  (col 1)     (col 2)    (col 3)   (col 4)  │
│                                             │
│ grid-template-columns: 1.5fr 1fr 1fr 1fr    │
│ gap: 48px                                   │
├─────────────────────────────────────────────┤
│ FOOTER BAR (padding 24px 0)                 │
│ border-top: 1px solid rgba(255,255,255,0.06)│
│                                             │
│ © 2026 Press Control          [Insta] [WhatsApp]│
│                                             │
│ flex, justify-content space-between         │
└─────────────────────────────────────────────┘
```
- Background: var(--navy) #0A1628
- Container: max-width 1280px

### Coluna 1: Sobre
- Logo: "e" cyan + "Manômetros" branco (mesmo da navbar, font-size 1.3rem)
- Descrição: DM Sans 400, 0.85rem, var(--slate-400), line-height 1.6, margin-top 16px, max-width 280px
- Texto: "Instrumentação industrial com precisão, qualidade e entrega rápida."

### Coluna 2: Produtos
- Título coluna: Plus Jakarta Sans 600, 0.8rem, #FFFFFF, uppercase, letter-spacing 0.08em, margin-bottom 20px
- Links: DM Sans 400, 0.85rem, var(--slate-400)
  - Manômetros
  - Manovacuômetros
  - Vacuômetros
  - Termômetros
  - Acessórios
  - Personalização
- Link spacing: 12px entre itens
- Hover: color #FFFFFF, transition 200ms ease

### Coluna 3: Institucional
- Mesmo estilo da coluna 2
- Links: Sobre Nós, Blog, Contato, Política de Trocas, Privacidade

### Coluna 4: Contato
- Mesmo título da coluna 2
- Itens com ícone + texto:
  - WhatsApp: ícone SVG 16x16 + "(31) 99972-8693" → link wa.me
  - Email: ícone + "contato@presscontrol.com.br" → mailto
  - Endereço: ícone + "Rua Platina, 693 - Prado, BH"
  - Horário: ícone + "Seg-Sex 8h-18h | Sáb 8h-12h"
- Font ícone+texto: DM Sans 400, 0.85rem, var(--slate-400)
- Gap entre ícone e texto: 10px
- Ícones: stroke var(--slate-400), 16x16

### Footer Bar
- Copyright: DM Sans 400, 0.75rem, var(--slate-400)
- Redes sociais: 2 ícones (Instagram, WhatsApp), 20x20, stroke var(--slate-400)
  - Hover: stroke #FFFFFF, transition 200ms

### Responsividade
- Tablet (≤1024px): grid 2x2
- Mobile (≤768px): grid 1 col, coluna 1 text-align center, demais colunas collapsible ou empilhadas
- Mobile: footer bar flex-direction column, gap 12px, text-align center

---

## Seção 13: WhatsApp Float (APROVADO — manter como está)

Referência: index.html linhas 242-250 + style.css .whatsapp-float
- Position: fixed, bottom 24px, right 24px
- Width/height: 60px
- Background: #25D366
- Border-radius: 50%
- Shadow: 0 4px 20px rgba(37,211,102,0.4)
- Ring animation: 3s infinite

---

## Elementos Encantadores Planejados

### Micro-interações
1. **Topbar rotativo** — mensagens trocam com fade suave a cada 4s
2. **Product card hover** — imagem faz scale sutil, card sobe, shadow cresce
3. **CTA WhatsApp pulse** — ao entrar no viewport, botão faz um pulse sutil (scale 1→1.02→1) uma única vez
4. **Links "→"** — seta se move 4px à direita no hover
5. **Badge "Pronta Entrega"** — dot com pulse animation (como o badge do hero)

### Animações de Entrada
6. **Stagger nos products** — cada card entra 80ms depois do anterior, criando efeito cascata
7. **Depoimentos offset** — card central está 24px abaixo, criando composição dinâmica
8. **Categorias Bento** — card grande entra primeiro, depois os menores em stagger
9. **Números/stats** — counter animation (0 → valor final) ao entrar no viewport

### Detalhes de Craft
10. **Noise texture** — presente no hero, CTA B2B e CTA final (consistência metallic)
11. **Gradient orb** — no CTA B2B, orb de luz sutil flutuando atrás do título
12. **Aspas tipográficas** — nos depoimentos, aspas enormes decorativas em cor sutil
13. **Cards de categoria** — gauge SVG outline decorativo no card de Manômetros (opacity 0.05)

### Elementos de Surpresa
14. **Scroll progress** — barra fina no topo (1px) mostrando progresso da página, cor cyan
15. **Back to top** — aparece ao scrollar 50% da página, ícone seta para cima, posição fixed left
