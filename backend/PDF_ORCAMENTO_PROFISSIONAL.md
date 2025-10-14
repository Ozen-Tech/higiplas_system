# PDF de Orçamento Profissional - Documentação

## Visão Geral

O sistema de geração de PDFs de orçamento foi completamente reformulado para criar documentos profissionais e visualmente atraentes que podem ser enviados diretamente aos clientes.

## Melhorias Implementadas

### 1. **Classe Personalizada `OrcamentoPDF`**

Criamos uma classe que estende `FPDF` com métodos especializados para cada seção do orçamento:

- `header()` - Cabeçalho com logo e informações da empresa
- `footer()` - Rodapé com número da página e identificação do orçamento
- `titulo_orcamento()` - Título destacado com número e data
- `secao_cliente()` - Informações completas do cliente
- `secao_vendedor()` - Dados do vendedor e condições comerciais
- `tabela_produtos()` - Tabela formatada com produtos e valores
- `secao_observacoes()` - Termos e observações importantes

### 2. **Design Profissional**

#### Cabeçalho
- **Logo da empresa** (60mm de largura) no canto superior esquerdo
- **Informações da empresa** no canto superior direito:
  - Nome da empresa (HIGIPLAS INDÚSTRIA E COMÉRCIO)
  - CNPJ
  - Endereço completo
  - Telefone
  - Email de contato
- **Linha separadora azul** (#0066CC) para delimitar o cabeçalho

#### Rodapé
- Linha separadora cinza clara
- Número do orçamento e paginação centralizada
- Texto em itálico e cor cinza para não competir com o conteúdo

### 3. **Seções Bem Definidas**

#### Título do Orçamento
- Fonte grande (18pt) em azul (#0066CC)
- Número do orçamento formatado com 5 dígitos (ex: 00001)
- Data de emissão formatada (DD/MM/AAAA)

#### Dados do Cliente
- Box com fundo cinza claro (#F5F5F5)
- Informações organizadas:
  - Razão Social
  - CNPJ/CPF
  - Telefone e Email (na mesma linha)
  - Endereço completo

#### Informações do Orçamento
- Box com fundo cinza claro
- Dados do vendedor
- Condição de pagamento
- Validade do orçamento (30 dias)

#### Tabela de Produtos
- **Cabeçalho** com fundo cinza (#DCDCDC) e texto em negrito
- **Colunas**:
  - Item (numeração sequencial)
  - Descrição do Produto (até 45 caracteres)
  - Quantidade
  - Preço Unitário
  - Subtotal
- **Linhas alternadas** (branco e cinza muito claro) para melhor leitura
- **Total destacado** com fundo azul (#0066CC) e texto branco

#### Observações e Termos
- Lista de observações importantes:
  - Validade do orçamento
  - Condições de preço
  - Prazo de entrega
  - Frete
  - Condições de pagamento
- Mensagem de agradecimento em itálico

### 4. **Paleta de Cores**

- **Azul Principal**: #0066CC (RGB: 0, 102, 204)
  - Usado em títulos, cabeçalhos de seção e total
- **Cinza Claro**: #F5F5F5 (RGB: 245, 245, 245)
  - Usado em boxes de informação
- **Cinza Médio**: #DCDCDC (RGB: 220, 220, 220)
  - Usado no cabeçalho da tabela
- **Cinza Escuro**: #808080 (RGB: 128, 128, 128)
  - Usado em textos secundários

### 5. **Formatação de Valores**

- Valores monetários formatados com separador de milhares: `R$ 1.234,56`
- Alinhamento à direita para valores numéricos
- Alinhamento centralizado para quantidades
- Alinhamento à esquerda para descrições

### 6. **Estrutura de Arquivos**

```
backend/
├── app/
│   ├── routers/
│   │   └── orcamentos.py (código atualizado)
│   └── static/
│       └── HIGIPLAS-LOGO-2048x761.png (logo da empresa)
```

## Informações da Empresa (Para Atualizar)

**IMPORTANTE**: As informações da empresa no PDF são exemplos e devem ser atualizadas com os dados reais:

```python
# No método header() da classe OrcamentoPDF (linha ~40)
self.cell(70, 5, 'HIGIPLAS INDÚSTRIA E COMÉRCIO', 0, 1, 'R')
self.cell(70, 4, 'CNPJ: 00.000.000/0001-00', 0, 1, 'R')  # ← ATUALIZAR
self.cell(70, 4, 'Rua Exemplo, 123 - São Luís/MA', 0, 1, 'R')  # ← ATUALIZAR
self.cell(70, 4, 'Tel: (98) 3000-0000', 0, 1, 'R')  # ← ATUALIZAR
self.cell(70, 4, 'contato@higiplas.com.br', 0, 1, 'R')  # ← ATUALIZAR
```

## Como Usar

### Gerar PDF de um Orçamento

**Endpoint**: `GET /orcamentos/{orcamento_id}/pdf/`

**Exemplo de requisição**:
```bash
curl -X GET "http://localhost:8000/orcamentos/1/pdf/" \
  -H "Authorization: Bearer {token}" \
  --output orcamento_00001.pdf
```

**Resposta**:
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=orcamento_00001.pdf`

### No Frontend

O frontend pode fazer o download do PDF assim:

```typescript
const downloadPDF = async (orcamentoId: number) => {
  const response = await fetch(`/api/orcamentos/${orcamentoId}/pdf/`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `orcamento_${orcamentoId.toString().padStart(5, '0')}.pdf`;
  a.click();
};
```

## Exemplo de Saída

O PDF gerado terá aproximadamente esta estrutura:

```
┌─────────────────────────────────────────────────────────────┐
│ [LOGO]                    HIGIPLAS INDÚSTRIA E COMÉRCIO     │
│                           CNPJ: XX.XXX.XXX/XXXX-XX          │
│                           Endereço completo                  │
│                           Tel: (XX) XXXX-XXXX               │
│                           email@empresa.com                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│              ORÇAMENTO DE VENDA                             │
│              Nº 00001 - 15/01/2025                          │
│                                                              │
│ ┌─ DADOS DO CLIENTE ────────────────────────────────────┐  │
│ │ Razão Social: Cliente Exemplo Ltda                     │  │
│ │ CNPJ/CPF: XX.XXX.XXX/XXXX-XX                          │  │
│ │ Telefone: (XX) XXXX-XXXX    Email: cliente@email.com  │  │
│ │ Endereço: Rua Exemplo, 123 - Cidade/UF               │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ ┌─ INFORMAÇÕES DO ORÇAMENTO ────────────────────────────┐  │
│ │ Vendedor: João Silva                                   │  │
│ │ Condição de Pagamento: 30 dias                        │  │
│ │ Validade: 30 dias                                     │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ ┌─ PRODUTOS E SERVIÇOS ─────────────────────────────────┐  │
│ │ Item │ Descrição        │ Qtd │ Preço Unit. │ Subtotal│  │
│ ├──────┼──────────────────┼─────┼─────────────┼─────────┤  │
│ │  1   │ Produto A        │  10 │  R$ 100,00  │ R$ 1.000│  │
│ │  2   │ Produto B        │   5 │  R$ 200,00  │ R$ 1.000│  │
│ ├──────┴──────────────────┴─────┴─────────────┼─────────┤  │
│ │ VALOR TOTAL DO ORÇAMENTO                    │ R$ 2.000│  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ ┌─ OBSERVAÇÕES E TERMOS ────────────────────────────────┐  │
│ │ • Este orçamento tem validade de 30 dias...           │  │
│ │ • Os preços estão sujeitos a alteração...             │  │
│ │ • O prazo de entrega será informado...                │  │
│ │ • Frete não incluso no valor do orçamento.            │  │
│ │ • Pagamento conforme condição especificada acima.     │  │
│ │                                                        │  │
│ │ Agradecemos a preferência e estamos à disposição...   │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│        Orçamento #00001 - Página 1/1                        │
└─────────────────────────────────────────────────────────────┘
```

## Melhorias Futuras Sugeridas

1. **Configuração Dinâmica**
   - Criar tabela de configurações da empresa no banco de dados
   - Permitir atualização das informações via interface administrativa

2. **Personalização**
   - Permitir escolha de cores/tema por empresa
   - Opção de adicionar observações personalizadas por orçamento

3. **Recursos Adicionais**
   - QR Code para validação do orçamento
   - Assinatura digital
   - Gráficos de comparação de preços
   - Imagens dos produtos

4. **Internacionalização**
   - Suporte para múltiplos idiomas
   - Formatação de moeda por região

5. **Envio Automático**
   - Integração com email para envio automático ao cliente
   - Notificação de visualização do PDF

## Dependências

- `fpdf2` - Biblioteca para geração de PDFs
- `Pillow` (opcional) - Para manipulação avançada de imagens

## Testes

Para testar a geração do PDF:

1. Certifique-se de que há um orçamento criado no sistema
2. Faça uma requisição GET para `/orcamentos/{id}/pdf/`
3. Verifique se o PDF é baixado corretamente
4. Abra o PDF e verifique:
   - Logo aparece corretamente
   - Todas as seções estão formatadas
   - Valores estão corretos
   - Paginação funciona (para orçamentos grandes)

## Troubleshooting

### Logo não aparece
- Verifique se o arquivo `HIGIPLAS-LOGO-2048x761.png` está em `backend/app/static/`
- Verifique as permissões do arquivo
- Verifique o caminho no código (linha ~38 do arquivo)

### Caracteres especiais não aparecem
- O FPDF usa encoding `latin-1` por padrão
- Caracteres especiais são tratados automaticamente no código

### PDF muito grande
- Considere reduzir o tamanho da logo
- Otimize as imagens antes de adicionar ao PDF

## Commits Relacionados

- `a7b8382` - "feat: Create professional PDF for budget quotes with logo, header, footer and modern design"

## Autor

Sistema Higiplas - Desenvolvido em Janeiro/2025
