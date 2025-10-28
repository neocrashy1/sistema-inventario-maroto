// Script para configurar usuário de demonstração
const API_BASE = 'http://localhost:8000/api/v1';

async function setupDemoUser() {
    try {
        console.log('🔧 Configurando usuário de demonstração...');
        
        // Dados do usuário padrão
        const userData = {
            username: 'admin',
            email: 'admin@levitiis.com',
            password: 'admin123',
            first_name: 'Administrador',
            last_name: 'Sistema',
            role: 'MANAGER'
        };

        // Registrar usuário
        console.log('📝 Registrando usuário...');
        const registerResponse = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        if (registerResponse.ok) {
            console.log('✅ Usuário registrado com sucesso!');
        } else {
            console.log('ℹ️ Usuário já existe ou erro no registro');
        }

        // Fazer login
        console.log('🔐 Fazendo login...');
        const formData = new FormData();
        formData.append('username', userData.username);
        formData.append('password', userData.password);

        const loginResponse = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            body: formData
        });

        if (loginResponse.ok) {
            const loginData = await loginResponse.json();
            
            // Salvar tokens no localStorage
            localStorage.setItem('access_token', loginData.access_token);
            localStorage.setItem('refresh_token', loginData.refresh_token);
            
            console.log('✅ Login realizado com sucesso!');
            console.log('🎯 Tokens salvos no localStorage');
            console.log('📊 Sistema pronto para uso!');
            
            // Recarregar a página para aplicar a autenticação
            window.location.reload();
        } else {
            const errorData = await loginResponse.json();
            console.error('❌ Erro no login:', errorData);
        }

    } catch (error) {
        console.error('❌ Erro ao configurar usuário:', error);
    }
}

// Executar automaticamente se não houver token
if (!localStorage.getItem('access_token')) {
    console.log('🚀 Iniciando configuração automática...');
    setupDemoUser();
} else {
    console.log('✅ Usuário já autenticado!');
}