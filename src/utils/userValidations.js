import { required, email, minLength, maxLength } from './formValidations.js'

/**
 * Validações específicas para usuários
 */

/**
 * Validação para nome de usuário
 */
export const validUsername = (value) => {
  if (!value) return 'Nome de usuário é obrigatório'
  
  // Username deve ter entre 3 e 30 caracteres
  const minLengthValidation = minLength(3)(value)
  if (minLengthValidation !== true) return minLengthValidation
  
  const maxLengthValidation = maxLength(30)(value)
  if (maxLengthValidation !== true) return maxLengthValidation
  
  // Username deve conter apenas letras, números, pontos, hífens e underscores
  const usernameRegex = /^[a-zA-Z0-9._-]+$/
  if (!usernameRegex.test(value)) {
    return 'Nome de usuário deve conter apenas letras, números, pontos, hífens e underscores'
  }
  
  // Não pode começar ou terminar com ponto, hífen ou underscore
  if (/^[._-]|[._-]$/.test(value)) {
    return 'Nome de usuário não pode começar ou terminar com ponto, hífen ou underscore'
  }
  
  return true
}

/**
 * Validação para nome completo
 */
export const validFullName = (value) => {
  if (!value) return 'Nome completo é obrigatório'
  
  const minLengthValidation = minLength(2)(value)
  if (minLengthValidation !== true) return minLengthValidation
  
  const maxLengthValidation = maxLength(100)(value)
  if (maxLengthValidation !== true) return maxLengthValidation
  
  // Nome deve conter pelo menos um espaço (nome e sobrenome)
  if (!value.includes(' ')) {
    return 'Digite o nome completo (nome e sobrenome)'
  }
  
  // Nome deve conter apenas letras, espaços, acentos e alguns caracteres especiais
  const nameRegex = /^[a-zA-ZÀ-ÿ\s'-]+$/
  if (!nameRegex.test(value)) {
    return 'Nome deve conter apenas letras, espaços e acentos'
  }
  
  return true
}

/**
 * Validação para telefone brasileiro
 */
export const validPhone = (value) => {
  if (!value) return true // Campo opcional
  
  // Remove todos os caracteres não numéricos
  const cleanPhone = value.replace(/\D/g, '')
  
  // Telefone brasileiro deve ter 10 ou 11 dígitos
  if (cleanPhone.length < 10 || cleanPhone.length > 11) {
    return 'Telefone deve ter 10 ou 11 dígitos'
  }
  
  // Validação básica de formato brasileiro
  const phoneRegex = /^(\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}$/
  if (!phoneRegex.test(value)) {
    return 'Formato de telefone inválido. Use: (11) 99999-9999'
  }
  
  return true
}

/**
 * Validação para email corporativo (opcional)
 */
export const validCorporateEmail = (domains = []) => (value) => {
  if (!value) return 'Email é obrigatório'
  
  const emailValidation = email(value)
  if (emailValidation !== true) return emailValidation
  
  // Se domínios específicos foram fornecidos, validar
  if (domains.length > 0) {
    const emailDomain = value.split('@')[1]?.toLowerCase()
    if (!domains.some(domain => emailDomain === domain.toLowerCase())) {
      return `Email deve ser de um dos domínios: ${domains.join(', ')}`
    }
  }
  
  return true
}

/**
 * Validação para senha (quando necessário)
 */
export const validPassword = (value) => {
  if (!value) return 'Senha é obrigatória'
  
  const minLengthValidation = minLength(8)(value)
  if (minLengthValidation !== true) return minLengthValidation
  
  const maxLengthValidation = maxLength(128)(value)
  if (maxLengthValidation !== true) return maxLengthValidation
  
  // Deve conter pelo menos uma letra minúscula
  if (!/[a-z]/.test(value)) {
    return 'Senha deve conter pelo menos uma letra minúscula'
  }
  
  // Deve conter pelo menos uma letra maiúscula
  if (!/[A-Z]/.test(value)) {
    return 'Senha deve conter pelo menos uma letra maiúscula'
  }
  
  // Deve conter pelo menos um número
  if (!/\d/.test(value)) {
    return 'Senha deve conter pelo menos um número'
  }
  
  // Deve conter pelo menos um caractere especial
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(value)) {
    return 'Senha deve conter pelo menos um caractere especial'
  }
  
  return true
}

/**
 * Validação para confirmação de senha
 */
export const validPasswordConfirmation = (originalPassword) => (value) => {
  if (!value) return 'Confirmação de senha é obrigatória'
  
  if (value !== originalPassword) {
    return 'Senhas não coincidem'
  }
  
  return true
}

/**
 * Regras de validação para formulário de usuário
 */
export const userValidationRules = {
  name: [validFullName],
  email: [validCorporateEmail()],
  username: [validUsername],
  phone: [validPhone],
  role: [required],
  department: [required],
  status: [required]
}

/**
 * Regras de validação para formulário de usuário com senha
 */
export const userWithPasswordValidationRules = {
  ...userValidationRules,
  password: [validPassword],
  passwordConfirmation: [validPasswordConfirmation]
}

/**
 * Função para obter regras de validação personalizadas
 */
export function getUserValidationRules(options = {}) {
  const {
    requirePassword = false,
    corporateDomains = [],
    optionalFields = []
  } = options
  
  let rules = { ...userValidationRules }
  
  // Atualizar validação de email se domínios corporativos foram fornecidos
  if (corporateDomains.length > 0) {
    rules.email = [validCorporateEmail(corporateDomains)]
  }
  
  // Adicionar validações de senha se necessário
  if (requirePassword) {
    rules.password = [validPassword]
    rules.passwordConfirmation = [validPasswordConfirmation]
  }
  
  // Remover campos opcionais das validações obrigatórias
  optionalFields.forEach(field => {
    if (rules[field]) {
      rules[field] = rules[field].filter(rule => rule !== required)
    }
  })
  
  return rules
}