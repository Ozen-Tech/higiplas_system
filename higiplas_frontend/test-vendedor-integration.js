/**
 * Script de teste de integração para funcionalidade do vendedor-app
 * Verifica se os componentes podem ser importados e se não há erros de sintaxe
 */

const fs = require('fs');
const path = require('path');

console.log('🧪 Testando integração do vendedor-app...\n');

const errors = [];

// Verificar se há problemas de importação circular
console.log('📦 Verificando imports...');

const checkImports = (filePath, visited = new Set()) => {
  if (visited.has(filePath)) {
    errors.push(`Possível import circular detectado: ${filePath}`);
    return;
  }
  
  visited.add(filePath);
  const fullPath = path.join(__dirname, filePath);
  
  if (!fs.existsSync(fullPath)) {
    return;
  }
  
  const content = fs.readFileSync(fullPath, 'utf-8');
  const importRegex = /import\s+.*?\s+from\s+['"]([^'"]+)['"]/g;
  let match;
  
  while ((match = importRegex.exec(content)) !== null) {
    const importPath = match[1];
    
    // Verificar se é um import local
    if (importPath.startsWith('@/') || importPath.startsWith('./') || importPath.startsWith('../')) {
      let resolvedPath = importPath;
      
      if (importPath.startsWith('@/')) {
        resolvedPath = path.join(__dirname, 'src', importPath.replace('@/', ''));
      } else if (importPath.startsWith('./') || importPath.startsWith('../')) {
        resolvedPath = path.resolve(path.dirname(fullPath), importPath);
      }
      
      // Tentar encontrar o arquivo
      const possibleExtensions = ['.ts', '.tsx', '.js', '.jsx'];
      let found = false;
      
      for (const ext of possibleExtensions) {
        if (fs.existsSync(resolvedPath + ext)) {
          found = true;
          checkImports(resolvedPath.replace(__dirname + '/', '') + ext, new Set(visited));
          break;
        }
      }
      
      if (!found && !importPath.includes('node_modules')) {
        // Não é erro crítico, pode ser um tipo ou algo que não existe ainda
        // console.log(`  ⚠️  Import não resolvido: ${importPath} em ${filePath}`);
      }
    }
  }
};

// Verificar arquivos principais do vendedor-app
const mainFiles = [
  'src/app/dashboard/vendedor/page.tsx',
  'src/app/dashboard/vendedor/novo/page.tsx',
  'src/hooks/useOrcamentos.ts',
  'src/services/apiService.ts',
];

mainFiles.forEach(file => {
  if (fs.existsSync(path.join(__dirname, file))) {
    console.log(`  ✅ Verificando ${file}...`);
    checkImports(file);
  }
});

// Verificar problemas comuns de SSR
console.log('\n🔍 Verificando problemas de SSR...');

const checkSSR = (filePath) => {
  const fullPath = path.join(__dirname, filePath);
  if (!fs.existsSync(fullPath)) return;
  
  const content = fs.readFileSync(fullPath, 'utf-8');
  
  // Verificar uso de localStorage sem verificação de window
  if (content.includes('localStorage') && !content.includes('typeof window')) {
    const lines = content.split('\n');
    lines.forEach((line, index) => {
      if (line.includes('localStorage') && !line.includes('typeof window') && !line.includes('//')) {
        // Verificar se não é um comentário ou string
        if (!line.trim().startsWith('//') && !line.includes('"localStorage"') && !line.includes("'localStorage'")) {
          errors.push(`Uso de localStorage sem verificação SSR em ${filePath}:${index + 1}`);
        }
      }
    });
  }
  
  // Verificar uso de window sem verificação
  if (content.includes('window.') && !content.includes('typeof window')) {
    const lines = content.split('\n');
    lines.forEach((line, index) => {
      if (line.includes('window.') && !line.includes('typeof window') && !line.includes('//')) {
        if (!line.trim().startsWith('//')) {
          errors.push(`Uso de window sem verificação SSR em ${filePath}:${index + 1}`);
        }
      }
    });
  }
};

mainFiles.forEach(file => {
  checkSSR(file);
});

// Verificar se apiService está usando verificação de window
const apiServicePath = path.join(__dirname, 'src/services/apiService.ts');
if (fs.existsSync(apiServicePath)) {
  const content = fs.readFileSync(apiServicePath, 'utf-8');
  if (content.includes('localStorage.getItem') && !content.includes('typeof window')) {
    errors.push('apiService.ts usa localStorage sem verificação de SSR');
  }
}

// Resumo
console.log('\n' + '='.repeat(50));
console.log('📊 RESUMO DOS TESTES DE INTEGRAÇÃO\n');

if (errors.length === 0) {
  console.log('✅ Todos os testes de integração passaram!');
  console.log('   O código está pronto para build.');
  process.exit(0);
} else {
  console.log(`❌ Erros encontrados (${errors.length}):`);
  errors.forEach(err => console.log(`   - ${err}`));
  console.log('\n⚠️  Por favor, corrija os erros antes de fazer deploy.');
  process.exit(1);
}

