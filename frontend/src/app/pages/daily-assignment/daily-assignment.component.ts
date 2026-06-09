import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/api.service';
import { UserContextService } from '../../core/user-context.service';

interface McqResult {
  questionId: string;
  prompt: string;
  options: string[];
  userAnswer: string;
  correctAnswer: string;
  explanation: string;
  correct: boolean;
}

@Component({
  selector: 'app-daily-assignment',
  standalone: true,
  imports: [CommonModule, FormsModule],
  styles: [`
    .eval-card { border-radius: 10px; padding: 16px; margin: 12px 0; border-left: 4px solid #ccc; }
    .eval-card.correct { border-color: #2f9e44; background: #f3fbf4; }
    .eval-card.wrong   { border-color: #d9480f; background: #fff5f0; }
    .eval-label { font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 6px; }
    .eval-label.correct { color: #2f9e44; }
    .eval-label.wrong   { color: #d9480f; }
    .eval-answer { background: #fff; border-radius: 6px; padding: 8px 12px; margin: 4px 0; font-size: 14px; }
    .eval-answer.user-wrong  { background: #ffe5d9; color: #c92a2a; text-decoration: line-through; }
    .eval-answer.user-right  { background: #d3f9d8; color: #1a6b29; }
    .eval-answer.correct-ans { background: #d3f9d8; color: #1a6b29; font-weight: 700; }
    .eval-explanation { font-size: 13px; color: #555; margin-top: 8px; padding: 8px 10px; background: #f8f9fa; border-radius: 6px; }
    .score-banner { display: flex; align-items: center; gap: 16px; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
    .score-banner.great { background: #d3f9d8; }
    .score-banner.ok    { background: #fff3cd; }
    .score-banner.poor  { background: #ffe5d9; }
    .score-number { font-size: 48px; font-weight: 900; line-height: 1; }
    .score-number.great { color: #2f9e44; }
    .score-number.ok    { color: #e67700; }
    .score-number.poor  { color: #c92a2a; }
    .written-review { border: 1px solid #dfe5e8; border-radius: 8px; padding: 14px; margin: 10px 0; background: #fff; }
    .written-q { font-weight: 700; margin-bottom: 8px; color: #182026; }
    .written-a { white-space: pre-wrap; color: #444; background: #f5f7f8; border-radius: 6px; padding: 10px; font-size: 14px; line-height: 1.6; }
    .written-a.empty { color: #999; font-style: italic; }
    .section-result-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
    .tag { display: inline-block; border-radius: 999px; padding: 4px 12px; font-size: 12px; font-weight: 800; }
    .tag-green  { background: #d3f9d8; color: #1a6b29; }
    .tag-orange { background: #fff3cd; color: #855e00; }
    .tag-red    { background: #ffe5d9; color: #c92a2a; }
    .step-divider { height: 1px; background: #dfe5e8; margin: 20px 0; }
  `],
  template: `
    <section class="page">
      <div class="page-header">
        <div>
          <h1>Daily Assignment</h1>
          <p>Notes → MCQs → Concepts → Practice → Score with full evaluation after every section.</p>
        </div>
      </div>

      @if (loading) {
        <article class="card empty-state"><h2>Loading assignment…</h2></article>
      }

      @if (error) {
        <article class="card warning empty-state">
          <h2>Backend not reachable</h2><p>{{ error }}</p>
        </article>
      }

      @if (assignment) {
        <!-- Progress bar -->
        <article class="card progress-card">
          <div class="progress-card-header">
            <div>
              <h2>Daily Completion {{ dailyCompletionPercent }}%</h2>
              <p>{{ dailyCompletedItems }} of {{ dailyTotalItems }} items done</p>
            </div>
            <strong>{{ dailyCompletionPercent }}%</strong>
          </div>
          <div class="progress-track">
            <div class="progress-fill" [style.width.%]="dailyCompletionPercent"></div>
          </div>
          <div class="progress-breakdown">
            <span [class.success]="notesCompleted">Notes</span>
            <span>MCQs {{ answeredMcqCount }}/{{ assignment.conceptualQuestions.length }}</span>
            <span>Concepts {{ answeredWrittenCount }}/{{ writtenQuestionCount }}</span>
            <span>SQL {{ boundedSqlSolved }}/{{ assignment.sqlPractice.length }}</span>
          </div>
        </article>

        <!-- Step tabs -->
        <div class="step-tabs">
          @for (label of steps; track label; let i = $index) {
            <button type="button" [class.active]="step === i" (click)="goToStep(i)">{{ label }}</button>
          }
        </div>

        <article class="card">

          <!-- ══ STEP 0: Notes ══ -->
          @if (step === 0) {
            <h2>{{ assignment.topic }}</h2>
            <div class="note-block">{{ assignment.notes }}</div>
            <label class="option">
              <input type="checkbox" [(ngModel)]="notesCompleted"> I read today's notes completely
            </label>
            <br>
            <button class="primary" type="button" (click)="step = 1">Start MCQs →</button>
          }

          <!-- ══ STEP 1a: MCQ Questions ══ -->
          @if (step === 1 && !showMcqResults) {
            <h2>MCQs — {{ assignment.conceptualQuestions.length }} Questions</h2>
            <p class="muted">Select one answer per question. You will see results immediately after submitting.</p>
            @for (q of assignment.conceptualQuestions; track q.id; let qi = $index) {
              <div class="card question-card">
                <strong>Q{{ qi + 1 }}. {{ q.prompt }}</strong>
                @for (opt of q.options; track opt) {
                  <label class="option">
                    <input type="radio" [name]="q.id" [value]="opt" [(ngModel)]="answers[q.id]">
                    {{ opt }}
                  </label>
                }
              </div>
            }
            <button class="primary" type="button" (click)="submitMcqs()">
              Submit MCQs &amp; See Results →
            </button>
          }

          <!-- ══ STEP 1b: MCQ Evaluation ══ -->
          @if (step === 1 && showMcqResults) {
            <div class="section-result-header">
              <h2>MCQ Results</h2>
              <span class="tag"
                [class.tag-green]="mcqScorePercent >= 70"
                [class.tag-orange]="mcqScorePercent >= 40 && mcqScorePercent < 70"
                [class.tag-red]="mcqScorePercent < 40">
                {{ mcqCorrectCount }}/{{ mcqResults.length }} correct · {{ mcqScorePercent }}%
              </span>
            </div>

            <div class="score-banner"
              [class.great]="mcqScorePercent >= 70"
              [class.ok]="mcqScorePercent >= 40 && mcqScorePercent < 70"
              [class.poor]="mcqScorePercent < 40">
              <div class="score-number"
                [class.great]="mcqScorePercent >= 70"
                [class.ok]="mcqScorePercent >= 40 && mcqScorePercent < 70"
                [class.poor]="mcqScorePercent < 40">
                {{ mcqScorePercent }}%
              </div>
              <div>
                <strong>{{ mcqCorrectCount }} correct · {{ mcqResults.length - mcqCorrectCount }} wrong</strong>
                <p style="margin:4px 0 0">
                  @if (mcqScorePercent >= 70) { Great job! Review the explanations below and move on. }
                  @else if (mcqScorePercent >= 40) { Good effort. Read the explanations carefully before continuing. }
                  @else { Re-read today's notes. The explanations show where to focus. }
                </p>
              </div>
            </div>

            @for (r of mcqResults; track r.questionId; let ri = $index) {
              <div class="eval-card" [class.correct]="r.correct" [class.wrong]="!r.correct">
                <div class="eval-label" [class.correct]="r.correct" [class.wrong]="!r.correct">
                  Q{{ ri + 1 }} · {{ r.correct ? '✓ Correct' : '✗ Wrong' }}
                </div>
                <p style="font-weight:700; margin:0 0 10px">{{ r.prompt }}</p>

                @if (!r.correct) {
                  <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:8px;">
                    <div style="flex:1; min-width:200px;">
                      <div style="font-size:11px; color:#999; margin-bottom:4px;">YOUR ANSWER</div>
                      <div class="eval-answer user-wrong">{{ r.userAnswer || '(no answer selected)' }}</div>
                    </div>
                    <div style="flex:1; min-width:200px;">
                      <div style="font-size:11px; color:#999; margin-bottom:4px;">CORRECT ANSWER</div>
                      <div class="eval-answer correct-ans">{{ r.correctAnswer }}</div>
                    </div>
                  </div>
                } @else {
                  <div class="eval-answer user-right">✓ {{ r.userAnswer }}</div>
                }
                <div class="eval-explanation">💡 {{ r.explanation }}</div>
              </div>
            }

            <div class="step-divider"></div>
            <button class="primary" type="button" (click)="proceedFromMcqResults()">
              Continue to Conceptual Questions →
            </button>
          }

          <!-- ══ STEP 2a: Written Concepts input ══ -->
          @if (step === 2 && !showWrittenResults) {
            <h2>Conceptual &amp; Business Questions</h2>
            <p class="muted">Answer in your own words as if in an interview. No wrong answers — the goal is to practice expressing concepts clearly.</p>
            <div class="practice-grid">
              <div>
                <h3>Conceptual Questions</h3>
                @for (q of assignment.writtenConceptQuestions; track q) {
                  <label class="field">
                    <span>{{ q }}</span>
                    <textarea [(ngModel)]="writtenAnswers[q]"
                      placeholder="Answer in 3-5 sentences as in an interview…" rows="4"></textarea>
                  </label>
                }
              </div>
              <div>
                <h3>Business Scenarios</h3>
                @for (s of assignment.businessScenarios; track s) {
                  <label class="field">
                    <span>{{ s }}</span>
                    <textarea [(ngModel)]="writtenAnswers[s]"
                      placeholder="Think from user, data, business and operations perspective…" rows="4"></textarea>
                  </label>
                }
              </div>
            </div>
            <button class="primary" type="button" (click)="submitWritten()">
              Save &amp; Review My Answers →
            </button>
          }

          <!-- ══ STEP 2b: Written Answers Review ══ -->
          @if (step === 2 && showWrittenResults) {
            <div class="section-result-header">
              <h2>Your Written Answers</h2>
              <span class="tag tag-green">{{ answeredWrittenCount }}/{{ writtenQuestionCount }} answered</span>
            </div>
            <p class="muted">Read each answer aloud. Could you say this clearly in an interview? Edit anything before continuing.</p>

            @if (assignment.writtenConceptQuestions?.length) {
              <h3 style="margin-top:16px;">Conceptual Questions</h3>
              @for (q of assignment.writtenConceptQuestions; track q) {
                <div class="written-review">
                  <div class="written-q">{{ q }}</div>
                  <div class="written-a" [class.empty]="!writtenAnswers[q]?.trim()">
                    {{ writtenAnswers[q]?.trim() || '(not answered — go back and fill this in)' }}
                  </div>
                </div>
              }
            }

            @if (assignment.businessScenarios?.length) {
              <h3 style="margin-top:16px;">Business Scenarios</h3>
              @for (s of assignment.businessScenarios; track s) {
                <div class="written-review">
                  <div class="written-q">{{ s }}</div>
                  <div class="written-a" [class.empty]="!writtenAnswers[s]?.trim()">
                    {{ writtenAnswers[s]?.trim() || '(not answered — go back and fill this in)' }}
                  </div>
                </div>
              }
            }

            <div class="step-divider"></div>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
              <button class="ghost" type="button" (click)="showWrittenResults = false">← Edit My Answers</button>
              <button class="primary" type="button" (click)="step = 3">Continue to Practice →</button>
            </div>
          }

          <!-- ══ STEP 3: Practice ══ -->
          @if (step === 3) {
            <h2>SQL, Spring Boot, Angular &amp; DSA</h2>
            <p class="muted">Use the Coding Practice section for runnable editors. Mark SQL exercises completed below.</p>
            <div class="practice-grid">
              <section>
                <h3>SQL Practice</h3>
                @for (item of assignment.sqlPractice; track item) { <p class="practice-item">{{ item }}</p> }
                <div class="field" style="margin-top:12px;">
                  <label>SQL exercises completed</label>
                  <input type="number" min="0" [max]="assignment.sqlPractice.length" [(ngModel)]="sqlSolved">
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
                <h3>DSA Problems</h3>
                @for (p of assignment.dsaPractice; track p.id) {
                  <article class="dsa-card">
                    <div class="task-heading">
                      <span class="pill">{{ p.difficulty }}</span>
                      <h3>{{ p.title }}</h3>
                    </div>
                    <p>{{ p.statement }}</p>
                    <details>
                      <summary>Hints &amp; complexity</summary>
                      @for (hint of p.hints; track hint) { <p>{{ hint }}</p> }
                      <p><strong>Time:</strong> {{ p.expectedTimeComplexity }} · <strong>Space:</strong> {{ p.expectedSpaceComplexity }}</p>
                    </details>
                  </article>
                }
              </section>
            </div>
            <button class="primary" type="button" (click)="submitDay()">
              Submit Day &amp; See Full Score →
            </button>
          }

          <!-- ══ STEP 4: Full Score + Complete Review ══ -->
          @if (step === 4 && result) {
            <div class="celebrate">
              <div class="score-banner"
                [class.great]="result.scorePercent >= 70"
                [class.ok]="result.scorePercent >= 40 && result.scorePercent < 70"
                [class.poor]="result.scorePercent < 40">
                <div class="score-number"
                  [class.great]="result.scorePercent >= 70"
                  [class.ok]="result.scorePercent >= 40 && result.scorePercent < 70"
                  [class.poor]="result.scorePercent < 40">
                  {{ result.scorePercent }}%
                </div>
                <div>
                  <strong style="font-size:18px;">Day Complete!</strong>
                  <p style="margin:4px 0 0">
                    <span class="success">+{{ result.earnedPoints }} pts earned</span>
                    @if (result.lostPoints > 0) {
                      <span class="danger"> · -{{ result.lostPoints }} pts penalty</span>
                    }
                    &nbsp;· Total: <strong>{{ result.totalPoints }}</strong>
                  </p>
                </div>
              </div>

              <!-- Full MCQ recap -->
              <h3>MCQ Recap ({{ mcqCorrectCount }}/{{ mcqResults.length }} correct)</h3>
              @for (r of mcqResults; track r.questionId; let ri = $index) {
                <div class="eval-card" [class.correct]="r.correct" [class.wrong]="!r.correct">
                  <div class="eval-label" [class.correct]="r.correct" [class.wrong]="!r.correct">
                    Q{{ ri + 1 }} · {{ r.correct ? '✓' : '✗' }} {{ r.prompt }}
                  </div>
                  @if (!r.correct) {
                    <p style="margin:4px 0 2px; font-size:13px;">
                      Your answer: <span style="color:#c92a2a; font-weight:700;">{{ r.userAnswer || '(none)' }}</span>
                      &nbsp;→ Correct: <span style="color:#1a6b29; font-weight:700;">{{ r.correctAnswer }}</span>
                    </p>
                  }
                  <div class="eval-explanation">💡 {{ r.explanation }}</div>
                </div>
              }

              <!-- Written answers recap -->
              @if (answeredWrittenCount > 0) {
                <div class="step-divider"></div>
                <h3>Written Answers (saved ✓)</h3>
                @for (q of assignment.writtenConceptQuestions; track q) {
                  @if (writtenAnswers[q]?.trim()) {
                    <div class="written-review">
                      <div class="written-q">{{ q }}</div>
                      <div class="written-a">{{ writtenAnswers[q] }}</div>
                    </div>
                  }
                }
                @for (s of assignment.businessScenarios; track s) {
                  @if (writtenAnswers[s]?.trim()) {
                    <div class="written-review">
                      <div class="written-q">{{ s }}</div>
                      <div class="written-a">{{ writtenAnswers[s] }}</div>
                    </div>
                  }
                }
              }

              <div class="step-divider"></div>
              <p class="muted" style="font-size:13px;">
                ✅ Full review saved to <strong>reviews/{{ assignment.id }}.json</strong> on the server — accessible from any machine via the app URL.
              </p>
              @for (line of result.feedback; track line) { <p>{{ line }}</p> }
              @if (result.nextAssignmentAvailable) {
                <button class="primary" type="button" (click)="loadNextDay()">Load Next Day →</button>
              } @else {
                <p>You have finished all available days. Check back tomorrow!</p>
              }
            </div>
          }

          @if (submitError) {
            <div class="card warning" style="margin-top:16px;">
              <h2>Submission failed</h2>
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

  mcqResults: McqResult[] = [];
  showMcqResults = false;
  showWrittenResults = false;

  result: any;
  loading = true;
  error = '';
  submitError = '';

  constructor(
    private api: ApiService,
    private userContext: UserContextService,
    private cd: ChangeDetectorRef
  ) {}

  // ── Computed ───────────────────────────────────────────────────────────────

  get answeredMcqCount() {
    return Object.values(this.answers).filter(Boolean).length;
  }

  get writtenQuestionCount() {
    if (!this.assignment) return 0;
    return (this.assignment.writtenConceptQuestions?.length || 0)
         + (this.assignment.businessScenarios?.length || 0);
  }

  get answeredWrittenCount() {
    const count = Object.values(this.writtenAnswers)
      .filter(a => String(a || '').trim().length > 0).length;
    return Math.min(count, this.writtenQuestionCount);
  }

  get boundedSqlSolved() {
    return Math.min(Number(this.sqlSolved) || 0, this.assignment?.sqlPractice?.length || 0);
  }

  get dailyTotalItems() {
    if (!this.assignment) return 0;
    return 1 + this.assignment.conceptualQuestions.length
             + this.writtenQuestionCount
             + this.assignment.sqlPractice.length;
  }

  get dailyCompletedItems() {
    return (this.notesCompleted ? 1 : 0)
         + this.answeredMcqCount
         + this.answeredWrittenCount
         + this.boundedSqlSolved;
  }

  get dailyCompletionPercent() {
    if (!this.dailyTotalItems) return 0;
    return Math.round((this.dailyCompletedItems / this.dailyTotalItems) * 100);
  }

  get mcqCorrectCount() {
    return this.mcqResults.filter(r => r.correct).length;
  }

  get mcqScorePercent() {
    if (!this.mcqResults.length) return 0;
    return Math.round((this.mcqCorrectCount / this.mcqResults.length) * 100);
  }

  // ── Actions ────────────────────────────────────────────────────────────────

  goToStep(i: number) {
    if (i <= this.step) this.step = i;
  }

  submitMcqs() {
    this.mcqResults = (this.assignment.conceptualQuestions as any[]).map(q => ({
      questionId: q.id,
      prompt: q.prompt,
      options: q.options,
      userAnswer: this.answers[q.id] || '',
      correctAnswer: q.correctAnswer,
      explanation: q.explanation || '',
      correct: (this.answers[q.id] || '') === q.correctAnswer
    }));
    this.showMcqResults = true;
    this.cd.detectChanges();
  }

  proceedFromMcqResults() {
    this.showMcqResults = false;
    this.step = 2;
    this.cd.detectChanges();
  }

  submitWritten() {
    this.showWrittenResults = true;
    this.cd.detectChanges();
  }

  submitDay() {
    this.submitError = '';
    const answers = Object.entries(this.answers)
      .map(([questionId, answer]) => ({ questionId, answer }));

    this.api.submitAssignment({
      email: this.userContext.email(),
      assignmentId: this.assignment.id,
      notesCompleted: this.notesCompleted,
      answers,
      codingSolved: 0,
      sqlSolved: this.boundedSqlSolved
    }).subscribe({
      next: (result) => {
        this.result = result;
        this.step = 4;
        // Fire-and-forget: save the full review to the server
        this.api.saveDayReview({
          email: this.userContext.email(),
          dayId: this.assignment.id,
          topic: this.assignment.topic,
          mcqScore: this.mcqCorrectCount,
          mcqTotal: this.mcqResults.length,
          mcqResults: this.mcqResults,
          writtenAnswers: this.writtenAnswers
        }).subscribe({ error: () => {} });
        this.cd.detectChanges();
      },
      error: (err) => {
        this.submitError = err?.message || 'Start the Spring Boot backend on port 8082, then try again.';
        this.cd.detectChanges();
      }
    });
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────────

  ngOnInit() {
    this.loadNextDay();
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
        this.mcqResults = [];
        this.showMcqResults = false;
        this.showWrittenResults = false;
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
