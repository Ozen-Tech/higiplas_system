// Serviço específico para o PWA de vendedores
import { apiService } from './apiService';

export interface Usuario {
  id: number;
  nome: string;
  email: string;
  perfil: string;
  empresa_id: number;
  is_active: boolean;
}

export const vendedorService = {
  // Obter dados do usuário logado
  getMe: async (): Promise<Usuario | null> => {
    try {
      const response = await apiService.get('/users/me');
      return response?.data || null;
    } catch (error) {
      console.error('Erro ao obter dados do usuário:', error);
      return null;
    }
  },

  // Verificar se o usuário é vendedor
  isVendedor: (perfil: string | undefined): boolean => {
    if (!perfil) return false;
    return perfil.toLowerCase().includes('vendedor');
  },
};

