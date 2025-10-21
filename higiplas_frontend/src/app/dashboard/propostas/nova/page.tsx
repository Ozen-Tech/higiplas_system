"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { usePropostas } from '@/hooks/usePropostas'
import { useClientesV2 } from '@/hooks/useClientesV2'
import { ClienteV2 } from '@/types'
import toast from 'react-hot-toast'
import { apiService } from '@/services/apiService'

import { ItemPropostaCreate, PropostaCreatePayload } from '@/types/propostas'
import { Header } from '@/components/Header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ArrowLeft, Plus, Trash2, FileText, Share2, X } from 'lucide-react'
import { Label } from '@/components/ui/label'

// Lista de produtos padrão da Higiplas com informações completas
const PRODUTOS_HIGIPLAS = [
  {
    nome: "OXIPRO 5L",
    titulo: "Limpador multiuso",
    descricao: "Oxipro: é um moderno e eficaz multiuso concentrado, destinado a limpeza e higienização de superfícies em geral. (LIMPADOR DE MDF, GRANITO, VIDROS, PISOS EM GERAL PARA LAVAGEM OU MANUTENÇÃO)",
    rendimento: "500"
  },
  {
    nome: "SANIFLOR MAX 5L",
    titulo: "Desinfetante bactericida",
    descricao: "Saniflor Max: Poderoso desinfetante bactericida a base do moderno quarternário de amonia de 5ª geração, concentrado aromatizado, ação bactericida comprovada.",
    rendimento: "250"
  },
  {
    nome: "PLASTILUX 5L",
    titulo: "Limpador multiuso",
    descricao: "PLASTILUX: é um limpador multiuso de grande poder de limpeza destinado a limpeza de mesas, fórmicas, plasticos e superfícies assemelhadas.",
    rendimento: "50"
  },
  {
    nome: "CERACRIL",
    titulo: "Impermeabilizante Acrílico Auto Brilho",
    descricao: "CERACRIL é uma cera acrílica auto brilho, antiderrapante, que não necessita de lustro com enceradeiras. CERACRIL facilita muito a manutenção de pisos encerados, promovendo brilho e proteção de pisos com baixo custo e excelente desempenho.",
    rendimento: "PURO"
  },
  {
    nome: "GEL SANITIZANTE 1L",
    titulo: "Para mãos",
    descricao: "Gel Sanitizante: pode ser utilizado como sanitizante das mãos, e em sanitização em geral.",
    rendimento: "PURO"
  },
  {
    nome: "LIMPAX 5L",
    titulo: "Detergente para louça manual",
    descricao: "Limpax: é um detergente para louça de altíssimo poder de limpeza e com grande suavidade no contato com as mãos.",
    rendimento: "100"
  },
  {
    nome: "DETERGENTE CLORADO 5L",
    titulo: "Desengraxante com cloro (RENDIMENTO ATÉ 500L)",
    descricao: "Detergente Clorado: é um produto que combina o efeito de um desengraxante com poder de limpeza e remoção, apresentando alto poder de limpeza em azulejos, pisos, inox e demais ambientes. (SUBSTITUI: ÁGUA SANITÁRIA, DETERGENTE, SABÃO EM PÓ)",
    rendimento: "500"
  },
  {
    nome: "DESINCROST",
    titulo: "Desincrustante e descarbonizante",
    descricao: "Desincrustante e descarbonizante para limpeza de fornos, fogões, fornos combinados, grelhas, coifas, pisos e paredes de cozinhas profissionais.",
    rendimento: "25 (fornos) / 500 (pisos)"
  },
  {
    nome: "CLORO ATIVO",
    titulo: "Desinfetante concentrado",
    descricao: "Desinfetante concentrado à base de Hipoclorito de sódio a 12% para desinfecção e limpeza de superfícies, equipamentos, piscinas e caixas d'água.",
    rendimento: "1250 (desinfecção) / 55 (limpeza pesada)"
  },
  {
    nome: "SEC MAQ",
    titulo: "Secante e abrilhantador",
    descricao: "Secante e abrilhantador de louças para máquinas de lavar, proporcionando secagem rápida e brilho.",
    rendimento: "Varia com o ciclo da máquina"
  },
  {
    nome: "LOUÇA MAQ PRO",
    titulo: "Detergente para máquinas",
    descricao: "Detergente líquido concentrado para máquinas de lavar louças, removendo resíduos gordurosos e de amido.",
    rendimento: "1000 a 5000"
  },
  {
    nome: "LAVENE AE",
    titulo: "Detergente desengordurante neutro",
    descricao: "Detergente desengordurante neutro concentrado com baixa espumação para diversos tipos de limpeza, inclusive em máquinas automáticas.",
    rendimento: "250 a 1000"
  },
  {
    nome: "SANILUX",
    titulo: "Desincrustante sanitário",
    descricao: "Desincrustante sanitário para remoção de manchas de ferrugem, resíduos de cimento e limpeza de mofo.",
    rendimento: "55 (leve) / 20 (pesada)"
  },
  {
    nome: "SANIMAX",
    titulo: "Desinfetante de amplo espectro",
    descricao: "Desinfetante de amplo espectro para superfícies que entram em contato com alimentos.",
    rendimento: "640"
  },
  {
    nome: "MULTILUX POWER",
    titulo: "Limpador multiuso concentrado",
    descricao: "Limpador multiuso concentrado para limpeza profunda e pesada de diversas superfícies.",
    rendimento: "200 a 300"
  },
  {
    nome: "AGUASSANI",
    titulo: "Água sanitária profissional",
    descricao: "Água sanitária para uso profissional com 2,0% a 2,5% de cloro ativo para desinfecção de banheiros, vestiários e caixas d'água.",
    rendimento: "PURO (bactericida) / 25 (limpeza geral)"
  },
  {
    nome: "ALUMICROST",
    titulo: "Desincrustante para metais moles",
    descricao: "Desincrustante para limpeza de metais moles, como panelas e formas de alumínio.",
    rendimento: "50 a 100 (imersão) / 125 a 500 (mecânica)"
  },
  {
    nome: "PISOFLOR",
    titulo: "Detergente para uso geral",
    descricao: "Detergente para uso geral com fragrância floral para limpeza diária de pisos.",
    rendimento: "100 a 200"
  },
  {
    nome: "DESINCROST GEL",
    titulo: "Desincrustante em gel",
    descricao: "Desincrustante e descarbonizante em gel para limpeza de fornos, fogões e grelhas. Sua consistência em gel garante maior fixação e economia.",
    rendimento: "PURO"
  },
  {
    nome: "LAVENE",
    titulo: "Detergente neutro industrial",
    descricao: "Detergente neutro industrial concentrado com poder desengordurante para diversas necessidades de limpeza.",
    rendimento: "200 a 500"
  },
  {
    nome: "REMOX",
    titulo: "Detergente desengordurante",
    descricao: "Detergente desengordurante para limpeza pesada de exaustores, pisos, fogões e fornos.",
    rendimento: "50 a 500"
  },
  {
    nome: "VIDROLUX",
    titulo: "Limpa vidros",
    descricao: "Limpa vidros com rápida evaporação para superfícies de vidro, granito e mármore.",
    rendimento: "PURO ou 55 (com kit)"
  },
  {
    nome: "MULTILUX BAC",
    titulo: "Limpador multiuso bactericida",
    descricao: "Limpador multiuso bactericida que substitui vários produtos em um só, executando as funções de limpador, desinfetante e limpa vidros.",
    rendimento: "400 a 1250"
  },
  {
    nome: "NT 100",
    titulo: "Desengordurante concentrado",
    descricao: "Desengordurante concentrado com alto poder de limpeza para óleos e graxas minerais, vegetais ou animais.",
    rendimento: "150 a 500"
  },
  {
    nome: "SANICLOR",
    titulo: "Desinfetante para alimentos",
    descricao: "Desinfetante para frutas, verduras e legumes.",
    rendimento: "500 (hortifrutícolas) / 100 (superfícies)"
  },
  {
    nome: "MULTILUX ECO",
    titulo: "Limpador multiuso ecoeficiente",
    descricao: "Limpador multiuso ecoeficiente com alta biodegradabilidade, formulado para amenizar o impacto ambiental.",
    rendimento: "500 a 1000"
  },
  {
    nome: "PERFUMAR",
    titulo: "Desodorizador de ambientes",
    descricao: "Desodorizador e aromatizador de ambientes com diversas fragrâncias de grande fixação.",
    rendimento: "PURO"
  },
  {
    nome: "HOSP NEUTRO PLUS",
    titulo: "Detergente hospitalar",
    descricao: "Detergente líquido neutro concentrado para uso hospitalar e no processamento de materiais e instrumentais cirúrgicos.",
    rendimento: "250 (instrumentais) / 500 (pisos)"
  },
  {
    nome: "LIMPA PORCELANATO",
    titulo: "Limpador para porcelanato",
    descricao: "Limpador desenvolvido especialmente para pisos de porcelanato e cerâmicos, com secagem rápida e mínimo residual.",
    rendimento: "100 a 500"
  },
  {
    nome: "SANIFLOR",
    titulo: "Desinfetante quaternário",
    descricao: "Desinfetante à base de quaternário de amônia com ação bactericida e bacteriostática.",
    rendimento: "50"
  },
  {
    nome: "LIMPAX DX",
    titulo: "Detergente neutro desengordurante",
    descricao: "Detergente neutro desengordurante e desengraxante concentrado para áreas de manipulação de alimentos e louças.",
    rendimento: "100 a 500"
  },
  {
    nome: "PISONEUTRO PLUS",
    titulo: "Detergente neutro para pisos",
    descricao: "Detergente concentrado neutro para limpeza diária de pisos e superfícies em geral.",
    rendimento: "400 a 750"
  },
  {
    nome: "REMOCALC",
    titulo: "Desincrustante ácido",
    descricao: "Desincrustante ácido para remoção de depósitos calcários em máquinas de lavar louças.",
    rendimento: "Varia com o tanque da máquina"
  },
  {
    nome: "REMOCRIL POWER",
    titulo: "Removedor de ceras",
    descricao: "Removedor de ceras acrílicas para remoção completa de qualquer tipo de tratamento de pisos.",
    rendimento: "25 a 50"
  },
  {
    nome: "SANIFLOR PLUS",
    titulo: "Desinfetante ultra concentrado",
    descricao: "Desinfetante ultra concentrado à base de quaternário de amônia.",
    rendimento: "750"
  },
  {
    nome: "LAVESSOL ORANGE",
    titulo: "Desengraxante biodegradável",
    descricao: "Desengraxante industrial biodegradável para remoção de óleos e graxas de pisos, máquinas e equipamentos.",
    rendimento: "750 a 15.000"
  }
];

export default function NovaPropostaPage() {
  const router = useRouter()
  const { criarProposta, gerarPDFProposta, loading } = usePropostas()
  const { clientes, fetchClientes, getClienteById } = useClientesV2()

  const [clienteSelecionado, setClienteSelecionado] = useState<ClienteV2 | null>(null)
  const [itensProposta, setItensProposta] = useState<ItemPropostaCreate[]>([])
  const [observacoes, setObservacoes] = useState('')

  // Estados para modais e busca
  const [isClientModalOpen, setIsClientModalOpen] = useState(false)
  const [isProdutoModalOpen, setIsProdutoModalOpen] = useState(false)
  const [termoBuscaCliente, setTermoBuscaCliente] = useState('')
  const [termoBuscaProduto, setTermoBuscaProduto] = useState('')

  // Estados para novo cliente
  const [novoClienteNome, setNovoClienteNome] = useState('')
  const [novoClienteTelefone, setNovoClienteTelefone] = useState('')

  // Estado para proposta finalizada
  const [propostaFinalizada, setPropostaFinalizada] = useState<number | null>(null)

  useEffect(() => {
    fetchClientes()
  }, [fetchClientes])

  const adicionarItem = (produto: typeof PRODUTOS_HIGIPLAS[0]) => {
    const novoItem: ItemPropostaCreate = {
      produto_nome: `${produto.nome} - ${produto.titulo}`,
      descricao: produto.descricao,
      valor: 0, // Será preenchido pelo vendedor
      rendimento_litros: produto.rendimento,
      custo_por_litro: 0 // Será calculado automaticamente
    }
    setItensProposta([...itensProposta, novoItem])
    setIsProdutoModalOpen(false)
    toast.success('Produto adicionado!')
  }

  const atualizarItem = (index: number, campo: keyof ItemPropostaCreate, valor: any) => {
    const novosItens = [...itensProposta]
    novosItens[index] = { ...novosItens[index], [campo]: valor }

    // Calcula custo por litro automaticamente
    if (campo === 'valor' || campo === 'rendimento_litros') {
      const item = novosItens[index]
      const rendimento = parseFloat(item.rendimento_litros || '0')
      if (rendimento > 0 && item.valor > 0) {
        novosItens[index].custo_por_litro = item.valor / rendimento
      }
    }

    setItensProposta(novosItens)
  }

  const removerItem = (index: number) => {
    setItensProposta(itensProposta.filter((_, i) => i !== index))
    toast.success('Item removido!')
  }

  const totalProposta = () => {
    return itensProposta.reduce((acc, item) => acc + item.valor, 0)
  }

  const handleFinalizar = async () => {
    if (!clienteSelecionado) {
      toast.error('Selecione um cliente!')
      return
    }

    if (itensProposta.length === 0) {
      toast.error('Adicione pelo menos um produto!')
      return
    }

    // Valida se todos os itens têm valor
    const itemSemValor = itensProposta.find(item => item.valor <= 0)
    if (itemSemValor) {
      toast.error('Todos os produtos devem ter um valor!')
      return
    }

    const payload: PropostaCreatePayload = {
      cliente_id: clienteSelecionado.id,
      status: 'ENVIADA',
      observacoes: observacoes || undefined,
      itens: itensProposta
    }

    const proposta = await criarProposta(payload)

    if (proposta) {
      setPropostaFinalizada(proposta.id)

      // Gera e baixa o PDF automaticamente
      const pdfBlob = await gerarPDFProposta(proposta.id)
      if (pdfBlob) {
        const url = window.URL.createObjectURL(pdfBlob)
        const link = document.createElement('a')
        link.href = url
        link.download = `proposta_${proposta.id}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      }
    }
  }

  const handleShareWhatsApp = () => {
    if (!clienteSelecionado || !propostaFinalizada) return

    const telefone = clienteSelecionado.telefone?.replace(/\D/g, '') || ''
    const mensagem = `Olá ${clienteSelecionado.nome}! Segue a proposta comercial #${propostaFinalizada} da Higiplas. Qualquer dúvida, estou à disposição!`
    const url = `https://wa.me/55${telefone}?text=${encodeURIComponent(mensagem)}`
    window.open(url, '_blank')
  }

  const handleCriarNovoCliente = async () => {
    if (!novoClienteNome || !novoClienteTelefone) {
      toast.error('Preencha nome e telefone!')
      return
    }

    try {
      const response = await apiService.post('/clientes-v2/quick', {
        nome: novoClienteNome,
        telefone: novoClienteTelefone
      })

      if (response?.data) {
        toast.success('Cliente criado com sucesso!')
        setClienteSelecionado(response.data)
        setIsClientModalOpen(false)
        setNovoClienteNome('')
        setNovoClienteTelefone('')
        fetchClientes()
      }
    } catch (error) {
      toast.error('Erro ao criar cliente')
    }
  }

  if (propostaFinalizada) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Header onLogoutClick={() => {
          localStorage.removeItem('authToken')
          router.push('/')
        }} />
        <div className="container mx-auto p-6">
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="text-center text-2xl text-green-600">
                ✅ Proposta Criada com Sucesso!
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-center text-gray-600">
                Proposta #{propostaFinalizada} criada e PDF gerado!
              </p>

              <Button
                onClick={handleShareWhatsApp}
                className="w-full gap-2 mb-4"
                size="lg"
                style={{backgroundColor: '#25D366', color: 'white'}}
              >
                <Share2 /> Compartilhar no WhatsApp
              </Button>

              <Button
                onClick={() => router.push('/dashboard/propostas')}
                variant="outline"
                className="w-full"
              >
                Ver Histórico de Propostas
              </Button>

              <Button
                onClick={() => {
                  setPropostaFinalizada(null)
                  setClienteSelecionado(null)
                  setItensProposta([])
                  setObservacoes('')
                }}
                variant="ghost"
                className="w-full"
              >
                Criar Nova Proposta
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header onLogoutClick={() => {
        localStorage.removeItem('authToken')
        router.push('/')
      }} />

      <div className="container mx-auto p-6">
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="gap-2"
          >
            <ArrowLeft size={20} />
            Voltar
          </Button>
        </div>

        <h1 className="text-3xl font-bold mb-6 text-gray-800">Nova Proposta Comercial</h1>

        <div className="grid gap-6">
          {/* Seleção de Cliente */}
          <Card>
            <CardHeader>
              <CardTitle>1. Selecione o Cliente</CardTitle>
            </CardHeader>
            <CardContent>
              {clienteSelecionado ? (
                <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-semibold">{clienteSelecionado.nome}</p>
                    <p className="text-sm text-gray-600">{clienteSelecionado.telefone}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setClienteSelecionado(null)}
                  >
                    <X size={16} />
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  <Input
                    placeholder="Buscar cliente..."
                    value={termoBuscaCliente}
                    onChange={(e) => setTermoBuscaCliente(e.target.value)}
                    className="mb-2"
                  />
                  <div className="max-h-60 overflow-y-auto space-y-2">
                    {clientes
                      .filter(c =>
                        c.nome.toLowerCase().includes(termoBuscaCliente.toLowerCase()) ||
                        c.telefone?.includes(termoBuscaCliente)
                      )
                      .map(c => (
                        <div
                          key={c.id}
                          onClick={async () => {
                            const clienteCompleto = await getClienteById(c.id)
                            if (clienteCompleto) {
                              setClienteSelecionado(clienteCompleto)
                            }
                          }}
                          className="p-3 border rounded-lg hover:bg-blue-50 cursor-pointer"
                        >
                          <p className="font-semibold">{c.nome}</p>
                          <p className="text-sm text-gray-600">{c.telefone}</p>
                        </div>
                      ))}
                  </div>
                  <Button 
                    onClick={() => setIsClientModalOpen(true)}
                    variant="outline"
                    className="w-full mt-2"
                  >
                    <Plus size={16} className="mr-2" />
                    Criar Novo Cliente
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Produtos */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>2. Adicione os Produtos</span>
                <Button onClick={() => setIsProdutoModalOpen(true)} size="sm">
                  <Plus size={16} className="mr-2" />
                  Adicionar Produto
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {itensProposta.length === 0 ? (
                <p className="text-center text-gray-500 py-8">
                  Nenhum produto adicionado ainda
                </p>
              ) : (
                <div className="space-y-4">
                  {itensProposta.map((item, index) => (
                    <div key={index} className="p-4 border rounded-lg space-y-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="font-semibold">{item.produto_nome}</p>
                          <p className="text-sm text-gray-600">{item.descricao}</p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removerItem(index)}
                        >
                          <Trash2 size={16} className="text-red-500" />
                        </Button>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-3">
                        <div>
                          <Label>Valor (R$)</Label>
                          <Input
                            type="number"
                            step="0.01"
                            value={item.valor || ''}
                            onChange={(e) => atualizarItem(index, 'valor', parseFloat(e.target.value) || 0)}
                            placeholder="0.00"
                          />
                        </div>
                        <div>
                          <Label>Rendimento (L)</Label>
                          <Input
                            value={item.rendimento_litros || ''}
                            onChange={(e) => atualizarItem(index, 'rendimento_litros', e.target.value)}
                            placeholder="Ex: 500"
                          />
                        </div>
                        <div>
                          <Label>Custo/Litro</Label>
                          <Input
                            value={item.custo_por_litro ? `R$ ${item.custo_por_litro.toFixed(2)}` : 'R$ 0.00'}
                            disabled
                            className="bg-gray-100"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  <div className="pt-4 border-t">
                    <div className="flex justify-between items-center text-xl font-bold">
                      <span>Total da Proposta:</span>
                      <span className="text-blue-600">
                        R$ {totalProposta().toFixed(2).replace('.', ',')}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Observações */}
          <Card>
            <CardHeader>
              <CardTitle>3. Observações (Opcional)</CardTitle>
            </CardHeader>
            <CardContent>
              <textarea
                className="w-full p-3 border rounded-lg min-h-[100px]"
                placeholder="Adicione observações sobre a proposta..."
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
              />
            </CardContent>
          </Card>

          {/* Botão Finalizar */}
          <Button
            onClick={handleFinalizar}
            disabled={loading || !clienteSelecionado || itensProposta.length === 0}
            size="lg"
            className="w-full"
          >
            <FileText className="mr-2" />
            {loading ? 'Gerando Proposta...' : 'Finalizar e Gerar PDF'}
          </Button>
        </div>
      </div>

      {/* Modal Criar Cliente */}
      {isClientModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Novo Cliente</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsClientModalOpen(false)}
                >
                  <X size={20} />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Nome *</Label>
                <Input
                  value={novoClienteNome}
                  onChange={(e) => setNovoClienteNome(e.target.value)}
                  placeholder="Nome do cliente"
                />
              </div>
              <div>
                <Label>Telefone *</Label>
                <Input
                  value={novoClienteTelefone}
                  onChange={(e) => setNovoClienteTelefone(e.target.value)}
                  placeholder="(00) 00000-0000"
                />
              </div>
              <Button onClick={handleCriarNovoCliente} className="w-full">
                Criar Cliente
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Modal Adicionar Produto */}
      {isProdutoModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Selecione um Produto</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsProdutoModalOpen(false)}
                >
                  <X size={20} />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="overflow-y-auto">
              <Input
                placeholder="Buscar produto..."
                value={termoBuscaProduto}
                onChange={(e) => setTermoBuscaProduto(e.target.value)}
                className="mb-4"
              />
              <div className="space-y-2">
                {PRODUTOS_HIGIPLAS
                  .filter(p => 
                    p.nome.toLowerCase().includes(termoBuscaProduto.toLowerCase()) ||
                    p.titulo.toLowerCase().includes(termoBuscaProduto.toLowerCase())
                  )
                  .map((produto, index) => (
                    <div
                      key={index}
                      onClick={() => adicionarItem(produto)}
                      className="p-4 border rounded-lg hover:bg-blue-50 cursor-pointer"
                    >
                      <p className="font-semibold">{produto.nome} - {produto.titulo}</p>
                      <p className="text-sm text-gray-600 mt-1">{produto.descricao}</p>
                      <p className="text-sm text-blue-600 mt-2">
                        Rendimento: {produto.rendimento} litros
                      </p>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
