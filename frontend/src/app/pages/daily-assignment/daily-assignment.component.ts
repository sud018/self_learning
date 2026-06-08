import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/api.service';
import { UserContextService } from '../../core/user-context.service';

@Component({
  selector: 'app-daily-assignment',
  imports: [CommonModule, FormsModule],
  template: `
    <section class="page">
      <div class="page-header">
        <div>
          <h1>Daily Assignment</h1>
          <p>Industry-focused prep with notes, MCQs, written concepts, business scenarios, coding, SQL, Angular, Spring Boot, and DSA.</p>
        </div>
      </div>

      @if (loading) {
        <article class="card empty-state">
          <h2>Loading Day 1...</h2>
          <p>Getting your notes, MCQs, coding exercises, SQL, and DSA practice.</p>
        </article>
      }

      @if (error) {
        <article class="card warning empty-state">
          <h2>Backend API is not reachable</h2>
          <p>{{ error }}</p>
        </article>
      }

      @if (assignment) {
        <article class="card progress-card">
          <div class="progress-card-header">
            <div>
              <h2>Daily Completion {{ dailyCompletionPercent }}%</h2>
              <p>{{ dailyCompletedItems }} of {{ dailyTotalItems }} daily items completed</p>
            </div>
            <strong>{{ dailyCompletionPercent }}%</strong>
          </div>
          <div class="progress-track"><div class="progress-fill" [style.width.%]="dailyCompletionPercent"></div></div>
          <div class="progress-breakdown">
            <span [class.success]="notesCompleted">Notes</span>
            <span>MCQs {{ answeredMcqCount }}/{{ assignment.conceptualQuestions.length }}</span>
            <span>Concepts {{ answeredWrittenCount }}/{{ writtenQuestionCount }}</span>
            <span>SQL {{ boundedSqlSolved }}/{{ assignment.sqlPractice.length }}</span>
          </div>
        </article>

        <div class="step-tabs">
          @for (label of steps; track label; let index = $index) {
            <button type="button" [class.active]="step === index" (click)="step = index">{{ label }}</button>
          }
        </div>

        <article class="card">
          @if (step === 0) {
            <h2>{{ assignment.topic }}</h2>
            <div class="note-block">{{ assignment.notes }}</div>
            <label class="option"><input type="checkbox" [(ngModel)]="notesCompleted"> I completed today’s notes</label>
            <button class="primary" type="button" (click)="step = 1">Start MCQs</button>
          }

          @if (step === 1) {
            <h2>MCQs</h2>
            @for (question of assignment.conceptualQuestions; track question.id) {
              <div class="card question-card">
                <strong>{{ question.prompt }}</strong>
                @for (option of question.options; track option) {
                  <label class="option">
                    <input type="radio" [name]="question.id" [value]="option" [(ngModel)]="answers[question.id]">
                    {{ option }}
                  </label>
                }
              </div>
            }
            <button class="primary" type="button" (click)="step = 2">Continue</button>
          }

          @if (step === 2) {
            <h2>Conceptual and Business Questions</h2>
            <div class="practice-grid">
              <div>
                <h3>Normal Conceptual Questions</h3>
                @for (question of assignment.writtenConceptQuestions; track question) {
                  <label class="field">
                    <span>{{ question }}</span>
                    <textarea [(ngModel)]="writtenAnswers[question]" placeholder="Write your explanation in interview style"></textarea>
                  </label>
                }
              </div>
              <div>
                <h3>Business Backend Scenarios</h3>
                @for (scenario of assignment.businessScenarios; track scenario) {
                  <label class="field">
                    <span>{{ scenario }}</span>
                    <textarea [(ngModel)]="writtenAnswers[scenario]" placeholder="Think from user, data, money, operations, and support point of view"></textarea>
                  </label>
                }
              </div>
            </div>
            <button class="primary" type="button" (click)="step = 3">Continue Practice</button>
          }

          @if (step === 3) {
            <h2>SQL, Spring Boot, Angular, and DSA</h2>
            <p>Coding editors and runnable DSA problems are available in the Coding Practice section.</p>
            <div class="practice-grid">
              <section>
                <h3>SQL</h3>
                @for (item of assignment.sqlPractice; track item) { <p class="practice-item">{{ item }}</p> }
                <div class="field">
                  <label>SQL exercises completed</label>
                  <input type="number" min="0" [(ngModel)]="sqlSolved">
                </div>
              </section>
              <section>
                <h3>Spring Boot</h3>
                @for (item of assignment.springBootScenarios; track item) { <p class="practice-item">{{ item }}</p> }
              </section>
              <section>
                <h3>Angular</h3>
                @for (item of assignment.angularQuestions; track item) { <p class="practice-item">{{ item }}</p> }
              </section>
              <section>
                <h3>Data Structures</h3>
                @for (problem of assignment.dsaPractice; track problem.id) {
                  <article class="dsa-card">
                    <div class="task-heading">
                      <div>
                        <span class="pill">{{ problem.difficulty }}</span>
                        <h3>{{ problem.title }}</h3>
                      </div>
                    </div>
                    <p>{{ problem.statement }}</p>
                    <h4>Examples</h4>
                    @for (example of problem.examples; track example) {
                      <p class="practice-item">{{ example }}</p>
                    }
                    <h4>Constraints</h4>
                    @for (constraint of problem.constraints; track constraint) {
                      <p class="practice-item">{{ constraint }}</p>
                    }
                    <p><strong>Expected:</strong> {{ problem.expectedTimeComplexity }} time, {{ problem.expectedSpaceComplexity }} space</p>
                    <details>
                      <summary>Show hints</summary>
                      @for (hint of problem.hints; track hint) {
                        <p>{{ hint }}</p>
                      }
                    </details>
                  </article>
                }
              </section>
            </div>
            <button class="primary" type="button" (click)="submit()">Submit Assignment</button>
          }

          @if (step === 4 && result) {
            <div class="celebrate">
              <h2>Score {{ result.scorePercent }}%</h2>
              <p class="success">Earned +{{ result.earnedPoints }} points</p>
              @if (result.lostPoints > 0) { <p class="danger">Lost -{{ result.lostPoints }} points</p> }
              <p>Total points: {{ result.totalPoints }}</p>
              @for (line of result.feedback; track line) { <p>{{ line }}</p> }
              @if (result.nextAssignmentAvailable) {
                <button class="primary" type="button" (click)="loadNextDay()">Load Next Day</button>
              } @else {
                <p>You finished all available sample days. Add more assignments in the backend list to extend the plan.</p>
              }
            </div>
          }

          @if (submitError) {
            <div class="card warning" style="margin-top: 16px;">
              <h2>Could not submit assignment</h2>
              <p>{{ submitError }}</p>
            </div>
          }
        </article>
      }
    </section>
  `
})
export class DailyAssignmentComponent implements OnInit {
  assignment: any;
  steps = ['Notes', 'MCQs', 'Concepts', 'Practice', 'Score'];
  step = 0;
  notesCompleted = false;
  answers: Record<string, string> = {};
  writtenAnswers: Record<string, string> = {};
  sqlSolved = 0;
  result: any;
  loading = true;
  error = '';
  submitError = '';

  constructor(private api: ApiService, private userContext: UserContextService, private cd: ChangeDetectorRef) {}

  get answeredMcqCount() {
    return Object.values(this.answers).filter(Boolean).length;
  }

  get writtenQuestionCount() {
    if (!this.assignment) {
      return 0;
    }
    return (this.assignment.writtenConceptQuestions?.length || 0) + (this.assignment.businessScenarios?.length || 0);
  }

  get answeredWrittenCount() {
    const answered = Object.values(this.writtenAnswers).filter((answer) => String(answer || '').trim().length > 0).length;
    return Math.min(answered, this.writtenQuestionCount);
  }

  get boundedSqlSolved() {
    return Math.min(Number(this.sqlSolved) || 0, this.assignment?.sqlPractice?.length || 0);
  }

  get dailyTotalItems() {
    if (!this.assignment) {
      return 0;
    }
    return 1 + this.assignment.conceptualQuestions.length + this.writtenQuestionCount + this.assignment.sqlPractice.length;
  }

  get dailyCompletedItems() {
    return (this.notesCompleted ? 1 : 0) + this.answeredMcqCount + this.answeredWrittenCount + this.boundedSqlSolved;
  }

  get dailyCompletionPercent() {
    if (!this.dailyTotalItems) {
      return 0;
    }
    return Math.round((this.dailyCompletedItems / this.dailyTotalItems) * 100);
  }

  ngOnInit() {
    this.loadNextDay();
  }

  submit() {
    this.submitError = '';
    const answers = Object.entries(this.answers).map(([questionId, answer]) => ({ questionId, answer }));
    this.api.submitAssignment({
      email: this.userContext.email(),
      assignmentId: this.assignment.id,
      notesCompleted: this.notesCompleted,
      answers,
      codingSolved: 0,
      sqlSolved: this.boundedSqlSolved
    }).subscribe((result) => {
      this.result = result;
      this.step = 4;
      this.cd.detectChanges();
    }, (error) => {
      this.submitError = error?.message || 'Start the Spring Boot backend on port 8082, then try again.';
      this.cd.detectChanges();
    });
  }

  loadNextDay() {
    this.loading = true;
    this.error = '';
    this.api.todayAssignment(this.userContext.email()).subscribe({
      next: (assignment) => {
        this.assignment = assignment;
        this.step = 0;
        this.notesCompleted = false;
        this.answers = {};
        this.writtenAnswers = {};
        this.sqlSolved = 0;
        this.result = null;
        this.submitError = '';
        this.loading = false;
        this.cd.detectChanges();
      },
      error: () => {
        this.assignment = null;
        this.loading = false;
        this.error = 'Start the Spring Boot backend on port 8082, then refresh this page.';
        this.cd.detectChanges();
      }
    });
  }
}
