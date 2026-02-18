import { Component, signal } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

interface NavItem {
  icon: string;
  label: string;
  route: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="app-shell" [class.sidebar-collapsed]="sidebarCollapsed()">
      <!-- Sidebar -->
      <aside class="sidebar">
        <!-- Logo -->
        <div class="sidebar-logo">
          <div class="logo-icon">
            <span class="material-symbols-rounded">pets</span>
          </div>
          <span class="logo-text">OpenPaw</span>
          <button class="collapse-btn" (click)="toggleSidebar()">
            <span class="material-symbols-rounded">
              {{ sidebarCollapsed() ? 'chevron_right' : 'chevron_left' }}
            </span>
          </button>
        </div>

        <!-- Navigation -->
        <nav class="sidebar-nav">
          @for (item of navItems; track item.route) {
            <a class="nav-item"
               [routerLink]="item.route"
               routerLinkActive="active"
               [title]="item.label">
              <span class="material-symbols-rounded nav-icon">{{ item.icon }}</span>
              <span class="nav-label">{{ item.label }}</span>
            </a>
          }
        </nav>

        <!-- Sidebar footer -->
        <div class="sidebar-footer">
          <div class="sidebar-version">
            <span class="material-symbols-rounded" style="font-size: 16px;">info</span>
            <span class="nav-label">v0.1.0</span>
          </div>
        </div>
      </aside>

      <!-- Main content -->
      <main class="main-content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [`
    .app-shell {
      display: flex;
      height: 100vh;
      overflow: hidden;
    }

    /* ---- Sidebar ---- */
    .sidebar {
      width: var(--sidebar-width);
      height: 100vh;
      background: var(--bg-secondary);
      border-right: 1px solid var(--border-primary);
      display: flex;
      flex-direction: column;
      transition: width var(--transition-base);
      position: relative;
      z-index: 100;
      flex-shrink: 0;
    }

    .sidebar-collapsed .sidebar {
      width: var(--sidebar-collapsed);
    }

    /* Logo */
    .sidebar-logo {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 20px 16px;
      border-bottom: 1px solid var(--border-primary);
      min-height: 68px;
    }

    .logo-icon {
      width: 38px;
      height: 38px;
      background: var(--gradient-primary);
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .logo-icon .material-symbols-rounded {
      font-size: 22px;
      color: white;
      font-variation-settings: 'FILL' 1;
    }

    .logo-text {
      font-size: 1.2rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      background: var(--gradient-primary);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      white-space: nowrap;
      overflow: hidden;
    }

    .sidebar-collapsed .logo-text,
    .sidebar-collapsed .nav-label,
    .sidebar-collapsed .sidebar-version .nav-label {
      display: none;
    }

    .collapse-btn {
      margin-left: auto;
      background: none;
      border: none;
      color: var(--text-tertiary);
      cursor: pointer;
      padding: 4px;
      border-radius: var(--radius-sm);
      transition: all var(--transition-fast);
      display: flex;
      align-items: center;
    }

    .collapse-btn:hover {
      background: var(--bg-surface);
      color: var(--text-primary);
    }

    .sidebar-collapsed .collapse-btn {
      margin-left: 0;
    }

    /* Navigation */
    .sidebar-nav {
      flex: 1;
      padding: 12px 10px;
      display: flex;
      flex-direction: column;
      gap: 2px;
      overflow-y: auto;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 11px 14px;
      border-radius: var(--radius-sm);
      color: var(--text-secondary);
      font-size: 0.9rem;
      font-weight: 500;
      transition: all var(--transition-fast);
      text-decoration: none;
      position: relative;
      white-space: nowrap;
      overflow: hidden;
    }

    .nav-item:hover {
      background: var(--bg-surface);
      color: var(--text-primary);
    }

    .nav-item.active {
      background: var(--accent-primary-dim);
      color: var(--accent-primary);
    }

    .nav-item.active::before {
      content: '';
      position: absolute;
      left: 0;
      top: 6px;
      bottom: 6px;
      width: 3px;
      background: var(--accent-primary);
      border-radius: 0 3px 3px 0;
    }

    .nav-icon {
      flex-shrink: 0;
      font-size: 21px;
    }

    .nav-item.active .nav-icon {
      font-variation-settings: 'FILL' 1;
    }

    /* Footer */
    .sidebar-footer {
      padding: 12px 10px;
      border-top: 1px solid var(--border-primary);
    }

    .sidebar-version {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 14px;
      color: var(--text-muted);
      font-size: 0.78rem;
      font-weight: 500;
    }

    /* ---- Main Content ---- */
    .main-content {
      flex: 1;
      overflow: hidden;
      background: var(--bg-primary);
    }
  `]
})
export class AppComponent {
  sidebarCollapsed = signal(false);

  navItems: NavItem[] = [
    { icon: 'dashboard', label: 'Dashboard', route: '/dashboard' },
    { icon: 'chat', label: 'Chat', route: '/chat' },
    { icon: 'extension', label: 'Skills', route: '/skills' },
    { icon: 'neurology', label: 'Knowledge Base', route: '/knowledge' },
    { icon: 'task_alt', label: 'Tasks', route: '/tasks' },
    { icon: 'settings', label: 'Settings', route: '/settings' },
  ];

  toggleSidebar(): void {
    this.sidebarCollapsed.update(v => !v);
  }
}
