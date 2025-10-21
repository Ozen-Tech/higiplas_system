"use client"

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { usePropostas } from '@/hooks/usePropostas'
import { Proposta } from '@/types/propostas'
import { Header } from '@/components/Header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Plus, FileText, Download, Eye, Calendar, User, DollarSign } from 'lucide-react'
import toast from 'react-hot-toast'

export default function PropostasPage() {
  const router = useRouter()
  const { propostas, loading, listarPropostasVendedor, gerarPDFProposta } = usePropostas()
  const [propostaSelecionada, setPropostaSelecionada] = useState<Proposta | null>(null)

  useEffect(() => {
    listarPropostasVendedor()
  }, [listarPropostasVendedor])

  const handleDownloadPDF = async (propostaId: number) => {
    const pdfBlob = await gerarPDFProposta(propostaId)
    if (pdfBlob) {
      const url = window.URL.createObjectURL(pdfBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `proposta_${propostaId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      toast.success('PDF baixado com sucesso!')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'RASCUNHO':
        return 'bg-gray-500'
      case 'ENVIADA':
        return 'bg-blue-500'
      case 'APROVADA':
        return 'bg-green-500'
      case 'REJEITADA':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  const calcularTotal = (proposta: Proposta) => {
    return proposta.itens.reduce((acc, item) => acc + item.valor, 0)
  }

  const formatarData = (dataString: string) => {
    const data = new Date(dataString)
    return data.toLocaleDateString('pt-BR')
  }

  if (loading && propostas.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Header onLogoutClick={() => {
          localStorage.removeItem('authToken')
          router.push('/')
        }} />
        <div className="container mx-auto p-6">
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-600">Carregando propostas...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header onLogoutClick={() => {
        localStorage.removeItem('authToken')
        router.push('/')
      }} />

      <div className="container mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Minhas Propostas</h1>
          <Button 
            onClick={() => router.push('/dashboard/propostas/nova')}
            className="gap-2"
          >
            <Plus size={20} />
            Nova Proposta
          </Button>
        </div>

        {propostas.length === 0 ? (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <FileText size={64} className="mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  Nenhuma proposta encontrada
                </h3>
                <p className="text-gray-500 mb-6">
                  Comece criando sua primeira proposta comercial
                </p>
                <Button onClick={() => router.push('/dashboard/propostas/nova')}>
                  <Plus size={20} className="mr-2" />
                  Criar Primeira Proposta
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6">
            {propostas.map((proposta) => (
              <Card key={proposta.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <CardTitle className="text-xl">
                          Proposta #{proposta.id}
                        </CardTitle>
                        <Badge className={getStatusColor(proposta.status)}>
                          {proposta.status}
                        </Badge>
                      </div>
                      <div className="space-y-1 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <User size={16} />
                          <span>{proposta.cliente.razao_social}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar size={16} />
                          <span>{formatarData(proposta.data_criacao)}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-2 text-2xl font-bold text-blue-600">
                        <DollarSign size={24} />
                        R$ {calcularTotal(proposta).toFixed(2).replace('.', ',')}
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        {proposta.itens.length} {proposta.itens.length === 1 ? 'item' : 'itens'}
                      </p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPropostaSelecionada(proposta)}
                      className="flex-1"
                    >
                      <Eye size={16} className="mr-2" />
                      Ver Detalhes
                    </Button>
                    <Button
                      variant="default"
                      size="sm"
                      onClick={() => handleDownloadPDF(proposta.id)}
                      className="flex-1"
                    >
                      <Download size={16} className="mr-2" />
                      Baixar PDF
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Modal de Detalhes */}
      {propostaSelecionada && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Detalhes da Proposta #{propostaSelecionada.id}</CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setPropostaSelecionada(null)}
                >
                  ✕
                </Button>
              </div>
            </CardHeader>
            <CardContent className="overflow-y-auto">
              <div className="space-y-6">
                {/* Informações do Cliente */}
                <div>
                  <h3 className="font-semibold text-lg mb-3">Cliente</h3>
                  <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                    <p><strong>Nome:</strong> {propostaSelecionada.cliente.razao_social}</p>
                    {propostaSelecionada.cliente.telefone && (
                      <p><strong>Telefone:</strong> {propostaSelecionada.cliente.telefone}</p>
                    )}
                    {propostaSelecionada.cliente.email && (
                      <p><strong>Email:</strong> {propostaSelecionada.cliente.email}</p>
                    )}
                    {propostaSelecionada.cliente.endereco && (
                      <p><strong>Endereço:</strong> {propostaSelecionada.cliente.endereco}</p>
                    )}
                  </div>
                </div>

                {/* Produtos */}
                <div>
                  <h3 className="font-semibold text-lg mb-3">Produtos</h3>
                  <div className="space-y-3">
                    {propostaSelecionada.itens.map((item, index) => (
                      <div key={item.id} className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <p className="font-semibold">{index + 1}. {item.produto_nome}</p>
                            {item.descricao && (
                              <p className="text-sm text-gray-600 mt-1">{item.descricao}</p>
                            )}
                          </div>
                          <p className="text-lg font-bold text-blue-600">
                            R$ {item.valor.toFixed(2).replace('.', ',')}
                          </p>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mt-3">
                          {item.rendimento_litros && (
                            <p><strong>Rendimento:</strong> {item.rendimento_litros} litros</p>
                          )}
                          {item.custo_por_litro && item.custo_por_litro > 0 && (
                            <p><strong>Custo/Litro:</strong> R$ {item.custo_por_litro.toFixed(2).replace('.', ',')}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Total */}
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between text-xl font-bold">
                    <span>Total da Proposta:</span>
                    <span className="text-blue-600">
                      R$ {calcularTotal(propostaSelecionada).toFixed(2).replace('.', ',')}
                    </span>
                  </div>
                </div>

                {/* Observações */}
                {propostaSelecionada.observacoes && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3">Observações</h3>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-gray-700">{propostaSelecionada.observacoes}</p>
                    </div>
                  </div>
                )}

                {/* Botão Download */}
                <Button
                  onClick={() => handleDownloadPDF(propostaSelecionada.id)}
                  className="w-full"
                  size="lg"
                >
                  <Download size={20} className="mr-2" />
                  Baixar PDF da Proposta
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
