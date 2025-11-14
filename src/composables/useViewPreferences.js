import { ref, onMounted } from 'vue'

export function useViewPreferences(scope = 'default') {
  const storageKey = `view-prefs:${scope}`
  const viewMode = ref('grid')

  const load = () => {
    try {
      const raw = localStorage.getItem(storageKey)
      if (raw) {
        const obj = JSON.parse(raw)
        if (obj && typeof obj.viewMode === 'string') {
          viewMode.value = obj.viewMode === 'list' ? 'list' : 'grid'
        }
      }
    } catch {}
  }

  const save = () => {
    try {
      localStorage.setItem(storageKey, JSON.stringify({ viewMode: viewMode.value }))
    } catch {}
  }

  const setViewMode = (mode) => {
    viewMode.value = mode === 'list' ? 'list' : 'grid'
    save()
  }

  onMounted(load)

  return { viewMode, setViewMode, load, save }
}