import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.css',
})
export class SettingsComponent {
  apiKey = signal('');
  apiKeyMasked = signal(true);
  model = signal('llama-3.3-70b-versatile');
  temperature = signal(0.7);
  maxTokens = signal(2000);
  theme = signal<'dark' | 'light'>('dark');
  saved = signal(false);

  models = [
    { value: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B — Versatile' },
    { value: 'llama-3.1-8b-instant', label: 'Llama 3.1 8B — Instant' },
    { value: 'openai/gpt-oss-120b', label: 'GPT OSS 120B' },
  ];

  toggleApiKeyVisibility(): void {
    this.apiKeyMasked.update(v => !v);
  }

  saveSettings(): void {
    this.saved.set(true);
    setTimeout(() => this.saved.set(false), 2000);
  }
}
