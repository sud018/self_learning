import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/api.service';
import { UserContextService } from '../../core/user-context.service';

@Component({
  selector: 'app-missed-day',
  imports: [FormsModule],
  template: `
    <section class="page">
      <div class="page-header">
        <div>
          <h1>Missed Day</h1>
          <p>Track every course day as done, missed, or pending. Valid missed reasons apply 0 penalty; invalid reasons subtract points.</p>
        </div>
      </div>

      <article class="card progress-card">
        <div class="progress-card-header">
          <div>
            <h2>{{ completedPercent() }}% handled</h2>
            <p>{{ doneCount() }} done, {{ missedCount() }} missed, {{ pendingCount() }} pending.</p>
          </div>
          <strong>{{ doneCount() + missedCount() }}/{{ days.length }}</strong>
        </div>
        <div class="progress-track">
          <div class="progress-fill" [style.width.%]="completedPercent()"></div>
        </div>
      </article>

      @if (loading) {
        <article class="card">
          <h2>Loading days...</h2>
          <p>Getting your done and missed status.</p>
        </article>
      } @else if (error) {
        <article class="card warning">
          <h2>Could not load missed-day data</h2>
          <p>{{ error }}</p>
          <button class="primary" type="button" (click)="loadDays()">Retry</button>
        </article>
      } @else {
        <div class="missed-day-list">
          @for (day of days; track day.assignmentId) {
            <article class="card missed-day-row">
              <div>
                <div class="missed-row-title">
                  <strong>Day {{ day.dayNumber }}</strong>
                  <span class="status-pill" [class.done]="day.status === 'done'" [class.missed]="day.status === 'missed'" [class.pending]="day.status === 'pending'">
                    {{ statusLabel(day) }}
                  </span>
                </div>
                <h3>{{ day.topic }}</h3>
                @if (day.status === 'missed') {
                  <p>
                    Reason: {{ day.reason || 'No reason saved' }}.
                    {{ day.excused ? 'Accepted with 0 penalty.' : 'Invalid reason, -' + day.penalty + ' points.' }}
                  </p>
                } @else if (day.status === 'done') {
                  <p>This day is completed, so no missed-day evaluation is needed.</p>
                } @else {
                  <p>Pending. If you cannot complete this day, mark it missed and enter the reason.</p>
                }
              </div>

              @if (day.status === 'pending') {
                <div class="missed-actions">
                  @if (selectedAssignmentId !== day.assignmentId) {
                    <button class="ghost" type="button" (click)="selectDay(day.assignmentId)">Mark missed</button>
                  } @else {
                    <form class="missed-reason-form" (ngSubmit)="submit(day.assignmentId)">
                      <div class="field">
                        <label>Reason for Day {{ day.dayNumber }}</label>
                        <textarea name="reason-{{ day.assignmentId }}" [(ngModel)]="reason" placeholder="Example: health issue, emergency, work priority, family emergency, travel, internet, system issue"></textarea>
                      </div>
                      <div class="editor-actions">
                        <button class="primary" type="submit">Evaluate Reason</button>
                        <button class="ghost" type="button" (click)="cancel()">Cancel</button>
                      </div>
                    </form>
                  }
                </div>
              }
            </article>
          }
        </div>
      }

      @if (result) {
        <article class="card missed-result" [class.warning]="!result.excused" [class.celebrate]="result.excused">
          <h2>{{ result.excused ? 'Reason accepted' : 'Penalty applied' }}</h2>
          <p>{{ result.message }}</p>
          <p>Total points: {{ result.totalPoints }}</p>
        </article>
      }
    </section>
  `
})
export class MissedDayComponent implements OnInit {
  reason = '';
  result: any;
  days: any[] = [];
  loading = true;
  error = '';
  selectedAssignmentId = '';

  constructor(private api: ApiService, private userContext: UserContextService, private cd: ChangeDetectorRef) {}

  ngOnInit() {
    this.loadDays();
  }

  loadDays() {
    this.loading = true;
    this.error = '';
    this.api.dayStatus(this.userContext.email()).subscribe((days) => {
      this.days = days;
      this.loading = false;
      this.cd.detectChanges();
    }, (error) => {
      this.loading = false;
      this.error = this.apiMessage(error);
      this.cd.detectChanges();
    });
  }

  selectDay(assignmentId: string) {
    this.selectedAssignmentId = assignmentId;
    this.reason = '';
    this.result = null;
  }

  cancel() {
    this.selectedAssignmentId = '';
    this.reason = '';
  }

  submit(assignmentId: string) {
    this.api.missedDay({ email: this.userContext.email(), assignmentId, reason: this.reason }).subscribe((result) => {
      this.result = result;
      this.selectedAssignmentId = '';
      this.reason = '';
      this.loadDays();
      this.cd.detectChanges();
    }, (error) => {
      this.result = {
        excused: false,
        message: this.apiMessage(error),
        totalPoints: 'not updated'
      };
      this.cd.detectChanges();
    });
  }

  private apiMessage(error: any) {
    return error?.message || 'Backend is not reachable. Restart Spring Boot on port 8082 and refresh this page.';
  }

  statusLabel(day: any) {
    if (day.status === 'done') return 'Done';
    if (day.status === 'missed') return day.excused ? 'Missed, excused' : 'Missed, penalty';
    return 'Pending';
  }

  doneCount() {
    return this.days.filter((day) => day.status === 'done').length;
  }

  missedCount() {
    return this.days.filter((day) => day.status === 'missed').length;
  }

  pendingCount() {
    return this.days.filter((day) => day.status === 'pending').length;
  }

  completedPercent() {
    if (!this.days.length) return 0;
    return Math.round(((this.doneCount() + this.missedCount()) / this.days.length) * 100);
  }
}
