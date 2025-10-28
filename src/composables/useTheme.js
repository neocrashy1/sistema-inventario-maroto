import { ref, computed, onMounted } from 'vue'
import { useTheme as useVuetifyTheme } from 'vuetify'

/**
 * Composable para gerenciar o tema claro/escuro
 * - Ajusta [data-theme] no elemento root para CSS custom vars
 * - Integra com Vuetify para alternar entre levitiisLight e levitiisThemeDark
 * - Persiste preferência em localStorage
 */
export function useTheme() {
  const theme = ref('light')
  const vuetifyTheme = useVuetifyTheme()

  const setTheme = (newTheme) => {
    theme.value = newTheme === 'dark' ? 'dark' : 'light'

    const root = document.documentElement
    root.setAttribute('data-theme', theme.value)

    localStorage.setItem('app-theme', theme.value)

    // Alternar Vuetify theme
    const target = theme.value === 'dark' ? 'levitiisThemeDark' : 'levitiisLight'
    if (vuetifyTheme?.global?.name) {
      vuetifyTheme.global.name.value = target
    }
  }

  const toggleTheme = () => setTheme(theme.value === 'dark' ? 'light' : 'dark')
  const isDark = computed(() => theme.value === 'dark')

  onMounted(() => {
    const saved = localStorage.getItem('app-theme')
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    const initial = saved || (prefersDark ? 'dark' : 'light')
    setTheme(initial)

    // Atualizar se preferência do sistema mudar (opcional)
    if (window.matchMedia) {
      const media = window.matchMedia('(prefers-color-scheme: dark)')
      const handler = (e) => {
        const auto = localStorage.getItem('app-theme-auto') === 'true'
        if (auto) {
          setTheme(e.matches ? 'dark' : 'light')
        }
      }
      try {
        media.addEventListener('change', handler)
      } catch {
        // Safari antigo
        media.addListener(handler)
      }
    }
  })

  return { theme, isDark, setTheme, toggleTheme }
}