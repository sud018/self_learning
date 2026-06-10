import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../../core/api.service';
import { UserContextService } from '../../core/user-context.service';

interface DayCard {
  dayNumber: number;
  assignmentId: string | null;
  topic: string;
  status: 'done' | 'current' | 'upcoming' | 'missed' | 'locked';
  date: Date;
  reason: string;
  excused: boolean;
  penalty: number;
  hasCurriculum: boolean;
}

@Component({
  selector: 'app-tracker',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="page">
      <div class="page-header">
        <div>
          <h1>90-Day Tracker</h1>
          <p>Your full learning schedule — click any day to start or review it.</p>
        </div>
        @if (!loading && !error) {
          <div class="trk-summary">
            <span class="trk-sum-item trk-sum-done"><strong>{{ doneCount }}</strong> done</span>
            <span class="trk-sum-item trk-sum-missed"><strong>{{ missedCount }}</strong> missed</span>
            <span class="trk-sum-item trk-sum-rem"><strong>{{ remainingCount }}</strong> remaining</span>
          </div>
        }
      </div>

      @if (loading) {
        <article class="card empty-state"><h2>Loading tracker…</h2></article>
      }

      @if (error) {
        <article class="card warning empty-state">
          <h2>Backend not reachable</h2><p>{{ error }}</p>
        </article>
      }

      @if (!loading && !error) {

        <!-- Legend -->
        <div class="trk-legend">
          <span class="trk-leg-item trk-leg-done">✓ Completed</span>
          <span class="trk-leg-item trk-leg-current">● Today</span>
          <span class="trk-leg-item trk-leg-upcoming">○ Upcoming</span>
          <span class="trk-leg-item trk-leg-missed">✗ Missed</span>
          <span class="trk-leg-item trk-leg-locked">🔒 Coming soon</span>
        </div>

        <!-- Day grid -->
        <div class="trk-grid">
          @for (day of days; track day.dayNumber) {
            <button
              type="button"
              class="trk-card"
              [class.trk-done]="day.status === 'done'"
              [class.trk-current]="day.status === 'current'"
              [class.trk-upcoming]="day.status === 'upcoming'"
              [class.trk-missed]="day.status === 'missed'"
              [class.trk-locked]="day.status === 'locked'"
              [disabled]="day.status === 'locked'"
              (click)="openDay(day)">

              <div class="trk-card-top">
                <span class="trk-day-num">Day {{ day.dayNumber }}</span>
                <span class="trk-date">{{ formatDate(day.date) }}</span>
              </div>

              <div class="trk-status-row">
                @switch (day.status) {
                  @case ('done')     { <span class="trk-status-icon trk-icon-done">✓</span><span class="trk-status-label">Completed</span> }
                  @case ('current')  { <span class="trk-status-icon trk-icon-current">●</span><span class="trk-status-label trk-cta">Start Today</span> }
                  @case ('upcoming') { <span class="trk-status-icon trk-icon-upcoming">○</span><span class="trk-status-label">Upcoming</span> }
                  @case ('missed')   { <span class="trk-status-icon trk-icon-missed">✗</span><span class="trk-status-label">Missed</span> }
                  @case ('locked')   { <span class="trk-status-icon">🔒</span><span class="trk-status-label">Coming soon</span> }
                }
              </div>

              @if (day.hasCurriculum) {
                <div class="trk-topic">{{ shortTopic(day.topic) }}</div>
              }

              @if (day.status === 'missed' && day.reason) {
                <div class="trk-reason">{{ day.reason }}</div>
              }

              @if (day.status !== 'locked') {
                <div class="trk-card-cta">
                  @switch (day.status) {
                    @case ('done')     { <span>Review →</span> }
                    @case ('current')  { <span class="trk-cta-strong">Start Now →</span> }
                    @case ('upcoming') { <span>Do it now →</span> }
                    @case ('missed')   { <span>Retry →</span> }
                  }
                </div>
              }
              @if (day.status !== 'done' && day.status !== 'locked') {
                <div class="trk-mark-done-row" (click)="$event.stopPropagation()">
                  <button type="button" class="trk-mark-done-btn"
                    [disabled]="markingDone === day.assignmentId"
                    (click)="markDone($event, day)">
                    {{ markingDone === day.assignmentId ? '…' : '✓ Mark as Done' }}
                  </button>
                </div>
              }
            </button>
          }
        </div>

        <!-- Coming soon footer -->
        @if (lockedCount > 0) {
          <div class="trk-coming-soon">
            🚀 <strong>{{ lockedCount }} more days</strong> of content are being added to complete your 90-day journey.
          </div>
        }

      }
    </section>
  `
})
export class TrackerComponent implements OnInit {
  days: DayCard[] = [];
  loading = true;
  error = '';
  markingDone: string | null = null;

  constructor(
    private api: ApiService,
    private userContext: UserContextService,
    private router: Router,
    private cd: ChangeDetectorRef
  ) {}

  get doneCount()      { return this.days.filter(d => d.status === 'done').length; }
  get missedCount()    { return this.days.filter(d => d.status === 'missed').length; }
  get remainingCount() { return this.days.filter(d => d.status === 'upcoming' || d.status === 'current').length; }
  get lockedCount()    { return this.days.filter(d => d.status === 'locked').length; }

  ngOnInit() {
    this.api.dayStatus(this.userContext.email()).subscribe({
      next: (statuses) => {
        this.buildDays(statuses);
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

  buildDays(statuses: any[]) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const currentIdx = statuses.findIndex(s => s.status === 'pending');
    const currentDayNum = currentIdx >= 0 ? statuses[currentIdx].dayNumber : statuses.length + 1;

    const curriculum: DayCard[] = statuses.map(s => {
      const offset = s.dayNumber - currentDayNum;
      const d = new Date(today);
      d.setDate(today.getDate() + offset);
      const status: DayCard['status'] =
        s.status === 'done' ? 'done' :
        s.status === 'missed' ? 'missed' :
        s.dayNumber === currentDayNum ? 'current' : 'upcoming';
      return {
        dayNumber: s.dayNumber,
        assignmentId: s.assignmentId,
        topic: s.topic,
        status,
        date: d,
        reason: s.reason || '',
        excused: s.excused,
        penalty: s.penalty,
        hasCurriculum: true
      };
    });

    const locked: DayCard[] = [];
    for (let n = statuses.length + 1; n <= 90; n++) {
      const offset = n - currentDayNum;
      const d = new Date(today);
      d.setDate(today.getDate() + offset);
      locked.push({
        dayNumber: n,
        assignmentId: null,
        topic: '',
        status: 'locked',
        date: d,
        reason: '',
        excused: false,
        penalty: 0,
        hasCurriculum: false
      });
    }

    this.days = [...curriculum, ...locked];
  }

  openDay(day: DayCard) {
    if (day.status === 'locked' || !day.assignmentId) return;
    this.router.navigate(['/daily'], { queryParams: { dayId: day.assignmentId } });
  }

  markDone(event: Event, day: DayCard) {
    event.stopPropagation();
    if (!day.assignmentId || this.markingDone) return;
    const confirmed = window.confirm(`Mark Day ${day.dayNumber} as completed?\n\nThis records it as done without going through the full assignment flow.`);
    if (!confirmed) return;
    this.markingDone = day.assignmentId;
    this.cd.detectChanges();
    this.api.markDayComplete(this.userContext.email(), day.assignmentId).subscribe({
      next: () => {
        this.markingDone = null;
        this.loading = true;
        this.cd.detectChanges();
        this.api.dayStatus(this.userContext.email()).subscribe({
          next: (statuses) => { this.buildDays(statuses); this.loading = false; this.cd.detectChanges(); },
          error: () => { this.loading = false; this.cd.detectChanges(); }
        });
      },
      error: () => { this.markingDone = null; this.cd.detectChanges(); }
    });
  }

  formatDate(date: Date): string {
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    const diff = Math.round((date.getTime() - now.getTime()) / 86400000);
    if (diff === 0) return 'Today';
    if (diff === 1) return 'Tomorrow';
    if (diff === -1) return 'Yesterday';
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', weekday: 'short' });
  }

  shortTopic(topic: string): string {
    const match = topic.match(/^Day \d+:\s*(.+)/);
    const clean = match ? match[1] : topic;
    return clean.length > 52 ? clean.slice(0, 52) + '…' : clean;
  }
}
