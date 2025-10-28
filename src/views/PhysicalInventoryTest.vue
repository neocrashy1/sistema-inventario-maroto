<template>
  <div class="physical-inventory-test">
    <h1>Teste do Inventário Físico</h1>
    <p>Se você está vendo esta mensagem, a rota está funcionando.</p>
    
    <div class="test-section">
      <h2>Teste dos Stores</h2>
      <div v-if="physicalInventoryStore">
        <p>✅ Physical Inventory Store carregado</p>
        <p>Total de inventários: {{ physicalInventoryStore.totalInventories }}</p>
      </div>
      <div v-else>
        <p>❌ Erro ao carregar Physical Inventory Store</p>
      </div>
      
      <div v-if="assetsStore">
        <p>✅ Assets Store carregado</p>
        <p>Total de ativos: {{ assetsStore.totalAvailableAssets }}</p>
      </div>
      <div v-else>
        <p>❌ Erro ao carregar Assets Store</p>
      </div>
    </div>
    
    <div class="test-section">
      <h2>Teste das Funções Utils</h2>
      <p>Data atual formatada: {{ currentDateFormatted }}</p>
      <p>Status de garantia teste: {{ testWarrantyStatus }}</p>
    </div>
  </div>
</template>

<script>
import logger from '@/utils/logger'
import { ref, computed, onMounted } from 'vue'
import { usePhysicalInventoryStore } from '@/stores/physicalInventory.js'
import { useAssetsStore } from '@/stores/assets.js'
import { formatDate } from '@/utils/dateUtils.js'
import { getWarrantyStatus } from '@/utils/warrantyUtils.js'

export default {
  name: 'PhysicalInventoryTest',
  setup() {
    // Inicializar stores dentro do setup onde o Pinia está ativo
    const physicalInventoryStore = usePhysicalInventoryStore()
    const assetsStore = useAssetsStore()
    
    const currentDateFormatted = computed(() => {
      try {
        return formatDate(new Date())
      } catch (error) {
        logger.error('Erro ao formatar data:', error)
        return 'Erro ao formatar data'
      }
    })
    
    const testWarrantyStatus = computed(() => {
      try {
        const futureDate = new Date()
        futureDate.setFullYear(futureDate.getFullYear() + 1)
        return getWarrantyStatus(futureDate)
      } catch (error) {
        logger.error('Erro ao calcular status:', error)
        return 'Erro ao calcular status'
      }
    })
    
    onMounted(() => {
      logger.debug('PhysicalInventoryTest montado')
      logger.debug('Physical Inventory Store:', physicalInventoryStore)
      logger.debug('Assets Store:', assetsStore)
    })
    
    return {
      physicalInventoryStore,
      assetsStore,
      currentDateFormatted,
      testWarrantyStatus
    }
  }
}
</script>

<style scoped>
.physical-inventory-test {
  padding: 20px;
}

.test-section {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.test-section h2 {
  margin-top: 0;
  color: #333;
}
</style>