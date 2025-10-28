import { describe, it, expect } from 'vitest'
import useValidation from '../useValidation'

describe('useValidation', () => {
  it('valida asset válido', () => {
    const { validateAsset, validationErrors } = useValidation()
    const validAsset = {
      tag: 'A123',
      name: 'Computador Teste',
      category: 'Informática',
      location: 'Sala 1',
      value: 1500.0
    }

    const ok = validateAsset(validAsset)
    expect(ok).toBe(true)
    expect(validationErrors.tag).toBe('')
    expect(validationErrors.name).toBe('')
  })

  it('detecta campos obrigatórios faltando', () => {
    const { validateAsset, validationErrors } = useValidation()
    const invalidAsset = {
      tag: '',
      name: '',
      category: '',
      location: '',
      value: ''
    }

    const ok = validateAsset(invalidAsset)
    expect(ok).toBe(false)
    expect(validationErrors.tag).toBeTruthy()
    expect(validationErrors.name).toBeTruthy()
    expect(validationErrors.category).toBeTruthy()
    expect(validationErrors.location).toBeTruthy()
    expect(validationErrors.value).toBeTruthy()
  })
})
