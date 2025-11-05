// /src/app/dashboard/usuarios/page.tsx
// Página de criação de usuários em produção (apenas para ADMIN)

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { UserPlus, ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/apiService';
import { Header } from '@/components/dashboard/Header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import toast from 'react-hot-toast';

interface UsuarioCreatePayload {
  nome: string;
  email: string;
  password: string;
  empresa_id: number;
  perfil: 'ADMIN' | 'GESTOR' | 'VENDEDOR';
}

export default function CriarUsuarioPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [isChecking, setIsChecking] = useState(true);
  
  const [formData, setFormData] = useState<UsuarioCreatePayload>({
    nome: '',
    email: '',
    password: '',
    empresa_id: 1, // Default, pode ser ajustado se necessário
    perfil: 'VENDEDOR',
  });
  
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Verificar se o usuário é ADMIN
  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        router.replace('/');
        return;
      }
      
      if (user.perfil !== 'ADMIN') {
        toast.error('Acesso negado. Apenas administradores podem criar usuários.');
        router.replace('/dashboard');
        return;
      }
      
      setIsChecking(false);
    }
  }, [user, authLoading, router]);

  // Validação do formulário
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.nome.trim() || formData.nome.length < 3) {
      newErrors.nome = 'Nome deve ter pelo menos 3 caracteres';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'E-mail é obrigatório';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'E-mail inválido';
    }

    if (!formData.password || formData.password.length < 6) {
      newErrors.password = 'Senha deve ter pelo menos 6 caracteres';
    }

    if (formData.password !== confirmPassword) {
      newErrors.confirmPassword = 'As senhas não conferem';
    }

    if (!formData.perfil) {
      newErrors.perfil = 'Perfil é obrigatório';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Por favor, corrija os erros no formulário');
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.post('/users/', formData);
      
      if (response?.data) {
        toast.success(`Usuário ${formData.nome} criado com sucesso!`);
        
        // Limpar formulário
        setFormData({
          nome: '',
          email: '',
          password: '',
          empresa_id: 1,
          perfil: 'VENDEDOR',
        });
        setConfirmPassword('');
        setErrors({});
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar usuário';
      
      if (errorMessage.includes('E-mail já registrado')) {
        setErrors({ email: 'Este e-mail já está em uso' });
        toast.error('Este e-mail já está cadastrado no sistema');
      } else {
        toast.error(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof UsuarioCreatePayload, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Limpar erro do campo quando o usuário começar a digitar
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  if (authLoading || isChecking) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-100 dark:bg-gray-900">
        <div className="text-center">
          <p className="text-lg">Verificando permissões...</p>
        </div>
      </div>
    );
  }

  if (user && user.perfil !== 'ADMIN') {
    return null; // O redirect já foi feito no useEffect
  }

  return (
    <>
      <Header>
        <Button variant="ghost" onClick={() => router.back()} className="gap-2">
          <ArrowLeft size={16} /> Voltar
        </Button>
        <h1 className="text-xl font-bold">Criar Novo Usuário</h1>
      </Header>
      
      <main className="flex-1 p-6">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus size={24} />
                Novo Usuário
              </CardTitle>
              <CardDescription>
                Preencha os dados para criar um novo usuário no sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Nome */}
                <div className="space-y-2">
                  <Label htmlFor="nome">Nome Completo *</Label>
                  <Input
                    id="nome"
                    type="text"
                    placeholder="Digite o nome completo"
                    value={formData.nome}
                    onChange={(e) => handleChange('nome', e.target.value)}
                    className={errors.nome ? 'border-red-500' : ''}
                  />
                  {errors.nome && (
                    <p className="text-sm text-red-500 flex items-center gap-1">
                      <AlertCircle size={14} />
                      {errors.nome}
                    </p>
                  )}
                </div>

                {/* E-mail */}
                <div className="space-y-2">
                  <Label htmlFor="email">E-mail *</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="usuario@exemplo.com"
                    value={formData.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    className={errors.email ? 'border-red-500' : ''}
                  />
                  {errors.email && (
                    <p className="text-sm text-red-500 flex items-center gap-1">
                      <AlertCircle size={14} />
                      {errors.email}
                    </p>
                  )}
                </div>

                {/* Senha */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="password">Senha *</Label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="Mínimo 6 caracteres"
                      value={formData.password}
                      onChange={(e) => handleChange('password', e.target.value)}
                      className={errors.password ? 'border-red-500' : ''}
                    />
                    {errors.password && (
                      <p className="text-sm text-red-500 flex items-center gap-1">
                        <AlertCircle size={14} />
                        {errors.password}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirmar Senha *</Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      placeholder="Digite a senha novamente"
                      value={confirmPassword}
                      onChange={(e) => {
                        setConfirmPassword(e.target.value);
                        if (errors.confirmPassword) {
                          setErrors(prev => {
                            const newErrors = { ...prev };
                            delete newErrors.confirmPassword;
                            return newErrors;
                          });
                        }
                      }}
                      className={errors.confirmPassword ? 'border-red-500' : ''}
                    />
                    {errors.confirmPassword && (
                      <p className="text-sm text-red-500 flex items-center gap-1">
                        <AlertCircle size={14} />
                        {errors.confirmPassword}
                      </p>
                    )}
                  </div>
                </div>

                {/* Perfil */}
                <div className="space-y-2">
                  <Label htmlFor="perfil">Perfil *</Label>
                  <Select
                    value={formData.perfil}
                    onValueChange={(value) => handleChange('perfil', value as 'ADMIN' | 'GESTOR' | 'VENDEDOR')}
                  >
                    <SelectTrigger id="perfil" className={errors.perfil ? 'border-red-500' : ''}>
                      <SelectValue placeholder="Selecione o perfil" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="VENDEDOR">Vendedor</SelectItem>
                      <SelectItem value="GESTOR">Gestor</SelectItem>
                      <SelectItem value="ADMIN">Administrador</SelectItem>
                    </SelectContent>
                  </Select>
                  {errors.perfil && (
                    <p className="text-sm text-red-500 flex items-center gap-1">
                      <AlertCircle size={14} />
                      {errors.perfil}
                    </p>
                  )}
                  <p className="text-xs text-gray-500">
                    Vendedor: Acesso ao módulo de vendas e orçamentos<br />
                    Gestor: Acesso completo exceto criação de usuários<br />
                    Administrador: Acesso total ao sistema
                  </p>
                </div>

                {/* Empresa ID (pode ser oculto ou editável dependendo da necessidade) */}
                <div className="space-y-2">
                  <Label htmlFor="empresa_id">ID da Empresa</Label>
                  <Input
                    id="empresa_id"
                    type="number"
                    min="1"
                    value={formData.empresa_id}
                    onChange={(e) => handleChange('empresa_id', parseInt(e.target.value) || 1)}
                  />
                  <p className="text-xs text-gray-500">
                    ID da empresa à qual o usuário pertence (padrão: 1)
                  </p>
                </div>

                {/* Botões */}
                <div className="flex gap-4 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => router.back()}
                    className="flex-1"
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    disabled={loading}
                    className="flex-1 gap-2"
                  >
                    {loading ? (
                      <>Criando...</>
                    ) : (
                      <>
                        <UserPlus size={18} />
                        Criar Usuário
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  );
}

