'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAdmin } from '@/hooks/useAdmin';
import { Header } from '@/components/dashboard/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Loader2, UserPlus, ArrowLeft, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const PERFIS = [
  { value: 'ADMIN', label: 'Administrador' },
  { value: 'GESTOR', label: 'Gestor' },
  { value: 'OPERADOR', label: 'Operador' },
  { value: 'vendedor', label: 'Vendedor' },
];

export default function CriarUsuarioPage() {
  const router = useRouter();
  const { usuario, loading, error, isAdmin, empresas, criarUsuario } = useAdmin();
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    password: '',
    confirmPassword: '',
    empresa_id: '',
    perfil: 'OPERADOR',
  });
  const [usuarioCriado, setUsuarioCriado] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validações
    if (!formData.nome || !formData.email || !formData.password || !formData.empresa_id) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error('As senhas não conferem');
      return;
    }

    if (formData.password.length < 6) {
      toast.error('A senha deve ter pelo menos 6 caracteres');
      return;
    }

    const payload = {
      nome: formData.nome,
      email: formData.email,
      password: formData.password,
      empresa_id: parseInt(formData.empresa_id),
      perfil: formData.perfil,
    };

    const novoUsuario = await criarUsuario(payload);

    if (novoUsuario) {
      setUsuarioCriado(true);
      // Limpar formulário
      setFormData({
        nome: '',
        email: '',
        password: '',
        confirmPassword: '',
        empresa_id: '',
        perfil: 'OPERADOR',
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Carregando...</p>
        </div>
      </div>
    );
  }

  if (error || !isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="max-w-md w-full">
          <CardContent className="p-6 text-center space-y-4">
            <p className="text-red-600 dark:text-red-400">
              {error || 'Acesso negado. Apenas o administrador pode acessar esta área.'}
            </p>
            <Button onClick={() => router.push('/dashboard')}>
              Voltar para o Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (usuarioCriado) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="max-w-md w-full">
          <CardContent className="p-6 text-center space-y-4">
            <CheckCircle className="h-12 w-12 text-green-600 mx-auto" />
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              Usuário criado com sucesso!
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              O usuário foi criado e já pode fazer login no sistema.
            </p>
            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={() => setUsuarioCriado(false)}
                className="flex-1"
              >
                Criar Outro Usuário
              </Button>
              <Button
                onClick={() => router.push('/dashboard')}
                className="flex-1"
              >
                Voltar ao Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <>
      <Header>
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/dashboard')}
          >
            <ArrowLeft size={16} className="mr-2" /> Voltar
          </Button>
          <div>
            <h1 className="text-xl font-bold">Criar Novo Usuário</h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Administrador: {usuario?.nome}
            </p>
          </div>
        </div>
      </Header>
      <main className="flex-1 p-6">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus size={20} /> Cadastrar Novo Usuário
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="md:col-span-2">
                    <Label htmlFor="nome">Nome Completo *</Label>
                    <Input
                      id="nome"
                      type="text"
                      value={formData.nome}
                      onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                      placeholder="Nome completo do usuário"
                      required
                    />
                  </div>

                  <div className="md:col-span-2">
                    <Label htmlFor="email">E-mail *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      placeholder="usuario@exemplo.com"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="password">Senha *</Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      placeholder="Mínimo 6 caracteres"
                      required
                      minLength={6}
                    />
                  </div>

                  <div>
                    <Label htmlFor="confirmPassword">Confirmar Senha *</Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      value={formData.confirmPassword}
                      onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                      placeholder="Confirme a senha"
                      required
                      minLength={6}
                    />
                  </div>

                  <div>
                    <Label htmlFor="empresa_id">Empresa *</Label>
                    <Select
                      value={formData.empresa_id}
                      onValueChange={(value) => setFormData({ ...formData, empresa_id: value })}
                      required
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione uma empresa" />
                      </SelectTrigger>
                      <SelectContent>
                        {empresas.map((empresa) => (
                          <SelectItem key={empresa.id} value={empresa.id.toString()}>
                            {empresa.nome}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="perfil">Perfil *</Label>
                    <Select
                      value={formData.perfil}
                      onValueChange={(value) => setFormData({ ...formData, perfil: value })}
                      required
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {PERFIS.map((perfil) => (
                          <SelectItem key={perfil.value} value={perfil.value}>
                            {perfil.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => router.push('/dashboard')}
                    className="flex-1"
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    disabled={loading}
                    className="flex-1"
                  >
                    {loading ? (
                      <>
                        <Loader2 size={16} className="mr-2 animate-spin" />
                        Criando...
                      </>
                    ) : (
                      <>
                        <UserPlus size={16} className="mr-2" />
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

