/**
import logger from '@/utils/logger'
 * Utilitários para manipulação e validação de datas
 */

/**
 * Formata uma data para o padrão brasileiro (DD/MM/AAAA)
 * @param {string|Date} date - Data a ser formatada
 * @returns {string} Data formatada ou string vazia se inválida
 */
export function formatDate(date) {
  if (!date) return '';
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    if (isNaN(dateObj.getTime())) {
      return '';
    }
    
    return dateObj.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  } catch (error) {
    logger.error('Erro ao formatar data:', error);
    return '';
  }
}

/**
 * Formata uma data para exibição completa (dia da semana, DD de mês de AAAA)
 * @param {string|Date} date - Data a ser formatada
 * @returns {string} Data formatada ou string vazia se inválida
 */
export function formatDateLong(date) {
  if (!date) return '';
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    if (isNaN(dateObj.getTime())) {
      return '';
    }
    
    return dateObj.toLocaleDateString('pt-BR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  } catch (error) {
    logger.error('Erro ao formatar data:', error);
    return '';
  }
}

/**
 * Valida se uma data é válida
 * @param {string|Date} date - Data a ser validada
 * @returns {boolean} True se a data for válida
 */
export function isValidDate(date) {
  if (!date) return false;
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return !isNaN(dateObj.getTime());
  } catch (error) {
    return false;
  }
}

/**
 * Verifica se uma data está no passado
 * @param {string|Date} date - Data a ser verificada
 * @returns {boolean} True se a data estiver no passado
 */
export function isDateInPast(date) {
  if (!isValidDate(date)) return false;
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  return dateObj < today;
}

/**
 * Verifica se uma data está no futuro
 * @param {string|Date} date - Data a ser verificada
 * @returns {boolean} True se a data estiver no futuro
 */
export function isDateInFuture(date) {
  if (!isValidDate(date)) return false;
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const today = new Date();
  today.setHours(23, 59, 59, 999);
  
  return dateObj > today;
}

/**
 * Calcula a diferença em dias entre duas datas
 * @param {string|Date} date1 - Primeira data
 * @param {string|Date} date2 - Segunda data
 * @returns {number} Diferença em dias (positivo se date1 > date2)
 */
export function daysDifference(date1, date2) {
  if (!isValidDate(date1) || !isValidDate(date2)) return 0;
  
  const dateObj1 = typeof date1 === 'string' ? new Date(date1) : date1;
  const dateObj2 = typeof date2 === 'string' ? new Date(date2) : date2;
  
  const timeDiff = dateObj1.getTime() - dateObj2.getTime();
  return Math.ceil(timeDiff / (1000 * 3600 * 24));
}

/**
 * Adiciona dias a uma data
 * @param {string|Date} date - Data base
 * @param {number} days - Número de dias a adicionar
 * @returns {Date|null} Nova data ou null se inválida
 */
export function addDays(date, days) {
  if (!isValidDate(date)) return null;
  
  const dateObj = typeof date === 'string' ? new Date(date) : new Date(date);
  dateObj.setDate(dateObj.getDate() + days);
  
  return dateObj;
}

/**
 * Converte uma string de data no formato DD/MM/AAAA para AAAA-MM-DD
 * @param {string} dateStr - Data no formato DD/MM/AAAA
 * @returns {string} Data no formato AAAA-MM-DD ou string vazia se inválida
 */
export function convertBrDateToIso(dateStr) {
  if (!dateStr) return '';
  
  try {
    const parts = dateStr.split('/');
    if (parts.length !== 3) return '';
    
    const [day, month, year] = parts;
    const isoDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    
    // Valida se a data é válida
    if (isValidDate(isoDate)) {
      return isoDate;
    }
    
    return '';
  } catch (error) {
    logger.error('Erro ao converter data:', error);
    return '';
  }
}

/**
 * Converte uma string de data no formato AAAA-MM-DD para DD/MM/AAAA
 * @param {string} dateStr - Data no formato AAAA-MM-DD
 * @returns {string} Data no formato DD/MM/AAAA ou string vazia se inválida
 */
export function convertIsoDateToBr(dateStr) {
  if (!dateStr) return '';
  
  try {
    const parts = dateStr.split('-');
    if (parts.length !== 3) return '';
    
    const [year, month, day] = parts;
    return `${day.padStart(2, '0')}/${month.padStart(2, '0')}/${year}`;
  } catch (error) {
    logger.error('Erro ao converter data:', error);
    return '';
  }
}

export function formatDateTime(date, options = { withSeconds: false }) {
  if (!date) return '';
  try {
    const d = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(d.getTime())) return '';
    const base = {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    if (options?.withSeconds) base.second = '2-digit';
    return d.toLocaleString('pt-BR', base);
  } catch (error) {
    logger.error('Erro ao formatar data/hora:', error);
    return '';
  }
}

export function formatTimeAgo(date) {
  if (!isValidDate(date)) return '';
  try {
    const d = typeof date === 'string' ? new Date(date) : date;
    const diffMs = Date.now() - d.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    if (diffSec < 5) return 'agora';
    if (diffSec < 60) return `há ${diffSec}s`;
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `há ${diffMin} min`;
    const diffHours = Math.floor(diffMin / 60);
    if (diffHours < 24) return `há ${diffHours} h`;
    const diffDays = Math.floor(diffHours / 24);
    return `há ${diffDays} d`;
  } catch (error) {
    logger.error('Erro ao calcular tempo relativo:', error);
    return '';
  }
}