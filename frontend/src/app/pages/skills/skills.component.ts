import { Component, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface Skill {
  id: string;
  name: string;
  description: string;
  version: string;
  status: 'active' | 'inactive' | 'error';
  triggers: string[];
  executionCount: number;
  lastExecuted: string | null;
}

@Component({
  selector: 'app-skills',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-container">
      <div class="page-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <h1>Skills</h1>
            <p>Manage agent skills and plugins</p>
          </div>
          <button class="btn btn-primary" (click)="showCreateModal.set(true)">
            <span class="material-symbols-rounded" style="font-size: 18px;">add</span>
            Register Skill
          </button>
        </div>
      </div>

      <!-- Built-in skills -->
      <h3 class="section-label">Built-in Skills</h3>
      <div class="skills-grid">
        @for (skill of builtInSkills(); track skill.id) {
          <div class="card skill-card">
            <div class="skill-header">
              <div class="skill-icon" [class]="skill.status === 'active' ? 'emerald' : 'rose'">
                <span class="material-symbols-rounded">extension</span>
              </div>
              <div class="skill-title">
                <h3>{{ skill.name }}</h3>
                <span class="badge" [class]="skill.status === 'active' ? 'badge-emerald' : 'badge-rose'">
                  {{ skill.status }}
                </span>
              </div>
              <button class="btn-ghost toggle-btn"
                      (click)="toggleSkill(skill)"
                      [title]="skill.status === 'active' ? 'Deactivate' : 'Activate'">
                <span class="material-symbols-rounded">
                  {{ skill.status === 'active' ? 'toggle_on' : 'toggle_off' }}
                </span>
              </button>
            </div>
            <p class="skill-desc">{{ skill.description }}</p>
            <div class="skill-meta">
              <span class="badge badge-blue">v{{ skill.version }}</span>
              <span class="skill-stat">
                <span class="material-symbols-rounded" style="font-size: 14px;">play_arrow</span>
                {{ skill.executionCount }} runs
              </span>
            </div>
            @if (skill.triggers.length > 0) {
              <div class="skill-triggers">
                <span class="detail-label">Triggers</span>
                <div class="trigger-chips">
                  @for (trigger of skill.triggers; track trigger) {
                    <span class="trigger-chip">{{ trigger }}</span>
                  }
                </div>
              </div>
            }
          </div>
        }
      </div>

      @if (customSkills().length > 0) {
        <h3 class="section-label" style="margin-top: 28px;">Custom Skills</h3>
        <div class="skills-grid">
          @for (skill of customSkills(); track skill.id) {
            <div class="card skill-card">
              <div class="skill-header">
                <div class="skill-icon purple">
                  <span class="material-symbols-rounded">code</span>
                </div>
                <div class="skill-title">
                  <h3>{{ skill.name }}</h3>
                  <span class="badge badge-emerald">{{ skill.status }}</span>
                </div>
                <button class="btn-ghost" (click)="deleteSkill(skill.id)">
                  <span class="material-symbols-rounded" style="font-size: 18px;">delete</span>
                </button>
              </div>
              <p class="skill-desc">{{ skill.description }}</p>
            </div>
          }
        </div>
      }

      <!-- Create Modal -->
      @if (showCreateModal()) {
        <div class="modal-overlay" (click)="showCreateModal.set(false)">
          <div class="modal" (click)="$event.stopPropagation()">
            <div class="modal-header">
              <h2>Register Skill</h2>
              <button class="btn-ghost" (click)="showCreateModal.set(false)">
                <span class="material-symbols-rounded">close</span>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Skill Name</label>
                <input class="input" [(ngModel)]="newSkill.name" placeholder="my-custom-skill" />
              </div>
              <div class="form-group">
                <label>Description</label>
                <textarea class="input" [(ngModel)]="newSkill.description" rows="2"
                          placeholder="What does this skill do?"></textarea>
              </div>
              <div class="form-group">
                <label>Trigger Phrases (comma separated)</label>
                <input class="input" [(ngModel)]="newSkill.triggersStr" placeholder="search, lookup, find" />
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" (click)="showCreateModal.set(false)">Cancel</button>
              <button class="btn btn-primary" (click)="registerSkill()" [disabled]="!newSkill.name.trim()">
                <span class="material-symbols-rounded" style="font-size: 18px;">check</span>
                Register
              </button>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .section-label {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 14px;
    }

    .skills-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 16px;
    }

    .skill-card { cursor: default; }

    .skill-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
    }

    .skill-icon {
      width: 40px;
      height: 40px;
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .skill-icon.emerald { background: var(--accent-emerald-dim); color: var(--accent-emerald); }
    .skill-icon.rose { background: var(--accent-rose-dim); color: var(--accent-rose); }
    .skill-icon.purple { background: var(--accent-secondary-dim); color: var(--accent-secondary); }

    .skill-title {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .skill-title h3 { font-size: 0.95rem; font-weight: 600; }

    .toggle-btn .material-symbols-rounded { font-size: 28px; }

    .skill-desc {
      font-size: 0.82rem;
      color: var(--text-tertiary);
      line-height: 1.5;
      margin-bottom: 14px;
    }

    .skill-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
    }

    .skill-stat {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 0.78rem;
      color: var(--text-muted);
    }

    .skill-triggers {
      padding-top: 12px;
      border-top: 1px solid var(--border-primary);
    }

    .detail-label {
      font-size: 0.72rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      font-weight: 600;
    }

    .trigger-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }

    .trigger-chip {
      padding: 3px 10px;
      background: var(--bg-surface);
      border: 1px solid var(--border-primary);
      border-radius: 100px;
      font-size: 0.75rem;
      color: var(--text-secondary);
    }

    /* Reuse modal styles from agents */
    .modal-overlay {
      position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
      display: flex; align-items: center; justify-content: center; z-index: 1000; animation: fadeIn 0.2s;
    }
    .modal {
      background: var(--bg-secondary); border: 1px solid var(--border-secondary);
      border-radius: var(--radius-lg); width: 520px; max-width: 95vw; box-shadow: var(--shadow-lg);
    }
    .modal-header {
      display: flex; justify-content: space-between; align-items: center;
      padding: 20px 24px; border-bottom: 1px solid var(--border-primary);
    }
    .modal-header h2 { font-size: 1.1rem; font-weight: 600; }
    .modal-body { padding: 24px; display: flex; flex-direction: column; gap: 18px; }
    .modal-footer {
      display: flex; justify-content: flex-end; gap: 10px; padding: 16px 24px;
      border-top: 1px solid var(--border-primary);
    }
    .form-group { display: flex; flex-direction: column; gap: 6px; }
    .form-group label { font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); }
  `]
})
export class SkillsComponent implements OnInit {
  builtInSkills = signal<any[]>([]);
  customSkills = signal<any[]>([]);
  showCreateModal = signal(false);
  loading = signal(false);
  newSkill = { name: '', description: '', triggersStr: '' };

  ngOnInit(): void {
    this.loadSkills();
  }

  async loadSkills(): Promise<void> {
    this.loading.set(true);
    try {
      const res = await fetch('/api/skills');
      if (res.ok) {
        const data = await res.json();
        // Separate built-in vs custom (for now we assume all from API are custom unless we have a flag)
        // Let's just group them all under Built-in if they are the standard ones
        this.builtInSkills.set(data.filter((s: any) => ['time', 'echo'].includes(s.name.toLowerCase())));
        this.customSkills.set(data.filter((s: any) => !['time', 'echo'].includes(s.name.toLowerCase())));
      }
    } catch { /* ignore */ }
    this.loading.set(false);
  }

  async toggleSkill(skill: any): Promise<void> {
    // Backend toggle not implemented yet, just UI update for now
    skill.status = skill.status === 'active' ? 'inactive' : 'active';
  }

  async registerSkill(): Promise<void> {
    try {
      const triggers = this.newSkill.triggersStr.split(',').map(s => s.trim()).filter(Boolean);
      const res = await fetch('/api/skills/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: this.newSkill.name,
          description: this.newSkill.description,
          version: '1.0.0',
          triggers: triggers,
        }),
      });
      if (res.ok) {
        this.loadSkills();
        this.showCreateModal.set(false);
        this.newSkill = { name: '', description: '', triggersStr: '' };
      }
    } catch { /* ignore */ }
  }

  async deleteSkill(id: string): Promise<void> {
    // Backend DELETE skills not strictly in the router yet, but we can assume it follows pattern
    // For now we'll just refresh list if we had a delete endpoint
    this.customSkills.update(list => list.filter(s => s.id !== id));
  }
}
