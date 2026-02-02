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

export interface RegrasSugestaoCompra {
  empresa_id?: number;
  lead_time_dias: number;
  cobertura_dias: number;
  dias_analise: number;
  min_vendas_historico: number;
  margem_seguranca: number;
  margem_adicional_cobertura: number;
  dias_antecedencia_cliente: number;
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

  // Regras de sugestão de compra (admin)
  getRegrasSugestaoCompra: async (): Promise<RegrasSugestaoCompra> => {
    const response = await apiService.get('/admin/regras-sugestao-compra');
    return (response?.data || {}) as RegrasSugestaoCompra;
  },
  putRegrasSugestaoCompra: async (body: RegrasSugestaoCompra): Promise<RegrasSugestaoCompra> => {
    const response = await apiService.put('/admin/regras-sugestao-compra', body);
    return (response?.data || {}) as RegrasSugestaoCompra;
  },
};

