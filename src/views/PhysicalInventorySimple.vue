<template>
  <div class="physical-inventory-simple">
    <h1>Inventário Físico - Teste Simples</h1>
    
    <!-- Teste básico sem stores -->
    <div class="basic-test">
      <h2>Teste Básico</h2>
      <p>Esta seção deve aparecer sempre</p>
      <p>Data atual: {{ new Date().toLocaleDateString() }}</p>
    </div>
    
    <!-- Teste com stores -->
    <div class="store-test" v-if="storesLoaded">
      <h2>Teste com Stores</h2>
      <p>✅ Stores carregados com sucesso</p>
      <p>Total de inventários: {{ totalInventories || 0 }}</p>
      <p>Inventários ativos: {{ activeInventoriesCount || 0 }}</p>
    </div>
    
    <div class="store-error" v-else-if="storeError">
      <h2>Erro nos Stores</h2>
      <p>❌ {{ storeError }}</p>
    </div>
    
    <div class="loading" v-else>
      <h2>Carregando Stores...</h2>
      <p>⏳ Aguarde...</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import logger from '@/utils/logger'

export default {
  name: 'PhysicalInventorySimple',
  setup() {
    const storesLoaded = ref(false)
    const storeError = ref('')
    const physicalInventoryStore = ref(null)
    const assetsStore = ref(null)
    
    // Propriedades reativas dos stores
    const totalInventories = ref(0)
    const activeInventoriesCount = ref(0)
    
    const initializeStores = async () => {
      try {
        logger.debug('Iniciando carregamento dos stores...')
        
        // Importar e inicializar Physical Inventory Store
        const { usePhysicalInventoryStore } = await import('@/stores/physicalInventory')
        physicalInventoryStore.value = usePhysicalInventoryStore()
        
        // Importar e inicializar Assets Store
        const { useAssetsStore } = await import('@/stores/assets')
        assetsStore.value = useAssetsStore()
        
  logger.debug('Stores importados com sucesso')
        
        // Usar storeToRefs para manter reatividade
        const physicalStoreRefs = storeToRefs(physicalInventoryStore.value)
        
        // Atribuir valores reativos
        totalInventories.value = physicalStoreRefs.totalInventories.value
        activeInventoriesCount.value = physicalStoreRefs.activeInventories.value?.length || 0
        
  storesLoaded.value = true
  logger.info('Stores inicializados com sucesso')
        
      } catch (error) {
        logger.error('Erro ao inicializar stores', { error })
        storeError.value = `Erro ao carregar stores: ${error.message}`
      }
    }
    
    onMounted(() => {
      logger.debug('Componente PhysicalInventorySimple montado')
      initializeStores()
    })
    
    return {
      storesLoaded,
      storeError,
      totalInventories,
      activeInventoriesCount
    }
  }
}
</script>

<style scoped>
.physical-inventory-simple {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.basic-test, .store-test, .store-error, .loading {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.basic-test {
  background-color: #f0f8ff;
  border-color: #007bff;
}

.store-test {
  background-color: #f0fff0;
  border-color: #28a745;
}

.store-error {
  background-color: #fff5f5;
  border-color: #dc3545;
}

.loading {
  background-color: #fff8e1;
  border-color: #ffc107;
}

h1, h2 {
  margin-top: 0;
  color: #333;
}
</style>