// /src/components/perfil/PasswordForm.tsx

'use client';

import { useState, FormEvent, ChangeEvent } from 'react';
import { UserPasswordUpdate } from '@/types';
import Input from '@/components/Input';
import Button from '@/components/Button';

interface PasswordFormProps {
  onUpdate: (data: UserPasswordUpdate) => Promise<void>;
}

export default function PasswordForm({ onUpdate }: PasswordFormProps) {
  const [formData, setFormData] = useState<UserPasswordUpdate>({
    senha_atual: '',
    nova_senha: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null);
  };

  const handleConfirmPasswordChange = (e: ChangeEvent<HTMLInputElement>) => {
    setConfirmPassword(e.target.value);
    setError(null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validações
    if (formData.nova_senha.length < 6) {
      setError('A nova senha deve ter pelo menos 6 caracteres');
      return;
    }

    if (formData.nova_senha !== confirmPassword) {
      setError('As senhas não coincidem');
      return;
    }

    setIsSubmitting(true);
    try {
      await onUpdate(formData);
      // Limpar formulário após sucesso
      setFormData({
        senha_atual: '',
        nova_senha: '',
      });
      setConfirmPassword('');
    } catch {
      // O erro será tratado pelo hook useProfile
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Senha Atual */}
      <Input
        label="Senha Atual"
        name="senha_atual"
        type="password"
        required
        value={formData.senha_atual}
        onChange={handleInputChange}
      />

      {/* Nova Senha */}
      <Input
        label="Nova Senha"
        name="nova_senha"
        type="password"
        required
        value={formData.nova_senha}
        onChange={handleInputChange}
        minLength={6}
      />

      {/* Confirmar Nova Senha */}
      <Input
        label="Confirmar Nova Senha"
        name="confirmar_senha"
        type="password"
        required
        value={confirmPassword}
        onChange={handleConfirmPasswordChange}
        minLength={6}
      />

      {/* Botões */}
      <div className="flex justify-end space-x-4 pt-4">
        <Button
          type="submit"
          variant="primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Alterando...' : 'Alterar Senha'}
        </Button>
      </div>
    </form>
  );
}


