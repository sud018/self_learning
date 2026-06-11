"""Rewrite days 68-74: Reactive Forms, Template Forms, HTTP Client, RxJS, Observables, Subjects, Guards."""
import json, os
DATA_DIR = "backend/data/curriculum"

CURRICULUM = {

"day-068": {
"notes": """# Angular Reactive Forms: FormBuilder, Validation, and Dynamic Forms

## What are Reactive Forms?
Reactive forms are model-driven: the form model lives in TypeScript (not HTML). They are explicit, immutable, and testable. Unlike template-driven forms, form state is always in sync with the TypeScript model.

```typescript
@Component({
  standalone: true,
  imports: [ReactiveFormsModule],
})
export class OrderFormComponent {
  private fb = inject(FormBuilder);

  // FormGroup with FormControls and validators
  orderForm = this.fb.group({
    customerId:  ['', [Validators.required, Validators.minLength(3)]],
    productId:   ['', Validators.required],
    quantity:    [1, [Validators.required, Validators.min(1), Validators.max(1000)]],
    note:        ['', Validators.maxLength(500)],
    address: this.fb.group({
      street: ['', Validators.required],
      city:   ['', Validators.required],
      zip:    ['', [Validators.required, Validators.pattern(/^\d{5}$/)]]
    })
  });

  onSubmit() {
    if (this.orderForm.invalid) return;
    const payload = this.orderForm.value; // typed FormValue
  }
}
```

## Typed Reactive Forms (Angular 14+)
```typescript
// FormGroup is now strongly typed
interface OrderForm {
  customerId: FormControl<string>;
  quantity:   FormControl<number>;
}

const form = new FormGroup<OrderForm>({
  customerId: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  quantity:   new FormControl(1,  { nonNullable: true, validators: [Validators.min(1)] }),
});

// form.value is now typed: { customerId: string; quantity: number }
// nonNullable: true — form.reset() resets to initial value, not null
```

## Accessing Controls and Validation
```html
<form [formGroup]="orderForm" (ngSubmit)="onSubmit()">

  <input formControlName="customerId" placeholder="Customer ID" />
  <div *ngIf="orderForm.get('customerId')?.invalid && orderForm.get('customerId')?.touched">
    <span *ngIf="orderForm.get('customerId')?.errors?.['required']">Required</span>
    <span *ngIf="orderForm.get('customerId')?.errors?.['minlength']">Min 3 characters</span>
  </div>

  <!-- Shorthand with getter -->
  <div *ngIf="quantity.invalid && quantity.dirty">
    <span *ngIf="quantity.errors?.['min']">Minimum quantity is 1</span>
  </div>

  <button type="submit" [disabled]="orderForm.invalid">Place Order</button>
</form>
```
```typescript
// Getter for cleaner template access
get quantity() { return this.orderForm.get('quantity')!; }
```

## FormArray — Dynamic List of Controls
```typescript
orderForm = this.fb.group({
  items: this.fb.array([this.createItem()])  // starts with one item
});

get items(): FormArray { return this.orderForm.get('items') as FormArray; }

createItem(): FormGroup {
  return this.fb.group({
    productId: ['', Validators.required],
    quantity:  [1, [Validators.min(1)]]
  });
}

addItem() { this.items.push(this.createItem()); }
removeItem(index: number) { this.items.removeAt(index); }
```
```html
<div formArrayName="items">
  @for (item of items.controls; track $index; let i = $index) {
    <div [formGroupName]="i">
      <input formControlName="productId" placeholder="Product ID" />
      <input formControlName="quantity" type="number" />
      <button (click)="removeItem(i)">Remove</button>
    </div>
  }
  <button type="button" (click)="addItem()">Add Item</button>
</div>
```

## Custom Validators
```typescript
// Synchronous validator
export function positiveEvenNumber(control: AbstractControl): ValidationErrors | null {
  const v = control.value;
  if (!v || v <= 0 || v % 2 !== 0) {
    return { positiveEven: { value: v } };
  }
  return null;
}

// Cross-field validator (on FormGroup)
export function passwordMatch(group: AbstractControl): ValidationErrors | null {
  const pass = group.get('password')?.value;
  const confirm = group.get('confirmPassword')?.value;
  return pass === confirm ? null : { mismatch: true };
}

// Async validator (e.g., check username availability)
export function usernameAvailable(userService: UserService): AsyncValidatorFn {
  return (control: AbstractControl): Observable<ValidationErrors | null> =>
    control.valueChanges.pipe(
      debounceTime(300),
      switchMap(v => userService.checkAvailability(v)),
      map(available => available ? null : { usernameTaken: true }),
      first()  // complete the observable after first emission
    );
}
```

## valueChanges and statusChanges
```typescript
ngOnInit() {
  // React to form value changes
  this.orderForm.get('productId')!.valueChanges
    .pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(id => this.productService.getProduct(id))
    )
    .subscribe(product => this.selectedProduct = product);

  // Disable submit button for invalid or pending forms
  this.orderForm.statusChanges.subscribe(status => {
    console.log(status); // 'VALID' | 'INVALID' | 'PENDING' | 'DISABLED'
  });
}
```

## Common Mistakes
1. **Using `form.value` when controls are disabled:** disabled controls are excluded from `form.value`. Use `form.getRawValue()` to include them.
2. **Forgetting `first()` in async validators:** an async validator Observable that never completes leaves the form in PENDING forever.
3. **Deep-nesting FormGroups without matching HTML structure:** `formGroupName` must match the TypeScript nesting.
""",
"mcqs": [
  {"id":"d68q1","prompt":"What is the difference between Reactive Forms and Template-Driven Forms?","options":["Only syntax differs","Reactive: form model defined in TypeScript (explicit, immutable, testable). Template-driven: model inferred from template directives (ngModel). Reactive is recommended for complex forms","Template forms are deprecated","Reactive forms require NgModule"],"correctAnswer":"Reactive: form model defined in TypeScript (explicit, immutable, testable). Template-driven: model inferred from template directives (ngModel). Reactive is recommended for complex forms","explanation":"Reactive: explicit FormGroup/FormControl in component class. Synchronous access to form state. Easier unit testing (no TestBed needed). Template-driven: model in HTML with ngModel. Asynchronous access to form state. Simpler for basic forms."},
  {"id":"d68q2","prompt":"What does `nonNullable: true` do on a FormControl in Angular 14+?","options":["Makes the field required","When the form is reset with form.reset(), the control returns to its initial value instead of null. Removes null from the control's type — FormControl<string> instead of FormControl<string|null>","nonNullable forces a value","Sets a minimum validator"],"correctAnswer":"When the form is reset with form.reset(), the control returns to its initial value instead of null. Removes null from the control's type — FormControl<string> instead of FormControl<string|null>","explanation":"Default: new FormControl('hello').reset() → value becomes null (type: string|null). nonNullable: true: reset() → value returns to 'hello'. Cleaner types and prevents null-check boilerplate throughout the component."},
  {"id":"d68q3","prompt":"What does `FormArray` provide that a regular FormGroup doesn't?","options":["Multiple form groups","A dynamically-sized array of form controls or groups — controls can be added/removed at runtime with push(), removeAt(), clear(). Enables repeating form rows like order line items","FormArray is a type of FormGroup","Arrays handle validation automatically"],"correctAnswer":"A dynamically-sized array of form controls or groups — controls can be added/removed at runtime with push(), removeAt(), clear(). Enables repeating form rows like order line items","explanation":"FormGroup: fixed set of named controls. FormArray: indexed list of controls. addItem() pushes a new FormGroup. removeItem(i) removes it. .controls gives array of AbstractControls. .value gives array of values."},
  {"id":"d68q4","prompt":"What should a custom validator return when validation passes?","options":["true","null — returning null means the control is valid. Returning a ValidationErrors object (e.g., { required: true }) means invalid","{ valid: true }","An empty object {}"],"correctAnswer":"null — returning null means the control is valid. Returning a ValidationErrors object (e.g., { required: true }) means invalid","explanation":"Validator function signature: (control: AbstractControl) => ValidationErrors | null. null = valid. { myError: true } = invalid with 'myError' key. Template: control.errors?.['myError'] to show the specific error message."},
  {"id":"d68q5","prompt":"What does `form.getRawValue()` do vs `form.value`?","options":["Identical","getRawValue() includes disabled controls in the result; form.value excludes them. Use getRawValue() when you need all field values regardless of disabled state","getRawValue() skips validation","form.value returns raw strings"],"correctAnswer":"getRawValue() includes disabled controls in the result; form.value excludes them. Use getRawValue() when you need all field values regardless of disabled state","explanation":"form.get('customerId')?.disable() → form.value won't have customerId. form.getRawValue() → includes customerId. Common pattern: disable fields to prevent editing but still include their values in submission payload."},
  {"id":"d68q6","prompt":"What is `statusChanges` on a FormGroup?","options":["Tracks HTTP request status","An Observable that emits 'VALID', 'INVALID', 'PENDING', or 'DISABLED' whenever the form's validation status changes — useful for async validation indicators","statusChanges is for debugging only","Emits only on form submit"],"correctAnswer":"An Observable that emits 'VALID', 'INVALID', 'PENDING', or 'DISABLED' whenever the form's validation status changes — useful for async validation indicators","explanation":"PENDING: one or more async validators are running. VALID: all validators pass. INVALID: at least one validator fails. DISABLED: form is disabled. Subscribe to show loading spinner while async validators check uniqueness."},
  {"id":"d68q7","prompt":"Why must an async validator Observable complete (e.g., using `first()`)?","options":["For performance","Angular waits for the Observable to complete before resolving the status. If it never completes, the form stays in 'PENDING' state forever — never becomes VALID or INVALID","first() prevents multiple checks","Async validators must return Promises"],"correctAnswer":"Angular waits for the Observable to complete before resolving the status. If it never completes, the form stays in 'PENDING' state forever — never becomes VALID or INVALID","explanation":"Async validators: must return Observable<ValidationErrors|null> or Promise. Observable must complete. Use first() or take(1) to complete after first HTTP response. Without it: statusChanges emits PENDING and stays there."},
  {"id":"d68q8","prompt":"What does `valueChanges.pipe(debounceTime(300), switchMap(...))` achieve in a form control?","options":["Caches form values","Waits 300ms after the last keystroke before making a search request, cancels previous in-flight requests if the user keeps typing — avoids a new API call on every keystroke","debounceTime blocks updates","switchMap adds a delay"],"correctAnswer":"Waits 300ms after the last keystroke before making a search request, cancels previous in-flight requests if the user keeps typing — avoids a new API call on every keystroke","explanation":"valueChanges: emits on every keystroke. debounceTime(300): suppress until 300ms quiet. switchMap: cancels previous Observable (previous HTTP request) when new value arrives. Combined: type 'abcd' quickly → only one request for 'abcd'."},
  {"id":"d68q9","prompt":"What is a cross-field validator and how do you apply it?","options":["Validates multiple fields of the same type","A validator applied to a FormGroup (not a control) that can compare multiple controls — e.g., password and confirmPassword must match. Applied as the second argument to FormGroup: fb.group({...}, { validators: [passwordMatch] })","Cross-field validators use HTTP","Applied at component level"],"correctAnswer":"A validator applied to a FormGroup (not a control) that can compare multiple controls — e.g., password and confirmPassword must match. Applied as the second argument to FormGroup: fb.group({...}, { validators: [passwordMatch] })","explanation":"Cross-field: group.get('password')?.value vs group.get('confirmPassword')?.value. Applied to the FormGroup, not individual controls. Access error: form.errors?.['mismatch']. To show error near confirm field: form.hasError('mismatch')."},
  {"id":"d68q10","prompt":"What does `formArrayName` directive do in the template?","options":["Names the HTML form","Binds a template section to a FormArray in the TypeScript model — required to iterate form array controls with formGroupName or formControlName inside","formArrayName is a CSS class","Required for all arrays"],"correctAnswer":"Binds a template section to a FormArray in the TypeScript model — required to iterate form array controls with formGroupName or formControlName inside","explanation":"<div formArrayName='items'>: binds to the 'items' FormArray. Inside: <div [formGroupName]='i'> binds to items.controls[i]. Without formArrayName, Angular doesn't know which array the child controls belong to."}
],
"writtenConceptQuestions": [
  "Build an order form with customerId, items (FormArray), and address nested group. Include required validators and show error messages.",
  "Show typed reactive forms (Angular 14+) with nonNullable controls. How does form.value type differ from the default?",
  "Write a custom async validator that checks username availability with 300ms debounce. Why is first() needed?",
  "Show a cross-field passwordMatch validator applied to a FormGroup.",
  "What is the difference between form.value and form.getRawValue()? Show with a disabled control.",
  "Show how to implement dynamic line items in a shopping cart using FormArray with add/remove buttons.",
  "Show valueChanges with debounceTime and switchMap for a product search autocomplete."
],
"businessScenarios": [
  "A checkout form has shipping and billing addresses with identical fields. Implement both as nested FormGroups with a 'same as shipping' checkbox that copies values using patchValue.",
  "An invoice form needs N line items, each with product, quantity, and price. Build with FormArray supporting add/remove, and compute the total reactively using valueChanges.",
  "A username registration field should check uniqueness in real-time. Add an async validator with debounce that calls UserService.checkUsername() and shows a loading indicator via statusChanges."
]
},

"day-069": {
"notes": """# Angular Template-Driven Forms: ngModel, ngForm, and Validation

## Template-Driven Forms Setup
```typescript
@Component({
  standalone: true,
  imports: [FormsModule],  // provides ngModel, ngForm
  template: `...`
})
export class ContactFormComponent {
  // Model object — two-way bound from the template
  contact = { name: '', email: '', phone: '', message: '' };
  submitted = false;

  onSubmit(form: NgForm) {
    if (form.invalid) return;
    console.log(form.value);  // { name: '...', email: '...', ... }
    this.submitted = true;
    form.reset();
  }
}
```

## Template — ngForm and ngModel
```html
<form #contactForm="ngForm" (ngSubmit)="onSubmit(contactForm)">

  <!-- ngModel with name attribute — required for NgForm tracking -->
  <input
    [(ngModel)]="contact.name"
    name="name"
    required
    minlength="2"
    #nameField="ngModel"
    placeholder="Full Name"
  />
  <!-- Show error only when touched and invalid -->
  <div *ngIf="nameField.touched && nameField.invalid">
    <span *ngIf="nameField.errors?.['required']">Name is required</span>
    <span *ngIf="nameField.errors?.['minlength']">Minimum 2 characters</span>
  </div>

  <input
    [(ngModel)]="contact.email"
    name="email"
    type="email"
    required
    email
    #emailField="ngModel"
    placeholder="Email"
  />
  <div *ngIf="emailField.touched && emailField.errors?.['email']">
    Invalid email format
  </div>

  <button [disabled]="contactForm.invalid">Submit</button>
</form>
```

## ngModel States and CSS Classes
```
ngModel state:  Angular CSS class:   Meaning
untouched       .ng-untouched        user hasn't interacted
touched         .ng-touched          user focused and blurred
pristine        .ng-pristine         value unchanged since init
dirty           .ng-dirty            user has typed something
valid           .ng-valid            all validators pass
invalid         .ng-invalid          at least one validator fails
pending         .ng-pending          async validator running
```
```css
/* Automatic CSS for field states */
input.ng-invalid.ng-touched { border: 1px solid red; }
input.ng-valid.ng-dirty      { border: 1px solid green; }
```

## ngModelGroup — Grouping Fields
```html
<form #orderForm="ngForm" (ngSubmit)="onSubmit(orderForm)">
  <div ngModelGroup="address">
    <input [(ngModel)]="order.address.street" name="street" required />
    <input [(ngModel)]="order.address.city"   name="city"   required />
    <input [(ngModel)]="order.address.zip"    name="zip"    required pattern="\d{5}" />
  </div>
  <input [(ngModel)]="order.note" name="note" />
  <button type="submit">Order</button>
</form>
<!-- form.value.address.street — grouped in ngModelGroup -->
```

## ngForm Reference — Programmatic Access
```typescript
@ViewChild('contactForm') contactForm!: NgForm;

resetForm() {
  this.contactForm.reset();         // resets all values AND resets valid/touched state
  this.contact = { name: '', email: '', phone: '', message: '' };
}

patchContact() {
  this.contactForm.setValue({       // set all fields
    name: 'John', email: 'j@example.com', phone: '', message: ''
  });
}
```

## Template-Driven vs Reactive Forms Comparison
```
Feature                | Template-Driven  | Reactive
-----------------------|------------------|---------------------------
Model location         | HTML template    | TypeScript class
Form creation          | Angular infers   | Explicit FormGroup/Control
Testing                | Requires TestBed | Unit test without TestBed
Dynamic forms          | Harder           | Easy (FormArray)
Custom validation      | Directives       | Plain functions
Async validation       | Directives       | Validators on control
Complex forms          | Messy            | Recommended
Simple forms           | Fine             | Also fine
```

## Custom Validation Directive for Template-Driven Forms
```typescript
@Directive({
  selector: '[appNoSpaces]',
  standalone: true,
  providers: [{ provide: NG_VALIDATORS, useExisting: NoSpacesDirective, multi: true }]
})
export class NoSpacesDirective implements Validator {
  validate(control: AbstractControl): ValidationErrors | null {
    return control.value?.includes(' ')
      ? { noSpaces: { value: control.value } }
      : null;
  }
}
// Usage: <input [(ngModel)]="username" name="username" appNoSpaces />
```

## Common Mistakes
1. **Missing `name` attribute with ngModel:** without `name`, Angular can't register the control with NgForm — no validation tracking.
2. **Resetting the model but not the form:** `this.contact = {}` resets the data but not `touched`/`dirty` states. Use `form.reset()`.
3. **Using template-driven for complex conditional forms:** switching to reactive forms is better when form structure depends on runtime conditions.
""",
"mcqs": [
  {"id":"d69q1","prompt":"What is required for Angular to track an ngModel control in NgForm?","options":["[(ngModel)] alone","Both `[(ngModel)]` AND the `name` attribute — Angular uses the name to register the control in the form model and expose it in form.value","ngForm attribute","formControlName"],"correctAnswer":"Both `[(ngModel)]` AND the `name` attribute — Angular uses the name to register the control in the name to register the control in the form model and expose it in form.value","explanation":"Without name: Angular ignores the control for form-level tracking (no form.value, no form.valid). name='email': form.value.email is populated; #emailField='ngModel' gives a reference to the control's NgModel instance."},
  {"id":"d69q2","prompt":"What CSS class does Angular add to a touched and invalid input?","options":["ng-error","Angular adds both `.ng-touched` and `.ng-invalid` classes — used for CSS styling validation states without custom JavaScript","ng-invalid-touched","is-invalid"],"correctAnswer":"Angular adds both `.ng-touched` and `.ng-invalid` classes — used for CSS styling validation states without custom JavaScript","explanation":"Angular's form CSS classes: ng-pristine/ng-dirty (changed?), ng-untouched/ng-touched (interacted?), ng-valid/ng-invalid (passes validators?). Target with CSS: input.ng-invalid.ng-touched { border: 1px solid red }."},
  {"id":"d69q3","prompt":"What does `#contactForm='ngForm'` do?","options":["Creates a CSS class","Creates a template reference variable pointing to the NgForm directive instance — gives access to contactForm.valid, contactForm.value, contactForm.reset() in the template and via @ViewChild","Required for form submission","Names the HTML form element"],"correctAnswer":"Creates a template reference variable pointing to the NgForm directive instance — gives access to contactForm.valid, contactForm.value, contactForm.reset() in the template and via @ViewChild","explanation":"#form='ngForm': the variable holds the NgForm directive, not the HTMLFormElement. Access form.invalid, form.value in template. In component: @ViewChild('contactForm') form: NgForm — programmatic access."},
  {"id":"d69q4","prompt":"What is `ngModelGroup` used for?","options":["Groups ngModels for CSS","Groups related form controls under a key in the form value — `<div ngModelGroup='address'>` makes nested controls appear as form.value.address.street","Required for validation","ngModelGroup creates a FormGroup"],"correctAnswer":"Groups related form controls under a key in the form value — `<div ngModelGroup='address'>` makes nested controls appear as form.value.address.street","explanation":"Without ngModelGroup: all controls flat in form.value. With ngModelGroup='address': form.value = { address: { street, city, zip }, note }. Mirrors reactive forms' nested FormGroup for template-driven forms."},
  {"id":"d69q5","prompt":"Why doesn't `this.contact = {}` fully reset the form?","options":["JavaScript error","It resets the data model but leaves Angular's form state (touched, dirty, valid) unchanged — users still see validation errors. Use form.reset() to reset both data and form state","contact must be immutable","Two-way binding prevents reset"],"correctAnswer":"It resets the data model but leaves Angular's form state (touched, dirty, valid) unchanged — users still see validation errors. Use form.reset() to reset both data and form state","explanation":"form.reset(): resets control values to initial and marks all as pristine/untouched. Then update the model: this.contact = { name: '', email: '' }. Or form.reset({ name: '', email: '' }) to reset to specific values."},
  {"id":"d69q6","prompt":"How do you create a custom validation directive for template-driven forms?","options":["Add a validator attribute","Implement the Validator interface and provide with `{ provide: NG_VALIDATORS, useExisting: MyDirective, multi: true }` — Angular calls validate() on this directive as part of ngModel validation","Create a class with validate()","Use @Input with a boolean"],"correctAnswer":"Implement the Validator interface and provide with `{ provide: NG_VALIDATORS, useExisting: MyDirective, multi: true }` — Angular calls validate() on this directive as part of ngModel validation","explanation":"NG_VALIDATORS multi-provider: Angular collects all validators for a control from this token. multi: true appends to the list instead of replacing. The directive's validate() runs alongside built-in validators."},
  {"id":"d69q7","prompt":"What does `nameField.dirty` mean?","options":["The field has an error","The field's value has been changed by the user since it was initialised — contrasted with pristine (unchanged). Used to show validation errors only after user interaction","dirty means invalid","dirty tracks server errors"],"correctAnswer":"The field's value has been changed by the user since it was initialised — contrasted with pristine (unchanged). Used to show validation errors only after user interaction","explanation":"pristine: true before user types. dirty: true after first change. touched: true after user focuses and blurs. Common pattern: show error only when dirty OR touched — don't show errors on a fresh form the user hasn't interacted with yet."},
  {"id":"d69q8","prompt":"What is the `email` validator in template-driven forms?","options":["Checks if email exists","HTML5 email input type validation in Angular — the `email` attribute on an ngModel input enables Angular's built-in email format validator. Error key: errors?.['email']","Must be added manually","email validator requires an API call"],"correctAnswer":"HTML5 email input type validation in Angular — the `email` attribute on an ngModel input enables Angular's built-in email format validator. Error key: errors?.['email']","explanation":"<input type='email' ngModel email />: Angular's built-in Validators.email equivalent for template-driven. Validates format (x@x.x), not existence. errors?.['email']: true if invalid format."},
  {"id":"d69q9","prompt":"When should you prefer Reactive Forms over Template-Driven Forms?","options":["Always use reactive forms","For complex forms: dynamic fields (FormArray), programmatic value setting, cross-field validation, async validators, and unit testing without a browser. Template-driven is fine for simple, static forms","Template forms are always simpler","Reactive forms require more imports"],"correctAnswer":"For complex forms: dynamic fields (FormArray), programmatic value setting, cross-field validation, async validators, and unit testing without a browser. Template-driven is fine for simple, static forms","explanation":"Reactive: explicit control in TypeScript. Test FormGroup validation without Angular TestBed. FormArray for dynamic items. patchValue/setValue programmatically. Template-driven: less boilerplate for simple login/contact forms."},
  {"id":"d69q10","prompt":"What does `(ngSubmit)='onSubmit(contactForm)'` do?","options":["Submits to a server","Fires the onSubmit method when the HTML form is submitted (button click or Enter key) and passes the NgForm directive instance — prevents default HTML form submission","(submit) and (ngSubmit) are identical","ngSubmit requires a FormGroup"],"correctAnswer":"Fires the onSubmit method when the HTML form is submitted (button click or Enter key) and passes the NgForm directive instance — prevents default HTML form submission","explanation":"ngSubmit: Angular's form submission event that calls event.preventDefault() automatically — no page reload. Passes the NgForm reference with .valid, .value, .reset(). (submit) would trigger browser's default form submission."}
],
"writtenConceptQuestions": [
  "Build a contact form with ngModel binding, required/email/minlength validators, and CSS error classes.",
  "Explain all ngModel states: pristine, dirty, touched, untouched, valid, invalid. Show CSS targeting each.",
  "How do you create a custom validation directive for template-driven forms? Show NoSpaces example.",
  "Show ngModelGroup for grouping address fields. What does form.value look like with vs without grouping?",
  "Compare template-driven vs reactive forms: when do you choose each? Show the same form in both styles.",
  "Show @ViewChild on #form='ngForm' and use it to call form.reset() programmatically.",
  "What is the `email` built-in validator in template-driven forms? Show error display."
],
"businessScenarios": [
  "A simple newsletter signup form needs name, email, and preference. Implement as template-driven form with validation and CSS error states.",
  "An admin user needs to reset a form to a specific state programmatically after cancelling an edit. Use @ViewChild NgForm and form.reset() with values.",
  "A feedback form groups personal info (name, email) and message separately. Use ngModelGroup to structure the submitted data."
]
},

"day-070": {
"notes": """# Angular HTTP Client: Interceptors, Error Handling, and Advanced Patterns

## provideHttpClient — Setup
```typescript
// app.config.ts (Angular 17+ standalone)
export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([authInterceptor, errorInterceptor, loggingInterceptor]),
      withFetch()  // use browser fetch API instead of XMLHttpRequest
    )
  ]
};
```

## Functional HTTP Interceptors (Angular 15+)
```typescript
// auth.interceptor.ts — adds Bearer token to every request
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(AuthService).getToken();

  if (!token) return next(req);  // pass through unauthenticated requests

  const authReq = req.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  });
  return next(authReq);
};

// error.interceptor.ts — global error handling
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      switch (error.status) {
        case 401:
          inject(AuthService).logout();
          inject(Router).navigate(['/login']);
          break;
        case 403:
          inject(Router).navigate(['/forbidden']);
          break;
        case 0:
          inject(SnackbarService).show('No internet connection');
          break;
        default:
          inject(SnackbarService).show(`Error: ${error.message}`);
      }
      return throwError(() => error);  // re-throw so caller can also handle
    })
  );
};

// loading.interceptor.ts — global loading indicator
export const loadingInterceptor: HttpInterceptorFn = (req, next) => {
  const loading = inject(LoadingService);
  loading.increment();
  return next(req).pipe(
    finalize(() => loading.decrement())
  );
};
```

## HttpContext — Passing Metadata to Interceptors
```typescript
// Define a context token to skip auth on certain requests
export const SKIP_AUTH = new HttpContextToken<boolean>(() => false);

// In interceptor: check the token
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  if (req.context.get(SKIP_AUTH)) return next(req);  // skip auth for public endpoints
  // add auth header...
};

// In service: set context on specific requests
this.http.post('/api/auth/login', credentials, {
  context: new HttpContext().set(SKIP_AUTH, true)  // don't add auth header to login
});
```

## Retry and Timeout Patterns
```typescript
@Injectable({ providedIn: 'root' })
export class OrderService {
  private http = inject(HttpClient);

  getOrders(): Observable<OrderDto[]> {
    return this.http.get<OrderDto[]>('/api/orders').pipe(
      timeout(5000),                               // fail if no response in 5s
      retry({ count: 3, delay: 1000 }),            // retry up to 3 times with 1s delay
      catchError(err => {
        if (err instanceof TimeoutError) {
          return throwError(() => new Error('Request timed out'));
        }
        return throwError(() => err);
      })
    );
  }
}
```

## Typed HttpClient Responses
```typescript
// Generic response types
interface Page<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  number: number;
  size: number;
}

getOrders(page = 0, size = 20): Observable<Page<OrderDto>> {
  return this.http.get<Page<OrderDto>>('/api/orders', {
    params: { page, size }
  });
}

// Upload with progress
uploadFile(file: File): Observable<HttpEvent<any>> {
  const formData = new FormData();
  formData.append('file', file);

  return this.http.post('/api/uploads', formData, {
    reportProgress: true,
    observe: 'events'
  }).pipe(
    filter(event => event.type === HttpEventType.UploadProgress),
    map(event => ({
      progress: Math.round(100 * (event as HttpUploadProgressEvent).loaded /
                                  (event as HttpUploadProgressEvent).total!)
    }))
  );
}
```

## Common Mistakes
1. **Multiple interceptors in wrong order:** interceptors run in registration order for requests, reverse order for responses.
2. **Forgetting `withInterceptors` in provideHttpClient:** functional interceptors require explicit opt-in.
3. **Not re-throwing errors after handling:** if your interceptor catches and doesn't re-throw, the calling code can't detect failure.
""",
"mcqs": [
  {"id":"d70q1","prompt":"What does an HTTP interceptor do?","options":["Caches HTTP responses","Intercepts every HTTP request and/or response — can add headers, log, handle errors, show loading state — without modifying individual service calls","Only intercepts 401 errors","Interceptors replace HttpClient"],"correctAnswer":"Intercepts every HTTP request and/or response — can add headers, log, handle errors, show loading state — without modifying individual service calls","explanation":"Interceptors form a chain. Each receives (req, next): req is the outgoing request; next(req) passes it to the next interceptor or HttpClient. Modify request: req.clone({setHeaders:...}); handle response: next(req).pipe(catchError(...))"},
  {"id":"d70q2","prompt":"Why must HTTP requests be cloned before modifying in an interceptor?","options":["HttpRequest is immutable — .clone() creates a new request with changes. Directly mutating the request would cause bugs since the same request object may be referenced elsewhere","Clone creates a new HTTP connection","Cloning is optional","Immutability is only for security"],"correctAnswer":"HttpRequest is immutable — .clone() creates a new request with changes. Directly mutating the request would cause bugs since the same request object may be referenced elsewhere","explanation":"req.clone({ setHeaders: { Authorization: 'Bearer ...' } }): returns a new HttpRequest with the header added. The original req is unchanged. All interceptors in the chain see the correctly modified request."},
  {"id":"d70q3","prompt":"What does `req.context.get(SKIP_AUTH)` do in an interceptor?","options":["Gets the request URL","Reads a typed metadata value attached to this specific request — HttpContextToken allows passing per-request configuration to interceptors without modifying the service API","context.get returns boolean only","SKIP_AUTH is a standard header"],"correctAnswer":"Reads a typed metadata value attached to this specific request — HttpContextToken allows passing per-request configuration to interceptors without modifying the service API","explanation":"HttpContext: per-request metadata bag. SKIP_AUTH token: defined with new HttpContextToken<boolean>(() => false). Service sets it: { context: new HttpContext().set(SKIP_AUTH, true) }. Interceptor reads it to decide behaviour."},
  {"id":"d70q4","prompt":"What does `finalize(() => loading.decrement())` do in a loading interceptor?","options":["Handles final response","Runs the callback whether the Observable completes successfully or errors — ensures loading counter is always decremented even on HTTP errors","finalize is like tap","finalize delays the response"],"correctAnswer":"Runs the callback whether the Observable completes successfully or errors — ensures loading counter is always decremented even on HTTP errors","explanation":"finalize: the RxJS equivalent of finally. Without it: HTTP error → catchError doesn't call next → finalize still runs. Guarantees loading indicator is hidden even if the request fails. Essential for loading counters."},
  {"id":"d70q5","prompt":"What does `retry({ count: 3, delay: 1000 })` do?","options":["Retries indefinitely","Retries a failed Observable up to 3 times with a 1000ms delay between attempts — if all retries fail, the error is propagated","retry overrides catchError","retry works on any Observable"],"correctAnswer":"Retries failed Observable up to 3 times with a 1000ms delay between attempts — if all retries fail, the error is propagated","explanation":"retry: subscribes again on error. count: max attempts. delay: ms between attempts. Can use: delay: (err, i) => timer(i * 1000) for exponential backoff. Network errors (status 0) are good candidates for retry; 4xx errors should not be retried."},
  {"id":"d70q6","prompt":"In what order do Angular interceptors run?","options":["Alphabetical order","Requests: in registration order (first registered runs first). Responses: in reverse registration order (last registered handles response first)","Random order","All interceptors run simultaneously"],"correctAnswer":"Requests: in registration order (first registered runs first). Responses: in reverse registration order (last registered handles response first)","explanation":"withInterceptors([auth, error, logging]): request → auth → error → logging → server. Response → logging → error → auth. Like middleware stacks. Place auth first (header added before error checking). Place logging last to capture the full request/response."},
  {"id":"d70q7","prompt":"What is `observe: 'events'` with `reportProgress: true` used for?","options":["Logs request events","Enables access to fine-grained upload/download progress events — HttpEventType.UploadProgress gives bytes uploaded/total for file upload progress bars","observe: 'events' is the default","Only works with WebSocket"],"correctAnswer":"Enables access to fine-grained upload/download progress events — HttpEventType.UploadProgress gives bytes uploaded/total for file upload progress bars","explanation":"Default observe:'body': just the response body. observe:'response': full HttpResponse (status, headers, body). observe:'events': all events (Sent, UploadProgress, DownloadProgress, Response). Filter by event.type for specific progress updates."},
  {"id":"d70q8","prompt":"What does `withFetch()` do in `provideHttpClient(withFetch())`?","options":["Fetches from a local file","Switches Angular's HttpClient to use the browser's native Fetch API instead of XMLHttpRequest — enables streaming, better performance, and compatibility with the Request/Response APIs","withFetch adds caching","Required for all Angular 17 apps"],"correctAnswer":"Switches Angular's HttpClient to use the browser's native Fetch API instead of XMLHttpRequest — enables streaming, better performance, and compatibility with the Request/Response APIs","explanation":"XHR is the historical HTTP transport. Fetch is the modern API. withFetch(): opt-in to Fetch. Benefits: streaming support, uses Web Streams, lighter API. Currently optional; may become default in future Angular versions."},
  {"id":"d70q9","prompt":"What happens when an interceptor calls `throwError(() => error)` after handling it?","options":["Throws a JavaScript exception","Re-propagates the error down the Observable chain — the calling service's catchError or subscribe error handler still receives it. Enables both interceptor-level handling (e.g., logout) and caller-level handling (e.g., show form error)","throwError retries the request","The next interceptor is skipped"],"correctAnswer":"Re-propagates the error down the Observable chain — the calling service's catchError or subscribe error handler still receives it. Enables both interceptor-level handling (e.g., logout) and caller-level handling (e.g., show form error)","explanation":"Error interceptor handles 401 (logout) then throwError(). The form component's subscribe error callback also receives the 401. If interceptor swallowed it (returned EMPTY): component doesn't know the request failed — can't show specific errors."},
  {"id":"d70q10","prompt":"What is the HttpParams API used for?","options":["Custom HTTP headers","Building URL query parameters — HttpParams is immutable (each operation returns new instance): new HttpParams().set('page','0').set('size','20') → ?page=0&size=20","HttpParams are the request body","Required for POST requests"],"correctAnswer":"Building URL query parameters — HttpParams is immutable (each operation returns new instance): new HttpParams().set('page','0').set('size','20') → ?page=0&size=20","explanation":"this.http.get('/api/orders', { params: { page: 0, size: 20 } }): Angular converts the object to HttpParams. Or: new HttpParams({ fromObject: { status: 'PENDING' } }). HttpParams.set returns a NEW instance — always chain or reassign."}
],
"writtenConceptQuestions": [
  "Write an authInterceptor that adds Bearer token from AuthService, and an errorInterceptor that handles 401/403/0 status codes.",
  "Show HttpContextToken (SKIP_AUTH) usage: define, provide from a service, and read in interceptor.",
  "Show a retry pattern with exponential backoff for a flaky API call.",
  "How do interceptors compose? Show auth + loading + error interceptors and their execution order.",
  "Show file upload with HttpEventType.UploadProgress for a progress bar.",
  "What is the difference between observe:'body', observe:'response', and observe:'events'?",
  "Show a full HttpParams construction for a paginated, filtered GET request."
],
"businessScenarios": [
  "Every API call should show a global loading spinner. Implement a LoadingService counter and a loading interceptor using finalize().",
  "When a 401 error occurs on any request, the user should be logged out and redirected to login. Add global 401 handling in errorInterceptor.",
  "A file upload form needs a progress bar. Use HttpClient with reportProgress:true and observe:'events' to track upload percentage."
]
},

"day-071": {
"notes": """# Angular RxJS: Core Operators and Patterns

## Essential Transformation Operators
```typescript
// map — transform each emitted value
of(1, 2, 3).pipe(
  map(n => n * 10)  // 10, 20, 30
);

// Products from API — map HTTP response to domain objects
this.http.get<ProductDto[]>('/api/products').pipe(
  map(dtos => dtos.map(dto => new Product(dto)))
);

// filter — pass only values matching predicate
from([1, 2, 3, 4, 5]).pipe(
  filter(n => n % 2 === 0)  // 2, 4
);

// tap — side effects without changing the stream
this.http.get<Order[]>('/api/orders').pipe(
  tap(orders => console.log('Fetched:', orders.length)),
  tap(orders => this.analytics.track('orders-loaded'))
);

// scan — accumulate values like array.reduce
const runningTotal$ = prices$.pipe(
  scan((acc, price) => acc + price, 0)
  // 10 → 10, 5 → 15, 20 → 35
);
```

## Higher-Order Mapping Operators
```typescript
// switchMap — cancel previous inner Observable on each new emission
// USE WHEN: typeahead search (only care about latest query)
searchTerm$.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  switchMap(term => this.http.get<Product[]>(`/api/products?q=${term}`))
  // typing 'apple' → request, then 'app' → previous request CANCELLED, new request
);

// mergeMap (flatMap) — run all inner Observables concurrently
// USE WHEN: parallel HTTP requests where ALL results are needed
productIds$.pipe(
  mergeMap(id => this.http.get<Product>(`/api/products/${id}`))
  // 3 ids → 3 concurrent requests, results in arrival order
);

// concatMap — wait for each inner Observable to complete before starting next
// USE WHEN: sequential operations where order matters (e.g., save then redirect)
saveActions$.pipe(
  concatMap(action => this.http.post('/api/actions', action))
  // action1 → save → action2 → save (sequential, preserves order)
);

// exhaustMap — ignore new emissions while inner Observable is active
// USE WHEN: submit button (ignore double-clicks while request is in flight)
submitClicks$.pipe(
  exhaustMap(() => this.http.post('/api/orders', order))
  // 3 rapid clicks → only 1 request, others IGNORED
);
```

## Combination Operators
```typescript
// combineLatest — emits when ANY source emits, with latest values from ALL
const dashboard$ = combineLatest([
  this.ordersService.orders$,
  this.userService.currentUser$,
  this.settingsService.settings$
]).pipe(
  map(([orders, user, settings]) => ({ orders, user, settings }))
);

// forkJoin — emit once when ALL Observables complete
// USE WHEN: load all data for a page on init
forkJoin({
  products: this.http.get<Product[]>('/api/products'),
  categories: this.http.get<Category[]>('/api/categories'),
  user: this.http.get<User>('/api/user/me')
}).subscribe(({ products, categories, user }) => {
  this.products = products;
  this.categories = categories;
  this.user = user;
});

// withLatestFrom — combine with latest value from another stream (no subscription trigger)
saveButton$.pipe(
  withLatestFrom(this.orderForm.valueChanges),
  map(([_click, formValue]) => formValue),
  switchMap(value => this.http.post('/api/orders', value))
);
```

## Error Handling Operators
```typescript
// catchError — recover from errors
this.http.get<Product[]>('/api/products').pipe(
  catchError(err => {
    if (err.status === 404) return of([]);        // empty array fallback
    return throwError(() => err);                 // re-throw others
  })
);

// retryWhen / retry
this.http.get('/api/data').pipe(
  retry({ count: 3, delay: (error, retryCount) => timer(retryCount * 1000) })
);
```

## Filtering Operators
```typescript
// distinctUntilChanged — don't emit if value hasn't changed
searchInput$.pipe(
  debounceTime(300),
  distinctUntilChanged()  // 'apple', 'apple', 'apples' → 'apple', 'apples'
);

// take, takeUntil, first, last
observable$.pipe(take(3));           // complete after 3 emissions
observable$.pipe(takeUntil(stop$));  // complete when stop$ emits
observable$.pipe(first());           // complete after first emission
```

## Common Mistakes
1. **Using `mergeMap` for search:** multiple concurrent requests mean out-of-order results. Use `switchMap` for search.
2. **Forgetting `distinctUntilChanged` with debounce:** without it, same value triggers API call on each emission.
3. **Subscribing inside `switchMap`:** never nest subscribe calls. Use higher-order mapping operators instead.
""",
"mcqs": [
  {"id":"d71q1","prompt":"When should you use `switchMap` vs `mergeMap`?","options":["They are interchangeable","switchMap: cancel previous inner Observable when a new value arrives — use for typeahead/search where you only care about the latest. mergeMap: run all inner Observables concurrently — use when all results are needed","mergeMap is always faster","switchMap only works with HTTP"],"correctAnswer":"switchMap: cancel previous inner Observable when a new value arrives — use for typeahead/search where you only care about the latest. mergeMap: run all inner Observables concurrently — use when all results are needed","explanation":"Search: switchMap — user types 'apple', then 'app'. switchMap cancels 'apple' request, issues 'app' request. mergeMap would keep both — 'apple' result might arrive after 'app', showing stale data. mergeMap: delete 5 items in parallel, need all 5 confirmations."},
  {"id":"d71q2","prompt":"What does `exhaustMap` do and when is it used?","options":["Maps exhaustively","Ignores new emissions while the inner Observable is still active — ideal for form submission: if the user clicks Submit twice quickly, only the first click's request is made; the second click is dropped","exhaustMap is like switchMap","exhaustMap requires a timer"],"correctAnswer":"Ignores new emissions while the inner Observable is still active — ideal for form submission: if the user clicks Submit twice quickly, only the first click's request is made; the second click is dropped","explanation":"submitBtn.clicks.pipe(exhaustMap(() => http.post('/api/orders', data))). 5 rapid clicks: only 1 HTTP request. Others exhausted while first is in flight. Prevents duplicate order submission. Complementary: disable the button while submitting."},
  {"id":"d71q3","prompt":"What does `combineLatest` do?","options":["Combines the first emissions","Emits an array of the LATEST values from ALL source Observables whenever ANY one of them emits — requires all sources to emit at least once","combineLatest waits for all to complete","Same as forkJoin"],"correctAnswer":"Emits an array of the LATEST values from ALL source Observables whenever ANY one of them emits — requires all sources to emit at least once","explanation":"combineLatest([a$, b$]): waits until both emit once, then emits [latestA, latestB] whenever either changes. Use for reactive dashboards where multiple independent streams power one view. forkJoin: only emits once when ALL complete."},
  {"id":"d71q4","prompt":"What is `forkJoin` best used for?","options":["Polling multiple APIs","Waiting for multiple Observables to ALL complete and emit their last values as an array or object — like Promise.all for Observables. Use to load all prerequisite data for a page","forkJoin emits on each change","forkJoin cancels on error by default"],"correctAnswer":"Waiting for multiple Observables to ALL complete and emit their last values as an array or object — like Promise.all for Observables. Use to load all prerequisite data for a page","explanation":"forkJoin({ users: http.get('/api/users'), roles: http.get('/api/roles') }): makes both HTTP requests in parallel, emits { users: [...], roles: [...] } when both complete. If either errors, the whole forkJoin errors."},
  {"id":"d71q5","prompt":"What does `scan` do?","options":["Scans the DOM","Accumulates emitted values like Array.reduce — maintains a running state: scan((acc, val) => acc + val, 0) over [1,2,3] emits 1, 3, 6 (running sum)","scan is for error detection","scan replaces map"],"correctAnswer":"Accumulates emitted values like Array.reduce — maintains a running state: scan((acc, val) => acc + val, 0) over [1,2,3] emits 1, 3, 6 (running sum)","explanation":"scan: like reduce but emits intermediate values. Use: running total, building an array incrementally (scan((acc, item) => [...acc, item], [])), counting events. reduce: only emits the final value after completion."},
  {"id":"d71q6","prompt":"What does `distinctUntilChanged` do?","options":["Filters duplicates from arrays","Suppresses consecutive duplicate emissions — if the same value is emitted twice in a row, the second is filtered. Combined with debounceTime in search: prevents re-fetching for the same query","Required for debounceTime","Compares by reference only"],"correctAnswer":"Suppresses consecutive duplicate emissions — if the same value is emitted twice in a row, the second is filtered. Combined with debounceTime in search: prevents re-fetching for the same query","explanation":"searchTerm$ emitting: 'a', 'ab', 'ab', 'abc'. Without distinctUntilChanged: 3 API calls for 'ab'. With it: 2 ('ab', 'abc'). By default compares with ===. Custom comparator: distinctUntilChanged((a,b) => a.id === b.id) for objects."},
  {"id":"d71q7","prompt":"What does `tap` do and when should it be used?","options":["Tap the Observable","Perform side effects without modifying the stream — debugging, logging, analytics tracking. tap(value => console.log(value)) passes value through unchanged","tap transforms values","tap is deprecated in favor of map"],"correctAnswer":"Perform side effects without modifying the stream — debugging, logging, analytics tracking. tap(value => console.log(value)) passes value through unchanged","explanation":"map: transforms value. tap: side effect only. tap receives the value, performs action, returns the SAME value downstream. Use for: console.log debugging, analytics.track(), cache updates, without affecting the stream's data."},
  {"id":"d71q8","prompt":"What is `withLatestFrom` used for?","options":["Gets the latest HTTP response","Combines a trigger Observable with the latest value of another Observable — the trigger causes emission; the other source is sampled, not subscribed to for triggering. Use: save button combines with latest form state","withLatestFrom subscribes both sources","Replaces combineLatest"],"correctAnswer":"Combines a trigger Observable with the latest value of another Observable — the trigger causes emission; the other source is sampled, not subscribed to for triggering. Use: save button combines with latest form state","explanation":"saveClicks$.pipe(withLatestFrom(form.value$)): emits [click, latestFormValue] only on clicks, not on every form change. Different from combineLatest which emits on EVERY source change. withLatestFrom: trigger-based."},
  {"id":"d71q9","prompt":"Why should you never subscribe inside a `switchMap` callback?","options":["Technical limitation","Nested subscriptions create memory leaks and are unmanageable — switchMap expects you to return an Observable. Angular manages the inner subscription. Nesting subscribe() inside switchMap() creates orphan subscriptions","switchMap requires Promises","Nested subscriptions are faster"],"correctAnswer":"Nested subscriptions create memory leaks and are unmanageable — switchMap expects you to return an Observable. Angular manages the inner subscription. Nesting subscribe() inside switchMap() creates orphan subscriptions","explanation":"WRONG: switchMap(id => { http.get('/api/'+id).subscribe(r => this.result = r); return EMPTY; }). CORRECT: switchMap(id => http.get('/api/'+id)). The outer pipe handles the inner subscription — no leaks, cancellable."},
  {"id":"d71q10","prompt":"What does `concatMap` ensure that `mergeMap` does not?","options":["Faster completion","Sequential execution — each inner Observable must complete before the next starts. Order is preserved. mergeMap: concurrent, unordered. concatMap: sequential, ordered","concatMap is for error handling","Identical to mergeMap"],"correctAnswer":"Sequential execution — each inner Observable must complete before the next starts. Order is preserved. mergeMap: concurrent, unordered. concatMap: sequential, ordered","explanation":"Audit logs: concatMap ensures events are saved in order. mergeMap: event 3 might be saved before event 2 if network varies. concatMap: 1 completes → 2 starts → 3 starts. Tradeoff: slower total time vs guaranteed ordering."}
],
"writtenConceptQuestions": [
  "Show switchMap for product search with debounceTime and distinctUntilChanged. Why does switchMap prevent stale results?",
  "Compare switchMap, mergeMap, concatMap, exhaustMap with concrete use cases for each.",
  "Show forkJoin loading products, categories, and user in parallel on page init.",
  "Show combineLatest for a reactive dashboard that combines orders, user, and settings streams.",
  "Show scan to build a running cart total from addItem events.",
  "Explain withLatestFrom vs combineLatest. Show save button + form state pattern.",
  "Show retry with exponential backoff using retryCount: retry({ count: 3, delay: (err, i) => timer(i*1000) })."
],
"businessScenarios": [
  "A product search input makes an API call on every keystroke, causing 429 errors. Apply debounceTime(300), distinctUntilChanged(), and switchMap to reduce API calls.",
  "An order form submit button causes duplicate orders when double-clicked. Wrap the submit handler in exhaustMap to drop concurrent submission attempts.",
  "A dashboard loads user profile, order summary, and notifications in sequence (3 HTTP calls). Parallelize with forkJoin."
]
},

"day-072": {
"notes": """# Angular Observables: Cold vs Hot, Creation Operators, and Multicasting

## Cold vs Hot Observables
```typescript
// COLD Observable — creates a new producer for each subscriber
// Each subscriber gets their own independent stream
const cold$ = new Observable(observer => {
  console.log('Producer created');           // logs on EVERY subscribe
  observer.next(Math.random());              // each subscriber gets different value
});

cold$.subscribe(v => console.log('Sub1:', v));  // Producer created, Sub1: 0.342
cold$.subscribe(v => console.log('Sub2:', v));  // Producer created, Sub2: 0.891

// Examples: HttpClient.get() — each subscribe = new HTTP request
// interval(), timer() — each subscribe starts its own timer

// HOT Observable — shares a single producer with all subscribers
// Subscribers join an existing stream — may miss past events
const subject = new Subject<number>();
const hot$ = subject.asObservable();

hot$.subscribe(v => console.log('Sub1:', v));
hot$.subscribe(v => console.log('Sub2:', v));
subject.next(42);  // BOTH subscribers receive 42 — shared producer

// Examples: DOM events, WebSockets, BehaviorSubject, EventEmitter
```

## Creation Operators
```typescript
// of — emit specific values synchronously, then complete
of(1, 2, 3).subscribe(console.log);             // 1, 2, 3, complete

// from — convert iterable or Promise to Observable
from([1, 2, 3]).subscribe(console.log);         // 1, 2, 3, complete
from(Promise.resolve('hello')).subscribe(v => console.log(v)); // hello

// interval / timer
interval(1000).subscribe(n => console.log(n));  // 0, 1, 2... every second
timer(2000).subscribe(() => showBanner());       // once after 2s
timer(0, 1000).subscribe(n => console.log(n));  // starts immediately, then every 1s

// fromEvent — DOM events as Observable
const clicks$ = fromEvent<MouseEvent>(document, 'click');
clicks$.pipe(
  map(e => ({ x: e.clientX, y: e.clientY }))
).subscribe(console.log);

// EMPTY, NEVER, throwError
EMPTY.subscribe({ complete: () => console.log('done') });  // completes immediately
throwError(() => new Error('fail')).subscribe({ error: e => console.error(e) });
```

## Multicasting — shareReplay
```typescript
// Without shareReplay: 3 subscriptions = 3 HTTP requests (cold Observable)
const products$ = this.http.get<Product[]>('/api/products');
// component A subscribes → request 1
// component B subscribes → request 2
// component C subscribes → request 3

// With shareReplay(1): share ONE request, cache last emission
const products$ = this.http.get<Product[]>('/api/products').pipe(
  shareReplay(1)  // 1 = buffer size — new subscribers get last value immediately
);
// component A subscribes → request made
// component B subscribes → receives cached response (no new request)
// After 5 seconds, component C subscribes → receives cached response

// share() — no buffer, no late replay — like Subject
// shareReplay(1) — buffers last value, late subscribers get it immediately
```

## Observable Contract
Every Observable must follow this contract:
- Can emit: 0 or more `next` notifications
- Can emit: 0 or 1 `error` notification (terminal — no more emissions)
- Can emit: 0 or 1 `complete` notification (terminal)
- After error or complete: no more emissions

```typescript
observable$.subscribe({
  next:     (value) => console.log('Next:', value),
  error:    (err)   => console.error('Error:', err),    // terminal
  complete: ()      => console.log('Complete')          // terminal
});
```

## Converting Promises to Observables and vice versa
```typescript
// Promise → Observable
from(fetch('/api/data').then(r => r.json()));

// Observable → Promise (completes after first emission)
const value = await firstValueFrom(observable$);
const value = await lastValueFrom(observable$);

// Avoid: observable$.toPromise() — deprecated
```

## Common Mistakes
1. **Subscribing to an HttpClient Observable twice:** two HTTP requests. Use `shareReplay(1)` if multiple consumers need the same data.
2. **Forgetting that cold Observables are lazy:** no code runs until subscribe() is called.
3. **Using `subscribe()` inside `subscribe()`:** nesting subscriptions causes memory leaks and missed cancellation.
""",
"mcqs": [
  {"id":"d72q1","prompt":"What is a cold Observable?","options":["An Observable that never emits","An Observable that creates its producer independently for each subscriber — each subscriber gets their own execution. HttpClient.get() is cold: each subscribe() makes a new HTTP request","Cold means synchronous","Observables created with of()"],"correctAnswer":"An Observable that creates its producer independently for each subscriber — each subscriber gets their own execution. HttpClient.get() is cold: each subscribe() makes a new HTTP request","explanation":"Cold: the Observable wraps a resource creation. subscribe() triggers creation. new Observable(obs => { http.get(...).subscribe(obs) }): each subscribe makes a new request. Unsubscribe cancels it. Interval: each subscribe starts its own timer."},
  {"id":"d72q2","prompt":"What is a hot Observable?","options":["An Observable that errors immediately","An Observable with a single shared producer — subscribers join an existing stream and may miss previous emissions. Examples: DOM events, WebSockets, Subject — emitting starts independent of subscription","Hot Observables complete faster","Hot Observables have no error handling"],"correctAnswer":"An Observable with a single shared producer — subscribers join an existing stream and may miss previous emissions. Examples: DOM events, WebSockets, Subject — emitting starts independent of subscription","explanation":"Subject.next(1): both existing subscribers receive 1. A subscriber that joins after the emission misses it (unless BehaviorSubject which replays the last value). document.addEventListener: the click event exists regardless of listeners."},
  {"id":"d72q3","prompt":"What does `shareReplay(1)` do to a cold Observable?","options":["Replays the Observable 1 time","Multicasts the Observable — converts it from cold to hot, sharing one subscription among all consumers. The '1' means buffer the last emission so late subscribers get it immediately","shareReplay increases HTTP requests","Requires a Subject"],"correctAnswer":"Multicasts the Observable — converts it from cold to hot, sharing one subscription among all consumers. The '1' means buffer the last emission so late subscribers get it immediately","explanation":"Without shareReplay: 3 async pipe usages = 3 HTTP requests. With shareReplay(1): 1 HTTP request, all 3 usages share the result. Late subscriber: immediately receives last cached value. Memory: shareReplay keeps a reference until all subscribers unsubscribe."},
  {"id":"d72q4","prompt":"What does `fromEvent(document, 'click')` produce?","options":["A Promise of clicks","An Observable of MouseEvent values — one emission per click. The Observable subscribes to the click event on subscription and removes the listener on unsubscribe","Emits once for the last click","fromEvent only works with input elements"],"correctAnswer":"An Observable of MouseEvent values — one emission per click. The Observable subscribes to the click event on subscription and removes the listener on unsubscribe","explanation":"fromEvent: wraps addEventListener/removeEventListener. Unsubscribe: listener removed. Cold by default but the source (DOM) is hot — multiple fromEvent subscriptions all receive the same DOM events."},
  {"id":"d72q5","prompt":"What is the difference between `share()` and `shareReplay(1)`?","options":["Identical","share(): hot multicast, NO buffer — late subscribers miss past emissions. shareReplay(1): hot multicast WITH buffer — late subscribers immediately receive the last emitted value","share() is deprecated","shareReplay requires count parameter"],"correctAnswer":"share(): hot multicast, NO buffer — late subscribers miss past emissions. shareReplay(1): hot multicast WITH buffer — late subscribers immediately receive the last emitted value","explanation":"HTTP response example: subscribe after response arrives. share(): nothing received (missed the emission). shareReplay(1): cached response immediately delivered. Use shareReplay(1) for data that should be available to any subscriber at any time."},
  {"id":"d72q6","prompt":"What does `firstValueFrom(observable$)` do?","options":["Returns the Observable","Converts an Observable to a Promise that resolves with the first emitted value, then unsubscribes. Replaces the deprecated .toPromise()","Gets the minimum value","Requires the Observable to be cold"],"correctAnswer":"Converts an Observable to a Promise that resolves with the first emitted value, then unsubscribes. Replaces the deprecated .toPromise()","explanation":"firstValueFrom: resolves on first next emission. lastValueFrom: resolves when Observable completes (last value). If Observable errors before emitting: Promise rejects. If Observable completes without emitting: firstValueFrom throws EmptyError (unless defaultValue provided)."},
  {"id":"d72q7","prompt":"What is `EMPTY` in RxJS?","options":["An empty array Observable","An Observable that completes immediately without emitting any values — useful as a fallback in catchError when you want to swallow an error and continue with no data","EMPTY throws an error","EMPTY is the same as null"],"correctAnswer":"An Observable that completes immediately without emitting any values — useful as a fallback in catchError when you want to swallow an error and continue with no data","explanation":"catchError(err => { if (err.status === 404) return EMPTY; ... }): 404 → no value emitted, Observable completes. subscribe's complete callback fires. No error propagated. Use of(defaultValue) to emit a fallback value instead."},
  {"id":"d72q8","prompt":"Why is subscribing to an HttpClient Observable inside another subscribe() problematic?","options":["Syntax error","Creates nested subscriptions that are unmanageable — the inner subscription isn't connected to the outer's lifecycle, can't be cancelled as a unit, and leads to memory leaks. Use switchMap/mergeMap instead","HttpClient prevents nesting","Inner subscriptions run faster"],"correctAnswer":"Creates nested subscriptions that are unmanageable — the inner subscription isn't connected to the outer's lifecycle, can't be cancelled as a unit, and leads to memory leaks. Use switchMap/mergeMap instead","explanation":"WRONG: outer$.subscribe(id => http.get('/api/'+id).subscribe(r => ...)). CORRECT: outer$.pipe(switchMap(id => http.get('/api/'+id))).subscribe(r => ...). Higher-order operators flatten observables properly with lifecycle management."},
  {"id":"d72q9","prompt":"What does `interval(1000)` produce?","options":["Delays 1 second then completes","An infinite Observable emitting 0, 1, 2... every 1000 milliseconds — never completes. Each subscription starts an independent timer. Must be cancelled with takeUntil or unsubscribe","interval emits once","interval is hot"],"correctAnswer":"An infinite Observable emitting 0, 1, 2... every 1000 milliseconds — never completes. Each subscription starts an independent timer. Must be cancelled with takeUntil or unsubscribe","explanation":"interval(1000): cold Observable, new timer per subscription. Emits incrementing integers. Use takeUntil(destroy$) to stop. timer(0, 1000): same but starts immediately (0ms delay for first emission). Common use: polling, countdown timers."},
  {"id":"d72q10","prompt":"What is the Observable contract regarding error and complete notifications?","options":["Both can fire multiple times","Error and complete are TERMINAL — once either fires, the Observable emits no more values. They are mutually exclusive: an Observable that errors doesn't complete normally, and a completed Observable can't error","Both are optional","complete must always fire"],"correctAnswer":"Error and complete are TERMINAL — once either fires, the Observable emits no more values. They are mutually exclusive: an Observable that errors doesn't complete normally, and a completed Observable can't error","explanation":"Contract: zero or more next() → zero or one error() OR complete() (never both). HttpClient get: next(body) → complete(). Failed request: error(HttpErrorResponse). After error/complete: no more emissions even if the producer still runs."}
],
"writtenConceptQuestions": [
  "Explain cold vs hot Observables with concrete examples. Show HttpClient being cold and Subject being hot.",
  "Show shareReplay(1) converting a cold HTTP Observable to one shared by multiple component subscribers.",
  "Show all major creation operators: of, from, interval, timer, fromEvent, EMPTY with their use cases.",
  "Show converting an Observable to a Promise with firstValueFrom. When would this be appropriate?",
  "Explain the Observable contract: next, error, complete. Show subscribing with all three handlers.",
  "Why are nested subscribe() calls problematic? Show the fix using switchMap.",
  "Compare share() and shareReplay(1). When does the difference matter?"
],
"businessScenarios": [
  "A product catalog is loaded by both ProductListComponent and ProductSearchComponent — two HTTP requests are made. Add shareReplay(1) to the service so both components share one request.",
  "A dashboard polls an API every 30 seconds. Use interval(30000) with takeUntil(destroy$) to auto-cancel on component destroy.",
  "An order status page needs to react to WebSocket messages. Wrap the WebSocket connection in a fromEvent-equivalent Observable using new Observable(observer => { ws.onmessage = m => observer.next(m) })."
]
},

"day-073": {
"notes": """# Angular Subjects: BehaviorSubject, ReplaySubject, and State Management

## Subject — The Basic Multicast
```typescript
// Subject is both Observable AND Observer
const subject = new Subject<string>();

// Subscribe first, then emit
subject.subscribe(v => console.log('A:', v));
subject.subscribe(v => console.log('B:', v));

subject.next('Hello');   // A: Hello, B: Hello
subject.next('World');   // A: World, B: World

// Late subscriber misses past emissions
subject.subscribe(v => console.log('C:', v));  // C doesn't get Hello or World
subject.next('Late!');   // A: Late!, B: Late!, C: Late!
```

## BehaviorSubject — Current State + Replay Last Value
```typescript
// Requires an initial value — always has a current value
const currentUser$ = new BehaviorSubject<User | null>(null);

// Subscribe — immediately gets the current value
currentUser$.subscribe(user => console.log('User:', user));  // User: null (immediately)

// Emit a new value
currentUser$.next({ id: '1', name: 'Alice' });  // User: { id:'1', name:'Alice' }

// Access current value synchronously
const user = currentUser$.getValue();  // { id:'1', name:'Alice' }

// Late subscriber gets the LATEST value immediately
setTimeout(() => {
  currentUser$.subscribe(u => console.log('Late:', u));  // Late: { id:'1', ... } immediately
}, 1000);
```

## Using BehaviorSubject for Service State
```typescript
@Injectable({ providedIn: 'root' })
export class CartService {
  // Private BehaviorSubject — only the service can emit
  private cartItems = new BehaviorSubject<CartItem[]>([]);

  // Public Observable — components read but can't emit
  readonly items$ = this.cartItems.asObservable();

  // Derived reactive values
  readonly itemCount$ = this.cartItems.pipe(
    map(items => items.reduce((acc, i) => acc + i.quantity, 0))
  );
  readonly total$ = this.cartItems.pipe(
    map(items => items.reduce((acc, i) => acc + i.price * i.quantity, 0))
  );

  addItem(item: CartItem) {
    const current = this.cartItems.getValue();
    const existing = current.find(i => i.productId === item.productId);
    if (existing) {
      this.cartItems.next(
        current.map(i => i.productId === item.productId
          ? { ...i, quantity: i.quantity + 1 }
          : i
        )
      );
    } else {
      this.cartItems.next([...current, item]);
    }
  }

  removeItem(productId: string) {
    this.cartItems.next(
      this.cartItems.getValue().filter(i => i.productId !== productId)
    );
  }
}
```

## ReplaySubject — Buffer and Replay Past Values
```typescript
// ReplaySubject(n) — keeps last n emissions, replays to new subscribers
const replay$ = new ReplaySubject<string>(3);  // buffer last 3

replay$.next('a');
replay$.next('b');
replay$.next('c');
replay$.next('d');  // 'd' pushes 'a' out of buffer

// Late subscriber gets last 3: b, c, d
replay$.subscribe(v => console.log(v));  // b, c, d, then live updates

// ReplaySubject with time window
const timed$ = new ReplaySubject<Event>(100, 5000);  // up to 100 events from last 5 seconds
```

## AsyncSubject — Last Value Before Complete
```typescript
const async$ = new AsyncSubject<number>();
async$.next(1);
async$.next(2);
async$.next(3);
// No emissions to subscribers yet...

async$.complete();  // Now all subscribers receive only: 3 (last value)
async$.subscribe(v => console.log(v));  // 3 (immediately, gets last value before complete)
```

## Signals vs BehaviorSubject (Angular 16+)
```typescript
// BehaviorSubject
private cartItems = new BehaviorSubject<CartItem[]>([]);
readonly items$ = this.cartItems.asObservable();
// Template: <div *ngFor="let item of items$ | async">

// Signal (Angular 16+) — simpler for component state
private cartItems = signal<CartItem[]>([]);
readonly items = this.cartItems.asReadonly();
// Template: @for (item of items(); track item.id)

// Signals: simpler syntax, no async pipe, works with OnPush automatically
// BehaviorSubject: integrates with RxJS operators (pipe, map, combineLatest)
```

## Common Mistakes
1. **Exposing BehaviorSubject directly:** `public items = new BehaviorSubject(...)` lets any code call `.next()`. Always expose `.asObservable()`.
2. **Forgetting to complete Subjects on service destroy:** for component-level services, call `subject.complete()` in ngOnDestroy.
3. **Using Subject when BehaviorSubject is needed:** if a component subscribes after the initial data is set, it misses it with a plain Subject.
""",
"mcqs": [
  {"id":"d73q1","prompt":"What is the key difference between Subject and BehaviorSubject?","options":["BehaviorSubject is faster","BehaviorSubject requires an initial value and replays the LAST emitted value to any new subscriber immediately. Subject: new subscribers only get future emissions","Subject doesn't support multicasting","BehaviorSubject is for HTTP only"],"correctAnswer":"BehaviorSubject requires an initial value and replays the LAST emitted value to any new subscriber immediately. Subject: new subscribers only get future emissions","explanation":"Subject: subscribe after .next('hello') → miss 'hello'. BehaviorSubject: subscribe after .next('hello') → immediately receive 'hello' (the current value). Use BehaviorSubject for current state (logged-in user, cart items). Use Subject for events."},
  {"id":"d73q2","prompt":"Why should you expose `.asObservable()` instead of the BehaviorSubject itself?","options":["asObservable is required","Encapsulation: exposing BehaviorSubject gives consumers the ability to call .next() and mutate state from outside the service. asObservable() returns a read-only Observable — only the service can push values","asObservable adds operators","BehaviorSubject can't be subscribed directly"],"correctAnswer":"Encapsulation: exposing BehaviorSubject gives consumers the ability to call .next() and mutate state from outside the service. asObservable() returns a read-only Observable — only the service can push values","explanation":"public items = new BehaviorSubject([]) → any component can call items.next([]) and corrupt state. public items$ = this.items.asObservable() → read-only. Only CartService.addItem() can mutate through private BehaviorSubject."},
  {"id":"d73q3","prompt":"What does `BehaviorSubject.getValue()` return?","options":["An Observable","The current synchronous value — doesn't require a subscription. Useful when you need the current state inside a method without subscribing","getValue() returns an array","Throws if not subscribed"],"correctAnswer":"The current synchronous value — doesn't require a subscription. Useful when you need the current state inside a method without subscribing","explanation":"In addItem(): this.cartItems.getValue() — reads current array synchronously. Then push new item and call next(newArray). This pattern avoids creating a subscription just to read the current value."},
  {"id":"d73q4","prompt":"What is ReplaySubject(3) and when would you use it?","options":["Replays 3 Observables","Buffers the last 3 emissions — any subscriber (including late ones) immediately receives the last 3 values. Use for: activity feeds (last N items), chat history, audit logs","ReplaySubject(3) limits to 3 subscribers","Replays the first 3 values only"],"correctAnswer":"Buffers the last 3 emissions — any subscriber (including late ones) immediately receives the last 3 values. Use for: activity feeds (last N items), chat history, audit logs","explanation":"Chat app: new component mount → gets last 10 messages immediately (ReplaySubject(10)). Compared to BehaviorSubject(1) which only gives the last 1. ReplaySubject(Infinity): gives ALL past values — basically a log."},
  {"id":"d73q5","prompt":"What is AsyncSubject and when does it emit?","options":["Emits asynchronously","Emits only the LAST value, and only AFTER the subject calls complete(). Like resolving a Promise — subscribers get the final value. Use for: lazy initialization, caching one-time async results","AsyncSubject emits on every next()","AsyncSubject requires a timer"],"correctAnswer":"Emits only the LAST value, and only AFTER the subject calls complete(). Like resolving a Promise — subscribers get the final value. Use for: lazy initialization, caching one-time async results","explanation":"next(1), next(2), next(3): nothing emitted yet. complete(): 3 emitted to all subscribers. Late subscriber after complete(): immediately gets 3. Like a Promise: resolves with one final value."},
  {"id":"d73q6","prompt":"In CartService, how should you update an immutable BehaviorSubject array?","options":["Push to the array","Use getValue() to get the current array, create a NEW array with the change, and call next() with the new array — never mutate the existing array","Arrays are always mutable","BehaviorSubject detects mutations"],"correctAnswer":"Use getValue() to get the current array, create a NEW array with the change, and call next() with the new array — never mutate the existing array","explanation":"Mutation: this.cartItems.getValue().push(item) — reference unchanged, BehaviorSubject emits same reference, OnPush components don't update. Immutable: this.cartItems.next([...this.cartItems.getValue(), item]) — new reference triggers all subscribers and OnPush."},
  {"id":"d73q7","prompt":"What does `subject.asObservable()` return?","options":["A new Subject","A read-only Observable wrapper — cannot call .next(), .error(), or .complete() on it. Provides the observer/consumer API without the producer API","asObservable() creates a new stream","Required for all Subjects"],"correctAnswer":"A read-only Observable wrapper — cannot call .next(), .error(), or .complete() on it. Provides the observer/consumer API without the producer API","explanation":"TypeScript: Observable<T> type has no next/error/complete methods — compile-time safety. Subject<T> has them. Expose Observable<T> from services, keep Subject<T> private. Consumers can only subscribe."},
  {"id":"d73q8","prompt":"When should you choose signals over BehaviorSubject for Angular state management?","options":["Always use signals","Signals: simpler syntax for component/service state (no async pipe, works with OnPush automatically, no boilerplate). BehaviorSubject: when you need to compose with RxJS operators (combineLatest, switchMap, debounce)","BehaviorSubject is deprecated","Signals require Angular 18"],"correctAnswer":"Signals: simpler syntax for component/service state (no async pipe, works with OnPush automatically, no boilerplate). BehaviorSubject: when you need to compose with RxJS operators (combineLatest, switchMap, debounce)","explanation":"Signal: const count = signal(0); count.update(v => v+1); template: {{ count() }}. BehaviorSubject: requires | async or subscribe(). Signals are simpler for most cases. BehaviorSubject shines for complex reactive pipelines with multiple RxJS operators."},
  {"id":"d73q9","prompt":"What happens if you call `subject.complete()` before subscribing?","options":["The subscription waits","For Subject/ReplaySubject: subscriber immediately receives the complete notification (no values). For AsyncSubject: subscriber immediately receives the last value (if any), then complete. For BehaviorSubject: subscriber gets current value, then complete","completed Subjects throw errors","Subscription fails"],"correctAnswer":"For Subject/ReplaySubject: subscriber immediately receives the complete notification (no values). For AsyncSubject: subscriber immediately receives the last value (if any), then complete. For BehaviorSubject: subscriber gets current value, then complete","explanation":"After complete(): new subscriptions immediately execute the complete callback. Further next() calls are ignored. A completed Subject won't emit any new values, even after subscribing."},
  {"id":"d73q10","prompt":"What is the typical pattern to prevent memory leaks with a BehaviorSubject-based service?","options":["BehaviorSubject services don't leak","Using async pipe in templates (auto-unsubscribes) or takeUntil(destroy$) in component subscriptions. If the service is component-scoped (providers:[Service]), call subject.complete() in the service's ngOnDestroy","Use unsubscribe() everywhere","BehaviorSubject auto-completes"],"correctAnswer":"Using async pipe in templates (auto-unsubscribes) or takeUntil(destroy$) in component subscriptions. If the service is component-scoped (providers:[Service]), call subject.complete() in the service's ngOnDestroy","explanation":"Root-scoped service: lives forever → no leak concern. Component-scoped service (providers:[]): destroys with component. Service's ngOnDestroy: this.cartItems.complete() — signals all subscribers that the stream is done."}
],
"writtenConceptQuestions": [
  "Implement a CartService using BehaviorSubject with addItem, removeItem, and derived item count/total observables.",
  "Explain the four Subject types: Subject, BehaviorSubject, ReplaySubject, AsyncSubject. Show when to use each.",
  "Show why exposing asObservable() instead of BehaviorSubject directly is important. Show the TypeScript type difference.",
  "Compare BehaviorSubject with signals for the same cart state. Show both implementations.",
  "Show how to update a BehaviorSubject array immutably. Why does mutation not work with OnPush?",
  "What does getValue() do? Show its use in an addItem method that checks for duplicates.",
  "Show ReplaySubject for a notification feed that gives the last 5 notifications to any new subscriber."
],
"businessScenarios": [
  "A shopping cart needs to be accessible from both HeaderComponent (count badge) and CartPageComponent (full list). Implement CartService with BehaviorSubject, expose asObservable(), and show both components subscribing.",
  "A notification system shows the last 3 alerts to users who navigate to the alerts page after some have been dismissed. Use ReplaySubject(3).",
  "User authentication state (logged in/out) must be immediately available to any component that subscribes, even after login. Use BehaviorSubject<User|null> in AuthService."
]
},

"day-074": {
"notes": """# Angular Guards: CanActivate, CanDeactivate, Resolve, and CanMatch

## Functional Guards (Angular 14+ Recommended)
```typescript
// canActivate — prevent navigation to a route
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) return true;

  // Store return URL for post-login redirect
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};

// canActivateChild — applied to all children of a route
export const adminAreaGuard: CanActivateChildFn = (childRoute, state) => {
  return inject(AuthService).hasRole('ADMIN')
    || inject(Router).createUrlTree(['/forbidden']);
};
```

## Role-Based Guard with Multiple Conditions
```typescript
// Guard factory — creates parameterized guards
export function hasRole(...requiredRoles: string[]): CanActivateFn {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);

    const userRoles = auth.getUserRoles();
    const hasAnyRole = requiredRoles.some(role => userRoles.includes(role));

    if (hasAnyRole) return true;
    return router.createUrlTree(['/forbidden']);
  };
}

// Route config
const routes: Routes = [
  {
    path: 'orders',
    component: OrdersComponent,
    canActivate: [authGuard, hasRole('VIEW_ORDERS', 'ADMIN')]
  },
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes').then(r => r.routes),
    canActivate: [authGuard, hasRole('ADMIN')]
  }
];
```

## CanDeactivate — Unsaved Changes
```typescript
export interface CanDeactivateComponent {
  canDeactivate: () => boolean | Observable<boolean>;
}

export const unsavedChangesGuard: CanDeactivateFn<CanDeactivateComponent> =
  (component) => {
    if (!component.canDeactivate()) {
      return inject(DialogService)
        .confirm('You have unsaved changes. Leave the page?');
      // DialogService returns Observable<boolean>
    }
    return true;
  };

// Component implements the interface
@Component({ standalone: true })
export class OrderEditComponent implements CanDeactivateComponent {
  private form = inject(FormBuilder).group({ ... });

  canDeactivate(): boolean {
    return this.form.pristine;  // true if no changes (allow deactivate)
  }
}

// Route
{ path: ':id/edit', component: OrderEditComponent, canDeactivate: [unsavedChangesGuard] }
```

## Resolve — Pre-fetch Data Before Route Activates
```typescript
// Resolver pre-fetches data — component receives it from route.data
export const orderResolver: ResolveFn<OrderDto> = (route) => {
  const orderService = inject(OrderService);
  const router = inject(Router);
  const id = route.paramMap.get('id')!;

  return orderService.findById(id).pipe(
    catchError(() => {
      router.navigate(['/not-found']);
      return EMPTY;
    })
  );
};

// Route — resolver result available in route.data
{ path: ':id', component: OrderDetailComponent, resolve: { order: orderResolver } }

// Component accesses pre-fetched data
@Component({ standalone: true })
export class OrderDetailComponent {
  private route = inject(ActivatedRoute);
  order = this.route.snapshot.data['order'] as OrderDto;
  // No need for loading state — data is ready when component renders
}
```

## CanMatch — Filter Which Route Loads
```typescript
// canMatch — applied before route matching — for feature flags / AB testing
export const betaFeatureGuard: CanMatchFn = () => {
  return inject(FeatureFlagService).isEnabled('BETA_ORDERS');
};

// If betaFeatureGuard returns false, this route is SKIPPED — next matching route evaluated
const routes: Routes = [
  { path: 'orders', component: BetaOrdersComponent, canMatch: [betaFeatureGuard] },
  { path: 'orders', component: OrdersComponent }  // fallback
];
```

## Common Mistakes
1. **Using class-based guards in new code:** Angular recommends functional guards for their simplicity and inject() support.
2. **Resolver not handling errors:** if the resolver Observable errors, navigation fails silently. Always add catchError.
3. **Using CanActivate when CanMatch is needed:** CanActivate still matches the route (just blocks navigation); CanMatch skips the route entirely, enabling fallback routes.
""",
"mcqs": [
  {"id":"d74q1","prompt":"What does a CanActivate guard returning a `UrlTree` do?","options":["Creates a new URL","Redirects the user to the URL represented by the UrlTree — the current navigation is cancelled and replaced with navigation to the new URL (e.g., redirect to /login)","UrlTree is only for logging","Returns false"],"correctAnswer":"Redirects the user to the URL represented by the UrlTree — the current navigation is cancelled and replaced with navigation to the new URL (e.g., redirect to /login)","explanation":"Guard return values: true (allow), false (block, no navigation), UrlTree (redirect). router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } }): redirect to login preserving the original destination."},
  {"id":"d74q2","prompt":"What is the difference between CanActivate and CanMatch?","options":["Identical","CanActivate: route is matched, guard decides whether navigation is allowed. CanMatch: evaluated BEFORE matching — if it returns false, the route is completely skipped and the router tries the next matching route","CanMatch is deprecated","CanActivate applies to children"],"correctAnswer":"CanActivate: route is matched, guard decides whether navigation is allowed. CanMatch: evaluated BEFORE matching — if it returns false, the route is completely skipped and the router tries the next matching route","explanation":"CanActivate false: navigation blocked, user stays or redirects. CanMatch false: route skipped, next route with same path evaluated. Use CanMatch for feature flags: A/B testing between BetaComponent and StableComponent on same path."},
  {"id":"d74q3","prompt":"What does a Resolve guard do?","options":["Guards navigation","Pre-fetches data before the route component activates — the component receives pre-loaded data via route.snapshot.data, eliminating loading state in the component","Resolve handles 404 errors","Replaces ngOnInit"],"correctAnswer":"Pre-fetches data before the route component activates — the component receives pre-loaded data via route.snapshot.data, eliminating loading state in the component","explanation":"Without resolver: component navigates, renders in loading state, makes HTTP call, shows data. With resolver: navigation waits for HTTP call to complete, component renders with data already available. Better UX: no loading spinner in the component."},
  {"id":"d74q4","prompt":"What does CanDeactivate guard protect?","options":["Prevents route activation","Navigation AWAY from the current route — used to warn users about unsaved changes. Returns true (allow leave), false (block leave), or Observable<boolean> (show async dialog)","Deactivates the component","Clears component state"],"correctAnswer":"Navigation AWAY from the current route — used to warn users about unsaved changes. Returns true (allow leave), false (block leave), or Observable<boolean> (show async dialog)","explanation":"component.hasUnsavedChanges(): true → guard shows confirm dialog → Observable<boolean>. User confirms → true → navigation proceeds. User cancels → false → stays on current page. Critical for forms with unsaved data."},
  {"id":"d74q5","prompt":"What is a guard factory function (like `hasRole(...roles)`) and why is it useful?","options":["A factory that creates services","A function that returns a CanActivateFn — allows parameterizing guards: hasRole('ADMIN') and hasRole('USER', 'EDITOR') reuse the same guard logic with different parameters","Factory functions replace providers","Required for async guards"],"correctAnswer":"A function that returns a CanActivateFn — allows parameterizing guards: hasRole('ADMIN') and hasRole('USER', 'EDITOR') reuse the same guard logic with different parameters","explanation":"canActivate: [hasRole('ADMIN')] calls the factory which returns the actual guard function. The factory closes over the role parameter. Avoids copy-pasting guard logic for each role combination."},
  {"id":"d74q6","prompt":"Why should a resolver's Observable not error without handling?","options":["Resolvers don't support errors","If the resolver Observable errors, the navigation is cancelled and the component never renders — and the error is NOT automatically shown to the user. Always add catchError to redirect or show an error page","Errors are auto-caught","Use try/catch in resolver"],"correctAnswer":"If the resolver Observable errors, the navigation is cancelled and the component never renders — and the error is NOT automatically shown to the user. Always add catchError to redirect or show an error page","explanation":"catchError(() => { router.navigate(['/not-found']); return EMPTY; }): on error, redirect to 404 page. Without catchError: silent navigation failure — user sees nothing. EMPTY: completes the resolver observable cleanly after redirect."},
  {"id":"d74q7","prompt":"What is `canActivateChild` and how does it differ from applying canActivate to each child?","options":["Guards the parent route","Applied to a parent route, guards ALL child route navigations — avoids repeating the guard on every child route definition. Equivalent to adding canActivate to each child","canActivateChild is for lazy routes","Same as canActivate on the parent"],"correctAnswer":"Applied to a parent route, guards ALL child route navigations — avoids repeating the guard on every child route definition. Equivalent to adding canActivate to each child","explanation":"{ path: 'admin', canActivateChild: [authGuard], children: [...] }: authGuard runs for every navigation to admin/* without adding it to each child. canActivate on parent: only guards direct navigation to /admin, not children."},
  {"id":"d74q8","prompt":"How does an Angular route component access data provided by a resolver?","options":["Via @Input","Via ActivatedRoute.snapshot.data['key'] or route.data Observable — the resolved value is available as the 'key' you specified in the route config's resolve property","Resolver injects into constructor","Via @Resolve decorator"],"correctAnswer":"Via ActivatedRoute.snapshot.data['key'] or route.data Observable — the resolved value is available as the 'key' you specified in the route config's resolve property","explanation":"Route: resolve: { order: orderResolver }. Component: this.route.snapshot.data['order'] as OrderDto. For param changes that don't recreate component: this.route.data.subscribe(data => this.order = data['order'])."},
  {"id":"d74q9","prompt":"What should a CanDeactivate guard return to show an async confirmation dialog?","options":["A boolean","An Observable<boolean> — the dialog emits true (leave) or false (stay). Angular waits for the Observable to complete before proceeding with or cancelling navigation","A Promise<boolean>","A UrlTree"],"correctAnswer":"An Observable<boolean> — the dialog emits true (leave) or false (stay). Angular waits for the Observable to complete before proceeding with or cancelling navigation","explanation":"DialogService.confirm() returns Observable<boolean>. CanDeactivateFn returns this Observable. Angular subscribes and waits. User clicks 'Yes' → Observable emits true → navigation proceeds. 'No' → false → stays. Both Observables and Promises work."},
  {"id":"d74q10","prompt":"In functional guards, how do you access Angular services like AuthService?","options":["Pass them as parameters","Use `inject(AuthService)` inside the guard function body — functional guards run in an injection context, so inject() works without constructor injection","Services are not available in guards","Use global variables"],"correctAnswer":"Use `inject(AuthService)` inside the guard function body — functional guards run in an injection context, so inject() works without constructor injection","explanation":"Functional guard: export const authGuard: CanActivateFn = (route, state) => { const auth = inject(AuthService); ... }. inject() works because Angular calls guards in an injection context. Cleaner than class-based guards which need constructor injection."}
],
"writtenConceptQuestions": [
  "Write an authGuard and a hasRole() guard factory. Show their composition on a route.",
  "Implement a CanDeactivate guard with a dialog service Observable for an order edit form.",
  "Write an orderResolver that pre-fetches order data and redirects to /not-found on 404.",
  "Explain CanActivate vs CanMatch. Show CanMatch for A/B testing between two route versions.",
  "Show canActivateChild on an admin route to protect all children with one guard.",
  "Explain how a component accesses resolved data. Show route.snapshot.data vs route.data Observable.",
  "Show a guard that reads a query parameter from the route and validates it before allowing access."
],
"businessScenarios": [
  "Clicking the Back button mid-checkout with filled form data loses all progress. Add CanDeactivate to the checkout form component.",
  "An order detail page shows a loading spinner, then the order content. Eliminate the spinner using a Resolve guard that pre-fetches the order.",
  "A feature flag controls whether users see the new beta order management UI or the old one. Use CanMatch to serve BetaOrdersComponent to beta users and OrdersComponent to others."
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
