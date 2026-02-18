import { Component, signal, effect, ViewChild, ElementRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_used?: string;
  created_at: string;
}

interface ChatResponse {
  conversation_id: string;
  agent_id: string;
  message: ChatMessage;
  reply: string;
  messages: ChatMessage[];
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="chat-page">
      <!-- Conversations sidebar -->
      <div class="conv-sidebar" [class.open]="showConversations()">
        <div class="conv-header">
          <h3>Conversations</h3>
          <button class="btn-ghost" (click)="newConversation()" title="New Chat">
            <span class="material-symbols-rounded">add</span>
          </button>
        </div>
        <div class="conv-list">
          @if (conversations().length === 0) {
            <div class="conv-empty">
              <span class="material-symbols-rounded">chat_bubble_outline</span>
              <p>No conversations yet</p>
            </div>
          }
          @for (conv of conversations(); track conv.id) {
            <div class="conv-item" [class.active]="conv.id === conversationId()"
                 (click)="switchConversation(conv.id)">
              <span class="material-symbols-rounded" style="font-size: 18px;">chat</span>
              <div class="conv-info">
                <span class="conv-title">{{ conv.preview || 'New Chat' }}</span>
                <small>{{ conv.messageCount }} messages</small>
              </div>
              <button class="btn-icon delete-btn" (click)="$event.stopPropagation(); deleteConversation(conv.id)">
                <span class="material-symbols-rounded" style="font-size: 16px;">delete</span>
              </button>
            </div>
          }
        </div>
      </div>

      <!-- Main chat area -->
      <div class="chat-main">
        <!-- Chat header -->
        <div class="chat-header">
          <button class="btn-ghost mobile-toggle" (click)="toggleConversations()">
            <span class="material-symbols-rounded">menu</span>
          </button>
          <div class="chat-header-info">
            <h2>Chat Playground</h2>
            <span class="chat-status" [class.ready]="!loading()">
              <span class="status-indicator"></span>
              {{ loading() ? 'Thinking...' : 'Ready' }}
            </span>
          </div>
          <button class="btn btn-secondary" (click)="newConversation()" style="margin-left: auto;">
            <span class="material-symbols-rounded" style="font-size: 18px;">add</span>
            New Chat
          </button>
        </div>

        <!-- Messages area -->
        <div class="chat-messages" #messagesContainer>
          @if (messages().length === 0) {
            <div class="chat-welcome">
              <div class="welcome-icon">
                <span class="material-symbols-rounded">pets</span>
              </div>
              <h2>Hello! I'm OpenPaw</h2>
              <p>Ask me anything, or try one of the suggestions below</p>
              <div class="suggestions">
                <button class="suggestion-chip" (click)="sendSuggestion('What time is it?')">
                  🕐 What time is it?
                </button>
                <button class="suggestion-chip" (click)="sendSuggestion('Tell me about yourself')">
                  🤖 Tell me about yourself
                </button>
                <button class="suggestion-chip" (click)="sendSuggestion('What can you help me with?')">
                  💡 What can you help me with?
                </button>
              </div>
            </div>
          }

          @for (msg of messages(); track msg.id) {
            <div class="message" [class]="msg.role">
              <div class="msg-avatar">
                <span class="material-symbols-rounded">
                  {{ msg.role === 'user' ? 'person' : 'smart_toy' }}
                </span>
              </div>
              <div class="msg-body">
                <div class="msg-header">
                  <strong>{{ msg.role === 'user' ? 'You' : 'OpenPaw' }}</strong>
                  <small>{{ formatTime(msg.created_at) }}</small>
                </div>
                <div class="msg-content">{{ msg.content }}</div>
                @if (msg.tool_used) {
                  <span class="badge badge-blue" style="margin-top: 8px;">
                    <span class="material-symbols-rounded" style="font-size: 14px;">build</span>
                    {{ msg.tool_used }}
                  </span>
                }
              </div>
            </div>
          }

          @if (loading()) {
            <div class="message assistant">
              <div class="msg-avatar">
                <span class="material-symbols-rounded">smart_toy</span>
              </div>
              <div class="msg-body">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          }
        </div>

        <!-- Input area -->
        <div class="chat-input-area">
          @if (error()) {
            <div class="error-banner">
              <span class="material-symbols-rounded" style="font-size: 18px;">error</span>
              <span>{{ error() }}</span>
              <button class="btn-ghost" (click)="error.set(null)" style="padding: 2px;">
                <span class="material-symbols-rounded" style="font-size: 16px;">close</span>
              </button>
            </div>
          }
          <div class="input-row">
            <textarea class="input chat-textarea"
                      [(ngModel)]="messageText"
                      (keydown)="handleKeydown($event)"
                      placeholder="Type your message... (Ctrl+Enter to send)"
                      rows="1"
                      (input)="autoResize($event)"></textarea>
            <button class="btn btn-primary send-btn"
                    (click)="sendMessage()"
                    [disabled]="loading() || !messageText.trim()">
              <span class="material-symbols-rounded" style="font-size: 20px;">send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chat-page {
      display: flex;
      height: 100%;
      overflow: hidden;
    }

    /* ---- Conversation Sidebar ---- */
    .conv-sidebar {
      width: 280px;
      background: var(--bg-secondary);
      border-right: 1px solid var(--border-primary);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }

    .conv-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px;
      border-bottom: 1px solid var(--border-primary);
    }

    .conv-header h3 {
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-secondary);
    }

    .conv-list {
      flex: 1;
      overflow-y: auto;
      padding: 8px;
    }

    .conv-empty {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 40px 20px;
      color: var(--text-muted);
    }

    .conv-empty .material-symbols-rounded { font-size: 32px; opacity: 0.4; }
    .conv-empty p { font-size: 0.82rem; }

    .conv-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      color: var(--text-secondary);
      transition: all var(--transition-fast);
    }

    .conv-item:hover { background: var(--bg-surface); color: var(--text-primary); }
    .conv-item.active { background: var(--accent-primary-dim); color: var(--accent-primary); }

    .conv-info {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }

    .conv-title {
      font-size: 0.85rem;
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .conv-info small {
      font-size: 0.72rem;
      color: var(--text-muted);
    }

    .delete-btn {
      margin-left: auto;
      opacity: 0;
      color: var(--text-muted);
      padding: 4px !important;
    }

    .conv-item:hover .delete-btn {
      opacity: 1;
    }

    .delete-btn:hover {
      color: var(--status-error);
      background: rgba(239, 68, 68, 0.1) !important;
    }

    /* ---- Chat Main ---- */
    .chat-main {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-width: 0;
    }

    .chat-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 24px;
      border-bottom: 1px solid var(--border-primary);
      background: var(--bg-secondary);
    }

    .chat-header-info h2 {
      font-size: 1rem;
      font-weight: 600;
    }

    .chat-status {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .status-indicator {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--accent-amber);
    }

    .chat-status.ready .status-indicator {
      background: var(--accent-emerald);
      box-shadow: 0 0 6px rgba(52, 211, 153, 0.4);
    }

    .mobile-toggle { display: none; }

    /* ---- Messages ---- */
    .chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .chat-welcome {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      flex: 1;
      text-align: center;
      padding: 40px;
      animation: fadeIn 0.5s ease-out;
    }

    .welcome-icon {
      width: 72px;
      height: 72px;
      background: var(--gradient-primary);
      border-radius: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 20px;
      box-shadow: 0 8px 30px rgba(56, 189, 248, 0.2);
    }

    .welcome-icon .material-symbols-rounded {
      font-size: 36px;
      color: white;
      font-variation-settings: 'FILL' 1;
    }

    .chat-welcome h2 {
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 6px;
    }

    .chat-welcome p {
      color: var(--text-secondary);
      margin-bottom: 24px;
    }

    .suggestions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: center;
    }

    .suggestion-chip {
      padding: 10px 18px;
      background: var(--bg-card);
      border: 1px solid var(--border-secondary);
      border-radius: 100px;
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 0.85rem;
      cursor: pointer;
      transition: all var(--transition-fast);
    }

    .suggestion-chip:hover {
      background: var(--bg-card-hover);
      color: var(--text-primary);
      border-color: var(--accent-primary);
      transform: translateY(-1px);
    }

    /* Messages */
    .message {
      display: flex;
      gap: 12px;
      animation: fadeIn 0.3s ease-out;
      max-width: 800px;
    }

    .message.user {
      align-self: flex-end;
      flex-direction: row-reverse;
    }

    .msg-avatar {
      width: 34px;
      height: 34px;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      font-size: 18px;
    }

    .message.user .msg-avatar {
      background: var(--accent-primary-dim);
      color: var(--accent-primary);
    }

    .message.assistant .msg-avatar {
      background: var(--accent-secondary-dim);
      color: var(--accent-secondary);
    }

    .msg-body {
      display: flex;
      flex-direction: column;
    }

    .msg-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 4px;
    }

    .msg-header strong {
      font-size: 0.82rem;
      font-weight: 600;
    }

    .msg-header small {
      font-size: 0.72rem;
      color: var(--text-muted);
    }

    .msg-content {
      padding: 12px 16px;
      border-radius: var(--radius-md);
      font-size: 0.9rem;
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .message.user .msg-content {
      background: var(--accent-primary);
      color: white;
      border-top-right-radius: 4px;
    }

    .message.assistant .msg-content {
      background: var(--bg-card);
      border: 1px solid var(--border-primary);
      color: var(--text-primary);
      border-top-left-radius: 4px;
    }

    /* Typing indicator */
    .typing-indicator {
      display: flex;
      gap: 4px;
      padding: 16px;
      background: var(--bg-card);
      border: 1px solid var(--border-primary);
      border-radius: var(--radius-md);
      border-top-left-radius: 4px;
    }

    .typing-indicator span {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--text-muted);
      animation: typing 1.4s infinite ease-in-out;
    }

    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

    @keyframes typing {
      0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
      30% { transform: translateY(-6px); opacity: 1; }
    }

    /* ---- Input Area ---- */
    .chat-input-area {
      padding: 16px 24px 20px;
      border-top: 1px solid var(--border-primary);
      background: var(--bg-secondary);
    }

    .error-banner {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 14px;
      margin-bottom: 12px;
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.2);
      border-radius: var(--radius-sm);
      color: var(--accent-rose);
      font-size: 0.82rem;
    }

    .error-banner span:first-child { flex-shrink: 0; }
    .error-banner > span:nth-child(2) { flex: 1; }

    .input-row {
      display: flex;
      gap: 10px;
      align-items: flex-end;
    }

    .chat-textarea {
      flex: 1;
      max-height: 150px;
      min-height: 44px;
      line-height: 1.5;
      resize: none;
      overflow-y: auto;
    }

    .send-btn {
      width: 46px;
      height: 44px;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      border-radius: var(--radius-sm);
    }

    @media (max-width: 768px) {
      .conv-sidebar {
        position: absolute;
        left: -280px;
        top: 0;
        bottom: 0;
        z-index: 200;
        transition: left var(--transition-base);
      }

      .conv-sidebar.open { left: 0; }
      .mobile-toggle { display: flex; }
    }
  `]
})
export class ChatComponent implements OnInit {
  @ViewChild('messagesContainer') messagesContainer: ElementRef | null = null;

  messages = signal<ChatMessage[]>([]);
  messageText = '';
  loading = signal(false);
  error = signal<string | null>(null);
  conversationId = signal<string | null>(null);
  showConversations = signal(true);
  conversations = signal<{ id: string; preview: string; messageCount: number }[]>([]);

  constructor() {
    effect(() => {
      this.messages();
      setTimeout(() => this.scrollToBottom(), 100);
    });
  }

  ngOnInit(): void {
    this.initChat();
  }

  async initChat(): Promise<void> {
    try {
      this.loading.set(true);
      // Fetch existing conversations
      const res = await fetch('/api/chat/conversations');
      if (res.ok) {
        const data = await res.json();
        const mapped = data.map((c: any) => ({
          id: c.conversation_id,
          preview: c.messages && c.messages.length > 0 ? c.messages[c.messages.length - 1].content.substring(0, 40) : 'New Chat',
          messageCount: c.messages ? c.messages.length : 0
        }));
        this.conversations.set(mapped);

        if (mapped.length > 0) {
          // Switch to the most recent conversation (first in list)
          await this.switchConversation(mapped[0].id);
        } else {
          await this.newConversation();
        }
      } else {
        await this.newConversation();
      }
    } catch (err) {
      console.error('Failed to init chat history:', err);
      await this.newConversation();
    } finally {
      this.loading.set(false);
    }
  }

  async newConversation(): Promise<void> {
    try {
      const res = await fetch('/api/chat/conversations', { method: 'POST' });
      if (!res.ok) throw new Error('Failed to create conversation');
      const data = await res.json();
      this.conversationId.set(data.conversation_id);
      this.messages.set([]);
      this.messageText = '';
      this.error.set(null);

      // Add to conversation list
      const current = this.conversations();
      this.conversations.set([
        { id: data.conversation_id, preview: 'New Chat', messageCount: 0 },
        ...current,
      ]);
    } catch (err) {
      this.error.set(err instanceof Error ? err.message : 'Failed to create conversation');
    }
  }

  async switchConversation(id: string): Promise<void> {
    try {
      this.conversationId.set(id);
      const res = await fetch(`/api/chat/conversations/${id}`);
      if (!res.ok) throw new Error('Failed to load conversation');
      const data = await res.json();
      this.messages.set(data.messages || []);
    } catch (err) {
      this.error.set(err instanceof Error ? err.message : 'Failed to load conversation');
    }
  }

  async deleteConversation(id: string): Promise<void> {
    if (!confirm('Are you sure you want to delete this conversation?')) return;

    try {
      const res = await fetch(`/api/chat/conversations/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete conversation');

      // Remove from list
      const current = this.conversations();
      this.conversations.set(current.filter(c => c.id !== id));

      // If active conversation was deleted, create a new one or switch
      if (this.conversationId() === id) {
        const remaining = this.conversations();
        if (remaining.length > 0) {
          this.switchConversation(remaining[0].id);
        } else {
          this.newConversation();
        }
      }
    } catch (err) {
      this.error.set(err instanceof Error ? err.message : 'Failed to delete conversation');
    }
  }

  async sendMessage(): Promise<void> {
    if (!this.messageText.trim() || !this.conversationId()) return;

    const userMessage = this.messageText.trim();
    this.messageText = '';
    this.loading.set(true);
    this.error.set(null);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: this.conversationId(),
          message: userMessage,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || errorData.message || `Request failed: ${res.status}`);
      }

      const data = (await res.json()) as ChatResponse;
      this.messages.set(data.messages);

      // Update conversation preview
      const convs = this.conversations();
      const idx = convs.findIndex(c => c.id === this.conversationId());
      if (idx >= 0) {
        convs[idx].preview = userMessage.substring(0, 40);
        convs[idx].messageCount = data.messages.length;
        this.conversations.set([...convs]);
      }
    } catch (err) {
      this.error.set(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      this.loading.set(false);
    }
  }

  sendSuggestion(text: string): void {
    this.messageText = text;
    this.sendMessage();
  }

  handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && event.ctrlKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  autoResize(event: Event): void {
    const el = event.target as HTMLTextAreaElement;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 150) + 'px';
  }

  formatTime(dateStr: string): string {
    try {
      const d = new Date(dateStr);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  }

  toggleConversations(): void {
    this.showConversations.update(v => !v);
  }

  private scrollToBottom(): void {
    if (this.messagesContainer) {
      const el = this.messagesContainer.nativeElement;
      el.scrollTop = el.scrollHeight;
    }
  }
}
