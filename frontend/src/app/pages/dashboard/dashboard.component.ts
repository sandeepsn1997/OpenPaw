import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

interface StatCard {
  icon: string;
  label: string;
  value: string;
  color: string;
  trend?: string;
}

interface ActivityItem {
  icon: string;
  text: string;
  time: string;
  color: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="page-container">
      <div class="page-header">
        <h1>Dashboard</h1>
        <p>Welcome to OpenPaw — your AI agent command center</p>
      </div>

      <!-- Stats -->
      <div class="stats-grid">
        @for (stat of stats(); track stat.label) {
          <div class="stat-card" [class]="stat.color">
            <div class="stat-icon" [class]="stat.color">
              <span class="material-symbols-rounded">{{ stat.icon }}</span>
            </div>
            <div class="stat-info">
              <h3>{{ stat.value }}</h3>
              <p>{{ stat.label }}</p>
            </div>
          </div>
        }
      </div>

      <div class="dashboard-grid">
        <!-- Quick Actions -->
        <div class="card quick-actions">
          <h2 class="section-title">
            <span class="material-symbols-rounded">bolt</span>
            Quick Actions
          </h2>
          <div class="actions-grid">
            <a routerLink="/chat" class="action-card">
              <div class="action-icon blue">
                <span class="material-symbols-rounded">add_comment</span>
              </div>
              <span>New Chat</span>
            </a>
            <a routerLink="/knowledge" class="action-card">
              <div class="action-icon teal">
                <span class="material-symbols-rounded">upload_file</span>
              </div>
              <span>Upload Knowledge</span>
            </a>
            <a routerLink="/tasks" class="action-card">
              <div class="action-icon amber">
                <span class="material-symbols-rounded">add_task</span>
              </div>
              <span>New Task</span>
            </a>
            <a routerLink="/skills" class="action-card">
              <div class="action-icon purple">
                <span class="material-symbols-rounded">extension</span>
              </div>
              <span>Manage Skills</span>
            </a>
          </div>
        </div>

        <!-- System Status -->
        <div class="card system-status">
          <h2 class="section-title">
            <span class="material-symbols-rounded">monitor_heart</span>
            System Status
          </h2>
          <div class="status-items">
            <div class="status-row">
              <div class="status-dot online"></div>
              <span class="status-label">Backend API</span>
              <span class="badge badge-emerald">{{ backendStatus() }}</span>
            </div>
            <div class="status-row">
              <div class="status-dot online"></div>
              <span class="status-label">LLM Provider</span>
              <span class="badge badge-emerald">Groq</span>
            </div>
            <div class="status-row">
              <div class="status-dot online"></div>
              <span class="status-label">Database</span>
              <span class="badge badge-emerald">SQLite</span>
            </div>
            <div class="status-row">
              <div class="status-dot" [class.online]="vectorDbOnline()" [class.offline]="!vectorDbOnline()"></div>
              <span class="status-label">Vector Store</span>
              <span class="badge" [class.badge-emerald]="vectorDbOnline()" [class.badge-rose]="!vectorDbOnline()">
                {{ vectorDbOnline() ? 'FAISS' : 'Not Configured' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="card activity-feed">
          <h2 class="section-title">
            <span class="material-symbols-rounded">history</span>
            Recent Activity
          </h2>
          @if (activities().length === 0) {
            <div class="empty-state" style="padding: 30px 10px;">
              <span class="material-symbols-rounded" style="font-size: 36px;">event_note</span>
              <p>No recent activity</p>
            </div>
          } @else {
            <div class="activity-list">
              @for (activity of activities(); track activity.text) {
                <div class="activity-item">
                  <div class="activity-icon" [class]="activity.color">
                    <span class="material-symbols-rounded">{{ activity.icon }}</span>
                  </div>
                  <div class="activity-text">
                    <p>{{ activity.text }}</p>
                    <small>{{ activity.time }}</small>
                  </div>
                </div>
              }
            </div>
          }
        </div>

        <!-- Model Info -->
        <div class="card model-info">
          <h2 class="section-title">
            <span class="material-symbols-rounded">psychology</span>
            Active Model
          </h2>
          <div class="model-card-inner">
            <div class="model-name">
              <span class="material-symbols-rounded" style="font-size: 28px; color: var(--accent-primary);">smart_toy</span>
              <div>
                <h3>llama-3.3-70b</h3>
                <p>versatile • via Groq</p>
              </div>
            </div>
            <div class="model-specs">
              <div class="spec">
                <span class="spec-label">Temperature</span>
                <span class="spec-value">0.7</span>
              </div>
              <div class="spec">
                <span class="spec-label">Max Tokens</span>
                <span class="spec-value">2,000</span>
              </div>
              <div class="spec">
                <span class="spec-label">Provider</span>
                <span class="spec-value">Groq Cloud</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 1rem;
      font-weight: 600;
      color: var(--text-secondary);
      margin-bottom: 20px;
    }

    .section-title .material-symbols-rounded {
      font-size: 20px;
      color: var(--text-tertiary);
    }

    /* Quick Actions */
    .actions-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    .action-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      padding: 20px 12px;
      background: var(--bg-surface);
      border: 1px solid var(--border-primary);
      border-radius: var(--radius-md);
      color: var(--text-secondary);
      font-size: 0.82rem;
      font-weight: 500;
      transition: all var(--transition-fast);
      text-decoration: none;
      cursor: pointer;
    }

    .action-card:hover {
      background: var(--bg-card-hover);
      border-color: var(--border-secondary);
      color: var(--text-primary);
      transform: translateY(-2px);
    }

    .action-icon {
      width: 42px;
      height: 42px;
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .action-icon.blue { background: var(--accent-primary-dim); color: var(--accent-primary); }
    .action-icon.purple { background: var(--accent-secondary-dim); color: var(--accent-secondary); }
    .action-icon.teal { background: var(--accent-teal-dim); color: var(--accent-teal); }
    .action-icon.amber { background: var(--accent-amber-dim); color: var(--accent-amber); }

    /* System Status */
    .status-items {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .status-row {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .status-dot.online {
      background: var(--accent-emerald);
      box-shadow: 0 0 8px rgba(52, 211, 153, 0.4);
    }

    .status-dot.offline {
      background: var(--text-muted);
    }

    .status-label {
      flex: 1;
      font-size: 0.875rem;
      color: var(--text-secondary);
    }

    /* Activity Feed */
    .activity-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .activity-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }

    .activity-icon {
      width: 32px;
      height: 32px;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .activity-icon .material-symbols-rounded { font-size: 16px; }
    .activity-icon.blue { background: var(--accent-primary-dim); color: var(--accent-primary); }
    .activity-icon.teal { background: var(--accent-teal-dim); color: var(--accent-teal); }
    .activity-icon.purple { background: var(--accent-secondary-dim); color: var(--accent-secondary); }

    .activity-text p {
      font-size: 0.85rem;
      color: var(--text-secondary);
    }

    .activity-text small {
      color: var(--text-muted);
      font-size: 0.75rem;
    }

    /* Model Info */
    .model-card-inner {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .model-name {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .model-name h3 {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--text-primary);
    }

    .model-name p {
      font-size: 0.8rem;
      color: var(--text-tertiary);
    }

    .model-specs {
      display: flex;
      gap: 20px;
    }

    .spec {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .spec-label {
      font-size: 0.72rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 600;
    }

    .spec-value {
      font-size: 0.9rem;
      color: var(--text-primary);
      font-weight: 500;
    }

    @media (max-width: 900px) {
      .dashboard-grid {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class DashboardComponent implements OnInit {
  stats = signal<StatCard[]>([
    { icon: 'forum', label: 'Conversations', value: '—', color: 'blue' },
    { icon: 'extension', label: 'Skills', value: '—', color: 'teal' },
    { icon: 'neurology', label: 'Knowledge Docs', value: '—', color: 'amber' },
  ]);

  backendStatus = signal('Online');
  vectorDbOnline = signal(false);
  activities = signal<ActivityItem[]>([]);

  ngOnInit(): void {
    this.loadStats();
  }

  async loadStats(): Promise<void> {
    try {
      // Check health
      const healthRes = await fetch('/api/health');
      if (healthRes.ok) {
        this.backendStatus.set('Online');
      } else {
        this.backendStatus.set('Degraded');
      }

      // Fetch stats
      const statsRes = await fetch('/api/dashboard/stats');
      if (statsRes.ok) {
        const data = await statsRes.json();
        this.stats.set([
          { icon: 'forum', label: 'Conversations', value: data.conversations_count.toString(), color: 'blue' },
          { icon: 'extension', label: 'Skills', value: data.skills_count.toString(), color: 'teal' },
          { icon: 'neurology', label: 'Knowledge Docs', value: data.docs_count.toString(), color: 'amber' },
        ]);
        this.vectorDbOnline.set(data.docs_count > 0);
      }
    } catch {
      this.backendStatus.set('Offline');
    }
  }
}
