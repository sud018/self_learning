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

  <!-- Loading -->
  @if (loading) {
    <div class="lc-center-state">
      <div class="lc-spinner"></div>
      <p>Loading problems from today's assignment…</p>
    </div>
  }

  <!-- Error -->
  @if (error) {
    <article class="card warning empty-state">
      <h2>Backend is not reachable</h2>
      <p>{{ error }}</p>
    </article>
  }

  <!-- 3-pane workspace -->
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

      <!-- drag handle -->
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
        </div>
      </article>

      <!-- drag handle -->
      <div class="lc-handle" (mousedown)="startDrag($event, 'right')"><div class="lc-handle-bar"></div></div>

      <!-- RIGHT: editor + console + actions -->
      <div class="lc-editor-pane">

        <!-- editor topbar -->
        <div class="lc-editor-topbar">
          <div class="lc-lang-display">
            <span class="lc-lang-dot" [attr.data-cat]="selected.category"></span>
            <span>{{ selected.language || 'Java' }}</span>
          </div>
          <button type="button" class="lc-btn-reset" (click)="resetCode()" title="Reset to starter code">↺ Reset</button>
        </div>

        <!-- Monaco editor -->
        <div class="lc-editor-area">
          <app-monaco-editor
            [value]="currentCode"
            [language]="editorLanguage"
            (valueChange)="onCodeChange($event)">
          </app-monaco-editor>
        </div>

        <!-- Console panel -->
        <div class="lc-console">
          <div class="lc-console-tabs">
            <button type="button" [class.active]="consoleTab === 'cases'" (click)="consoleTab = 'cases'">Test Cases</button>
            <button type="button" [class.active]="consoleTab === 'result'" (click)="consoleTab = 'result'">
              Output
              @if (result) {
                <span class="lc-result-dot" [class.pass]="result.passed" [class.fail]="!result.passed"></span>
              }
            </button>
          </div>

          <div class="lc-console-body">
            @if (consoleTab === 'cases') {
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
                  {{ result.passed ? '✓ Accepted' : '✗ Wrong Answer' }} — {{ result.message }}
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
                        <div><strong>Output</strong><code>{{ row.userOutput || '(empty)' }}</code></div>
                      }
                    </div>
                  </div>
                }
                @if (!result.results?.length) {
                  <div class="lc-result-msg">{{ result.message }}</div>
                }
              }
            }
          </div>
        </div>

        <!-- Action bar -->
        <div class="lc-action-bar">
          <span class="lc-action-note">
            {{ selected.runnable ? 'Compiled & run on server (JDK)' : 'Structure keyword check only' }}
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
  consoleTab: 'cases' | 'result' = 'cases';

  listPaneWidth = 240;
  descPaneWidth = 460;
  dragPane: 'left' | 'right' | null = null;

  @ViewChild('workspace') workspace?: ElementRef<HTMLElement>;
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
      if (this.result.passed && !this.solvedIds.includes(this.selected.id)) this.markSolved(this.selected.id);
      this.running = false;
      this.cd.detectChanges();
      return;
    }

    this.api.submitCode({ email: this.userContext.email(), problemId: this.selected.id, code: this.codeEditors[this.selected.id] || '' })
      .subscribe({
        next: res => {
          this.result = res;
          if (res.passed && !this.solvedIds.includes(this.selected.id)) this.solvedIds = [...this.solvedIds, this.selected.id];
          this.running = false;
          this.cd.detectChanges();
        },
        error: err => { this.result = this.errResult(err); this.running = false; this.cd.detectChanges(); }
      });
  }

  startDrag(event: MouseEvent, pane: 'left' | 'right') {
    this.dragPane = pane;
    event.preventDefault();
  }

  @HostListener('document:mousemove', ['$event'])
  onMouseMove(event: MouseEvent) {
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
  onMouseUp() { this.dragPane = null; }

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
      title: `Spring Boot Practice ${i + 1}`,
      category: 'Spring Boot', language: 'Java / Spring Boot',
      difficulty: i === 0 ? 'Easy' : 'Medium',
      statement: item,
      examples: ['Design controller → service → repository flow with DTOs, validation, and error handling.'],
      constraints: ['Thin controller', 'Use DTOs', 'Return correct HTTP status codes', 'Add validation'],
      hints: ['Think request DTO → controller → service → response DTO.', 'What status for invalid input?'],
      testCases: ['Contains @RestController or @Service', 'Contains DTO/request/response', 'Contains validation or error handling'],
      starterCode: '@RestController\n@RequestMapping("/api/orders")\npublic class OrderController {\n\n  // TODO: inject service, add endpoint, DTO, validation\n\n}\n',
      runnable: false
    };
  }

  private toAngularProblem(item: string, i: number) {
    return {
      id: `angular-${i + 1}`,
      title: `Angular Practice ${i + 1}`,
      category: 'Angular', language: 'TypeScript / Angular',
      difficulty: i === 0 ? 'Easy' : 'Medium',
      statement: item,
      examples: ['Build a component with loading, success, empty, and error states.'],
      constraints: ['TypeScript interfaces', 'Service separation', 'Handle loading/error state'],
      hints: ['Start with an interface for the API response.', 'Keep API calls in a service.'],
      testCases: ['Contains interface/type', 'Contains service or HttpClient', 'Contains loading/error'],
      starterCode: 'interface ApiResponse {\n  id: string;\n}\n\n@Component({\n  selector: "app-practice",\n  template: `<!-- TODO -->`\n})\nexport class PracticeComponent {\n  loading = false;\n  error = "";\n  // TODO: inject service and handle data\n}\n',
      runnable: false
    };
  }

  private toSqlProblem(item: string, i: number) {
    return {
      id: `sql-${i + 1}`,
      title: `SQL Practice ${i + 1}`,
      category: 'SQL', language: 'SQL',
      difficulty: i === 0 ? 'Easy' : 'Medium',
      statement: item,
      examples: ['Write a query a business user would use for filtering, reporting, or auditing.'],
      constraints: ['Use SELECT', 'Avoid SELECT *', 'Use WHERE / JOIN / GROUP BY as needed'],
      hints: ['Name the table and columns clearly.', 'Think about what business question this answers.'],
      testCases: ['Contains SELECT', 'Contains FROM', 'Uses realistic table/column/filter'],
      starterCode: 'SELECT\n  -- columns\nFROM\n  -- table_name\nWHERE\n  -- condition;\n',
      runnable: false
    };
  }

  private localCheck(isSubmit: boolean) {
    const code = (this.codeEditors[this.selected.id] || '').toLowerCase();
    const checks: [string, boolean][] =
      this.selected.category === 'SQL'
        ? [['Has SELECT', code.includes('select')], ['Has FROM', code.includes('from')], ['Has filter or join', /where|join|group by|having|order by/.test(code)]]
        : this.selected.category === 'Angular'
          ? [['Has interface/type', /interface|type\s/.test(code)], ['Has component/service', /component|service|httpclient|inject/.test(code)], ['Handles loading/error', /loading|error|catch|subscribe/.test(code)]]
          : [['Has Spring annotation', /@restcontroller|@service|@requestmapping|@getmapping|@postmapping/.test(code)], ['Uses DTO/service/response', /dto|service|response|request/.test(code)], ['Mentions validation/error/status', /valid|error|exception|status|badrequest|notfound/.test(code)]];

    const results = checks.map(([label, passed]) => ({ input: label, expectedOutput: 'Present', userOutput: passed ? 'Present' : 'Missing', passed }));
    const passed = results.every(r => r.passed);
    return {
      passed, results,
      message: passed
        ? (isSubmit ? 'All checks passed. Marked as solved.' : 'Structure checks passed.')
        : 'Some checks failed. Improve your code and try again.'
    };
  }

  private errResult(err: any) {
    return { passed: false, message: err?.message || 'Could not run code.', results: [] };
  }

  private clamp(v: number, min: number, max: number) { return Math.max(min, Math.min(max, v)); }
}
