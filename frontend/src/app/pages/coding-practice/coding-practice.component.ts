import {
  ChangeDetectorRef, Component, ElementRef, HostListener,
  OnDestroy, OnInit, ViewChild
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/api.service';
import { UserContextService } from '../../core/user-context.service';
import { MonacoEditorComponent } from '../../shared/monaco-editor/monaco-editor.component';

@Component({
  selector: 'app-coding-practice',
  standalone: true,
  imports: [CommonModule, FormsModule, MonacoEditorComponent],
  template: `
<section class="lc-page">

  <!-- Category tabs + overall progress -->
  <div class="lc-header">
    <div class="lc-cat-tabs">
      @for (cat of categories; track cat) {
        <button type="button" [class.active]="activeCategory === cat" (click)="selectCategory(cat)">
          {{ cat }}
          @if (!loading) {
            <span class="lc-count">{{ solvedCount(cat) }}/{{ totalCount(cat) }}</span>
          }
        </button>
      }
    </div>
    @if (!loading && problems.length) {
      <div class="lc-global-progress">
        <span class="lc-gp-label">{{ codingCompletionPercent }}% solved</span>
        <div class="lc-gp-bar"><div class="lc-gp-fill" [style.width.%]="codingCompletionPercent"></div></div>
      </div>
    }
  </div>

  @if (loading) {
    <div class="lc-center-state">
      <div class="lc-spinner"></div>
      <p>Loading problems from today's assignment…</p>
    </div>
  }

  @if (error) {
    <article class="card warning empty-state">
      <h2>Backend is not reachable</h2>
      <p>{{ error }}</p>
    </article>
  }

  @if (!loading && !error && selected) {
    <div #workspace class="lc-workspace" [style.grid-template-columns]="gridCols" [class.dragging]="!!dragPane">

      <!-- LEFT: problem list -->
      <aside class="lc-list">
        <div class="lc-list-head">
          <span>{{ activeCategory }}</span>
          <span class="lc-list-badge">{{ solvedCount(activeCategory) }}/{{ totalCount(activeCategory) }}</span>
        </div>
        <div class="lc-list-body">
          @for (p of visibleProblems; track p.id; let i = $index) {
            <button type="button" class="lc-list-item"
              [class.active]="selected?.id === p.id"
              [class.solved]="solvedIds.includes(p.id)"
              (click)="selectProblem(p)">
              <span class="lc-check-icon">{{ solvedIds.includes(p.id) ? '✓' : '' }}</span>
              <span class="lc-list-name">{{ i + 1 }}. {{ p.title }}</span>
              <span class="lc-diff-tag" [attr.data-diff]="normDiff(p.difficulty)">{{ p.difficulty }}</span>
            </button>
          }
        </div>
      </aside>

      <div class="lc-handle" (mousedown)="startDrag($event, 'left')"><div class="lc-handle-bar"></div></div>

      <!-- MIDDLE: problem description -->
      <article class="lc-desc">
        <div class="lc-desc-titlebar">
          <div style="min-width:0">
            <h2 class="lc-desc-title">{{ selected.title }}</h2>
            <div class="lc-desc-meta">
              <span class="lc-diff-badge" [attr.data-diff]="normDiff(selected.difficulty)">{{ selected.difficulty }}</span>
              <span class="lc-cat-badge">{{ selected.category }}</span>
            </div>
          </div>
          <div class="lc-timer-widget">
            <span class="lc-timer-time">{{ formatTime(elapsedSeconds[selected.id] || 0) }}</span>
            <span class="lc-timer-label" [class.solved-label]="solvedIds.includes(selected.id)">
              {{ solvedIds.includes(selected.id) ? '✓ Solved' : '⏱ Timer' }}
            </span>
          </div>
        </div>

        <div class="lc-desc-body">
          <p class="lc-statement">{{ selected.statement }}</p>

          @if (selected.examples?.length) {
            <div class="lc-section">
              @for (ex of selected.examples; track ex; let i = $index) {
                <div class="lc-example">
                  <div class="lc-example-label">Example {{ i + 1 }}</div>
                  <pre class="lc-example-pre">{{ ex }}</pre>
                </div>
              }
            </div>
          }

          @if (selected.constraints?.length) {
            <div class="lc-section">
              <div class="lc-section-title">Constraints</div>
              <ul class="lc-constraints">
                @for (c of selected.constraints; track c) {
                  <li>{{ c }}</li>
                }
              </ul>
            </div>
          }

          @if (selected.hints?.length) {
            <details class="lc-hints">
              <summary>💡 Hints</summary>
              <ul>
                @for (h of selected.hints; track h) { <li>{{ h }}</li> }
              </ul>
            </details>
          }

          <!-- Approach guide in problem panel -->
          <details class="lc-hints lc-approach-guide">
            <summary>🎯 How to think about {{ selected.category }} problems</summary>
            <ol class="lc-approach-ol">
              @for (step of selectedApproach; track step; let si = $index) {
                <li><span class="lc-step-num">{{ si + 1 }}</span>{{ step }}</li>
              }
            </ol>
          </details>
        </div>
      </article>

      <div class="lc-handle" (mousedown)="startDrag($event, 'right')"><div class="lc-handle-bar"></div></div>

      <!-- RIGHT: editor + console + actions -->
      <div #editorPane class="lc-editor-pane" [class.console-dragging]="consoleDragging">

        <div class="lc-editor-topbar">
          <div class="lc-lang-display">
            <span class="lc-lang-dot" [attr.data-cat]="selected.category"></span>
            <span>{{ selected.language || 'Java' }}</span>
          </div>
          <button type="button" class="lc-btn-reset" (click)="resetCode()" title="Reset to starter code">↺ Reset</button>
        </div>

        <div class="lc-editor-area">
          <app-monaco-editor
            [value]="currentCode"
            [language]="editorLanguage"
            (valueChange)="onCodeChange($event)">
          </app-monaco-editor>
        </div>

        <div class="lc-console-handle" (mousedown)="startConsoleDrag($event)">
          <div class="lc-console-handle-bar"></div>
        </div>

        <!-- Console panel -->
        <div class="lc-console" [style.height.px]="consoleHeight">
          <div class="lc-console-tabs">
            <button type="button" [class.active]="consoleTab === 'cases'" (click)="consoleTab = 'cases'">Test Cases</button>
            <button type="button" [class.active]="consoleTab === 'result'" (click)="consoleTab = 'result'">
              Output
              @if (result) {
                <span class="lc-result-dot" [class.pass]="result.passed" [class.fail]="!result.passed"></span>
              }
            </button>
            <!-- Solution tab: always visible; locked until first submit -->
            <button type="button"
              class="lc-sol-tab-btn"
              [class.active]="consoleTab === 'solution'"
              [class.lc-sol-locked]="!solutionVisible"
              (click)="consoleTab = 'solution'">
              Solution
              @if (!solutionVisible) { <span class="lc-lock-icon">🔒</span> }
              @if (solutionVisible) { <span class="lc-sol-dot"></span> }
            </button>
          </div>

          <div class="lc-console-body">
            @if (consoleTab === 'cases') {
              @if (!selected.runnable) {
                <div class="lc-non-runnable-note">
                  <strong>Self-assessment problem.</strong> Write your best solution, then Submit to compare with the model answer.
                </div>
              }
              @for (t of selected.testCases; track t; let i = $index) {
                <div class="lc-tc-row">
                  <span class="lc-tc-num">{{ i + 1 }}</span>
                  <code class="lc-tc-text">{{ t }}</code>
                </div>
              }
              @if (!selected.testCases?.length) {
                <p class="lc-console-empty">No visible test cases for this problem.</p>
              }
            }

            @if (consoleTab === 'result') {
              @if (!result) {
                <p class="lc-console-empty">Run or Submit to see output here.</p>
              }
              @if (result) {
                <div class="lc-result-summary" [class.pass]="result.passed" [class.fail]="!result.passed">
                  {{ result.passed ? '✓ Accepted' : '✗ Not Yet' }} — {{ result.message }}
                </div>
                @for (row of result.results; track row.input; let i = $index) {
                  <div class="lc-result-case">
                    <div class="lc-rc-head">
                      <span>Case {{ i + 1 }}</span>
                      <span class="lc-rc-tag" [class.pass]="row.passed" [class.fail]="!row.passed">
                        {{ row.passed ? 'Passed' : 'Failed' }}
                      </span>
                    </div>
                    <div class="lc-rc-body">
                      <div><strong>Input</strong><code>{{ row.input }}</code></div>
                      <div><strong>Expected</strong><code>{{ row.expectedOutput }}</code></div>
                      @if (!row.passed) {
                        <div><strong>Your Output</strong><code>{{ row.userOutput || '(empty)' }}</code></div>
                      }
                    </div>
                  </div>
                }
                @if (!result.results?.length) {
                  <div class="lc-result-msg">{{ result.message }}</div>
                }
                @if (!selected.runnable && result.passed) {
                  <div class="lc-sol-nudge">
                    Open the <strong>Solution</strong> tab → compare your code with the model answer to see what you got right and what you missed.
                  </div>
                }
              }
            }

            @if (consoleTab === 'solution') {
              @if (!solutionVisible) {
                <div class="lc-sol-locked-msg">
                  <div class="lc-sol-locked-icon">🔒</div>
                  <p><strong>Submit your code first</strong> to unlock the model answer.</p>
                  <p class="lc-sol-locked-sub">Writing your own solution — even an imperfect one — makes the model answer 10× more educational.</p>
                </div>
              } @else {
                <div class="lc-solution-panel">

                  <!-- Step-by-step approach -->
                  <div class="lc-sol-section">
                    <div class="lc-sol-header">🎯 How to approach this problem (step by step)</div>
                    <ol class="lc-sol-steps">
                      @for (step of selectedApproach; track step; let si = $index) {
                        <li><span class="lc-sol-step-num">{{ si + 1 }}</span><span>{{ step }}</span></li>
                      }
                    </ol>
                  </div>

                  <!-- Model answer -->
                  <div class="lc-sol-section">
                    <div class="lc-sol-header">✅ Model Answer</div>
                    @if (selectedModelAnswer) {
                      <pre class="lc-sol-code">{{ selectedModelAnswer }}</pre>
                    } @else {
                      <p class="lc-sol-no-answer">Solve using the approach above and the test cases as validation. The correct logic is described in the hints.</p>
                    }
                  </div>

                  <!-- Self-assessment checklist for non-runnable -->
                  @if (!selected.runnable && selectedSelfCheck.length) {
                    <div class="lc-sol-section">
                      <div class="lc-sol-header">✓ Self-check — does your answer include?</div>
                      <ul class="lc-self-check">
                        @for (item of selectedSelfCheck; track item) {
                          <li>☐ {{ item }}</li>
                        }
                      </ul>
                    </div>
                  }

                  <!-- Key learning points -->
                  @if (selected.keyPoints?.length) {
                    <div class="lc-sol-section">
                      <div class="lc-sol-header">💡 Key learning points</div>
                      <ul class="lc-key-points">
                        @for (pt of selected.keyPoints; track pt) { <li>{{ pt }}</li> }
                      </ul>
                    </div>
                  }

                  <!-- Back to test results -->
                  @if (result) {
                    <div class="lc-sol-section">
                      <button type="button" class="lc-back-to-result" (click)="consoleTab = 'result'">
                        ← View test results / compiler output
                      </button>
                    </div>
                  }

                </div>
              }
            }
          </div>
        </div>

        <!-- Action bar -->
        <div class="lc-action-bar">
          <span class="lc-action-note">
            @if (selected.runnable) {
              Compiled &amp; run on server (JDK 21)
            } @else {
              Write your solution → Submit to see model answer
            }
          </span>
          <div class="lc-action-btns">
            <button type="button" class="lc-btn-run" [disabled]="running" (click)="run()">
              @if (running) { <span class="lc-spinner-sm"></span> } @else { <span>▶</span> }
              Run
            </button>
            <button type="button" class="lc-btn-submit" [disabled]="running" (click)="submit()">Submit</button>
          </div>
        </div>
      </div>
    </div>
  }
</section>
  `
})
export class CodingPracticeComponent implements OnInit, OnDestroy {
  problems: any[] = [];
  categories = ['Java', 'Spring Boot', 'Angular', 'SQL', 'DSA'];
  activeCategory = 'Java';
  selected: any;
  codeEditors: Record<string, string> = {};
  elapsedSeconds: Record<string, number> = {};
  solvedIds: string[] = [];
  result: any;
  loading = true;
  error = '';
  running = false;
  consoleTab: 'cases' | 'result' | 'solution' = 'cases';
  solutionVisible = false;

  listPaneWidth = 240;
  descPaneWidth = 460;
  dragPane: 'left' | 'right' | null = null;

  consoleHeight = 220;
  consoleDragging = false;
  private consoleDragStartY = 0;
  private consoleDragStartHeight = 0;

  @ViewChild('workspace') workspace?: ElementRef<HTMLElement>;
  @ViewChild('editorPane') editorPane?: ElementRef<HTMLElement>;
  private timerId: number | null = null;

  constructor(
    private api: ApiService,
    private userContext: UserContextService,
    private cd: ChangeDetectorRef
  ) {}

  get gridCols() {
    return `${this.listPaneWidth}px 6px minmax(${this.descPaneWidth}px, 1fr) 6px minmax(460px, 1.4fr)`;
  }

  get visibleProblems() {
    return this.problems.filter(p => p.category === this.activeCategory);
  }

  get currentCode() {
    if (!this.selected) return '';
    if (this.codeEditors[this.selected.id] === undefined) {
      this.codeEditors[this.selected.id] = this.selected.starterCode ?? '';
    }
    return this.codeEditors[this.selected.id];
  }

  get editorLanguage(): string {
    if (!this.selected) return 'java';
    switch (this.selected.category) {
      case 'SQL': return 'sql';
      case 'Angular': return 'typescript';
      default: return 'java';
    }
  }

  get codingCompletionPercent() {
    if (!this.problems.length) return 0;
    return Math.round((this.solvedIds.length / this.problems.length) * 100);
  }

  get selectedApproach(): string[] {
    return this.selected?.approach?.length
      ? this.selected.approach
      : this.genericApproach(this.selected?.category);
  }

  get selectedModelAnswer(): string {
    return this.selected?.modelAnswer || '';
  }

  get selectedSelfCheck(): string[] {
    return this.selected?.selfCheck || [];
  }

  totalCount(cat: string) { return this.problems.filter(p => p.category === cat).length; }
  solvedCount(cat: string) { return this.problems.filter(p => p.category === cat && this.solvedIds.includes(p.id)).length; }

  normDiff(diff: string): 'easy' | 'medium' | 'hard' {
    const d = (diff || '').toLowerCase();
    if (d.includes('hard')) return 'hard';
    if (d.includes('med')) return 'medium';
    return 'easy';
  }

  ngOnInit() {
    this.api.todayAssignment(this.userContext.email()).subscribe({
      next: (assignment) => {
        this.problems = [
          ...(assignment.codingTasks || []).map((t: any) => ({ ...t, category: 'Java', language: 'Java', runnable: true })),
          ...(assignment.springBootScenarios || []).map((s: string, i: number) => this.toSpringBootProblem(s, i)),
          ...(assignment.angularQuestions || []).map((q: string, i: number) => this.toAngularProblem(q, i)),
          ...(assignment.sqlPractice || []).map((q: string, i: number) => this.toSqlProblem(q, i)),
          ...(assignment.dsaPractice || []).map((p: any) => this.toDsaProblem(p)),
        ];
        const firstCat = this.categories.find(c => this.problems.some(p => p.category === c)) || 'Java';
        this.selectCategory(firstCat);
        this.loading = false;
        this.cd.detectChanges();
        this.loadSolvedProgress();
      },
      error: () => {
        this.loading = false;
        this.error = 'Start the Spring Boot backend on port 8082, then refresh this page.';
        this.cd.detectChanges();
      }
    });
  }

  ngOnDestroy() { this.stopTimer(); }

  selectProblem(p: any) {
    this.selected = p;
    if (this.codeEditors[p.id] === undefined) this.codeEditors[p.id] = p.starterCode ?? '';
    this.result = null;
    this.solutionVisible = false;
    this.consoleTab = 'cases';
    this.startTimer(p.id);
    this.cd.detectChanges();
  }

  selectCategory(cat: string) {
    this.activeCategory = cat;
    const first = this.visibleProblems[0];
    if (first) this.selectProblem(first);
  }

  onCodeChange(code: string) {
    if (this.selected) this.codeEditors[this.selected.id] = code;
  }

  resetCode() {
    if (!this.selected) return;
    this.codeEditors[this.selected.id] = this.selected.starterCode ?? '';
    this.result = null;
    this.solutionVisible = false;
    this.consoleTab = 'cases';
    this.cd.detectChanges();
  }

  run() {
    if (!this.selected || this.running) return;
    this.running = true;
    this.consoleTab = 'result';
    this.cd.detectChanges();

    if (!this.selected.runnable) {
      this.result = this.localCheck(false);
      this.running = false;
      this.cd.detectChanges();
      return;
    }

    this.api.runCode({ email: this.userContext.email(), problemId: this.selected.id, code: this.codeEditors[this.selected.id] || '' })
      .subscribe({
        next: res => { this.result = res; this.running = false; this.cd.detectChanges(); },
        error: err => { this.result = this.errResult(err); this.running = false; this.cd.detectChanges(); }
      });
  }

  submit() {
    if (!this.selected || this.running) return;
    this.running = true;
    this.consoleTab = 'result';
    this.cd.detectChanges();

    if (!this.selected.runnable) {
      this.result = this.localCheck(true);
      this.solutionVisible = true;
      if (this.result.passed && !this.solvedIds.includes(this.selected.id)) this.markSolved(this.selected.id);
      this.running = false;
      // auto-open solution tab so user sees model answer immediately
      this.consoleTab = 'solution';
      this.cd.detectChanges();
      return;
    }

    this.api.submitCode({ email: this.userContext.email(), problemId: this.selected.id, code: this.codeEditors[this.selected.id] || '' })
      .subscribe({
        next: res => {
          this.result = res;
          this.solutionVisible = true;
          if (res.passed && !this.solvedIds.includes(this.selected.id)) this.solvedIds = [...this.solvedIds, this.selected.id];
          this.running = false;
          this.consoleTab = 'solution';  // always show model answer after submit
          this.cd.detectChanges();
        },
        error: err => { this.result = this.errResult(err); this.running = false; this.cd.detectChanges(); }
      });
  }

  startDrag(event: MouseEvent, pane: 'left' | 'right') {
    this.dragPane = pane;
    event.preventDefault();
  }

  startConsoleDrag(event: MouseEvent) {
    this.consoleDragging = true;
    this.consoleDragStartY = event.clientY;
    this.consoleDragStartHeight = this.consoleHeight;
    event.preventDefault();
  }

  @HostListener('document:mousemove', ['$event'])
  onMouseMove(event: MouseEvent) {
    if (this.consoleDragging && this.editorPane) {
      const paneHeight = this.editorPane.nativeElement.getBoundingClientRect().height;
      const maxHeight = Math.floor(paneHeight * 0.8);
      const delta = this.consoleDragStartY - event.clientY;
      this.consoleHeight = this.clamp(this.consoleDragStartHeight + delta, 100, maxHeight);
      this.cd.detectChanges();
      return;
    }
    if (!this.dragPane || !this.workspace) return;
    const rect = this.workspace.nativeElement.getBoundingClientRect();
    const x = event.clientX - rect.left;
    if (this.dragPane === 'left') {
      this.listPaneWidth = this.clamp(x, 160, 380);
    } else {
      this.descPaneWidth = this.clamp(x - this.listPaneWidth - 16, 280, 780);
    }
    this.cd.detectChanges();
  }

  @HostListener('document:mouseup')
  onMouseUp() {
    this.dragPane = null;
    this.consoleDragging = false;
  }

  startTimer(id: string) {
    this.stopTimer();
    if (this.elapsedSeconds[id] === undefined) this.elapsedSeconds[id] = 0;
    this.timerId = window.setInterval(() => {
      this.elapsedSeconds = { ...this.elapsedSeconds, [id]: (this.elapsedSeconds[id] || 0) + 1 };
      this.cd.detectChanges();
    }, 1000);
  }

  formatTime(secs: number) {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }

  private stopTimer() {
    if (this.timerId !== null) { window.clearInterval(this.timerId); this.timerId = null; }
  }

  private loadSolvedProgress() {
    this.api.codingProgress(this.userContext.email()).subscribe({
      next: p => {
        const ids = new Set(this.problems.map(pr => pr.id));
        this.solvedIds = (p.solvedProblemIds || []).filter((id: string) => ids.has(id));
        this.cd.detectChanges();
      },
      error: () => {}
    });
  }

  private markSolved(id: string) {
    this.api.markCodingSolved({ email: this.userContext.email(), problemId: id }).subscribe({
      next: p => {
        const ids = new Set(this.problems.map(pr => pr.id));
        this.solvedIds = (p.solvedProblemIds || []).filter((id: string) => ids.has(id));
        this.cd.detectChanges();
      },
      error: () => {
        this.solvedIds = this.solvedIds.includes(id) ? this.solvedIds : [...this.solvedIds, id];
        this.cd.detectChanges();
      }
    });
  }

  // ─────────────────────────────────────────────────────────────────────────
  // localCheck — real structural validation for Spring Boot / Angular / SQL
  // Boilerplate code NEVER passes. All required elements must be present.
  // ─────────────────────────────────────────────────────────────────────────
  private localCheck(isSubmit: boolean) {
    const code = this.codeEditors[this.selected.id] || '';
    const starter = this.selected.starterCode || '';
    const cat = this.selected.category;

    const strip = (s: string) => s
      .replace(/\/\/[^\n]*/g, '')
      .replace(/\/\*[\s\S]*?\*\//g, '')
      .replace(/--[^\n]*/g, '');

    // Gate 1: user must have written something beyond the starter template
    const net = strip(code).replace(/\s/g, '');
    const starterNet = strip(starter).replace(/\s/g, '');
    if (net.length <= starterNet.length + 10) {
      return {
        passed: false, results: [],
        message: '📝 Your code is the same as the starter template. Write your own solution — even an imperfect attempt — before submitting.'
      };
    }

    // Gate 2: per-category structural checks
    const checks = this.structuralChecks(cat, code);
    const results = checks.map(c => ({
      input: c.label,
      expectedOutput: '✓ Required',
      userOutput: c.pass ? '✓ Present' : '✗ Missing',
      passed: c.pass
    }));

    const allPass = checks.length === 0 || checks.every(c => c.pass);

    if (!allPass) {
      const missing = checks.filter(c => !c.pass).length;
      return {
        passed: false,
        results,
        message: `${missing} required element(s) missing — see the checklist above. Fix them, then resubmit.`
      };
    }

    return {
      passed: true,
      results,
      message: isSubmit
        ? '✓ All requirements met! The Solution tab below shows the model answer — compare your logic.'
        : 'All checks pass. Hit Submit to record and unlock the full model answer.'
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Structural checks: returns one entry per requirement.
  // All entries must pass for the code to be accepted.
  // Boilerplate code FAILS every check except possibly the first Spring Boot one.
  // ─────────────────────────────────────────────────────────────────────────
  private structuralChecks(cat: string, code: string): Array<{label: string, pass: boolean}> {
    // Work on a comment-stripped copy for accurate detection
    const nc = code
      .replace(/\/\/[^\n]*/g, '')
      .replace(/\/\*[\s\S]*?\*\//g, '')
      .replace(/--[^\n]*/g, '');

    if (cat === 'Spring Boot') {
      return [
        {
          label: '@RestController on the controller class',
          pass: /@RestController/i.test(code)
        },
        {
          // Boilerplate has ONLY @RequestMapping, no method-level mapping → fails
          label: 'HTTP method mapping: @GetMapping / @PostMapping / @PutMapping / @DeleteMapping',
          pass: /@(Get|Post|Put|Delete|Patch)Mapping/i.test(code)
        },
        {
          // Boilerplate has no @Service at all → fails
          label: '@Service class (controller must delegate to a service — no business logic in controller)',
          pass: /@Service\b/i.test(code)
        },
        {
          // Boilerplate has no DTO class → fails
          label: 'Request or Response DTO (class/record whose name contains Request, Response, or Dto)',
          pass: /(?:record|class)\s+\w*(?:Request|Response|Dto|DTO)\s*[(<{]/i.test(code)
        },
        {
          // Boilerplate has no validation → fails
          label: 'Bean validation: @Valid on the parameter and @NotBlank / @NotNull / @Min / @Max on DTO fields',
          pass: /@(Valid|NotBlank|NotNull|NotEmpty|Min|Max|Size|Positive|Email)\b/i.test(code)
        }
      ];
    }

    if (cat === 'Angular') {
      return [
        {
          // Boilerplate has `interface ApiResponse { id: string; }` — only ONE field
          // Require at least 2 typed fields in the interface
          label: 'TypeScript interface with at least 2 typed properties (e.g., id: number; name: string;)',
          pass: (() => {
            const m = code.match(/interface\s+\w+\s*\{([^}]+)\}/);
            if (!m) return false;
            const props = (m[1].match(/\w+\s*\??\s*:\s*\w+/g) || []);
            return props.length >= 2;
          })()
        },
        {
          // Boilerplate has no @Injectable → fails
          label: '@Injectable service class (HttpClient calls must live in the service, not the component)',
          pass: /@Injectable/i.test(code)
        },
        {
          // Boilerplate has no .subscribe( → fails
          label: 'Observable subscription: .subscribe({ next: ..., error: ... })',
          pass: /\.subscribe\s*\(/i.test(code)
        },
        {
          // Boilerplate HAS loading and error BUT with no real handling — still passes this check
          // so we check for subscribe as the real gate above
          label: 'Both loading and error state properties (to handle all 4 UI states)',
          pass: /\bloading\s*[:=]/i.test(code) && /\berror\s*[:=]/i.test(code)
        },
        {
          // Boilerplate has no ngOnDestroy → fails
          label: 'ngOnDestroy + unsubscribe() to prevent memory leaks',
          pass: /ngOnDestroy/i.test(code) || /\.unsubscribe\s*\(\s*\)/i.test(code)
        }
      ];
    }

    if (cat === 'SQL') {
      // For SQL, check the comment-stripped version
      const sqlKeywords = new Set(['where','join','group','order','having','limit','union','select','from','on','inner','left','right','full']);

      // Check 1: SELECT has actual column names (not just whitespace before FROM)
      const selectBlock = nc.match(/SELECT\b([\s\S]*?)\bFROM\b/i);
      const hasColumns = !!(selectBlock && /\w/.test(selectBlock[1])) && !/SELECT\s*\*/i.test(nc);

      // Check 2: FROM is followed by a real table name (not another SQL keyword)
      const fromMatch = nc.match(/\bFROM\b\s+(\w+)/i);
      const hasRealTable = !!(fromMatch && !sqlKeywords.has(fromMatch[1].toLowerCase()));

      // Check 3: WHERE / JOIN / GROUP BY / ORDER BY with actual content following
      const hasClause =
        /\bWHERE\b\s+\w/i.test(nc) ||
        /\b(INNER|LEFT|RIGHT|FULL|CROSS)\s+JOIN\b\s+\w/i.test(nc) ||
        /\bGROUP\s+BY\b\s+\w/i.test(nc) ||
        /\bORDER\s+BY\b\s+\w/i.test(nc);

      return [
        {
          label: 'SELECT with specific column names — not SELECT * and not empty',
          pass: hasColumns
        },
        {
          label: 'FROM with a real table name (e.g., FROM customers c)',
          pass: hasRealTable
        },
        {
          label: 'At least one clause with content: WHERE <condition> / JOIN <table> / GROUP BY <col> / ORDER BY <col>',
          pass: hasClause
        }
      ];
    }

    return [];
  }

  private errResult(err: any) {
    return { passed: false, message: err?.message || 'Could not run code.', results: [] };
  }

  private clamp(v: number, min: number, max: number) { return Math.max(min, Math.min(max, v)); }

  // ─────────────────────────────────────────────────────────────────────────
  // Generic approach steps per category (shown when problem has no custom steps)
  // ─────────────────────────────────────────────────────────────────────────
  private genericApproach(category: string): string[] {
    switch (category) {
      case 'Spring Boot': return [
        'What does the API DO? (Create / Read / Update / Delete) → pick POST / GET / PUT / DELETE',
        'What data comes IN from the client? → Create a Request DTO record with validation: @NotNull, @NotBlank, @Min, @Max',
        'What data goes OUT to the client? → Create a Response DTO (NEVER return a JPA entity directly to the client)',
        'Controller (thin): one method, delegate to Service, return the right HTTP status (201 CREATED, 200 OK, 404 NOT FOUND, 400 BAD REQUEST)',
        'Service: add @Transactional, validate business rules (e.g., "email already exists"), map DTO→Entity→DTO',
        'Repository: extend JpaRepository<Entity, Long> — get save(), findById(), findAll() for free',
        'Error handling: @RestControllerAdvice class, @ExceptionHandler for MethodArgumentNotValidException (400) and custom exceptions',
      ];
      case 'Angular': return [
        'What data shape does the API return? → Write a TypeScript interface (id: number, name: string, ...) — never use "any"',
        'Create an @Injectable service: one class, inject HttpClient, one method per API call that returns Observable<T>',
        'In the component, inject the service in the constructor. Add: data = [], loading = false, error = "" properties',
        'In ngOnInit(), set loading = true, call service.getXxx().subscribe({ next: ..., error: ... })',
        'In the template, handle ALL 4 states: @if (loading), @if (error), @if (!data.length) (empty), @for (item of data)',
        'Use catchError in the service pipe to transform HttpErrorResponse into a user-friendly message',
        'ngOnDestroy(): store the Subscription in private sub? and call this.sub?.unsubscribe() — prevents memory leaks',
      ];
      case 'SQL': return [
        'Read the question: what business information is being requested? (Who? What? When? How many?)',
        'Identify the main table → write FROM <table_name> first (it anchors the rest of the query)',
        'What other tables are needed? → INNER JOIN for required relationship, LEFT JOIN when the right-side row might not exist',
        'Filter rows with WHERE (applied BEFORE grouping): WHERE status = \'active\' AND created_at > \'2024-01-01\'',
        'If you need totals/counts per group → GROUP BY <group_column> with aggregate functions: COUNT(), SUM(), AVG(), MAX(), MIN()',
        'Filter GROUPS with HAVING (applied AFTER grouping): HAVING COUNT(*) > 3  (NOT WHERE — WHERE runs first)',
        'Sort results with ORDER BY <col> DESC/ASC. Limit rows with LIMIT N. Always alias aggregates: COUNT(*) AS order_count',
      ];
      case 'DSA': return [
        'Read the problem twice. Write down clearly: what is the INPUT, what is the OUTPUT?',
        'Work through the examples by hand — trace the expected transformation step by step',
        'Think of the brute-force approach first (nested loops are fine). Get it working before optimising',
        'Ask: "What data structure helps here?" HashMap for O(1) lookup, Stack for LIFO, Queue for FIFO, Set to track seen values',
        'Handle edge cases: empty array, single element, all duplicates, negative numbers, zero',
        'Analyse time complexity: O(n²) brute force, can we get O(n log n) with sorting, or O(n) with HashMap?',
        'Write clean code: meaningful variable names, one responsibility per loop, test against the provided test cases',
      ];
      default: return [
        'Read the problem statement twice and clarify the input/output types',
        'Work through the examples manually — trace the algorithm step by step',
        'Write a simple, correct solution first (readability over cleverness)',
        'Handle edge cases: null/empty input, boundary values, negative numbers',
        'Check your return type matches exactly what the signature says',
        'Test against the provided test cases before submitting',
      ];
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Problem generators for non-runnable categories
  // ─────────────────────────────────────────────────────────────────────────
  private toDsaProblem(problem: any) {
    const title = String(problem.title || '').toLowerCase();
    if (title.includes('maximum')) {
      return { ...problem, category: 'DSA', language: 'Java', runnable: true,
        testCases: ['[1,5,2] -> 5', '[-3,-1,-7] -> -1'],
        starterCode: 'public int maxValue(int[] nums) {\n  // write Java solution\n  return 0;\n}' };
    }
    if (title.includes('count target')) {
      return { ...problem, category: 'DSA', language: 'Java', runnable: true,
        testCases: ['[2,1,2,3], 2 -> 2', '[], 5 -> 0'],
        starterCode: 'public int countTarget(int[] nums, int target) {\n  // write Java solution\n  return 0;\n}' };
    }
    return { ...problem, category: 'DSA', language: 'Java', runnable: true,
      testCases: ['[1,2,3] -> 6', '[] -> 0'],
      starterCode: 'public int solve(int[] nums) {\n  // DSA practice\n  return 0;\n}' };
  }

  private toSpringBootProblem(item: string, i: number) {
    return {
      id: `spring-${i + 1}`,
      title: `Spring Boot ${i + 1}: ${item.split('.')[0].trim().substring(0, 55)}`,
      category: 'Spring Boot', language: 'Java / Spring Boot',
      difficulty: i === 0 ? 'Easy' : 'Medium',
      statement: item,
      examples: [
        'POST /api/orders → 201 CREATED with order ID',
        'GET /api/orders/42 → 200 OK with order details, or 404 NOT FOUND',
        'POST /api/orders with missing required fields → 400 BAD REQUEST with field error map',
      ],
      constraints: [
        'Thin controller — only HTTP concerns, no business logic',
        'Request DTO with @NotNull / @NotBlank / @Min validators',
        'Response DTO (never return the JPA entity directly)',
        '@Service class with @Transactional for write operations',
        'Return correct HTTP status codes (201, 200, 400, 404, 409)',
        '@RestControllerAdvice for global exception handling',
      ],
      hints: [
        'Start with the controller signature: @PostMapping, @Valid @RequestBody, return type',
        'Ask yourself: what can go wrong? Duplicate, not found, invalid input → each needs its own exception',
        'Map DTO → Entity in the service layer, map Entity → Response DTO before returning',
        'The @Valid annotation only works if you also add Spring Validation dependency (already included)',
      ],
      testCases: [
        'Has @RestController and @RequestMapping on the controller class',
        'Has a separate @Service class (controller delegates to it)',
        'Has Request DTO with validation annotations (@NotNull, @NotBlank, etc.)',
        'Has Response DTO (not returning the entity directly)',
        'Returns correct HTTP status codes (uses @ResponseStatus or ResponseEntity)',
        'Has @Transactional on write service methods',
      ],
      runnable: false,
      modelAnswer: this.springBootModelAnswer(),
      approach: this.genericApproach('Spring Boot'),
      selfCheck: [
        'Controller class has @RestController + @RequestMapping("/api/...")',
        'Separate @Service class with business logic and @Transactional',
        'Request DTO with at least one validation annotation (@NotBlank, @Min, @NotNull)',
        'Response DTO — not the JPA entity — returned from the controller',
        'POST returns 201, GET returns 200 or 404, invalid input returns 400',
        '@RestControllerAdvice to handle MethodArgumentNotValidException (returns 400 with field errors)',
      ],
      keyPoints: [
        'Controller = HTTP layer only. Service = business logic. Never mix them.',
        'NEVER return JPA entities to the client — use DTOs to control what data is exposed',
        '@Valid only validates if the DTO has annotations AND you have spring-boot-starter-validation',
        '@Transactional on the service ensures the DB is rolled back on any unchecked exception',
        'Use constructor injection (not @Autowired) — it makes dependencies explicit and testable',
      ],
    };
  }

  private toAngularProblem(item: string, i: number) {
    return {
      id: `angular-${i + 1}`,
      title: `Angular ${i + 1}: ${item.split('.')[0].trim().substring(0, 55)}`,
      category: 'Angular', language: 'TypeScript / Angular',
      difficulty: i === 0 ? 'Easy' : 'Medium',
      statement: item,
      examples: [
        'Component renders a list of items from an API endpoint',
        'Shows a spinner while loading, an error message on failure, empty state when list is empty',
        'Clicking an item navigates to a detail route using Router',
      ],
      constraints: [
        'TypeScript interface for every API response shape (no "any")',
        '@Injectable service wrapping all HttpClient calls',
        'Component handles all 4 states: loading, error, empty, data',
        'Unsubscribe in ngOnDestroy to prevent memory leaks',
        'Use @for with track in templates (Angular 17+)',
      ],
      hints: [
        'Define your interface first — it acts as documentation for the data shape',
        'Service responsibility: HTTP calls only. Component responsibility: UI state only.',
        'catchError in the pipe transforms a raw HttpErrorResponse into a friendly message',
        'The async pipe auto-unsubscribes, OR store the Subscription and call unsubscribe() manually',
      ],
      testCases: [
        'TypeScript interface defined for the API response type',
        '@Injectable service with HttpClient injected via constructor',
        'Component has loading, error, and data properties',
        'Template handles all 4 states: loading, error, empty list, data display',
        'ngOnDestroy unsubscribes to prevent memory leaks',
      ],
      runnable: false,
      modelAnswer: this.angularModelAnswer(),
      approach: this.genericApproach('Angular'),
      selfCheck: [
        'TypeScript interface with specific property types (no "any")',
        '@Injectable service class with HttpClient + a method returning Observable<T>',
        'Component: loading = false, error = "", data = [] properties initialized',
        'Template: @if (loading), @if (error), @if (!data.length), @for (item of data; track item.id)',
        'ngOnDestroy: private sub?: Subscription → this.sub?.unsubscribe()',
        'catchError in the Observable pipe returns a user-friendly error message',
      ],
      keyPoints: [
        'Always define interfaces — "any" defeats TypeScript\'s entire purpose',
        'Keep HTTP calls in services, not in components — it makes them testable and reusable',
        'Memory leaks from forgotten subscriptions cause the browser tab to slow down over time',
        'The 4 states pattern (loading/error/empty/data) is used in EVERY real-world Angular app',
        'Track by id in @for gives Angular a stable key for efficient DOM diffing',
      ],
    };
  }

  private toSqlProblem(item: string, i: number) {
    return {
      id: `sql-${i + 1}`,
      title: `SQL ${i + 1}: ${item.split('.')[0].trim().substring(0, 55)}`,
      category: 'SQL', language: 'SQL',
      difficulty: i === 0 ? 'Easy' : 'Medium',
      statement: item,
      examples: [
        'List orders with customer names → INNER JOIN orders + customers ON customer_id',
        'Count orders per customer → GROUP BY customer_id with COUNT(order_id)',
        'Customers with > 3 orders → HAVING COUNT(order_id) > 3',
      ],
      constraints: [
        'Specific column names in SELECT — avoid SELECT *',
        'Use table aliases (c for customers, o for orders) to keep the query readable',
        'Add WHERE to filter rows, HAVING to filter groups',
        'Use ORDER BY for meaningful sort and LIMIT for result caps',
      ],
      hints: [
        'Start with the simplest possible query, then add clauses one by one',
        'INNER JOIN when every row MUST have a match. LEFT JOIN when the match might not exist.',
        'GROUP BY + COUNT/SUM/AVG turns many rows into one aggregated row per group',
        'HAVING is like WHERE but runs AFTER GROUP BY — use it to filter aggregated results',
      ],
      testCases: [
        'Uses SELECT with specific column names (not SELECT *)',
        'Has a FROM clause with a realistic table name',
        'Uses WHERE, JOIN, GROUP BY, or ORDER BY as appropriate for the question',
        'Aggregation (COUNT/SUM/AVG) with GROUP BY where the question asks for totals',
      ],
      runnable: false,
      modelAnswer: this.sqlModelAnswer(),
      approach: this.genericApproach('SQL'),
      selfCheck: [
        'SELECT lists specific column names with aliases (AS order_count)',
        'FROM with a realistic table name (not "table1")',
        'INNER JOIN or LEFT JOIN with ON <join condition> when using multiple tables',
        'WHERE for row-level filtering (before GROUP BY)',
        'GROUP BY + aggregate function (COUNT, SUM, AVG) when question asks for totals per group',
        'HAVING for group-level filtering (after GROUP BY)',
        'ORDER BY <column> DESC/ASC at the end for readable sorted output',
      ],
      keyPoints: [
        'SELECT * is bad practice: it returns columns you don\'t need and breaks if table schema changes',
        'INNER JOIN: only rows with a match in BOTH tables. LEFT JOIN: all rows from left, NULL for unmatched right.',
        'WHERE filters rows BEFORE grouping. HAVING filters GROUPS AFTER aggregation.',
        'Always alias aggregate functions: COUNT(*) AS order_count — raw aggregates are unreadable',
        'Use table aliases consistently — "c" for customers, "o" for orders, "p" for products',
      ],
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Model answer strings
  // ─────────────────────────────────────────────────────────────────────────
  private springBootModelAnswer(): string {
    return `// ══════════ 1. REQUEST DTO ══════════
// Use a Java record — compact, immutable, no boilerplate
public record CreateOrderRequest(
    @NotNull(message = "customerId is required")
    String customerId,

    @NotEmpty(message = "At least one product required")
    List<@NotBlank String> productIds,

    @Min(value = 1, message = "quantity must be at least 1")
    int quantity
) {}

// ══════════ 2. RESPONSE DTO ══════════
// NEVER return the JPA Entity to the client (it can expose DB internals)
public record OrderResponse(
    String orderId,
    String customerId,
    String status,
    int quantity,
    LocalDateTime createdAt
) {}

// ══════════ 3. CONTROLLER (HTTP layer only — keep it THIN) ══════════
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private final OrderService orderService;  // constructor injection

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    // POST /api/orders → 201 CREATED
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public OrderResponse create(@Valid @RequestBody CreateOrderRequest request) {
        return orderService.create(request);  // ONE LINE — delegate everything
    }

    // GET /api/orders/{id} → 200 OK or 404 NOT FOUND
    @GetMapping("/{id}")
    public OrderResponse findById(@PathVariable String id) {
        return orderService.findById(id)
            .orElseThrow(() -> new ResponseStatusException(
                HttpStatus.NOT_FOUND, "Order not found: " + id));
    }

    // GET /api/orders?status=PENDING → 200 OK with list
    @GetMapping
    public List<OrderResponse> findAll(@RequestParam(required = false) String status) {
        return orderService.findAll(status);
    }
}

// ══════════ 4. SERVICE (BUSINESS LOGIC lives here) ══════════
@Service
public class OrderService {

    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @Transactional          // rolls back DB on any RuntimeException
    public OrderResponse create(CreateOrderRequest request) {
        // Business rule: check for duplicates, inventory, etc.
        // 1. Map DTO → Entity
        Order order = new Order(
            UUID.randomUUID().toString(),
            request.customerId(),
            request.productIds(),
            request.quantity(),
            "PENDING",
            LocalDateTime.now()
        );
        // 2. Save entity
        Order saved = orderRepository.save(order);
        // 3. Map Entity → Response DTO
        return toResponse(saved);
    }

    @Transactional(readOnly = true)   // optimises read-only queries
    public Optional<OrderResponse> findById(String id) {
        return orderRepository.findById(id).map(this::toResponse);
    }

    @Transactional(readOnly = true)
    public List<OrderResponse> findAll(String status) {
        List<Order> orders = status != null
            ? orderRepository.findByStatus(status)
            : orderRepository.findAll();
        return orders.stream().map(this::toResponse).toList();
    }

    private OrderResponse toResponse(Order o) {
        return new OrderResponse(o.getId(), o.getCustomerId(),
            o.getStatus(), o.getQuantity(), o.getCreatedAt());
    }
}

// ══════════ 5. GLOBAL ERROR HANDLER ══════════
// One place handles all validation errors — not in each controller
@RestControllerAdvice
public class GlobalExceptionHandler {

    // @Valid fails → 400 BAD REQUEST with field-level error map
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Map<String, String> handleValidation(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors()
            .forEach(e -> errors.put(e.getField(), e.getDefaultMessage()));
        return errors;
        // Response: { "customerId": "customerId is required", "quantity": "must be >= 1" }
    }
}`;
  }

  private angularModelAnswer(): string {
    return `// ══════════ 1. INTERFACE (data contract) ══════════
// Define BEFORE writing any service or component code
// This is the shape of what the API returns — no "any" allowed
interface Order {
  id: string;
  customerId: string;
  status: 'PENDING' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED';
  quantity: number;
  createdAt: string;  // ISO 8601 string from JSON
}

interface ApiErrorResponse {
  message: string;
  status: number;
}

// ══════════ 2. SERVICE (HTTP layer — lives here, not in components) ══════════
@Injectable({ providedIn: 'root' })
export class OrderService {
  private readonly baseUrl = '/api/orders';  // relative, not hardcoded host

  constructor(private http: HttpClient) {}

  getOrders(status?: string): Observable<Order[]> {
    const params = status ? { params: { status } } : {};
    return this.http.get<Order[]>(this.baseUrl, params).pipe(
      catchError((err: HttpErrorResponse) =>
        throwError(() => ({
          message: err.error?.message || \`Server error \${err.status}\`,
          status: err.status
        } as ApiErrorResponse))
      )
    );
  }

  getOrder(id: string): Observable<Order> {
    return this.http.get<Order>(\`\${this.baseUrl}/\${id}\`);
  }

  createOrder(data: Omit<Order, 'id' | 'createdAt' | 'status'>): Observable<Order> {
    return this.http.post<Order>(this.baseUrl, data);
  }
}

// ══════════ 3. COMPONENT ══════════
@Component({
  selector: 'app-orders',
  standalone: true,
  imports: [CommonModule],
  template: \`
    <!-- State 1: loading -->
    @if (loading) {
      <div class="loading">Loading orders…</div>
    }

    <!-- State 2: error -->
    @if (error) {
      <div class="error-box">
        <p>{{ error }}</p>
        <button (click)="loadOrders()">Retry</button>
      </div>
    }

    <!-- States 3 & 4: empty or data (only shown when not loading AND no error) -->
    @if (!loading && !error) {
      @if (orders.length === 0) {
        <!-- State 3: empty -->
        <p class="empty">No orders yet.</p>
      } @else {
        <!-- State 4: data -->
        @for (order of orders; track order.id) {
          <div class="order-card" [class]="'status-' + order.status.toLowerCase()">
            <span class="order-id">{{ order.id }}</span>
            <span class="status">{{ order.status }}</span>
            <span class="qty">Qty: {{ order.quantity }}</span>
          </div>
        }
        <p class="count">Total: {{ orders.length }} orders</p>
      }
    }
  \`
})
export class OrdersComponent implements OnInit, OnDestroy {
  orders: Order[] = [];
  loading = false;
  error = '';
  private sub?: Subscription;  // store to unsubscribe later

  constructor(private orderService: OrderService) {}

  ngOnInit() {
    this.loadOrders();
  }

  loadOrders() {
    this.loading = true;
    this.error = '';            // clear previous error on each attempt
    this.sub = this.orderService.getOrders().subscribe({
      next: (orders) => {
        this.orders = orders;
        this.loading = false;   // always set loading = false in both next AND error
      },
      error: (err: ApiErrorResponse) => {
        this.error = err.message;
        this.loading = false;   // if you forget this, the spinner never stops
      }
    });
  }

  ngOnDestroy() {
    // CRITICAL: unsubscribe when component is destroyed
    // Without this, the callback still fires on destroyed components → memory leak
    this.sub?.unsubscribe();
  }
}`;
  }

  private sqlModelAnswer(): string {
    return `-- ══════════ EXAMPLE: Orders report with customer info ══════════
-- Business question: Show all completed orders from the last 30 days,
--   grouped by customer, sorted by total revenue descending, top 10 only.

SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name  AS customer_name,
    c.email,
    COUNT(o.order_id)                   AS total_orders,   -- how many orders
    SUM(o.amount)                       AS total_revenue,  -- sum of all order amounts
    AVG(o.amount)                       AS avg_order_size, -- useful for segmentation
    MAX(o.created_at)                   AS last_order_date -- when they last ordered

FROM customers c                        -- start with the main table

-- INNER JOIN: only include customers who placed at least one order
INNER JOIN orders o
    ON c.customer_id = o.customer_id

WHERE
    o.status = 'COMPLETED'                               -- filter rows (runs BEFORE GROUP BY)
    AND o.created_at >= CURRENT_DATE - INTERVAL '30 days'

GROUP BY
    c.customer_id,    -- group by all non-aggregate columns in SELECT
    c.first_name,
    c.last_name,
    c.email

HAVING
    COUNT(o.order_id) >= 1   -- filter GROUPS after aggregation (not rows)
                             -- e.g., "only customers with 3+ orders": HAVING COUNT(*) >= 3

ORDER BY
    total_revenue DESC       -- highest spenders first

LIMIT 10;                    -- top 10 only


-- ══════════ JOIN TYPE REFERENCE ══════════
-- INNER JOIN: rows that match in BOTH tables. Customers with no orders are excluded.
-- LEFT  JOIN: ALL rows from the LEFT table + matched rows from right (NULLs for no match)
--             Use when: "show all customers even if they have no orders"
-- RIGHT JOIN: ALL rows from RIGHT. Rarely used — rewrite as LEFT JOIN for clarity.


-- ══════════ AGGREGATE FUNCTIONS ══════════
-- COUNT(*)        → total row count (includes NULLs)
-- COUNT(col)      → count non-NULL values in that column
-- SUM(col)        → sum (ignores NULLs)
-- AVG(col)        → average (ignores NULLs)
-- MAX(col)        → highest value
-- MIN(col)        → lowest value
-- Always alias: COUNT(*) AS order_count — raw aggregates have ugly column names


-- ══════════ WHERE vs HAVING ══════════
-- WHERE  filters ROWS   before grouping  → fast (uses indexes)
-- HAVING filters GROUPS after  grouping  → slow if overused
-- Rule: use WHERE whenever possible, HAVING only for aggregated conditions


-- ══════════ SUBQUERY EXAMPLE ══════════
-- Find customers whose average order is above the overall average
SELECT customer_id, AVG(amount) AS avg_order
FROM orders
GROUP BY customer_id
HAVING AVG(amount) > (
    SELECT AVG(amount) FROM orders  -- correlated subquery
);`;
  }
}
