"""Rewrite days 86-90: Full Stack Mini Project, Resume Questions, Behavioral, System Design, Final."""
import json, os
DATA_DIR = "backend/data/curriculum"

CURRICULUM = {

"day-086": {
"notes": """# Full Stack Mini Project: End-to-End Feature Implementation

## Feature: Order Management with Real-Time Status Updates

### Backend — Spring Boot
```java
// Entity
@Entity
@Table(name = "orders")
public class Order {
    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private OrderStatus status = OrderStatus.PENDING;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false)
    private Customer customer;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @PrePersist
    void prePersist() { this.createdAt = this.updatedAt = LocalDateTime.now(); }

    @PreUpdate
    void preUpdate() { this.updatedAt = LocalDateTime.now(); }
}

// Service Layer
@Service
@Transactional
public class OrderService {
    private final OrderRepository orderRepo;
    private final CustomerRepository customerRepo;
    private final ApplicationEventPublisher events;

    public OrderDto createOrder(CreateOrderRequest req) {
        Customer customer = customerRepo.findById(req.customerId())
            .orElseThrow(() -> new EntityNotFoundException("Customer not found: " + req.customerId()));

        Order order = new Order();
        order.setCustomer(customer);
        req.items().forEach(item -> order.getItems().add(
            new OrderItem(order, item.productId(), item.quantity(), item.unitPrice())
        ));

        Order saved = orderRepo.save(order);
        events.publishEvent(new OrderCreatedEvent(saved.getId()));  // domain event
        return OrderMapper.toDto(saved);
    }

    public OrderDto updateStatus(String id, OrderStatus newStatus) {
        Order order = orderRepo.findById(id)
            .orElseThrow(() -> new EntityNotFoundException("Order not found: " + id));

        order.setStatus(newStatus);
        events.publishEvent(new OrderStatusChangedEvent(id, newStatus));
        return OrderMapper.toDto(order);
    }
}

// REST Controller
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {
    private final OrderService orderService;

    @GetMapping
    public Page<OrderDto> getOrders(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size,
        @RequestParam(required = false) OrderStatus status
    ) {
        return orderService.findAll(PageRequest.of(page, size), status);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public OrderDto createOrder(@Valid @RequestBody CreateOrderRequest req) {
        return orderService.createOrder(req);
    }

    @PatchMapping("/{id}/status")
    public OrderDto updateStatus(@PathVariable String id,
                                  @RequestBody UpdateStatusRequest req) {
        return orderService.updateStatus(id, req.status());
    }
}
```

### Angular Frontend
```typescript
// order.service.ts
@Injectable({ providedIn: 'root' })
export class OrderService {
  private http = inject(HttpClient);
  private baseUrl = '/api/orders';

  getOrders(params: OrderQueryParams): Observable<Page<OrderDto>> {
    return this.http.get<Page<OrderDto>>(this.baseUrl, { params: params as any });
  }

  createOrder(req: CreateOrderRequest): Observable<OrderDto> {
    return this.http.post<OrderDto>(this.baseUrl, req);
  }

  updateStatus(id: string, status: string): Observable<OrderDto> {
    return this.http.patch<OrderDto>(`${this.baseUrl}/${id}/status`, { status });
  }
}

// order-list.component.ts
@Component({
  standalone: true,
  imports: [CommonModule, RouterLink, OrderCardComponent, SpinnerComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (loading()) {
      <app-spinner />
    } @else {
      @for (order of orders(); track order.id) {
        <app-order-card [order]="order" (statusChange)="onStatusChange($event)" />
      }
      <app-paginator [page]="page()" [total]="total()" (pageChange)="loadPage($event)" />
    }
  `
})
export class OrderListComponent implements OnInit {
  private orderService = inject(OrderService);

  orders  = signal<OrderDto[]>([]);
  loading = signal(false);
  page    = signal(0);
  total   = signal(0);

  ngOnInit() { this.loadOrders(); }

  loadOrders() {
    this.loading.set(true);
    this.orderService.getOrders({ page: this.page(), size: 20 })
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe(result => {
        this.orders.set(result.content);
        this.total.set(result.totalElements);
      });
  }

  onStatusChange(event: { id: string; status: string }) {
    this.orderService.updateStatus(event.id, event.status).subscribe(updated =>
      this.orders.update(orders => orders.map(o => o.id === updated.id ? updated : o))
    );
  }

  loadPage(p: number) { this.page.set(p); this.loadOrders(); }
}
```

## DSA Topic: Two Sum (HashMap)
```java
// LeetCode 1 — classic HashMap lookup
public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> seen = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int complement = target - nums[i];
        if (seen.containsKey(complement)) {
            return new int[]{seen.get(complement), i};
        }
        seen.put(nums[i], i);
    }
    return new int[]{};
}
// Time: O(n), Space: O(n)
// Key insight: for each number, check if its complement was already seen
```

## Full Stack Integration Checklist
```
Backend:              Frontend:
Entity + JPA        | Signal-based state
Service + @Tx       | OnPush components
REST Controller     | Typed interfaces
DTOs + Validation   | Error handling
Exception Handler   | Loading indicators
Repository          | Pagination
Unit Tests          | Route guards
Integration Tests   | HTTP interceptors
```
""",
"mcqs": [
  {"id":"d86q1","prompt":"What does `cascade = CascadeType.ALL` with `orphanRemoval = true` do in JPA?","options":["Only cascades deletes","CascadeType.ALL: all operations (persist, merge, remove, refresh, detach) cascade to child entities. orphanRemoval: when an item is removed from the items list, it's automatically deleted from the DB — no explicit delete call needed","orphanRemoval prevents deletions","CASCADE requires @OneToMany"],"correctAnswer":"CascadeType.ALL: all operations (persist, merge, remove, refresh, detach) cascade to child entities. orphanRemoval: when an item is removed from the items list, it's automatically deleted from the DB — no explicit delete call needed","explanation":"Without orphanRemoval: remove item from list → item stays in DB (orphaned). With orphanRemoval: remove from Java list → JPA deletes from DB. CascadeType.ALL with orphanRemoval: the collection is fully managed — add, update, remove all work through the parent."},
  {"id":"d86q2","prompt":"What is `ApplicationEventPublisher` used for in Spring?","options":["HTTP event publishing","Decoupled event-driven communication — publish domain events (OrderCreatedEvent) from the service. Listeners (@EventListener) in other services react independently. Prevents tight service coupling","EventPublisher is for logging","Replaces @Autowired"],"correctAnswer":"Decoupled event-driven communication — publish domain events (OrderCreatedEvent) from the service. Listeners (@EventListener) in other services react independently. Prevents tight service coupling","explanation":"OrderService.createOrder() → events.publishEvent(new OrderCreatedEvent(id)). EmailService @EventListener(OrderCreatedEvent): sends confirmation email. InventoryService listens: deducts stock. Loose coupling: OrderService doesn't know about EmailService or InventoryService."},
  {"id":"d86q3","prompt":"What does `@PrePersist` and `@PreUpdate` do in JPA?","options":["Database triggers","JPA lifecycle callbacks — @PrePersist: runs before INSERT. @PreUpdate: runs before UPDATE. Used for: setting createdAt/updatedAt timestamps, validation, audit fields — without external infrastructure","@PrePersist is synchronous","Requires AuditorAware"],"correctAnswer":"JPA lifecycle callbacks — @PrePersist: runs before INSERT. @PreUpdate: runs before UPDATE. Used for: setting createdAt/updatedAt timestamps, validation, audit fields — without external infrastructure","explanation":"Entity-level callbacks: method annotated with @PrePersist runs inside the JPA/Hibernate layer before writing to DB. @CreationTimestamp/@UpdateTimestamp (Hibernate annotations) do the same thing but are Hibernate-specific. @PrePersist/@PreUpdate are JPA standard."},
  {"id":"d86q4","prompt":"Why use `signal.update(orders => orders.map(...))` instead of direct mutation?","options":["API requirement","Immutable update triggers change detection in Angular signals and OnPush components. Mutating the existing array (push/splice) doesn't change the reference — Angular doesn't detect the change. Spread/map creates new reference","signals detect mutations","map() is faster than push"],"correctAnswer":"Immutable update triggers change detection in Angular signals and OnPush components. Mutating the existing array (push/splice) doesn't change the reference — Angular doesn't detect the change. Spread/map creates new reference","explanation":"signal.update(arr => arr.map(o => o.id === id ? updated : o)): creates new array → signal detects change → template updates. signal.update(arr => { arr[0] = updated; return arr; }): same reference → no update detected."},
  {"id":"d86q5","prompt":"What is Two Sum and why does HashMap make it O(n)?","options":["Sort then binary search","Store each number's index in a HashMap. For each number, check if its complement (target - num) was already stored. O(1) lookup per element → O(n) total. Brute force: O(n²) nested loops","Sort + two pointers: O(n log n)","Two Sum requires a sorted array"],"correctAnswer":"Store each number's index in a HashMap. For each number, check if its complement (target - num) was already stored. O(1) lookup per element → O(n) total. Brute force: O(n²) nested loops","explanation":"Process nums[i]: complement = target - nums[i]. If complement in seen: found. Else: add nums[i]→i to seen. One pass, O(1) HashMap lookup per step → O(n). Classic example of space-time tradeoff."},
  {"id":"d86q6","prompt":"What is the role of DTOs (Data Transfer Objects) vs JPA Entities?","options":["Identical","Entities: database mapping, may contain lazy-loaded relationships, internal state. DTOs: API contract, only expose needed fields, serializable without lazy-load issues, prevent accidental data exposure","DTOs replace Entities","Use Entities for REST APIs"],"correctAnswer":"Entities: database mapping, may contain lazy-loaded relationships, internal state. DTOs: API contract, only expose needed fields, serializable without lazy-load issues, prevent accidental data exposure","explanation":"Entity to REST: Jackson serializes all fields including passwords, internal fields. DTO: explicit fields only. Lazy relationships: entity.getItems() → LazyInitializationException outside transaction. DTO: already loaded and mapped."},
  {"id":"d86q7","prompt":"What does `finalize(() => this.loading.set(false))` do in the Angular component?","options":["Finalizes the component","Ensures loading is set to false whether the HTTP request succeeds OR fails — prevents a stuck loading spinner. RxJS finalize runs when an Observable terminates for any reason","finalize replaces complete","Same as tap"],"correctAnswer":"Ensures loading is set to false whether the HTTP request succeeds OR fails — prevents a stuck loading spinner. RxJS finalize runs when an Observable terminates for any reason","explanation":"Without finalize: error → catchError → loading never set to false → spinner stays forever. With finalize: guaranteed cleanup. Like try/finally: always runs. Essential for loading/spinner state management."},
  {"id":"d86q8","prompt":"What is `@ResponseStatus(HttpStatus.CREATED)` on a controller method?","options":["Creates a new HTTP connection","Sets the HTTP response status to 201 Created instead of the default 200 OK — appropriate for POST endpoints that create new resources. Can also be used on exception classes to set specific error status codes","Only works with POST","CREATED is 202"],"correctAnswer":"Sets the HTTP response status to 201 Created instead of the default 200 OK — appropriate for POST endpoints that create new resources. Can also be used on exception classes to set specific error status codes","explanation":"REST conventions: 201 Created + Location header for successful resource creation. @ResponseStatus(HttpStatus.CREATED): Spring automatically returns 201. Return ResponseEntity.created(uri).body(dto) for explicit Location header."},
  {"id":"d86q9","prompt":"How does `@Valid` work with a custom ConstraintValidator on a DTO?","options":["Validates HTML only","@Valid triggers Bean Validation on the annotated parameter. Spring calls all ConstraintValidators on the object and its fields. If violations found: MethodArgumentNotValidException → 400 Bad Request with field error details","@Valid is for forms only","Requires a database call"],"correctAnswer":"@Valid triggers Bean Validation on the annotated parameter. Spring calls all ConstraintValidators on the object and its fields. If violations found: MethodArgumentNotValidException → 400 Bad Request with field error details","explanation":"@PostMapping createOrder(@Valid @RequestBody CreateOrderRequest req): Spring validates req before calling the method. Custom validator: @NoFutureDate on a field. Validation fails → 400 before service is called."},
  {"id":"d86q10","prompt":"What is the integration between `Page<T>` from Spring Data and Angular pagination?","options":["No standard integration","Spring Data Page<T> returns JSON: {content:[], totalElements:N, totalPages:M, number:P, size:S}. Angular types this as Page<OrderDto> interface. Component reads totalElements for paginator, content for list, number for current page","Page<T> is Spring-only","Angular handles pagination server-side"],"correctAnswer":"Spring Data Page<T> returns JSON: {content:[], totalElements:N, totalPages:M, number:P, size:S}. Angular types this as Page<OrderDto> interface. Component reads totalElements for paginator, content for list, number for current page","explanation":"PageRequest.of(page, size): Spring builds paginated query. Response: standard Page JSON structure. Angular: getOrders({page:0, size:20}): Observable<Page<OrderDto>>. Template: orders() = response.content; total() = response.totalElements."}
],
"writtenConceptQuestions": [
  "Build the Order entity with JPA relationships, lifecycle callbacks, and status enum.",
  "Show the complete create-order flow: Controller → @Valid → Service → Repository → Event.",
  "Implement the Angular OrderListComponent with signals, OnPush, loading state, and pagination.",
  "Solve Two Sum. Show why HashMap gives O(n) vs brute force O(n²).",
  "Explain the DTO pattern. Show OrderDto mapping from Order entity with MapStruct or manual mapper.",
  "Show ApplicationEventPublisher for decoupled order events. Show an @EventListener in EmailService.",
  "Show finalize() in Angular HTTP service call and explain why it's needed for loading state."
],
"businessScenarios": [
  "Build an end-to-end Create Order feature: Spring Boot REST endpoint with @Valid, service layer with transaction, and Angular reactive form submitting to it.",
  "Order items are orphaned in the database when removed from an order. Add orphanRemoval=true and cascade to fix.",
  "Two different Angular components need to show order count and order list. Centralise with OrderStateService using signals."
]
},

"day-087": {
"notes": """# Resume Questions: Technical Interview Deep Dive

## How to Talk About Your Projects

### STAR Framework for Technical Questions
```
S — Situation:   The context and challenge
T — Task:        What you were responsible for
A — Action:      The specific technical steps you took
R — Result:      Measurable outcome (performance, reliability, user impact)
```

### Sample: "Tell me about a challenging technical problem you solved"
```
Situation: Our product catalog API was responding in 4-5 seconds — unacceptable for users.

Task: I was responsible for identifying the bottleneck and reducing response time to under 500ms.

Action:
1. Used EXPLAIN ANALYZE to find 47 queries per request (N+1 problem from lazy loading)
2. Added @EntityGraph to load product + category + images in 1 query
3. Added a composite index on (category_id, status, created_at) — query went from Seq Scan to Index Scan
4. Added Redis caching for the category tree (rarely changes)
5. Added database connection pooling (HikariCP) — was using default pool of 10, increased to 50

Result: Response time dropped from 4.8s to 180ms. Load test showed 10x throughput improvement.
DB queries per request: 47 → 1. Cache hit rate: 85%.
```

## Spring Boot Interview Talking Points
```java
// "How does Spring Boot auto-configuration work?"
// 1. @EnableAutoConfiguration reads spring.factories / AutoConfiguration.imports
// 2. Each auto-config class has @Conditional annotations
// 3. If conditions pass (class on classpath, property set, no bean defined): configure
// Example: If spring.datasource.url set AND HikariCP on classpath:
//          → HikariCP DataSource bean auto-created

// "Explain your security implementation"
// JWT-based stateless authentication:
// 1. POST /auth/login → validate credentials → return JWT (access) + refresh token
// 2. Every request: JwtFilter validates token → sets SecurityContextHolder
// 3. @PreAuthorize("hasRole('ADMIN')") — method-level authorization
// 4. Token expiry: access 15min, refresh 7days
// 5. Refresh: POST /auth/refresh → new access token
```

## Angular Interview Talking Points
```typescript
// "How do you handle state in Angular?"
// Simple state: signal-based service
// Complex/shared: NgRx for large teams needing strict conventions
// Real-time: WebSocket + RxJS Subject → components subscribe

// "How do you optimize Angular performance?"
// OnPush: 80% reduction in CD checks
// Lazy loading: initial bundle from 2MB → 400KB
// @defer for below-fold content
// Virtual scrolling for large lists
// trackBy in @for to prevent DOM node recreation
// async pipe over manual subscribe (no memory leaks)

// "How do you handle HTTP errors?"
// Global interceptor: 401 → logout, 403 → forbidden page
// Service level: catchError with EMPTY or of(default)
// Component: error signal for user-facing messages
```

## DSA Topic: Best Time to Buy and Sell Stock (Greedy)
```java
// LeetCode 121 — one transaction, maximize profit
public int maxProfit(int[] prices) {
    int minPrice = Integer.MAX_VALUE, maxProfit = 0;

    for (int price : prices) {
        if (price < minPrice) {
            minPrice = price;       // update lowest buy price seen
        } else if (price - minPrice > maxProfit) {
            maxProfit = price - minPrice;  // best profit from current min
        }
    }
    return maxProfit;
}
// Time: O(n), Space: O(1)
// Greedy: track the minimum price seen so far, compute max profit at each step
```

## Behavioral Technical Questions
```
"What technical decision are you most proud of?"
→ The decision to migrate from NgModule to standalone components early.
  At first the team resisted the change. I wrote an RFC showing the 30% bundle reduction
  and simplified testing. After a proof-of-concept, the team agreed.
  Result: onboarding time for new Angular developers reduced by 40%.

"Tell me about a time you improved performance."
→ Use the N+1 story above with concrete numbers.

"Describe your testing strategy."
→ Unit tests for services (Mockito), controller slice tests (@WebMvcTest),
  repository tests (@DataJpaTest with H2), E2E with Cypress.
  Target: 80% coverage on critical paths, 100% on financial calculations.

"How do you stay current with Java/Angular?"
→ Follow Angular blog, Spring releases. Built side projects with Angular 17 signals
  and Java 21 virtual threads. Subscribe to Baeldung, InfoQ.
```

## Common Resume Question Mistakes
1. **Vague answers:** "I improved performance" → say HOW MUCH (numbers).
2. **Technology laundry list:** saying you know 20 technologies without depth.
3. **No business impact:** always connect technical work to business outcome.
4. **Blaming teammates:** talk about challenges in terms of problems solved, not people.
""",
"mcqs": [
  {"id":"d87q1","prompt":"What does the STAR framework stand for in behavioral interviews?","options":["Skills, Tasks, Actions, Results","Situation, Task, Action, Result — a structured way to answer behavioral questions: describe the context, what you were responsible for, the specific steps you took, and measurable outcomes","Strategy, Tactics, Approach, Review","Status, Timeline, Achievement, Review"],"correctAnswer":"Situation, Task, Action, Result — a structured way to answer behavioral questions: describe the context, what you were responsible for, the specific steps you took, and measurable outcomes","explanation":"STAR makes answers concrete and measurable. Without STAR: 'I improved performance' (vague). With STAR: Situation (4.8s response time), Task (reduce to 500ms), Action (EntityGraph, index, caching), Result (180ms, 10x throughput). Numbers make it memorable."},
  {"id":"d87q2","prompt":"What is the Best Time to Buy and Sell Stock algorithm?","options":["Use DP with 2D array","Track minimum price seen so far. For each price, compute profit = price - minPrice. Update maxProfit if higher. One pass O(n), O(1) space. Greedy: at each point, best profit uses the lowest price seen before current","Sort prices first","Use sliding window"],"correctAnswer":"Track minimum price seen so far. For each price, compute profit = price - minPrice. Update maxProfit if higher. One pass O(n), O(1) space. Greedy: at each point, best profit uses the lowest price seen before current","explanation":"minPrice: lowest buy price available. At each day: max we could make = price - minPrice. Update maxProfit if better. Never sell before buy: only update minPrice on days before we'd sell. [7,1,5,3,6,4] → minPrice=1, maxProfit=5."},
  {"id":"d87q3","prompt":"How should you quantify performance improvements in interviews?","options":["Say it was much better","Use specific metrics: response time (ms), throughput (req/sec), query count, cache hit rate, bundle size (KB), test coverage (%). Interviewers remember 'from 4.8s to 180ms' — they forget 'I made it faster'","Mention the tools used","Focus on code quality"],"correctAnswer":"Use specific metrics: response time (ms), throughput (req/sec), query count, cache hit rate, bundle size (KB), test coverage (%). Interviewers remember 'from 4.8s to 180ms' — they forget 'I made it faster'","explanation":"Strong answer: 'Reduced DB queries from 47 to 1 using EntityGraph, added composite index, implemented Redis cache — response time dropped from 4.8s to 180ms, 10x throughput'. Weak: 'Fixed the N+1 problem and added caching'."},
  {"id":"d87q4","prompt":"How should you explain your Spring Security JWT implementation in an interview?","options":["Mention that you used it","Walk through the flow: 1) Login → validate → issue JWT, 2) Every request → JwtFilter parses token → set SecurityContext, 3) @PreAuthorize for method authorization, 4) Token rotation: 15min access + 7d refresh, 5) Interceptor for 401 handling","Say JWT is stateless","Mention the library only"],"correctAnswer":"Walk through the flow: 1) Login → validate → issue JWT, 2) Every request → JwtFilter parses token → set SecurityContext, 3) @PreAuthorize for method authorization, 4) Token rotation: 15min access + 7d refresh, 5) Interceptor for 401 handling","explanation":"Interviewers want to know you understand the full flow, not just that you used JWT. Show: filter chain, token validation, refresh mechanism, revocation strategy. Bonus: mention security considerations (httpOnly cookies, CSRF, token storage)."},
  {"id":"d87q5","prompt":"What is the key mistake when describing technical decisions in interviews?","options":["Mentioning too many tools","Not connecting technical choices to business impact. 'I used OnPush change detection' is less compelling than 'OnPush reduced the change detection overhead by 80%, letting us handle 5x more concurrent users without scaling up servers'","Being too detailed","Avoiding numbers"],"correctAnswer":"Not connecting technical choices to business impact. 'I used OnPush change detection' is less compelling than 'OnPush reduced the change detection overhead by 80%, letting us handle 5x more concurrent users without scaling up servers'","explanation":"Every technical decision answers a business need. Ask: why did this matter? How did it affect users/revenue/reliability? 'Lazy loading reduced initial bundle by 70%' → 'page load time < 2s → 15% improvement in user retention'."},
  {"id":"d87q6","prompt":"How do you explain Angular state management in an interview?","options":["Say you used NgRx","Explain the decision: for simple shared state → signal-based service (less boilerplate). For complex async flows and large teams → NgRx (strict conventions, time-travel debug). Show you understand trade-offs, not just the tool","Mention Redux principles","Angular has built-in state"],"correctAnswer":"Explain the decision: for simple shared state → signal-based service (less boilerplate). For complex async flows and large teams → NgRx (strict conventions, time-travel debug). Show you understand trade-offs, not just the tool","explanation":"Strong answer: 'We evaluated NgRx vs signal services. For our 3-person team with straightforward CRUD state, NgRx overhead wasn't justified. We used signal-based services — 60% less boilerplate than NgRx, easier onboarding.'"},
  {"id":"d87q7","prompt":"What numbers should you memorize about your Angular app's performance?","options":["Lines of code","Initial bundle size (before/after lazy loading), LCP time, number of components with OnPush, test coverage %, lighthouse score, number of lazy-loaded routes. These make answers concrete and memorable","Component count","Dependency versions"],"correctAnswer":"Initial bundle size (before/after lazy loading), LCP time, number of components with OnPush, test coverage %, lighthouse score, number of lazy-loaded routes. These make answers concrete and memorable","explanation":"'Our initial bundle was 1.8MB. I added lazy loading for 4 feature routes and @defer for below-fold content — bundle dropped to 380KB, LCP improved from 3.2s to 1.1s.' This tells a complete performance story."},
  {"id":"d87q8","prompt":"How do you handle 'What is your weakness?' in a technical interview?","options":["Say you have no weaknesses","Choose a genuine technical area you're improving, describe what you're doing to address it, and show evidence of growth. 'I was less experienced in Kubernetes. I took a CKA prep course, deployed our staging environment using Helm charts, reduced deployment time by 40%.'","Say you work too hard","Mention a strength disguised as weakness"],"correctAnswer":"Choose a genuine technical area you're improving, describe what you're doing to address it, and show evidence of growth. 'I was less experienced in Kubernetes. I took a CKA prep course, deployed our staging environment using Helm charts, reduced deployment time by 40%.'","explanation":"Authentic + growth-oriented wins. Interviewers disrespect 'I'm a perfectionist' non-answers. A real weakness with a clear improvement plan shows self-awareness and initiative — both valued engineering traits."},
  {"id":"d87q9","prompt":"How should you explain handling a production incident in an interview?","options":["Say it never happened","Focus on: how quickly you detected it (monitoring/alerting), how you diagnosed it (logs, metrics, EXPLAIN ANALYZE), what you did to fix it (immediate mitigation, root cause fix), and what you did to prevent recurrence (test, alert, documentation)","Minimize the impact","Blame the team"],"correctAnswer":"Focus on: how quickly you detected it (monitoring/alerting), how you diagnosed it (logs, metrics, EXPLAIN ANALYZE), what you did to fix it (immediate mitigation, root cause fix), and what you did to prevent recurrence (test, alert, documentation)","explanation":"Incidents show how you perform under pressure. Strong: 'Alert fired at 2am, P99 latency spike. I queried slow_query_log, found a missing index on orders table after a migration. Hotfix in 20min. Added query performance tests to CI to prevent recurrence.'"},
  {"id":"d87q10","prompt":"What does 'tell me about a time you disagreed with a technical decision' test?","options":["How argumentative you are","Communication and influence skills — can you make a case with evidence (benchmark, RFC, POC) and influence without authority? Can you implement a decision you disagreed with gracefully? Interviewers want professional, constructive disagreement","Technical knowledge only","Whether you follow orders"],"correctAnswer":"Communication and influence skills — can you make a case with evidence (benchmark, RFC, POC) and influence without authority? Can you implement a decision you disagreed with gracefully? Interviewers want professional, constructive disagreement","explanation":"Strong answer: 'I thought we should use WebSockets for real-time updates vs polling. I built a POC showing 80% less server load with WebSockets. Shared the benchmark with the team. Lead agreed. Implemented it — polling dropped from 5k req/min to near zero.'"}
],
"writtenConceptQuestions": [
  "Write a STAR-format answer for 'Tell me about a performance problem you solved' using the N+1 scenario.",
  "Solve Best Time to Buy and Sell Stock. Trace on [7,1,5,3,6,4]. Explain the greedy insight.",
  "Describe your Spring Security JWT implementation in 5 bullet points as you would in an interview.",
  "How would you explain Angular OnPush change detection and its business impact to a non-technical interviewer?",
  "Write a STAR answer for 'Tell me about a time you improved a process' in the context of testing.",
  "How do you discuss a project where requirements changed mid-way? Show STAR format.",
  "Describe your state management approach in Angular: when signals, when NgRx."
],
"businessScenarios": [
  "Prepare a 2-minute technical walkthrough of your capstone project covering: tech stack choice, key technical challenge, how you solved it, and measurable results.",
  "Prepare for: 'Your Spring Boot API is getting 1000 req/sec and p99 latency is 5s. How do you diagnose and fix it?' Walk through tools, steps, and potential solutions.",
  "Prepare for a system design question: 'Design a notification system that sends email/SMS/push when an order status changes.' Cover Spring events, message queues, retry logic, and Angular real-time updates."
]
},

"day-088": {
"notes": """# Behavioral Questions: Engineering Culture and Collaboration

## Core Behavioral Competencies Tested
```
Competency              | Sample Question
------------------------|-------------------------------------------
Ownership               | Tell me about a time you took initiative
Collaboration           | How do you work with difficult teammates?
Technical communication | How do you explain complex topics to non-tech?
Learning agility        | How do you learn new technologies quickly?
Conflict resolution     | Tell me about a disagreement with your team lead
Failure/growth          | Tell me about a project that failed
Customer focus          | How do you ensure your code meets user needs?
```

## Answering "Tell me about a failure"
```
WRONG: "I've never really failed on a project."
WRONG: "We missed a deadline because of unclear requirements."

CORRECT STRUCTURE:
Situation: We deployed a database migration without a rollback plan.
           The migration had a bug that corrupted order totals for 3 hours.

Task: I was the engineer who wrote and deployed the migration.
      I had to resolve the production incident and prevent recurrence.

Action:
1. Immediately rolled back using a backup (learned: always test rollback)
2. Wrote a post-mortem (blameless): root causes were no migration dry run,
   no data validation tests, no rollback script prepared
3. Introduced: migration testing in CI with production-like data,
   mandatory rollback scripts, staging validation step

Result: Zero migration-related incidents in the following 18 months.
        This process became the team standard.

Key: Own it. Show learning. Show systemic fix. Don't blame others.
```

## Engineering Collaboration Scenarios
```
"How do you handle disagreements with code reviews?"
→ "I try to understand the reviewer's concern first. If I disagree,
   I propose alternatives with reasoning — not just 'I prefer this.'
   If still disagreed: agree to consistent team standard, move on.
   I've learned most reviewers have good points I initially missed."

"How do you work with a teammate whose code quality is poor?"
→ "I start with pair programming — it's less threatening than criticism.
   I also contribute useful PR templates and linting configs so
   the standard is clear. If the issue persists, I'd have a direct
   but constructive conversation, focusing on the code, not the person."

"How do you balance technical debt vs feature delivery?"
→ "I track tech debt in the backlog with impact estimates.
   For each sprint, I advocate for 20% of capacity for debt reduction.
   For urgent features: negotiate scope — reduce feature to MVP now,
   refactor after. I've found showing measurable debt cost (e.g.,
   'this module causes 30% of bug reports') gets stakeholder buy-in."
```

## DSA Topic: Contains Duplicate (HashSet)
```java
// LeetCode 217 — O(n) with HashSet
public boolean containsDuplicate(int[] nums) {
    Set<Integer> seen = new HashSet<>();
    for (int num : nums) {
        if (!seen.add(num)) return true;  // add() returns false if already present
    }
    return false;
}
// Time: O(n), Space: O(n)
// Note: Set.add() returns false when element already exists — elegant
```

## Questions to Ask the Interviewer
```
Technical depth:
- "What does the deployment pipeline look like for a typical feature?"
- "How do you handle database migrations in production?"
- "What is the current test coverage target and testing strategy?"

Team culture:
- "How does the team handle technical debt?"
- "What does a typical sprint look like — how is work prioritized?"
- "What has the team's biggest technical challenge been this year?"

Growth:
- "What would success look like for this role in 6 months?"
- "How does the company support continuous learning?"
- "What is the career growth path for engineers here?"
```

## Red Flags in Answers to Avoid
```
- "I work best alone" → signals poor collaboration
- "My previous company did everything wrong" → signals blame culture
- "I don't really have failures" → signals lack of self-awareness
- "I just did what was assigned" → signals no ownership
- "I'm not sure about that technology" (without showing curiosity) → signals fixed mindset
```

## Common Mistakes
1. **Not preparing 5-7 STAR stories:** behavioral questions are predictable — prepare them.
2. **Stories without technical detail:** for engineering roles, include the technical content.
3. **Not asking questions:** "I have no questions" signals low engagement.
""",
"mcqs": [
  {"id":"d88q1","prompt":"What does the STAR format help you avoid in behavioral answers?","options":["Technical jargon","Vague, unstructured answers like 'I worked on a project once and it went well.' STAR forces specificity: what was the context, your role, your actions, and measurable results","Long answers","Emotional responses"],"correctAnswer":"Vague, unstructured answers like 'I worked on a project once and it went well.' STAR forces specificity: what was the context, your role, your actions, and measurable results","explanation":"Interviewers have limited time. STAR: crisp, memorable, comparable across candidates. Without STAR: interviewer doesn't know if you individually solved it or were a bystander. STAR shows YOUR specific contribution."},
  {"id":"d88q2","prompt":"What does HashSet.add() return and how does it simplify Contains Duplicate?","options":["Returns the element","Returns true if the element was newly added, false if it already existed. containsDuplicate: if (!seen.add(num)) return true — one line elegantly combines the contains check and insert","Returns the set size","add() always returns true"],"correctAnswer":"Returns true if the element was newly added, false if it already existed. containsDuplicate: if (!seen.add(num)) return true — one line elegantly combines the contains check and insert","explanation":"Without this: if (seen.contains(num)) return true; seen.add(num). With add() return value: if (!seen.add(num)) return true. Cleaner, fewer operations. HashSet uses HashMap internally — O(1) average for add and contains."},
  {"id":"d88q3","prompt":"How should you answer 'Tell me about a failure'?","options":["Deny any failure","Own the failure, describe specifically what went wrong, what YOU did to fix it, and what systemic change you made to prevent recurrence. Show growth mindset and no blame of others","Describe a minor mistake","Blame external factors"],"correctAnswer":"Own the failure, describe specifically what went wrong, what YOU did to fix it, and what systemic change you made to prevent recurrence. Show growth mindset and no blame of others","explanation":"Best failure answers: specific (not vague), owned (not blamed), actionable (you fixed it), systemic (you prevented recurrence). 'I deployed a bad migration, here's what I learned and the process I introduced' shows maturity."},
  {"id":"d88q4","prompt":"What should you NEVER say when asked about handling a difficult teammate?","options":["Talk about process","'They were incompetent' or 'I just avoided them.' This signals inability to collaborate, no empathy, no conflict resolution skills. Instead: describe what you did to understand their perspective and improve the situation","Mention specific facts","Describe your actions"],"correctAnswer":"'They were incompetent' or 'I just avoided them.' This signals inability to collaborate, no empathy, no conflict resolution skills. Instead: describe what you did to understand their perspective and improve the situation","explanation":"Engineering is collaborative. 'Difficult teammate' question tests: do you blame, avoid, or solve? Good engineers solve: pair programming, clear standards, direct conversations, escalation as last resort."},
  {"id":"d88q5","prompt":"Why is asking questions at the end of an interview important?","options":["Mandatory etiquette","Shows genuine interest in the role and company, helps you evaluate if this is a good fit for you, and demonstrates research and critical thinking. Not asking signals disengagement or that you'd accept any offer","Questions extend the interview","Only senior candidates ask"],"correctAnswer":"Shows genuine interest in the role and company, helps you evaluate if this is a good fit for you, and demonstrates research and critical thinking. Not asking signals disengagement or that you'd accept any offer","explanation":"Good questions: about deployment process (shows DevOps interest), tech debt handling (shows engineering maturity), success in 6 months (shows goal orientation). Bad questions: salary, benefits before offer, 'can I work from home always?'"},
  {"id":"d88q6","prompt":"How do you answer 'How do you balance technical debt vs feature delivery?'","options":["Always choose features","Show structured thinking: track debt with impact estimates, advocate for regular capacity (20% per sprint), use data to justify refactoring (module X causes 30% of bugs). Shows you understand both business AND technical concerns","Always choose technical debt","Avoid the question"],"correctAnswer":"Show structured thinking: track debt with impact estimates, advocate for regular capacity (20% per sprint), use data to justify refactoring (module X causes 30% of bugs). Shows you understand both business AND technical concerns","explanation":"Engineers who always say 'features' have no craft. Engineers who always say 'tech debt' have no business sense. Best: 'I track debt, quantify impact, negotiate capacity. For urgent features: MVP now, refactor after with data to justify it.'"},
  {"id":"d88q7","prompt":"What does 'ownership' mean as an engineering competency?","options":["Owning the code","Proactively identifying and fixing problems beyond your assigned tasks, taking responsibility for outcomes (not just activities), following through without being reminded, treating the product as if you're responsible for its success","Only doing assigned work","Having a specific domain"],"correctAnswer":"Proactively identifying and fixing problems beyond your assigned tasks, taking responsibility for outcomes (not just activities), following through without being reminded, treating the product as if you're responsible for its success","explanation":"Amazon LP: Ownership. Evidence: 'I noticed our API had no request rate limiting. I researched options, wrote a proposal, implemented Spring rate limiting middleware — reduced abuse incidents by 90%.' Not asked, just did it."},
  {"id":"d88q8","prompt":"How should you answer 'How do you learn new technologies quickly?'","options":["Say you google things","Describe your learning system: official docs + build something small, identify the mental model (how this technology thinks), find the gaps by comparing to something you know, then teach/write about it to solidify. Give an example with timeline","Say you take courses","Mention YouTube"],"correctAnswer":"Describe your learning system: official docs + build something small, identify the mental model (how this technology thinks), find the gaps by comparing to something you know, then teach/write about it to solidify. Give an example with timeline","explanation":"Strong answer: 'When Angular signals came out, I read the RFC, built a small app over a weekend to replace BehaviorSubject, identified 3 patterns where signals are better. Shared a team presentation. Within 2 weeks I was productive.'"},
  {"id":"d88q9","prompt":"Why should behavioral stories include technical details for engineering roles?","options":["Makes you sound smarter","Technical interviewers need to verify you actually did the technical work. 'I optimized the database' is weaker than 'I added a composite index on (customer_id, status) after EXPLAIN ANALYZE showed Seq Scan on 5M rows — p99 dropped from 4s to 180ms'","Technical details are optional","Non-technical interviewers prefer stories"],"correctAnswer":"Technical interviewers need to verify you actually did the technical work. 'I optimized the database' is weaker than 'I added a composite index on (customer_id, status) after EXPLAIN ANALYZE showed Seq Scan on 5M rows — p99 dropped from 4s to 180ms'","explanation":"Generic: could be anyone. Specific: only someone who did the work knows these details. Technical depth in behavioral stories: proves you have hands-on experience, not just managed others who did the work."},
  {"id":"d88q10","prompt":"What is a 'blameless post-mortem' and why is it valued in engineering culture?","options":["Ignoring mistakes","A structured incident review that focuses on systemic failures and process improvements rather than individual blame. Goal: learn and prevent recurrence, not punish. 'The system made the mistake easy to make' vs 'John made a mistake'","Post-mortems assign responsibility","Required only for major outages"],"correctAnswer":"A structured incident review that focuses on systemic failures and process improvements rather than individual blame. Goal: learn and prevent recurrence, not punish. 'The system made the mistake easy to make' vs 'John made a mistake'","explanation":"Blameless culture: engineers speak openly about mistakes (no fear of punishment). Result: better learning, faster improvement, fewer recurring incidents. Companies with blame culture: engineers hide mistakes → problems compound. Google, Netflix, Etsy popularized blameless post-mortems."}
],
"writtenConceptQuestions": [
  "Write a complete STAR story for a production incident you resolved. Include technical detail and systemic prevention.",
  "Solve Contains Duplicate using HashSet.add() return value. Show O(n) solution and explain why sorting approach is O(n log n).",
  "Prepare 5 questions to ask at the end of a backend engineering interview. Explain what each question signals.",
  "Write a STAR answer for 'Tell me about a time you handled conflict in a code review.'",
  "How do you explain your testing strategy in a behavioral interview? Include coverage targets and testing types.",
  "Write a STAR answer for 'Tell me about a time you had to learn a new technology quickly.'",
  "Describe your approach to technical debt in a behavioral format. Show how you'd justify it to a product manager."
],
"businessScenarios": [
  "Prepare for 'Walk me through your most complex Spring Boot feature.' Write a 3-minute technical narrative covering architecture decisions, challenges, and results.",
  "Prepare for 'Tell me about a time you improved your team's engineering practices.' STAR the introduction of code review standards, CI/CD, or test coverage.",
  "Prepare for 'How do you ensure API quality?' Cover: @Valid input validation, error handling, HTTP status codes, API documentation, contract tests."
]
},

"day-089": {
"notes": """# System Design Basics: Scalability, Caching, and Distributed Systems

## System Design Framework
```
Step 1: Clarify Requirements (5 min)
  - Scale: users, requests/sec, data volume
  - Features: core flows, edge cases
  - Non-functional: latency, availability, consistency

Step 2: Estimate Scale (2 min)
  - 10M users → ~100 DAU → ~100 req/sec (typical)
  - 1M orders/day → ~12 writes/sec
  - 1KB per record × 1M records = 1GB (for indexes etc × 10)

Step 3: High-Level Design (10 min)
  - Client → Load Balancer → API Servers → Database
  - Add: Cache, Message Queue, CDN

Step 4: Deep Dive Key Components (15 min)
  - Database schema, indexing strategy
  - Cache eviction, invalidation
  - API design

Step 5: Identify Bottlenecks (5 min)
  - Single points of failure
  - Scaling strategy
```

## Caching Strategies
```
Cache-Aside (Lazy Loading):
  1. App checks cache
  2. Cache miss → query DB → store in cache → return
  3. Cache hit → return
  Pros: only caches what's actually requested
  Cons: first request always hits DB (cold start)

Write-Through:
  1. Write to cache AND DB simultaneously
  Pros: cache always fresh
  Cons: every write hits cache (even uncached data)

Write-Behind (Write-Back):
  1. Write to cache immediately → return
  2. Async: flush cache → DB
  Pros: fast writes
  Cons: data loss risk if cache fails before flush

Read-Through:
  1. App asks cache for data
  2. Cache handles DB lookup on miss (not app)
  Pros: cache is the only data source for app
  Cons: cold start latency

Eviction Policies:
  LRU (Least Recently Used): evict what wasn't accessed recently
  LFU (Least Frequently Used): evict least accessed overall
  TTL: expire after time period (Redis default)
```

## Database Scaling Patterns
```
Vertical Scaling: bigger server (limit: one machine)
Horizontal Scaling: more servers (requires stateless apps)

Read Replicas:
  Primary: all writes
  Read replicas: all reads (90% of traffic)
  Spring: @Transactional(readOnly=true) → route to replica

Database Sharding:
  Shard by customer_id: all orders for customer on same shard
  Pros: distributes load
  Cons: cross-shard queries are expensive

Connection Pooling (HikariCP):
  Default: 10 connections per app instance
  High traffic: 50-100 connections
  Formula: threads × (Tc/Tq) where Tc=connection time, Tq=query time
```

## DSA Topic: Maximum Subarray — Kadane's Algorithm
```java
// LeetCode 53 — maximum sum contiguous subarray
public int maxSubArray(int[] nums) {
    int maxSum = nums[0], currentSum = nums[0];

    for (int i = 1; i < nums.length; i++) {
        // Either extend current subarray or start fresh
        currentSum = Math.max(nums[i], currentSum + nums[i]);
        maxSum = Math.max(maxSum, currentSum);
    }
    return maxSum;
}
// Time: O(n), Space: O(1)
// Key insight: if currentSum becomes negative, start fresh from current element
// Kadane's is DP: dp[i] = max subarray ending at i = max(nums[i], dp[i-1]+nums[i])
```

## Microservices vs Monolith
```
Monolith:
  + Simple deployment, transactions, debugging
  + Low latency (in-process calls)
  - Scaling: entire app scales, not just bottleneck
  - Team: all teams deploy together

Microservices:
  + Independent scaling, deployment, technology
  + Team autonomy
  - Distributed transactions (Saga pattern)
  - Network latency, partial failures
  - Operational complexity (k8s, service mesh)

Start monolith, extract services when: clear boundaries,
  team > 10, different scaling needs per component.
```

## Common System Design Questions
```
Design a URL shortener:
  - Hash function: MD5 first 6 chars of URL
  - Collision: increment + retry
  - DB: (short_code, original_url, created_at, expiry, click_count)
  - Cache: LRU cache of popular short codes
  - Scale: read-heavy → many read replicas, Redis cache

Design a rate limiter:
  - Token Bucket: bucket refills at rate R, requests consume 1 token
  - Sliding Window: count requests in last N seconds (Redis sorted set)
  - Redis + Lua script: atomic check-and-decrement

Design a notification system:
  - Producers: OrderService publishes to Kafka
  - Consumers: EmailService, SMSService, PushService
  - Retry: DLT for failed notifications
  - Template engine for email/SMS content
```

## Common Mistakes
1. **Jumping to solution without clarifying requirements:** ask about scale, features first.
2. **Over-engineering:** no need for microservices + Kafka + Elasticsearch for a simple CRUD app.
3. **Ignoring failures:** always discuss: what if the cache fails, the DB goes down, a service is slow.
""",
"mcqs": [
  {"id":"d89q1","prompt":"What is Kadane's Algorithm and what is the key decision at each step?","options":["Sort then sum","At each element: decide whether to extend the current subarray (currentSum + nums[i]) or start a new subarray from the current element (nums[i]). Take whichever is larger. Track overall maxSum. O(n), O(1)","Use sliding window","Binary search approach"],"correctAnswer":"At each element: decide whether to extend the current subarray (currentSum + nums[i]) or start a new subarray from the current element (nums[i]). Take whichever is larger. Track overall maxSum. O(n), O(1)","explanation":"currentSum = max(nums[i], currentSum + nums[i]): if extending makes it worse (currentSum negative), start fresh. maxSum tracks global best. DP framing: dp[i] = max subarray ending at i. [-2,1,-3,4,-1,2,1] → max=6 subarray [4,-1,2,1]."},
  {"id":"d89q2","prompt":"What is the Cache-Aside pattern and when does a cache miss occur?","options":["Cache always has data","Application checks cache first. Miss: query database, store result in cache, return. Hit: return cached value. Miss triggers DB query. First request after cache eviction always hits DB","Cache-aside uses write-through","Cache-aside prevents all DB queries"],"correctAnswer":"Application checks cache first. Miss: query database, store result in cache, return. Hit: return cached value. Miss triggers DB query. First request after cache eviction always hits DB","explanation":"Cache-Aside (Lazy Loading): cache only stores what's actually requested. Cold start: all misses. Warm: mostly hits. TTL expiry triggers miss. Most common pattern for read-heavy applications with Spring @Cacheable."},
  {"id":"d89q3","prompt":"What is database read replica and how does Spring Boot route to it?","options":["Backup database","A replica of the primary database that handles read queries. Primary: all writes. Replicas: all reads (typically 90% of traffic). Spring: @Transactional(readOnly=true) can be configured to route to replica datasource","Replicas are synchronized manually","Only for horizontal sharding"],"correctAnswer":"A replica of the primary database that handles read queries. Primary: all writes. Replicas: all reads (typically 90% of traffic). Spring: @Transactional(readOnly=true) can be configured to route to replica datasource","explanation":"AbstractRoutingDataSource: determines which datasource based on transaction context. readOnly=true → replicas. readOnly=false → primary. Reduces primary load significantly. Spring Boot + Hibernate: use LazyConnectionDataSourceProxy for deferred determination."},
  {"id":"d89q4","prompt":"What is the Token Bucket rate limiting algorithm?","options":["Store requests in a queue","Bucket holds max N tokens. Tokens refill at rate R/second. Each request consumes 1 token. If bucket empty: reject. Allows burst up to N, sustains at R/sec. Redis key = user_id, value = token count","Token Bucket uses a database","Rate limiting blocks all requests"],"correctAnswer":"Bucket holds max N tokens. Tokens refill at rate R/second. Each request consumes 1 token. If bucket empty: reject. Allows burst up to N, sustains at R/sec. Redis key = user_id, value = token count","explanation":"User with bucket of 100 tokens: can burst 100 requests immediately. Refill at 10/sec: sustained 10 req/sec. Excess: 429 Too Many Requests. Redis DECR + EXPIRE for atomic implementation."},
  {"id":"d89q5","prompt":"What is Write-Behind (Write-Back) caching and what is the risk?","options":["Write directly to DB","Write to cache immediately (fast), then asynchronously flush to database. Pros: very fast writes. Risk: if cache fails before flush, data is LOST — writes in cache not yet in DB","Write-behind is always safe","Same as write-through"],"correctAnswer":"Write immediately to cache, then asynchronously flush to database. Pros: very fast writes. Risk: if cache fails before flush, data is LOST — writes in cache not yet in DB","explanation":"Write-Through: cache + DB written together — safe but slower. Write-Behind: cache written first, DB async — fast but data loss risk. Use Write-Behind for non-critical, high-write data (analytics, counts). Not for orders, payments, financial data."},
  {"id":"d89q6","prompt":"When should you choose microservices over a monolith?","options":["Always for new projects","When team is large (>10 engineers), services have clearly different scaling needs, teams need independent deployment, or services use different technologies. For small teams: monolith first — lower complexity, easier debugging","Microservices are always better","When using Kubernetes"],"correctAnswer":"When team is large (>10 engineers), services have clearly different scaling needs, teams need independent deployment, or services use different technologies. For small teams: monolith first — lower complexity, easier debugging","explanation":"Premature microservices: distributed monolith (all services deployed together, tight coupling) + operational overhead. Monolith: single transaction, easy debugging, simple deployment. Extract service when: clear boundary, independent scaling need, team autonomy required."},
  {"id":"d89q7","prompt":"What is the first step in a system design interview?","options":["Start drawing the architecture","Clarify requirements: scale (users, requests/sec, data volume), core features, non-functional requirements (latency, availability, consistency). Without this: you might design a system for 100 users when they need 100M","Estimate capacity","Discuss database schema"],"correctAnswer":"Clarify requirements: scale (users, requests/sec, data volume), core features, non-functional requirements (latency, availability, consistency). Without this: you might design a system for 100 users when they need 100M","explanation":"'Design Twitter' is vague. Clarify: how many users? (500M). Read/write ratio? (90/10 — read heavy). Consistency requirements? (eventual is OK). Latency? (<500ms for timeline). Features? (just core: tweet, follow, timeline). Now design appropriately."},
  {"id":"d89q8","prompt":"What is database sharding and what is its main drawback?","options":["Encrypting the database","Horizontal partitioning — data split across multiple database instances by a shard key (e.g., customer_id). Each shard holds a subset of data. Drawback: cross-shard queries (JOIN across shards) are expensive and complex","Sharding eliminates indexes","Only for NoSQL databases"],"correctAnswer":"Horizontal partitioning — data split across multiple database instances by a shard key (e.g., customer_id). Each shard holds a subset of data. Drawback: cross-shard queries (JOIN across shards) are expensive and complex","explanation":"Shard by customer_id: all customer's orders on shard 1. Report across all customers: must query all shards, merge results. Re-sharding: notoriously difficult. Alternative: read replicas (simpler, handles 90% of scaling needs without sharding complexity)."},
  {"id":"d89q9","prompt":"What is the role of a message queue (Kafka/RabbitMQ) in system design?","options":["Stores messages permanently","Decouples producers from consumers — producer publishes event, multiple consumers process it independently. Benefits: async processing, retry on failure, handles traffic spikes (queue buffers), service isolation","Message queues replace REST APIs","Only for microservices"],"correctAnswer":"Decouples producers from consumers — producer publishes event, multiple consumers process it independently. Benefits: async processing, retry on failure, handles traffic spikes (queue buffers), service isolation","explanation":"Order created: OrderService publishes to Kafka. EmailService, InventoryService, AnalyticsService all consume independently. If email service is down: message waits in queue, processed when back up. Spike handling: queue absorbs burst, consumers process at their rate."},
  {"id":"d89q10","prompt":"What is HikariCP connection pooling and why does the default pool size of 10 matter?","options":["HikariCP encrypts connections","A high-performance JDBC connection pool — maintains a pool of DB connections ready to use. Default pool of 10: 11th concurrent DB request blocks. Under load: connection exhaustion → thread stalls → response time spikes. Tune based on DB capacity and concurrency","HikariCP is optional","Pool size doesn't affect performance"],"correctAnswer":"A high-performance JDBC connection pool — maintains a pool of DB connections ready to use. Default pool of 10: 11th concurrent DB request blocks. Under load: connection exhaustion → thread stalls → response time spikes. Tune based on DB capacity and concurrency","explanation":"Optimal pool size: (DB_CPU_cores × 2) + effective_spindle_count. Not more = DB overwhelmed; not less = thread starvation. Common mistake: default pool of 10 on a service handling 100 req/sec → each request holds a connection → queue depth grows → latency spikes."}
],
"writtenConceptQuestions": [
  "Walk through the system design framework for 'Design an Order Management System' (requirements, estimation, HLD, deep dive, bottlenecks).",
  "Solve Maximum Subarray with Kadane's algorithm. Trace on [-2,1,-3,4,-1,2,1,-5,4]. Show the DP connection.",
  "Compare Cache-Aside vs Write-Through vs Write-Behind. Show Spring @Cacheable as Cache-Aside.",
  "Design a rate limiter using Redis Token Bucket. Show the Redis operations needed.",
  "Explain database read replicas and sharding. When would you choose each?",
  "Compare monolith vs microservices architecture. When should you migrate?",
  "Design the notification system: Kafka producers, multiple consumers, retry with DLT."
],
"businessScenarios": [
  "Your order API is getting 500 req/sec with 10 DB connections — p99 latency is 8s. Design the caching + read replica strategy to handle the load.",
  "An OrderService, EmailService, and InventoryService are tightly coupled — all deploy together. Design the Kafka-based decoupling.",
  "A URL shortener needs to handle 10M redirects/day with <50ms latency. Design: storage, caching strategy, and scaling approach."
]
},

"day-090": {
"notes": """# Final Assessment: Full Stack Mastery Review

## Java + Spring Boot Mastery Checklist
```
Java Core:
  [x] Collections: HashMap, LinkedHashMap, TreeMap, ConcurrentHashMap
  [x] Streams: map, filter, collect, groupingBy, flatMap, reduce
  [x] Java 21: Records, Sealed Classes, Pattern Matching, Virtual Threads
  [x] Concurrency: synchronized, volatile, AtomicInteger, ExecutorService
  [x] Generics: bounded type parameters, wildcards, type erasure

Spring Boot:
  [x] Auto-configuration: @Conditional annotations, spring.factories
  [x] Bean scopes: singleton, prototype, request, session
  [x] @Transactional: propagation, isolation, rollback rules
  [x] JPA/Hibernate: entity lifecycle, lazy loading, N+1, EntityGraph
  [x] Security: SecurityFilterChain, JWT, JwtFilter, roles
  [x] Testing: @SpringBootTest, @WebMvcTest, @DataJpaTest, MockMvc
  [x] Exception handling: @RestControllerAdvice, ProblemDetail
```

## Angular Mastery Checklist
```
Core:
  [x] Standalone components, lifecycle hooks, @Input/@Output
  [x] Change detection: Default, OnPush, signals, zone-less
  [x] Reactive Forms: FormBuilder, FormGroup, validators, FormArray
  [x] HTTP: HttpClient, interceptors, error handling

Advanced:
  [x] RxJS: switchMap, mergeMap, exhaustMap, combineLatest, forkJoin
  [x] Subjects: BehaviorSubject, ReplaySubject, signals
  [x] Guards: CanActivate, CanDeactivate, Resolve, CanMatch
  [x] Routing: lazy loading, preloading, nested routes
  [x] Performance: OnPush, @defer, virtual scrolling, bundle analysis
  [x] Testing: TestBed, ComponentFixture, HttpTestingController
```

## DSA Topic: Product of Array Except Self (Prefix/Suffix Products)
```java
// LeetCode 238 — O(n) no division
public int[] productExceptSelf(int[] nums) {
    int n = nums.length;
    int[] result = new int[n];

    // Pass 1: fill result[i] with product of all elements LEFT of i
    result[0] = 1;
    for (int i = 1; i < n; i++) {
        result[i] = result[i - 1] * nums[i - 1];
    }

    // Pass 2: multiply by product of all elements RIGHT of i
    int right = 1;
    for (int i = n - 1; i >= 0; i--) {
        result[i] *= right;
        right *= nums[i];
    }
    return result;
}
// Time: O(n), Space: O(1) output array excluded
// Elegant: result[i] = left_product[i] * right_product[i]
// Two-pass without extra arrays
```

## Full Stack Architecture Summary
```
Client (Angular 17)
    ↓  HTTPS
Load Balancer
    ↓
API Gateway (rate limiting, auth)
    ↓
Spring Boot Services (stateless, JWT)
    ↓                  ↓
PostgreSQL          Redis Cache
(primary + replica)  (sessions, hot data)
    ↓
Kafka (async events)
    ↓
Email / SMS / Analytics Services
```

## Interview Day Checklist
```
Technical:
  [ ] Review your 3 strongest projects with STAR stories
  [ ] Practice 5 DSA problems (medium difficulty, LeetCode)
  [ ] Prepare system design for: URL shortener, notification system, order management
  [ ] Review Spring Boot internals: auto-config, transactions, security
  [ ] Review Angular: change detection, RxJS operators, state management

Behavioral:
  [ ] 7 STAR stories: achievement, failure, conflict, initiative, learning, collaboration, impact
  [ ] 5 questions to ask the interviewer
  [ ] Know your numbers: performance metrics, test coverage, bundle sizes

Logistics:
  [ ] Arrive 10 min early (or join video 5 min early)
  [ ] Have IDE/editor ready for live coding
  [ ] Have resume printed / PDF open
  [ ] Water and a calm space
```

## 90-Day Learning Journey Summary
```
Days 1-10:   Java fundamentals, OOP, Spring Boot basics
Days 11-20:  REST APIs, JPA, Spring Security
Days 21-30:  Advanced Java, Streams, Optional, Design Patterns
Days 31-40:  Exception handling, Validation, Logging, Kafka basics
Days 41-50:  Microservices, WebClient, Circuit Breakers, Testing
Days 51-60:  JPA Relationships, JWT, Advanced Testing
Days 61-70:  Angular: Components, Templates, Binding, Directives
Days 71-80:  Angular: RxJS, State Management, Performance, Testing
Days 81-90:  Mock Interviews, System Design, Behavioral Prep
```

## What Makes a Senior Full Stack Engineer
```
Technical depth:      Can explain WHY, not just HOW
System thinking:      Considers scale, failures, maintainability
Code quality:         Writes code others can understand and extend
Testing mindset:      Tests are not optional, they're part of done
Performance aware:    Knows query plans, bundle sizes, CD cycles
Security conscious:   Thinks about attack vectors and data exposure
Communication:        Can explain complex topics simply
Ownership:            Fixes problems, not just assigned tickets
```
""",
"mcqs": [
  {"id":"d90q1","prompt":"What is the Product of Array Except Self algorithm and why avoid division?","options":["Use cumulative sum","Two-pass prefix/suffix product: result[i] = product of all elements left × product of all elements right. O(n) time, O(1) extra space. Avoid division because input may contain zeros (0/0 is undefined)","Sort first","Use HashMap for products"],"correctAnswer":"Two-pass prefix/suffix product: result[i] = product of all elements left × product of all elements right. O(n) time, O(1) extra space. Avoid division because input may contain zeros (0/0 is undefined)","explanation":"[1,2,3,4]: result[0]=1(no left)×24(right)=24, result[1]=1×12=12, result[2]=2×4=8, result[3]=6×1=6. Pass 1: build left products in result[]. Pass 2: right variable tracks right product, multiply into result[]. No extra array needed."},
  {"id":"d90q2","prompt":"What distinguishes a senior full stack engineer from a junior one?","options":["Years of experience only","Depth of understanding: senior explains WHY (trade-offs, constraints), not just HOW (implementation). System thinking: considers scale, failure modes, maintainability. Ownership: proactively identifies problems. Can mentor others","Number of languages known","Having a CS degree"],"correctAnswer":"Depth of understanding: senior explains WHY (trade-offs, constraints), not just HOW (implementation). System thinking: considers scale, failure modes, maintainability. Ownership: proactively identifies problems. Can mentor others","explanation":"Junior: 'I used OnPush.' Senior: 'OnPush reduced CD overhead by 80% — we were running CD on 100 components per mouse move. With OnPush, only changed components update. Tradeoff: immutable inputs required.' Depth + trade-offs + impact."},
  {"id":"d90q3","prompt":"What is the complete Spring Boot request lifecycle?","options":["Request → Controller → DB","HTTP Request → DispatcherServlet → Security Filter Chain → HandlerMapping → Interceptors → @Controller method → Service → Repository → JPA → DB → back through chain → JSON response","Request goes directly to database","Load Balancer handles all routing"],"correctAnswer":"HTTP Request → DispatcherServlet → Security Filter Chain → HandlerMapping → Interceptors → @Controller method → Service → Repository → JPA → DB → back through chain → JSON response","explanation":"Every Spring MVC request: 1. DispatcherServlet receives. 2. Security filters (JWT validation). 3. HandlerMapping finds controller. 4. HandlerInterceptor.preHandle(). 5. Controller. 6. Service (@Transactional). 7. Repository. 8. JPA/Hibernate → SQL. 9. Response through @ControllerAdvice → JSON."},
  {"id":"d90q4","prompt":"What is the complete Angular component rendering lifecycle?","options":["Compile → Run","Browser loads HTML → Angular bootstrap → App component → Router match → Lazy load chunk → Component factory → constructor → ngOnChanges → ngOnInit → template render → ngAfterViewInit → live","Angular renders instantly","Zone.js handles all rendering"],"correctAnswer":"Browser loads HTML → Angular bootstrap → App component → Router match → Lazy load chunk → Component factory → constructor → ngOnChanges → ngOnInit → template render → ngAfterViewInit → live","explanation":"Full cycle: index.html loads → main.js bootstraps Angular → Router reads URL → lazy chunk downloaded if needed → component instantiated → lifecycle hooks run → change detection renders template → child components repeat the cycle."},
  {"id":"d90q5","prompt":"What are the most important RxJS operators for Angular HTTP interactions?","options":["subscribe() is enough","switchMap: cancel previous (search), exhaustMap: ignore while active (submit), mergeMap: parallel (multi-fetch), concatMap: sequential (audit), combineLatest: reactive dashboard, forkJoin: parallel page load, catchError: resilience","Only map and filter","RxJS is optional for HTTP"],"correctAnswer":"switchMap: cancel previous (search), exhaustMap: ignore while active (submit), mergeMap: parallel (multi-fetch), concatMap: sequential (audit), combineLatest: reactive dashboard, forkJoin: parallel page load, catchError: resilience","explanation":"Pattern matching: search → switchMap. Submit → exhaustMap. Dashboard → combineLatest. Page init (multiple APIs) → forkJoin. Error → catchError + EMPTY or throwError. These 6 operators cover 90% of Angular HTTP scenarios."},
  {"id":"d90q6","prompt":"What are the 3 key performance optimizations every Angular app should have?","options":["More servers","1. OnPush change detection: reduces CD overhead dramatically. 2. Lazy loading: split initial bundle — only load what's needed. 3. async pipe: auto-manages subscriptions, no memory leaks, integrates with OnPush","Use React instead","Optimize images only"],"correctAnswer":"1. OnPush change detection: reduces CD overhead dramatically. 2. Lazy loading: split initial bundle — only load what's needed. 3. async pipe: auto-manages subscriptions, no memory leaks, integrates with OnPush","explanation":"OnPush: 80% fewer CD checks. Lazy loading: 70% bundle reduction for feature routes. Async pipe: eliminates subscription memory leaks + correct OnPush integration. These three compound: small bundle + fast rendering + no leaks = performant app."},
  {"id":"d90q7","prompt":"What are the 3 key performance optimizations every Spring Boot API should have?","options":["More RAM","1. Solve N+1 with EntityGraph/JOIN FETCH. 2. Index strategy (composite indexes, covering indexes) verified with EXPLAIN ANALYZE. 3. Connection pool tuning (HikariCP) — match pool size to DB capacity and concurrency","Use more caching","Disable all logging"],"correctAnswer":"1. Solve N+1 with EntityGraph/JOIN FETCH. 2. Index strategy (composite indexes, covering indexes) verified with EXPLAIN ANALYZE. 3. Connection pool tuning (HikariCP) — match pool size to DB capacity and concurrency","explanation":"N+1: most common JPA performance killer. Indexes: make 5s queries run in 50ms. Connection pool: 10 connections default → 11th request blocks. These three cover most Spring Boot performance issues."},
  {"id":"d90q8","prompt":"What is the complete JWT authentication flow in a full stack application?","options":["JWT stores password","1. Angular: login form → POST /auth/login. 2. Spring: validate credentials, issue access token + refresh token. 3. Angular: store tokens, interceptor adds Authorization header. 4. Spring: JwtFilter validates each request. 5. Angular: on 401, interceptor refreshes token. 6. Both: logout clears tokens server and client","JWT is stored in database","Spring Security handles everything"],"correctAnswer":"1. Angular: login form → POST /auth/login. 2. Spring: validate credentials, issue access token + refresh token. 3. Angular: store tokens, interceptor adds Authorization header. 4. Spring: JwtFilter validates each request. 5. Angular: on 401, interceptor refreshes token. 6. Both: logout clears tokens server and client","explanation":"End-to-end: Angular form → Spring validates → JWT issued → Angular interceptor auto-adds header → Spring JwtFilter verifies on each request → 401 → Angular refreshes transparently → logout invalidates both sides. Stateless, scalable, secure."},
  {"id":"d90q9","prompt":"What are the testing layers in a full stack application and what does each test?","options":["Only unit tests","Unit: service logic with Mockito. Controller: @WebMvcTest with MockMvc. Repository: @DataJpaTest. Integration: @SpringBootTest with Testcontainers. Angular: component with TestBed, service with HttpTestingController. E2E: Cypress","Only integration tests","Tests are optional"],"correctAnswer":"Unit: service logic with Mockito. Controller: @WebMvcTest with MockMvc. Repository: @DataJpaTest. Integration: @SpringBootTest with Testcontainers. Angular: component with TestBed, service with HttpTestingController. E2E: Cypress","explanation":"Testing pyramid: many unit (fast), fewer integration (slower), few E2E (slowest). Each layer catches different bugs: unit = logic errors, integration = wiring/DB, E2E = user flow. All layers needed for confidence."},
  {"id":"d90q10","prompt":"What mindset shift takes a developer from intermediate to advanced?","options":["Learning more frameworks","Shifting from 'make it work' to 'make it right AND scalable': thinking about failure modes, considering the reader of your code, designing for testability, asking why before implementing, measuring impact. Curiosity-driven vs task-driven","Working longer hours","Using more design patterns"],"correctAnswer":"Shifting from 'make it work' to 'make it right AND scalable': thinking about failure modes, considering the reader of your code, designing for testability, asking why before implementing, measuring impact. Curiosity-driven vs task-driven","explanation":"Intermediate: implement requirements. Advanced: question requirements, identify edge cases upfront, design for change, instrument for observability, make code self-explanatory. The difference: one ships features; the other ships reliable systems."}
],
"writtenConceptQuestions": [
  "Solve Product of Array Except Self. Trace [1,2,3,4] through both passes. Show why division fails with zeros.",
  "Write the complete JWT authentication flow end-to-end: Angular login form to Spring JwtFilter validation.",
  "Design the full system architecture for the 90-day capstone: Angular frontend + Spring Boot backend + PostgreSQL + Redis + Kafka.",
  "What are the 5 most important things you learned in 90 days? For each, show a code example.",
  "Walk through diagnosing and fixing a Spring Boot API showing 5s p99 latency. Show tools and steps.",
  "What is the difference between an intermediate and senior full stack developer? Show examples.",
  "Write your elevator pitch: explain your full stack capabilities in 2 minutes covering Java, Spring Boot, Angular, and key skills."
],
"businessScenarios": [
  "Final capstone: design and implement a mini Order Management System end-to-end: Spring Boot REST API with JWT, Angular frontend with reactive forms and state management, deployed with Docker Compose.",
  "A production API has 3s p99 latency at 100 req/sec. Walk through the complete diagnosis: EXPLAIN ANALYZE, connection pool metrics, N+1 check, cache hit rate — and the remediation plan.",
  "Prepare for your first senior developer interview: review 3 real projects, prepare STAR stories for 7 behavioral questions, and practice explaining the system design of your most complex project."
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
