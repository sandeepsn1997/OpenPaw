import { Component, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface PersistentFile {
  filename: string;
  content: string;
}

@Component({
  selector: 'app-knowledge',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-container">
      <div class="page-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <h1>Knowledge & Memory</h1>
            <p>Manage both project documents and agentic persistence</p>
          </div>
          <button class="btn btn-primary" (click)="showUploadModal.set(true)">
            <span class="material-symbols-rounded" style="font-size: 18px;">upload_file</span>
            Upload Document
          </button>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tabs-container">
        <button class="tab-btn" [class.active]="activeTab() === 'memory'" (click)="activeTab.set('memory')">
          <span class="material-symbols-rounded">psychology</span>
          Persistent Memory
        </button>
        <button class="tab-btn" [class.active]="activeTab() === 'rag'" (click)="activeTab.set('rag')">
          <span class="material-symbols-rounded">library_books</span>
          RAG Documents
        </button>
      </div>

      <!-- TAB: Persistent Memory (Editor for soul.md, user_info.md, memory.md) -->
      @if (activeTab() === 'memory') {
        <div class="memory-layout">
          <div class="memory-sidebar">
            <div class="sidebar-label">Memory Files</div>
            @for (file of memoryFiles(); track file) {
              <div class="memory-file-item" 
                   [class.active]="selectedMemoryFile()?.filename === file"
                   (click)="loadMemoryFile(file)">
                <span class="material-symbols-rounded">description</span>
                {{ file.replace('.md', '').replace('_', ' ').toUpperCase() }}
              </div>
            }
          </div>
          
          <div class="memory-editor card">
            @if (selectedMemoryFile(); as file) {
              <div class="editor-header">
                <h3>Editing: {{ file.filename }}</h3>
                <div style="display: flex; gap: 8px;">
                  @if (saveStatus()) {
                    <span class="save-status">{{ saveStatus() }}</span>
                  }
                  <button class="btn btn-primary btn-sm" (click)="saveMemoryFile()">
                    <span class="material-symbols-rounded" style="font-size: 16px;">save</span>
                    Save Changes
                  </button>
                </div>
              </div>
              <textarea class="editor-area" [(ngModel)]="file.content" 
                        placeholder="Content of the memory file..."></textarea>
            } @else {
              <div class="editor-empty">
                <span class="material-symbols-rounded" style="font-size: 48px;">edit_note</span>
                <p>Select a memory file from the sidebar to view or edit its content.</p>
              </div>
            }
          </div>
        </div>
      }

      <!-- TAB: RAG Documents (Original Knowledge View) -->
      @if (activeTab() === 'rag') {
        <div class="rag-container">
          <!-- Search bar -->
          <div class="search-bar">
            <span class="material-symbols-rounded search-icon">search</span>
            <input class="input search-input" [(ngModel)]="searchQuery" placeholder="Search knowledge base..."
                   (input)="search()" />
          </div>

          <!-- Stats -->
          <div class="stats-grid" style="margin-top: 20px;">
            <div class="stat-card teal">
              <div class="stat-icon teal">
                <span class="material-symbols-rounded">description</span>
              </div>
              <div class="stat-info">
                <h3>{{ documents().length }}</h3>
                <p>Documents</p>
              </div>
            </div>
            <div class="stat-card purple">
              <div class="stat-icon purple">
                <span class="material-symbols-rounded">dataset</span>
              </div>
              <div class="stat-info">
                <h3>{{ totalChunks() }}</h3>
                <p>Indexed Chunks</p>
              </div>
            </div>
            <div class="stat-card blue">
              <div class="stat-icon blue">
                <span class="material-symbols-rounded">manage_search</span>
              </div>
              <div class="stat-info">
                <h3>{{ vectorStatus() }}</h3>
                <p>Vector Store</p>
              </div>
            </div>
          </div>

          <!-- Documents list -->
          @if (filteredDocs().length === 0 && documents().length === 0) {
            <div class="empty-state">
              <span class="material-symbols-rounded">library_books</span>
              <h3>No documents uploaded</h3>
              <p>Upload markdown or text files to build your knowledge base for RAG</p>
            </div>
          } @else {
            <div class="docs-list">
              @for (doc of filteredDocs(); track doc.id) {
                <div class="card doc-card">
                  <div class="doc-header">
                    <div class="doc-icon">
                      <span class="material-symbols-rounded">
                        {{ doc.type === '.md' ? 'markdown' : 'text_snippet' }}
                      </span>
                    </div>
                    <div class="doc-info">
                      <h3>{{ doc.title }}</h3>
                      <div class="doc-meta">
                        <span class="badge badge-teal">{{ doc.type }}</span>
                        <span>{{ doc.chunks }} chunks</span>
                        <span>{{ formatDate(doc.createdAt) }}</span>
                      </div>
                    </div>
                    <div class="doc-actions">
                      <button class="btn-ghost" (click)="viewDoc(doc)" title="View">
                        <span class="material-symbols-rounded" style="font-size: 18px;">visibility</span>
                      </button>
                      <button class="btn-ghost" (click)="deleteDoc(doc.id)" title="Delete">
                        <span class="material-symbols-rounded" style="font-size: 18px;">delete</span>
                      </button>
                    </div>
                  </div>
                  @if (selectedDoc()?.id === doc.id) {
                    <div class="doc-preview">
                      <pre>{{ doc.content }}</pre>
                    </div>
                  }
                </div>
              }
            </div>
          }
        </div>
      }

      <!-- Upload Modal (For RAG) -->
      @if (showUploadModal()) {
        <div class="modal-overlay" (click)="showUploadModal.set(false)">
          <div class="modal" (click)="$event.stopPropagation()">
            <div class="modal-header">
              <h2>Upload Document</h2>
              <button class="btn-ghost" (click)="showUploadModal.set(false)">
                <span class="material-symbols-rounded">close</span>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Title</label>
                <input class="input" [(ngModel)]="newDoc.title" placeholder="Document title" />
              </div>
              <div class="form-group">
                <label>Content (Markdown or plain text)</label>
                <textarea class="input" [(ngModel)]="newDoc.content" rows="10"
                          placeholder="Paste your knowledge content here..."></textarea>
              </div>
              <div class="form-group">
                <label>Type</label>
                <select class="input" [(ngModel)]="newDoc.type">
                  <option value=".md">Markdown (.md)</option>
                  <option value=".txt">Text (.txt)</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" (click)="showUploadModal.set(false)">Cancel</button>
              <button class="btn btn-primary" (click)="uploadDoc()" [disabled]="!newDoc.title.trim() || !newDoc.content.trim()">
                <span class="material-symbols-rounded" style="font-size: 18px;">upload</span>
                Upload
              </button>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .tabs-container {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      padding: 4px;
      background: var(--bg-secondary-dim);
      border-radius: var(--radius-md);
      width: fit-content;
    }

    .tab-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-size: 0.9rem;
      font-weight: 500;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all 0.2s;
    }

    .tab-btn:hover {
      color: var(--text-primary);
      background: var(--bg-hover);
    }

    .tab-btn.active {
      color: var(--accent-primary);
      background: var(--bg-secondary);
      box-shadow: var(--shadow-sm);
    }

    /* Memory Layout */
    .memory-layout {
      display: grid;
      grid-template-columns: 240px 1fr;
      gap: 24px;
      height: calc(100vh - 280px);
      min-height: 500px;
    }

    .memory-sidebar {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .sidebar-label {
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 0 8px 8px 8px;
    }

    .memory-file-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      border-radius: var(--radius-md);
      font-size: 0.88rem;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.2s;
    }

    .memory-file-item span { font-size: 18px; color: var(--text-muted); }

    .memory-file-item:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
    }

    .memory-file-item.active {
      background: var(--accent-primary-dim);
      color: var(--accent-primary);
      font-weight: 600;
    }

    .memory-file-item.active span { color: var(--accent-primary); }

    .memory-editor {
      display: flex;
      flex-direction: column;
      padding: 0;
      overflow: hidden;
    }

    .editor-header {
      display: flex;
      justify-content: space-between; align-items: center;
      padding: 16px 20px;
      border-bottom: 1px solid var(--border-primary);
      background: var(--bg-secondary-dim);
    }

    .editor-header h3 { font-size: 0.9rem; font-weight: 600; }

    .save-status {
      font-size: 0.8rem;
      color: var(--accent-emerald);
      align-self: center;
    }

    .editor-area {
      flex: 1;
      border: none;
      background: var(--bg-secondary);
      color: var(--text-primary);
      padding: 24px;
      font-family: 'DM Mono', monospace;
      font-size: 0.95rem;
      line-height: 1.6;
      resize: none;
      outline: none;
    }

    .editor-empty {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      flex: 1;
      color: var(--text-muted);
      gap: 16px;
    }

    /* RAG Styles */
    .search-bar { position: relative; }
    .search-icon {
      position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
      color: var(--text-muted); font-size: 20px;
    }
    .search-input { padding-left: 42px; }
    .docs-list { display: flex; flex-direction: column; gap: 12px; margin-top: 20px; }
    .doc-card { cursor: default; padding: 18px 24px; }
    .doc-header { display: flex; align-items: center; gap: 14px; }
    .doc-icon {
      width: 40px; height: 40px; background: var(--accent-teal-dim);
      color: var(--accent-teal); border-radius: var(--radius-md);
      display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .doc-info { flex: 1; min-width: 0; }
    .doc-info h3 { font-size: 0.95rem; font-weight: 600; margin-bottom: 4px; }
    .doc-meta { display: flex; align-items: center; gap: 12px; font-size: 0.78rem; color: var(--text-muted); }
    .doc-actions { display: flex; gap: 4px; }
    .doc-preview { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border-primary); }
    .doc-preview pre {
      font-size: 0.82rem; color: var(--text-tertiary); white-space: pre-wrap;
      line-height: 1.6; max-height: 200px; overflow-y: auto; font-family: 'Inter', sans-serif;
    }

    .btn-sm { padding: 6px 12px; font-size: 0.8rem; }

    /* Modal */
    .modal-overlay {
      position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
      display: flex; align-items: center; justify-content: center; z-index: 1000;
    }
    .modal {
      background: var(--bg-secondary); border: 1px solid var(--border-secondary);
      border-radius: var(--radius-lg); width: 600px; max-width: 95vw; box-shadow: var(--shadow-lg);
    }
    .modal-header {
      display: flex; justify-content: space-between; align-items: center;
      padding: 20px 24px; border-bottom: 1px solid var(--border-primary);
    }
    .modal-body { padding: 24px; display: flex; flex-direction: column; gap: 18px; }
    .modal-footer {
      display: flex; justify-content: flex-end; gap: 10px; padding: 16px 24px;
      border-top: 1px solid var(--border-primary);
    }
    .form-group { display: flex; flex-direction: column; gap: 6px; }
    .form-group label { font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); }
  `]
})
export class KnowledgeComponent implements OnInit {
  activeTab = signal<'memory' | 'rag'>('memory');

  // Memory signals
  memoryFiles = signal<string[]>([]);
  selectedMemoryFile = signal<PersistentFile | null>(null);
  saveStatus = signal('');

  // RAG signals
  documents = signal<any[]>([]);
  filteredDocs = signal<any[]>([]);
  selectedDoc = signal<any | null>(null);
  showUploadModal = signal(false);
  loading = signal(false);
  searchQuery = '';
  vectorStatus = signal('Ready');
  totalChunks = signal(0);
  newDoc = { title: '', content: '', type: '.md' };

  ngOnInit(): void {
    this.listMemoryFiles();
    this.loadDocs();
  }

  // --- MEMORY METHODS ---
  async listMemoryFiles(): Promise<void> {
    try {
      const res = await fetch('/api/knowledge/persistent');
      if (res.ok) {
        this.memoryFiles.set(await res.json());
      }
    } catch { /* ignore */ }
  }

  async loadMemoryFile(filename: string): Promise<void> {
    try {
      const res = await fetch(`/api/knowledge/persistent/${filename}`);
      if (res.ok) {
        this.selectedMemoryFile.set(await res.json());
        this.saveStatus.set('');
      }
    } catch { /* ignore */ }
  }

  async saveMemoryFile(): Promise<void> {
    const file = this.selectedMemoryFile();
    if (!file) return;

    try {
      this.saveStatus.set('Saving...');
      const res = await fetch(`/api/knowledge/persistent/${file.filename}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(file),
      });
      if (res.ok) {
        this.saveStatus.set('Saved!');
        setTimeout(() => this.saveStatus.set(''), 3000);
      } else {
        this.saveStatus.set('Error saving');
      }
    } catch {
      this.saveStatus.set('Error saving');
    }
  }

  // --- RAG METHODS ---
  async loadDocs(): Promise<void> {
    this.loading.set(true);
    try {
      const res = await fetch('/api/knowledge');
      if (res.ok) {
        const data = await res.json();
        this.documents.set(data);
        this.filteredDocs.set(data);
        this.totalChunks.set(data.reduce((acc: number, d: any) => acc + Math.ceil(d.content.length / 500), 0));
      }
    } catch { /* ignore */ }
    this.loading.set(false);
  }

  async search(): Promise<void> {
    if (!this.searchQuery.trim()) {
      this.filteredDocs.set(this.documents());
      return;
    }
    this.filteredDocs.set(this.documents().filter(d =>
      d.content.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
      d.title.toLowerCase().includes(this.searchQuery.toLowerCase())
    ));
  }

  viewDoc(doc: any): void {
    this.selectedDoc.set(this.selectedDoc()?.id === doc.id ? null : doc);
  }

  async uploadDoc(): Promise<void> {
    try {
      const formData = new FormData();
      formData.append('title', this.newDoc.title);
      formData.append('content', this.newDoc.content);
      formData.append('type', this.newDoc.type);

      const res = await fetch('/api/knowledge/upload', {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        this.loadDocs();
        this.showUploadModal.set(false);
        this.newDoc = { title: '', content: '', type: '.md' };
      }
    } catch { /* ignore */ }
  }

  async deleteDoc(id: string): Promise<void> {
    if (!confirm('Are you sure you want to delete this document?')) return;
    try {
      const res = await fetch(`/api/knowledge/${id}`, { method: 'DELETE' });
      if (res.ok) {
        this.loadDocs();
      }
    } catch { /* ignore */ }
  }

  formatDate(dateStr: string): string {
    try { return new Date(dateStr).toLocaleDateString(); } catch { return ''; }
  }
}
