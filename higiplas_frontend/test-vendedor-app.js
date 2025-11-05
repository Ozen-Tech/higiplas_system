/**
 * Script de teste para validar funcionalidade do vendedor-app
 * Verifica se os componentes e hooks estão funcionando corretamente
 */

const fs = require('fs');
const path = require('path');

console.log('🧪 Testando funcionalidade do vendedor-app...\n');

const errors = [];
const warnings = [];

// Verificar se os arquivos principais existem
const requiredFiles = [
  'src/app/dashboard/vendedor/page.tsx',
  'src/app/dashboard/vendedor/novo/page.tsx',
  'src/hooks/useOrcamentos.ts',
  'src/hooks/useVendas.ts',
  'src/services/apiService.ts',
  'src/types/orcamentos.ts',
];

console.log('📁 Verificando arquivos principais...');
requiredFiles.forEach(file => {
  const fullPath = path.join(__dirname, file);
  if (fs.existsSync(fullPath)) {
    console.log(`  ✅ ${file}`);
  } else {
    errors.push(`Arquivo não encontrado: ${file}`);
    console.log(`  ❌ ${file} - NÃO ENCONTRADO`);
  }
});

// Verificar imports críticos
console.log('\n📦 Verificando imports...');
const checkFile = (filePath, checks) => {
  const fullPath = path.join(__dirname, filePath);
  if (!fs.existsSync(fullPath)) {
    errors.push(`Arquivo não encontrado para verificação: ${filePath}`);
    return;
  }
  
  const content = fs.readFileSync(fullPath, 'utf-8');
  checks.forEach(check => {
    if (check.type === 'import') {
      if (content.includes(check.pattern)) {
        console.log(`  ✅ ${check.name} encontrado em ${filePath}`);
      } else {
        warnings.push(`Import não encontrado: ${check.name} em ${filePath}`);
        console.log(`  ⚠️  ${check.name} não encontrado em ${filePath}`);
      }
    } else if (check.type === 'export') {
      if (content.includes(check.pattern)) {
        console.log(`  ✅ ${check.name} exportado em ${filePath}`);
      } else {
        warnings.push(`Export não encontrado: ${check.name} em ${filePath}`);
        console.log(`  ⚠️  ${check.name} não exportado em ${filePath}`);
      }
    }
  });
};

// Verificar useOrcamentos
checkFile('src/hooks/useOrcamentos.ts', [
  { type: 'import', name: 'useState', pattern: "import { useState" },
  { type: 'import', name: 'useCallback', pattern: "import { useCallback" },
  { type: 'import', name: 'apiService', pattern: "from '@/services/apiService'" },
  { type: 'export', name: 'useOrcamentos', pattern: 'export function useOrcamentos' },
  { type: 'export', name: 'listarOrcamentosVendedor', pattern: 'listarOrcamentosVendedor' },
  { type: 'export', name: 'criarOrcamento', pattern: 'criarOrcamento' },
]);

// Verificar apiService
checkFile('src/services/apiService.ts', [
  { type: 'export', name: 'apiService', pattern: 'export const apiService' },
  { type: 'export', name: 'getBlob', pattern: 'getBlob:' },
  { type: 'export', name: 'get', pattern: 'get:' },
  { type: 'export', name: 'post', pattern: 'post:' },
]);

// Verificar página do vendedor
checkFile('src/app/dashboard/vendedor/page.tsx', [
  { type: 'import', name: 'useOrcamentos', pattern: "from '@/hooks/useOrcamentos'" },
  { type: 'import', name: 'apiService', pattern: "from '@/services/apiService'" },
  { type: 'export', name: 'VendedorHubPage', pattern: 'export default function VendedorHubPage' },
]);

// Verificar variáveis de ambiente
console.log('\n🌍 Verificando variáveis de ambiente...');
const vercelJsonPath = path.join(__dirname, 'vercel.json');
if (fs.existsSync(vercelJsonPath)) {
  const vercelJson = JSON.parse(fs.readFileSync(vercelJsonPath, 'utf-8'));
  if (vercelJson.env && vercelJson.env.NEXT_PUBLIC_API_URL) {
    console.log(`  ✅ NEXT_PUBLIC_API_URL configurado: ${vercelJson.env.NEXT_PUBLIC_API_URL}`);
  } else {
    warnings.push('NEXT_PUBLIC_API_URL não configurado no vercel.json');
    console.log('  ⚠️  NEXT_PUBLIC_API_URL não configurado');
  }
} else {
  warnings.push('vercel.json não encontrado');
  console.log('  ⚠️  vercel.json não encontrado');
}

// Verificar next.config.ts
console.log('\n⚙️  Verificando configuração do Next.js...');
const nextConfigPath = path.join(__dirname, 'next.config.ts');
if (fs.existsSync(nextConfigPath)) {
  console.log('  ✅ next.config.ts existe');
} else {
  warnings.push('next.config.ts não encontrado');
  console.log('  ⚠️  next.config.ts não encontrado');
}

// Verificar package.json
console.log('\n📋 Verificando dependências...');
const packageJsonPath = path.join(__dirname, 'package.json');
if (fs.existsSync(packageJsonPath)) {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
  const requiredDeps = [
    'next',
    'react',
    'react-dom',
    'react-hot-toast',
    'lucide-react',
  ];
  
  requiredDeps.forEach(dep => {
    if (packageJson.dependencies && packageJson.dependencies[dep]) {
      console.log(`  ✅ ${dep}: ${packageJson.dependencies[dep]}`);
    } else {
      errors.push(`Dependência faltando: ${dep}`);
      console.log(`  ❌ ${dep} - NÃO ENCONTRADO`);
    }
  });
}

// Resumo
console.log('\n' + '='.repeat(50));
console.log('📊 RESUMO DOS TESTES\n');

if (errors.length === 0 && warnings.length === 0) {
  console.log('✅ Todos os testes passaram! A funcionalidade do vendedor-app está OK.');
  process.exit(0);
} else {
  if (errors.length > 0) {
    console.log(`❌ Erros encontrados (${errors.length}):`);
    errors.forEach(err => console.log(`   - ${err}`));
  }
  if (warnings.length > 0) {
    console.log(`\n⚠️  Avisos (${warnings.length}):`);
    warnings.forEach(warn => console.log(`   - ${warn}`));
  }
  process.exit(errors.length > 0 ? 1 : 0);
}

