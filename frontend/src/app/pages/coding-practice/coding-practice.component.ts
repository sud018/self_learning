import { ChangeDetectorRef, Component, ElementRef, HostListener, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/api.service';
import { UserContextService } from '../../core/user-context.service';

@Component({
  selector: 'app-coding-practice',
  imports: [CommonModule, FormsModule],
  template: `
    <section class="page">
      <div class="page-header">
        <div>
          <h1>Coding Practice</h1>
          <p>Hands-on editors for Java, Spring Boot APIs, Angular, SQL, and DSA.</p>
        </div>
      </div>

      @if (loading) {
        <article class="card empty-state">
          <h2>Loading problems...</h2>
          <p>Getting Java and DSA exercises from today's assignment.</p>
        </article>
      }
      @if (error) {
        <article class="card warning empty-state">
          <h2>Backend API is not reachable</h2>
          <p>{{ error }}</p>
        </article>
      }

      @if (!loading && selected) {
        <article class="card progress-card">
          <div class="progress-card-header">
            <div>
              <h2>Coding Completion {{ codingCompletionPercent }}%</h2>
              <p>{{ solvedIds.length }} of {{ problems.length }} problems solved overall</p>
            </div>
            <strong>{{ categoryCompletionPercent }}% {{ activeCategory }}</strong>
          </div>
          <div class="progress-track"><div class="progress-fill" [style.width.%]="codingCompletionPercent"></div></div>
          <div class="progress-breakdown">
            @for (category of categories; track category) {
              <button type="button" [class.active]="activeCategory === category" (click)="selectCategory(category)">
                {{ category }} {{ solvedCount(category) }}/{{ totalCount(category) }}
              </button>
            }
          </div>
        </article>

        <div class="step-tabs coding-tabs">
          @for (category of categories; track category) {
            <button type="button" [class.active]="activeCategory === category" (click)="selectCategory(category)">{{ category }}</button>
          }
        </div>

        <div #codingWorkspace class="leetcode-workspace draggable-workspace" [style.grid-template-columns]="codingGridColumns" [class.dragging]="dragPane">
          <aside class="problem-list">
            <div class="problem-list-header">{{ activeCategory }} Problems</div>
            @for (problem of visibleProblems; track problem.id; let index = $index) {
              <button type="button" [class.active]="selected?.id === problem.id" (click)="select(problem)">
                <span>{{ index + 1 }}. {{ problem.title }}</span>
                <small>{{ problem.category }} · {{ problem.difficulty }}</small>
              </button>
            }
          </aside>

          <div class="split-handle" title="Drag to resize problem list" (mousedown)="startPaneDrag($event, 'left')"></div>

          <section class="problem-statement">
            <div class="task-heading">
              <div>
                <span class="pill">{{ selected.category }}</span>
                <span class="pill muted-pill">{{ selected.difficulty }}</span>
                <h2>{{ selected.title }}</h2>
              </div>
              <div class="timer">
                <strong>{{ formatTime(elapsedSeconds[selected.id] || 0) }}</strong>
                <span>{{ solvedIds.includes(selected.id) ? 'Solved' : 'Timer' }}</span>
              </div>
            </div>

            <p>{{ selected.statement }}</p>

            <h3>Examples</h3>
            <div class="examples">
              @for (example of selected.examples; track example) {
                <code>{{ example }}</code>
              }
            </div>

            <h3>Constraints</h3>
            @for (constraint of selected.constraints; track constraint) {
              <p class="practice-item">{{ constraint }}</p>
            }

            @if (selected.hints?.length) {
              <details>
                <summary>Show hints</summary>
                @for (hint of selected.hints; track hint) {
                  <p>{{ hint }}</p>
                }
              </details>
            }

            <h3>Visible Test Cases</h3>
            @for (test of selected.testCases; track test) {
              <p class="practice-item">{{ test }}</p>
            }
          </section>

          <div class="split-handle" title="Drag to resize editor" (mousedown)="startPaneDrag($event, 'right')"></div>

          <section class="code-workbench">
            <div class="editor-topbar">
              <div>
                <h3>Code</h3>
                <span>{{ selected.language }}</span>
              </div>
              <div class="timer compact-timer">
                <strong>{{ formatTime(elapsedSeconds[selected.id] || 0) }}</strong>
                <span>{{ solvedIds.includes(selected.id) ? 'Solved' : 'Running timer' }}</span>
              </div>
            </div>

            <textarea class="editor leetcode-editor" [(ngModel)]="codeEditors[selected.id]" (focus)="startTimer(selected.id)"></textarea>

            <div class="editor-actions">
              <button class="ghost" type="button" (click)="resetCode()">Reset Starter</button>
              <button class="ghost" type="button" (click)="run()">{{ selected.runnable ? 'Run Sample Tests' : 'Run Checks' }}</button>
              <button class="primary" type="button" (click)="submit()">{{ selected.runnable ? 'Submit Code' : 'Submit Practice' }}</button>
            </div>

            <p class="muted">{{ selected.runnable ? 'Run checks visible tests. Submit checks extra edge cases before marking solved.' : 'Run checks structure and important keywords for this practice item.' }}</p>

            @if (result) {
              <div class="card test-results" [class.celebrate]="result.passed" [class.warning]="!result.passed">
                <h3>{{ result.message }}</h3>
                @for (row of result.results; track row.input) {
                  <div class="result-row">
                    <span><strong>Input</strong> {{ row.input }}</span>
                    <span><strong>Expected</strong> {{ row.expectedOutput }}</span>
                    <span><strong>Your Output</strong> {{ row.userOutput || '(blank)' }}</span>
                    <strong [class.success]="row.passed" [class.danger]="!row.passed">{{ row.passed ? 'Pass' : 'Fail' }}</strong>
                  </div>
                }
              </div>
            }
          </section>
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
  codingGridColumns = '220px 8px minmax(420px, .95fr) 8px minmax(560px, 1.35fr)';
  dragPane: 'left' | 'right' | null = null;
  private listPaneWidth = 220;
  private statementPaneWidth = 430;
  private timerId: number | null = null;

  @ViewChild('codingWorkspace') codingWorkspace?: ElementRef<HTMLElement>;

  constructor(private api: ApiService, private userContext: UserContextService, private cd: ChangeDetectorRef) {}

  get visibleProblems() {
    return this.problems.filter((problem) => problem.category === this.activeCategory);
  }

  get codingCompletionPercent() {
    if (!this.problems.length) {
      return 0;
    }
    return Math.round((this.solvedIds.length / this.problems.length) * 100);
  }

  get categoryCompletionPercent() {
    const total = this.totalCount(this.activeCategory);
    if (!total) {
      return 0;
    }
    return Math.round((this.solvedCount(this.activeCategory) / total) * 100);
  }

  totalCount(category: string) {
    return this.problems.filter((problem) => problem.category === category).length;
  }

  solvedCount(category: string) {
    return this.problems.filter((problem) => problem.category === category && this.solvedIds.includes(problem.id)).length;
  }

  ngOnInit() {
    this.api.todayAssignment(this.userContext.email()).subscribe({
      next: (assignment) => {
        this.problems = [
          ...(assignment.codingTasks || []).map((task: any) => ({ ...task, category: 'Java', language: 'Java', runnable: true, source: 'coding' })),
          ...(assignment.springBootScenarios || []).map((item: string, index: number) => this.toSpringBootProblem(item, index)),
          ...(assignment.angularQuestions || []).map((item: string, index: number) => this.toAngularProblem(item, index)),
          ...(assignment.sqlPractice || []).map((item: string, index: number) => this.toSqlProblem(item, index)),
          ...(assignment.dsaPractice || []).map((problem: any) => this.toDsaEditorProblem(problem))
        ];
        this.selectCategory(this.categories.find((category) => this.problems.some((problem) => problem.category === category)) || 'Java');
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

  ngOnDestroy() {
    this.stopTimer();
  }

  select(problem: any) {
    this.selected = problem;
    this.codeEditors[problem.id] ||= problem.starterCode;
    this.result = null;
    this.startTimer(problem.id);
  }

  selectCategory(category: string) {
    this.activeCategory = category;
    const firstProblem = this.visibleProblems[0];
    if (firstProblem) {
      this.select(firstProblem);
    }
  }

  resetCode() {
    this.codeEditors[this.selected.id] = this.selected.starterCode;
    this.result = null;
  }

  run() {
    if (!this.selected.runnable) {
      this.result = this.localCheck(false);
      this.cd.detectChanges();
      return;
    }
    this.api.runCode({ email: this.userContext.email(), problemId: this.selected.id, code: this.codeEditors[this.selected.id] }).subscribe((result) => {
      this.result = result;
      this.cd.detectChanges();
    }, (error) => {
      this.result = this.errorResult(error);
      this.cd.detectChanges();
    });
  }

  submit() {
    if (!this.selected.runnable) {
      this.result = this.localCheck(true);
      if (this.result.passed && !this.solvedIds.includes(this.selected.id)) {
        this.markSolved(this.selected.id);
      }
      this.cd.detectChanges();
      return;
    }
    this.api.submitCode({ email: this.userContext.email(), problemId: this.selected.id, code: this.codeEditors[this.selected.id] }).subscribe((result) => {
      this.result = result;
      if (result.passed && !this.solvedIds.includes(this.selected.id)) {
        this.solvedIds = [...this.solvedIds, this.selected.id];
      }
      this.cd.detectChanges();
    }, (error) => {
      this.result = this.errorResult(error);
      this.cd.detectChanges();
    });
  }

  startPaneDrag(event: MouseEvent, pane: 'left' | 'right') {
    this.dragPane = pane;
    event.preventDefault();
  }

  @HostListener('document:mousemove', ['$event'])
  resizeCodingPanes(event: MouseEvent) {
    if (!this.dragPane || !this.codingWorkspace) {
      return;
    }
    const rect = this.codingWorkspace.nativeElement.getBoundingClientRect();
    const x = event.clientX - rect.left;
    if (this.dragPane === 'left') {
      this.listPaneWidth = this.clamp(x, 160, 360);
    } else {
      this.statementPaneWidth = this.clamp(x - this.listPaneWidth - 24, 320, 900);
    }
    this.codingGridColumns = `${this.listPaneWidth}px 8px minmax(${this.statementPaneWidth}px, .95fr) 8px minmax(560px, 1.35fr)`;
    this.cd.detectChanges();
  }

  @HostListener('document:mouseup')
  stopPaneDrag() {
    this.dragPane = null;
  }

  startTimer(problemId: string) {
    this.stopTimer();
    this.elapsedSeconds[problemId] ||= 0;
    this.timerId = window.setInterval(() => {
      this.elapsedSeconds = {
        ...this.elapsedSeconds,
        [problemId]: (this.elapsedSeconds[problemId] || 0) + 1
      };
      this.cd.detectChanges();
    }, 1000);
  }

  formatTime(totalSeconds: number) {
    const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
    const seconds = (totalSeconds % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  }

  private stopTimer() {
    if (this.timerId !== null) {
      window.clearInterval(this.timerId);
      this.timerId = null;
    }
  }

  private loadSolvedProgress() {
    this.api.codingProgress(this.userContext.email()).subscribe((progress) => {
      const availableIds = new Set(this.problems.map((problem) => problem.id));
      this.solvedIds = (progress.solvedProblemIds || []).filter((id) => availableIds.has(id));
      this.cd.detectChanges();
    }, () => {});
  }

  private markSolved(problemId: string) {
    this.api.markCodingSolved({ email: this.userContext.email(), problemId }).subscribe((progress) => {
      const availableIds = new Set(this.problems.map((problem) => problem.id));
      this.solvedIds = (progress.solvedProblemIds || []).filter((id) => availableIds.has(id));
      this.cd.detectChanges();
    }, () => {
      this.solvedIds = this.solvedIds.includes(problemId) ? this.solvedIds : [...this.solvedIds, problemId];
      this.cd.detectChanges();
    });
  }

  private toDsaEditorProblem(problem: any) {
    const title = String(problem.title || '').toLowerCase();
    if (title.includes('maximum')) {
      return {
        ...problem,
        category: 'DSA',
        language: 'Java',
        runnable: true,
        testCases: ['[1,5,2] -> 5', '[-3,-1,-7] -> -1'],
        starterCode: 'public int maxValue(int[] nums) {\n  // write Java solution\n  return 0;\n}'
      };
    }
    if (title.includes('count target')) {
      return {
        ...problem,
        category: 'DSA',
        language: 'Java',
        runnable: true,
        testCases: ['[2,1,2,3], 2 -> 2', '[], 5 -> 0'],
        starterCode: 'public int countTarget(int[] nums, int target) {\n  // write Java solution\n  return 0;\n}'
      };
    }
    return {
      ...problem,
      category: 'DSA',
      language: 'Java',
      runnable: true,
      testCases: ['[1,2,3] -> 6', '[] -> 0'],
      starterCode: 'public int solve(int[] nums) {\n  // default DSA practice: return the sum of nums\n  return 0;\n}'
    };
  }

  private toSpringBootProblem(item: string, index: number) {
    return {
      id: `spring-${index + 1}`,
      title: `Spring Boot API Practice ${index + 1}`,
      category: 'Spring Boot',
      language: 'Java / Spring Boot',
      difficulty: index === 0 ? 'Easy' : 'Medium',
      statement: item,
      examples: ['Create controller, DTO, service method, validation, and clear HTTP response handling.'],
      constraints: ['Use REST naming', 'Keep controller thin', 'Use DTOs', 'Add validation/error handling comments'],
      hints: ['Think request DTO -> controller -> service -> response DTO.', 'Mention what status code should be returned for invalid input.'],
      testCases: ['Contains @RestController or @Service', 'Contains DTO/request/response shape', 'Contains validation or error handling'],
      starterCode: '@RestController\n@RequestMapping("/api/orders")\npublic class OrderController {\n\n  // TODO: add DTOs, service dependency, endpoint, validation, and response\n\n}\n',
      runnable: false
    };
  }

  private toAngularProblem(item: string, index: number) {
    return {
      id: `angular-${index + 1}`,
      title: `Angular Practice ${index + 1}`,
      category: 'Angular',
      language: 'TypeScript / Angular',
      difficulty: index === 0 ? 'Easy' : 'Medium',
      statement: item,
      examples: ['Build component/service code with loading, success, empty, and error states.'],
      constraints: ['Use TypeScript types', 'Use HttpClient/service separation', 'Handle loading and error state'],
      hints: ['Start with an interface for the API response.', 'Keep API calls inside a service, not directly in template logic.'],
      testCases: ['Contains interface/type', 'Contains service or HttpClient', 'Contains loading/error state'],
      starterCode: 'interface ApiResponse {\n  id: string;\n}\n\n@Component({\n  selector: "app-practice",\n  template: `<!-- TODO -->`\n})\nexport class PracticeComponent {\n  loading = false;\n  error = "";\n\n  // TODO: inject service and handle data\n}\n',
      runnable: false
    };
  }

  private toSqlProblem(item: string, index: number) {
    return {
      id: `sql-${index + 1}`,
      title: `SQL Query Practice ${index + 1}`,
      category: 'SQL',
      language: 'SQL',
      difficulty: index === 0 ? 'Easy' : 'Medium',
      statement: item,
      examples: ['Write the query a business user could use for filtering, reporting, or auditing.'],
      constraints: ['Use SELECT', 'Avoid SELECT * when possible', 'Use WHERE/JOIN/GROUP BY when relevant'],
      hints: ['Name the table and columns clearly.', 'Think about what question the business is asking.'],
      testCases: ['Contains SELECT', 'Contains FROM', 'Uses a realistic table/column/filter'],
      starterCode: 'SELECT\n  -- columns\nFROM\n  -- table_name\nWHERE\n  -- condition;\n',
      runnable: false
    };
  }

  private localCheck(isSubmit: boolean) {
    const code = (this.codeEditors[this.selected.id] || '').toLowerCase();
    const checks = this.selected.category === 'SQL'
      ? [
          ['Has SELECT', code.includes('select')],
          ['Has FROM', code.includes('from')],
          ['Has filter, join, group, or meaningful condition', /where|join|group by|having|order by/.test(code)]
        ]
      : this.selected.category === 'Angular'
        ? [
            ['Has TypeScript model/interface', /interface|type\s/.test(code)],
            ['Has component/service structure', /component|service|httpclient|inject/.test(code)],
            ['Handles loading or error state', /loading|error|catch|subscribe/.test(code)]
          ]
        : [
            ['Has Spring annotation', /@restcontroller|@service|@requestmapping|@getmapping|@postmapping/.test(code)],
            ['Uses DTO/service/response concept', /dto|service|response|request/.test(code)],
            ['Mentions validation/error/status handling', /valid|error|exception|status|badrequest|notfound/.test(code)]
          ];
    const results = checks.map(([label, passed]) => ({
      input: label,
      expectedOutput: 'Present',
      userOutput: passed ? 'Present' : 'Missing',
      passed
    }));
    const passed = results.every((row) => row.passed);
    return {
      passed,
      results,
      message: passed
        ? (isSubmit ? 'Practice checks passed and marked solved.' : 'Visible structure checks passed.')
        : 'Some structure checks are missing. Improve the editor content and try again.'
    };
  }

  private errorResult(error: Error) {
    return {
      passed: false,
      message: error.message || 'Could not run code.',
      results: []
    };
  }

  private clamp(value: number, min: number, max: number) {
    return Math.max(min, Math.min(max, value));
  }
}
