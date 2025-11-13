import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { setupAuthGuards } from '@/middleware/auth'
import logger from '@/utils/logger'

// Layouts
import AuthLayout from '@/layouts/AuthLayout.vue'
import MainLayout from '@/layouts/MainLayout.vue'

// Views críticas (carregamento imediato)
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import Dashboard from '@/views/Dashboard.vue'

// Lazy loading com loading states e error handling
const lazyLoad = (importer, chunkName) => {
  return () => importer().catch(error => {
    logger.error(`Erro ao carregar componente via lazyLoad`, {
      chunkName,
      error: error.message
    })
    return import('@/components/common/ErrorFallback.vue')
  })
}

// Componentes com lazy loading otimizado
const Assets = () => import('@/views/assets/Assets.vue')
const NetworkDiscovery = lazyLoad(() => import('@/views/NetworkDiscovery.vue'), 'network-discovery')
const Movements = lazyLoad(() => import('@/views/Movements.vue'), 'movements')
const MovementsList = lazyLoad(() => import('@/views/movements/Movements.vue'), 'movements-list')
const Locations = lazyLoad(() => import('@/views/Locations.vue'), 'locations')
const EmployeeLoans = lazyLoad(() => import('@/views/EmployeeLoans.vue'), 'employee-loans')
const Employees = lazyLoad(() => import('@/views/Employees.vue'), 'employees')
const ThirdParties = lazyLoad(() => import('@/views/ThirdParties.vue'), 'third-parties')
const ThirdPartyLoans = lazyLoad(() => import('@/views/ThirdPartyLoans.vue'), 'third-party-loans')
const Audits = lazyLoad(() => import('@/views/Audits.vue'), 'audits')
const PhysicalInventory = lazyLoad(() => import('@/views/PhysicalInventory.vue'), 'physical-inventory')
const ServiceOrders = lazyLoad(() => import('@/views/ServiceOrders.vue'), 'service-orders')
const Schedules = lazyLoad(() => import('@/views/maintenance/Schedule.vue'), 'schedules')
const SLAContracts = lazyLoad(() => import('@/views/maintenance/SLAContracts.vue'), 'sla-contracts')
const Reports = lazyLoad(() => import('@/views/Reports.vue'), 'reports')
const ReportsAnalytics = lazyLoad(() => import('@/views/reports/Analytics.vue'), 'reports-analytics')
const TestCharts = lazyLoad(() => import('@/views/TestCharts.vue'), 'test-charts')
const Users = lazyLoad(() => import('@/views/admin/Users.vue'), 'users')
const Settings = lazyLoad(() => import('@/views/admin/Settings.vue'), 'settings')
const Profile = lazyLoad(() => import('@/views/Profile.vue'), 'profile')
const Machines = lazyLoad(() => import('@/views/Machines.vue'), 'machines')
const MonitoringView = lazyLoad(() => import('@/views/MonitoringView.vue'), 'monitoring')
const DesignSystemDemo = lazyLoad(() => import('@/components/demo/DesignSystemDemo.vue'), 'design-system-demo')
const Purchases = lazyLoad(() => import('@/views/purchases/Purchases.vue'), 'purchases')
const Licenses = lazyLoad(() => import('@/views/licenses/Licenses.vue'), 'licenses')
const Software = lazyLoad(() => import('@/views/software/Software.vue'), 'software')
const Payments = lazyLoad(() => import('@/views/payments/Payments.vue'), 'payments')

const routes = [
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: Login,
        meta: { requiresGuest: true }
      },
      {
        path: 'register',
        name: 'Register',
        component: Register,
        meta: { requiresGuest: true }
      }
    ]
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: false },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
        meta: { 
          title: 'Dashboard',
          breadcrumb: [{ text: 'Dashboard', to: '/' }]
        }
      },
      {
      path: '/test',
      name: 'TestFunctionalities',
      component: () => import('@/views/TestFunctionalities.vue'),
      meta: {
        title: 'Teste de Funcionalidades',
        breadcrumb: [
          { text: 'Dashboard', to: '/' },
          { text: 'Teste', to: '/test' }
        ]
      }
    },
    {
      path: '/analytics',
      name: 'Analytics',
      component: () => import('@/views/Analytics.vue'),
      meta: {
        title: 'Analytics',
        breadcrumb: [
          { text: 'Dashboard', to: '/' },
          { text: 'Analytics', to: '/analytics' }
        ]
      }
    },
    {
      path: '/design-system',
      name: 'DesignSystemDemo',
      component: DesignSystemDemo,
      meta: {
        title: 'Design System Levitiis',
        breadcrumb: [
          { text: 'Dashboard', to: '/' },
          { text: 'Design System', to: '/design-system' }
        ]
      }
    },
    {
      path: '/assets',
      name: 'Assets',
      component: Assets,
      meta: { 
        title: 'Lista de Ativos',
        breadcrumb: [
          { text: 'Dashboard', to: '/' },
          { text: 'Ativos', to: '/assets' }
        ]
      }
    },
      {
        path: '/assets/network-discovery',
        name: 'NetworkDiscovery',
        component: NetworkDiscovery,
        meta: { 
          title: 'Descoberta de Rede',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Ativos', to: '/assets' },
            { text: 'Descoberta de Rede', to: '/assets/network-discovery' }
          ]
        }
      },
      {
        path: '/machines',
        name: 'Machines',
        component: Machines,
        meta: { 
          title: 'Monitoramento de Máquinas',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Monitoramento', to: '/machines' }
          ]
        }
      },
      {
        path: '/monitoring',
        name: 'Monitoring',
        component: MonitoringView,
        meta: { 
          title: 'Dashboard de Monitoramento',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Monitoramento', to: '/monitoring' }
          ]
        }
      },
      {
        path: '/movements',
        name: 'Movements',
        component: Movements,
        meta: { 
          title: 'Movimentações',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Movimentações', to: '/movements' }
          ]
        },
        children: [
          {
            path: '',
            name: 'MovementsRedirect',
            redirect: '/movements/list'
          },
          {
            path: 'list',
            name: 'MovementsList',
            component: MovementsList,
            meta: { 
              title: 'Lista de Movimentações',
              breadcrumb: [
                { text: 'Dashboard', to: '/' },
                { text: 'Movimentações', to: '/movements' }
              ]
            }
          }
        ]
      },
      {
        path: '/locations',
        name: 'Locations',
        component: Locations,
        meta: { 
          title: 'Localizações',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Localizações', to: '/locations' }
          ]
        }
      },
      {
        path: '/employees',
        name: 'Employees',
        component: Employees,
        meta: { 
          title: 'Funcionários',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Empréstimos', to: '#' },
            { text: 'Funcionários', to: '/employees' }
          ]
        }
      },
      {
        path: '/third-parties',
        name: 'ThirdParties',
        component: ThirdParties,
        meta: { 
          title: 'Terceiros',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Empréstimos', to: '#' },
            { text: 'Terceiros', to: '/third-parties' }
          ]
        }
      },
      {
        path: '/loans/employees',
        name: 'EmployeeLoans',
        component: EmployeeLoans,
        meta: { 
          title: 'Empréstimos para Funcionários',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Empréstimos', to: '#' },
            { text: 'Funcionários', to: '/loans/employees' }
          ]
        }
      },
      {
        path: '/loans/third-party',
        name: 'ThirdPartyLoans',
        component: ThirdPartyLoans,
        meta: { 
          title: 'Empréstimos para Terceiros',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Empréstimos', to: '#' },
            { text: 'Terceiros', to: '/loans/third-party' }
          ]
        }
      },
      {
        path: '/audits',
        name: 'Audits',
        component: Audits,
        meta: { 
          title: 'Auditorias',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Auditoria', to: '#' },
            { text: 'Auditorias', to: '/audits' }
          ]
        }
      },
      {
        path: '/audits/physical-inventory',
        name: 'PhysicalInventory',
        component: PhysicalInventory,
        meta: { 
          title: 'Inventário Físico',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Auditoria', to: '#' },
            { text: 'Inventário Físico', to: '/audits/physical-inventory' }
          ]
        }
      },
      {
        path: '/maintenance/service-orders',
        name: 'ServiceOrders',
        component: ServiceOrders,
        meta: { 
          title: 'Ordens de Serviço',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Manutenção', to: '#' },
            { text: 'Ordens de Serviço', to: '/maintenance/service-orders' }
          ]
        }
      },
      {
        path: '/maintenance/schedules',
        name: 'Schedules',
        component: Schedules,
        meta: { 
          title: 'Agendamentos',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Manutenção', to: '#' },
            { text: 'Agendamentos', to: '/maintenance/schedules' }
          ]
        }
      },
      {
        path: '/maintenance/sla-contracts',
        name: 'SLAContracts',
        component: SLAContracts,
        meta: { 
          title: 'SLA & Contratos',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Manutenção', to: '#' },
            { text: 'SLA & Contratos', to: '/maintenance/sla-contracts' }
          ]
        }
      },
      {
        path: '/purchases',
        name: 'Purchases',
        component: Purchases,
        meta: {
          title: 'Compras & Orçamentos',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Compras', to: '/purchases' }
          ]
        }
      },
      {
        path: '/licenses',
        name: 'Licenses',
        component: Licenses,
        meta: {
          title: 'Licenças',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Licenças', to: '/licenses' }
          ]
        }
      },
      {
        path: '/software',
        name: 'Software',
        component: Software,
        meta: {
          title: 'Software',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Software', to: '/software' }
          ]
        }
      },
      {
        path: '/payments',
        name: 'Payments',
        component: Payments,
        meta: {
          title: 'Pagamentos',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Pagamentos', to: '/payments' }
          ]
        }
      },
      {
        path: '/reports',
        name: 'Reports',
        component: Reports,
        meta: { 
          title: 'Relatórios',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Relatórios', to: '/reports' }
          ]
        }
      },
      {
        path: '/reports',
        name: 'Reports',
        component: Reports,
        meta: { 
          title: 'Relatórios',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Relatórios', to: '/reports' }
          ]
        }
      },
      {
        path: '/reports/analytics',
        name: 'ReportsAnalytics',
        component: ReportsAnalytics,
        meta: { 
          title: 'Analytics',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Relatórios', to: '/reports' },
            { text: 'Analytics', to: '/reports/analytics' }
          ]
        }
      },
      {
        path: '/admin/users',
        name: 'Users',
        component: Users,
        meta: { 
          title: 'Usuários',
          requiresRole: 'admin',
          requiresPermission: 'users.manage',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Administração', to: '#' },
            { text: 'Usuários', to: '/admin/users' }
          ]
        }
      },
      {
        path: '/admin/settings',
        name: 'Settings',
        component: Settings,
        meta: { 
          title: 'Configurações',
          requiresRole: 'admin',
          requiresPermission: 'system.configure',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Administração', to: '#' },
            { text: 'Configurações', to: '/admin/settings' }
          ]
        }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: Profile,
        meta: { 
          title: 'Perfil',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Perfil', to: '/profile' }
          ]
        }
      },
      {
        path: '/test-charts',
        name: 'TestCharts',
        component: TestCharts,
        meta: { 
          title: 'Teste de Gráficos',
          breadcrumb: [
            { text: 'Dashboard', to: '/' },
            { text: 'Teste de Gráficos', to: '/test-charts' }
          ]
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Setup authentication guards
setupAuthGuards(router)

export default router