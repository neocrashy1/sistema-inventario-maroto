/**
 * Validações para formulários
 */

import { isValidDate, isDateInPast, isDateInFuture } from './dateUtils.js';
import { validateWarrantyDates, WARRANTY_TYPES } from './warrantyUtils.js';

/**
 * Regras de validação para campos obrigatórios
 */
export const required = (value) => {
  if (value === null || value === undefined || value === '') {
    return 'Este campo é obrigatório';
  }
  return true;
};

/**
 * Validação para email
 */
export const email = (value) => {
  if (!value) return true; // Campo opcional
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(value)) {
    return 'Email inválido';
  }
  return true;
};

/**
 * Validação para datas
 */
export const validDate = (value) => {
  if (!value) return true; // Campo opcional
  
  if (!isValidDate(value)) {
    return 'Data inválida';
  }
  return true;
};

/**
 * Validação para data não pode ser no passado
 */
export const notPastDate = (value) => {
  if (!value) return true; // Campo opcional
  
  if (!isValidDate(value)) {
    return 'Data inválida';
  }
  
  if (isDateInPast(value)) {
    return 'Data não pode ser no passado';
  }
  return true;
};

/**
 * Validação para data não pode ser no futuro
 */
export const notFutureDate = (value) => {
  if (!value) return true; // Campo opcional
  
  if (!isValidDate(value)) {
    return 'Data inválida';
  }
  
  if (isDateInFuture(value)) {
    return 'Data não pode ser no futuro';
  }
  return true;
};

/**
 * Validação para números positivos
 */
export const positiveNumber = (value) => {
  if (!value) return true; // Campo opcional
  
  const num = parseFloat(value);
  if (isNaN(num) || num <= 0) {
    return 'Deve ser um número positivo';
  }
  return true;
};

/**
 * Validação para números inteiros
 */
export const integer = (value) => {
  if (!value) return true; // Campo opcional
  
  const num = parseInt(value);
  if (isNaN(num) || !Number.isInteger(num)) {
    return 'Deve ser um número inteiro';
  }
  return true;
};

/**
 * Validação para comprimento mínimo
 */
export const minLength = (min) => (value) => {
  if (!value) return true; // Campo opcional
  
  if (value.length < min) {
    return `Deve ter pelo menos ${min} caracteres`;
  }
  return true;
};

/**
 * Validação para comprimento máximo
 */
export const maxLength = (max) => (value) => {
  if (!value) return true; // Campo opcional
  
  if (value.length > max) {
    return `Deve ter no máximo ${max} caracteres`;
  }
  return true;
};

/**
 * Validações específicas para garantia
 */
export const warrantyValidations = {
  /**
   * Valida se o tipo de garantia é válido
   */
  validType: (value) => {
    if (!value) return true; // Campo opcional
    
    const validTypes = Object.values(WARRANTY_TYPES);
    if (!validTypes.includes(value)) {
      return 'Tipo de garantia inválido';
    }
    return true;
  },

  /**
   * Valida se a data de início da garantia é válida
   */
  validStartDate: (value) => {
    if (!value) return true; // Campo opcional
    
    const dateValidation = validDate(value);
    if (dateValidation !== true) return dateValidation;
    
    // Data de início não pode ser muito no futuro (mais de 1 ano)
    const oneYearFromNow = new Date();
    oneYearFromNow.setFullYear(oneYearFromNow.getFullYear() + 1);
    
    if (new Date(value) > oneYearFromNow) {
      return 'Data de início não pode ser mais de 1 ano no futuro';
    }
    
    return true;
  },

  /**
   * Valida se a data de término da garantia é válida
   */
  validEndDate: (value) => {
    if (!value) return true; // Campo opcional
    
    const dateValidation = validDate(value);
    if (dateValidation !== true) return dateValidation;
    
    return true;
  },

  /**
   * Valida se as datas de garantia são consistentes
   */
  consistentDates: (startDate, endDate) => {
    if (!startDate || !endDate) return true; // Campos opcionais
    
    const validation = validateWarrantyDates(startDate, endDate);
    if (!validation.isValid) {
      return validation.errors.join(', ');
    }
    
    return true;
  },

  /**
   * Valida se o fornecedor da garantia é válido
   */
  validProvider: (value) => {
    if (!value) return true; // Campo opcional
    
    const minLengthValidation = minLength(2)(value);
    if (minLengthValidation !== true) return minLengthValidation;
    
    const maxLengthValidation = maxLength(100)(value);
    if (maxLengthValidation !== true) return maxLengthValidation;
    
    return true;
  }
};

/**
 * Validações específicas para ativos
 */
export const assetValidations = {
  /**
   * Valida código do ativo
   */
  validCode: (value) => {
    if (!value) return 'Código do ativo é obrigatório';
    
    // Código deve ter entre 3 e 20 caracteres alfanuméricos
    const codeRegex = /^[A-Za-z0-9-_]{3,20}$/;
    if (!codeRegex.test(value)) {
      return 'Código deve ter entre 3 e 20 caracteres alfanuméricos, hífens ou underscores';
    }
    
    return true;
  },

  /**
   * Valida nome do ativo
   */
  validName: (value) => {
    if (!value) return 'Nome do ativo é obrigatório';
    
    const minLengthValidation = minLength(2)(value);
    if (minLengthValidation !== true) return minLengthValidation;
    
    const maxLengthValidation = maxLength(100)(value);
    if (maxLengthValidation !== true) return maxLengthValidation;
    
    return true;
  },

  /**
   * Valida número de série
   */
  validSerialNumber: (value) => {
    if (!value) return true; // Campo opcional
    
    const minLengthValidation = minLength(3)(value);
    if (minLengthValidation !== true) return minLengthValidation;
    
    const maxLengthValidation = maxLength(50)(value);
    if (maxLengthValidation !== true) return maxLengthValidation;
    
    return true;
  },

  /**
   * Valida valor do ativo
   */
  validValue: (value) => {
    if (!value) return true; // Campo opcional
    
    const positiveValidation = positiveNumber(value);
    if (positiveValidation !== true) return positiveValidation;
    
    // Valor não pode ser maior que 1 milhão
    if (parseFloat(value) > 1000000) {
      return 'Valor não pode ser maior que R$ 1.000.000,00';
    }
    
    return true;
  },

  /**
   * Valida data de aquisição
   */
  validAcquisitionDate: (value) => {
    if (!value) return true; // Campo opcional
    
    const dateValidation = validDate(value);
    if (dateValidation !== true) return dateValidation;
    
    // Data de aquisição não pode ser no futuro
    const futureValidation = notFutureDate(value);
    if (futureValidation !== true) return futureValidation;
    
    // Data de aquisição não pode ser muito antiga (mais de 50 anos)
    const fiftyYearsAgo = new Date();
    fiftyYearsAgo.setFullYear(fiftyYearsAgo.getFullYear() - 50);
    
    if (new Date(value) < fiftyYearsAgo) {
      return 'Data de aquisição não pode ser mais de 50 anos atrás';
    }
    
    return true;
  }
};

/**
 * Função para executar múltiplas validações
 */
export function validateField(value, validations) {
  for (const validation of validations) {
    const result = validation(value);
    if (result !== true) {
      return result;
    }
  }
  return true;
}

/**
 * Função para validar um objeto completo
 */
export function validateObject(obj, validationRules) {
  const errors = {};
  
  for (const [field, rules] of Object.entries(validationRules)) {
    const value = obj[field];
    const result = validateField(value, rules);
    
    if (result !== true) {
      errors[field] = result;
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}