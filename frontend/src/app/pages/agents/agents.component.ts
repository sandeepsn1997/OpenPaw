import { Component, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface Agent {
  id: string;
  name: string;
  model: string;
  state: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
  createdAt: string;
}

@Component({
  selector: 'app-agents',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-container">
      <div class="page-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <h1>Agents</h1>
            <p>Create and manage your AI agents</p>
          </div>
          <button class="btn btn-primary" (click)="showCreateModal.set(true)">
            <span class="material-symbols-rounded" style="font-size: 18px;">add</span>
            Create Agent
          </button>
        </div>
      </div>

      @if (agents().length === 0) {
        <div class="empty-state">
          <span class="material-symbols-rounded">smart_toy</span>
          <h3>No agents yet</h3>
          <p>Create your first AI agent to get started with autonomous tasks</p>
          <button class="btn btn-primary" style="margin-top: 16px;" (click)="showCreateModal.set(true)">
            <span class="material-symbols-rounded" style="font-size: 18px;">add</span>
            Create Agent
          </button>
        </div>
      } @else {
        <div class="agents-grid">
          @for (agent of agents(); track agent.id) {
            <div class="card agent-card">
              <div class="agent-header">
                <div class="agent-avatar">
                  <span class="material-symbols-rounded">smart_toy</span>
                </div>
                <div class="agent-title">
                  <h3>{{ agent.name }}</h3>
                  <span class="badge" [class]="agent.state === 'idle' ? 'badge-emerald' : 'badge-amber'">
                    {{ agent.state }}
                  </span>
                </div>
                <button class="btn-ghost" (click)="deleteAgent(agent.id)">
                  <span class="material-symbols-rounded" style="font-size: 18px;">delete</span>
                </button>
              </div>
              <div class="agent-details">
                <div class="detail-row">
                  <span class="detail-label">Model</span>
                  <span class="detail-value">{{ agent.config.model_name }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Temperature</span>
                  <span class="detail-value">{{ agent.config.temperature }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Max Tokens</span>
                  <span class="detail-value">{{ agent.config.max_tokens }}</span>
                </div>
              </div>
              <div class="agent-prompt">
                <span class="detail-label">System Prompt</span>
                <p>{{ agent.config.system_prompt }}</p>
              </div>
            </div>
          }
        </div>
      }

      <!-- Create Modal -->
      @if (showCreateModal()) {
        <div class="modal-overlay" (click)="showCreateModal.set(false)">
          <div class="modal" (click)="$event.stopPropagation()">
            <div class="modal-header">
              <h2>Create Agent</h2>
              <button class="btn-ghost" (click)="showCreateModal.set(false)">
                <span class="material-symbols-rounded">close</span>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Agent Name</label>
                <input class="input" [(ngModel)]="newAgent.name" placeholder="My AI Agent" />
              </div>
              <div class="form-group">
                <label>Model</label>
                <select class="input" [(ngModel)]="newAgent.config.model_name">
                  <option value="llama-3.3-70b-versatile">Llama 3.3 70B (Versatile)</option>
                  <option value="llama-3.1-8b-instant">Llama 3.1 8B (Instant)</option>
                  <option value="openai/gpt-oss-120b">GPT OSS 120B</option>
                </select>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Temperature</label>
                  <input class="input" type="number" [(ngModel)]="newAgent.config.temperature" min="0" max="2" step="0.1" />
                </div>
                <div class="form-group">
                  <label>Max Tokens</label>
                  <input class="input" type="number" [(ngModel)]="newAgent.config.max_tokens" min="1" max="32768" />
                </div>
              </div>
              <div class="form-group">
                <label>System Prompt</label>
                <textarea class="input" [(ngModel)]="newAgent.config.system_prompt" rows="3"
                          placeholder="You are a helpful AI assistant."></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" (click)="showCreateModal.set(false)">Cancel</button>
              <button class="btn btn-primary" (click)="createAgent()" [disabled]="!newAgent.name.trim()">
                <span class="material-symbols-rounded" style="font-size: 18px;">check</span>
                Create
              </button>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .agents-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 20px;
    }

    .agent-card { cursor: default; }

    .agent-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 18px;
    }

    .agent-avatar {
      width: 42px;
      height: 42px;
      background: var(--accent-secondary-dim);
      color: var(--accent-secondary);
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .agent-title {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .agent-title h3 {
      font-size: 1rem;
      font-weight: 600;
    }

    .agent-details {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 14px;
    }

    .detail-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .detail-label {
      font-size: 0.78rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      font-weight: 600;
    }

    .detail-value {
      font-size: 0.85rem;
      color: var(--text-secondary);
      font-weight: 500;
    }

    .agent-prompt {
      padding-top: 14px;
      border-top: 1px solid var(--border-primary);
    }

    .agent-prompt p {
      margin-top: 6px;
      font-size: 0.82rem;
      color: var(--text-tertiary);
      line-height: 1.5;
    }

    /* Modal */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      animation: fadeIn 0.2s;
    }

    .modal {
      background: var(--bg-secondary);
      border: 1px solid var(--border-secondary);
      border-radius: var(--radius-lg);
      width: 520px;
      max-width: 95vw;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: var(--shadow-lg);
    }

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 24px;
      border-bottom: 1px solid var(--border-primary);
    }

    .modal-header h2 {
      font-size: 1.1rem;
      font-weight: 600;
    }

    .modal-body {
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .modal-footer {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      padding: 16px 24px;
      border-top: 1px solid var(--border-primary);
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .form-group label {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-secondary);
    }

    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    select.input {
      appearance: none;
      cursor: pointer;
    }
  `]
})
export class AgentsComponent implements OnInit {
  agents = signal<any[]>([]);
  showCreateModal = signal(false);
  loading = signal(false);

  newAgent = {
    name: '',
    config: {
      model_name: 'llama-3.3-70b-versatile',
      temperature: 0.7,
      max_tokens: 2000,
      system_prompt: 'You are a helpful AI assistant.',
    }
  };

  ngOnInit(): void {
    this.loadAgents();
  }

  async loadAgents(): Promise<void> {
    this.loading.set(true);
    try {
      const res = await fetch('/api/agents');
      if (res.ok) {
        this.agents.set(await res.json());
      }
    } catch { /* ignore */ }
    this.loading.set(false);
  }

  async createAgent(): Promise<void> {
    try {
      const res = await fetch(`/api/agents?name=${encodeURIComponent(this.newAgent.name)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.newAgent.config),
      });
      if (res.ok) {
        this.loadAgents();
        this.showCreateModal.set(false);
        this.newAgent.name = '';
      }
    } catch { /* ignore */ }
  }

  async deleteAgent(id: string): Promise<void> {
    if (!confirm('Are you sure you want to delete this agent?')) return;
    try {
      const res = await fetch(`/api/agents/${id}`, { method: 'DELETE' });
      if (res.ok) {
        this.loadAgents();
      }
    } catch { /* ignore */ }
  }
}
