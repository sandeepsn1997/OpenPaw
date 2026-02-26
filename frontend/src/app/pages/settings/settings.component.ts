import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface SkillSettingsField {
  key: string;
  label: string;
  type?: 'text' | 'password' | 'select' | 'action_qr';
  options?: { value: string; label: string }[];
  placeholder?: string;
  secret?: boolean;
  hint?: string;
  condition?: string; // e.g. "auth_type === 'callmebot'"
  action_label?: string;
  action_endpoint?: string;
  status_endpoint?: string;
  qr_endpoint?: string;
}

interface SkillSettings {
  id: string;
  title: string;
  description: string;
  setup_guide?: string;
  provider: string;
  auth?: {
    type: 'oauth2' | 'api_key';
    connectButton?: { endpoint: string; label: string };
    revokeButton?: { endpoint: string; label: string };
    saveEndpoint?: string;
    saveMethod?: string;
    statusEndpoint?: string;
    fields?: SkillSettingsField[];
  };
  actions?: string[];
  // Dynamic values for fields
  values: Record<string, any>;
  connected: boolean;
  statusInfo?: any;
  loading: boolean;
  qrImage?: string;
  linkStatus?: string;
}

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.css',
})
export class SettingsComponent implements OnInit {
  apiKey = signal('');
  apiKeyMasked = signal(true);
  model = signal('llama-3.3-70b-versatile');
  temperature = signal(0.7);
  maxTokens = signal(2000);
  theme = signal<'dark' | 'light'>('dark');
  saved = signal(false);

  skillSettings = signal<SkillSettings[]>([]);
  globalLoading = signal(false);

  models = [
    { value: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B — Versatile' },
    { value: 'llama-3.1-8b-instant', label: 'Llama 3.1 8B — Instant' },
    { value: 'openai/gpt-oss-120b', label: 'GPT OSS 120B' },
  ];

  ngOnInit(): void {
    this.loadAllSkillSettings();
  }

  async loadAllSkillSettings(): Promise<void> {
    this.globalLoading.set(true);
    try {
      const skillsRes = await fetch('/api/skills');
      if (!skillsRes.ok) return;
      const skills = await skillsRes.json();

      const settingsPromises = skills.map(async (skill: any) => {
        try {
          const res = await fetch(`/api/skills/${skill.id}/settings`);
          if (res.ok) {
            const settings = await res.json();
            return {
              ...settings,
              id: skill.id,
              values: {},
              connected: false,
              loading: false
            } as SkillSettings;
          }
        } catch { /* ignore skills without settings */ }
        return null;
      });

      const allSettings = (await Promise.all(settingsPromises)).filter(s => s !== null) as SkillSettings[];
      this.skillSettings.set(allSettings);

      // Load status for each
      for (const s of allSettings) {
        this.loadSkillStatus(s);
      }
    } finally {
      this.globalLoading.set(false);
    }
  }

  async loadSkillStatus(skill: SkillSettings): Promise<void> {
    const endpoint = skill.auth?.statusEndpoint;
    if (!endpoint) return;

    try {
      const res = await fetch(endpoint);
      if (!res.ok) return;
      const data = await res.json();

      this.skillSettings.update(skills => skills.map(s => {
        if (s.id === skill.id) {
          const updated = { ...s, connected: Boolean(data.connected), statusInfo: data };
          // If this is WhatsApp and using wa_web, check link status too
          if (s.id === 'whatsapp' && (data.provider_type === 'wa_web' || s.values['provider_type'] === 'wa_web')) {
            this.checkAndPollWhatsAppLink(updated);
          }
          return updated;
        }
        return s;
      }));
    } catch {
      this.skillSettings.update(skills => skills.map(s => {
        if (s.id === skill.id) return { ...s, connected: false };
        return s;
      }));
    }
  }

  async handleAuthAction(skill: SkillSettings): Promise<void> {
    if (skill.auth?.type === 'oauth2') {
      const endpoint = skill.auth.connectButton?.endpoint;
      if (!endpoint) return;

      this.setSkillLoading(skill, true);
      try {
        const res = await fetch(endpoint);
        const data = await res.json();
        if (data.auth_url) window.location.href = data.auth_url;
      } finally {
        this.setSkillLoading(skill, false);
      }
    } else if (skill.auth?.type === 'api_key') {
      this.saveSkillConfig(skill);
    }
  }

  async saveSkillConfig(skill: SkillSettings): Promise<void> {
    const endpoint = skill.auth?.saveEndpoint;
    if (!endpoint) return;

    this.setSkillLoading(skill, true);
    try {
      const res = await fetch(endpoint, {
        method: skill.auth?.saveMethod || 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(skill.values)
      });
      if (res.ok) {
        this.saved.set(true);
        setTimeout(() => this.saved.set(false), 2000);
        this.loadSkillStatus(skill);
      }
    } finally {
      this.setSkillLoading(skill, false);
    }
  }

  async revokeAccess(skill: SkillSettings): Promise<void> {
    const endpoint = skill.auth?.revokeButton?.endpoint;
    if (!endpoint) return;

    this.setSkillLoading(skill, true);
    try {
      await fetch(endpoint, { method: 'POST' });
      this.loadSkillStatus(skill);
    } finally {
      this.setSkillLoading(skill, false);
    }
  }

  private setSkillLoading(skill: SkillSettings, loading: boolean) {
    this.skillSettings.update(skills => skills.map(s => {
      if (s.id === skill.id) return { ...s, loading };
      return s;
    }));
  }

  onFieldChange(skillId: string, key: string, event: any) {
    const value = event.target.value;
    this.skillSettings.update(skills => skills.map(s => {
      if (s.id === skillId) {
        return { ...s, values: { ...s.values, [key]: value } };
      }
      return s;
    }));
  }

  checkCondition(field: SkillSettingsField, skill: SkillSettings): boolean {
    if (!field.condition) return true;

    // Simple parser for "key === 'value'" or "key !== 'value'" or composite "A && B"
    try {
      if (field.condition.includes('&&')) {
        return field.condition.split('&&').every(c => this.checkCondition({ ...field, condition: c.trim() }, skill));
      }

      const match = field.condition.match(/(\w+)\s+(===|!==)\s+'([^']+)'/);
      if (match) {
        const [_, key, op, val] = match;
        const actualValue = skill.values[key] || skill.statusInfo?.[key];
        if (op === '===') return actualValue === val;
        if (op === '!==') return actualValue !== val;
      }
    } catch (e) {
      console.error('Error parsing condition:', field.condition, e);
    }
    return true;
  }

  async triggerAction(field: SkillSettingsField, skill: SkillSettings) {
    if (!field.action_endpoint) return;

    try {
      skill.loading = true;
      await fetch(field.action_endpoint, { method: 'POST' });
      skill.linkStatus = 'starting';
      this.pollStatus(field, skill);
    } finally {
      skill.loading = false;
    }
  }

  private checkAndPollWhatsAppLink(skill: SkillSettings) {
    // Find the action_qr field to get endpoints
    const field = skill.auth?.fields?.find(f => f.type === 'action_qr');
    if (field) {
      if (skill.linkStatus !== 'connected' && skill.linkStatus !== 'error') {
        this.pollStatus(field, skill);
      }
    }
  }

  private pollStatus(field: SkillSettingsField, skill: SkillSettings) {
    if (!field.status_endpoint || !field.qr_endpoint) return;

    const poll = async () => {
      try {
        const res = await fetch(field.status_endpoint!);
        if (!res.ok) return;
        const data = await res.json();

        skill.linkStatus = data.status;

        if (data.is_connected) {
          skill.qrImage = undefined;
          skill.connected = true;
          // IMPORTANT: Update the signal so the UI reflects the change, but do NOT call loadSkillStatus
          // to avoid an infinite polling loop.
          this.skillSettings.update(skills => [...skills]);
          return;
        }

        if (data.status === 'qr_ready') {
          const qrRes = await fetch(field.qr_endpoint!);
          if (qrRes.ok) {
            const qrData = await qrRes.json();
            skill.qrImage = qrData.qr;
          }
        }

        // Continue polling if not connected and we are still viewing this provider
        const currentProvider = skill.values['provider_type'] || skill.statusInfo?.['provider_type'];
        if (!data.is_connected && currentProvider === 'wa_web') {
          setTimeout(poll, 3000);
        }
      } catch (e) {
        console.error("Polling error", e);
      }
    };

    poll();
  }


  toggleApiKeyVisibility(): void {
    this.apiKeyMasked.update(v => !v);
  }

  saveSettings(): void {
    this.saved.set(true);
    setTimeout(() => this.saved.set(false), 2000);
  }
}
