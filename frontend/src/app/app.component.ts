import { Component, signal, HostListener } from '@angular/core';
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
    <div class="app-shell" [class.sidebar-collapsed]="sidebarCollapsed()" [class.mobile-open]="mobileMenuOpen()">
      <!-- Mobile overlay -->
      <div class="mobile-overlay" (click)="closeMobileMenu()"></div>

      <!-- Sidebar -->
      <aside class="sidebar">
        <!-- Logo -->
        <div class="sidebar-logo">
          <div class="logo-icon">
            <span class="material-symbols-rounded">pets</span>
          </div>
          <span class="logo-text">OpenPaw</span>
          <button class="collapse-btn desktop-only" (click)="toggleSidebar()">
            <span class="material-symbols-rounded">
              {{ sidebarCollapsed() ? 'chevron_right' : 'chevron_left' }}
            </span>
          </button>
          <button class="collapse-btn mobile-only" (click)="closeMobileMenu()">
            <span class="material-symbols-rounded">close</span>
          </button>
        </div>

        <!-- Navigation -->
        <nav class="sidebar-nav">
          @for (item of navItems; track item.route) {
            <a class="nav-item"
               [routerLink]="item.route"
               routerLinkActive="active"
               [title]="item.label"
               (click)="onNavClick()">
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
        <!-- Mobile top bar -->
        <div class="mobile-topbar">
          <button class="mobile-hamburger" (click)="openMobileMenu()">
            <span class="material-symbols-rounded">menu</span>
          </button>
          <div class="mobile-logo">
            <div class="logo-icon small">
              <span class="material-symbols-rounded">pets</span>
            </div>
            <span class="logo-text">OpenPaw</span>
          </div>
          <div class="mobile-spacer"></div>
        </div>
        <div class="main-content-inner">
          <router-outlet></router-outlet>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .app-shell {
      display: flex;
      height: 100vh;
      height: 100dvh;
      overflow: hidden;
      width: 100%;
      max-width: 100%;
      min-width: 0;
    }

    /* ---- Mobile overlay ---- */
    .mobile-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(4px);
      z-index: 150;
      opacity: 0;
      transition: opacity var(--transition-base);
      pointer-events: none;
    }

    /* ---- Sidebar ---- */
    .sidebar {
      width: var(--sidebar-width);
      height: 100vh;
      height: 100dvh;
      background: var(--bg-secondary);
      border-right: 1px solid var(--border-primary);
      display: flex;
      flex-direction: column;
      transition: width var(--transition-base), transform var(--transition-base);
      position: relative;
      z-index: 200;
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

    .logo-icon.small {
      width: 32px;
      height: 32px;
    }

    .logo-icon.small .material-symbols-rounded {
      font-size: 18px;
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

    .mobile-only { display: none; }
    .desktop-only { display: flex; }

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
      display: flex;
      flex-direction: column;
      min-width: 0;
      width: 100%;
    }

    .main-content-inner {
      flex: 1;
      overflow: hidden;
      overflow-x: hidden;
      min-width: 0;
      width: 100%;
    }

    /* ---- Mobile top bar ---- */
    .mobile-topbar {
      display: none;
      align-items: center;
      gap: 12px;
      padding: 10px 16px;
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border-primary);
      min-height: 56px;
    }

    .mobile-hamburger {
      background: none;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      padding: 6px;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      transition: all var(--transition-fast);
    }

    .mobile-hamburger:hover {
      background: var(--bg-surface);
      color: var(--text-primary);
    }

    .mobile-logo {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }

    .mobile-logo .logo-text {
      font-size: 1.05rem;
    }

    .mobile-spacer {
      flex: 1;
    }

    /* ---- Responsive ---- */
    @media (max-width: 768px) {
      .sidebar {
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        transform: translateX(-100%);
        width: 280px !important;
        box-shadow: var(--shadow-lg);
      }

      .mobile-open .sidebar {
        transform: translateX(0);
      }

      .mobile-open .mobile-overlay {
        display: block;
        opacity: 1;
        pointer-events: auto;
      }

      .mobile-overlay {
        display: block;
      }

      .mobile-topbar {
        display: flex;
      }

      .desktop-only { display: none; }
      .mobile-only { display: flex; }

      .sidebar-collapsed .sidebar {
        width: 280px;
      }

      .sidebar-collapsed .logo-text,
      .sidebar-collapsed .nav-label,
      .sidebar-collapsed .sidebar-version .nav-label {
        display: inline;
      }
    }
  `]
})
export class AppComponent {
  sidebarCollapsed = signal(false);
  mobileMenuOpen = signal(false);

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

  openMobileMenu(): void {
    this.mobileMenuOpen.set(true);
  }

  closeMobileMenu(): void {
    this.mobileMenuOpen.set(false);
  }

  onNavClick(): void {
    // Close mobile menu when navigating
    if (window.innerWidth <= 768) {
      this.mobileMenuOpen.set(false);
    }
  }
}
