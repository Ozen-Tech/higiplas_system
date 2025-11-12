// Serviço para operações administrativas
import { apiService } from './apiService';

export interface UsuarioCreatePayload {
  nome: string;
  email: string;
  password: string;
  empresa_id: number;
  perfil: string;
}

export interface Usuario {
  id: number;
  nome: string;
  email: string;
  perfil: string;
  empresa_id: number;
  is_active: boolean;
}

export interface Empresa {
  id: number;
  nome: string;
  cnpj?: string;
  data_criacao?: string;
}

export const adminService = {
  // Criar novo usuário
  criarUsuario: async (payload: UsuarioCreatePayload): Promise<Usuario | null> => {
    try {
      const response = await apiService.post('/users/admin/create', payload);
      return response?.data || null;
    } catch (error) {
      console.error('Erro ao criar usuário:', error);
      throw error;
    }
  },

  // Listar empresas
  listarEmpresas: async (): Promise<Empresa[]> => {
    try {
      const response = await apiService.get('/empresas/');
      return (response?.data || []) as Empresa[];
    } catch (error) {
      console.error('Erro ao listar empresas:', error);
      return [];
    }
  },

  // Verificar se o usuário é admin ou gestor
  isAdmin: (perfil: string | undefined): boolean => {
    if (!perfil) return false;
    const perfilUpper = perfil.toUpperCase();
    return perfilUpper === 'ADMIN' || perfilUpper === 'GESTOR';
  },
};

