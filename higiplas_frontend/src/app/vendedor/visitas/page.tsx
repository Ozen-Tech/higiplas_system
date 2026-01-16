'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useVendedor } from '@/hooks/useVendedor';
import { useVisitas, VisitaVendedor, VisitaCreate } from '@/hooks/useVisitas';
import { useClientesV2 } from '@/hooks/useClientesV2';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2, MapPin, CheckCircle, XCircle, Calendar, User } from 'lucide-react';
import toast from 'react-hot-toast';

export default function VisitasPage() {
  const router = useRouter();
  const { usuario, loading: userLoading, isVendedor } = useVendedor();
  const { criarVisita, listarVisitas, confirmarVisita, obterEstatisticas, stats, loading: visitasLoading } = useVisitas();
  const { fetchClientes, clientes } = useClientesV2();
  
  const [mounted, setMounted] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  const [fotoPreview, setFotoPreview] = useState<string | null>(null);
  const [fotoFile, setFotoFile] = useState<File | null>(null);
  
  // Formulário
  const [clienteId, setClienteId] = useState<number | null>(null);
  const [motivoVisita, setMotivoVisita] = useState('');
  const [observacoes, setObservacoes] = useState('');
  const [clienteSearch, setClienteSearch] = useState('');
  
  // Lista de visitas
  const [visitas, setVisitas] = useState<VisitaVendedor[]>([]);
  const [filterConfirmadas, setFilterConfirmadas] = useState<boolean | undefined>(undefined);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && isVendedor && usuario) {
      carregarVisitas();
      obterEstatisticas(usuario.id, 30);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mounted, isVendedor, usuario, filterConfirmadas]);

  useEffect(() => {
    if (clienteSearch.trim().length >= 2) {
      fetchClientes({ search: clienteSearch, limit: 10 });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clienteSearch]);

  const carregarVisitas = async () => {
    if (!usuario) return;
    const visitasList = await listarVisitas(usuario.id, filterConfirmadas, 50, 0);
    setVisitas(visitasList);
  };

  const obterLocalizacao = useCallback(() => {
    setIsGettingLocation(true);
    setLocationError(null);

    if (!navigator.geolocation) {
      setLocationError('Geolocalização não é suportada pelo seu navegador.');
      setIsGettingLocation(false);
      return;
    }

    const options = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        });
        setLocationError(null);
        setIsGettingLocation(false);
        toast.success('Localização obtida com sucesso!');
      },
      (error) => {
        let errorMessage = 'Erro ao obter localização.';
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Permissão de localização negada. Por favor, habilite no navegador.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Informações de localização não disponíveis.';
            break;
          case error.TIMEOUT:
            errorMessage = 'Tempo limite para obter localização excedido.';
            break;
        }
        setLocationError(errorMessage);
        setIsGettingLocation(false);
        toast.error(errorMessage);
      },
      options
    );
  }, []);

  const handleFotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Foto muito grande. Máximo 5MB.');
        return;
      }
      setFotoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setFotoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadFoto = async (): Promise<string | null> => {
    if (!fotoFile) return null;

    try {
      // Por enquanto, retornamos null - em produção, você faria upload para um servidor de arquivos
      // e retornaria a URL
      toast('Upload de foto será implementado em produção', { icon: 'ℹ️' });
      return null;
    } catch {
      toast.error('Erro ao fazer upload da foto');
      return null;
    }
  };

  const handleSubmitVisita = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!usuario || !location) {
      toast.error('É necessário obter a localização GPS para registrar a visita.');
      return;
    }

    if (!motivoVisita.trim()) {
      toast.error('Motivo da visita é obrigatório.');
      return;
    }

    try {
      // Upload da foto se houver
      let fotoUrl: string | null = null;
      if (fotoFile) {
        fotoUrl = await handleUploadFoto();
      }

      const visitaData: VisitaCreate = {
        vendedor_id: usuario.id,
        cliente_id: clienteId || undefined,
        latitude: location.latitude,
        longitude: location.longitude,
        motivo_visita: motivoVisita,
        observacoes: observacoes || undefined,
        foto_comprovante: fotoUrl || undefined,
        empresa_id: usuario.empresa_id || 1
      };

      const visitaCriada = await criarVisita(visitaData);
      
      if (visitaCriada) {
        // Confirmar automaticamente após criar
        if (visitaCriada.id) {
          await confirmarVisita(visitaCriada.id);
        }
        
        // Limpar formulário
        setClienteId(null);
        setMotivoVisita('');
        setObservacoes('');
        setClienteSearch('');
        setFotoPreview(null);
        setFotoFile(null);
        setLocation(null);
        setShowForm(false);
        
        // Recarregar visitas
        carregarVisitas();
        obterEstatisticas(usuario.id, 30);
      }
    } catch (error) {
      console.error('Erro ao criar visita:', error);
    }
  };

  const handleConfirmarVisita = async (visitaId: number) => {
    if (!usuario) return;
    
    const confirmada = await confirmarVisita(visitaId);
    if (confirmada) {
      carregarVisitas();
      obterEstatisticas(usuario.id, 30);
    }
  };

  if (!mounted) {
    return null;
  }

  if (userLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!isVendedor) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardContent className="p-6 text-center">
            <p className="text-red-600 dark:text-red-400">
              Acesso negado. Apenas vendedores podem acessar esta área.
            </p>
            <Button onClick={() => router.push('/vendedor/login')} className="mt-4">
              Voltar para Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                Sistema de Visitas
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Bem-vindo, {usuario?.nome}
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={() => router.push('/vendedor/app')}
              >
                ← Voltar
              </Button>
              <Button
                onClick={() => router.push('/vendedor/visitas/mapa')}
                variant="secondary"
              >
                <MapPin className="h-4 w-4 mr-2" />
                Ver Mapa
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Estatísticas */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Hoje</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {stats.visitas_hoje}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Esta Semana</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {stats.visitas_semana}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Este Mês</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {stats.visitas_mes}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Confirmadas</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {stats.visitas_confirmadas}
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Botão para registrar nova visita */}
        {!showForm && (
          <Card>
            <CardContent className="p-6">
              <Button
                onClick={() => {
                  setShowForm(true);
                  obterLocalizacao();
                }}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              >
                <MapPin className="h-5 w-5 mr-2" />
                Registrar Nova Visita
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Formulário de registro */}
        {showForm && (
          <Card>
            <CardContent className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  Nova Visita
                </h2>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setShowForm(false);
                    setLocation(null);
                    setLocationError(null);
                  }}
                >
                  Cancelar
                </Button>
              </div>

              <form onSubmit={handleSubmitVisita} className="space-y-4">
                {/* Localização GPS */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Localização GPS *
                  </label>
                  {!location ? (
                    <div className="space-y-2">
                        <Button
                          type="button"
                          onClick={obterLocalizacao}
                          disabled={isGettingLocation}
                          variant="secondary"
                          className="w-full"
                        >
                        {isGettingLocation ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Obtendo localização...
                          </>
                        ) : (
                          <>
                            <MapPin className="h-4 w-4 mr-2" />
                            Obter Localização
                          </>
                        )}
                      </Button>
                      {locationError && (
                        <p className="text-sm text-red-600 dark:text-red-400">
                          {locationError}
                        </p>
                      )}
                    </div>
                  ) : (
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-green-800 dark:text-green-200">
                            ✓ Localização obtida
                          </p>
                          <p className="text-xs text-green-600 dark:text-green-400">
                            Lat: {location.latitude.toFixed(6)}, Lng: {location.longitude.toFixed(6)}
                          </p>
                        </div>
                        <Button
                          type="button"
                          onClick={obterLocalizacao}
                          variant="secondary"
                        >
                          Atualizar
                        </Button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Busca de Cliente */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Cliente (Opcional)
                  </label>
                  <Input
                    label=""
                    type="text"
                    placeholder="Buscar cliente por nome..."
                    value={clienteSearch}
                    onChange={(e) => setClienteSearch(e.target.value)}
                    className="w-full"
                  />
                  {clienteSearch && clientes.length > 0 && (
                    <div className="border border-gray-200 dark:border-gray-700 rounded-lg max-h-48 overflow-y-auto">
                      {clientes.map((cliente) => (
                        <button
                          key={cliente.id}
                          type="button"
                          onClick={() => {
                            setClienteId(cliente.id);
                            setClienteSearch(cliente.nome);
                          }}
                          className={`w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 ${
                            clienteId === cliente.id ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                          }`}
                        >
                          <p className="font-medium">{cliente.nome}</p>
                          {cliente.telefone && (
                            <p className="text-xs text-gray-500">{cliente.telefone}</p>
                          )}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Motivo da Visita */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Motivo da Visita *
                  </label>
                  <select
                    value={motivoVisita}
                    onChange={(e) => setMotivoVisita(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
                    required
                  >
                    <option value="">Selecione...</option>
                    <option value="Diluição">Diluição</option>
                    <option value="Atendimento">Atendimento</option>
                    <option value="Entrega">Entrega</option>
                    <option value="Orçamento">Orçamento</option>
                    <option value="Outro">Outro</option>
                  </select>
                </div>

                {/* Observações */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Observações
                  </label>
                  <textarea
                    value={observacoes}
                    onChange={(e) => setObservacoes(e.target.value)}
                    rows={3}
                    className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
                    placeholder="Adicione observações sobre a visita..."
                  />
                </div>

                {/* Foto */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Foto Comprovante (Opcional)
                  </label>
                  <div className="space-y-2">
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      onChange={handleFotoChange}
                      className="w-full text-sm text-gray-600 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900/20 dark:file:text-blue-300"
                    />
                    {fotoPreview && (
                      <div className="relative">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={fotoPreview}
                          alt="Preview"
                          className="w-full max-w-xs rounded-lg border border-gray-200 dark:border-gray-700"
                        />
                        <button
                          type="button"
                          onClick={() => {
                            setFotoPreview(null);
                            setFotoFile(null);
                          }}
                          className="absolute top-2 right-2 bg-red-600 text-white rounded-full p-1"
                        >
                          <XCircle className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Botões */}
                <div className="flex gap-3 pt-4">
                  <Button
                    type="submit"
                    disabled={!location || !motivoVisita || visitasLoading}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {visitasLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Registrando...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Registrar e Confirmar Visita
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Lista de Visitas */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Histórico de Visitas
              </h2>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setFilterConfirmadas(undefined);
                  }}
                  className={`px-3 py-1 rounded-lg text-sm ${
                    filterConfirmadas === undefined
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  Todas
                </button>
                <button
                  onClick={() => {
                    setFilterConfirmadas(true);
                  }}
                  className={`px-3 py-1 rounded-lg text-sm ${
                    filterConfirmadas === true
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  Confirmadas
                </button>
                <button
                  onClick={() => {
                    setFilterConfirmadas(false);
                  }}
                  className={`px-3 py-1 rounded-lg text-sm ${
                    filterConfirmadas === false
                      ? 'bg-amber-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  Pendentes
                </button>
              </div>
            </div>

            {visitasLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
              </div>
            ) : visitas.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                Nenhuma visita registrada ainda.
              </div>
            ) : (
              <div className="space-y-3">
                {visitas.map((visita) => (
                  <div
                    key={visita.id}
                    className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {visita.confirmada ? (
                            <CheckCircle className="h-5 w-5 text-green-600" />
                          ) : (
                            <XCircle className="h-5 w-5 text-amber-600" />
                          )}
                          <span className={`font-semibold ${
                            visita.confirmada ? 'text-green-700 dark:text-green-300' : 'text-amber-700 dark:text-amber-300'
                          }`}>
                            {visita.confirmada ? 'Confirmada' : 'Pendente'}
                          </span>
                        </div>
                        <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            <span>
                              {new Date(visita.data_visita).toLocaleString('pt-BR')}
                            </span>
                          </div>
                          {visita.motivo_visita && (
                            <p><strong>Motivo:</strong> {visita.motivo_visita}</p>
                          )}
                          {visita.cliente_nome && (
                            <div className="flex items-center gap-2">
                              <User className="h-4 w-4" />
                              <span>{visita.cliente_nome}</span>
                            </div>
                          )}
                          {visita.observacoes && (
                            <p><strong>Observações:</strong> {visita.observacoes}</p>
                          )}
                          {visita.endereco_completo && (
                            <div className="flex items-center gap-2">
                              <MapPin className="h-4 w-4" />
                              <span className="text-xs">{visita.endereco_completo}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      {!visita.confirmada && (
                        <Button
                          onClick={() => handleConfirmarVisita(visita.id)}
                          variant="secondary"
                          className="ml-2"
                        >
                          Confirmar
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
