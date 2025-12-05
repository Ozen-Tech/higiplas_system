// /src/components/perfil/ProfileForm.tsx

'use client';

import { useState, FormEvent, ChangeEvent } from 'react';
import Image from 'next/image';
import { User, UserUpdate } from '@/types';
import Input from '@/components/Input';
import Button from '@/components/Button';
import { User as UserIcon } from 'lucide-react';

interface ProfileFormProps {
  user: User;
  onUpdate: (data: UserUpdate) => Promise<void>;
}

export default function ProfileForm({ user, onUpdate }: ProfileFormProps) {
  const [formData, setFormData] = useState<UserUpdate>({
    nome: user.nome || '',
    email: user.email || '',
    foto_perfil: user.foto_perfil || null,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Converter para base64 (simples, pode ser melhorado com upload de arquivo)
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => ({
          ...prev,
          foto_perfil: reader.result as string
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onUpdate(formData);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Foto de Perfil */}
      <div className="flex flex-col items-center space-y-4">
        <div className="relative">
          {formData.foto_perfil ? (
            <Image
              src={formData.foto_perfil}
              alt="Foto de perfil"
              width={128}
              height={128}
              className="w-32 h-32 rounded-full object-cover border-4 border-higiplas-blue"
            />
          ) : (
            <div className="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center border-4 border-higiplas-blue">
              <UserIcon className="w-16 h-16 text-gray-400" />
            </div>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Alterar Foto de Perfil
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-higiplas-blue file:text-white
              hover:file:bg-blue-800
              cursor-pointer"
          />
        </div>
      </div>

      {/* Nome */}
      <Input
        label="Nome"
        name="nome"
        type="text"
        required
        value={formData.nome || ''}
        onChange={handleInputChange}
      />

      {/* Email */}
      <Input
        label="E-mail"
        name="email"
        type="email"
        required
        value={formData.email || ''}
        onChange={handleInputChange}
      />

      {/* Botões */}
      <div className="flex justify-end space-x-4 pt-4">
        <Button
          type="submit"
          variant="primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Salvando...' : 'Salvar Alterações'}
        </Button>
      </div>
    </form>
  );
}


