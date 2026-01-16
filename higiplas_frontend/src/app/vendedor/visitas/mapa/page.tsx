'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useVendedor } from '@/hooks/useVendedor';
import { useVisitas, VisitaVendedor } from '@/hooks/useVisitas';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, MapPin, Filter, Calendar, User, X } from 'lucide-react';

export default function MapaVisitasPage() {
  const router = useRouter();
  const { usuario, loading: userLoading, isVendedor } = useVendedor();
  const { listarVisitasMapa, loading: visitasLoading } = useVisitas();
  
  const [mounted, setMounted] = useState(false);
  const [visitas, setVisitas] = useState<VisitaVendedor[]>([]);
  const [filtros, setFiltros] = useState({
    vendedor_id: undefined as number | undefined,
    cliente_id: undefined as number | undefined,
    data_inicio: undefined as string | undefined,
    data_fim: undefined as string | undefined
  });
  const [showFiltros, setShowFiltros] = useState(false);
  const [mapCenter, setMapCenter] = useState<[number, number]>([-2.5297, -44.3028]); // São Luís - MA (padrão)
  const [selectedVisita, setSelectedVisita] = useState<VisitaVendedor | null>(null);

  useEffect(() => {
    setMounted(true);
    
    // Tentar obter localização atual do usuário para centralizar o mapa
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setMapCenter([position.coords.latitude, position.coords.longitude]);
        },
        () => {
          // Usar padrão se não conseguir obter
        }
      );
    }
  }, []);

  useEffect(() => {
    if (mounted && isVendedor && usuario) {
      carregarVisitasMapa();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mounted, isVendedor, usuario, filtros]);

  const carregarVisitasMapa = async () => {
    if (!usuario) return;
    
    const visitasList = await listarVisitasMapa(
      filtros.vendedor_id || usuario.id,
      filtros.cliente_id,
      filtros.data_inicio,
      filtros.data_fim,
      1000
    );
    
    setVisitas(visitasList);
    
    // Centralizar mapa na primeira visita se houver
    if (visitasList.length > 0 && visitasList[0]) {
      setMapCenter([visitasList[0].latitude, visitasList[0].longitude]);
    }
  };

  const aplicarFiltros = () => {
    carregarVisitasMapa();
    setShowFiltros(false);
  };

  const limparFiltros = () => {
    setFiltros({
      vendedor_id: undefined,
      cliente_id: undefined,
      data_inicio: undefined,
      data_fim: undefined
    });
  };

  if (!mounted) {
    return null;
  }

  if (userLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!isVendedor) {
    return (
      <div className="flex items-center justify-center min-h-screen">
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
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                Mapa de Visitas
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {visitas.length} visitas confirmadas no mapa
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setShowFiltros(!showFiltros)}
              >
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
              <Button
                variant="outline"
                onClick={() => router.push('/vendedor/visitas')}
              >
                ← Voltar
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Painel de Filtros */}
      {showFiltros && (
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-4">
          <div className="max-w-7xl mx-auto">
            <Card>
              <CardContent className="p-4 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                    Filtros
                  </h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowFiltros(false)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Data Início
                    </label>
                    <input
                      type="date"
                      value={filtros.data_inicio || ''}
                      onChange={(e) => setFiltros(prev => ({ ...prev, data_inicio: e.target.value || undefined }))}
                      className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Data Fim
                    </label>
                    <input
                      type="date"
                      value={filtros.data_fim || ''}
                      onChange={(e) => setFiltros(prev => ({ ...prev, data_fim: e.target.value || undefined }))}
                      className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm"
                    />
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button
                    onClick={aplicarFiltros}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    Aplicar Filtros
                  </Button>
                  <Button
                    onClick={limparFiltros}
                    variant="outline"
                  >
                    Limpar
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      <main className="relative" style={{ height: 'calc(100vh - 120px)' }}>
        {/* Container do Mapa - Usando OpenStreetMap/Leaflet via iframe temporário */}
        {/* Em produção, instalar react-leaflet ou usar Google Maps API */}
        <div className="w-full h-full relative">
          {visitasLoading ? (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-900 z-10">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : visitas.length === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-900 z-10">
              <Card className="max-w-md">
                <CardContent className="p-6 text-center">
                  <MapPin className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    Nenhuma visita confirmada para exibir no mapa.
                  </p>
                  <Button
                    onClick={() => router.push('/vendedor/visitas')}
                    className="mt-4"
                  >
                    Registrar Primeira Visita
                  </Button>
                </CardContent>
              </Card>
            </div>
          ) : (
            <>
              {/* Mapa usando OpenStreetMap via URL (solução temporária) */}
              {/* Em produção, usar biblioteca de mapas adequada */}
              <div className="w-full h-full">
                <iframe
                  src={`https://www.openstreetmap.org/export/embed.html?bbox=${
                    mapCenter[1] - 0.01
                  },${mapCenter[0] - 0.01},${mapCenter[1] + 0.01},${
                    mapCenter[0] + 0.01
                  }&layer=mapnik&marker=${mapCenter[0]},${mapCenter[1]}`}
                  className="w-full h-full border-0"
                  title="Mapa de Visitas"
                />
              </div>

              {/* Lista de visitas como overlay */}
              <div className="absolute top-4 right-4 z-20 max-w-sm w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 max-h-[calc(100vh-200px)] overflow-y-auto">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                    Visitas ({visitas.length})
                  </h3>
                </div>
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {visitas.map((visita) => (
                    <button
                      key={visita.id}
                      onClick={() => {
                        setSelectedVisita(visita);
                        setMapCenter([visita.latitude, visita.longitude]);
                      }}
                      className={`w-full text-left p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition ${
                        selectedVisita?.id === visita.id ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <MapPin className="h-5 w-5 text-blue-600 mt-0.5" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-900 dark:text-gray-100 truncate">
                            {visita.cliente_nome || 'Visita sem cliente'}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {new Date(visita.data_visita).toLocaleString('pt-BR')}
                          </p>
                          {visita.motivo_visita && (
                            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                              {visita.motivo_visita}
                            </p>
                          )}
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Lat: {visita.latitude.toFixed(6)}, Lng: {visita.longitude.toFixed(6)}
                          </p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Modal de detalhes da visita */}
              {selectedVisita && (
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-30 p-4">
                  <Card className="max-w-md w-full">
                    <CardContent className="p-6 space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                          Detalhes da Visita
                        </h3>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedVisita(null)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-600 dark:text-gray-400">
                            {new Date(selectedVisita.data_visita).toLocaleString('pt-BR')}
                          </span>
                        </div>
                        
                        {selectedVisita.cliente_nome && (
                          <div className="flex items-center gap-2">
                            <User className="h-4 w-4 text-gray-400" />
                            <span className="text-gray-600 dark:text-gray-400">
                              {selectedVisita.cliente_nome}
                            </span>
                          </div>
                        )}
                        
                        {selectedVisita.motivo_visita && (
                          <div>
                            <p className="font-medium text-gray-700 dark:text-gray-300">
                              Motivo:
                            </p>
                            <p className="text-gray-600 dark:text-gray-400">
                              {selectedVisita.motivo_visita}
                            </p>
                          </div>
                        )}
                        
                        {selectedVisita.observacoes && (
                          <div>
                            <p className="font-medium text-gray-700 dark:text-gray-300">
                              Observações:
                            </p>
                            <p className="text-gray-600 dark:text-gray-400">
                              {selectedVisita.observacoes}
                            </p>
                          </div>
                        )}
                        
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4 text-gray-400" />
                          <div>
                            <p className="text-gray-600 dark:text-gray-400">
                              {selectedVisita.endereco_completo || 'Endereço não disponível'}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-500">
                              Lat: {selectedVisita.latitude.toFixed(6)}, Lng: {selectedVisita.longitude.toFixed(6)}
                            </p>
                          </div>
                        </div>
                        
                        {selectedVisita.foto_comprovante && (
                          <div>
                            <p className="font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Foto:
                            </p>
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img
                              src={selectedVisita.foto_comprovante}
                              alt="Comprovante"
                              className="w-full rounded-lg border border-gray-200 dark:border-gray-700"
                            />
                          </div>
                        )}
                      </div>
                      
                      <div className="flex gap-2 pt-4">
                        <Button
                          variant="outline"
                          onClick={() => setSelectedVisita(null)}
                          className="flex-1"
                        >
                          Fechar
                        </Button>
                        <Button
                          onClick={() => {
                            // Abrir em nova aba com Google Maps
                            const url = `https://www.google.com/maps?q=${selectedVisita.latitude},${selectedVisita.longitude}`;
                            window.open(url, '_blank');
                          }}
                          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                        >
                          Abrir no Google Maps
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
