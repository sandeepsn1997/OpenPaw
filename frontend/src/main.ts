import { bootstrapApplication } from '@angular/platform-browser';
import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface AgentResponse {
  reply: string;
  tool_used: string | null;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './styles.css'
})
class AppComponent {
  prompt = '';
  loading = signal(false);
  response = signal<AgentResponse | null>(null);
  error = signal<string | null>(null);

  async askAgent(): Promise<void> {
    if (!this.prompt.trim()) return;

    this.loading.set(true);
    this.error.set(null);

    try {
      const res = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: this.prompt })
      });

      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
      }

      this.response.set((await res.json()) as AgentResponse);
    } catch (err) {
      this.error.set(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      this.loading.set(false);
    }
  }
}

bootstrapApplication(AppComponent).catch((err) => console.error(err));
