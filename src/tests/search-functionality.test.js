/**
 * Testes para Funcionalidade de Busca Inteligente
 * Arquiteto: Análise de Qualidade de Software
 */

// Simulação de testes unitários para a funcionalidade de busca
const searchTestCases = [
  // Testes para busca de usuários
  {
    input: 'usuário admin',
    expectedRoute: 'Users',
    description: 'Deve redirecionar para página de usuários ao buscar "usuário"'
  },
  {
    input: 'funcionário joão',
    expectedRoute: 'Users', 
    description: 'Deve redirecionar para página de usuários ao buscar "funcionário"'
  },
  {
    input: 'employee management',
    expectedRoute: 'Users',
    description: 'Deve redirecionar para página de usuários ao buscar "employee"'
  },

  // Testes para busca de empréstimos
  {
    input: 'empréstimo notebook',
    expectedRoute: 'EmployeeLoans',
    description: 'Deve redirecionar para empréstimos ao buscar "empréstimo"'
  },
  {
    input: 'terceiros equipamento',
    expectedRoute: 'EmployeeLoans',
    description: 'Deve redirecionar para empréstimos ao buscar "terceiros"'
  },
  {
    input: 'loan status',
    expectedRoute: 'EmployeeLoans',
    description: 'Deve redirecionar para empréstimos ao buscar "loan"'
  },

  // Testes para busca de auditoria
  {
    input: 'auditoria 2024',
    expectedRoute: 'Audits',
    description: 'Deve redirecionar para auditorias ao buscar "auditoria"'
  },
  {
    input: 'inventário físico',
    expectedRoute: 'Audits',
    description: 'Deve redirecionar para auditorias ao buscar "inventário"'
  },
  {
    input: 'audit report',
    expectedRoute: 'Audits',
    description: 'Deve redirecionar para auditorias ao buscar "audit"'
  },

  // Testes para busca padrão (ativos)
  {
    input: 'notebook dell',
    expectedRoute: 'Assets',
    description: 'Deve redirecionar para ativos por padrão'
  },
  {
    input: 'impressora hp',
    expectedRoute: 'Assets',
    description: 'Deve redirecionar para ativos ao buscar equipamentos'
  },
  {
    input: 'monitor samsung',
    expectedRoute: 'Assets',
    description: 'Deve redirecionar para ativos ao buscar por marca'
  }
];

// Função para simular o comportamento da busca
function simulateSearch(query) {
  const lowerQuery = query.toLowerCase().trim();
  
  if (lowerQuery.includes('usuário') || lowerQuery.includes('usuario') || lowerQuery.includes('user') || 
      lowerQuery.includes('funcionário') || lowerQuery.includes('funcionario') || lowerQuery.includes('employee')) {
    return 'Users';
  }
  else if (lowerQuery.includes('empréstimo') || lowerQuery.includes('emprestimo') || lowerQuery.includes('loan') ||
           lowerQuery.includes('terceiro') || lowerQuery.includes('terceiros')) {
    return 'EmployeeLoans';
  }
  else if (lowerQuery.includes('auditoria') || lowerQuery.includes('audit') || lowerQuery.includes('inventário') || 
           lowerQuery.includes('inventario') || lowerQuery.includes('inventory')) {
    return 'Audits';
  }
  else {
    return 'Assets';
  }
}

// Executar testes
console.log('🧪 INICIANDO TESTES DE BUSCA INTELIGENTE\n');

let passedTests = 0;
let failedTests = 0;

searchTestCases.forEach((testCase, index) => {
  const result = simulateSearch(testCase.input);
  const passed = result === testCase.expectedRoute;
  
  if (passed) {
    passedTests++;
    console.log(`✅ Teste ${index + 1}: PASSOU`);
  } else {
    failedTests++;
    console.log(`❌ Teste ${index + 1}: FALHOU`);
    console.log(`   Entrada: "${testCase.input}"`);
    console.log(`   Esperado: ${testCase.expectedRoute}`);
    console.log(`   Obtido: ${result}`);
  }
  console.log(`   Descrição: ${testCase.description}\n`);
});

console.log('📊 RESULTADOS DOS TESTES:');
console.log(`✅ Testes Aprovados: ${passedTests}`);
console.log(`❌ Testes Falharam: ${failedTests}`);
console.log(`📈 Taxa de Sucesso: ${((passedTests / searchTestCases.length) * 100).toFixed(1)}%`);

// Testes de edge cases
console.log('\n🔍 TESTANDO CASOS EXTREMOS:');

const edgeCases = [
  { input: '', expected: 'Assets', description: 'String vazia deve ir para Assets' },
  { input: '   ', expected: 'Assets', description: 'Apenas espaços deve ir para Assets' },
  { input: 'USUÁRIO', expected: 'Users', description: 'Maiúsculas devem funcionar' },
  { input: 'usuário empréstimo', expected: 'Users', description: 'Primeira palavra-chave deve ter prioridade' }
];

edgeCases.forEach((testCase, index) => {
  const result = simulateSearch(testCase.input);
  const passed = result === testCase.expected;
  
  console.log(`${passed ? '✅' : '❌'} Edge Case ${index + 1}: ${testCase.description}`);
  if (!passed) {
    console.log(`   Entrada: "${testCase.input}"`);
    console.log(`   Esperado: ${testCase.expected}, Obtido: ${result}`);
  }
});

export { searchTestCases, simulateSearch };