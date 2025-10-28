import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import errorHandler from './plugins/errorHandler'
import cacheMiddleware from './plugins/cacheMiddleware'
import { useAuthStore } from '@/stores/auth'

// Configuração do Vuetify
import vuetify from './plugins/vuetify'

// Estilos
import './assets/styles/main.scss'
// Tema personalizado da Levitiis
import '@/assets/styles/levitiis-theme.scss'
import './assets/css/accessibility.css'

const app = createApp(App)

// Configurar plugins
app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(errorHandler)
app.use(cacheMiddleware)

// Inicializar autenticação antes de montar a aplicação
const bootstrap = async () => {
  const authStore = useAuthStore()
  await authStore.initializeAuth()
  app.mount('#app')
}

bootstrap()