# Configurações Padrão da Apresentação

TITULO_PADRAO = "DESENVOLVIMENTO DE UM SISTEMA WEB PARA APOIO À CRIAÇÃO DE APRESENTAÇÕES DE TCC NO INSTITUTO FEDERAL DE SERGIPE"
INSTITUTO_PADRAO = "Instituto Federal de Sergipe"
SUBTITULO_PADRAO = "Discente: Seu Nome<br>Orientador: Nome do Orientador<br>Coorientadora: Nome da Coorientadora"

CONTEUDO_PADRAO = """## 1. Contextualização

- Padronização de documentos acadêmicos no IFS.
- Dificuldades no uso de ferramentas complexas (LaTeX) ou manuais (PowerPoint).
- Necessidade de automação para foco no conteúdo.

## 2. Problema de Pesquisa

> "Como facilitar a criação de slides para TCC garantindo a conformidade com as normas visuais do instituto?"

## 3. Objetivos

### Objetivo Geral
Desenvolver uma ferramenta web intuitiva para geração automática de apresentações.

### Objetivos Específicos
- Simplificar a formatação através de Markdown.
- Garantir a identidade visual do IFS.
- Permitir exportação em HTML interativo (Reveal.js).

## 4. Metodologia

- **Backend:** Python + Streamlit.
- **Motor de Renderização:** Quarto CLI.
- **Frontend:** HTML5 + CSS3 (Sass).

## 5. Cronograma e Resultados

| Etapa | Status | Prazo |
|-------|--------|-------|
| Levantamento | Concluído | Jan/24 |
| Prototipagem | Concluído | Fev/24 |
| Desenvolvimento| Em andamento | Mar/24 |

## 6. Exemplo de Layout em Colunas

:::: {.columns}

::: {.column width="50%"}
**Vantagens do Sistema**

- Foco no texto
- Layout automático
- Responsivo
:::

::: {.column width="50%"}
**Tecnologias**

![](https://placeholder.pics/svg/300x200/DEDEDE/555555/Python+Streamlit)
:::

::::

## 7. Multimídia

A ferramenta suporta integração direta com vídeos. Defina `width` e `height` para ajustar o tamanho:

{{< video https://www.youtube.com/watch?v=wo9vZccmqwc width="100%" height="500" >}}

## 8. Slide com Rolagem (Scrollable) {.scrollable}

Este slide possui a propriedade `.scrollable`. É útil para conteúdos extensos que excedem a altura do slide. A barra de rolagem aparecerá automaticamente.

1.  Referência bibliográfica 1
2.  Referência bibliográfica 2
3.  Referência bibliográfica 3
4.  Referência bibliográfica 4
5.  Referência bibliográfica 5
6.  Referência bibliográfica 6
7.  Referência bibliográfica 7
8.  Referência bibliográfica 8
9.  Referência bibliográfica 9
10. Referência bibliográfica 10
11. Referência bibliográfica 11
12. Referência bibliográfica 12

## 9. Animações (Fragmentos)

Elementos que aparecem sequencialmente ao avançar o slide:

::: {.fragment}
➡️ **Primeiro Ponto**
:::

::: {.fragment}
➡️ **Segundo Ponto**
:::

::: {.fragment .fade-up}
🚀 **Texto com animação de subida**
:::

## 10. Diagramas e Interatividade

::: {.panel-tabset}

### Fluxograma

```{mermaid}
flowchart LR
  A[Usuário] --> B(Interface Streamlit)
  B --> C{Processamento}
  C -->|Gera| D[Markdown]
  C -->|Renderiza| E[HTML/Reveal.js]
  E -.-> A
```

### Código Fonte

```python
# Exemplo de código Python
import streamlit as st

def main():
    st.write("Apresentação Gerada!")
```

:::

## 11. Caixas de Destaque (Callouts)

As "Callouts" são ótimas para destacar informações:

::: {.callout-note}
Esta é uma nota de lembrete simples.
:::

::: {.callout-tip}
## Dica Importante
Você pode colocar títulos nas callouts usando `## Título`.
:::

::: {.callout-important}
Atenção para prazos e normas.
:::

## 12. Equações Matemáticas (LaTeX)

O Quarto renderiza equações perfeitamente usando sintaxe LaTeX:

**Equação Inline:** $E = mc^2$

**Bloco de Equação:**
$$
\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{v}) = 0
$$

## 13. Código com Destaque

Você pode destacar linhas específicas do código para focar a explicação (observe as linhas 2 e 4):

```python {code-line-numbers="2,4"}
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.show()
```

## 14. Notas de Rodapé

Podemos adicionar notas de rodapé facilmente para citar fontes ou explicar termos[^1].

[^1]: Esta é a nota de rodapé. Ela aparecerá automaticamente organizada.

## 15. Considerações Finais

A ferramenta demonstra viabilidade técnica e potencial para auxiliar discentes na etapa final de seus cursos.
"""