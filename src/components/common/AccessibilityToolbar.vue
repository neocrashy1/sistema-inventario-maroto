<template>
  <div 
    class="accessibility-toolbar"
    role="toolbar"
    aria-label="Controles de acessibilidade"
    :class="{ 'toolbar-expanded': isExpanded }"
  >
    <!-- Toggle Button -->
    <button
      class="toolbar-toggle"
      @click="toggleToolbar"
      :aria-expanded="isExpanded"
      aria-controls="accessibility-controls"
      aria-label="Abrir controles de acessibilidade"
      title="Controles de acessibilidade (Alt + A)"
    >
      <i class="fas fa-universal-access" aria-hidden="true"></i>
      <span class="sr-only">Acessibilidade</span>
    </button>

    <!-- Controls Panel -->
    <div 
      id="accessibility-controls"
      class="toolbar-controls"
      :class="{ 'controls-visible': isExpanded }"
      role="group"
      aria-labelledby="toolbar-title"
    >
      <h3 id="toolbar-title" class="toolbar-title">
        Opções de Acessibilidade
      </h3>

      <!-- Font Size Controls -->
      <div class="control-group" role="group" aria-labelledby="font-size-label">
        <label id="font-size-label" class="control-label">
          Tamanho da Fonte
        </label>
        <div class="button-group">
          <button
            class="control-btn"
            @click="decreaseFontSize"
            :disabled="fontSize === 'small'"
            aria-label="Diminuir tamanho da fonte"
            title="Diminuir fonte (Alt + -)"
          >
            <i class="fas fa-minus" aria-hidden="true"></i>
            A-
          </button>
          <span class="font-size-indicator" aria-live="polite">
            {{ fontSizeLabel }}
          </span>
          <button
            class="control-btn"
            @click="increaseFontSize"
            :disabled="fontSize === 'extra-large'"
            aria-label="Aumentar tamanho da fonte"
            title="Aumentar fonte (Alt + +)"
          >
            <i class="fas fa-plus" aria-hidden="true"></i>
            A+
          </button>
        </div>
      </div>

      <!-- High Contrast Toggle -->
      <div class="control-group">
        <button
          class="control-btn toggle-btn"
          @click="toggleHighContrast"
          :class="{ 'active': isHighContrast }"
          :aria-pressed="isHighContrast"
          aria-label="Alternar alto contraste"
          title="Alto contraste (Alt + H)"
        >
          <i class="fas fa-adjust" aria-hidden="true"></i>
          Alto Contraste
        </button>
      </div>

      <!-- Theme Toggle -->
      <div class="control-group">
        <button
          class="control-btn toggle-btn"
          @click="toggleTheme"
          :class="{ 'active': isDark }"
          :aria-pressed="isDark"
          aria-label="Alternar tema claro/escuro"
          title="Tema (Alt + T)"
        >
          <i class="fas" :class="isDark ? 'fa-moon' : 'fa-sun'" aria-hidden="true"></i>
          Tema {{ isDark ? 'Escuro' : 'Claro' }}
        </button>
      </div>

      <!-- Keyboard Navigation Help -->
      <div class="control-group">
        <button
          class="control-btn"
          @click="showKeyboardHelp"
          aria-label="Mostrar ajuda de navegação por teclado"
        >
          <i class="fas fa-keyboard" aria-hidden="true"></i>
          Atalhos do Teclado
        </button>
      </div>

      <!-- Reset Button -->
      <div class="control-group">
        <button
          class="control-btn reset-btn"
          @click="resetSettings"
          aria-label="Restaurar configurações padrão"
        >
          <i class="fas fa-undo" aria-hidden="true"></i>
          Restaurar Padrão
        </button>
      </div>

      <!-- Close Button -->
      <button
        class="close-btn"
        @click="closeToolbar"
        aria-label="Fechar controles de acessibilidade"
      >
        <i class="fas fa-times" aria-hidden="true"></i>
      </button>
    </div>

    <!-- Keyboard Help Modal -->
    <div
      v-if="showingKeyboardHelp"
      class="modal-overlay"
      @click="hideKeyboardHelp"
      role="dialog"
      aria-labelledby="keyboard-help-title"
      aria-modal="true"
    >
      <div class="modal-content" @click.stop>
        <header class="modal-header">
          <h2 id="keyboard-help-title">Atalhos do Teclado</h2>
          <button
            class="modal-close"
            @click="hideKeyboardHelp"
            aria-label="Fechar ajuda"
          >
            <i class="fas fa-times" aria-hidden="true"></i>
          </button>
        </header>
        
        <div class="modal-body">
          <div class="shortcut-section">
            <h3>Acessibilidade</h3>
            <ul class="shortcut-list">
              <li>
                <kbd>Alt + A</kbd>
                <span>Abrir/fechar controles de acessibilidade</span>
              </li>
              <li>
                <kbd>Alt + H</kbd>
                <span>Alternar alto contraste</span>
              </li>
              <li>
                <kbd>Alt + +</kbd>
                <span>Aumentar tamanho da fonte</span>
              </li>
              <li>
                <kbd>Alt + -</kbd>
                <span>Diminuir tamanho da fonte</span>
              </li>
            </ul>
          </div>

          <div class="shortcut-section">
            <h3>Navegação</h3>
            <ul class="shortcut-list">
              <li>
                <kbd>Tab</kbd>
                <span>Navegar para próximo elemento</span>
              </li>
              <li>
                <kbd>Shift + Tab</kbd>
                <span>Navegar para elemento anterior</span>
              </li>
              <li>
                <kbd>Enter</kbd>
                <span>Ativar botão ou link</span>
              </li>
              <li>
                <kbd>Espaço</kbd>
                <span>Ativar botão ou checkbox</span>
              </li>
              <li>
                <kbd>Escape</kbd>
                <span>Fechar modal ou menu</span>
              </li>
            </ul>
          </div>

          <div class="shortcut-section">
            <h3>Formulários</h3>
            <ul class="shortcut-list">
              <li>
                <kbd>↑ ↓</kbd>
                <span>Navegar em listas e selects</span>
              </li>
              <li>
                <kbd>Home</kbd>
                <span>Ir para o início</span>
              </li>
              <li>
                <kbd>End</kbd>
                <span>Ir para o final</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAccessibility } from '@/composables/useAccessibility'
import { useTheme } from '@/composables/useTheme'

export default {
  name: 'AccessibilityToolbar',
  setup() {
    const {
      isHighContrast,
      fontSize,
      toggleHighContrast,
      changeFontSize,
      announce,
      trapFocus
    } = useAccessibility()

    const themeState = useTheme()
    // Expose a stable computed ref to avoid "property was accessed during render but is not defined"
    const isDarkLocal = computed(() => {
      try {
        return themeState.isDark?.value ?? false
      } catch {
        return false
      }
    })
    const toggleTheme = themeState.toggleTheme

    const isExpanded = ref(false)
    const showingKeyboardHelp = ref(false)

    const fontSizeLabel = computed(() => {
      const labels = {
        'small': 'Pequeno',
        'normal': 'Normal',
        'large': 'Grande',
        'extra-large': 'Extra Grande'
      }
      return labels[fontSize.value] || 'Normal'
    })

    const toggleToolbar = () => {
      isExpanded.value = !isExpanded.value
      
      if (isExpanded.value) {
        announce('Controles de acessibilidade abertos')
        // Focar primeiro controle
        setTimeout(() => {
          const firstControl = document.querySelector('.toolbar-controls button')
          if (firstControl) {
            firstControl.focus()
          }
        }, 100)
      } else {
        announce('Controles de acessibilidade fechados')
      }
    }

    const closeToolbar = () => {
      isExpanded.value = false
      announce('Controles de acessibilidade fechados')
      
      // Retornar foco para o botão toggle
      setTimeout(() => {
        const toggleBtn = document.querySelector('.toolbar-toggle')
        if (toggleBtn) {
          toggleBtn.focus()
        }
      }, 100)
    }

    const increaseFontSize = () => {
      const sizes = ['small', 'normal', 'large', 'extra-large']
      const currentIndex = sizes.indexOf(fontSize.value)
      if (currentIndex < sizes.length - 1) {
        const newSize = sizes[currentIndex + 1]
        changeFontSize(newSize)
        announce(`Tamanho da fonte alterado para ${fontSizeLabel.value}`)
      }
    }

    const decreaseFontSize = () => {
      const sizes = ['small', 'normal', 'large', 'extra-large']
      const currentIndex = sizes.indexOf(fontSize.value)
      if (currentIndex > 0) {
        const newSize = sizes[currentIndex - 1]
        changeFontSize(newSize)
        announce(`Tamanho da fonte alterado para ${fontSizeLabel.value}`)
      }
    }

    const showKeyboardHelp = () => {
      showingKeyboardHelp.value = true
      announce('Ajuda de atalhos do teclado aberta')
      
      // Configurar trap de foco
      setTimeout(() => {
        const modal = document.querySelector('.modal-content')
        if (modal) {
          trapFocus(modal)
        }
      }, 100)
    }

    const hideKeyboardHelp = () => {
      showingKeyboardHelp.value = false
      announce('Ajuda de atalhos do teclado fechada')
    }

    const resetSettings = () => {
      changeFontSize('normal')
      if (isHighContrast.value) {
        toggleHighContrast()
      }
      announce('Configurações de acessibilidade restauradas para o padrão')
    }

    // Atalhos de teclado
    const handleKeydown = (e) => {
      // Alt + A: Toggle toolbar
      if (e.altKey && e.key.toLowerCase() === 'a') {
        e.preventDefault()
        toggleToolbar()
      }

      // Alt + T: Alternar tema
      if (e.altKey && e.key.toLowerCase() === 't') {
        e.preventDefault()
        toggleTheme()
        announce(`Tema ${isDark.value ? 'escuro' : 'claro'} ativado`)
      }
      
      // Escape: Fechar toolbar ou modal
      if (e.key === 'Escape') {
        if (showingKeyboardHelp.value) {
          hideKeyboardHelp()
        } else if (isExpanded.value) {
          closeToolbar()
        }
      }
    }

    onMounted(() => {
      document.addEventListener('keydown', handleKeydown)
    })

    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown)
    })

    return {
      isExpanded,
      showingKeyboardHelp,
      isHighContrast,
      fontSize,
      fontSizeLabel,
      // return the local computed name to the template
      isDark: isDarkLocal,
      toggleToolbar,
      closeToolbar,
      toggleHighContrast,
      increaseFontSize,
      decreaseFontSize,
      showKeyboardHelp,
      hideKeyboardHelp,
      resetSettings,
      toggleTheme
    }
  }
}
</script>

<style scoped>
.accessibility-toolbar {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
}

.toolbar-toggle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: var(--primary-color);
  color: var(--levitiis-white);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
}

.toolbar-toggle:hover {
  background: var(--primary-dark);
  transform: scale(1.05);
}

.toolbar-toggle:focus {
  outline: 3px solid var(--focus-ring);
  outline-offset: 2px;
}

.toolbar-controls {
  position: absolute;
  top: 60px;
  right: 0;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  min-width: 280px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s ease;
}

.controls-visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.toolbar-title {
  margin: 0 0 16px 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
}

.control-group {
  margin-bottom: 16px;
}

.control-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.button-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 36px;
}

.control-btn:hover:not(:disabled) {
  background: var(--primary-color);
  color: var(--levitiis-white);
  border-color: var(--primary-color);
}

.control-btn:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.reset-btn {
  background: var(--danger-color);
  color: var(--levitiis-white);
  border-color: var(--danger-color);
}

.reset-btn:hover {
  background: var(--danger-color);
  border-color: var(--danger-color);
  filter: brightness(0.95);
}

.font-size-indicator {
  font-size: 0.875rem;
  color: var(--text-secondary);
  min-width: 60px;
  text-align: center;
}

.close-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.close-btn:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 1px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.modal-content {
  background: var(--bg-primary);
  border-radius: 12px;
  max-width: 600px;
  max-height: 80vh;
  overflow: auto;
  margin: 20px;
  box-shadow: var(--shadow-xl);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
}

.shortcut-section {
  margin-bottom: 24px;
}

.shortcut-section h3 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.shortcut-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.shortcut-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.shortcut-list li:last-child {
  border-bottom: none;
}

kbd {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 4px 8px;
  font-family: monospace;
  font-size: 0.875rem;
  color: var(--text-primary);
  min-width: 80px;
  text-align: center;
}

.shortcut-list span {
  color: var(--text-secondary);
  font-size: 0.875rem;
  flex: 1;
  margin-left: 16px;
}

/* Responsive */
@media (max-width: 768px) {
  .accessibility-toolbar {
    top: 10px;
    right: 10px;
  }
  
  .toolbar-controls {
    right: -10px;
    min-width: 260px;
  }
  
  .modal-content {
    margin: 10px;
    max-height: 90vh;
  }
}

/* High contrast mode */
.high-contrast .toolbar-toggle {
  background: #00ffff;
  color: var(--text-primary);
}

.high-contrast .control-btn {
  border-color: #ffffff;
}

.high-contrast .control-btn:hover:not(:disabled) {
  background: #00ffff;
  color: var(--text-primary);
}

/* Reduced motion */
.reduced-motion .toolbar-toggle,
.reduced-motion .toolbar-controls {
  transition: none;
}
</style>