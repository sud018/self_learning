import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../core/api.service';
import { UserContextService } from '../../core/user-context.service';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule],
  template: `
    <section class="page">
      <div class="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Daily discipline, interview readiness, and skill progress in one place.</p>
        </div>
        <div class="card">
          <strong class="fire">Streak {{ dashboard?.streakCount ?? 0 }}</strong>
        </div>
      </div>

      @if (loading) {
        <article class="card empty-state">
          <h2>Loading dashboard...</h2>
          <p>Getting your current points, streak, and skill progress.</p>
        </article>
      }

      @if (error) {
        <article class="card warning empty-state">
          <h2>Backend API is not reachable</h2>
          <p>{{ error }}</p>
        </article>
      }

      @if (dashboard) {
        <div style="margin-bottom:16px; text-align:right;">
          <button type="button" class="ghost danger-btn" (click)="confirmReset()">Reset Progress</button>
          @if (resetMsg) { <span style="margin-left:12px; font-size:13px; color:#999;">{{ resetMsg }}</span> }
        </div>
        <div class="grid metrics">
          <article class="card metric"><span>Today target</span><strong>{{ dashboard.todaysTargetPoints }}</strong></article>
          <article class="card metric celebrate"><span>Total points</span><strong>{{ dashboard.totalPoints }}</strong></article>
          <article class="card metric"><span>Earned today</span><strong class="success">{{ dashboard.earnedToday }}</strong></article>
          <article class="card metric" [class.warning]="dashboard.lostToday > 0"><span>Lost today</span><strong class="danger">{{ dashboard.lostToday }}</strong></article>
          <article class="card metric"><span>Completed days</span><strong>{{ dashboard.completedDays }}</strong></article>
          <article class="card metric"><span>Missed days</span><strong>{{ dashboard.missedDays }}</strong></article>
          <article class="card metric"><span>Weekly points</span><strong>{{ dashboard.weeklyPoints }}</strong></article>
          <article class="card metric"><span>Monthly points</span><strong>{{ dashboard.monthlyPoints }}</strong></article>
        </div>

        <div class="grid" style="margin-top: 16px;">
          <article class="card">
            <h2>Interview Readiness {{ dashboard.interviewReadiness }}%</h2>
            <div class="progress-track"><div class="progress-fill" [style.width.%]="dashboard.interviewReadiness"></div></div>
          </article>
          <article class="card">
            <h2>Skill Progress</h2>
            @for (item of progressItems; track item.name) {
              <p><strong>{{ item.name }}</strong> {{ item.value }}%</p>
              <div class="progress-track"><div class="progress-fill" [style.width.%]="item.value"></div></div>
            }
          </article>
        </div>
      }
    </section>
  `
})
export class DashboardComponent implements OnInit {
  dashboard: any;
  progressItems: Array<{ name: string; value: number }> = [];
  loading = true;
  error = '';
  resetMsg = '';

  constructor(private api: ApiService, private userContext: UserContextService, private cd: ChangeDetectorRef) {}

  confirmReset() {
    const confirmed = window.confirm(
      'Reset all progress to 0%?\n\nThis clears your completed days, points, streak, and skill progress. This cannot be undone.'
    );
    if (!confirmed) return;
    this.api.resetProgress(this.userContext.email()).subscribe({
      next: () => {
        this.resetMsg = 'Progress reset. Reloading…';
        this.cd.detectChanges();
        setTimeout(() => window.location.reload(), 800);
      },
      error: () => {
        this.resetMsg = 'Reset failed — is the backend running?';
        this.cd.detectChanges();
      }
    });
  }

  ngOnInit() {
    this.api.dashboard(this.userContext.email()).subscribe({
      next: (dashboard) => {
        this.dashboard = dashboard;
        this.progressItems = Object.entries(dashboard.progress).map(([name, value]) => ({ name, value: Number(value) }));
        this.loading = false;
        this.cd.detectChanges();
      },
      error: () => {
        this.loading = false;
        this.error = 'Start the Spring Boot backend on port 8082, then refresh this page.';
        this.cd.detectChanges();
      }
    });
  }
}
