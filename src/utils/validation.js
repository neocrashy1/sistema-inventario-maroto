// Utilitários simples de validação
export function required(value) {
  return value !== null && value !== undefined && String(value).trim() !== ''
}

export function isNumber(value) {
  if (value === null || value === undefined || value === '') return false
  return !isNaN(Number(String(value).replace(/\./g, '').replace(',', '.')))
}

export function minLength(value, length) {
  if (value === null || value === undefined) return false
  return String(value).trim().length >= length
}
