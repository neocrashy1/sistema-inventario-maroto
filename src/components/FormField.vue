<template>
  <div class="form-field" :class="fieldClasses">
    <label v-if="label" :for="fieldId" class="form-label">
      {{ label }}
      <span v-if="required" class="required-indicator">*</span>
    </label>
    
    <div class="form-input-container">
      <!-- Input padrão -->
      <input
        v-if="type !== 'textarea' && type !== 'select'"
        :id="fieldId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />
      
      <!-- Textarea -->
      <textarea
        v-else-if="type === 'textarea'"
        :id="fieldId"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :rows="rows"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      ></textarea>
      
      <!-- Select -->
      <select
        v-else-if="type === 'select'"
        :id="fieldId"
        :value="modelValue"
        :disabled="disabled"
        :class="inputClasses"
        @change="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      >
        <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
        <option
          v-for="option in options"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>
      
      <!-- Ícones de status -->
      <div v-if="showStatusIcon" class="status-icon">
        <i v-if="isValid" class="fas fa-check-circle text-success"></i>
        <i v-else-if="hasError" class="fas fa-exclamation-circle text-error"></i>
      </div>
    </div>
    
    <!-- Mensagem de erro -->
    <div v-if="hasError && showError" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      {{ errorMessage }}
    </div>
    
    <!-- Mensagem de ajuda -->
    <div v-if="helpText && !hasError" class="help-text">
      {{ helpText }}
    </div>
  </div>
</template>

<script>
import { computed, ref } from 'vue'

export default {
  name: 'FormField',
  props: {
    modelValue: {
      type: [String, Number, Boolean],
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'text'
    },
    placeholder: {
      type: String,
      default: ''
    },
    required: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    readonly: {
      type: Boolean,
      default: false
    },
    errorMessage: {
      type: String,
      default: ''
    },
    helpText: {
      type: String,
      default: ''
    },
    showStatusIcon: {
      type: Boolean,
      default: true
    },
    showError: {
      type: Boolean,
      default: true
    },
    touched: {
      type: Boolean,
      default: false
    },
    rows: {
      type: Number,
      default: 3
    },
    options: {
      type: Array,
      default: () => []
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    }
  },
  emits: ['update:modelValue', 'blur', 'focus'],
  setup(props, { emit }) {
    const isFocused = ref(false)
    
    // ID único para o campo
    const fieldId = computed(() => {
      return `field-${Math.random().toString(36).substr(2, 9)}`
    })
    
    // Estado de validação
    const hasError = computed(() => {
      return props.touched && !!props.errorMessage
    })
    
    const isValid = computed(() => {
      return props.touched && !props.errorMessage
    })
    
    // Classes do campo
    const fieldClasses = computed(() => {
      return {
        'form-field--error': hasError.value,
        'form-field--valid': isValid.value,
        'form-field--focused': isFocused.value,
        'form-field--disabled': props.disabled,
        'form-field--readonly': props.readonly,
        [`form-field--${props.size}`]: true
      }
    })
    
    // Classes do input
    const inputClasses = computed(() => {
      return {
        'form-input': true,
        'form-input--error': hasError.value,
        'form-input--valid': isValid.value,
        'form-input--focused': isFocused.value,
        'form-input--disabled': props.disabled,
        'form-input--readonly': props.readonly,
        [`form-input--${props.size}`]: true
      }
    })
    
    // Handlers de eventos
    const handleInput = (event) => {
      const value = event.target.value
      emit('update:modelValue', value)
    }
    
    const handleBlur = (event) => {
      isFocused.value = false
      emit('blur', event)
    }
    
    const handleFocus = (event) => {
      isFocused.value = true
      emit('focus', event)
    }
    
    return {
      fieldId,
      hasError,
      isValid,
      fieldClasses,
      inputClasses,
      handleInput,
      handleBlur,
      handleFocus
    }
  }
}
</script>

<style scoped>
.form-field {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.required-indicator {
  color: #ef4444;
  margin-left: 2px;
}

.form-input-container {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input--error {
  border-color: #ef4444;
  background-color: #fef2f2;
}

.form-input--error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-input--valid {
  border-color: #10b981;
  background-color: #f0fdf4;
}

.form-input--valid:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-input--disabled {
  background-color: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
}

.form-input--readonly {
  background-color: #f9fafb;
  cursor: default;
}

.form-input--small {
  padding: 8px 12px;
  font-size: 12px;
}

.form-input--large {
  padding: 16px 20px;
  font-size: 16px;
}

.status-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.text-success {
  color: #10b981;
}

.text-error {
  color: #ef4444;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  font-size: 12px;
  color: #ef4444;
}

.help-text {
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
}

.form-field--error .form-label {
  color: #ef4444;
}

.form-field--valid .form-label {
  color: #10b981;
}

.form-field--disabled .form-label {
  color: #9ca3af;
}

/* Animações */
.form-input {
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.error-message,
.help-text {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsividade */
@media (max-width: 768px) {
  .form-input {
    padding: 10px 14px;
    font-size: 16px; /* Evita zoom no iOS */
  }
  
  .form-input--small {
    padding: 8px 12px;
    font-size: 14px;
  }
  
  .form-input--large {
    padding: 14px 18px;
    font-size: 16px;
  }
}
</style>