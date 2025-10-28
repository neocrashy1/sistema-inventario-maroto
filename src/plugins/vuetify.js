/**
 * Configuração do Vuetify com tema personalizado da Levitiis
 * Baseado nas cores do site: https://levitiis.com.br/
 */

import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Importar estilos do Vuetify
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

// Paleta de cores da Levitiis extraída do site
const levitiisTheme = {
  dark: false,
  colors: {
    // Cores primárias da Levitiis
    primary: '#6366F1', // Roxo/Azul principal
    secondary: '#8B5CF6', // Roxo secundário
    accent: '#06B6D4', // Azul cyan
    
    // Cores de apoio
    success: '#10B981', // Verde sucesso
    warning: '#F59E0B', // Amarelo/laranja
    error: '#EF4444', // Vermelho erro
    info: '#3B82F6', // Azul informação
    
    // Cores neutras
    background: '#FAFAFA', // Fundo claro
    surface: '#FFFFFF', // Superfície
    'surface-variant': '#F3F4F6', // Variante de superfície
    'on-surface': '#1F2937', // Texto em superfície
    'on-primary': '#FFFFFF', // Texto em primário
    'on-secondary': '#FFFFFF', // Texto em secundário
    
    // Gradientes (representados como cores sólidas)
    'gradient-start': '#6366F1',
    'gradient-end': '#8B5CF6',
    
    // Cores específicas da Levitiis
    'levitiis-purple': '#6366F1',
    'levitiis-blue': '#06B6D4',
    'levitiis-dark': '#1F2937',
    'levitiis-light': '#F8FAFC'
  }
}

const levitiisThemeDark = {
  dark: true,
  colors: {
    // Cores primárias da Levitiis (modo escuro)
    primary: '#8B5CF6',
    secondary: '#6366F1',
    accent: '#06B6D4',
    
    // Cores de apoio
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
    
    // Cores neutras (modo escuro)
    background: '#0F172A', // Fundo escuro
    surface: '#1E293B', // Superfície escura
    'surface-variant': '#334155', // Variante de superfície escura
    'on-surface': '#F1F5F9', // Texto em superfície escura
    'on-primary': '#FFFFFF',
    'on-secondary': '#FFFFFF',
    
    // Gradientes (modo escuro)
    'gradient-start': '#8B5CF6',
    'gradient-end': '#6366F1',
    
    // Cores específicas da Levitiis (modo escuro)
    'levitiis-purple': '#8B5CF6',
    'levitiis-blue': '#06B6D4',
    'levitiis-dark': '#0F172A',
    'levitiis-light': '#1E293B'
  }
}

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'levitiisLight',
    themes: {
      levitiisLight: levitiisTheme,
      levitiisThemeDark: levitiisThemeDark,
    },
    variations: {
      colors: ['primary', 'secondary', 'accent'],
      lighten: 4,
      darken: 4,
    },
  },
  defaults: {
    VBtn: {
      style: 'text-transform: none;', // Remove uppercase padrão
      rounded: 'lg',
    },
    VCard: {
      rounded: 'lg',
      elevation: 2,
    },
    VTextField: {
      rounded: 'lg',
      variant: 'outlined',
    },
    VSelect: {
      rounded: 'lg',
      variant: 'outlined',
    },
    VTextarea: {
      rounded: 'lg',
      variant: 'outlined',
    },
  },
})