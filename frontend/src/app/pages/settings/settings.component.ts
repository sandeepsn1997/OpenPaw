import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface GmailSkillSettings {
  title: string;
  description: string;
  auth?: {
    connectButton?: { endpoint: string; label: string };
    revokeButton?: { endpoint: string; label: string };
    statusEndpoint?: string;
  };
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

  gmailSettings = signal<GmailSkillSettings | null>(null);
  gmailConnected = signal(false);
  gmailEmail = signal('');
  gmailLoading = signal(false);

  models = [
    { value: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B — Versatile' },
    { value: 'llama-3.1-8b-instant', label: 'Llama 3.1 8B — Instant' },
    { value: 'openai/gpt-oss-120b', label: 'GPT OSS 120B' },
  ];

  ngOnInit(): void {
    this.loadGmailSkillSettings();
  }

  async loadGmailSkillSettings(): Promise<void> {
    try {
      const settingsRes = await fetch('/api/skills/email/settings');
      if (!settingsRes.ok) return;

      const settings = (await settingsRes.json()) as GmailSkillSettings;
      this.gmailSettings.set(settings);
      await this.loadGmailStatus();
    } catch {
      this.gmailSettings.set(null);
    }
  }

  async loadGmailStatus(): Promise<void> {
    const endpoint = this.gmailSettings()?.auth?.statusEndpoint;
    if (!endpoint) return;

    try {
      const res = await fetch(endpoint);
      if (!res.ok) return;
      const data = await res.json();
      this.gmailConnected.set(Boolean(data.connected));
      this.gmailEmail.set(data.email || '');
    } catch {
      this.gmailConnected.set(false);
      this.gmailEmail.set('');
    }
  }

  async connectGmail(): Promise<void> {
    const endpoint = this.gmailSettings()?.auth?.connectButton?.endpoint;
    if (!endpoint) return;

    this.gmailLoading.set(true);
    try {
      const res = await fetch(endpoint);
      if (!res.ok) return;
      const data = await res.json();
      if (data.auth_url) {
        window.location.href = data.auth_url;
      }
    } finally {
      this.gmailLoading.set(false);
    }
  }

  async revokeGmail(): Promise<void> {
    const endpoint = this.gmailSettings()?.auth?.revokeButton?.endpoint;
    if (!endpoint) return;

    this.gmailLoading.set(true);
    try {
      await fetch(endpoint, { method: 'POST' });
      this.gmailConnected.set(false);
      this.gmailEmail.set('');
    } finally {
      this.gmailLoading.set(false);
    }
  }

  toggleApiKeyVisibility(): void {
    this.apiKeyMasked.update(v => !v);
  }

  saveSettings(): void {
    this.saved.set(true);
    setTimeout(() => this.saved.set(false), 2000);
  }
}
