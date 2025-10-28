/**
 * Testes para Navegação e Roteamento
 * Arquiteto: Análise de UX e Navegabilidade
 */

// Simulação das rotas do sistema
const routes = [
  // Rotas de autenticação
  { path: '/login', name: 'Login', requiresAuth: false },
  { path: '/register', name: 'Register', requiresAuth: false },
  
  // Rotas principais
  { path: '/', name: 'Dashboard', requiresAuth: true },
  { path: '/profile', name: 'Profile', requiresAuth: true },
  
  // Rotas administrativas
  { path: '/admin/settings', name: 'Settings', requiresAuth: true, requiresAdmin: true },
  { path: '/admin/users', name: 'Users', requiresAuth: true, requiresAdmin: true },
  
  // Rotas de ativos
  { path: '/assets', name: 'Assets', requiresAuth: true },
  { path: '/assets/movements', name: 'AssetMovements', requiresAuth: true },
  
  // Rotas de empréstimos
  { path: '/loans/employees', name: 'EmployeeLoans', requiresAuth: true },
  { path: '/loans/third-parties', name: 'ThirdPartyLoans', requiresAuth: true },
  
  // Rotas de auditoria
  { path: '/audits', name: 'Audits', requiresAuth: true },
  { path: '/physical-inventory', name: 'PhysicalInventory', requiresAuth: true },
  
  // Rotas de análise
  { path: '/analytics', name: 'Analytics', requiresAuth: true },
  { path: '/test-charts', name: 'TestCharts', requiresAuth: true }
];

// Simulação de usuários
const users = {
  admin: { role: 'admin', authenticated: true },
  user: { role: 'user', authenticated: true },
  guest: { role: null, authenticated: false }
};

// Função para validar acesso a rota
function canAccessRoute(route, user) {
  // Se a rota requer autenticação e o usuário não está autenticado
  if (route.requiresAuth && !user.authenticated) {
    return { allowed: false, reason: 'Usuário não autenticado' };
  }
  
  // Se a rota requer admin e o usuário não é admin
  if (route.requiresAdmin && user.role !== 'admin') {
    return { allowed: false, reason: 'Acesso restrito a administradores' };
  }
  
  return { allowed: true, reason: 'Acesso permitido' };
}

// Função para validar breadcrumbs
function validateBreadcrumbs(routeName) {
  const breadcrumbMap = {
    'Dashboard': [{ text: 'Dashboard', to: '/' }],
    'Profile': [
      { text: 'Dashboard', to: '/' },
      { text: 'Perfil', to: '/profile' }
    ],
    'Settings': [
      { text: 'Dashboard', to: '/' },
      { text: 'Administração', to: '#' },
      { text: 'Configurações', to: '/admin/settings' }
    ],
    'Users': [
      { text: 'Dashboard', to: '/' },
      { text: 'Administração', to: '#' },
      { text: 'Usuários', to: '/admin/users' }
    ],
    'Assets': [
      { text: 'Dashboard', to: '/' },
      { text: 'Ativos', to: '/assets' }
    ]
  };
  
  return breadcrumbMap[routeName] || [];
}

// Executar testes
console.log('🧭 INICIANDO TESTES DE NAVEGAÇÃO E ROTEAMENTO\n');

let testsPassed = 0;
let testsFailed = 0;

function runTest(testName, testFunction) {
  try {
    const result = testFunction();
    if (result) {
      console.log(`✅ ${testName}: PASSOU`);
      testsPassed++;
    } else {
      console.log(`❌ ${testName}: FALHOU`);
      testsFailed++;
    }
  } catch (error) {
    console.log(`❌ ${testName}: ERRO - ${error.message}`);
    testsFailed++;
  }
}

// Teste 1: Rota do perfil existe
runTest('Rota do perfil existe', () => {
  const profileRoute = routes.find(r => r.name === 'Profile');
  return profileRoute && profileRoute.path === '/profile';
});

// Teste 2: Rota do perfil requer autenticação
runTest('Rota do perfil requer autenticação', () => {
  const profileRoute = routes.find(r => r.name === 'Profile');
  return profileRoute && profileRoute.requiresAuth === true;
});

// Teste 3: Usuário autenticado pode acessar perfil
runTest('Usuário autenticado pode acessar perfil', () => {
  const profileRoute = routes.find(r => r.name === 'Profile');
  const access = canAccessRoute(profileRoute, users.admin);
  return access.allowed;
});

// Teste 4: Usuário não autenticado não pode acessar perfil
runTest('Usuário não autenticado não pode acessar perfil', () => {
  const profileRoute = routes.find(r => r.name === 'Profile');
  const access = canAccessRoute(profileRoute, users.guest);
  return !access.allowed;
});

// Teste 5: Rotas administrativas requerem admin
runTest('Rotas administrativas requerem admin', () => {
  const settingsRoute = routes.find(r => r.name === 'Settings');
  const usersRoute = routes.find(r => r.name === 'Users');
  
  const userAccess = canAccessRoute(settingsRoute, users.user);
  const adminAccess = canAccessRoute(settingsRoute, users.admin);
  
  return !userAccess.allowed && adminAccess.allowed;
});

// Teste 6: Breadcrumbs do perfil estão corretos
runTest('Breadcrumbs do perfil estão corretos', () => {
  const breadcrumbs = validateBreadcrumbs('Profile');
  const expectedBreadcrumbs = [
    { text: 'Dashboard', to: '/' },
    { text: 'Perfil', to: '/profile' }
  ];
  
  return JSON.stringify(breadcrumbs) === JSON.stringify(expectedBreadcrumbs);
});

// Teste 7: Todas as rotas principais existem
runTest('Todas as rotas principais existem', () => {
  const requiredRoutes = ['Dashboard', 'Profile', 'Assets', 'EmployeeLoans', 'Audits', 'Settings'];
  const existingRoutes = routes.map(r => r.name);
  
  return requiredRoutes.every(route => existingRoutes.includes(route));
});

// Teste 8: Rotas públicas não requerem autenticação
runTest('Rotas públicas não requerem autenticação', () => {
  const publicRoutes = routes.filter(r => !r.requiresAuth);
  const loginRoute = publicRoutes.find(r => r.name === 'Login');
  const registerRoute = publicRoutes.find(r => r.name === 'Register');
  
  return loginRoute && registerRoute;
});

// Teste 9: Validação de paths únicos
runTest('Paths das rotas são únicos', () => {
  const paths = routes.map(r => r.path);
  const uniquePaths = [...new Set(paths)];
  
  return paths.length === uniquePaths.length;
});

// Teste 10: Validação de nomes únicos
runTest('Nomes das rotas são únicos', () => {
  const names = routes.map(r => r.name);
  const uniqueNames = [...new Set(names)];
  
  return names.length === uniqueNames.length;
});

console.log('\n📊 RESULTADOS DOS TESTES DE NAVEGAÇÃO:');
console.log(`✅ Testes Aprovados: ${testsPassed}`);
console.log(`❌ Testes Falharam: ${testsFailed}`);
console.log(`📈 Taxa de Sucesso: ${((testsPassed / (testsPassed + testsFailed)) * 100).toFixed(1)}%`);

// Teste de cobertura de rotas
console.log('\n🗺️  ANÁLISE DE COBERTURA DE ROTAS:');

const routesByCategory = {
  'Autenticação': routes.filter(r => ['Login', 'Register'].includes(r.name)),
  'Principais': routes.filter(r => ['Dashboard', 'Profile'].includes(r.name)),
  'Administrativas': routes.filter(r => r.requiresAdmin),
  'Ativos': routes.filter(r => r.name.includes('Asset')),
  'Empréstimos': routes.filter(r => r.name.includes('Loan')),
  'Auditoria': routes.filter(r => ['Audits', 'PhysicalInventory'].includes(r.name)),
  'Análise': routes.filter(r => ['Analytics', 'TestCharts'].includes(r.name))
};

Object.entries(routesByCategory).forEach(([category, categoryRoutes]) => {
  console.log(`📂 ${category}: ${categoryRoutes.length} rotas`);
  categoryRoutes.forEach(route => {
    console.log(`   - ${route.name} (${route.path})`);
  });
});

console.log(`\n📊 Total de rotas: ${routes.length}`);
console.log(`🔒 Rotas protegidas: ${routes.filter(r => r.requiresAuth).length}`);
console.log(`👑 Rotas administrativas: ${routes.filter(r => r.requiresAdmin).length}`);
console.log(`🌐 Rotas públicas: ${routes.filter(r => !r.requiresAuth).length}`);

export { routes, canAccessRoute, validateBreadcrumbs };