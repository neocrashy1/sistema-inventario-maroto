/**
 * Utilitários para validação e cálculo de garantias
 */

import { isValidDate, isDateInPast, daysDifference } from './dateUtils.js';

/**
 * Status possíveis de garantia
 */
export const WARRANTY_STATUS = {
  ACTIVE: 'active',
  EXPIRING: 'expiring',
  EXPIRED: 'expired',
  NONE: 'none'
};

/**
 * Tipos de garantia
 */
export const WARRANTY_TYPES = {
  MANUFACTURER: 'manufacturer',
  EXTENDED: 'extended',
  ON_SITE: 'on_site',
  NEXT_BUSINESS_DAY: 'next_business_day',
  SAME_DAY: 'same_day'
};

/**
 * Calcula o status da garantia baseado na data de término
 * @param {string|Date} endDate - Data de término da garantia
 * @param {number} warningDays - Dias antes do vencimento para considerar "expirando" (padrão: 30)
 * @returns {string} Status da garantia (active, expiring, expired, none)
 */
export function getWarrantyStatus(endDate, warningDays = 30) {
  if (!endDate || !isValidDate(endDate)) {
    return WARRANTY_STATUS.NONE;
  }
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const endDateObj = typeof endDate === 'string' ? new Date(endDate) : endDate;
  endDateObj.setHours(0, 0, 0, 0);
  
  // Garantia expirada
  if (endDateObj < today) {
    return WARRANTY_STATUS.EXPIRED;
  }
  
  // Garantia expirando em breve
  const daysUntilExpiry = daysDifference(endDateObj, today);
  if (daysUntilExpiry <= warningDays) {
    return WARRANTY_STATUS.EXPIRING;
  }
  
  // Garantia ativa
  return WARRANTY_STATUS.ACTIVE;
}

/**
 * Calcula quantos dias restam até o vencimento da garantia
 * @param {string|Date} endDate - Data de término da garantia
 * @returns {number} Dias restantes (negativo se expirada)
 */
export function getDaysUntilExpiry(endDate) {
  if (!endDate || !isValidDate(endDate)) {
    return 0;
  }
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const endDateObj = typeof endDate === 'string' ? new Date(endDate) : endDate;
  endDateObj.setHours(0, 0, 0, 0);
  
  return daysDifference(endDateObj, today);
}

/**
 * Verifica se a garantia está ativa
 * @param {string|Date} endDate - Data de término da garantia
 * @returns {boolean} True se a garantia estiver ativa
 */
export function isWarrantyActive(endDate) {
  const status = getWarrantyStatus(endDate);
  return status === WARRANTY_STATUS.ACTIVE || status === WARRANTY_STATUS.EXPIRING;
}

/**
 * Verifica se a garantia está expirada
 * @param {string|Date} endDate - Data de término da garantia
 * @returns {boolean} True se a garantia estiver expirada
 */
export function isWarrantyExpired(endDate) {
  return getWarrantyStatus(endDate) === WARRANTY_STATUS.EXPIRED;
}

/**
 * Verifica se a garantia está expirando em breve
 * @param {string|Date} endDate - Data de término da garantia
 * @param {number} warningDays - Dias antes do vencimento para considerar "expirando"
 * @returns {boolean} True se a garantia estiver expirando
 */
export function isWarrantyExpiring(endDate, warningDays = 30) {
  return getWarrantyStatus(endDate, warningDays) === WARRANTY_STATUS.EXPIRING;
}

/**
 * Valida se as datas de garantia são consistentes
 * @param {string|Date} startDate - Data de início da garantia
 * @param {string|Date} endDate - Data de término da garantia
 * @returns {object} Objeto com resultado da validação e mensagens de erro
 */
export function validateWarrantyDates(startDate, endDate) {
  const result = {
    isValid: true,
    errors: []
  };
  
  // Verifica se as datas são válidas
  if (startDate && !isValidDate(startDate)) {
    result.isValid = false;
    result.errors.push('Data de início da garantia é inválida');
  }
  
  if (endDate && !isValidDate(endDate)) {
    result.isValid = false;
    result.errors.push('Data de término da garantia é inválida');
  }
  
  // Se ambas as datas são válidas, verifica a consistência
  if (startDate && endDate && isValidDate(startDate) && isValidDate(endDate)) {
    const startDateObj = typeof startDate === 'string' ? new Date(startDate) : startDate;
    const endDateObj = typeof endDate === 'string' ? new Date(endDate) : endDate;
    
    if (endDateObj <= startDateObj) {
      result.isValid = false;
      result.errors.push('Data de término deve ser posterior à data de início');
    }
  }
  
  return result;
}

/**
 * Calcula a duração da garantia em meses
 * @param {string|Date} startDate - Data de início da garantia
 * @param {string|Date} endDate - Data de término da garantia
 * @returns {number} Duração em meses (0 se datas inválidas)
 */
export function getWarrantyDurationInMonths(startDate, endDate) {
  if (!isValidDate(startDate) || !isValidDate(endDate)) {
    return 0;
  }
  
  const startDateObj = typeof startDate === 'string' ? new Date(startDate) : startDate;
  const endDateObj = typeof endDate === 'string' ? new Date(endDate) : endDate;
  
  const yearDiff = endDateObj.getFullYear() - startDateObj.getFullYear();
  const monthDiff = endDateObj.getMonth() - startDateObj.getMonth();
  
  return yearDiff * 12 + monthDiff;
}

/**
 * Formata o status da garantia para exibição
 * @param {string} status - Status da garantia
 * @returns {string} Status formatado para exibição
 */
export function formatWarrantyStatus(status) {
  const statusMap = {
    [WARRANTY_STATUS.ACTIVE]: 'Ativa',
    [WARRANTY_STATUS.EXPIRING]: 'Expirando',
    [WARRANTY_STATUS.EXPIRED]: 'Expirada',
    [WARRANTY_STATUS.NONE]: 'Sem Garantia'
  };
  
  return statusMap[status] || 'Desconhecido';
}

/**
 * Formata o tipo de garantia para exibição
 * @param {string} type - Tipo da garantia
 * @returns {string} Tipo formatado para exibição
 */
export function formatWarrantyType(type) {
  const typeMap = {
    [WARRANTY_TYPES.MANUFACTURER]: 'Fabricante',
    [WARRANTY_TYPES.EXTENDED]: 'Estendida',
    [WARRANTY_TYPES.ON_SITE]: 'On-Site',
    [WARRANTY_TYPES.NEXT_BUSINESS_DAY]: 'Próximo Dia Útil',
    [WARRANTY_TYPES.SAME_DAY]: 'Mesmo Dia'
  };
  
  return typeMap[type] || type;
}

/**
 * Gera uma mensagem descritiva sobre o status da garantia
 * @param {string|Date} endDate - Data de término da garantia
 * @param {number} warningDays - Dias antes do vencimento para considerar "expirando"
 * @returns {string} Mensagem descritiva
 */
export function getWarrantyStatusMessage(endDate, warningDays = 30) {
  const status = getWarrantyStatus(endDate, warningDays);
  const daysUntilExpiry = getDaysUntilExpiry(endDate);
  
  switch (status) {
    case WARRANTY_STATUS.ACTIVE:
      return `Garantia ativa por mais ${daysUntilExpiry} dias`;
    case WARRANTY_STATUS.EXPIRING:
      return `Garantia expira em ${daysUntilExpiry} dias`;
    case WARRANTY_STATUS.EXPIRED:
      return `Garantia expirada há ${Math.abs(daysUntilExpiry)} dias`;
    case WARRANTY_STATUS.NONE:
      return 'Sem informações de garantia';
    default:
      return 'Status desconhecido';
  }
}