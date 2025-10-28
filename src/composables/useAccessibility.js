import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Composable para gerenciar funcionalidades de acessibilidade
 */
export function useAccessibility() {
  const isHighContrast = ref(false)
  const isReducedMotion = ref(false)
  const fontSize = ref('normal')
  const announcements = ref([])

  // Detectar preferências do sistema
  const detectSystemPreferences = () => {
    // Detectar preferência por alto contraste
    if (window.matchMedia) {
      const highContrastQuery = window.matchMedia('(prefers-contrast: high)')
      isHighContrast.value = highContrastQuery.matches
      
      highContrastQuery.addEventListener('change', (e) => {
        isHighContrast.value = e.matches
        applyHighContrast(e.matches)
      })

      // Detectar preferência por movimento reduzido
      const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
      isReducedMotion.value = reducedMotionQuery.matches
      
      reducedMotionQuery.addEventListener('change', (e) => {
        isReducedMotion.value = e.matches
        applyReducedMotion(e.matches)
      })
    }
  }

  // Aplicar alto contraste
  const applyHighContrast = (enable) => {
    const root = document.documentElement
    if (enable) {
      root.classList.add('high-contrast')
    } else {
      root.classList.remove('high-contrast')
    }
  }

  // Aplicar movimento reduzido
  const applyReducedMotion = (enable) => {
    const root = document.documentElement
    if (enable) {
      root.classList.add('reduced-motion')
    } else {
      root.classList.remove('reduced-motion')
    }
  }

  // Alterar tamanho da fonte
  const changeFontSize = (size) => {
    fontSize.value = size
    const root = document.documentElement
    
    // Remove classes anteriores
    root.classList.remove('font-small', 'font-normal', 'font-large', 'font-extra-large')
    
    // Adiciona nova classe
    if (size !== 'normal') {
      root.classList.add(`font-${size}`)
    }
    
    // Salva preferência
    localStorage.setItem('accessibility-font-size', size)
  }

  // Anunciar para leitores de tela
  const announce = (message, priority = 'polite') => {
    const announcement = {
      id: Date.now(),
      message,
      priority,
      timestamp: new Date()
    }
    
    announcements.value.push(announcement)
    
    // Criar elemento para anúncio
    const announcer = document.createElement('div')
    announcer.setAttribute('aria-live', priority)
    announcer.setAttribute('aria-atomic', 'true')
    announcer.className = 'sr-only'
    announcer.textContent = message
    
    document.body.appendChild(announcer)
    
    // Remove após 5 segundos
    setTimeout(() => {
      if (document.body.contains(announcer)) {
        document.body.removeChild(announcer)
      }
      announcements.value = announcements.value.filter(a => a.id !== announcement.id)
    }, 5000)
  }

  // Focar elemento com segurança
  const focusElement = (selector, options = {}) => {
    const element = typeof selector === 'string' 
      ? document.querySelector(selector) 
      : selector
    
    if (element && typeof element.focus === 'function') {
      // Aguarda próximo tick para garantir que o elemento está visível
      setTimeout(() => {
        element.focus(options)
        
        if (options.announce) {
          announce(`Foco movido para ${options.announce}`)
        }
      }, 0)
    }
  }

  // Gerenciar foco em modais
  const trapFocus = (container) => {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    
    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]
    
    const handleTabKey = (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement.focus()
            e.preventDefault()
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement.focus()
            e.preventDefault()
          }
        }
      }
      
      if (e.key === 'Escape') {
        // Emitir evento personalizado para fechar modal
        container.dispatchEvent(new CustomEvent('escape-pressed'))
      }
    }
    
    container.addEventListener('keydown', handleTabKey)
    
    // Focar primeiro elemento
    if (firstElement) {
      firstElement.focus()
    }
    
    // Retornar função de limpeza
    return () => {
      container.removeEventListener('keydown', handleTabKey)
    }
  }

  // Verificar se elemento está visível
  const isElementVisible = (element) => {
    const rect = element.getBoundingClientRect()
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    )
  }

  // Rolar para elemento com suavidade
  const scrollToElement = (selector, options = {}) => {
    const element = typeof selector === 'string' 
      ? document.querySelector(selector) 
      : selector
    
    if (element) {
      const behavior = isReducedMotion.value ? 'auto' : 'smooth'
      
      element.scrollIntoView({
        behavior,
        block: options.block || 'center',
        inline: options.inline || 'nearest'
      })
      
      if (options.focus) {
        setTimeout(() => {
          focusElement(element, { announce: options.announce })
        }, behavior === 'smooth' ? 500 : 0)
      }
    }
  }

  // Carregar preferências salvas
  const loadSavedPreferences = () => {
    const savedFontSize = localStorage.getItem('accessibility-font-size')
    if (savedFontSize) {
      changeFontSize(savedFontSize)
    }
    
    const savedHighContrast = localStorage.getItem('accessibility-high-contrast')
    if (savedHighContrast === 'true') {
      isHighContrast.value = true
      applyHighContrast(true)
    }
  }

  // Salvar preferências
  const savePreferences = () => {
    localStorage.setItem('accessibility-font-size', fontSize.value)
    localStorage.setItem('accessibility-high-contrast', isHighContrast.value.toString())
  }

  // Alternar alto contraste
  const toggleHighContrast = () => {
    isHighContrast.value = !isHighContrast.value
    applyHighContrast(isHighContrast.value)
    savePreferences()
    announce(
      isHighContrast.value 
        ? 'Alto contraste ativado' 
        : 'Alto contraste desativado'
    )
  }

  // Atalhos de teclado
  const setupKeyboardShortcuts = () => {
    const handleKeydown = (e) => {
      // Alt + H: Alternar alto contraste
      if (e.altKey && e.key === 'h') {
        e.preventDefault()
        toggleHighContrast()
      }
      
      // Alt + +: Aumentar fonte
      if (e.altKey && e.key === '+') {
        e.preventDefault()
        const sizes = ['small', 'normal', 'large', 'extra-large']
        const currentIndex = sizes.indexOf(fontSize.value)
        if (currentIndex < sizes.length - 1) {
          changeFontSize(sizes[currentIndex + 1])
          announce(`Tamanho da fonte alterado para ${sizes[currentIndex + 1]}`)
        }
      }
      
      // Alt + -: Diminuir fonte
      if (e.altKey && e.key === '-') {
        e.preventDefault()
        const sizes = ['small', 'normal', 'large', 'extra-large']
        const currentIndex = sizes.indexOf(fontSize.value)
        if (currentIndex > 0) {
          changeFontSize(sizes[currentIndex - 1])
          announce(`Tamanho da fonte alterado para ${sizes[currentIndex - 1]}`)
        }
      }
    }
    
    document.addEventListener('keydown', handleKeydown)
    
    return () => {
      document.removeEventListener('keydown', handleKeydown)
    }
  }

  // Inicialização
  onMounted(() => {
    detectSystemPreferences()
    loadSavedPreferences()
    const cleanupShortcuts = setupKeyboardShortcuts()
    
    // Cleanup na desmontagem
    onUnmounted(() => {
      cleanupShortcuts()
    })
  })

  return {
    // Estado
    isHighContrast,
    isReducedMotion,
    fontSize,
    announcements,
    
    // Métodos
    announce,
    focusElement,
    trapFocus,
    scrollToElement,
    changeFontSize,
    toggleHighContrast,
    isElementVisible,
    savePreferences,
    loadSavedPreferences
  }
}