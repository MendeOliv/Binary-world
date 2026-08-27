// Chat functionality for Código Binário
class CódigoBinárioChat {
    constructor() {
        // Get API base from meta tag, fallback to relative /api
        const meta = document.querySelector('meta[name="api-base"]');
        this.apiBase = meta ? meta.getAttribute('content') : '/api';
        this.currentProjectId = null;
        this.isTyping = false;
        this.init();
    }

    init() {
        // Create or get current project
        this.getOrCreateProject();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial chat history
        this.loadChatHistory();
        
        // Add welcome message if no history
        this.addInitialMessage();
    }

    setupEventListeners() {
        const sendButton = document.querySelector('button[aria-label="Send"]') || 
                          document.querySelector('button:has(> span.material-symbols-outlined:contains("send"))');
        const textarea = document.querySelector('textarea[placeholder*="Enter command or message"]');
        
        if (sendButton && textarea) {
            sendButton.addEventListener('click', () => this.sendMessage());
            textarea.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
    }

    async getOrCreateProject() {
        try {
            // Try to get existing project or create a default one
            const response = await fetch(`${this.apiBase}/projects`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    // In a real app, you'd have auth here
                }
            });
            
            if (!response.ok) {
                // Create a default project for visitors
                const projectResponse = await fetch(`${this.apiBase}/projects`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: `Projeto Visitante ${new Date().toISOString().slice(0,10)}`,
                        status: 'active',
                        current_phase_id: 'INITIALIZE'
                    })
                });
                
                if (projectResponse.ok) {
                    const projectData = await projectResponse.json();
                    this.currentProjectId = projectData.id;
                }
            } else {
                const projects = await response.json();
                if (projects.length > 0) {
                    this.currentProjectId = projects[0].id;
                } else {
                    // Create project if none exists
                    const projectResponse = await fetch(`${this.apiBase}/projects`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: `Projeto Visitante ${new Date().toISOString().slice(0,10)}`,
                            status: 'active',
                            current_phase_id: 'INITIALIZE'
                        })
                    });
                    
                    if (projectResponse.ok) {
                        const projectData = await projectResponse.json();
                        this.currentProjectId = projectData.id;
                    }
                }
            }
        } catch (error) {
            console.error('Error getting/creating project:', error);
            // Fallback to a hardcoded ID for demo - in production, handle properly
            this.currentProjectId = '11111111-1111-1111-1111-111111111111';
        }
    }

    async sendMessage() {
        const textarea = document.querySelector('textarea[placeholder*="Enter command or message"]');
        if (!textarea) return;
        
        const message = textarea.value.trim();
        if (!message) return;
        
        // Clear input
        textarea.value = '';
        textarea.style.height = 'auto';
        
        // Add user message to chat
        this.addUserMessage(message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to backend
            const response = await fetch(`${this.apiBase}/projects/${this.currentProjectId}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add AI response to chat
            this.addAIMessage(data.response);
            
            // Process extracted memory if available
            if (data.extracted_memory) {
                this.processExtractedMemory(data.extracted_memory);
            }
            
            // If clarification is needed, we already handled it in the response
            // The orchestrator returns a clarification question as the response when needed
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addSystemMessage('Desculpe, ocorreu um erro. Por favor, tente novamente.');
        }
    }

    addUserMessage(content) {
        const chatHistory = document.querySelector('.flex-1.overflow-y-auto.p-lg.space-y-6');
        if (!chatHistory) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex justify-end';
        messageDiv.innerHTML = `
            <div class="bg-surface border border-outline-variant p-md rounded-lg max-w-[80%] rounded-tr-none hard-shadow">
                <p class="font-body-md text-body-md text-on-surface">${this.escapeHtml(content)}</p>
                <span class="font-label-sm text-label-sm text-on-surface-variant block mt-2 text-right">${this.getCurrentTime()}</span>
            </div>
        `;
        
        chatHistory.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addAIMessage(content) {
        const chatHistory = document.querySelector('.flex-1.overflow-y-auto.p-lg.space-y-6');
        if (!chatHistory) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex justify-start';
        messageDiv.innerHTML = `
            <div class="bg-surface border border-primary-container p-md rounded-lg max-w-[85%] rounded-tl-none glow-hover transition-all">
                <div class="flex items-center gap-2 mb-2 text-primary font-label-sm text-label-sm">
                    <span class="material-symbols-outlined text-[16px]">terminal</span>
                    CB_SYS_AGENT
                </div>
                <p class="font-body-md text-body-md text-on-surface mb-4">${this.escapeHtml(content)}</p>
                <span class="font-label-sm text-label-sm text-on-surface-variant block mt-2">${this.getCurrentTime()}</span>
            </div>
        `;
        
        chatHistory.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addSystemMessage(content) {
        const chatHistory = document.querySelector('.flex-1.overflow-y-auto.p-lg.space-y-6');
        if (!chatHistory) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex justify-center';
        messageDiv.innerHTML = `
            <div class="text-center text-text-secondary italic p-md">
                <p>${this.escapeHtml(content)}</p>
            </div>
        `;
        
        chatHistory.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        // Remove any existing typing indicator
        this.hideTypingIndicator();
        
        const chatHistory = document.querySelector('.flex-1.overflow-y-auto.p-lg.space-y-6');
        if (!chatHistory) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'flex justify-start typing-indicator';
        typingDiv.innerHTML = `
            <div class="bg-surface border border-primary-container p-md rounded-lg max-w-[85%] rounded-tl-none">
                <div class="flex items-center gap-2 mb-2 text-primary font-label-sm text-label-sm">
                    <span class="material-symbols-outlined text-[16px]">terminal</span>
                    CB_SYS_AGENT
                </div>
                <div class="flex space-x-2">
                    <div class="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
                    <div class="w-2 h-2 rounded-full bg-primary animate-pulse" style="animation-delay: 0.2s"></div>
                    <div class="w-2 h-2 rounded-full bg-primary animate-pulse" style="animation-delay: 0.4s"></div>
                </div>
            </div>
        `;
        
        typingDiv.id = 'typing-indicator';
        chatHistory.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const existing = document.getElementById('typing-indicator');
        if (existing) {
            existing.remove();
        }
    }

    processExtractedMemory(extractedMemory) {
        // This would update the sidebar panels with new decisions, requirements, etc.
        // For now, we'll just log it - in a full implementation, this would update the UI
        console.log('Extracted memory:', extractedMemory);
        
        // TODO: Update sidebar panels with new data
        // This would involve:
        // - Updating decisions list
        // - Updating requirements list  
        // - Updating tasks list
        // - Updating project state
        // - Showing notifications for new items
    }

    loadChatHistory() {
        // In a real implementation, we'd fetch chat history from backend
        // For now, we'll start fresh or show a welcome message
        // This could be enhanced to load previous conversation
    }

    addInitialMessage() {
        // Check if chat is empty and add welcome message
        const chatHistory = document.querySelector('.flex-1.overflow-y-auto.p-lg.space-y-6');
        if (!chatHistory || chatHistory.children.length === 0) {
            this.addSystemMessage('Olá! Bem-vindo à Código Binário. Posso ajudá-lo a transformar uma ideia em uma solução utilizando inteligência artificial, automação ou tecnologia. O que você gostaria de criar ou resolver?');
        }
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute:'2-digit' });
    }

    escapeHtml(text) {
        const map = {
            '&': '&',
            '<': '<',
            '>': '>',
            '"': '"',
            "'": '&#039;'
        };
        
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    scrollToBottom() {
        const chatHistory = document.querySelector('.flex-1.overflow-y-auto.p-lg.space-y-6');
        if (chatHistory) {
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.códigoBinárioChat = new CódigoBinárioChat();
});