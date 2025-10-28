# Sprint Checklist — Levitiis (Resumo gerado automaticamente)

Este arquivo lista as tarefas priorizadas por sprint, com arquivos-alvo sugeridos e estimativas.

---

## Sprint 1 — Fundação UX (5 dias)

- [x] Task: Loading States Consistentes — 2-3h
  - Objetivo: Criar feedback visual consistente durante operações assíncronas.
  - Arquivos: `src/components/common/LoadingSpinner.vue` (já existe), `src/components/common/SkeletonLoader.vue` (criado), `src/views/assets/Assets.vue` (integrado), `src/views/Dashboard.vue` (integrado)

- [x] Task: Validação de Formulários — 3-4h
  - Objetivo: Implementar validação mais robusta em formulários (Login, Assets, Users).
  - Arquivos sugeridos: `src/views/auth/Login.vue`, `src/views/assets/Assets.vue`, `src/utils/validation.js` (criar)

- [ ] Task: Sistema de Notificações — 2-3h
  - Objetivo: Centralizar tratamento de erros e toasts.
  - Arquivos sugeridos: `src/plugins/notifications.js` (criar), `src/components/common/ToastNotification.vue` (criar), `src/services/api.js` (atualizar)

## Sprint 2 — Qualidade e Performance (5 dias)

- [ ] Task: Remover `console.log` em produção — 1h
  - Arquivos: varredura em `src/**/*.vue` e `src/**/*.js`

- [ ] Task: Lazy Loading de Componentes — 2-3h
  - Arquivos: `src/router/index.js`, `vite.config.js` (ajustes), rotas grandes e views

- [ ] Task: Testes Unitários (iniciar) — 4-6h
  - Arquivos: componentes críticos em `src/components/` e stores em `src/stores/`

## Sprint 3 — Otimização Avançada (5 dias)

- [ ] Task: Cache Inteligente de API — 3-4h
  - Arquivos: `src/services/**`, `backend/app/services/**`

- [ ] Task: Acessibilidade (WCAG) — 4-5h
  - Arquivos: todos os componentes de interface (`src/components/**`, `src/views/**`)

---

Observações:
- `SkeletonLoader.vue` foi criado em `src/components/common/` e integrado em `Assets.vue` e `Dashboard.vue`.
- `LoadingSpinner.vue` já existia e é utilizado como loadingComponent em componentes carregados assincronamente.
- Próximos passos sugeridos: gerar issues a partir dessa checklist, ou atribuir tarefas para desenvolvedores.
