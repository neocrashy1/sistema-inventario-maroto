import { reactive } from 'vue'
import { required, isNumber, minLength } from '@/utils/validation'

export default function useValidation() {
  const validationErrors = reactive({
    tag: '',
    name: '',
    category: '',
    location: '',
    value: ''
  })

  function clearErrors() {
    validationErrors.tag = ''
    validationErrors.name = ''
    validationErrors.category = ''
    validationErrors.location = ''
    validationErrors.value = ''
  }

  function validateAsset(asset) {
    clearErrors()

    if (!required(asset.tag)) {
      validationErrors.tag = 'Código é obrigatório.'
    } else if (!minLength(asset.tag, 2)) {
      validationErrors.tag = 'Código muito curto.'
    }

    if (!required(asset.name)) {
      validationErrors.name = 'Nome é obrigatório.'
    } else if (!minLength(asset.name, 2)) {
      validationErrors.name = 'Nome muito curto.'
    }

    if (!required(asset.category)) {
      validationErrors.category = 'Categoria é obrigatória.'
    }

    if (!required(asset.location)) {
      validationErrors.location = 'Localização é obrigatória.'
    }

    if (!required(asset.value) || !isNumber(asset.value)) {
      validationErrors.value = 'Valor inválido.'
    }

    // Return true only if no errors
    return !validationErrors.tag && !validationErrors.name && !validationErrors.category && !validationErrors.location && !validationErrors.value
  }

  return { validationErrors, validateAsset, clearErrors }
}
