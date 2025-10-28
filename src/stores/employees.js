import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useEmployeesStore = defineStore('employees', () => {
  // Estado
  const employees = ref([
    {
      id: 1,
      code: 'FUNC001',
      name: 'João Silva',
      email: 'joao.silva@levitiis.com',
      phone: '(11) 99999-1111',
      cpf: '123.456.789-01',
      rg: '12.345.678-9',
      birthDate: '1985-03-15',
      hireDate: '2020-01-15',
      department: 'Tecnologia da Informação',
      position: 'Desenvolvedor Senior',
      manager: 'Carlos Oliveira',
      location: {
        id: 1,
        name: 'Matriz São Paulo',
        address: 'Av. Paulista, 1000 - São Paulo/SP'
      },
      status: 'Ativo',
      salary: 8500.00,
      workSchedule: '08:00 - 17:00',
      contractType: 'CLT',
      emergencyContact: {
        name: 'Maria Silva',
        relationship: 'Esposa',
        phone: '(11) 99999-2222'
      },
      address: {
        street: 'Rua das Flores, 123',
        neighborhood: 'Vila Madalena',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '05432-000'
      },
      avatar: null,
      notes: 'Funcionário exemplar, especialista em Vue.js',
      createdAt: '2020-01-15T09:00:00Z',
      updatedAt: '2024-01-15T10:30:00Z'
    },
    {
      id: 2,
      code: 'FUNC002',
      name: 'Maria Santos',
      email: 'maria.santos@levitiis.com',
      phone: '(11) 99999-3333',
      cpf: '987.654.321-02',
      rg: '98.765.432-1',
      birthDate: '1990-07-22',
      hireDate: '2021-03-10',
      department: 'Marketing',
      position: 'Coordenadora de Marketing',
      manager: 'Ana Paula Costa',
      location: {
        id: 1,
        name: 'Matriz São Paulo',
        address: 'Av. Paulista, 1000 - São Paulo/SP'
      },
      status: 'Ativo',
      salary: 7200.00,
      workSchedule: '09:00 - 18:00',
      contractType: 'CLT',
      emergencyContact: {
        name: 'José Santos',
        relationship: 'Pai',
        phone: '(11) 99999-4444'
      },
      address: {
        street: 'Av. Rebouças, 456',
        neighborhood: 'Pinheiros',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '05401-000'
      },
      avatar: null,
      notes: 'Responsável por campanhas digitais',
      createdAt: '2021-03-10T14:00:00Z',
      updatedAt: '2024-01-10T16:20:00Z'
    },
    {
      id: 3,
      code: 'FUNC003',
      name: 'Carlos Lima',
      email: 'carlos.lima@levitiis.com',
      phone: '(11) 99999-5555',
      cpf: '456.789.123-03',
      rg: '45.678.912-3',
      birthDate: '1982-11-08',
      hireDate: '2019-06-01',
      department: 'Vendas',
      position: 'Gerente de Vendas',
      manager: 'Roberto Silva',
      location: {
        id: 2,
        name: 'Filial Rio de Janeiro',
        address: 'Av. Copacabana, 500 - Rio de Janeiro/RJ'
      },
      status: 'Ativo',
      salary: 9500.00,
      workSchedule: '08:30 - 17:30',
      contractType: 'CLT',
      emergencyContact: {
        name: 'Fernanda Lima',
        relationship: 'Esposa',
        phone: '(21) 99999-6666'
      },
      address: {
        street: 'Rua Barata Ribeiro, 789',
        neighborhood: 'Copacabana',
        city: 'Rio de Janeiro',
        state: 'RJ',
        zipCode: '22040-000'
      },
      avatar: null,
      notes: 'Especialista em vendas B2B',
      createdAt: '2019-06-01T10:00:00Z',
      updatedAt: '2024-01-05T11:15:00Z'
    },
    {
      id: 4,
      code: 'FUNC004',
      name: 'Ana Costa',
      email: 'ana.costa@levitiis.com',
      phone: '(11) 99999-7777',
      cpf: '789.123.456-04',
      rg: '78.912.345-6',
      birthDate: '1988-04-12',
      hireDate: '2022-01-20',
      department: 'Administração',
      position: 'Analista Administrativo',
      manager: 'Pedro Almeida',
      location: {
        id: 1,
        name: 'Matriz São Paulo',
        address: 'Av. Paulista, 1000 - São Paulo/SP'
      },
      status: 'Ativo',
      salary: 5800.00,
      workSchedule: '08:00 - 17:00',
      contractType: 'CLT',
      emergencyContact: {
        name: 'Luiz Costa',
        relationship: 'Irmão',
        phone: '(11) 99999-8888'
      },
      address: {
        street: 'Rua Augusta, 321',
        neighborhood: 'Consolação',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01305-000'
      },
      avatar: null,
      notes: 'Responsável por processos administrativos',
      createdAt: '2022-01-20T13:30:00Z',
      updatedAt: '2024-01-12T09:45:00Z'
    },
    {
      id: 5,
      code: 'FUNC005',
      name: 'Rafael Oliveira',
      email: 'rafael.oliveira@levitiis.com',
      phone: '(11) 99999-9999',
      cpf: '321.654.987-05',
      rg: '32.165.498-7',
      birthDate: '1992-09-30',
      hireDate: '2023-05-15',
      department: 'Tecnologia da Informação',
      position: 'Analista de Suporte',
      manager: 'João Silva',
      location: {
        id: 1,
        name: 'Matriz São Paulo',
        address: 'Av. Paulista, 1000 - São Paulo/SP'
      },
      status: 'Ativo',
      salary: 4500.00,
      workSchedule: '08:00 - 17:00',
      contractType: 'CLT',
      emergencyContact: {
        name: 'Sandra Oliveira',
        relationship: 'Mãe',
        phone: '(11) 99999-0000'
      },
      address: {
        street: 'Rua Teodoro Sampaio, 654',
        neighborhood: 'Pinheiros',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '05406-000'
      },
      avatar: null,
      notes: 'Especialista em infraestrutura de TI',
      createdAt: '2023-05-15T08:00:00Z',
      updatedAt: '2024-01-08T14:20:00Z'
    }
  ])

  const searchTerm = ref('')
  const selectedDepartment = ref('')
  const selectedStatus = ref('')
  const selectedLocation = ref('')

  // Getters computados
  const totalEmployees = computed(() => employees.value.length)
  
  const activeEmployees = computed(() => 
    employees.value.filter(emp => emp.status === 'Ativo').length
  )
  
  const inactiveEmployees = computed(() => 
    employees.value.filter(emp => emp.status === 'Inativo').length
  )

  const departments = computed(() => {
    const depts = [...new Set(employees.value.map(emp => emp.department))]
    return depts.sort()
  })

  const locations = computed(() => {
    const locs = [...new Set(employees.value.map(emp => emp.location.name))]
    return locs.sort()
  })

  const filteredEmployees = computed(() => {
    let filtered = employees.value

    if (searchTerm.value) {
      const search = searchTerm.value.toLowerCase()
      filtered = filtered.filter(emp => 
        emp.name.toLowerCase().includes(search) ||
        emp.email.toLowerCase().includes(search) ||
        emp.code.toLowerCase().includes(search) ||
        emp.department.toLowerCase().includes(search) ||
        emp.position.toLowerCase().includes(search)
      )
    }

    if (selectedDepartment.value) {
      filtered = filtered.filter(emp => emp.department === selectedDepartment.value)
    }

    if (selectedStatus.value) {
      filtered = filtered.filter(emp => emp.status === selectedStatus.value)
    }

    if (selectedLocation.value) {
      filtered = filtered.filter(emp => emp.location.name === selectedLocation.value)
    }

    return filtered
  })

  const employeesByDepartment = computed(() => {
    const stats = {}
    employees.value.forEach(emp => {
      if (!stats[emp.department]) {
        stats[emp.department] = 0
      }
      stats[emp.department]++
    })
    return stats
  })

  // Actions
  const addEmployee = (employeeData) => {
    const newEmployee = {
      id: Math.max(...employees.value.map(e => e.id)) + 1,
      code: `FUNC${String(Math.max(...employees.value.map(e => e.id)) + 1).padStart(3, '0')}`,
      ...employeeData,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    employees.value.push(newEmployee)
    return newEmployee
  }

  const updateEmployee = (id, employeeData) => {
    const index = employees.value.findIndex(emp => emp.id === id)
    if (index !== -1) {
      employees.value[index] = {
        ...employees.value[index],
        ...employeeData,
        updatedAt: new Date().toISOString()
      }
      return employees.value[index]
    }
    return null
  }

  const deleteEmployee = (id) => {
    const index = employees.value.findIndex(emp => emp.id === id)
    if (index !== -1) {
      employees.value.splice(index, 1)
      return true
    }
    return false
  }

  const getEmployeeById = (id) => {
    return employees.value.find(emp => emp.id === id)
  }

  const getEmployeeByCode = (code) => {
    return employees.value.find(emp => emp.code === code)
  }

  const deactivateEmployee = (id, reason = '') => {
    const employee = getEmployeeById(id)
    if (employee) {
      employee.status = 'Inativo'
      employee.deactivationDate = new Date().toISOString()
      employee.deactivationReason = reason
      employee.updatedAt = new Date().toISOString()
      return true
    }
    return false
  }

  const reactivateEmployee = (id) => {
    const employee = getEmployeeById(id)
    if (employee) {
      employee.status = 'Ativo'
      employee.deactivationDate = null
      employee.deactivationReason = null
      employee.updatedAt = new Date().toISOString()
      return true
    }
    return false
  }

  const clearFilters = () => {
    searchTerm.value = ''
    selectedDepartment.value = ''
    selectedStatus.value = ''
    selectedLocation.value = ''
  }

  return {
    // Estado
    employees,
    searchTerm,
    selectedDepartment,
    selectedStatus,
    selectedLocation,
    
    // Getters
    totalEmployees,
    activeEmployees,
    inactiveEmployees,
    departments,
    locations,
    filteredEmployees,
    employeesByDepartment,
    
    // Actions
    addEmployee,
    updateEmployee,
    deleteEmployee,
    getEmployeeById,
    getEmployeeByCode,
    deactivateEmployee,
    reactivateEmployee,
    clearFilters
  }
})