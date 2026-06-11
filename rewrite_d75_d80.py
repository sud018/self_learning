"""Rewrite days 75-80: Interceptors, Authentication, State Management, Performance, Lazy Loading, Testing."""
import json, os
DATA_DIR = "backend/data/curriculum"

CURRICULUM = {

"day-075": {
"notes": """# Angular Interceptors: Advanced Patterns and Token Refresh

## Functional Interceptor Patterns
```typescript
// token-refresh.interceptor.ts
// Automatically refresh expired JWT and retry the original request
export const tokenRefreshInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status !== 401 || req.url.includes('/auth/refresh')) {
        return throwError(() => error);  // not a token issue, re-throw
      }

      // Token expired — refresh then retry
      return auth.refreshToken().pipe(
        switchMap(token => {
          // Clone with new token and retry
          return next(req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }));
        }),
        catchError(refreshError => {
          auth.logout();
          inject(Router).navigate(['/login']);
          return throwError(() => refreshError);
        })
      );
    })
  );
};
```

## Request Deduplication Interceptor
```typescript
// cache.interceptor.ts — cache GET requests for 30 seconds
export const cacheInterceptor: HttpInterceptorFn = (req, next) => {
  const cache = inject(HttpCacheService);

  if (req.method !== 'GET') return next(req);  // only cache GETs

  const cached = cache.get(req.url);
  if (cached) return of(cached);               // serve from cache

  return next(req).pipe(
    tap(response => cache.set(req.url, response, 30_000))  // cache 30s
  );
};
```

## Request Correlation ID and Tracing
```typescript
// correlation.interceptor.ts — add X-Request-Id to every request
export const correlationInterceptor: HttpInterceptorFn = (req, next) => {
  const requestId = crypto.randomUUID();
  return next(req.clone({
    setHeaders: {
      'X-Request-Id': requestId,
      'X-Correlation-Id': inject(TraceService).getTraceId()
    }
  })).pipe(
    tap({ error: err => console.error(`[${requestId}] HTTP Error:`, err) })
  );
};
```

## Using HttpContextToken for Per-Request Configuration
```typescript
// Define tokens
export const CACHE_TTL    = new HttpContextToken<number>(() => 0);    // 0 = no cache
export const RETRY_COUNT  = new HttpContextToken<number>(() => 0);    // 0 = no retry
export const SKIP_LOADING = new HttpContextToken<boolean>(() => false);

// Smart loading interceptor — respects SKIP_LOADING token
export const loadingInterceptor: HttpInterceptorFn = (req, next) => {
  if (req.context.get(SKIP_LOADING)) return next(req);

  const loading = inject(LoadingService);
  loading.show();
  return next(req).pipe(finalize(() => loading.hide()));
};

// Service uses context tokens for fine-grained control
this.http.get('/api/products/autocomplete', {
  context: new HttpContext()
    .set(SKIP_LOADING, true)      // don't show global loader for autocomplete
    .set(CACHE_TTL, 60_000)       // cache for 1 minute
    .set(RETRY_COUNT, 2)          // retry up to 2 times
});
```

## Interceptor Order and Composition
```typescript
// provideHttpClient — interceptor chain
export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([
        correlationInterceptor,  // 1st: add trace headers
        authInterceptor,         // 2nd: add auth token
        tokenRefreshInterceptor, // 3rd: handle 401 + refresh
        loadingInterceptor,      // 4th: show/hide loader
        cacheInterceptor,        // 5th: serve from cache if available
      ])
    )
  ]
};
// Request chain:  correlation → auth → tokenRefresh → loading → cache → HttpBackend
// Response chain: cache → loading → tokenRefresh → auth → correlation
```

## Testing Interceptors
```typescript
describe('authInterceptor', () => {
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClientTesting(),
        provideHttpClient(withInterceptors([authInterceptor])),
        { provide: AuthService, useValue: { getToken: () => 'test-token' } }
      ]
    });
    httpTesting = TestBed.inject(HttpTestingController);
  });

  it('should add Authorization header', () => {
    inject([HttpClient], (http: HttpClient) => {
      http.get('/api/orders').subscribe();
      const req = httpTesting.expectOne('/api/orders');
      expect(req.request.headers.get('Authorization')).toBe('Bearer test-token');
    });
  });
});
```

## Common Mistakes
1. **Infinite retry loop on 401:** token refresh interceptor must check `req.url.includes('/auth/refresh')` to avoid retrying the refresh request itself.
2. **Race condition on concurrent 401s:** multiple requests expiring at the same time each trigger a token refresh. Use `shareReplay(1)` on the refresh Observable.
""",
"mcqs": [
  {"id":"d75q1","prompt":"What is the token refresh pattern in Angular HTTP interceptors?","options":["Refresh tokens before every request","Catch a 401 error, call the refresh endpoint to get a new token, then retry the ORIGINAL request with the new token — transparent re-authentication without user interaction","Token refresh requires logout","Only works with OAuth"],"correctAnswer":"Catch a 401 error, call the refresh endpoint to get a new token, then retry the ORIGINAL request with the new token — transparent re-authentication without user interaction","explanation":"Flow: request → 401 → refreshToken() → new token → clone original request with new token → retry. User experience: seamless. Without this: every token expiry shows login page, even mid-workflow."},
  {"id":"d75q2","prompt":"Why must the token refresh interceptor check if the failing request is the refresh endpoint itself?","options":["Performance optimization","Prevents infinite loop: if the refresh request returns 401 (expired refresh token), the interceptor would try to refresh again, causing infinite recursion","Refresh endpoint is different","Required for all interceptors"],"correctAnswer":"Prevents infinite loop: if the refresh request returns 401 (expired refresh token), the interceptor would try to refresh again, causing infinite recursion","explanation":"if (error.status !== 401 || req.url.includes('/auth/refresh')) return throwError(error): if the failing request IS the refresh endpoint, give up and logout instead of trying to refresh again."},
  {"id":"d75q3","prompt":"What is the race condition problem when multiple requests get 401 simultaneously?","options":["All requests fail","Multiple requests expire at the same time → each triggers its own refresh → multiple parallel refresh calls → token rotation issues. Fix: share the refresh Observable with shareReplay(1)","Only one request can fail","401 is handled sequentially"],"correctAnswer":"Multiple requests expire at the same time → each triggers its own refresh → multiple parallel refresh calls → token rotation issues. Fix: share the refresh Observable with shareReplay(1)","explanation":"3 concurrent requests all 401 → 3 refreshToken() calls. With refresh token rotation: each refresh invalidates the previous token → second and third refresh fail. Fix: private refresh$ = this.refreshToken().pipe(shareReplay(1)) — all 401 responses share one refresh operation."},
  {"id":"d75q4","prompt":"What does the cache interceptor with `of(cached)` achieve?","options":["Creates an in-memory database","Returns the cached HttpResponse as an Observable without making a network request — the component sees an identical Observable regardless of whether data came from cache or network","of() is not an HTTP response","Cache interceptors require IndexedDB"],"correctAnswer":"Returns the cached HttpResponse as an Observable without making a network request — the component sees an identical Observable regardless of whether data came from cache or network","explanation":"of(cached): creates an Observable that immediately emits the cached value and completes. The caller's subscribe() handler runs with cached data. No network request, no latency. Cache hit: instant. Cache miss: actual HTTP then store."},
  {"id":"d75q5","prompt":"What is an HttpContextToken and what problem does it solve?","options":["A custom HTTP header","A typed metadata carrier attached to a specific HTTP request — allows per-request configuration to reach interceptors without changing service method signatures","Context tokens are for authentication","Same as HttpParams"],"correctAnswer":"A typed metadata carrier attached to a specific HTTP request — allows per-request configuration to reach interceptors without changing service method signatures","explanation":"Without context tokens: interceptors can't distinguish between requests that should and shouldn't be cached/loaded/retried. With SKIP_LOADING token: a specific request can tell the loading interceptor not to show the spinner."},
  {"id":"d75q6","prompt":"In what order do multiple interceptors process responses?","options":["Same as requests","Reverse order of registration — the last-registered interceptor's pipe operators handle the response first (closest to HttpBackend), unwinding back to the first interceptor. Like a stack.","Parallel processing","Alphabetical order"],"correctAnswer":"Reverse order of registration — the last-registered interceptor's pipe operators handle the response first (closest to HttpBackend), unwinding back to the first interceptor. Like a stack.","explanation":"withInterceptors([A, B, C]): request A→B→C→server; response C→B→A. C is closest to the actual HTTP backend. Think of it as middleware: request flows inward, response flows outward."},
  {"id":"d75q7","prompt":"What does `provideHttpClientTesting()` provide for testing interceptors?","options":["A mock HttpClient","HttpTestingController: allows intercepting HTTP requests in tests, verifying request headers/methods/URLs, and controlling responses — without making real HTTP calls","Provides a test database","Replaces TestBed"],"correctAnswer":"HttpTestingController: allows intercepting HTTP requests in tests, verifying request headers/methods/URLs, and controlling responses — without making real HTTP calls","explanation":"httpTesting.expectOne('/api/orders'): asserts one request was made to that URL. req.flush({ data: [] }): provide the fake response. afterEach: httpTesting.verify() — ensures no unexpected requests. Deterministic HTTP testing."},
  {"id":"d75q8","prompt":"What is `req.clone()` and why is it needed?","options":["Creates a backup request","Creates a new HttpRequest with specified modifications while keeping other properties — HttpRequest is immutable, so modifications require cloning. req.clone({ setHeaders: { Authorization: 'Bearer token' } })","clone() makes a deep copy","Clone is optional for GET requests"],"correctAnswer":"Creates a new HttpRequest with specified modifications while keeping other properties — HttpRequest is immutable, so modifications require cloning. req.clone({ setHeaders: { Authorization: 'Bearer token' } })","explanation":"HttpRequest immutability: prevents one interceptor's modifications from unexpectedly affecting others. clone({ setHeaders }): keeps everything (url, method, body, params) but adds/replaces the specified headers."},
  {"id":"d75q9","prompt":"What does `finalize(() => loading.hide())` ensure in a loading interceptor?","options":["Loads data at the end","loading.hide() is called whether the request succeeds OR fails — prevents a stuck loading spinner when an HTTP error occurs","finalize runs before the response","finalize requires a timer"],"correctAnswer":"loading.hide() is called whether the request succeeds OR fails — prevents a stuck loading spinner when an HTTP error occurs","explanation":"Without finalize: error → catchError → loading.hide() only if you remember. With finalize: always runs on complete OR error — like a try/finally. Prevents UI stuck in loading state."},
  {"id":"d75q10","prompt":"What is the X-Request-Id header pattern in interceptors used for?","options":["Authentication","Distributed tracing — a unique ID added to every request. When a request fails, the ID appears in both browser logs and server logs, enabling correlation of client errors to specific server-side log entries","X-Request-Id is required","Used only with CORS"],"correctAnswer":"Distributed tracing — a unique ID added to every request. When a request fails, the ID appears in both browser logs and server logs, enabling correlation of client errors to specific server-side log entries","explanation":"Production incident: user reports error 'EX-2847'. Developer searches server logs for that Request-Id → finds the exact failed request, all log context, input data. Without correlation IDs, matching client errors to server logs is impossible in high-traffic systems."}
],
"writtenConceptQuestions": [
  "Implement a complete token refresh interceptor that handles 401 errors, refreshes the token, and retries the original request.",
  "Show the race condition problem with concurrent 401s and fix it using shareReplay(1) on the refresh Observable.",
  "Design a cache interceptor using HttpContextToken for TTL configuration. Show a service setting CACHE_TTL on specific requests.",
  "Show the interceptor execution order for request and response phases with withInterceptors([A, B, C]).",
  "Write a correlation ID interceptor that adds X-Request-Id to every request and logs errors with the ID.",
  "Show how to test an interceptor using provideHttpClientTesting() and HttpTestingController.",
  "Implement a loading interceptor that respects SKIP_LOADING context token for autocomplete endpoints."
],
"businessScenarios": [
  "Access tokens expire every 15 minutes. Users get logged out mid-session. Add a transparent token refresh interceptor so sessions persist without manual re-login.",
  "Product autocomplete endpoint is called on every keystroke, slowing the UI. Add a cache interceptor with 30-second TTL for GET requests.",
  "Support team can't correlate browser errors to server logs. Add a correlation interceptor generating X-Request-Id for every request."
]
},

"day-076": {
"notes": """# Angular Authentication: JWT Integration, Auth Service, and Route Protection

## Authentication Flow
```
User submits login form
  → POST /api/auth/login { username, password }
  → Server returns { accessToken, refreshToken, user }
  → Store tokens (memory + secure cookie or localStorage)
  → Set user state in AuthService (BehaviorSubject)
  → Redirect to intended route
  → Every request: interceptor adds Authorization: Bearer <accessToken>
  → On 401: interceptor refreshes token transparently
  → On logout: clear tokens, clear user state, redirect to login
```

## Auth Service Implementation
```typescript
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly TOKEN_KEY   = 'access_token';
  private readonly REFRESH_KEY = 'refresh_token';
  private http   = inject(HttpClient);
  private router = inject(Router);

  // BehaviorSubject — all components react to auth state changes
  private currentUser = new BehaviorSubject<UserDto | null>(this.getUserFromToken());
  readonly currentUser$  = this.currentUser.asObservable();
  readonly isLoggedIn$   = this.currentUser$.pipe(map(u => u !== null));

  login(credentials: LoginRequest): Observable<void> {
    return this.http.post<AuthResponse>('/api/auth/login', credentials).pipe(
      tap(response => {
        localStorage.setItem(this.TOKEN_KEY, response.accessToken);
        localStorage.setItem(this.REFRESH_KEY, response.refreshToken);
        this.currentUser.next(response.user);
      }),
      map(() => void 0)
    );
  }

  logout() {
    this.http.post('/api/auth/logout', {}).subscribe();  // invalidate server-side
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
    this.currentUser.next(null);
    this.router.navigate(['/login']);
  }

  refreshToken(): Observable<string> {
    const refresh = localStorage.getItem(this.REFRESH_KEY);
    return this.http.post<{ accessToken: string }>('/api/auth/refresh', { refreshToken: refresh })
      .pipe(
        tap(res => localStorage.setItem(this.TOKEN_KEY, res.accessToken)),
        map(res => res.accessToken)
      );
  }

  getToken(): string | null { return localStorage.getItem(this.TOKEN_KEY); }

  hasRole(role: string): boolean {
    const user = this.currentUser.getValue();
    return user?.roles?.includes(role) ?? false;
  }

  isAuthenticated(): boolean { return !!this.getToken() && !this.isTokenExpired(); }

  private isTokenExpired(): boolean {
    const token = this.getToken();
    if (!token) return true;
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  }

  private getUserFromToken(): UserDto | null {
    const token = this.getToken();
    if (!token) return null;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.user ?? null;
    } catch { return null; }
  }
}
```

## Login Component
```typescript
@Component({
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <input formControlName="username" placeholder="Username" />
      <input formControlName="password" type="password" placeholder="Password" />
      <div *ngIf="errorMessage" class="error">{{ errorMessage }}</div>
      <button [disabled]="form.invalid || isLoading">
        {{ isLoading ? 'Logging in...' : 'Login' }}
      </button>
    </form>
  `
})
export class LoginComponent {
  private auth   = inject(AuthService);
  private router = inject(Router);
  private route  = inject(ActivatedRoute);

  form = inject(FormBuilder).group({
    username: ['', Validators.required],
    password: ['', [Validators.required, Validators.minLength(8)]]
  });
  isLoading  = false;
  errorMessage = '';

  onSubmit() {
    if (this.form.invalid) return;
    this.isLoading = true;
    this.errorMessage = '';

    this.auth.login(this.form.value as LoginRequest).subscribe({
      next: () => {
        const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl') ?? '/dashboard';
        this.router.navigateByUrl(returnUrl);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.status === 401 ? 'Invalid credentials' : 'Login failed';
      }
    });
  }
}
```

## JWT Security Considerations
```typescript
// Token storage security:
// localStorage: XSS vulnerable (accessible by any script)
// sessionStorage: cleared on tab close
// httpOnly cookies: XSS-safe (server sets, JS can't read) — recommended for production
// Memory (signal/variable): lost on page refresh

// JWT payload decoding (NOT verification — done server-side)
function decodeJwtPayload(token: string): JwtPayload {
  const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
  return JSON.parse(atob(base64));
}

// Never trust JWT claims for authorization in client — only for UX
// Real authorization: always server-side
```

## Auth Guard with Return URL
```typescript
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) return true;

  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};
```

## Common Mistakes
1. **Trusting JWT payload for authorization:** client can manipulate base64 decoded payload. Authorization must be server-side.
2. **Storing tokens in localStorage in high-security apps:** XSS can steal tokens. Use httpOnly cookies for sensitive data.
3. **Not initializing auth state on app startup:** `getUserFromToken()` in BehaviorSubject init restores state after page refresh.
""",
"mcqs": [
  {"id":"d76q1","prompt":"Why must JWT authorization always be verified server-side, not just client-side?","options":["Server is faster","The client can manipulate the JWT payload (it's just base64, not encrypted). Client-side claims are for UX only. Real access control: server validates signature and checks permissions","JWTs are encrypted","Angular guards are sufficient"],"correctAnswer":"The client can manipulate the JWT payload (it's just base64, not encrypted). Client-side claims are for UX only. Real access control: server validates signature and checks permissions","explanation":"JWT.decode(token): just base64 decode, no signature verification. Anyone can change payload.roles = ['ADMIN']. Server-side: verifies HMAC/RSA signature — if payload is tampered, signature mismatch → 403. Angular guards are UX, not security."},
  {"id":"d76q2","prompt":"Why is token storage in httpOnly cookies more secure than localStorage?","options":["Cookies are faster","httpOnly cookies are inaccessible to JavaScript — XSS attacks can't steal them. localStorage is readable by any script on the page — a single XSS vulnerability exposes all tokens","localStorage requires HTTPS","Cookies are encrypted"],"correctAnswer":"httpOnly cookies are inaccessible to JavaScript — XSS attacks can't steal them. localStorage is readable by any script on the page — a single XSS vulnerability exposes any stored tokens","explanation":"XSS: malicious script injected via user input/CDN/third-party. document.cookie: httpOnly cookies not accessible. localStorage.getItem('access_token'): accessible. httpOnly + Secure + SameSite=Strict: CSRF and XSS resistant."},
  {"id":"d76q3","prompt":"How does Angular auth state persist across page refreshes?","options":["Angular remembers state","By initializing the BehaviorSubject with the result of parsing the stored JWT on service construction — getUserFromToken() reads localStorage on startup and populates initial auth state","Angular state is ephemeral","Use sessionStorage"],"correctAnswer":"By initializing the BehaviorSubject with the result of parsing the stored JWT on service construction — getUserFromToken() reads localStorage on startup and populates initial auth state","explanation":"new BehaviorSubject<User|null>(this.getUserFromToken()): on app start, reads JWT from storage, decodes user payload, sets as initial value. All components subscribing to currentUser$ see the logged-in user immediately."},
  {"id":"d76q4","prompt":"What does the login component store as a `returnUrl` query parameter?","options":["The previous URL","The URL the user was trying to access before being redirected to login — after successful login, the user is sent to returnUrl instead of the default dashboard","returnUrl is the login URL","returnUrl is optional in all cases"],"correctAnswer":"The URL the user was trying to access before being redirected to login — after successful login, the user is sent to returnUrl instead of the default dashboard","explanation":"Guard: router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } }). Login component: this.route.snapshot.queryParamMap.get('returnUrl'). After login success: router.navigateByUrl(returnUrl ?? '/dashboard'). UX: seamless continuation."},
  {"id":"d76q5","prompt":"What does `isTokenExpired()` check by parsing the JWT?","options":["Token length","The `exp` (expiration) claim in the JWT payload — exp is a Unix timestamp in seconds. If exp * 1000 < Date.now(): token expired. Prevents making API calls with a known-expired token","Token signature validity","exp is not in the JWT"],"correctAnswer":"The `exp` (expiration) claim in the JWT payload — exp is a Unix timestamp in seconds. If exp * 1000 < Date.now(): token expired. Prevents making API calls with a known-expired token","explanation":"JWT payload: { sub: 'user-id', exp: 1712345678, roles: ['USER'] }. Decode: JSON.parse(atob(token.split('.')[1])). exp * 1000: milliseconds. < Date.now(): expired. Pre-emptive expiry check: refresh before the request fails."},
  {"id":"d76q6","prompt":"What should the Angular logout function do?","options":["Only remove the token","1) Call server logout endpoint (invalidate server-side session), 2) Remove tokens from storage, 3) Clear user BehaviorSubject to null, 4) Navigate to login page","Only navigate to login","Clear only localStorage"],"correctAnswer":"1) Call server logout endpoint (invalidate server-side session), 2) Remove tokens from storage, 3) Clear user BehaviorSubject to null, 4) Navigate to login page","explanation":"Server logout: invalidates refresh token in DB (prevents token reuse after logout). Storage clear: removes local tokens. BehaviorSubject null: all subscribing components update immediately. Navigate: redirect to login. Without server call, stolen refresh token still works until expiry."},
  {"id":"d76q7","prompt":"Why should BehaviorSubject<User|null> be private in AuthService?","options":["TypeScript requirement","Prevents external code from calling .next() and setting arbitrary user state — only AuthService's login/logout methods should control auth state. Expose as asObservable()","BehaviorSubject can't be public","Performance optimization"],"correctAnswer":"Prevents external code from calling .next() and setting arbitrary user state — only AuthService's login/logout methods should control auth state. Expose as asObservable()","explanation":"If public: any component can call authService.currentUser.next({ roles: ['ADMIN'] }) → privilege escalation. Private + asObservable(): read-only for consumers. Only AuthService can emit new user states through its controlled methods."},
  {"id":"d76q8","prompt":"What does the `hasRole()` method in AuthService do?","options":["Checks server permissions","Returns a boolean based on the CURRENT user's roles from the BehaviorSubject — used for conditional UI rendering (show/hide admin buttons). NOT for security — server must also check","hasRole() makes an API call","Roles are in the JWT only"],"correctAnswer":"Returns a boolean based on the CURRENT user's roles from the BehaviorSubject — used for conditional UI rendering (show/hide admin buttons). NOT for security — server must also check","explanation":"this.currentUser.getValue()?.roles?.includes(role): synchronous. Used in templates: *ngIf='authService.hasRole(\"ADMIN\")'. This controls visibility, not access. API endpoint still validates roles server-side."},
  {"id":"d76q9","prompt":"What does `map(() => void 0)` do at the end of the login pipe?","options":["Returns undefined","Transforms the Observable<AuthResponse> to Observable<void> — callers don't need the response body, and void type prevents accidental dependency on the response structure","void 0 is a JavaScript constant","Prevents the login from completing"],"correctAnswer":"Transforms the Observable<AuthResponse> to Observable<void> — callers don't need the response body, and void type prevents accidental dependency on the response structure","explanation":"login(): Observable<void> — clean public API. Internal: stores tokens via tap (side effect). External: caller just knows 'login succeeded' without coupling to the response structure. If AuthResponse changes, callers are unaffected."},
  {"id":"d76q10","prompt":"What is the security risk of not calling the server logout endpoint?","options":["No risk","The refresh token remains valid on the server until its natural expiry — if stolen before logout, an attacker can use it to get new access tokens even after the user has logged out","Server logout is optional","Logout always invalidates all tokens"],"correctAnswer":"The refresh token remains valid on the server until its natural expiry — if stolen before logout, an attacker can use it to get new access tokens even after the user has logged out","explanation":"Refresh token stolen: attacker can request new access tokens indefinitely. Server-side logout: deletes/invalidates the refresh token in the DB. Subsequent refresh attempt: 401 (token not found). Client-only logout: attackers with the old refresh token stay authenticated."}
],
"writtenConceptQuestions": [
  "Implement a complete AuthService with login, logout, refreshToken, isAuthenticated, hasRole, and BehaviorSubject state.",
  "Show the login component flow: form submit → API call → token storage → redirect to returnUrl.",
  "Explain JWT token security: localStorage vs httpOnly cookies vs memory. What are XSS implications?",
  "Show how to restore auth state after page refresh by initializing BehaviorSubject from stored JWT.",
  "What is isTokenExpired()? Show decoding the JWT payload to read the exp claim.",
  "Show the complete authentication flow: guard → login → returnUrl → dashboard.",
  "What security vulnerability exists if you trust Angular route guards alone for authorization?"
],
"businessScenarios": [
  "Users lose their session data when they manually refresh the browser. Fix by initializing AuthService BehaviorSubject from the stored JWT on startup.",
  "After clicking 'Logout', users can still access admin pages if they directly navigate to the URL. Implement both client-side guards and server-side token revocation.",
  "The app stores JWT in localStorage. A third-party analytics script could steal it via XSS. Migrate to httpOnly cookie authentication with CSRF protection."
]
},

"day-077": {
"notes": """# Angular State Management: Signals, NgRx, and Service-Based State

## Service-Based State with Signals (Angular 16+)
```typescript
// Simple, effective state for most applications
@Injectable({ providedIn: 'root' })
export class ProductStateService {
  // Private writable signals
  private _products  = signal<Product[]>([]);
  private _loading   = signal(false);
  private _error     = signal<string | null>(null);
  private _filter    = signal('');

  // Public read-only signals
  readonly products  = this._products.asReadonly();
  readonly loading   = this._loading.asReadonly();
  readonly error     = this._error.asReadonly();

  // Computed derived state
  readonly filteredProducts = computed(() => {
    const term = this._filter().toLowerCase();
    return this._products().filter(p => p.name.toLowerCase().includes(term));
  });
  readonly productCount = computed(() => this.filteredProducts().length);

  constructor(private api: ProductApiService) {}

  loadProducts() {
    this._loading.set(true);
    this._error.set(null);
    this.api.getProducts().subscribe({
      next:  products => { this._products.set(products); this._loading.set(false); },
      error: err      => { this._error.set(err.message);  this._loading.set(false); }
    });
  }

  setFilter(term: string) { this._filter.set(term); }

  addProduct(product: Product) {
    this._products.update(current => [...current, product]);
  }
}
```

## Component Consuming Signals
```html
<!-- Template uses signals like functions -->
@if (state.loading()) {
  <app-spinner />
} @else if (state.error()) {
  <p class="error">{{ state.error() }}</p>
} @else {
  <input [value]="filterTerm()" (input)="state.setFilter($event.target.value)" />
  <p>Showing {{ state.productCount() }} products</p>
  @for (product of state.filteredProducts(); track product.id) {
    <app-product-card [product]="product" />
  }
}
```

## NgRx — Redux Pattern for Complex State
```typescript
// actions.ts
export const loadProducts = createAction('[Products] Load');
export const loadProductsSuccess = createAction('[Products] Load Success',
  props<{ products: Product[] }>());
export const loadProductsFailure = createAction('[Products] Load Failure',
  props<{ error: string }>());

// reducer.ts
interface ProductState { products: Product[]; loading: boolean; error: string | null; }
const initialState: ProductState = { products: [], loading: false, error: null };

export const productReducer = createReducer(
  initialState,
  on(loadProducts, state => ({ ...state, loading: true, error: null })),
  on(loadProductsSuccess, (state, { products }) => ({ ...state, products, loading: false })),
  on(loadProductsFailure, (state, { error }) => ({ ...state, error, loading: false }))
);

// effects.ts
@Injectable()
export class ProductEffects {
  loadProducts$ = createEffect(() =>
    this.actions$.pipe(
      ofType(loadProducts),
      switchMap(() =>
        this.api.getProducts().pipe(
          map(products => loadProductsSuccess({ products })),
          catchError(err => of(loadProductsFailure({ error: err.message })))
        )
      )
    )
  );
  constructor(private actions$: Actions, private api: ProductApiService) {}
}

// selectors.ts
export const selectProducts = createSelector(
  selectProductState,
  state => state.products
);
export const selectLoading = createSelector(
  selectProductState,
  state => state.loading
);
```

## NgRx Component Integration
```typescript
@Component({ standalone: true, imports: [StoreModule] })
export class ProductListComponent {
  private store = inject(Store);

  products$ = this.store.select(selectProducts);
  loading$  = this.store.select(selectLoading);

  ngOnInit() { this.store.dispatch(loadProducts()); }
  deleteProduct(id: string) { this.store.dispatch(deleteProduct({ id })); }
}
```

## When to Use Each Pattern
```
Signal Services      → 80% of apps. Simple, readable, no extra library.
NgRx                 → Large teams, complex async flows, time-travel debugging.
Component Signals    → Local UI state (form open/closed, selected tab).
BehaviorSubject      → When RxJS operators needed (combineLatest, etc).
```

## Common Mistakes
1. **NgRx for simple apps:** massive boilerplate for simple CRUD. Start with signals.
2. **Mutable state in signals:** `products.update(arr => { arr.push(item); return arr; })` — same reference, OnPush doesn't update. Always create new references.
3. **Selectors without memoization:** use createSelector for derived state — memoizes based on input selectors.
""",
"mcqs": [
  {"id":"d77q1","prompt":"What is a computed() signal and when does it recalculate?","options":["A computed property in HTML","A derived signal that automatically recalculates when any of its signal dependencies change — filteredProducts = computed(() => products().filter(...)) updates whenever products() or filter() changes","computed() runs on every render","Requires OnPush"],"correctAnswer":"A derived signal that automatically recalculates when any of its signal dependencies change — filteredProducts = computed(() => products().filter(...)) updates whenever products() or filter() changes","explanation":"computed(): lazily evaluated and memoized. If no dependency changed: returns cached value. If any dependency changes: recalculates. Eliminates getter methods that recalculate on every CD cycle. Like RxJS combineLatest but synchronous."},
  {"id":"d77q2","prompt":"What problem does NgRx solve that service-based state doesn't?","options":["NgRx is faster","NgRx provides: predictable state mutations (reducer is pure function), time-travel debugging (DevTools), traceable actions, effects for side effects, strict separation of concerns. Overkill for most apps but essential for large teams","NgRx prevents memory leaks","NgRx replaces HttpClient"],"correctAnswer":"NgRx provides: predictable state mutations (reducer is pure function), time-travel debugging (DevTools), traceable actions, effects for side effects, strict separation of concerns. Overkill for most apps but essential for large teams","explanation":"Service state: any component can call any method → hard to track mutations. NgRx: all mutations go through actions → reducers are pure → Redux DevTools shows exact state at each point → time-travel debug."},
  {"id":"d77q3","prompt":"What does an NgRx reducer guarantee about state mutations?","options":["Reducers can make HTTP calls","Reducers are PURE FUNCTIONS — given the same state and action, always return the same new state. No side effects, no HTTP calls, no async operations. Makes state predictable and testable","Reducers replace effects","Pure reducers allow mutation"],"correctAnswer":"Reducers are PURE FUNCTIONS — given the same state and action, always return the same new state. No side effects, no HTTP calls, no async operations. Makes state predictable and testable","explanation":"(state, action) => newState. No this, no inject(), no Date.now(). Immutable: always spread (...state, newField). Side effects (HTTP, navigation, logging) → NgRx Effects. Pure reducer: trivial to unit test without mocks."},
  {"id":"d77q4","prompt":"What is an NgRx Effect and what is it responsible for?","options":["HTML side effects","Handles async side effects (HTTP calls, navigation, localStorage) that shouldn't be in reducers. Listens for actions, performs side effects, dispatches new actions with results","Effects replace services","Effects run in the template"],"correctAnswer":"Handles async side effects (HTTP calls, navigation, localStorage) that shouldn't be in reducers. Listens for actions, performs side effects, dispatches new actions with results","explanation":"loadProducts action → Effect catches it → calls API → dispatches loadProductsSuccess or loadProductsFailure → reducer handles those synchronously. Chain: Action → Effect (async) → Action → Reducer (sync)."},
  {"id":"d77q5","prompt":"What does `signal.asReadonly()` return?","options":["An Observable","A ReadonlySignal — consumers can read the value but cannot call .set() or .update() on it. Enforces state encapsulation: only the owning service modifies state","asReadonly() is for debugging","Required for computed()"],"correctAnswer":"A ReadonlySignal — consumers can read the value but cannot call .set() or .update() on it. Enforces state encapsulation: only the owning service modifies state","explanation":"TypeScript: ReadonlySignal<T> has no set/update methods. Compile error if component tries to modify. Same as BehaviorSubject.asObservable(). Service: private _products = signal([]); exposed: products = this._products.asReadonly()"},
  {"id":"d77q6","prompt":"When should you choose signal-based services over NgRx?","options":["Always use NgRx","For most applications: signal services are simpler, no boilerplate, Angular native, easier to understand. NgRx when: large team needing strict conventions, complex async orchestration, time-travel debugging is critical","NgRx is always better","NgRx requires Angular 18"],"correctAnswer":"For most applications: signal services are simpler, no boilerplate, Angular native, easier to understand. NgRx when: large team needing strict conventions, complex async orchestration, time-travel debugging is critical","explanation":"80% of apps: signal service + computed() is sufficient. NgRx overhead: actions, reducers, effects, selectors, StoreModule — significant setup for simple CRUD. Use NgRx when team size/complexity justifies it."},
  {"id":"d77q7","prompt":"What does `createSelector` do in NgRx?","options":["Creates an HTML element","Creates a memoized selector — only recalculates when the input selectors' results change. selectFilteredProducts = createSelector(selectAll, selectFilter, (products, filter) => ...) is only recalculated when products or filter changes","createSelector replaces reducers","Selectors dispatch actions"],"correctAnswer":"Creates a memoized selector — only recalculates when the input selectors' results change. selectFilteredProducts = createSelector(selectAll, selectFilter, (products, filter) => ...) is only recalculated when products or filter changes","explanation":"Without memoization: selector runs on every store change. With createSelector: input selectors compared, if unchanged → cached result returned. For filtering 10,000 items: only re-filters when products or filter actually change."},
  {"id":"d77q8","prompt":"Why should state updates always create new object/array references?","options":["JavaScript requirement","Mutation (array.push(), object.prop = x) keeps the same reference — Angular's OnPush change detection, signal comparisons, and NgRx reducers all compare by reference (===). New reference → update triggered","Angular copies objects","Only matters for arrays"],"correctAnswer":"Mutation (array.push(), object.prop = x) keeps the same reference — Angular's OnPush change detection, signal comparisons, and NgRx reducers all compare by reference (===). New reference → update triggered","explanation":"products.update(arr => { arr.push(item); return arr; }): same array reference → no update. products.update(arr => [...arr, item]): new reference → triggers update. NgRx reducers: { ...state, products: [...state.products, newProduct] }."},
  {"id":"d77q9","prompt":"What is `effect()` in Angular signals (not NgRx)?","options":["An animation effect","A side-effect runner that automatically re-executes whenever any signal it reads changes — effect(() => localStorage.setItem('prefs', JSON.stringify(prefs()))) persists preferences on every change","effect() replaces ngOnInit","Same as tap() in RxJS"],"correctAnswer":"A side-effect runner that automatically re-executes whenever any signal it reads changes — effect(() => localStorage.setItem('prefs', JSON.stringify(prefs()))) persists preferences on every change","explanation":"effect(): tracks signal reads automatically (like computed but for side effects, no return value). Runs when any read signal changes. Use for: sync to localStorage, logging, analytics. Don't use for DOM manipulation (use AfterRenderEffect) or heavy computations (use computed)."},
  {"id":"d77q10","prompt":"How does store.dispatch() work in NgRx?","options":["Dispatches HTTP requests","Sends an action to the NgRx store — all reducers and effects that handle this action type are invoked. The state update is synchronous (reducer); side effects are asynchronous (effects)","dispatch() sends to the server","Only one reducer handles each action"],"correctAnswer":"Sends an action to the NgRx store — all reducers and effects that handle this action type are invoked. The state update is synchronous (reducer); side effects are asynchronous (effects)","explanation":"store.dispatch(loadProducts()): → productReducer handles it synchronously (sets loading:true) → ProductEffects handles it asynchronously (makes HTTP call, dispatches loadProductsSuccess). Multiple reducers can handle the same action."}
],
"writtenConceptQuestions": [
  "Implement a ProductStateService using signals with loading, error, filter state, and computed filteredProducts.",
  "Show NgRx setup for products: actions, reducer, effects, and selectors. Show component dispatching and selecting.",
  "Compare signals vs NgRx for a shopping cart. When would you choose each?",
  "Explain createSelector memoization. Show selectFilteredSortedProducts combining two selectors.",
  "Show computed() signal for cart total. Show effect() for persisting to localStorage.",
  "Why is immutability critical for signal and NgRx state? Show mutation vs immutable update.",
  "Show the complete NgRx action→effect→reducer chain for loading products with error handling."
],
"businessScenarios": [
  "The product list re-renders on every keypress in the search box. Add a computed() signal for filtered products so Angular only re-renders when the filtered result actually changes.",
  "Five developers are working on a large e-commerce app. Component state mutations are causing hard-to-track bugs. Introduce NgRx with strict action tracing for the order management feature.",
  "User preferences (theme, language) should persist across sessions. Use effect() to sync a preferences signal to localStorage automatically."
]
},

"day-078": {
"notes": """# Angular Performance: OnPush, trackBy, Zone-less, and Optimization Techniques

## Change Detection Strategies
```typescript
// Default: check every component on every browser event
@Component({ changeDetection: ChangeDetectionStrategy.Default })

// OnPush: check only when:
// 1. @Input reference changes
// 2. Event originates from this component/child
// 3. async pipe emits
// 4. markForCheck() or detectChanges() called
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `...`
})
export class ProductCardComponent {
  @Input({ required: true }) product!: Product;

  // PROBLEM: parent mutates the array, same @Input reference
  // this.products.push(newProduct) → OnPush doesn't detect
  //
  // FIX: create new reference
  // this.products = [...this.products, newProduct]
}
```

## ChangeDetectorRef — Manual Control
```typescript
@Component({ changeDetection: ChangeDetectionStrategy.OnPush })
export class NotificationComponent {
  notifications: string[] = [];
  private cdr = inject(ChangeDetectorRef);

  // Triggered outside Angular zone (e.g., from WebSocket)
  receiveNotification(msg: string) {
    this.notifications.push(msg);
    this.cdr.markForCheck();  // tell Angular: re-check this component tree
  }

  // Or run inside Angular zone:
  private ngZone = inject(NgZone);
  receiveOutOfZone(msg: string) {
    this.ngZone.run(() => {
      this.notifications.push(msg);  // triggers normal CD
    });
  }
}
```

## @for with track — Efficient List Rendering
```html
<!-- Without track: Angular destroys and recreates ALL DOM nodes on list change -->
@for (product of products; track $index) {     <!-- track by index: moves → destroy/recreate -->
@for (product of products; track product.id) { <!-- track by id: same id → reuse DOM node -->

<!-- Best: use stable unique identifier -->
@for (order of orders; track order.id) {
  <app-order-card [order]="order" />  <!-- OnPush + track = minimal renders -->
}

<!-- For primitive arrays without IDs: -->
@for (name of names; track name) { <li>{{ name }}</li> }
```

## Pure Pipes vs Methods in Templates
```typescript
// BAD: method called on every CD cycle
// <p>{{ getFormattedPrice(product.price) }}</p>
// This runs on every mouse move, keypress, etc.
formatPrice(price: number): string {
  return '$' + price.toFixed(2);  // called many times per second
}

// GOOD: pure pipe — only recalculates when input reference changes
@Pipe({ name: 'price', standalone: true, pure: true })
export class PricePipe implements PipeTransform {
  transform(price: number, currency = 'USD'): string {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(price);
  }
}
// Template: {{ product.price | price:'USD' }}
```

## Zone-less Applications (Angular 18+)
```typescript
// Opt out of Zone.js for maximum performance
export const appConfig: ApplicationConfig = {
  providers: [
    provideExperimentalZonelessChangeDetection()  // Angular 18+
  ]
};

// Without Zone.js: change detection only via signals and markForCheck()
// No monkey-patching of browser APIs
// Faster initial load, smaller bundle (Zone.js removed)
// Use signals for all reactive state
```

## Bundle Optimization Strategies
```typescript
// 1. Lazy loading (code splitting)
{ path: 'admin', loadComponent: () => import('./admin.component').then(m => m.AdminComponent) }

// 2. Defer block (Angular 17+) — lazy load parts of a template
@defer (on viewport) {
  <app-product-reviews [productId]="product.id" />
} @placeholder {
  <div class="skeleton" style="height: 200px"></div>
}

// 3. Images with NgOptimizedImage
<img ngSrc="product.jpg" width="400" height="300" priority />
// Adds: loading="lazy" by default, srcset for responsive, priority for LCP images

// 4. Virtual scrolling for large lists (CDK)
<cdk-virtual-scroll-viewport itemSize="80" style="height: 400px">
  <app-order-row *cdkVirtualFor="let order of orders" [order]="order" />
</cdk-virtual-scroll-viewport>
```

## Common Mistakes
1. **Method calls in templates:** every method in `{{ method() }}` runs on every CD cycle. Replace with pure pipes or computed signals.
2. **track $index with sort/filter:** if you sort, the same item gets a different index → DOM nodes destroyed and recreated. Use `track item.id`.
3. **Large initial bundles:** not lazy-loading feature routes results in users downloading unused code.
""",
"mcqs": [
  {"id":"d78q1","prompt":"What are the four conditions that trigger OnPush change detection?","options":["Any state change","1. @Input reference changes, 2. An event originates from the component or its children, 3. async pipe emits a new value, 4. markForCheck() or detectChanges() is explicitly called","Only explicit markForCheck()","HTTP responses trigger OnPush"],"correctAnswer":"1. @Input reference changes, 2. An event originates from the component or its children, 3. async pipe emits a new value, 4. markForCheck() or detectChanges() is explicitly called","explanation":"Default CD: every setTimeout, click, HTTP response triggers full tree check. OnPush: selective. Angular skips the component unless one of these 4 conditions is met. Result: fewer checks, better performance."},
  {"id":"d78q2","prompt":"Why does `track $index` cause poor performance when sorting or filtering a list?","options":["Indices aren't numbers","When the list is sorted or filtered, item at index 0 may be a different item — Angular sees 'index 0 changed' → destroys and recreates that DOM node even though the item itself is unchanged. track item.id: same item, same DOM node, just moved","track $index is deprecated","Sorting breaks all track expressions"],"correctAnswer":"When the list is sorted or filtered, item at index 0 may be a different item — Angular sees 'index 0 changed' → destroys and recreates that DOM node even though the item itself is unchanged. track item.id: same item, same DOM node, just moved","explanation":"Sort: [A, B, C] → [C, A, B]. With track $index: index 0 changed from A to C → destroy A node, create C node. With track item.id: C moved from index 2 to 0 → just a DOM move, no destroy/create. 10x faster for large lists."},
  {"id":"d78q3","prompt":"Why are method calls in templates bad for performance?","options":["Syntax error","Methods are called on every change detection cycle — every mouse move, keypress, timer — regardless of whether their inputs changed. For expensive computations, this causes significant lag","Methods are slower than pipes","Template methods are deprecated"],"correctAnswer":"Methods are called on every change detection cycle — every mouse move, keypress, timer — regardless of whether their inputs changed. For expensive computations, this causes significant lag","explanation":"{{ formatDate(order.date) }}: formatDate() called 60 times per second on an active page. {{ order.date | date:'dd/MM/yyyy' }}: DatePipe runs only when order.date reference changes. Fix: pure pipe or computed signal."},
  {"id":"d78q4","prompt":"What does the Angular 17 `@defer` block do?","options":["Defers the entire app","Lazily loads a part of the template — the component/content is only downloaded and rendered when the trigger condition is met (on viewport, on interaction, on idle). Improves initial page load","@defer requires Zone.js","@defer is for HTTP requests"],"correctAnswer":"Lazily loads a part of the template — the component/content is only downloaded and rendered when the trigger condition is met (on viewport, on interaction, on idle). Improves initial page load","explanation":"@defer (on viewport): the component is not in the initial bundle. When it scrolls into view, Angular downloads its chunk and renders it. @placeholder: shown while loading. Reduces LCP and TTI for pages with below-the-fold content."},
  {"id":"d78q5","prompt":"What does `ChangeDetectorRef.markForCheck()` do in OnPush?","options":["Forces immediate re-render","Marks the component and all its ancestors for check in the NEXT change detection run — used when state changes come from outside Angular's zone (WebSocket, third-party library callbacks)","markForCheck() triggers CD immediately","Same as detectChanges()"],"correctAnswer":"Marks the component and all its ancestors for check in the NEXT change detection run — used when state changes come from outside Angular's zone (WebSocket, third-party library callbacks)","explanation":"WebSocket message arrives outside Angular zone → Zone.js doesn't know → CD not triggered → UI not updated. this.cdr.markForCheck(): tells Angular to include this component in the next CD run. detectChanges(): runs CD on this subtree immediately."},
  {"id":"d78q6","prompt":"What does `NgOptimizedImage` (ngSrc) provide?","options":["Optimizes all CSS images","Adds: automatic lazy loading (loading='lazy' by default), explicit width/height for CLS prevention, srcset for responsive images, priority attribute for LCP, and warns on unoptimized images","Requires a CDN","ngSrc replaces all <img> tags"],"correctAnswer":"Adds: automatic lazy loading (loading='lazy' by default), explicit width/height for CLS prevention, srcset for responsive images, priority attribute for LCP, and warns on unoptimized images","explanation":"Core Web Vitals: CLS (layout shift) prevented by width/height. LCP (largest contentful paint) improved by priority='true' on hero images (adds fetchpriority='high'). LCP offscreen images get loading='lazy'. Significant performance improvement with minimal code change."},
  {"id":"d78q7","prompt":"What is virtual scrolling and when is it necessary?","options":["Video streaming","Rendering only the visible DOM nodes in a large list — cdk-virtual-scroll-viewport renders ~10 visible rows instead of 10,000 DOM nodes. Critical when list length is in thousands","Virtual scrolling is for pagination","Only works with fixed-height items"],"correctAnswer":"Rendering only the visible DOM nodes in a large list — cdk-virtual-scroll-viewport renders ~10 visible rows instead of 10,000 DOM nodes. Critical when list length is in thousands","explanation":"1000 *ngFor items: 1000 DOM nodes, styles, event listeners — slow render, high memory. Virtual scroll: renders visible items + small buffer. Scroll: destroy off-screen, render newly visible. 10x+ performance improvement for large lists."},
  {"id":"d78q8","prompt":"What is zone-less Angular (`provideExperimentalZonelessChangeDetection`)?","options":["Removes all zones from JavaScript","Removes Zone.js entirely — no monkey-patching of browser APIs. Change detection triggered only by signals and markForCheck(). Smaller bundle, faster startup, predictable CD. Requires signal-based state","Zone-less removes all change detection","Zone-less is production-ready in Angular 17"],"correctAnswer":"Removes Zone.js entirely — no monkey-patching of browser APIs. Change detection triggered only by signals and markForCheck(). Smaller bundle, faster startup, predictable CD. Requires signal-based state","explanation":"Zone.js: ~15KB, monkey-patches all browser APIs (setTimeout, Promise, etc.) to trigger CD. Costly for performance. Without Zone.js: no magic — only signals and explicit markForCheck() trigger updates. Angular 18 makes this experimental; future default."},
  {"id":"d78q9","prompt":"What is the difference between `markForCheck()` and `detectChanges()`?","options":["Identical","markForCheck(): schedules the component and ancestors for the NEXT CD run (asynchronous). detectChanges(): immediately runs CD on this component and its children synchronously. Use markForCheck for most cases; detectChanges in specific synchronous scenarios","detectChanges() is deprecated","Both run asynchronously"],"correctAnswer":"markForCheck(): schedules the component and ancestors for the NEXT CD run (asynchronous). detectChanges(): immediately runs CD on this component and its children synchronously. Use markForCheck for most cases; detectChanges in specific synchronous scenarios","explanation":"markForCheck(): batches updates, more efficient. detectChanges(): immediate but can cause ExpressionChangedAfterItHasBeenCheckedError if called during a CD cycle. For most cases, markForCheck is preferred."},
  {"id":"d78q10","prompt":"What is `detach()` on ChangeDetectorRef and when is it used?","options":["Removes the component","Completely removes the component from Angular's CD tree — the component never updates automatically. Must manually call detectChanges() when needed. Use for: dashboards, read-only reports, tables that update on demand","detach() destroys the component","Only for OnPush components"],"correctAnswer":"Completely removes the component from Angular's CD tree — the component never updates automatically. Must manually call detectChanges() when needed. Use for: dashboards, read-only reports, tables that update on demand","explanation":"Real-time dashboard: 100 child components. Even with OnPush, Angular walks all of them. cdr.detach(): component removed from tree entirely — zero CD overhead. When refresh needed: cdr.detectChanges(). Maximum performance for read-heavy UIs."}
],
"writtenConceptQuestions": [
  "Show OnPush change detection with @Input immutability pattern. Show what breaks with array.push() and the fix.",
  "Show @for with track product.id. Explain why track $index breaks after sort/filter.",
  "Compare method calls in templates vs pure pipes vs computed signals for performance.",
  "Show @defer with on viewport trigger and @placeholder. What bundle optimization does it enable?",
  "Explain markForCheck() vs detectChanges(). Show when WebSocket data requires markForCheck().",
  "Show virtual scrolling with CdkVirtualScrollViewport for a 10,000-item order list.",
  "What is zone-less Angular? Show provideExperimentalZonelessChangeDetection and its requirements."
],
"businessScenarios": [
  "An order management table with 100 rows re-renders on every mouse move. Add OnPush to the row component and fix all @Input mutations.",
  "A product detail page has customer reviews below the fold, slowing initial render. Use @defer (on viewport) to lazy-load the reviews section.",
  "A real-time WebSocket dashboard shows 50 charts that update frequently. Use cdr.detach() on charts that aren't visible and manually trigger detectChanges() on data update."
]
},

"day-079": {
"notes": """# Angular Lazy Loading: Feature Routes, Preloading, and Bundle Strategies

## Route-Based Lazy Loading
```typescript
// Without lazy loading: ALL components loaded at startup
import { AdminComponent } from './admin/admin.component';     // eager
import { ReportsComponent } from './reports/reports.component';  // eager

// With lazy loading: components load only when navigated to
export const routes: Routes = [
  // Eager routes (fast path — load immediately)
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },

  // Lazy routes (separate JS chunks — only downloaded on navigation)
  {
    path: 'orders',
    loadComponent: () => import('./orders/orders.component').then(m => m.OrdersComponent),
    canActivate: [authGuard]
  },
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes').then(r => r.adminRoutes),
    canActivate: [authGuard, hasRole('ADMIN')]
  },
  {
    path: 'reports',
    loadChildren: () => import('./reports/reports.routes').then(r => r.reportsRoutes),
    canActivate: [authGuard]
  }
];
```

## Feature Route Files
```typescript
// admin/admin.routes.ts
export const adminRoutes: Routes = [
  { path: '', component: AdminDashboardComponent },
  { path: 'users', component: UserManagementComponent },
  { path: 'users/:id', component: UserDetailComponent },
  {
    path: 'settings',
    loadComponent: () => import('./settings/settings.component').then(m => m.SettingsComponent)
  }
];
```

## Preloading Strategies
```typescript
// No preloading (default) — only load on navigation
provideRouter(routes)

// Preload all lazy routes after startup (aggressive)
provideRouter(routes, withPreloading(PreloadAllModules))

// Custom preloading — selective based on route data
export class SelectivePreloadingStrategy implements PreloadingStrategy {
  preload(route: Route, load: () => Observable<any>): Observable<any> {
    return route.data?.['preload'] === true ? load() : EMPTY;
  }
}

provideRouter(routes, withPreloading(SelectivePreloadingStrategy))

// Mark routes for preloading:
{ path: 'orders', loadChildren: () => import(...), data: { preload: true } }
```

## Webpack Bundle Analysis
```bash
# Build with bundle analysis
ng build --stats-json
npx webpack-bundle-analyzer dist/app/stats.json

# Source map explorer
npm install -g source-map-explorer
ng build --source-map
npx source-map-explorer 'dist/app/*.js'
```

## Defer Blocks for Template-Level Lazy Loading (Angular 17+)
```html
<!-- Defer entire component until it scrolls into view -->
@defer (on viewport) {
  <app-product-reviews [productId]="product.id" />
} @loading (minimum 300ms) {
  <div class="skeleton" />
} @error {
  <p>Failed to load reviews</p>
} @placeholder (minimum 200ms) {
  <div style="height: 200px" />
}

<!-- Trigger options -->
@defer (on idle)           { ... }  <!-- browser idle -->
@defer (on timer(3s))      { ... }  <!-- after 3 seconds -->
@defer (on interaction)    { ... }  <!-- on user interaction -->
@defer (when isLoggedIn()) { ... }  <!-- when signal becomes true -->

<!-- Prefetch separately from rendering -->
@defer (on viewport; prefetch on idle) {
  <app-heavy-chart />
}
```

## Module-Level Tree Shaking
```typescript
// BAD: importing entire library
import * as _ from 'lodash';                  // ~71KB
import { format } from 'date-fns';            // imports all of date-fns

// GOOD: specific imports (tree-shaken)
import { debounce, throttle } from 'lodash-es';  // only debounce + throttle
import { format } from 'date-fns/format';         // only format

// Angular Material: import only what you use
import { MatButtonModule } from '@angular/material/button';   // OK
import { MatInputModule }  from '@angular/material/input';    // OK
// NOT: import { MaterialModule } from './material.module';   // imports everything
```

## Common Mistakes
1. **Lazy loading but forgetting standalone imports:** standalone lazy-loaded components must import their dependencies in `imports: []`.
2. **Not verifying code splitting:** use `ng build --stats-json` and webpack-bundle-analyzer to confirm chunks are separate.
3. **Over-aggressive preloading:** PreloadAllModules defeats the purpose of lazy loading for admin routes.
""",
"mcqs": [
  {"id":"d79q1","prompt":"What does `loadComponent: () => import('./admin.component').then(m => m.AdminComponent)` achieve?","options":["Creates a component","Tells Angular to lazy-load AdminComponent — it's compiled into a separate JavaScript chunk that is only downloaded when the user navigates to this route, reducing the initial bundle size","Loads the component eagerly","Requires NgModule"],"correctAnswer":"Tells Angular to lazy-load AdminComponent — it's compiled into a separate JavaScript chunk that is only downloaded when the user navigates to this route, reducing the initial bundle size","explanation":"Dynamic import(): Webpack creates a separate chunk file. First navigation to the route: Angular downloads the chunk → creates component. Subsequent navigations: chunk is cached → instant. Network tab: you'll see admin-component-xxx.js appear on first visit."},
  {"id":"d79q2","prompt":"What is the difference between `loadComponent` and `loadChildren`?","options":["loadComponent is faster","loadComponent: lazy-load a single standalone component. loadChildren: lazy-load a routes configuration file (can contain multiple components with their own children) — creates a separate chunk for the entire feature","loadChildren requires NgModule","Both produce identical bundles"],"correctAnswer":"loadComponent: lazy-load a single standalone component. loadChildren: lazy-load a routes configuration file (can contain multiple components with their own children) — creates a separate chunk for the entire feature","explanation":"loadComponent: one component, one chunk. loadChildren: one routes file that can import many components — all bundled in the feature chunk. Use loadChildren for features with multiple routes; loadComponent for single lazy pages."},
  {"id":"d79q3","prompt":"What does `PreloadAllModules` preloading strategy do?","options":["Loads all modules at once","After the app shell loads and becomes interactive, Angular downloads ALL lazy route chunks in the background — subsequent navigations feel instant even before the user visits them","Preloads only the current route","Replaces lazy loading"],"correctAnswer":"After the app shell loads and becomes interactive, Angular downloads ALL lazy route chunks in the background — subsequent navigations feel instant even before the user visits them","explanation":"Trade-off: faster subsequent navigation (chunks pre-downloaded) but wastes bandwidth for routes never visited. Better: selective preloading — only preload routes likely to be visited next (e.g., the next step in a workflow)."},
  {"id":"d79q4","prompt":"What does `@defer (on viewport)` do in Angular 17?","options":["Renders after 1 second","The deferred content is NOT downloaded until the element's placeholder comes into the browser viewport. The component code is excluded from the initial bundle — reduces initial bundle size and improves LCP","on viewport is experimental","Requires the Intersection Observer API manually"],"correctAnswer":"The deferred content is NOT downloaded until the element's placeholder comes into the browser viewport. The component code is excluded from the initial bundle — reduces initial bundle size and improves LCP","explanation":"Product reviews below the fold: users scrolling eventually see them. Until scroll: only the @placeholder renders (no chunk downloaded). On scroll into view: Angular downloads the reviews chunk and renders it. Zero cost for users who don't scroll."},
  {"id":"d79q5","prompt":"What is tree shaking and why does `import * as _ from 'lodash'` defeat it?","options":["Removing unused CSS","Tree shaking eliminates unused JavaScript from the bundle. `import * as _` pulls ALL of lodash into the bundle even if you only use one function. `import { debounce } from 'lodash-es'`: only debounce is bundled","Tree shaking is automatic for all imports","Only applies to Angular modules"],"correctAnswer":"Tree shaking eliminates unused JavaScript from the bundle. `import * as _` pulls ALL of lodash into the bundle even if you only use one function. `import { debounce } from 'lodash-es'`: only debounce is bundled","explanation":"Lodash: 71KB. You use only debounce. import * as _: entire 71KB included. import { debounce } from 'lodash-es': only debounce function included — maybe 2KB. Named imports from ES modules are tree-shakeable; default imports often aren't."},
  {"id":"d79q6","prompt":"What does the `@defer (on idle)` trigger mean?","options":["Loads when browser crashes","Defers loading until the browser's main thread is idle (requestIdleCallback) — loads non-critical content without competing with user interactions and critical rendering","on idle is the default","Requires a service worker"],"correctAnswer":"Defers loading until the browser's main thread is idle (requestIdleCallback) — loads non-critical content without competing with user interactions and critical rendering","explanation":"Initial page load: critical content renders. Browser idle: Angular downloads deferred chunks (analytics, chat widget, non-critical widgets). Result: fast initial render, deferred content loads when CPU is free without blocking interactions."},
  {"id":"d79q7","prompt":"What is a SelectivePreloadingStrategy and why is it better than PreloadAllModules?","options":["Random preloading","Only preloads routes marked with `data: { preload: true }` — you control which routes are worth preloading (likely next steps) vs routes rarely visited (admin). Balances performance vs bandwidth","Selective is default","PreloadAllModules is deprecated"],"correctAnswer":"Only preloads routes marked with `data: { preload: true }` — you control which routes are worth preloading (likely next steps) vs routes rarely visited (admin). Balances performance vs bandwidth","explanation":"E-commerce: preload /orders (everyone goes there) but not /admin (only 1% of users). PreloadAllModules: downloads admin chunk for all users. Selective: only downloads what's likely needed. Better for metered connections."},
  {"id":"d79q8","prompt":"What does `--stats-json` with webpack-bundle-analyzer show?","options":["Test coverage","Visual treemap of every module in your bundle — shows which chunks exist, their sizes, and which packages take up the most space. Identifies large dependencies to optimize","Only shows total bundle size","Required for production builds"],"correctAnswer":"Visual treemap of every module in your bundle — shows which chunks exist, their sizes, and which packages take up the most space. Identifies large dependencies to optimize","explanation":"ng build --stats-json → dist/stats.json. webpack-bundle-analyzer dist/stats.json: browser opens with interactive treemap. See: rxjs (150KB), @angular/forms (80KB), lodash (71KB). Identify: why is this chunk 500KB? What can be removed or split?"},
  {"id":"d79q9","prompt":"What is the `@loading` block in @defer and when is it shown?","options":["Shows during HTTP calls","Shows while the deferred content is being downloaded and initialized — appears after the trigger condition is met but before the content is ready. @placeholder shows BEFORE the trigger; @loading shows DURING download","Same as @placeholder","@loading requires async pipe"],"correctAnswer":"Shows while the deferred content is being downloaded and initialized — appears after the trigger condition is met but before the trigger; @loading shows DURING download","explanation":"@defer timeline: before trigger → @placeholder. Trigger fires (scroll, idle, etc.) → download starts → @loading shows. Download complete, component init → deferred content shows. If download fails → @error. minimum: shows loading for at least N ms even if fast."},
  {"id":"d79q10","prompt":"Why must standalone lazy-loaded components include their imports?","options":["Standalone is a TypeScript requirement","Standalone components don't rely on NgModule for their dependencies — they declare their own imports. A lazy-loaded standalone component that uses CommonModule/RouterLink must import them in its @Component imports or it fails to compile","NgModule handles imports automatically","Only required for directives"],"correctAnswer":"Standalone components don't rely on NgModule for their dependencies — they declare their own imports. A lazy-loaded standalone component that uses CommonModule/RouterLink must import them in its @Component imports or it fails to compile","explanation":"Lazy component: @Component({ standalone: true, imports: [CommonModule, RouterLink, ReactiveFormsModule] }). Forgetting imports: template uses *ngIf but CommonModule not imported → compiler error. Each standalone component is self-contained."}
],
"writtenConceptQuestions": [
  "Show route configuration with eager routes (dashboard) and lazy routes (orders, admin) using loadComponent and loadChildren.",
  "Implement a SelectivePreloadingStrategy that preloads routes with data: { preload: true }.",
  "Show @defer with all trigger options: on viewport, on idle, on interaction, when signal. Include @loading and @error.",
  "Show how to analyze bundle sizes with ng build --stats-json and webpack-bundle-analyzer.",
  "Explain the difference between route-level lazy loading (@defer) and template-level defer blocks.",
  "Show tree-shakeable imports from lodash-es and Angular Material.",
  "Show feature routes file (admin.routes.ts) and the parent routes loading it with loadChildren."
],
"businessScenarios": [
  "The app has a 2MB initial bundle. Admin and reports are included even for non-admin users. Add lazy loading so admin and reports only download for users who navigate there.",
  "A product page has customer reviews taking 400ms to render, blocking LCP. Use @defer (on viewport) for the reviews section.",
  "Performance analysis shows date-fns is 80KB in the bundle but only 3 format functions are used. Fix with specific named imports."
]
},

"day-080": {
"notes": """# Angular Testing: TestBed, ComponentFixture, and Service Testing

## Unit Testing Angular Components
```typescript
describe('ProductCardComponent', () => {
  let component: ProductCardComponent;
  let fixture: ComponentFixture<ProductCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProductCardComponent],  // standalone component — import directly
      providers: [
        { provide: ProductService, useValue: mockProductService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ProductCardComponent);
    component = fixture.componentInstance;

    // Set required @Input
    component.product = { id: '1', name: 'Widget', price: 9.99, stock: 10 };
    fixture.detectChanges();  // trigger ngOnInit and first render
  });

  it('should display product name', () => {
    const nameEl = fixture.debugElement.query(By.css('.product-name'));
    expect(nameEl.nativeElement.textContent).toContain('Widget');
  });

  it('should emit addToCart when button clicked', () => {
    let emittedProduct: Product | undefined;
    component.addToCart.subscribe(p => emittedProduct = p);

    const btn = fixture.debugElement.query(By.css('[data-testid="add-to-cart"]'));
    btn.triggerEventHandler('click', null);

    expect(emittedProduct).toEqual(component.product);
  });

  it('should disable Add to Cart button when out of stock', () => {
    component.product = { ...component.product, stock: 0 };
    fixture.detectChanges();

    const btn = fixture.debugElement.query(By.css('button'));
    expect(btn.nativeElement.disabled).toBeTrue();
  });
});
```

## Testing Services with HttpClientTesting
```typescript
describe('OrderService', () => {
  let service: OrderService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        OrderService,
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });
    service = TestBed.inject(OrderService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();  // assert no unexpected HTTP requests remain
  });

  it('should fetch orders', () => {
    const mockOrders: Order[] = [{ id: '1', status: 'PENDING' }];

    service.getOrders().subscribe(orders => {
      expect(orders.length).toBe(1);
      expect(orders[0].status).toBe('PENDING');
    });

    const req = httpMock.expectOne('/api/orders');
    expect(req.request.method).toBe('GET');
    req.flush(mockOrders);  // provide the mock response
  });

  it('should handle 404 errors', () => {
    service.getOrderById('999').subscribe({
      next: () => fail('Expected error'),
      error: err => expect(err.status).toBe(404)
    });

    httpMock.expectOne('/api/orders/999').flush('Not found', {
      status: 404,
      statusText: 'Not Found'
    });
  });
});
```

## Testing with Signals
```typescript
describe('CartStateService', () => {
  let service: CartStateService;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [CartStateService] });
    service = TestBed.inject(CartStateService);
  });

  it('should start with empty cart', () => {
    expect(service.items().length).toBe(0);
    expect(service.total()).toBe(0);
  });

  it('should add item to cart', () => {
    service.addItem({ id: '1', name: 'Widget', price: 9.99, quantity: 1 });
    expect(service.items().length).toBe(1);
    expect(service.total()).toBe(9.99);
  });
});
```

## ComponentHarness — Angular Material Testing
```typescript
import { MatButtonHarness } from '@angular/material/button/testing';

it('should click submit button', async () => {
  const loader = TestbedHarnessEnvironment.loader(fixture);
  const button = await loader.getHarness(MatButtonHarness.with({ text: 'Submit' }));

  expect(await button.isDisabled()).toBeFalse();
  await button.click();
  expect(component.submitted).toBeTrue();
});
```

## Async Testing with fakeAsync and tick
```typescript
it('should debounce search', fakeAsync(() => {
  component.searchTerm = 'prod';
  component.onSearchChange('prod');

  // Observable hasn't fired yet (debounce pending)
  expect(mockService.search).not.toHaveBeenCalled();

  tick(300);  // advance virtual time 300ms

  expect(mockService.search).toHaveBeenCalledWith('prod');
}));

it('should load products on init', fakeAsync(() => {
  const mockProducts = [{ id: '1', name: 'Widget' }];
  mockProductService.getProducts.and.returnValue(of(mockProducts));

  fixture.detectChanges();  // triggers ngOnInit
  tick();                   // flush observables

  expect(component.products.length).toBe(1);
}));
```

## Common Mistakes
1. **Not calling `fixture.detectChanges()` after input changes:** Angular won't re-render without it.
2. **Using `fixture.nativeElement.querySelector()` instead of `By.css()`:** By.css returns DebugElement with access to Angular-specific methods.
3. **Forgetting `httpMock.verify()`:** outstanding HTTP requests won't fail the test without it.
""",
"mcqs": [
  {"id":"d80q1","prompt":"What does `fixture.detectChanges()` do in a component test?","options":["Detects CSS changes","Triggers Angular change detection — runs ngOnInit (first call), updates template bindings, and processes @Input changes. Must be called after setting @Input values to see the effect in the template","detectChanges() is automatic","Required only for OnPush components"],"correctAnswer":"Triggers Angular change detection — runs ngOnInit (first call), updates template bindings, and processes @Input changes. Must be called after setting @Input values to see the effect in the template","explanation":"TestBed.createComponent: creates the component but doesn't call ngOnInit or update the template. First fixture.detectChanges(): runs ngOnInit + renders. After changing inputs: detectChanges() again to reflect new values. Without it, tests query stale DOM."},
  {"id":"d80q2","prompt":"What does `httpMock.verify()` do in afterEach?","options":["Verifies test data","Asserts that there are no outstanding (unhandled) HTTP requests — prevents tests from silently making unrequested calls. Without it, unexpected HTTP calls in tested code go unnoticed","verify() resets the mock","Required before each test"],"correctAnswer":"Asserts that there are no outstanding (unhandled) HTTP requests — prevents tests from silently making unrequested calls. Without it, unexpected HTTP calls in tested code go unnoticed","explanation":"After httpMock.verify(): if your code made an HTTP request that wasn't matched by expectOne/match, the test fails. Ensures tests are exhaustive about all HTTP interactions. Always in afterEach."},
  {"id":"d80q3","prompt":"What does `By.css('.product-name')` return vs `nativeElement.querySelector`?","options":["Identical","By.css returns a DebugElement — Angular's testing wrapper with access to componentInstance, injector, triggerEventHandler. nativeElement.querySelector returns raw DOM HTMLElement — no Angular-specific methods","By.css is deprecated","querySelector is faster"],"correctAnswer":"By.css returns a DebugElement — Angular's testing wrapper with access to componentInstance, injector, triggerEventHandler. nativeElement.querySelector returns raw DOM HTMLElement — no Angular-specific methods","explanation":"debugElement.query(By.css('button')): DebugElement — .componentInstance, .triggerEventHandler('click', null), .injector.get(Service). .nativeElement: the underlying DOM element. Use DebugElement for Angular-aware queries."},
  {"id":"d80q4","prompt":"What does `fakeAsync` and `tick(300)` allow in a test?","options":["Real time-based testing","Synchronously advance virtual time — test debounced operations, setTimeout, and interval without waiting real milliseconds. tick(300) advances the fake clock by 300ms, triggering pending timers","fakeAsync requires a spy","tick() only works for Promise"],"correctAnswer":"Synchronously advance virtual time — test debounced operations, setTimeout, and interval without waiting real milliseconds. tick(300) advances the fake clock by 300ms, triggering pending timers","explanation":"Without fakeAsync: testing 300ms debounce requires actually waiting 300ms. With fakeAsync: onSearchChange('prod'); tick(300) — synchronous, immediate. All timers, intervals, debounces execute in fakeAsync zone when you call tick()."},
  {"id":"d80q5","prompt":"What is `req.flush(mockData)` in HttpTestingController?","options":["Flushes HTTP connections","Provides the response for a pending test HTTP request — the Observable in the service resolves with mockData as if the server responded","flush() makes a real HTTP call","Requires the server to run"],"correctAnswer":"Provides the response for a pending test HTTP request — the Observable in the service resolves with mockData as if the server responded","explanation":"service.getOrders().subscribe(orders => expect(orders).toEqual(mockOrders)). req.flush(mockOrders): the subscribe callback runs synchronously with mockOrders. No real HTTP. req.flush(null, { status: 404, statusText: 'Not Found' }): simulate error."},
  {"id":"d80q6","prompt":"How do you test a standalone component in TestBed?","options":["Add to NgModule.declarations","Import the component directly in TestBed.configureTestingModule({ imports: [MyComponent] }) — standalone components are self-contained and imported like modules","Standalone components can't be tested","Use imports: [NgModule]"],"correctAnswer":"Import the component directly in TestBed.configureTestingModule({ imports: [MyComponent] }) — standalone components are self-contained and imported like modules","explanation":"Traditional component: TestBed.configureTestingModule({ declarations: [MyComponent] }). Standalone: imports: [MyComponent]. The component brings its own dependencies. Override specific ones in providers: [{ provide: Service, useValue: mock }]."},
  {"id":"d80q7","prompt":"What does `DebugElement.triggerEventHandler('click', null)` do?","options":["Triggers a real browser click","Invokes Angular event handlers bound to the element via `(click)` or `@HostListener` — works without a real DOM event, useful for testing Angular-specific event bindings","triggerEventHandler simulates keyboard","Only works with native events"],"correctAnswer":"Invokes Angular event handlers bound to the element via `(click)` or `@HostListener` — works without a real DOM event, useful for testing Angular-specific event bindings","explanation":"btn.triggerEventHandler('click', { type: 'click' }): calls all handlers bound with (click)='handler($event)'. The $event is the second argument ({type:'click'}). More reliable than .nativeElement.click() which may not trigger Angular bindings in all environments."},
  {"id":"d80q8","prompt":"What is the purpose of `data-testid` attributes in templates?","options":["CSS styling hooks","Stable selectors for tests — decoupled from CSS classes (which change for styling) and HTML structure. By.css('[data-testid=\"add-to-cart\"]') finds elements regardless of class renames","Required by TestBed","Only for accessibility"],"correctAnswer":"Stable selectors for tests — decoupled from CSS classes (which change for styling) and HTML structure. By.css('[data-testid=\"add-to-cart\"]') finds elements regardless of class renames","explanation":"CSS classes: .btn-primary → .btn — breaks tests. data-testid: never changed for styling — stable contract for tests. Convention: strip data-testid in production builds. Prevents the 'test breaks on UI refactor' problem."},
  {"id":"d80q9","prompt":"What is a `Spy` in Jasmine and how is it used in Angular tests?","options":["Observes HTTP calls","A mock function that records calls and return values — `spyOn(service, 'getProducts').and.returnValue(of([]))` replaces the real method for the test duration, controls what it returns","Spies only work with services","jasmine.createSpy creates a component"],"correctAnswer":"A mock function that records calls and return values — `spyOn(service, 'getProducts').and.returnValue(of([]))` replaces the real method for the test duration, controls what it returns","explanation":"spyOn(service, 'getProducts').and.returnValue(of(mockProducts)): when component calls service.getProducts(), returns Observable of mockProducts instead of making HTTP. expect(service.getProducts).toHaveBeenCalled(): assert it was called. Isolates component from service."},
  {"id":"d80q10","prompt":"When should you use `async/await` vs `fakeAsync/tick` in Angular tests?","options":["Identical","async/await (with `waitForAsync`): for Promise-based async or when using real timing. fakeAsync/tick: for Observable/timer-based async when you need to control virtual time — faster, synchronous-looking tests","async is deprecated","fakeAsync requires Zone.js"],"correctAnswer":"async/await (with `waitForAsync`): for Promise-based async or when using real timing. fakeAsync/tick: for Observable/timer-based async when you need to control virtual time — faster, synchronous-looking tests","explanation":"waitForAsync: wraps test in Zone, waits for all async operations. Good for: component initialization with Promises. fakeAsync: freezes real time, tick() advances virtual clock. Good for: debounce, interval, RxJS timers. fakeAsync: faster, synchronous syntax for timer-based code."}
],
"writtenConceptQuestions": [
  "Write a complete component test for ProductCardComponent: test DOM rendering, @Output emit, and disabled state.",
  "Show OrderService test with HttpTestingController: test success, 404 error, and verify no extra requests.",
  "Show testing a signal-based CartStateService: addItem, removeItem, computed total.",
  "Show fakeAsync with tick() for testing a debounced search. Why is fakeAsync better than async here?",
  "Show how to test an @Input binding: set the input, detectChanges, and query the DOM.",
  "What are ComponentHarnesses? Show MatButtonHarness for testing a Material button.",
  "Show spyOn usage to mock a service method and assert it was called with the correct arguments."
],
"businessScenarios": [
  "Developers are manually testing every button click scenario in the browser. Write a comprehensive test for OrderFormComponent covering valid submit, invalid form state, and API error handling.",
  "OrderService tests are slow because they make real HTTP calls. Migrate to HttpTestingController-based tests.",
  "A debounced search input test is flaky due to real timing. Rewrite using fakeAsync and tick(300)."
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
