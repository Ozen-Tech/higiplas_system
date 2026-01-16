'use client';

import { useEffect, useRef, useState } from 'react';
import { VisitaVendedor } from '@/hooks/useVisitas';
import { MapPin } from 'lucide-react';

interface MapaVisitasProps {
  visitas: VisitaVendedor[];
  center?: [number, number];
  zoom?: number;
  onVisitaClick?: (visita: VisitaVendedor) => void;
  selectedVisita?: VisitaVendedor | null;
}

export function MapaVisitas({
  visitas,
  onVisitaClick,
  selectedVisita
}: MapaVisitasProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    // Esta é uma implementação básica usando OpenStreetMap via iframe
    // Em produção, recomenda-se usar:
    // - react-leaflet (OpenStreetMap)
    // - @react-google-maps/api (Google Maps)
    // - mapbox-gl-react (Mapbox)
    setMapLoaded(true);
  }, []);

  if (!mapLoaded || visitas.length === 0) {
    return (
      <div className="w-full h-full bg-gray-100 dark:bg-gray-900 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <MapPin className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            Carregando mapa...
          </p>
        </div>
      </div>
    );
  }

  // Calcular bounds do mapa baseado nas visitas
  const latitudes = visitas.map(v => v.latitude);
  const longitudes = visitas.map(v => v.longitude);
  const minLat = Math.min(...latitudes);
  const maxLat = Math.max(...latitudes);
  const minLng = Math.min(...longitudes);
  const maxLng = Math.max(...longitudes);

  // Calcular centro médio
  const centerLat = (minLat + maxLat) / 2;
  const centerLng = (minLng + maxLng) / 2;

  return (
    <div className="w-full h-full relative" ref={mapRef}>
      {/* Mapa usando OpenStreetMap - Solução básica */}
      {/* NOTA: Para produção, instale e use react-leaflet ou Google Maps API */}
      <div className="w-full h-full rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
        <iframe
          src={`https://www.openstreetmap.org/export/embed.html?bbox=${
            minLng - 0.01
          },${minLat - 0.01},${maxLng + 0.01},${
            maxLat + 0.01
          }&layer=mapnik&marker=${centerLat},${centerLng}`}
          className="w-full h-full border-0"
          title="Mapa de Visitas"
        />
      </div>

      {/* Legenda de visitas */}
      <div className="absolute top-4 left-4 z-10 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3 max-w-xs">
        <div className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Visitas ({visitas.length})
        </div>
        <div className="space-y-1 max-h-48 overflow-y-auto">
          {visitas.slice(0, 5).map((visita) => (
            <button
              key={visita.id}
              onClick={() => onVisitaClick?.(visita)}
              className={`w-full text-left p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700 text-xs ${
                selectedVisita?.id === visita.id ? 'bg-blue-50 dark:bg-blue-900/20' : ''
              }`}
            >
              <div className="flex items-center gap-2">
                <MapPin className="h-3 w-3 text-blue-600" />
                <span className="truncate">
                  {visita.cliente_nome || 'Sem cliente'} - {new Date(visita.data_visita).toLocaleDateString('pt-BR')}
                </span>
              </div>
            </button>
          ))}
          {visitas.length > 5 && (
            <p className="text-xs text-gray-500 dark:text-gray-400 text-center pt-2">
              +{visitas.length - 5} mais visitas
            </p>
          )}
        </div>
      </div>

      {/* Instrução para instalar biblioteca de mapas */}
      <div className="absolute bottom-4 right-4 z-10 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 max-w-xs text-xs text-blue-800 dark:text-blue-200">
        <p className="font-semibold mb-1">💡 Melhorias Futuras</p>
        <p>
          Para um mapa interativo completo, instale <code className="bg-blue-100 dark:bg-blue-900 px-1 rounded">react-leaflet</code> ou <code className="bg-blue-100 dark:bg-blue-900 px-1 rounded">@react-google-maps/api</code>
        </p>
      </div>
    </div>
  );
}
