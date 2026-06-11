"""Rewrite days 61-67: Angular Components, Templates, Data Binding, Directives, Services, DI, Routing."""
import json, os
DATA_DIR = "backend/data/curriculum"

CURRICULUM = {

"day-061": {
"notes": """# Angular Components: Anatomy, Lifecycle Hooks, and Standalone Architecture

## What is a Component?
An Angular component is the fundamental building block of an Angular application. Every visible UI element is a component — it combines an HTML template, TypeScript logic, and CSS styles.

```typescript
// Standalone component (Angular 14+ preferred approach)
@Component({
  selector: 'app-order-card',          // HTML tag: <app-order-card />
  standalone: true,
  imports: [CommonModule, RouterLink],  // explicit imports — no NgModule needed
  templateUrl: './order-card.component.html',
  styleUrls: ['./order-card.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush  // performance optimization
})
export class OrderCardComponent {
  @Input() order!: Order;              // receives data from parent
  @Output() cancelled = new EventEmitter<string>(); // sends events to parent

  cancelOrder() {
    this.cancelled.emit(this.order.id);
  }
}
```

## @Input and @Output — Component Communication
```typescript
// PARENT component
@Component({
  template: `
    <app-order-card
      [order]="selectedOrder"
      (cancelled)="onOrderCancelled($event)"
    />
  `
})
export class OrderListComponent {
  selectedOrder: Order = { id: 'o1', status: 'PENDING', total: 99.99 };

  onOrderCancelled(orderId: string) {
    console.log('Cancel order:', orderId);
  }
}

// CHILD component
export class OrderCardComponent {
  @Input({ required: true }) order!: Order;  // required: true (Angular 16+)
  @Output() cancelled = new EventEmitter<string>();
}
```

## Lifecycle Hooks
```typescript
@Component({ selector: 'app-user', standalone: true })
export class UserComponent implements OnInit, OnChanges, OnDestroy {
  @Input() userId!: string;
  user: User | null = null;
  private destroy$ = new Subject<void>();

  // 1. ngOnChanges — called before ngOnInit and when @Input changes
  ngOnChanges(changes: SimpleChanges) {
    if (changes['userId'] && !changes['userId'].firstChange) {
      this.loadUser(); // reload when userId input changes
    }
  }

  // 2. ngOnInit — component initialised, @Inputs available (most common hook)
  ngOnInit() {
    this.loadUser();
  }

  // 3. ngOnDestroy — cleanup (unsubscribe, clear timers)
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadUser() {
    this.userService.getUser(this.userId)
      .pipe(takeUntil(this.destroy$))  // auto-unsubscribe on destroy
      .subscribe(u => this.user = u);
  }
}

// Full lifecycle order:
// constructor → ngOnChanges → ngOnInit → ngDoCheck → ngAfterContentInit
// → ngAfterContentChecked → ngAfterViewInit → ngAfterViewChecked → ngOnDestroy
```

## ChangeDetection.OnPush — Performance
```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush  // check only on:
  // 1. @Input reference changes (not mutations)
  // 2. Events from the component's template
  // 3. Async pipe emitting new value
  // 4. markForCheck() or detectChanges() called manually
})
export class ProductListComponent {
  @Input() products: Product[] = [];

  // WRONG with OnPush: mutating input doesn't trigger CD
  // products.push(newProduct) → UI doesn't update

  // CORRECT: new reference triggers CD
  // this.products = [...this.products, newProduct]
}
```

## ViewChild and ContentChild
```typescript
@Component({
  template: `<input #nameInput type="text" /> <app-child #child />`
})
export class ParentComponent implements AfterViewInit {
  @ViewChild('nameInput') nameInput!: ElementRef<HTMLInputElement>;
  @ViewChild(ChildComponent) child!: ChildComponent;

  ngAfterViewInit() {
    this.nameInput.nativeElement.focus(); // DOM access after view initialised
    this.child.doSomething();
  }
}
```

## Common Mistakes
1. **Accessing @ViewChild in ngOnInit:** ViewChild is available only after `ngAfterViewInit`.
2. **Mutating @Input arrays with OnPush:** `push()` doesn't change the array reference — CD skipped. Always create new arrays.
3. **Memory leaks:** subscribing to Observables without unsubscribing in `ngOnDestroy`.
4. **Missing `standalone: true`:** older NgModule pattern requires declaring components in a module.
""",
"mcqs": [
  {"id":"d61q1","prompt":"What does the `@Component` `selector` property define?","options":["The component's CSS class","The HTML tag used to render the component in templates — `selector: 'app-order-card'` means `<app-order-card />` in templates","The component's route path","The component's module"],"correctAnswer":"The HTML tag used to render the component in templates — `selector: 'app-order-card'` means `<app-order-card />` in templates","explanation":"The selector is a CSS selector Angular uses to identify where to insert the component. 'app-order-card' → element selector. '.app-order-card' → class selector. '[appDirective]' → attribute selector used for directives."},
  {"id":"d61q2","prompt":"When is `ngOnChanges` called?","options":["Only once, before ngOnInit","Before ngOnInit AND whenever an @Input property changes — receives SimpleChanges object with previous and current values","After ngOnInit only","Only when the component is destroyed"],"correctAnswer":"Before ngOnInit AND whenever an @Input property changes — receives SimpleChanges object with previous and current values","explanation":"ngOnChanges: called first (before ngOnInit) when any @Input changes. SimpleChanges: { userId: { previousValue: 'u1', currentValue: 'u2', firstChange: false } }. Use to react to @Input changes without rerunning full ngOnInit."},
  {"id":"d61q3","prompt":"What is `ChangeDetectionStrategy.OnPush`?","options":["Pushes data to child components","Restricts change detection to run only when @Input references change, events fire, or markForCheck() is called — avoids unnecessary checks on every CD cycle","Enables push notifications","OnPush is the default strategy"],"correctAnswer":"Restricts change detection to run only when @Input references change, events fire, or markForCheck() is called — avoids unnecessary checks on every CD cycle","explanation":"Default CD: Angular checks every component on every browser event. OnPush: only checks when inputs change by reference. For a list of 100 items with OnPush, only changed items are re-checked. Critical for performance in large applications."},
  {"id":"d61q4","prompt":"What does `@Output() cancelled = new EventEmitter<string>()` do?","options":["Listens for external events","Creates an output property — the child component emits events via `cancelled.emit(id)` which the parent listens to with `(cancelled)='handler($event)'`","Creates a two-way binding","Outputs data to the console"],"correctAnswer":"Creates an output property — the child component emits events via `cancelled.emit(id)` which the parent listens to with `(cancelled)='handler($event)'`","explanation":"@Output + EventEmitter: child-to-parent communication. cancelled.emit('order-1') → parent's (cancelled)='onCancelled($event)' receives 'order-1' as $event. EventEmitter<string> specifies the event payload type."},
  {"id":"d61q5","prompt":"When is `ngAfterViewInit` called and why is @ViewChild accessed there?","options":["Before ngOnInit","After the component's view and all child views are fully initialised — @ViewChild references are only available after the template is rendered","During constructor","@ViewChild works in ngOnInit too"],"correctAnswer":"After the component's view and all child views are fully initialised — @ViewChild references are only available after the template is rendered","explanation":"@ViewChild queries the DOM. The DOM isn't ready until ngAfterViewInit. Accessing @ViewChild in ngOnInit: null reference. ngAfterViewInit: the template element exists, @ViewChild is resolved. Always access DOM elements in ngAfterViewInit."},
  {"id":"d61q6","prompt":"What is a standalone component in Angular 14+?","options":["A component with no dependencies","A component that doesn't require declaration in an NgModule — imports its own dependencies directly via `imports: []` in @Component decorator","A component that runs in isolation","Standalone means no @Input/@Output"],"correctAnswer":"A component that doesn't require declaration in an NgModule — imports its own dependencies directly via `imports: []` in @Component decorator","explanation":"Traditional: declare component in NgModule.declarations, import dependencies in NgModule.imports. Standalone: component directly declares its imports (standalone: true). Simpler, more explicit, tree-shakeable. Angular 17+ makes standalone the default."},
  {"id":"d61q7","prompt":"What is the correct way to avoid memory leaks from RxJS subscriptions in a component?","options":["Call unsubscribe() in ngOnInit","Use takeUntil(destroy$) where destroy$ is a Subject that emits in ngOnDestroy — auto-cancels all subscriptions when component is destroyed","Angular unsubscribes automatically","Use setTimeout to unsubscribe"],"correctAnswer":"Use takeUntil(destroy$) where destroy$ is a Subject that emits in ngOnDestroy — auto-cancels all subscriptions when component is destroyed","explanation":"Pattern: private destroy$ = new Subject<void>(). In observable chains: .pipe(takeUntil(this.destroy$)). In ngOnDestroy: this.destroy$.next(); this.destroy$.complete(). All subscriptions using takeUntil auto-complete when the subject emits."},
  {"id":"d61q8","prompt":"What happens with OnPush if you mutate an @Input array with `push()`?","options":["The UI updates immediately","Angular doesn't detect the change — the array reference is the same. UI not updated. Fix: create a new array: [...existing, newItem]","Push triggers re-render","OnPush doesn't work with arrays"],"correctAnswer":"Angular doesn't detect the change — the array reference is the same. UI not updated. Fix: create a new array: [...existing, newItem]","explanation":"OnPush compares input values by reference (===). products.push(item): same reference → CD skipped. this.products = [...this.products, item]: new reference → CD triggered. Immutable data patterns are required for OnPush to work correctly."},
  {"id":"d61q9","prompt":"What is the order of lifecycle hooks for a component that receives @Input?","options":["ngOnInit → ngOnChanges → ngAfterViewInit","constructor → ngOnChanges → ngOnInit → ngAfterContentInit → ngAfterViewInit → ngOnDestroy","ngOnInit → constructor → ngOnChanges","ngAfterViewInit → ngOnInit → constructor"],"correctAnswer":"constructor → ngOnChanges → ngOnInit → ngAfterContentInit → ngAfterViewInit → ngOnDestroy","explanation":"Full order: constructor (class instantiated) → ngOnChanges (inputs set) → ngOnInit (component ready) → ngDoCheck → ngAfterContentInit → ngAfterContentChecked → ngAfterViewInit → ngAfterViewChecked → [updates: ngOnChanges/ngDoCheck] → ngOnDestroy."},
  {"id":"d61q10","prompt":"What does `@Input({ required: true })` do in Angular 16+?","options":["Makes the input optional","Throws a compile-time error if the parent component doesn't provide this input — eliminates null check boilerplate","Makes the input two-way","Required inputs are always strings"],"correctAnswer":"Throws a compile-time error if the parent component doesn't provide this input — eliminates null check boilerplate","explanation":"Angular 16+ required inputs: @Input({ required: true }) order!: Order — Angular CLI and the template compiler enforce that the parent always provides this value. Previously you'd use ngOnInit assertions or the ! non-null assertion."}
],
"writtenConceptQuestions": [
  "Design a ProductCard component: @Input for product data, @Output for addToCart event, OnPush change detection, and proper ngOnDestroy cleanup.",
  "Explain all Angular lifecycle hooks in order. For which tasks is each hook most appropriate?",
  "What is ChangeDetectionStrategy.OnPush? Show a case where it breaks with array mutation and the correct immutable fix.",
  "What is a standalone component vs NgModule-based? Show the migration of a component from NgModule to standalone.",
  "Show @ViewChild usage: focus an input element in ngAfterViewInit. Why can't you do it in ngOnInit?",
  "How do you prevent memory leaks from RxJS subscriptions? Show the takeUntil pattern with destroy$.",
  "Show parent-child communication: parent passes order via @Input, child emits cancel event via @Output EventEmitter."
],
"businessScenarios": [
  "A dashboard with 50 product cards is slow — Angular checks every card on every mouse move. Add OnPush to ProductCardComponent and fix all array mutations to use spread operator.",
  "After navigating away from UserProfileComponent, an HTTP subscription keeps running, causing null pointer errors when the response arrives. Add ngOnDestroy with takeUntil cleanup.",
  "A child CartItemComponent needs to tell its parent to remove an item. Design the @Output EventEmitter pattern and the parent handler."
]
},

"day-062": {
"notes": """# Angular Templates: Interpolation, Structural Directives, and Control Flow

## Template Syntax Overview
```html
<!-- Interpolation: {{ expression }} -->
<h1>Welcome, {{ user.firstName }} {{ user.lastName }}</h1>
<p>Order total: {{ order.total | currency:'USD' }}</p>

<!-- Property binding: [property]="expression" -->
<img [src]="product.imageUrl" [alt]="product.name" />
<button [disabled]="form.invalid">Submit</button>
<app-card [title]="'Hello'" [count]="42" />

<!-- Event binding: (event)="handler($event)" -->
<button (click)="onSubmit()">Submit</button>
<input (keyup.enter)="onSearch()" (input)="onInputChange($event)" />

<!-- Two-way binding: [(ngModel)]="property" -->
<input [(ngModel)]="searchTerm" placeholder="Search..." />
<!-- Equivalent to: [ngModel]="searchTerm" (ngModelChange)="searchTerm=$event" -->
```

## Angular 17 Control Flow (@if, @for, @switch)
```html
<!-- @if / @else if / @else (replaces *ngIf) -->
@if (isLoggedIn) {
  <app-dashboard />
} @else if (isLoading) {
  <app-spinner />
} @else {
  <app-login />
}

<!-- @for with track (replaces *ngFor) — track is REQUIRED -->
@for (product of products; track product.id) {
  <app-product-card [product]="product" />
} @empty {
  <p>No products found.</p>
}

<!-- @switch (replaces ngSwitch) -->
@switch (order.status) {
  @case ('PENDING')    { <span class="badge-yellow">Pending</span> }
  @case ('SHIPPED')    { <span class="badge-blue">Shipped</span> }
  @case ('DELIVERED')  { <span class="badge-green">Delivered</span> }
  @default             { <span class="badge-grey">Unknown</span> }
}
```

## Old Structural Directives (still common in codebases)
```html
<!-- *ngIf with else template -->
<div *ngIf="user; else loading">
  <h2>{{ user.name }}</h2>
</div>
<ng-template #loading><app-spinner /></ng-template>

<!-- *ngFor with index, first, last -->
<li *ngFor="let item of items; let i = index; let last = last"
    [class.last]="last">
  {{ i + 1 }}. {{ item.name }}
</li>

<!-- ngSwitch -->
<div [ngSwitch]="status">
  <span *ngSwitchCase="'ACTIVE'">Active</span>
  <span *ngSwitchDefault>Inactive</span>
</div>
```

## Built-in Pipes
```html
<!-- String pipes -->
{{ 'hello world' | uppercase }}          <!-- HELLO WORLD -->
{{ 'HELLO' | lowercase }}                <!-- hello -->
{{ 'john doe' | titlecase }}             <!-- John Doe -->
{{ longText | slice:0:100 }}             <!-- first 100 chars -->

<!-- Number/currency pipes -->
{{ 1234567.89 | number:'1.2-2' }}        <!-- 1,234,567.89 -->
{{ 99.99 | currency:'USD' }}             <!-- $99.99 -->
{{ 0.856 | percent:'1.1-1' }}           <!-- 85.6% -->

<!-- Date pipe -->
{{ order.createdAt | date:'dd/MM/yyyy HH:mm' }}   <!-- 15/06/2024 14:30 -->
{{ order.createdAt | date:'medium' }}              <!-- Jun 15, 2024, 2:30:00 PM -->
{{ order.createdAt | date:'relative' }}            <!-- (custom pipe) "2 hours ago" -->

<!-- Async pipe — subscribes and unsubscribes automatically -->
{{ user$ | async | json }}
@if (order$ | async; as order) {
  <p>{{ order.id }}</p>
}
```

## Custom Pipes
```typescript
@Pipe({ name: 'truncate', standalone: true, pure: true })
export class TruncatePipe implements PipeTransform {
  transform(value: string, limit = 100, ellipsis = '...'): string {
    if (!value || value.length <= limit) return value;
    return value.substring(0, limit) + ellipsis;
  }
}

// Usage: {{ description | truncate:50:'…' }}

// Impure pipe (re-runs on every CD cycle — avoid for performance)
@Pipe({ name: 'filterBy', pure: false })
export class FilterByPipe implements PipeTransform {
  transform(items: any[], term: string): any[] {
    return items.filter(i => i.name.includes(term));
  }
}
```

## Template Reference Variables
```html
<input #searchInput type="text" placeholder="Search" />
<button (click)="search(searchInput.value)">Search</button>

<!-- Access component methods -->
<app-modal #modal />
<button (click)="modal.open()">Open Modal</button>
```

## Common Mistakes
1. **Missing `track` in @for:** Angular cannot efficiently update the DOM without a track expression. Always use `track item.id` or `track $index`.
2. **Complex expressions in templates:** move logic to component methods or pipes — keep templates declarative.
3. **Impure pipes in performance-sensitive code:** impure pipes run on every change detection cycle.
4. **Using `async` pipe without null guard:** `{{ (user$ | async).name }}` throws if the Observable hasn't emitted yet. Use `@if (user$ | async; as user)`.
""",
"mcqs": [
  {"id":"d62q1","prompt":"What is the difference between `{{ value }}` interpolation and `[property]='value'` property binding?","options":["Identical","Interpolation converts to string and embeds in text content; property binding sets a DOM property directly to the TypeScript value (preserves type, works for non-string values)","Property binding only works with HTML attributes","Interpolation is reactive; property binding is not"],"correctAnswer":"Interpolation converts to string and embeds in text content; property binding sets a DOM property directly to the TypeScript value (preserves type, works for non-string values)","explanation":"{{ order.total }}: calls toString(), places text in DOM. [disabled]='form.invalid': sets the DOM disabled property to a boolean directly. Use property binding for boolean, number, object inputs to components, and DOM properties that are not string-based."},
  {"id":"d62q2","prompt":"What does `track product.id` do in Angular 17's @for block?","options":["Filters products by id","Tells Angular's diffing algorithm how to identify each item — enables efficient DOM reuse when the list changes instead of destroying and recreating all elements","Tracks user interactions with products","track is optional performance hint"],"correctAnswer":"Tells Angular's diffing algorithm how to identify each item — enables efficient DOM reuse when the list changes instead of destroying and recreating all elements","explanation":"Without track: Angular can't match old DOM nodes to new items — destroys and recreates everything. With track product.id: same id → reuse DOM node, only update changed properties. Dramatically improves performance for large lists with insertions/deletions."},
  {"id":"d62q3","prompt":"What does the `async` pipe do?","options":["Makes the template render asynchronously","Subscribes to an Observable or Promise, automatically updates the template when a value emits, and unsubscribes when the component is destroyed","async is required for all Observables","Converts a callback to an Observable"],"correctAnswer":"Subscribes to an Observable or Promise, automatically updates the template when a value emits, and unsubscribes when the component is destroyed","explanation":"async pipe handles the full lifecycle: subscribe on use, push new values to template, unsubscribe on ngOnDestroy. Eliminates manual subscribe/unsubscribe in the component. @if (orders$ | async; as orders) { } provides the value with a null guard."},
  {"id":"d62q4","prompt":"What is the difference between a pure and impure pipe?","options":["Pure pipes are faster","Pure pipes only re-execute when input reference changes (fast); impure pipes re-execute on every change detection cycle (every mouse move, keypress) — avoid impure pipes in performance-critical templates","Impure pipes can modify state","Pure pipes are for strings only"],"correctAnswer":"Pure pipes only re-execute when input reference changes (fast); impure pipes re-execute on every change detection cycle (every mouse move, keypress) — avoid impure pipes in performance-critical templates","explanation":"Pure pipe (default): cached — only runs when input changes by reference. Impure pipe (pure: false): runs every CD cycle. FilterBy pipe filtering a 1000-item list on every keypress → 1000 comparisons per keystroke. Solution: move filtering to the component and use a pure pipe."},
  {"id":"d62q5","prompt":"What does `[(ngModel)]='searchTerm'` expand to?","options":["Creates a FormControl","Is syntactic sugar for `[ngModel]='searchTerm' (ngModelChange)='searchTerm=$event'` — binds value to input and updates it on change","[()] is a new Angular 17 syntax","Two-way binding only works with inputs"],"correctAnswer":"Is syntactic sugar for `[ngModel]='searchTerm' (ngModelChange)='searchTerm=$event'` — binds value to input and updates it on change","explanation":"Banana-in-a-box syntax: [(x)] = [x]='val' (ngxChange)='val=$event'. [ngModel] sets the input value from the component; (ngModelChange) updates the component when the input changes. Requires FormsModule. For reactive forms, use FormControl."},
  {"id":"d62q6","prompt":"What does `{{ order.createdAt | date:'dd/MM/yyyy' }}` do?","options":["Converts date to milliseconds","Formats the date value using Angular's built-in DatePipe with the specified format string — 'dd/MM/yyyy' produces '15/06/2024'","date pipe requires moment.js","Formats only ISO strings"],"correctAnswer":"Formats the date value using Angular's built-in DatePipe with the specified format string — 'dd/MM/yyyy' produces '15/06/2024'","explanation":"Angular's DatePipe accepts Date objects, ISO strings, and milliseconds. 'dd' = day, 'MM' = month, 'yyyy' = full year. Predefined: 'short', 'medium', 'long'. Also accepts timezone: | date:'dd/MM/yyyy':'UTC'. Locale-aware with LOCALE_ID."},
  {"id":"d62q7","prompt":"What is a template reference variable like `#searchInput`?","options":["A TypeScript variable","A reference to the DOM element or component instance in the template — `#searchInput` on an `<input>` gives access to the HTMLInputElement; `#comp` on `<app-comp>` gives access to the component instance","Template variables are global","Only works with components"],"correctAnswer":"A reference to the DOM element or component instance in the template — `#searchInput` on an `<input>` gives access to the HTMLInputElement; `#comp` on `<app-comp>` gives access to the component instance","explanation":"#searchInput on native element → HTMLInputElement (searchInput.value). #modal on component → component instance (modal.open()). Accessible within the same template. Use @ViewChild to access from TypeScript."},
  {"id":"d62q8","prompt":"What is the `@empty` block in Angular 17's @for?","options":["Renders when the array is null","Renders when the iterable is empty — shown in place of the @for content when there are no items to display","@empty filters empty strings","Required with every @for"],"correctAnswer":"Renders when the iterable is empty — shown in place of the @for content when there are no items to display","explanation":"@for (item of items; track item.id) { ... } @empty { <p>No items found</p> }. Cleaner than *ngIf checks. Previously required: *ngIf='items.length' / show empty message. @empty makes the intent explicit."},
  {"id":"d62q9","prompt":"What happens if you write `{{ (user$ | async).name }}` before the Observable emits?","options":["Returns empty string","Throws TypeError: Cannot read property 'name' of null — async pipe returns null until the Observable emits. Fix: use @if (user$ | async; as user) { {{ user.name }} }","Returns undefined","async pipe waits before rendering"],"correctAnswer":"Throws TypeError: Cannot read property 'name' of null — async pipe returns null until the Observable emits. Fix: use @if (user$ | async; as user) { {{ user.name }} }","explanation":"async pipe initial value is null (before first emission). .name access on null → runtime error. Fix: @if (user$ | async; as user) { {{ user.name }} } — the if block only renders after the observable emits, providing the value as 'user'."},
  {"id":"d62q10","prompt":"What is the `currency` pipe and what format does `99.99 | currency:'USD'` produce?","options":["Converts currency code to symbol","Angular's built-in CurrencyPipe formats numbers as currency: '$99.99' for USD. Locale-aware: currency:'GBP':'symbol':'1.2-2' produces '£99.99'","currency requires a server call","Only works with numbers"],"correctAnswer":"Angular's built-in CurrencyPipe formats numbers as currency: '$99.99' for USD. Locale-aware: currency:'GBP':'symbol':'1.2-2' produces '£99.99'","explanation":"CurrencyPipe: | currency:'currencyCode':'display':'digitsInfo':'locale'. Display: 'symbol' ($), 'code' (USD), 'symbol-narrow' (£). DigitsInfo '1.2-2': min 1 integer digit, min 2 and max 2 fraction digits."}
],
"writtenConceptQuestions": [
  "Show Angular 17 control flow: @if/@else, @for with track, @switch for order status display. What does @empty do?",
  "Explain the difference between {{ }}, [ ], ( ), and [( )]. Show an example of each.",
  "Write a custom TruncatePipe that truncates text to N characters with an ellipsis. Mark it as pure.",
  "What is the async pipe? Show using it with @if and as keyword to safely display user data.",
  "Explain pure vs impure pipes. Show why a filter pipe as impure is a performance problem.",
  "What are template reference variables? Show #modalRef on a component and calling its open() method from a button.",
  "Show the date, currency, number, and percent pipes with format strings. What locale-related configuration is needed?"
],
"businessScenarios": [
  "A product list renders 500 items. After filtering, all 500 DOM nodes are destroyed and recreated. Add track product.id to @for to enable efficient DOM reuse.",
  "An impure FilterPipe runs on every keystroke in a 10,000 item list causing 100ms lag. Move filtering to the component property with a filter$ Observable and use a pure pipe.",
  "An order status badge needs to show different colors for PENDING/PROCESSING/SHIPPED/DELIVERED. Implement using @switch in the template."
]
},

"day-063": {
"notes": """# Angular Data Binding: Property, Event, Two-Way, and Attribute Binding

## Four Types of Data Binding
```html
<!-- 1. Interpolation (one-way: component → template) -->
<p>Hello, {{ userName }}</p>
<title>{{ pageTitle }}</title>

<!-- 2. Property Binding (one-way: component → DOM property) -->
<input [value]="searchTerm" />
<button [disabled]="isLoading">Submit</button>
<img [src]="avatarUrl" [alt]="userName" />
<app-card [data]="cardData" />   <!-- component @Input -->

<!-- 3. Event Binding (one-way: DOM → component) -->
<button (click)="save()">Save</button>
<input (input)="onInput($event)" (blur)="validate()" />
<form (ngSubmit)="onSubmit()">...</form>

<!-- 4. Two-way Binding (bidirectional) -->
<input [(ngModel)]="firstName" />
<!-- Angular 17+ model() signal for two-way: -->
<app-input [(value)]="name" />
```

## Property vs Attribute Binding
```html
<!-- DOM Property binding (recommended) — uses [property] -->
<input [value]="name" />         <!-- sets HTMLInputElement.value (live) -->
<td [colSpan]="2"></td>          <!-- sets colspan via DOM property -->

<!-- HTML Attribute binding — for attributes with no DOM property equivalent -->
<td [attr.colspan]="colSpan" />  <!-- use attr.* for HTML attributes -->
<button [attr.aria-label]="label">Icon Button</button>
<svg [attr.viewBox]="viewBox" />

<!-- Class binding -->
<div [class.active]="isActive" [class.loading]="isLoading">...</div>
<div [ngClass]="{ 'active': isActive, 'error': hasError }">...</div>

<!-- Style binding -->
<div [style.color]="textColor">...</div>
<div [style.font-size.px]="fontSize">...</div>
<div [ngStyle]="{ color: textColor, fontSize: fontSize + 'px' }">...</div>
```

## Event Binding — $event and Custom Events
```typescript
// Template
// <input (keyup)="onKey($event)" />
// <button (click)="onButtonClick($event)">Click</button>

export class SearchComponent {
  searchTerm = '';

  // $event is the native DOM event
  onKey(event: KeyboardEvent) {
    const input = event.target as HTMLInputElement;
    this.searchTerm = input.value;
    if (event.key === 'Enter') this.search();
  }

  // Shorthand: $event.target.value
  // <input (input)="searchTerm = $event.target.value" />
}
```

## Signals — Angular 16+ Reactive Primitives
```typescript
@Component({ standalone: true })
export class CounterComponent {
  // signal() creates a reactive value
  count = signal(0);
  doubleCount = computed(() => this.count() * 2);  // derived signal

  increment() { this.count.update(v => v + 1); }
  reset()     { this.count.set(0); }
}
// Template:
// <p>Count: {{ count() }}</p>   <-- signals are functions, call them
// <p>Double: {{ doubleCount() }}</p>
// <button (click)="increment()">+</button>
```

## model() — Signals for Two-Way Binding (Angular 17+)
```typescript
// Child component — replaces @Input + @Output pattern for two-way
@Component({
  template: `<input [value]="value()" (input)="value.set($event.target.value)" />`
})
export class TextInputComponent {
  value = model<string>('');  // replaces: @Input() value + @Output() valueChange
}

// Parent usage:
// <app-text-input [(value)]="name" />
// name is updated automatically (can be a signal or plain variable)
```

## ViewBinding and HostBinding
```typescript
@Directive({ selector: '[appHighlight]' })
export class HighlightDirective {
  @HostBinding('class.highlighted') isHighlighted = false;
  @HostBinding('style.backgroundColor') bgColor = '';

  @HostListener('mouseenter')
  onMouseEnter() { this.isHighlighted = true; this.bgColor = 'yellow'; }

  @HostListener('mouseleave')
  onMouseLeave() { this.isHighlighted = false; this.bgColor = ''; }
}
```

## Common Mistakes
1. **Using `[attr.href]` instead of `[href]`:** `href` has a DOM property — use `[href]`. Use `attr.*` only for attributes without DOM property equivalents.
2. **Mutating objects with two-way binding:** `[(ngModel)]` on an object field doesn't notify OnPush CD — use signals or spread to new object.
3. **Calling signals without `()`:** `{{ count }}` shows the Signal object, `{{ count() }}` shows the value.
""",
"mcqs": [
  {"id":"d63q1","prompt":"What is the difference between `[value]` property binding and `[attr.value]` attribute binding?","options":["Identical","[value] sets the DOM property (live value of the input); [attr.value] sets the HTML attribute (initial value only, not updated dynamically)","attr.value is faster","[value] only works with text inputs"],"correctAnswer":"[value] sets the DOM property (live value of the input); [attr.value] sets the HTML attribute (initial value only, not updated dynamically)","explanation":"HTML attribute: initial state in HTML markup. DOM property: live state of the element. For input.value: [value]='x' updates the visible value dynamically. [attr.value]='x' sets the initial attribute — after user types, getAttribute('value') stays at original, input.value changes."},
  {"id":"d63q2","prompt":"When should you use `[attr.colspan]` instead of `[colSpan]`?","options":["Always use attr.","Use [attr.colspan] for HTML attributes that have NO corresponding DOM property (like colspan on td, aria-* attributes, data-*, SVG attributes). Use [property] for DOM properties","attr. is deprecated","Only for SVG elements"],"correctAnswer":"Use [attr.colspan] for HTML attributes that have NO corresponding DOM property (like colspan on td, aria-* attributes, data-*, SVG attributes). Use [property] for DOM properties","explanation":"Most HTML attributes have DOM properties: [disabled], [value], [href], [src]. Some don't: aria-label, data-*, colspan, rowspan, SVG viewBox. Angular requires attr. prefix for attributes without DOM property equivalents to avoid binding errors."},
  {"id":"d63q3","prompt":"What is an Angular Signal (`signal()`) and how does it differ from a regular property?","options":["A signal is an Observable","A signal is a reactive primitive — a getter function wrapping a value. Reading it (count()) registers a dependency; writing it (count.set()) schedules updates only for dependents — more granular than zone-based CD","Signals are only for events","Signals replace NgModule"],"correctAnswer":"A signal is a reactive primitive — a getter function wrapping a value. Reading it (count()) registers a dependency; writing it (count.set()) schedules updates only for dependents — more granular than zone-based CD","explanation":"Regular property: Angular detects changes via Zone.js (monkey-patches browser APIs). Signal: Angular knows exactly which templates/computed values depend on this signal — updates only those. Enables fine-grained reactivity and makes OnPush change detection simpler."},
  {"id":"d63q4","prompt":"What does `[class.active]='isActive'` do?","options":["Sets all classes","Adds the 'active' CSS class when isActive is true, removes it when false — a conditional class binding","Creates a new CSS class","[class.active] requires SCSS"],"correctAnswer":"Adds the 'active' CSS class when isActive is true, removes it when false — a conditional class binding","explanation":"[class.active]='condition': Angular adds/removes the 'active' class based on the boolean expression. [ngClass]=\"{'active': isActive, 'error': hasError}\" handles multiple conditional classes. [class]='classString' replaces all classes with the string."},
  {"id":"d63q5","prompt":"What does `model()` in Angular 17+ replace?","options":["FormControl","The @Input() + @Output() pattern for two-way data binding — model<string>('') creates a signal that can be set externally via [(value)] binding and also set internally by the child","Services for state management","model() replaces async pipe"],"correctAnswer":"The @Input() + @Output() pattern for two-way data binding — model<string>('') creates a signal that can be set externally via [(value)] binding and also set internally by the child","explanation":"Old pattern: @Input() value: string; @Output() valueChange = new EventEmitter<string>() — must emit on every change. model(): single declaration that Angular manages both directions. Parent: <comp [(value)]='name' /> — name updated as the child changes."},
  {"id":"d63q6","prompt":"What does `$event` refer to in `(click)='handler($event)'`?","options":["The component instance","The native DOM event object (MouseEvent, InputEvent, etc.) — gives access to event.target, event.key, event.preventDefault(), etc.","$event is always a string","The Angular event wrapper"],"correctAnswer":"The native DOM event object (MouseEvent, InputEvent, etc.) — gives access to event.target, event.key, event.preventDefault(), etc.","explanation":"(click)='handler($event)': $event is MouseEvent. (input)='handler($event)': $event is InputEvent. ($event.target as HTMLInputElement).value gets the current input value. For custom @Output EventEmitters: $event is whatever the child emitted."},
  {"id":"d63q7","prompt":"What does `@HostBinding('class.active')` do in a directive?","options":["Binds to the host component's class","Adds/removes the 'active' class on the HOST element (the element the directive is applied to) based on the property value — no need to inject ElementRef","Only works with CSS modules","HostBinding requires SCSS"],"correctAnswer":"Adds/removes the 'active' CSS class on the HOST element (the element the directive is applied to) based on the property value — no need to inject ElementRef","explanation":"@HostBinding('class.active') isActive = false: sets class.active on the element hosting the directive. @HostListener('click') onClick() { this.isActive = true }: responds to click on the host. Cleaner than injecting ElementRef and manipulating classList manually."},
  {"id":"d63q8","prompt":"How do you call a signal's value in a template?","options":["{{ count }}","{{ count() }} — signals are functions; calling them reads the current value AND registers the template as a dependent","{{ signal.value }}","{{ count.get() }}"],"correctAnswer":"{{ count() }} — signals are functions; calling them reads the current value AND registers the template as a dependent","explanation":"signal() returns a SignalFunction. {{ count }} would display '[Signal: 0]'. {{ count() }} invokes the getter, returns the value. In computed(): computed(() => count() * 2) — read by calling. In effect(): effect(() => console.log(count())) — auto-tracks."},
  {"id":"d63q9","prompt":"What does `[ngClass]=\"{'error': hasError, 'loading': isLoading}\"` do?","options":["Replaces all existing classes","Conditionally adds 'error' class if hasError is true AND 'loading' class if isLoading is true — multiple classes managed independently","Only the first truthy class is applied","ngClass requires a string"],"correctAnswer":"Conditionally adds 'error' class if hasError is true AND 'loading' class if isLoading is true — multiple classes managed independently","explanation":"ngClass object syntax: keys are class names, values are boolean conditions. Multiple classes can be true simultaneously. Can also accept a string ('class1 class2'), an array (['class1', 'class2']), or an expression."},
  {"id":"d63q10","prompt":"What is `computed()` in Angular signals?","options":["A computed property for classes","A derived signal that automatically recalculates when its dependencies change — computed(() => count() * 2) updates whenever count changes, without explicit subscriptions","computed() is for DOM computation","Replaces ngOnChanges"],"correctAnswer":"A derived signal that automatically recalculates when its dependencies change — computed(() => count() * 2) updates whenever count changes, without explicit subscriptions","explanation":"computed() lazily evaluates and caches: only recalculates when a dependency signal changes. Multiple reads between changes return the cached value. Like RxJS combineLatest but synchronous. Replaces getter methods that recalculate every CD cycle."}
],
"writtenConceptQuestions": [
  "Show all four binding types (interpolation, property, event, two-way) with concrete examples for a user profile form.",
  "When do you use [attr.] vs direct property binding? Show examples with colspan, aria-label, and data-testid.",
  "Explain Angular Signals: signal(), computed(), effect(). Show a counter with a computed doubleCount.",
  "What is model() in Angular 17? Show a reusable text input component using model() for two-way binding.",
  "Show [class.active], [ngClass], and [style.color] bindings with conditional logic.",
  "Explain @HostBinding and @HostListener in a highlight directive.",
  "What is the difference between (input) and (change) event bindings on an input element?"
],
"businessScenarios": [
  "A form has 10 boolean flag properties toggling CSS classes. Replace scattered [class.x]='flag' bindings with a computed ngClass object signal.",
  "A button should be disabled while a form is submitting and re-enabled on completion. Show [disabled]='isSubmitting' binding wired to a signal.",
  "An input component needs to work with [(value)] two-way binding from its parent. Migrate from @Input/@Output pattern to Angular 17 model()."
]
},

"day-064": {
"notes": """# Angular Directives: Structural, Attribute, and Custom Directives

## Types of Directives
- **Component:** a directive with a template (most common)
- **Structural directive:** changes DOM structure (`*ngIf`, `*ngFor`, `@if`, `@for`)
- **Attribute directive:** changes appearance or behaviour of an existing element

## Built-in Attribute Directives
```html
<!-- ngClass — conditional classes -->
<div [ngClass]="{ 'btn-primary': isPrimary, 'btn-disabled': isDisabled }">Button</div>

<!-- ngStyle — inline styles -->
<p [ngStyle]="{ 'font-size': size + 'px', 'color': textColor }">Text</p>

<!-- ngModel — two-way binding (requires FormsModule) -->
<input [(ngModel)]="email" name="email" />
```

## Custom Attribute Directive
```typescript
@Directive({
  selector: '[appHighlight]',
  standalone: true
})
export class HighlightDirective implements OnInit {
  @Input() appHighlight = 'yellow';   // same name as selector = shorthand input
  @Input() defaultColor = 'transparent';

  constructor(private el: ElementRef, private renderer: Renderer2) {}

  @HostListener('mouseenter')
  onMouseEnter() {
    this.renderer.setStyle(this.el.nativeElement, 'backgroundColor', this.appHighlight);
  }

  @HostListener('mouseleave')
  onMouseLeave() {
    this.renderer.setStyle(this.el.nativeElement, 'backgroundColor', this.defaultColor);
  }
}

// Usage: <p appHighlight='lightblue' defaultColor='white'>Hover me</p>
```

## Custom Structural Directive
```typescript
// Replicates *ngIf with delay
@Directive({
  selector: '[appDelayedIf]',
  standalone: true
})
export class DelayedIfDirective implements OnInit, OnDestroy {
  @Input() set appDelayedIf(condition: boolean) {
    this.condition = condition;
    this.updateView();
  }
  @Input() appDelayedIfDelay = 300;

  private condition = false;
  private hasView = false;

  constructor(
    private templateRef: TemplateRef<any>,
    private viewContainer: ViewContainerRef
  ) {}

  private updateView() {
    setTimeout(() => {
      if (this.condition && !this.hasView) {
        this.viewContainer.createEmbeddedView(this.templateRef);
        this.hasView = true;
      } else if (!this.condition && this.hasView) {
        this.viewContainer.clear();
        this.hasView = false;
      }
    }, this.appDelayedIfDelay);
  }
}
// Usage: <div *appDelayedIf="showContent" [appDelayedIfDelay]="500">Content</div>
```

## Renderer2 — Safe DOM Manipulation
```typescript
// Direct DOM manipulation (avoid in Angular):
// this.el.nativeElement.style.color = 'red'; // breaks SSR, security risk

// Use Renderer2 (works in SSR, safe):
constructor(private renderer: Renderer2, private el: ElementRef) {}

setColor(color: string) {
  this.renderer.setStyle(this.el.nativeElement, 'color', color);
  this.renderer.addClass(this.el.nativeElement, 'highlighted');
  this.renderer.setAttribute(this.el.nativeElement, 'aria-selected', 'true');
  this.renderer.listen(this.el.nativeElement, 'click', () => this.onClick());
}
```

## Directive Composition API (Angular 15+)
```typescript
// Apply multiple directives to a component via hostDirectives
@Component({
  selector: 'app-button',
  hostDirectives: [
    HighlightDirective,
    { directive: TooltipDirective, inputs: ['tooltip: appTooltip'] }
  ],
  template: `<button><ng-content /></button>`
})
export class ButtonComponent {}
// ButtonComponent automatically gets highlight and tooltip behaviour
```

## Common Mistakes
1. **Directly manipulating `nativeElement`:** works in browser but breaks server-side rendering and web workers. Use Renderer2.
2. **Structural directive on same element as `*ngIf`:** can't have two structural directives on the same element. Use `<ng-container>` to nest them.
3. **Forgetting standalone imports:** if a directive is standalone, it must be in the `imports` array of the component using it.
""",
"mcqs": [
  {"id":"d64q1","prompt":"What is the difference between attribute and structural directives?","options":["Only naming convention differs","Attribute directives modify appearance/behaviour of existing elements; structural directives change the DOM structure by adding/removing elements (*ngIf adds/removes the element)","Structural directives are faster","Attribute directives require NgModule"],"correctAnswer":"Attribute directives modify appearance/behaviour of existing elements; structural directives change the DOM structure by adding/removing elements (*ngIf adds/removes the element)","explanation":"Attribute: [appHighlight], [ngClass], [ngStyle] — modifies the element in place. Structural: *ngIf, *ngFor, *ngSwitch — prefixed with * which is syntactic sugar for <ng-template> wrapping. @if/@for are the new template-based equivalents."},
  {"id":"d64q2","prompt":"Why should you use `Renderer2` instead of directly accessing `nativeElement`?","options":["Renderer2 is faster","nativeElement manipulation breaks Server-Side Rendering (Angular Universal) and web workers. Renderer2 abstracts DOM operations, working in all rendering environments","Renderer2 requires fewer imports","nativeElement is deprecated"],"correctAnswer":"nativeElement manipulation breaks Server-Side Rendering (Angular Universal) and web workers. Renderer2 abstracts DOM operations, working in all rendering environments","explanation":"document.body.appendChild, element.style.color — browser-only APIs. In Angular Universal (SSR), there's no browser DOM. Renderer2 provides platform-agnostic methods: setStyle, addClass, setAttribute, listen — work in browser, SSR, and web workers."},
  {"id":"d64q3","prompt":"What does `@Input() appHighlight = 'yellow'` mean when the selector is `[appHighlight]`?","options":["Conflicts with the selector","The input shares the same name as the directive selector — allows shorthand usage: `<p appHighlight='blue'>` passes 'blue' as the appHighlight input instead of needing a separate [inputName] binding","Creates a default value only","Selector and input name must differ"],"correctAnswer":"The input shares the same name as the directive selector — allows shorthand usage: `<p appHighlight='blue'>` passes 'blue' as the appHighlight input instead of needing a separate [inputName] binding","explanation":"Selector [appHighlight] + @Input() appHighlight: using appHighlight='blue' (attribute value) OR [appHighlight]='variable' both set the input. This is the standard Angular pattern for attribute directives with a primary input."},
  {"id":"d64q4","prompt":"What do `TemplateRef` and `ViewContainerRef` provide to a structural directive?","options":["Template caching and DOM container","TemplateRef: reference to the <ng-template> content (what to render). ViewContainerRef: the location in the DOM where to insert/remove the view — together they enable showing/hiding DOM sections","TemplateRef is for components only","ViewContainerRef stores component instances"],"correctAnswer":"TemplateRef: reference to the <ng-template> content (what to render). ViewContainerRef: the location in the DOM where to insert/remove the view — together they enable showing/hiding DOM sections","explanation":"vcr.createEmbeddedView(templateRef): renders the template content at this location. vcr.clear(): removes all rendered views. The * prefix in *ngIf='condition' expands to <ng-template [ngIf]='condition'> — the template is the wrapped content."},
  {"id":"d64q5","prompt":"Why can't you put two structural directives on the same element?","options":["JavaScript limitation","Angular allows only one structural directive per element — *ngIf and *ngFor on the same element cause a compile error. Use <ng-container> to layer them: <ng-container *ngIf='show'><div *ngFor='...'></ng-container>","Structural directives are singletons","Both would apply but only the last wins"],"correctAnswer":"Angular allows only one structural directive per element — *ngIf and *ngFor on the same element cause a compile error. Use <ng-container> to layer them: <ng-container *ngIf='show'><div *ngFor='...'></ng-container>","explanation":"Both *ngIf and *ngFor want to control the element's DOM creation. Angular forbids this. Solution: wrap with <ng-container *ngIf='show'> (ng-container renders no DOM element) then put *ngFor on the inner element."},
  {"id":"d64q6","prompt":"What is the Directive Composition API (`hostDirectives`)?","options":["Composing multiple templates","Applying directives to a component's host element declaratively in the @Component metadata — the component automatically has the behaviour of all listed directives without any parent template changes","hostDirectives creates child components","Only works with structural directives"],"correctAnswer":"Applying directives to a component's host element declaratively in the @Component metadata — the component automatically has the behaviour of all listed directives without any parent template changes","explanation":"hostDirectives: [HighlightDirective, TooltipDirective] on ButtonComponent — every <app-button> automatically has hover highlight and tooltip behaviour. No need to add appHighlight and appTooltip to every usage. Angular 15+."},
  {"id":"d64q7","prompt":"What does `@HostListener('mouseenter') onEnter() {}` do?","options":["Listens for child component events","Registers an event listener on the HOST element (the element the directive is applied to) — when mouseenter fires, onEnter() is called","HostListener is for services only","Requires EventEmitter"],"correctAnswer":"Registers an event listener on the HOST element (the element the directive is applied to) — when mouseenter fires, onEnter() is called","explanation":"@HostListener attaches event handlers to the host element without querying it. Clean alternative to renderer.listen(). Multiple @HostListeners can be stacked. Can also listen to window/document: @HostListener('window:resize', ['$event'])."},
  {"id":"d64q8","prompt":"What is `ng-container` used for with structural directives?","options":["Creates a visible wrapper element","An invisible grouping element that renders no DOM output — lets you apply structural directives without adding extra DOM elements like <div> or <span>","ng-container requires NgModule","Only used with *ngFor"],"correctAnswer":"An invisible grouping element that renders no DOM output — lets you apply structural directives without adding extra DOM elements like <div> or <span>","explanation":"<ng-container *ngIf='loggedIn'>: the *ngIf applies but no wrapping div appears in the DOM. Useful when adding a wrapper element would break CSS layout (flex children, table rows). Also used to apply *ngFor without a wrapper."},
  {"id":"d64q9","prompt":"When a standalone directive is created, what must the using component do?","options":["Add it to NgModule","Add it to the component's `imports: []` array in @Component decorator — standalone components import their dependencies directly","Add it to app.module.ts","Register it with a service"],"correctAnswer":"Add it to the component's `imports: []` array in @Component decorator — standalone components import their dependencies directly","explanation":"Standalone architecture: no NgModule. Each component declares its own imports. HighlightDirective standalone → add to @Component({ imports: [HighlightDirective] }). This makes dependencies explicit and enables better tree-shaking."},
  {"id":"d64q10","prompt":"What problem does a custom structural directive solve over *ngIf?","options":["More performance than *ngIf","Adds custom logic around show/hide decisions — e.g., delayed rendering, permission-based visibility, animation trigger — behaviours *ngIf doesn't support","Custom directives run faster","They replace *ngFor"],"correctAnswer":"Adds custom logic around show/hide decisions — e.g., delayed rendering, permission-based visibility, animation trigger — behaviours *ngIf doesn't support","explanation":"*ngIf: simple boolean. Custom structural: *appHasPermission='ADMIN' can check the auth service and show/hide. *appDelayedIf can animate entrance. *appLetContext can provide context variables to the template. Any show/hide logic that goes beyond a simple boolean."}
],
"writtenConceptQuestions": [
  "Write a custom `appButtonLoading` attribute directive that disables a button and shows a spinner while a loading boolean @Input is true.",
  "Show a custom `appHasRole` structural directive that shows content only if the current user has the required role. Inject AuthService.",
  "Explain TemplateRef and ViewContainerRef. Show how they enable a structural directive to create/destroy a view.",
  "When should you use Renderer2 vs direct nativeElement access? Show both approaches for setting a style.",
  "What is the Directive Composition API? Show hostDirectives applying a tooltip and ripple directive to a ButtonComponent.",
  "Show ng-container usage to nest *ngIf and @for without extra DOM elements.",
  "Explain @HostBinding and @HostListener together in a drag-and-drop directive."
],
"businessScenarios": [
  "A role-based UI needs to hide admin buttons from regular users. Implement *appHasPermission='WRITE_ORDERS' structural directive that queries AuthService and removes elements for unauthorized users.",
  "A table component renders badly because *ngIf adds wrapping divs inside table rows. Replace with ng-container to fix the HTML structure.",
  "Multiple components all add nativeElement.style manipulations for hover effects, causing SSR failures. Extract to a Renderer2-based highlight directive."
]
},

"day-065": {
"notes": """# Angular Services: Singleton Services, Dependency Injection, and HTTP

## What is a Service?
Services encapsulate shared logic, data fetching, and state that doesn't belong in a component. Components should be thin — delegate business logic to services.

```typescript
@Injectable({
  providedIn: 'root'   // singleton across the entire application
})
export class OrderService {
  private readonly apiUrl = '/api/orders';

  constructor(private http: HttpClient) {}

  findAll(params?: { page?: number; size?: number }): Observable<Page<OrderDto>> {
    return this.http.get<Page<OrderDto>>(this.apiUrl, { params: params as any });
  }

  findById(id: string): Observable<OrderDto> {
    return this.http.get<OrderDto>(`${this.apiUrl}/${id}`);
  }

  create(request: CreateOrderRequest): Observable<OrderDto> {
    return this.http.post<OrderDto>(this.apiUrl, request);
  }

  updateStatus(id: string, status: string): Observable<OrderDto> {
    return this.http.patch<OrderDto>(`${this.apiUrl}/${id}/status`, { status });
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
```

## HttpClient — Making HTTP Requests
```typescript
// HttpClient methods return cold Observables — subscribe to execute
this.http.get<User[]>('/api/users')
  .pipe(
    map(users => users.filter(u => u.active)),
    catchError(err => {
      this.errorService.handle(err);
      return EMPTY; // don't propagate error, just stop
    })
  )
  .subscribe(users => this.users = users);

// POST with headers
this.http.post<OrderDto>('/api/orders', body, {
  headers: new HttpHeaders({ 'X-Request-Id': uuid() })
})

// Response type: observe full response (headers, status)
this.http.get<OrderDto>('/api/orders/1', { observe: 'response' })
  .subscribe(response => {
    console.log(response.status);           // 200
    console.log(response.headers.get('X-Total-Count'));
    console.log(response.body);             // OrderDto
  });
```

## Service Layers — Separation of Concerns
```typescript
// API Service (HTTP only)
@Injectable({ providedIn: 'root' })
export class OrderApiService {
  constructor(private http: HttpClient) {}
  getOrders(): Observable<OrderDto[]> { return this.http.get<OrderDto[]>('/api/orders'); }
}

// State Service (manages application state)
@Injectable({ providedIn: 'root' })
export class OrderStateService {
  private orders = signal<OrderDto[]>([]);
  readonly orders$ = this.orders.asReadonly();

  constructor(private api: OrderApiService) {}

  loadOrders() {
    this.api.getOrders().subscribe(orders => this.orders.set(orders));
  }

  addOrder(order: OrderDto) {
    this.orders.update(current => [...current, order]);
  }
}

// Component uses state service
@Component({ standalone: true })
export class OrderListComponent {
  private orderState = inject(OrderStateService);
  orders = this.orderState.orders$;  // signal — use in template as orders()
}
```

## inject() Function — Modern DI
```typescript
// Traditional constructor injection
export class MyComponent {
  constructor(private service: MyService) {}
}

// Modern inject() function (Angular 14+)
export class MyComponent {
  private service = inject(MyService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  // Works in constructor, field initializers, and injection context functions
}
```

## Service Scope — providedIn Options
```typescript
// 'root' — singleton, lazy-loaded if not used (tree-shaking)
@Injectable({ providedIn: 'root' })

// Component-level scope — new instance per component instance
@Component({ providers: [OrderService] })
// Each instance of this component gets its own OrderService

// 'platform' — shared across multiple Angular apps on the same page
@Injectable({ providedIn: 'platform' })
```

## Common Mistakes
1. **Subscribing in services:** services should return Observables — let components subscribe and unsubscribe.
2. **Putting HTTP calls in components:** use services — components should not know about API URLs.
3. **Multiple instances:** using `providers: [MyService]` at component level when you need the singleton — accidentally creates a new instance.
""",
"mcqs": [
  {"id":"d65q1","prompt":"What does `providedIn: 'root'` mean for a service?","options":["Creates multiple instances","Creates a single instance (singleton) shared across the entire application — lazy-loaded (not created until first injection), and tree-shakeable if never injected","Makes the service available only in the root module","Requires AppModule to register it"],"correctAnswer":"Creates a single instance (singleton) shared across the entire application — lazy-loaded (not created until first injection), and tree-shakeable if never injected","explanation":"providedIn:'root': Angular adds the service to the root injector. One instance shared everywhere. Tree-shakeable: if nothing injects it, it's excluded from the bundle. Previously: add to NgModule.providers (not tree-shakeable)."},
  {"id":"d65q2","prompt":"What does `HttpClient.get<OrderDto[]>('/api/orders')` return?","options":["OrderDto[] directly","An Observable<OrderDto[]> — cold Observable that executes the HTTP request when subscribed. Each subscription makes a new HTTP request","A Promise<OrderDto[]>","null until the request completes"],"correctAnswer":"An Observable<OrderDto[]> — cold Observable that executes the HTTP request when subscribed. Each subscription makes a new HTTP request","explanation":"HttpClient returns cold Observables — no request is made until subscribe() is called. Multiple subscriptions = multiple HTTP requests. Use shareReplay(1) if you need to share one response across multiple subscribers."},
  {"id":"d65q3","prompt":"What is the `inject()` function in Angular 14+?","options":["Injects HTML into the DOM","A functional alternative to constructor injection — inject(MyService) can be called in field initializers, constructor, and injection context functions — enables DI outside of classes","inject() replaces @Injectable","Inject forces eager loading"],"correctAnswer":"A functional alternative to constructor injection — inject(MyService) can be called in field initializers, constructor, and injection context functions — enables DI outside of classes","explanation":"inject(Service) works anywhere in the injection context (component/directive/service class body, factory functions). Enables functional interceptors, guards, and resolvers. More composable than constructor injection."},
  {"id":"d65q4","prompt":"When should you use `providers: [MyService]` at component level instead of `providedIn: 'root'`?","options":["Always use component-level providers","When each component instance needs its own isolated service state — each component instance gets a fresh MyService. Root provides: shared singleton.","Component providers are faster","For all HTTP services"],"correctAnswer":"When each component instance needs its own isolated service state — each component instance gets a fresh MyService. Root provides: shared singleton.","explanation":"Example: a wizard with 3 steps, each step is a component. WizardStepService tracks step state. providedIn:'root' → all steps share one state (wrong). providers:[WizardStepService] on each step component → each gets its own isolated service instance."},
  {"id":"d65q5","prompt":"What does `catchError(err => EMPTY)` do in an HTTP pipe?","options":["Rethrows the error","Catches the error, handles it (e.g., logs it), and returns EMPTY which completes the Observable without emitting any value — prevents unhandled error propagation","EMPTY emits null","catchError is for synchronous errors only"],"correctAnswer":"Catches the error, handles it (e.g., logs it), and returns EMPTY which completes the Observable without emitting any value — prevents unhandled error propagation","explanation":"Without catchError: HTTP error → Observable errors → component's subscribe error handler runs (or unhandled error). With catchError → EMPTY: error is caught, observable completes normally, subscribe's next handler never called. Use of(defaultValue) to emit a fallback."},
  {"id":"d65q6","prompt":"What does `observe: 'response'` do in an HttpClient request?","options":["Observes the Observable","Returns the full HttpResponse<T> object instead of just the body — allows access to status code, headers, and body","Enables streaming responses","observe: 'response' is the default"],"correctAnswer":"Returns the full HttpResponse<T> object instead of just the body — allows access to status code, headers, and body","explanation":"Default: get<T>() returns T (just the body). observe:'response': returns HttpResponse<T> with .status (200), .headers (HttpHeaders), .body (T). Needed when you must read response headers (pagination total, correlation ID, etc.)."},
  {"id":"d65q7","prompt":"Why should services return Observables rather than subscribing internally?","options":["Services can't subscribe","Returning Observables lets the consumer (component) control the subscription lifecycle — unsubscribe when the component is destroyed. Services subscribing internally cause memory leaks and prevent callers from composing operators","Observables are required by HttpClient","Internal subscription is faster"],"correctAnswer":"Returning Observables lets the consumer (component) control the subscription lifecycle — unsubscribe when the component is destroyed. Services subscribing internally cause memory leaks and prevent callers from composing operators","explanation":"Service.getOrders() subscribing internally: subscription lives forever (no ngOnDestroy in service with providedIn:'root'). Service returning Observable: component subscribes, uses takeUntil(destroy$), subscription ends with component. Caller can also pipe additional operators."},
  {"id":"d65q8","prompt":"What is the difference between an API service and a state service?","options":["They are identical","API service: handles HTTP transport (urls, request/response mapping). State service: manages application state (signals/BehaviorSubject, caches data, exposes to components). Separation enables testing each independently","State services don't use HTTP","API services are only for GET requests"],"correctAnswer":"API service: handles HTTP transport (urls, request/response mapping). State service: manages application state (signals/BehaviorSubject, caches data, exposes to components). Separation enables testing each independently","explanation":"OrderApiService: knows about '/api/orders' URL. OrderStateService: holds orders Signal, calls API, exposes to components. Components inject StateService, not ApiService. Testing: mock ApiService for state service tests; mock state service for component tests."},
  {"id":"d65q9","prompt":"What does `new HttpHeaders({ 'Authorization': 'Bearer ' + token })` do?","options":["Creates a header for security","Creates an immutable HttpHeaders object with the Authorization header — passed to HttpClient request options. Interceptors are a better pattern for adding auth headers to every request","HttpHeaders is mutable","Authorization header is added automatically"],"correctAnswer":"Creates an immutable HttpHeaders object with the Authorization header — passed to HttpClient request options. Interceptors are a better pattern for adding auth headers to every request","explanation":"HttpHeaders is immutable: every modification returns a new object. Manual headers per request is error-prone. Use HTTP interceptors to add authorization headers globally: intercept(req) { return next(req.clone({ setHeaders: { Authorization: 'Bearer ' + token } })) }"},
  {"id":"d65q10","prompt":"What Angular module must be imported/provided to use HttpClient?","options":["HttpModule","HttpClientModule (older) or provideHttpClient() in app.config.ts (Angular 15+) — without it, HttpClient injection fails with NullInjectorError","HttpService","CommonModule"],"correctAnswer":"HttpClientModule (older) or provideHttpClient() in app.config.ts (Angular 15+) — without it, HttpClient injection fails with NullInjectorError","explanation":"Standalone apps (Angular 17): app.config.ts: providers: [provideHttpClient()]. NgModule apps: imports: [HttpClientModule] in AppModule. Without this, HttpClient is not in the injector and injection throws."}
],
"writtenConceptQuestions": [
  "Write a ProductService with CRUD operations using HttpClient: findAll with pagination params, findById, create, update, delete.",
  "Explain service scope: providedIn:'root', component-level providers, and when to use each. Show an example where component-level scope is necessary.",
  "Show the inject() function vs constructor injection. When is inject() required (field initializers)?",
  "Design a two-layer service pattern: ProductApiService (HTTP) and ProductStateService (signals). Show how the state service caches data.",
  "Show catchError with EMPTY and of(defaultValue). When should you use each?",
  "What is observe:'response'? Show reading the X-Total-Count header for pagination.",
  "Why should services return Observables rather than subscribing internally? Show the memory leak scenario."
],
"businessScenarios": [
  "A component makes HTTP calls directly in ngOnInit. Move the HTTP logic to an OrderService, add error handling with catchError, and add pagination support.",
  "Multiple components independently fetch the same product list, causing redundant HTTP requests. Centralise in ProductStateService with a signal — components read from the signal, state service fetches once.",
  "Every HTTP request needs an Authorization header. Currently each service manually adds the header. Replace with an HTTP interceptor in the service layer."
]
},

"day-066": {
"notes": """# Angular Dependency Injection: Injectors, Tokens, and Hierarchical DI

## The Injector Hierarchy
Angular has a tree of injectors matching the component tree:
```
Root Injector (application-wide singletons)
  └── Platform Injector (shared between apps)
  └── Environment Injector (route-level providers)
       └── Element Injector (component/directive-level)
```
When a component needs a dependency, Angular walks up the injector tree until it finds a provider.

## Injection Tokens — Non-Class Dependencies
```typescript
// InjectionToken for non-class values (strings, objects, functions)
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL');
export const APP_CONFIG = new InjectionToken<AppConfig>('APP_CONFIG');

// Provide in app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: API_BASE_URL, useValue: environment.apiUrl },
    { provide: APP_CONFIG, useValue: { maxRetries: 3, timeout: 5000 } },
  ]
};

// Inject the token
@Injectable({ providedIn: 'root' })
export class OrderService {
  private baseUrl = inject(API_BASE_URL);
  // or constructor(@Inject(API_BASE_URL) private baseUrl: string) {}
}
```

## Provider Types
```typescript
// useValue — static value
{ provide: API_BASE_URL, useValue: 'https://api.example.com' }

// useClass — substitute a different class
{ provide: EmailService, useClass: MockEmailService }  // in tests

// useFactory — computed value / factory function
{
  provide: Logger,
  useFactory: (config: AppConfig) => new Logger(config.logLevel),
  deps: [APP_CONFIG]
}

// useExisting — alias (both resolve to same instance)
{ provide: OldService, useExisting: NewService }
```

## Optional and Self Decorators
```typescript
// @Optional — inject null if provider not found (instead of error)
constructor(@Optional() private logger: LoggerService) {
  this.logger?.log('Service initialized');
}

// @Self — only look in THIS component's injector, not parents
constructor(@Self() private service: MyService) {}

// @SkipSelf — skip THIS component's injector, look in parents only
constructor(@SkipSelf() private parentService: ParentService) {}

// @Host — look up to the host component's injector
constructor(@Host() private hostService: HostService) {}
```

## Environment Injectors for Route-Level Providers
```typescript
// Route-level providers — new instances per route activation
const routes: Routes = [
  {
    path: 'orders',
    component: OrdersComponent,
    providers: [OrderStateService]  // fresh instance per route
  }
];
```

## Forward Reference
```typescript
// forwardRef solves circular reference issues at class declaration time
@Component({
  providers: [{ provide: BASE, useExisting: forwardRef(() => DerivedComponent) }]
})
export class DerivedComponent {}
```

## Testing with DI — Overriding Providers
```typescript
TestBed.configureTestingModule({
  providers: [
    OrderService,
    { provide: HttpClient, useClass: MockHttpClient },
    { provide: API_BASE_URL, useValue: 'http://localhost:3000' },
  ]
});
```

## Common Mistakes
1. **Providing a service in both `providedIn:'root'` and `NgModule.providers`:** creates two instances.
2. **Injecting at wrong scope:** service with component state in providedIn:'root' → shared across all components.
3. **Circular DI:** A depends on B, B depends on A → use forwardRef or restructure.
""",
"mcqs": [
  {"id":"d66q1","prompt":"What is an InjectionToken and when is it needed?","options":["A token for HTTP authentication","A typed key for injecting non-class values (strings, numbers, configuration objects) — used when the dependency doesn't have a unique class type to use as the injection key","InjectionToken is for services only","Required for all DI registrations"],"correctAnswer":"A typed key for injecting non-class values (strings, numbers, configuration objects) — used when the dependency doesn't have a unique class type to use as the injection key","explanation":"Class-based services: class type IS the token. For string/number/object dependencies: new InjectionToken<string>('API_URL'). Without it, multiple string providers would conflict. TypeScript type parameter provides compile-time type safety."},
  {"id":"d66q2","prompt":"What does `{ provide: EmailService, useClass: MockEmailService }` do?","options":["Extends EmailService with MockEmailService","Substitutes MockEmailService wherever EmailService is injected — the injector returns a MockEmailService instance when EmailService is requested","Creates two services","useClass must extend the provided class"],"correctAnswer":"Substitutes MockEmailService wherever EmailService is injected — the injector returns a MockEmailService instance when EmailService is requested","explanation":"useClass substitution: common in tests (use MockEmailService instead of real EmailService) and feature flags (use PremiumService in place of BasicService). MockEmailService doesn't need to extend EmailService — it just needs the same interface."},
  {"id":"d66q3","prompt":"What does `@Optional()` do in a constructor parameter?","options":["Makes the parameter optional in TypeScript","Tells Angular to inject null if no provider is found (instead of throwing NullInjectorError) — useful for optional integrations","@Optional is only for constructor injection","Makes the service lazy-loaded"],"correctAnswer":"Tells Angular to inject null if no provider is found (instead of throwing NullInjectorError) — useful for optional integrations","explanation":"@Optional() private logger: LoggerService: if no provider for LoggerService, inject null instead of throwing. Always null-check: this.logger?.log(). Use for optional features (analytics, logging) that may not be configured in all environments."},
  {"id":"d66q4","prompt":"What is the Angular injector hierarchy?","options":["A flat list of all providers","A tree of injectors: Root (app-wide) → Environment (route) → Element (component/directive). Angular walks UP the tree when resolving dependencies — finds the nearest provider","All components share one injector","Hierarchy is only for modules"],"correctAnswer":"A tree of injectors: Root (app-wide) → Environment (route) → Element (component/directive). Angular walks UP the tree when resolving dependencies — finds the nearest provider","explanation":"Component needs ServiceA: look in component's element injector → not found → parent component → not found → root injector → found → inject root instance. If component has providers:[ServiceA], its own instance is used. This enables both singleton and per-component instances."},
  {"id":"d66q5","prompt":"What does `useFactory` allow in DI?","options":["Only synchronous factory functions","Creating a provider with a factory function that receives injected dependencies via `deps` array — enables computed configuration, conditional providers, or complex initialization","useFactory replaces useValue","Factories only work with InjectionToken"],"correctAnswer":"Creating a provider with a factory function that receives injected dependencies via `deps` array — enables computed configuration, conditional providers, or complex initialization","explanation":"{ provide: Logger, useFactory: (config) => new Logger(config.logLevel), deps: [APP_CONFIG] }: the factory receives APP_CONFIG from the injector, creates a configured Logger. deps array specifies what to inject into the factory function parameters."},
  {"id":"d66q6","prompt":"What does `@Self()` mean when applied to a constructor parameter?","options":["Inject the component itself","Only look in THIS injector (the current component/directive) — don't walk up to parent injectors. Throws if not provided locally","@Self is the default behaviour","Self injects the parent"],"correctAnswer":"Only look in THIS injector (the current component/directive) — don't walk up to parent injectors. Throws if not provided locally","explanation":"Default DI: walks up injector tree. @Self: only checks the current element injector. Combined with @Optional: @Optional() @Self() — inject null if not provided locally. Useful for directives that want a service specifically from their host component, not a global singleton."},
  {"id":"d66q7","prompt":"Why should you NOT provide a service in both `providedIn:'root'` AND in a module's `providers`?","options":["Compile error","Creates TWO instances — the root injector has one, the module's injector has another. Components in the module get the module's instance; others get the root's instance — state is not shared as expected","Both providers merge into one","The module provider takes priority always"],"correctAnswer":"Creates TWO instances — the root injector has one, the module's injector has another. Components in the module get the module's instance; others get the root's instance — state is not shared as expected","explanation":"Double provisioning is a common bug. Order placed via module component → state service instance A updated. Dashboard component → reads state service instance B (empty). Same service, different instances, no shared state. Rule: pick one provider location."},
  {"id":"d66q8","prompt":"How do you provide a route-specific service that resets on navigation?","options":["Use providedIn: 'route'","Add the service to the route's `providers` array in the route configuration — a fresh service instance is created when the route activates and destroyed when it deactivates","Set service scope to 'transient'","Route services are always singletons"],"correctAnswer":"Add the service to the route's `providers` array in the route configuration — a fresh service instance is created when the route activates and destroyed when it deactivates","explanation":"{ path: 'checkout', component: CheckoutComponent, providers: [CheckoutStateService] }: each navigation to /checkout creates a fresh CheckoutStateService. Navigating away destroys it. Perfect for wizard/multi-step flows that shouldn't retain state between visits."},
  {"id":"d66q9","prompt":"What is `useExisting` and when would you use it?","options":["Creates a new instance from existing class","An alias — { provide: OldService, useExisting: NewService } means: when OldService is requested, return the SAME instance as NewService. No new instance created","useExisting duplicates the provider","useExisting is for lazy-loaded modules"],"correctAnswer":"An alias — { provide: OldService, useExisting: NewService } means: when OldService is requested, return the SAME instance as NewService. No new instance created","explanation":"Use case: API deprecation. OldService was renamed to NewService. { provide: OldService, useExisting: NewService }: old code still works, both resolve to the same instance. Unlike useClass which creates a new instance, useExisting reuses."},
  {"id":"d66q10","prompt":"What is `forwardRef()` in Angular DI?","options":["References a future version","Wraps a class reference in a function to defer evaluation — needed when you reference a class before it's declared in JavaScript (circular reference or definition order issues)","Provides a service lazily","Required for all self-references"],"correctAnswer":"Wraps a class reference in a function to defer evaluation — needed when you reference a class before it's declared in JavaScript (circular reference or definition order issues)","explanation":"JavaScript hoists only function declarations, not class declarations. forwardRef(() => MyClass) wraps the reference in a lambda — evaluated later when the class is defined. Required in providers and decorators where the class being referenced is defined after the decorator."}
],
"writtenConceptQuestions": [
  "Show InjectionToken for API_BASE_URL and APP_CONFIG. Provide them in app.config.ts and inject in a service.",
  "Explain all four provider types: useValue, useClass, useFactory, useExisting. Show a concrete example of each.",
  "What is the injector hierarchy? Show a component with its own providers getting a different instance than the root.",
  "When do you use @Optional, @Self, @SkipSelf, @Host? Show a directive that uses @Optional @Self.",
  "Show route-level providers for a checkout wizard where state resets on every navigation.",
  "How do you override providers in tests? Show TestBed configuration with useClass and useValue substitutions.",
  "What causes 'double provisioning'? Show the bug and the fix."
],
"businessScenarios": [
  "A CheckoutService holds cart state. After checkout, navigating back shows the previous cart. Fix using route-level providers so state resets on each /checkout navigation.",
  "Integration tests need to run without real HTTP calls. Configure TestBed to substitute HttpClient with a MockHttpClient using useClass.",
  "A legacy application uses OldPaymentService everywhere. New code uses NewPaymentService. Use useExisting to make both point to the same NewPaymentService instance during the migration."
]
},

"day-067": {
"notes": """# Angular Routing: Configuration, Guards, Lazy Loading, and Router Events

## Basic Router Configuration
```typescript
// app.routes.ts
export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  {
    path: 'orders',
    component: OrdersComponent,
    children: [
      { path: '', component: OrderListComponent },
      { path: ':id', component: OrderDetailComponent },
      { path: ':id/edit', component: OrderEditComponent }
    ]
  },
  { path: '**', component: NotFoundComponent }  // wildcard — must be last
];

// app.config.ts — standalone app routing
export const appConfig: ApplicationConfig = {
  providers: [provideRouter(routes)]
};
```

## Router Navigation — Template and TypeScript
```html
<!-- Template navigation -->
<a routerLink="/orders">All Orders</a>
<a [routerLink]="['/orders', order.id]">Order Detail</a>
<a [routerLink]="['/orders', order.id, 'edit']" [queryParams]="{ tab: 'details' }">Edit</a>
<a routerLink="/orders" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">Orders</a>
```
```typescript
// TypeScript navigation
export class OrderComponent {
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  navigateToOrder(id: string) {
    this.router.navigate(['/orders', id]);
    // or relative: this.router.navigate(['..', id], { relativeTo: this.route })
  }

  navigateWithQuery() {
    this.router.navigate(['/orders'], { queryParams: { status: 'PENDING', page: 0 } });
  }
}
```

## Route Parameters and Query Params
```typescript
@Component({ standalone: true })
export class OrderDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);

  orderId = '';
  tab = '';

  ngOnInit() {
    // Snapshot — use for data that doesn't change while on this route
    this.orderId = this.route.snapshot.paramMap.get('id')!;
    this.tab = this.route.snapshot.queryParamMap.get('tab') ?? 'details';

    // Observable — use when params can change without navigation (e.g., tabs)
    this.route.paramMap.subscribe(params => {
      this.orderId = params.get('id')!;
    });

    // Signals (Angular 17+)
    const routeParams = toSignal(this.route.paramMap);
  }
}
```

## Lazy Loading — Route-Based Code Splitting
```typescript
// Lazy load a feature route — only downloaded when navigated to
export const routes: Routes = [
  {
    path: 'admin',
    loadComponent: () =>
      import('./admin/admin.component').then(m => m.AdminComponent),  // standalone
    canActivate: [authGuard]
  },
  {
    path: 'reports',
    loadChildren: () =>
      import('./reports/reports.routes').then(r => r.reportsRoutes),  // route config
    canActivate: [authGuard]
  }
];

// reports.routes.ts — child route config
export const reportsRoutes: Routes = [
  { path: '', component: ReportListComponent },
  { path: ':id', component: ReportDetailComponent }
];
```

## Route Guards
```typescript
// Functional guard (Angular 14+)
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn()) return true;

  return router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
};

// Guard with role check
export const adminGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.hasRole('ADMIN') || inject(Router).createUrlTree(['/forbidden']);
};

// CanDeactivate — confirm navigation away
export const unsavedChangesGuard: CanDeactivateFn<OrderEditComponent> =
  (component) => {
    if (!component.hasUnsavedChanges()) return true;
    return confirm('You have unsaved changes. Leave?');
  };

// Apply guards to routes
{ path: 'admin', component: AdminComponent, canActivate: [authGuard, adminGuard] }
{ path: 'orders/:id/edit', component: EditComponent, canDeactivate: [unsavedChangesGuard] }
```

## Router Events
```typescript
// Listen to router events for loading indicators
@Injectable({ providedIn: 'root' })
export class LoadingService {
  private router = inject(Router);
  loading = signal(false);

  constructor() {
    this.router.events
      .pipe(filter(e => e instanceof NavigationStart || e instanceof NavigationEnd))
      .subscribe(event => {
        this.loading.set(event instanceof NavigationStart);
      });
  }
}
```

## Common Mistakes
1. **Wildcard route `**` not last:** put it last or it matches all routes.
2. **`pathMatch: 'full'` missing on empty path redirect:** without it, `''` matches all paths (prefix match).
3. **Subscribing to `route.params` instead of `route.paramMap`:** paramMap gives `get()`, `has()`, `getAll()` methods; params is a plain object.
""",
"mcqs": [
  {"id":"d67q1","prompt":"What does `pathMatch: 'full'` do on the empty path redirect?","options":["Matches only full URL strings","Requires the ENTIRE URL to match the path (not just the start). Without it, `path: ''` matches ALL routes as a prefix — every URL starts with an empty string","pathMatch: 'full' is the default","Only affects child routes"],"correctAnswer":"Requires the ENTIRE URL to match the path (not just the start). Without it, `path: ''` matches ALL routes as a prefix — every URL starts with an empty string","explanation":"path: '' with prefix matching: every URL matches (empty string is prefix of everything). pathMatch: 'full': only URL exactly equal to '' (root) matches. Required for empty-path redirects."},
  {"id":"d67q2","prompt":"What is the difference between `loadComponent` and `loadChildren` in lazy loading?","options":["loadComponent is faster","loadComponent: lazy-loads a single standalone component. loadChildren: lazy-loads a routes configuration file (multiple components) — creates a separate chunk for the entire feature","loadChildren is deprecated","Both produce identical bundles"],"correctAnswer":"loadComponent: lazy-loads a single standalone component. loadChildren: lazy-loads a routes configuration file (multiple components) — creates a separate chunk for the entire feature","explanation":"loadComponent: for one lazy component. loadChildren: for a feature module or routes config with multiple routes. Both use dynamic import() for code splitting — the chunk is only downloaded when the user navigates to that path."},
  {"id":"d67q3","prompt":"What does a route guard returning `router.createUrlTree(['/login'])` do?","options":["Creates a login page","Redirects the user to /login instead of granting access — the navigation to the protected route is cancelled and replaced with a navigation to /login","createUrlTree is only for logging","Returns a boolean"],"correctAnswer":"Redirects the user to /login instead of granting access — the navigation to the protected route is cancelled and replaced with a navigation to /login","explanation":"Guards return: true (allow), false (block with no navigation), UrlTree (redirect to that URL). Return createUrlTree(['/login']) to redirect unauthenticated users to login. Pass the original URL as a query param: createUrlTree(['/login'], { queryParams: { returnUrl: state.url } })."},
  {"id":"d67q4","prompt":"What is `CanDeactivateFn` used for?","options":["Deactivating an admin account","Guarding navigation AWAY from a component — e.g., warning users about unsaved changes before they navigate to another route","Disabling lazy-loaded routes","It removes components from the DOM"],"correctAnswer":"Guarding navigation AWAY from a component — e.g., warning users about unsaved changes before they navigate to another route","explanation":"CanDeactivate: called when user tries to leave the current route. Component.hasUnsavedChanges() → if true, confirm dialog → user cancels → stays on page. Prevents accidental data loss on form pages."},
  {"id":"d67q5","prompt":"What is the difference between `route.snapshot.paramMap.get('id')` and subscribing to `route.paramMap`?","options":["Snapshot is deprecated","Snapshot: reads current values once (no updates if params change without navigation). Observable: live stream — updates if the same component receives new params (e.g., navigating from /orders/1 to /orders/2 on the same component)","Observable paramMap doesn't work","Snapshot is for query params only"],"correctAnswer":"Snapshot: reads current values once (no updates if params change without navigation). Observable: live stream — updates if the same component receives new params (e.g., navigating from /orders/1 to /orders/2 on the same component)","explanation":"If Angular reuses the component (same route, different params), ngOnInit doesn't run again. snapshot.paramMap.get('id') stays at the original value. route.paramMap.subscribe() receives new params on every change. Use observable when the component can receive param updates."},
  {"id":"d67q6","prompt":"What does `routerLinkActive='active'` do?","options":["Activates the route","Adds the CSS class 'active' to the element when the current URL matches the routerLink — enables active link styling in navigation menus","routerLinkActive requires CSS","active class is built-in to Angular"],"correctAnswer":"Adds the CSS class 'active' to the element when the current URL matches the routerLink — enables active link styling in navigation menus","explanation":"routerLinkActive='active': Angular adds 'active' class when the linked route is active. [routerLinkActiveOptions]=\"{ exact: true }\": only match exact URL, not prefix (otherwise '/orders' is active for '/orders/1'). Multiple classes: routerLinkActive=\"active selected\"."},
  {"id":"d67q7","prompt":"Why must the wildcard route `{ path: '**', component: NotFoundComponent }` be the LAST route?","options":["JavaScript requires it","Angular matches routes top-to-bottom and stops at the first match — placing ** first means every URL matches it, preventing all other routes from ever matching","** auto-sorts to last","Wildcard routes don't have this constraint"],"correctAnswer":"Angular matches routes top-to-bottom and stops at the first match — placing ** first means every URL matches it, preventing all other routes from ever matching","explanation":"Route matching is sequential. ** matches everything. If first, every navigation shows NotFoundComponent. If last, it's the fallback for unmatched URLs. Same applies to redirects and broad path patterns."},
  {"id":"d67q8","prompt":"What does `relativeTo: this.route` do in `router.navigate(['..', id])`?","options":["Navigates to the parent page","Makes the navigation relative to the current activated route — '../' goes to the parent segment. Without relativeTo, navigation is from the root","relativeTo is required","Only works with child routes"],"correctAnswer":"Makes the navigation relative to the current activated route — '../' goes to the root segment. Without relativeTo, navigation is from the root","explanation":"navigate(['/orders/1']): absolute. navigate(['..', '2'], { relativeTo: this.route }): relative to current route. From /orders/1: '../2' → /orders/2. Useful in reusable child components that don't know their parent path."},
  {"id":"d67q9","prompt":"What is a functional guard (Angular 14+) vs a class-based guard?","options":["Functional guards are faster","Functional guards are plain functions using inject() — no class boilerplate, composable. Class guards implement CanActivate interface with full DI via constructor. Angular recommends functional guards for new code","Functional guards don't support redirect","Class guards are required for CanDeactivate"],"correctAnswer":"Functional guards are plain functions using inject() — no class boilerplate, composable. Class guards implement CanActivate interface with full DI via constructor. Angular recommends functional guards for new code","explanation":"Class guard: implements CanActivate { constructor(private auth: AuthService) {} canActivate() { ... } }. Functional: export const authGuard: CanActivateFn = () => { const auth = inject(AuthService); ... }. Same capability, less boilerplate. inject() works in functional context."},
  {"id":"d67q10","prompt":"What does `{ provide: LocationStrategy, useClass: HashLocationStrategy }` change in routing?","options":["Enables history API","Changes URL strategy to use hash (#) — URLs become /#/orders instead of /orders. No server configuration needed since the path before # is always '/'","HashLocationStrategy is deprecated","This changes the router outlet"],"correctAnswer":"Changes URL strategy to use hash (#) — URLs become /#/orders instead of /orders. No server configuration needed since the path before # is always '/'","explanation":"Default PathLocationStrategy: uses HTML5 History API (/orders). Server must return index.html for all paths (otherwise direct URL access → 404). HashLocationStrategy: hash portion ignored by server — always serves index.html. Used for static hosting without server config."}
],
"writtenConceptQuestions": [
  "Show a route configuration with nested routes, lazy-loaded feature, wildcard, and redirect. Explain the order.",
  "Write an authGuard functional guard that redirects to /login with returnUrl if not authenticated.",
  "Explain loadComponent vs loadChildren lazy loading. Show both with dynamic import().",
  "What is CanDeactivate? Show an unsaved changes guard for an order edit form.",
  "Show reading route params both ways: snapshot (simple) and observable (reusable component).",
  "Explain routerLinkActive and routerLinkActiveOptions. Show a navigation menu with exact matching.",
  "Show router.navigate with absolute path, relative path, and query parameters."
],
"businessScenarios": [
  "An admin dashboard loads its full JavaScript bundle on page load even for non-admin users. Add lazy loading so the admin module only downloads when an admin navigates to /admin.",
  "Users accidentally navigate away from the order edit form, losing unsaved data. Add a CanDeactivate guard with confirm dialog.",
  "After login, users should be redirected back to the page they tried to access. Implement returnUrl query param in authGuard and post-login redirect."
]
},

}

def update_file(day_key, content):
    path = os.path.join(DATA_DIR, f"{day_key}.json")
    if not os.path.exists(path):
        print(f"  SKIP: {day_key}")
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["notes"] = content["notes"]
    data["conceptualQuestions"] = content["mcqs"]
    data["writtenConceptQuestions"] = content["writtenConceptQuestions"]
    data["businessScenarios"] = content["businessScenarios"]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Updated: {day_key}")

def main():
    for day_key, content in CURRICULUM.items():
        update_file(day_key, content)
    print("Done.")

if __name__ == "__main__":
    main()
