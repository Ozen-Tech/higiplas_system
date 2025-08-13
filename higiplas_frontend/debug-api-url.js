// Script para debugar qual URL a API está usando no frontend
// Execute no console do browser na página do frontend

console.log('🔍 Debug da configuração da API');
console.log('Environment:', process.env.NODE_ENV);
console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);

// Tenta importar o apiService para ver a URL base
try {
  // Se estiver no browser, pode não funcionar, mas vale a tentativa
  const apiService = require('./src/services/apiService');
  console.log('API Service baseURL:', apiService.baseURL);
} catch (e) {
  console.log('Não foi possível importar apiService no browser');
}

// Verifica se há fetch interceptado
if (window.fetch.toString().includes('native')) {
  console.log('✅ Fetch nativo sendo usado');
} else {
  console.log('⚠️ Fetch foi interceptado/modificado');
}

// Testa uma requisição simples
fetch('/api/test-url')
  .then(response => {
    console.log('Teste de fetch local funcionou');
  })
  .catch(error => {
    console.log('Erro no teste de fetch local:', error);
  });

console.log('\n💡 Para testar manualmente:');
console.log('1. Abra o Network tab do DevTools');
console.log('2. Tente fazer uma ação que falha (excluir/editar cliente)');
console.log('3. Verifique para qual URL a requisição está sendo enviada');
console.log('4. Verifique os headers da requisição');