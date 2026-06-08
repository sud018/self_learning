import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="app-shell">
      <aside class="sidebar">
        <a class="brand" routerLink="/dashboard">
          <span class="brand-mark">JP</span>
          <span>
            <strong>Java Prep</strong>
            <small>Interview discipline</small>
          </span>
        </a>
        <nav>
          <a routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
          <a routerLink="/daily" routerLinkActive="active">Daily Assignment</a>
          <a routerLink="/roadmap" routerLinkActive="active">Roadmap</a>
          <a routerLink="/coding" routerLinkActive="active">Coding Practice</a>
          <a routerLink="/missed-day" routerLinkActive="active">Missed Day</a>
        </nav>
        <div class="user-panel">
          <span>Personal prep mode</span>
        </div>
      </aside>
      <main class="content">
        <router-outlet />
      </main>
    </div>
  `
})
export class AppComponent {}
