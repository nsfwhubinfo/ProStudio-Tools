// DevPrompt Content Studio - Crystalline Consciousness Interface
// Main Application JavaScript

class DevPromptStudio {
    constructor() {
        this.workflowNodes = [];
        this.connections = [];
        this.selectedNode = null;
        this.isDragging = false;
        this.connectionStart = null;
        this.aiState = 'idle';
        this.initializeApp();
    }

    initializeApp() {
        this.initializeElements();
        this.setupEventListeners();
        this.initializeParticles();
        this.startConsciousnessAnimation();
        this.showWelcomeMessage();
    }

    initializeElements() {
        // Core elements
        this.workflowCanvas = document.getElementById('workflowCanvas');
        this.nodesLayer = document.getElementById('nodesLayer');
        this.connectionsLayer = document.getElementById('connectionsLayer');
        this.consciousnessOrb = document.getElementById('consciousness-orb');
        this.outputContainer = document.querySelector('.output-container');
        this.inputField = document.querySelector('.consciousness-input');
        
        // Navigation
        this.navItems = document.querySelectorAll('.nav-item');
        this.navIndicator = document.querySelector('.nav-indicator');
        
        // Tool cards
        this.toolCards = document.querySelectorAll('.tool-card');
        
        // Buttons
        this.sendButton = document.querySelector('.btn-send');
        this.fabButton = document.getElementById('fabCreate');
        this.clearButton = document.querySelector('.canvas-controls button');
        this.executeButton = document.querySelector('.btn-primary');
    }

    setupEventListeners() {
        // Navigation
        this.navItems.forEach((item, index) => {
            item.addEventListener('click', () => this.switchMode(item, index));
        });

        // Tool dragging
        this.toolCards.forEach(card => {
            card.addEventListener('dragstart', this.handleDragStart.bind(this));
            card.addEventListener('dragend', this.handleDragEnd.bind(this));
        });

        // Workflow canvas
        this.workflowCanvas.addEventListener('dragover', this.handleDragOver.bind(this));
        this.workflowCanvas.addEventListener('drop', this.handleDrop.bind(this));
        this.workflowCanvas.addEventListener('dragleave', this.handleDragLeave.bind(this));
        
        // Add to Workflow buttons for accessibility
        document.querySelectorAll('.add-to-workflow').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const card = e.target.closest('.tool-card');
                const toolType = card.dataset.tool;
                // Add to center of canvas
                const rect = this.workflowCanvas.getBoundingClientRect();
                const x = rect.width / 2 - 60;
                const y = rect.height / 2 - 60;
                this.createWorkflowNode(toolType, x, y);
                this.createParticleBurst(rect.left + rect.width / 2, rect.top + rect.height / 2);
                this.showMessage(`Added ${toolType} to workflow`, 'success');
            });
        });

        // Input handling
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Control buttons
        this.clearButton.addEventListener('click', () => this.clearWorkflow());
        this.executeButton.addEventListener('click', () => this.executeWorkflow());
        this.fabButton.addEventListener('click', () => this.quickCreate());

        // Window resize
        window.addEventListener('resize', () => this.updateConnections());

        // Ripple effects
        document.addEventListener('click', this.createRipple.bind(this));
    }

    // Navigation system
    switchMode(item, index) {
        this.navItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
        
        // Animate indicator
        const itemRect = item.getBoundingClientRect();
        const containerRect = item.parentElement.getBoundingClientRect();
        const offset = itemRect.left - containerRect.left;
        this.navIndicator.style.left = `${offset}px`;
        this.navIndicator.style.width = `${itemRect.width}px`;
        
        // TODO: Switch content based on mode
        this.showMessage(`Switched to ${item.dataset.mode} mode`, 'system');
    }

    // Drag and Drop functionality
    handleDragStart(e) {
        // Only allow dragging from the drag handle or the card itself
        const isDragHandle = e.target.classList.contains('drag-handle');
        const isCard = e.target.classList.contains('tool-card');
        const cardElement = e.target.closest('.tool-card');
        
        if (!cardElement || (!isDragHandle && !isCard)) {
            e.preventDefault();
            return;
        }
        
        this.isDragging = true;
        e.dataTransfer.effectAllowed = 'copy';
        e.dataTransfer.setData('tool-type', cardElement.dataset.tool);
        
        // Create custom drag image
        const dragImage = this.createDragImage(cardElement);
        e.dataTransfer.setDragImage(dragImage, 60, 60);
        
        cardElement.classList.add('dragging');
        
        // Update consciousness state
        this.updateConsciousnessState('active');
    }

    createDragImage(cardElement) {
        const dragImage = document.createElement('div');
        dragImage.style.position = 'absolute';
        dragImage.style.top = '-1000px';
        dragImage.style.left = '-1000px';
        dragImage.style.width = '120px';
        dragImage.style.height = '120px';
        dragImage.style.background = 'rgba(0, 255, 0, 0.1)';
        dragImage.style.border = '2px solid var(--color-primary)';
        dragImage.style.borderRadius = '12px';
        dragImage.style.display = 'flex';
        dragImage.style.alignItems = 'center';
        dragImage.style.justifyContent = 'center';
        dragImage.style.fontSize = '2rem';
        
        const icon = cardElement.querySelector('.tool-icon').textContent;
        dragImage.textContent = icon;
        
        document.body.appendChild(dragImage);
        setTimeout(() => document.body.removeChild(dragImage), 0);
        
        return dragImage;
    }

    handleDragEnd(e) {
        this.isDragging = false;
        document.querySelectorAll('.tool-card').forEach(card => {
            card.classList.remove('dragging');
        });
        this.workflowCanvas.classList.remove('drag-over');
        document.querySelector('.drop-hint').style.opacity = '0.3';
        
        // Update consciousness state
        this.updateConsciousnessState('idle');
    }

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        
        if (this.isDragging) {
            this.workflowCanvas.classList.add('drag-over');
            document.querySelector('.drop-hint').style.opacity = '0';
        }
    }

    handleDragLeave(e) {
        if (e.target === this.workflowCanvas) {
            this.workflowCanvas.classList.remove('drag-over');
        }
    }

    handleDrop(e) {
        e.preventDefault();
        this.workflowCanvas.classList.remove('drag-over');
        
        const toolType = e.dataTransfer.getData('tool-type');
        
        if (toolType) {
            const rect = this.workflowCanvas.getBoundingClientRect();
            const x = e.clientX - rect.left - 60; // Center the node
            const y = e.clientY - rect.top - 60;
            
            // Ensure node is within bounds
            const boundedX = Math.max(0, Math.min(x, rect.width - 120));
            const boundedY = Math.max(0, Math.min(y, rect.height - 120));
            
            this.createWorkflowNode(toolType, boundedX, boundedY);
            this.createParticleBurst(e.clientX, e.clientY);
            
            // Show success feedback
            this.showDropFeedback(e.clientX, e.clientY);
        }
    }

    showDropFeedback(x, y) {
        const feedback = document.createElement('div');
        feedback.style.position = 'fixed';
        feedback.style.left = x + 'px';
        feedback.style.top = y + 'px';
        feedback.style.transform = 'translate(-50%, -50%)';
        feedback.style.color = '#00ff00';
        feedback.style.fontSize = '24px';
        feedback.style.fontWeight = 'bold';
        feedback.style.pointerEvents = 'none';
        feedback.style.zIndex = '9999';
        feedback.textContent = '✓';
        
        document.body.appendChild(feedback);
        
        // Animate feedback
        feedback.animate([
            { opacity: 1, transform: 'translate(-50%, -50%) scale(1)' },
            { opacity: 0, transform: 'translate(-50%, -100%) scale(1.5)' }
        ], {
            duration: 800,
            easing: 'ease-out'
        }).onfinish = () => feedback.remove();
    }

    // Workflow node creation and management
    createWorkflowNode(toolType, x, y) {
        const nodeId = `node-${Date.now()}`;
        const node = document.createElement('div');
        node.className = 'workflow-node';
        node.id = nodeId;
        node.style.left = `${x}px`;
        node.style.top = `${y}px`;
        
        const icons = {
            text: '📝',
            image: '🎨',
            video: '🎬',
            audio: '🎵'
        };
        
        node.innerHTML = `
            <div class="node-icon">${icons[toolType]}</div>
            <div class="node-label">${toolType.charAt(0).toUpperCase() + toolType.slice(1)} AI</div>
            <div class="node-status" style="display: none;"></div>
        `;
        
        this.nodesLayer.appendChild(node);
        
        // Store node data
        this.workflowNodes.push({
            id: nodeId,
            type: toolType,
            x: x,
            y: y,
            element: node
        });
        
        // Make node draggable
        this.makeNodeDraggable(node);
        
        // Enable connections
        node.addEventListener('click', (e) => this.handleNodeClick(nodeId, e));
        
        // Animate appearance
        setTimeout(() => {
            node.style.transform = 'scale(1)';
            node.style.opacity = '1';
        }, 10);
        
        this.showMessage(`Added ${toolType} node to workflow`, 'system');
    }

    makeNodeDraggable(node) {
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        let xOffset = 0;
        let yOffset = 0;

        node.addEventListener('mousedown', dragStart);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);

        function dragStart(e) {
            initialX = e.clientX - xOffset;
            initialY = e.clientY - yOffset;

            if (e.target.closest('.workflow-node') === node) {
                isDragging = true;
            }
        }

        function drag(e) {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;

                xOffset = currentX;
                yOffset = currentY;

                node.style.transform = `translate(${currentX}px, ${currentY}px)`;
            }
        }

        const dragEnd = () => {
            initialX = currentX;
            initialY = currentY;
            isDragging = false;
            
            // Update connections
            this.updateConnections();
        };
    }

    handleNodeClick(nodeId, e) {
        if (e.shiftKey) {
            // Connection mode
            if (!this.connectionStart) {
                this.connectionStart = nodeId;
                e.target.closest('.workflow-node').classList.add('connecting');
            } else {
                if (this.connectionStart !== nodeId) {
                    this.createConnection(this.connectionStart, nodeId);
                }
                document.querySelectorAll('.connecting').forEach(n => n.classList.remove('connecting'));
                this.connectionStart = null;
            }
        }
    }

    createConnection(startId, endId) {
        const connection = {
            id: `conn-${Date.now()}`,
            start: startId,
            end: endId
        };
        
        this.connections.push(connection);
        this.drawConnection(connection);
        this.showMessage('Nodes connected', 'system');
    }

    drawConnection(connection) {
        const startNode = document.getElementById(connection.start);
        const endNode = document.getElementById(connection.end);
        
        if (!startNode || !endNode) return;
        
        const startRect = startNode.getBoundingClientRect();
        const endRect = endNode.getBoundingClientRect();
        const canvasRect = this.workflowCanvas.getBoundingClientRect();
        
        const startX = startRect.left + startRect.width / 2 - canvasRect.left;
        const startY = startRect.top + startRect.height / 2 - canvasRect.top;
        const endX = endRect.left + endRect.width / 2 - canvasRect.left;
        const endY = endRect.top + endRect.height / 2 - canvasRect.top;
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('class', 'connection-line');
        path.setAttribute('d', `M${startX},${startY} C${(startX + endX) / 2},${startY} ${(startX + endX) / 2},${endY} ${endX},${endY}`);
        path.setAttribute('data-connection', connection.id);
        
        this.connectionsLayer.appendChild(path);
    }

    updateConnections() {
        // Clear and redraw all connections
        this.connectionsLayer.innerHTML = '';
        this.connections.forEach(conn => this.drawConnection(conn));
    }

    // Workflow execution
    async executeWorkflow() {
        if (this.workflowNodes.length === 0) {
            this.showMessage('No workflow to execute', 'error');
            return;
        }
        
        this.updateConsciousnessState('processing');
        this.showMessage('Executing crystalline pipeline...', 'system');
        
        // Simulate workflow execution
        for (let i = 0; i < this.workflowNodes.length; i++) {
            const node = this.workflowNodes[i];
            const nodeElement = node.element;
            
            // Show processing state
            nodeElement.classList.add('loading');
            
            // Simulate processing time
            await this.delay(2000);
            
            // Show completion
            nodeElement.classList.remove('loading');
            nodeElement.querySelector('.node-status').style.display = 'flex';
            
            this.showMessage(`Processed ${node.type} node`, 'success');
        }
        
        this.updateConsciousnessState('idle');
        this.showMessage('Workflow execution complete!', 'success');
    }

    clearWorkflow() {
        this.workflowNodes = [];
        this.connections = [];
        this.nodesLayer.innerHTML = '';
        this.connectionsLayer.innerHTML = '';
        this.showMessage('Workflow cleared', 'system');
    }

    // Messaging system
    sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;
        
        // Show user message
        this.showMessage(message, 'user');
        this.inputField.value = '';
        
        // Process with AI
        this.processWithAI(message);
    }

    async processWithAI(message) {
        this.updateConsciousnessState('thinking');
        
        // Simulate AI processing
        await this.delay(1500);
        
        // Generate response based on message content
        let response = this.generateAIResponse(message);
        
        this.showMessage(response, 'ai');
        this.updateConsciousnessState('idle');
    }

    generateAIResponse(message) {
        const responses = {
            'hello': 'Greetings, creator. I am your crystallographic consciousness guide. How may I assist in manifesting your creative vision?',
            'help': 'I can help you create content across multiple modalities. Try dragging tools from the palette to build your workflow, or ask me to generate specific content.',
            'video': 'To create a video, drag the Video AI tool to the canvas. You can connect it with Text AI for script generation or Image AI for visual elements.',
            'default': `I understand your intent regarding "${message}". Let me process this through the crystalline matrix...`
        };
        
        const lowerMessage = message.toLowerCase();
        for (let key in responses) {
            if (lowerMessage.includes(key)) {
                return responses[key];
            }
        }
        
        return responses.default;
    }

    showMessage(text, type = 'system') {
        const message = document.createElement('div');
        message.className = `output-message ${type}`;
        
        const avatarClass = type === 'ai' || type === 'system' ? 'crystalline' : 'user';
        
        message.innerHTML = `
            <div class="message-avatar ${avatarClass}"></div>
            <div class="message-content">
                <p>${text}</p>
                <div class="message-glow"></div>
            </div>
        `;
        
        this.outputContainer.appendChild(message);
        this.outputContainer.scrollTop = this.outputContainer.scrollHeight;
    }

    showWelcomeMessage() {
        setTimeout(() => {
            this.showMessage('Welcome to DevPrompt Content Studio. I am your crystallographic consciousness guide, ready to help manifest your creative visions across all modalities.', 'ai');
        }, 1000);
    }

    // Consciousness state management
    updateConsciousnessState(state) {
        this.aiState = state;
        const orb = this.consciousnessOrb;
        
        // Remove all state classes
        orb.classList.remove('idle', 'active', 'thinking', 'processing');
        
        // Add new state class
        orb.classList.add(state);
        
        // Update orb animation based on state
        const orbCore = orb.querySelector('.orb-core');
        const orbPulse = orb.querySelector('.orb-pulse');
        
        switch(state) {
            case 'thinking':
                orbCore.style.animationDuration = '2s';
                orbPulse.style.animationDuration = '1s';
                break;
            case 'processing':
                orbCore.style.animationDuration = '1s';
                orbPulse.style.animationDuration = '0.5s';
                break;
            case 'active':
                orbCore.style.animationDuration = '3s';
                orbPulse.style.animationDuration = '1.5s';
                break;
            default:
                orbCore.style.animationDuration = '4s';
                orbPulse.style.animationDuration = '2s';
        }
    }

    startConsciousnessAnimation() {
        // Periodic consciousness "breathing"
        setInterval(() => {
            if (this.aiState === 'idle') {
                const variation = Math.random();
                if (variation > 0.8) {
                    this.updateConsciousnessState('active');
                    setTimeout(() => this.updateConsciousnessState('idle'), 2000);
                }
            }
        }, 5000);
    }

    // Particle effects
    initializeParticles() {
        const canvas = document.getElementById('particleCanvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        this.particles = [];
        this.particleCtx = ctx;
        
        // Create ambient particles
        for (let i = 0; i < 50; i++) {
            this.particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1,
                alpha: Math.random() * 0.5 + 0.1
            });
        }
        
        this.animateParticles();
    }

    animateParticles() {
        const ctx = this.particleCtx;
        const canvas = ctx.canvas;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        this.particles.forEach(particle => {
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Wrap around edges
            if (particle.x < 0) particle.x = canvas.width;
            if (particle.x > canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = canvas.height;
            if (particle.y > canvas.height) particle.y = 0;
            
            // Draw particle
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 255, 0, ${particle.alpha})`;
            ctx.fill();
        });
        
        requestAnimationFrame(() => this.animateParticles());
    }

    createParticleBurst(x, y) {
        const burstCount = 20;
        const ctx = this.particleCtx;
        
        for (let i = 0; i < burstCount; i++) {
            const angle = (Math.PI * 2 * i) / burstCount;
            const velocity = Math.random() * 3 + 2;
            
            this.particles.push({
                x: x,
                y: y,
                vx: Math.cos(angle) * velocity,
                vy: Math.sin(angle) * velocity,
                size: Math.random() * 3 + 2,
                alpha: 1,
                life: 100,
                decay: true
            });
        }
    }

    // Ripple effect
    createRipple(e) {
        const ripple = document.createElement('div');
        ripple.className = 'ripple';
        
        const size = 100;
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = (e.clientX - size / 2) + 'px';
        ripple.style.top = (e.clientY - size / 2) + 'px';
        
        document.body.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    // Quick create functionality
    quickCreate() {
        // TODO: Implement quick create modal
        this.showMessage('Quick create feature coming soon!', 'system');
        
        // Animate FAB
        this.fabButton.style.transform = 'scale(0.8)';
        setTimeout(() => {
            this.fabButton.style.transform = '';
        }, 200);
    }

    // Utility functions
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.devPromptStudio = new DevPromptStudio();
});

// Handle visibility change to pause/resume animations
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pause intensive animations
    } else {
        // Resume animations
    }
});