"""Rewrite days 81-85: Java Mock Interviews, Spring Boot, Angular, SQL, DSA Mock Interviews."""
import json, os
DATA_DIR = "backend/data/curriculum"

CURRICULUM = {

"day-081": {
"notes": """# Java Mock Interview Preparation: Core Java Deep Dive

## Collections Framework — Interview Essentials
```java
// HashMap internals — common interview topic
// Java 8+: array of buckets, each bucket is a linked list → balanced BST when >8 nodes
// hashCode() determines bucket; equals() resolves collisions

Map<String, Integer> inventory = new HashMap<>();
inventory.put("apples", 100);
inventory.getOrDefault("oranges", 0);         // 0 — null-safe
inventory.putIfAbsent("apples", 200);          // no-op — "apples" already exists
inventory.computeIfAbsent("grapes", k -> 50);  // adds if absent, returns value
inventory.merge("apples", 50, Integer::sum);   // 100 + 50 = 150

// Why HashMap is not thread-safe: concurrent modification → infinite loop (Java 7),
// ConcurrentHashMap uses segment locking (Java 7) / CAS (Java 8+)

// LinkedHashMap — preserves insertion order
// TreeMap — sorted by key (natural order or Comparator)
// HashMap — O(1) avg; TreeMap — O(log n)
```

## Java 8+ Streams — Functional Processing
```java
List<Order> orders = getOrders();

// Filter, map, collect
List<String> pendingCustomers = orders.stream()
    .filter(o -> o.getStatus() == OrderStatus.PENDING)
    .map(Order::getCustomerId)
    .distinct()
    .sorted()
    .collect(Collectors.toList());

// groupingBy — very common interview question
Map<OrderStatus, Long> countByStatus = orders.stream()
    .collect(Collectors.groupingBy(Order::getStatus, Collectors.counting()));

// toMap with merge function (handles duplicate keys)
Map<String, Double> totalByCustomer = orders.stream()
    .collect(Collectors.toMap(
        Order::getCustomerId,
        Order::getTotal,
        Double::sum  // merge function for duplicate keys
    ));

// reduce
double grandTotal = orders.stream()
    .mapToDouble(Order::getTotal)
    .sum();

// flatMap — flatten nested collections
List<String> allProductIds = orders.stream()
    .flatMap(o -> o.getItems().stream())
    .map(OrderItem::getProductId)
    .collect(Collectors.toList());
```

## Java 21 — Modern Features
```java
// Records — immutable data carriers
public record OrderDto(String id, String customerId, double total, OrderStatus status) {}
// Generates: constructor, getters, equals, hashCode, toString automatically

// Sealed Classes — restrict subtype hierarchy
public sealed interface Shape permits Circle, Rectangle, Triangle {}
public record Circle(double radius) implements Shape {}
public record Rectangle(double width, double height) implements Shape {}

// Pattern Matching with switch (Java 21)
double area = switch (shape) {
    case Circle c       -> Math.PI * c.radius() * c.radius();
    case Rectangle r    -> r.width() * r.height();
    case Triangle t     -> 0.5 * t.base() * t.height();
};

// Text Blocks (Java 15+) — multi-line strings using triple-quote syntax
// String json = triple-quote { "orderId": "O-001", "status": "PENDING" } triple-quote;
// Avoids manual escape sequences; treated as a raw string block

// Virtual Threads (Java 21) — Project Loom
Thread.ofVirtual().start(() -> {
    // Lightweight thread — can run millions concurrently
    // No blocking concern — JVM manages scheduling
});
```

## DSA Topic: Partition Equal Subset Sum (0/1 Knapsack — DP)
```java
// Problem: can we partition array into two equal-sum subsets?
// LeetCode 416
// Approach: DP — can we reach sum/2 using any subset?

public boolean canPartition(int[] nums) {
    int total = Arrays.stream(nums).sum();
    if (total % 2 != 0) return false;        // odd total → impossible

    int target = total / 2;
    boolean[] dp = new boolean[target + 1];
    dp[0] = true;                             // empty subset sums to 0

    for (int num : nums) {
        // Traverse right to left to avoid using same element twice (0/1 knapsack)
        for (int j = target; j >= num; j--) {
            dp[j] = dp[j] || dp[j - num];
        }
    }
    return dp[target];
}

// Time: O(n * target), Space: O(target)
// Key insight: dp[j] = true if we can reach sum j using elements seen so far
// Right-to-left traversal: prevents reusing the same element
```

## Common Java Interview Questions
```java
// Q: Difference between String, StringBuilder, StringBuffer?
// String: immutable — new object on every concat (interned in String pool)
// StringBuilder: mutable, NOT thread-safe, faster
// StringBuffer: mutable, thread-safe (synchronized), slower

// Q: What is the contract between equals() and hashCode()?
// If a.equals(b) then a.hashCode() == b.hashCode() MUST be true
// Violation: HashMap stores equal objects in different buckets → never found

// Q: What is a functional interface?
@FunctionalInterface
interface Processor<T, R> { R process(T input); }
// Has exactly ONE abstract method — can be used as lambda target

// Q: Difference between checked and unchecked exceptions?
// Checked: must be declared or caught (IOException, SQLException)
// Unchecked (RuntimeException): not required (NullPointerException, IllegalArgumentException)
```

## Common Mistakes in Interviews
1. **Modifying collection while iterating:** use `Iterator.remove()` or `removeIf()`.
2. **Using `==` for String comparison:** `==` checks reference, `.equals()` checks value.
3. **Integer cache gotcha:** `Integer a = 127; Integer b = 127; a == b` is `true` (cached). `Integer a = 128; a == b` is `false`.
""",
"mcqs": [
  {"id":"d81q1","prompt":"What is the time complexity of HashMap get/put and why?","options":["O(n) always","O(1) average — hashCode() directly maps key to bucket. O(n) worst case when all keys hash to the same bucket (rare). Java 8+: O(log n) worst case (linked list converts to balanced BST when bucket size >8)","O(log n) always","O(1) guaranteed"],"correctAnswer":"O(1) average — hashCode() directly maps key to bucket. O(n) worst case when all keys hash to the same bucket (rare). Java 8+: O(log n) worst case (linked list converts to balanced BST when bucket size >8)","explanation":"HashMap: array of buckets. get(key): compute hashCode → bucket index → equals() to find exact entry. O(1) when hash distribution is good. Degenerate case (all same hashCode): O(n) before Java 8, O(log n) in Java 8+ due to treeification."},
  {"id":"d81q2","prompt":"What is the contract between equals() and hashCode()?","options":["No relationship","If two objects are equal (a.equals(b) == true), they MUST have the same hashCode. Violation breaks HashMap/HashSet — equal objects land in different buckets and are never found","hashCode must be unique","equals() and hashCode() are independent"],"correctAnswer":"If two objects are equal (a.equals(b) == true), they MUST have the same hashCode. Violation breaks HashMap/HashSet — equal objects land in different buckets and are never found","explanation":"HashMap.get(key): computes hashCode to find bucket, then equals() to find exact key. If equal objects have different hashCodes: they'd be in different buckets, get() returns null even though the key 'exists'. @Override both or neither."},
  {"id":"d81q3","prompt":"What does `Collectors.groupingBy()` do in streams?","options":["Groups threads","Partitions stream elements into a Map by a classifier function — groupingBy(Order::getStatus) produces Map<OrderStatus, List<Order>>. With downstream collector: groupingBy(status, counting()) gives Map<Status, Long>","Only works with strings","Replaces forEach"],"correctAnswer":"Partitions stream elements into a Map by a classifier function — groupingBy(Order::getStatus) produces Map<OrderStatus, List<Order>>. With downstream collector: groupingBy(status, counting()) gives Map<Status, Long>","explanation":"Like SQL GROUP BY. orders.stream().collect(groupingBy(Order::getStatus)): { PENDING: [o1,o3], SHIPPED: [o2] }. With downstream: groupingBy(Order::getStatus, summingDouble(Order::getTotal)) — total per status."},
  {"id":"d81q4","prompt":"What are Java Records (Java 16+)?","options":["Database records","Immutable data carrier classes — `record Point(int x, int y) {}` automatically generates all-args constructor, getters (x(), y()), equals, hashCode, toString. Ideal for DTOs and value objects","Records can be subclassed","Records replace all classes"],"correctAnswer":"Immutable data carrier classes — `record Point(int x, int y) {}` automatically generates all-args constructor, getters (x(), y()), equals, hashCode, toString. Ideal for DTOs and value objects","explanation":"record replaces: class + @Getter + @EqualsAndHashCode + @ToString. Fields are final. Cannot extend other classes. Can implement interfaces. Can have compact constructors for validation."},
  {"id":"d81q5","prompt":"What is the difference between `flatMap` and `map` in streams?","options":["flatMap is slower","map: transforms each element to one value (1-to-1). flatMap: transforms each element to a stream, then flattens all streams into one (1-to-many). Use flatMap to flatten nested collections","flatMap only works with Optional","map and flatMap are identical"],"correctAnswer":"map: transforms each element to one value (1-to-1). flatMap: transforms each element to a stream, then flattens all streams into one (1-to-many). Use flatMap to flatten nested collections","explanation":"orders.stream().map(Order::getItems): Stream<List<Item>>. orders.stream().flatMap(o -> o.getItems().stream()): Stream<Item> (flat). Use flatMap when each element maps to multiple values."},
  {"id":"d81q6","prompt":"What is the Partition Equal Subset Sum problem and its approach?","options":["Sort the array","Determine if an array can be split into two subsets with equal sum. 0/1 Knapsack DP: boolean dp[target+1] where dp[j]=true if sum j is reachable. Key: traverse right-to-left to prevent reusing elements","Use binary search","Greedy always works"],"correctAnswer":"Determine if an array can be split into two subsets with equal sum. 0/1 Knapsack DP: boolean dp[target+1] where dp[j]=true if sum j is reachable. Key: traverse right-to-left to prevent reusing elements","explanation":"target = sum/2. dp[0]=true. For each num: for j=target to num: dp[j] |= dp[j-num]. Right-to-left prevents using same element twice (unlike unbounded knapsack which traverses left-to-right). Time O(n*target)."},
  {"id":"d81q7","prompt":"What is a functional interface and how does it enable lambdas?","options":["An interface with no methods","An interface with exactly ONE abstract method — enables lambda syntax: Comparator<String> c = (a,b) -> a.compareTo(b). @FunctionalInterface annotation enforces this at compile time","Functional interfaces use reflection","Cannot be used with generics"],"correctAnswer":"An interface with exactly ONE abstract method — enables lambda syntax: Comparator<String> c = (a,b) -> a.compareTo(b). @FunctionalInterface annotation enforces this at compile time","explanation":"Java lambdas implement functional interfaces. Built-in: Supplier<T>, Consumer<T>, Function<T,R>, Predicate<T>, BiFunction<T,U,R>. Any interface with one abstract method works as a lambda target."},
  {"id":"d81q8","prompt":"What are Virtual Threads in Java 21?","options":["Threads in a virtual machine","Lightweight JVM-managed threads — millions can run concurrently (unlike platform threads limited to thousands). When a virtual thread blocks on I/O, JVM parks it and runs another — no OS thread wasted","Virtual threads don't support I/O","Replace CompletableFuture"],"correctAnswer":"Lightweight JVM-managed threads — millions can run concurrently (unlike platform threads limited to thousands). When a virtual thread blocks on I/O, JVM parks it and runs another — no OS thread wasted","explanation":"Platform thread: 1-to-1 with OS thread (~1MB stack). Blocking I/O: OS thread parked. Virtual thread: JVM manages scheduling. Blocking: JVM unmounts from carrier thread, another virtual thread runs. 10x throughput for I/O-bound workloads."},
  {"id":"d81q9","prompt":"What is the difference between Comparable and Comparator in Java?","options":["Identical interfaces","Comparable: natural ordering — class implements it to define how its instances compare (compareTo). Comparator: external ordering — separate class/lambda defining comparison without modifying the original class","Comparator is deprecated","Comparable is for primitives only"],"correctAnswer":"Comparable: natural ordering — class implements it to define how its instances compare (compareTo). Comparator: external ordering — separate class/lambda defining comparison without modifying the original class","explanation":"String implements Comparable<String>: natural alphabetical. Custom: Comparator<Product> byPrice = Comparator.comparingDouble(Product::getPrice). Multiple sorts: products.sort(Comparator.comparing(Product::getCategory).thenComparing(Product::getPrice))."},
  {"id":"d81q10","prompt":"What is ConcurrentHashMap and when should you use it?","options":["A slow HashMap","Thread-safe HashMap using segment locking (Java 7) or CAS operations (Java 8+). Use when multiple threads read/write the map concurrently. Allows concurrent reads without locking. putIfAbsent, computeIfAbsent are atomic operations","Same as synchronized HashMap","ConcurrentHashMap is deprecated"],"correctAnswer":"Thread-safe HashMap using segment locking (Java 7) or CAS operations (Java 8+). Use when multiple threads read/write the map concurrently. Allows concurrent reads without locking. putIfAbsent, computeIfAbsent are atomic operations","explanation":"Collections.synchronizedMap: locks the entire map for every operation. ConcurrentHashMap: fine-grained locking/CAS — reads are non-blocking, writes lock only the affected bucket. Throughput: far better than synchronized under concurrent load."}
],
"writtenConceptQuestions": [
  "Explain HashMap internals: hashing, buckets, collision resolution, and Java 8 treeification.",
  "Show streams: filter, map, collect, groupingBy, flatMap with an order processing example.",
  "Explain Java Records. Show a UserDto record with a compact constructor for validation.",
  "Show sealed interfaces with pattern matching switch (Java 21). When are they useful?",
  "Solve Partition Equal Subset Sum. Explain why right-to-left traversal is needed for 0/1 knapsack.",
  "What is the equals/hashCode contract? Show a class breaking it and how HashMap is affected.",
  "Compare StringBuilder vs StringBuffer vs String for concatenation in loops."
],
"businessScenarios": [
  "An e-commerce system groups orders by status and calculates totals per group. Show the streams solution using groupingBy with summingDouble downstream collector.",
  "A caching layer uses HashMap concurrently from multiple request threads, causing race conditions. Migrate to ConcurrentHashMap with computeIfAbsent for atomic cache population.",
  "An order API returns DTOs with many fields. Replace verbose POJO classes with Java Records and show the reduction in boilerplate."
]
},

"day-082": {
"notes": """# Spring Boot Mock Interview Preparation: Deep Dive

## Spring Boot Auto-Configuration
```java
// Spring Boot convention-over-configuration
// @SpringBootApplication = @Configuration + @ComponentScan + @EnableAutoConfiguration
@SpringBootApplication
public class OrderApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderApplication.class, args);
    }
}

// Auto-configuration: Spring Boot reads META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
// DataSourceAutoConfiguration: if H2 on classpath + no DataSource bean → creates H2 DataSource
// JpaAutoConfiguration: if Hibernate on classpath + DataSource → creates EntityManagerFactory
// You can override by providing your own bean

// Conditionals control auto-configuration
@ConditionalOnClass(DataSource.class)        // only if DataSource class is present
@ConditionalOnMissingBean(DataSource.class)  // only if no DataSource bean defined
@ConditionalOnProperty("spring.datasource.url")
public class DataSourceAutoConfiguration { ... }
```

## Spring Security — SecurityFilterChain (Spring Security 6)
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)         // REST APIs: CSRF disabled
            .sessionManagement(sm ->
                sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS)) // JWT: no sessions
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()               // public
                .requestMatchers("/api/admin/**").hasRole("ADMIN")         // role-restricted
                .anyRequest().authenticated()                              // everything else: auth
            )
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }
}
```

## Bean Scopes and Lifecycle
```java
@Component                      // Singleton (default) — one instance per ApplicationContext
@Component @Scope("prototype")  // New instance every time injected
@Component @Scope("request")    // One per HTTP request (web apps)
@Component @Scope("session")    // One per HTTP session (web apps)

// Lifecycle callbacks
@Component
public class OrderProcessor {
    @PostConstruct          // runs after DI is done — initialize resources
    public void init() { ... }

    @PreDestroy             // runs before bean removed from context — cleanup
    public void cleanup() { ... }
}
```

## Transaction Management
```java
@Service
@Transactional(readOnly = true)  // default for all methods: read-only
public class OrderService {

    @Transactional                // override: full read-write transaction
    public OrderDto createOrder(CreateOrderRequest req) {
        Order order = orderMapper.toEntity(req);
        orderRepo.save(order);

        // Inventory deduction — same transaction
        inventoryService.deduct(req.getProductId(), req.getQuantity());

        // If inventoryService throws → entire transaction rolls back
        return orderMapper.toDto(order);
    }

    // @Transactional(propagation = Propagation.REQUIRES_NEW)
    // Starts a NEW transaction regardless of outer transaction
    // Used for: audit logging (must persist even if outer transaction rolls back)

    // @Transactional(rollbackFor = BusinessException.class)
    // Default: rolls back on RuntimeException and Error
    // Must specify for checked exceptions
}
```

## DSA Topic: Decode Ways (DP)
```java
// Problem: count ways to decode a string of digits ('A'=1..'Z'=26)
// LeetCode 91
public int numDecodings(String s) {
    if (s.isEmpty() || s.charAt(0) == '0') return 0;

    int n = s.length();
    int[] dp = new int[n + 1];
    dp[0] = 1;   // empty string: 1 way
    dp[1] = 1;   // first char (non-zero): 1 way

    for (int i = 2; i <= n; i++) {
        int oneDigit = Integer.parseInt(s.substring(i - 1, i));
        int twoDigit = Integer.parseInt(s.substring(i - 2, i));

        if (oneDigit >= 1)                    dp[i] += dp[i - 1];  // decode as single
        if (twoDigit >= 10 && twoDigit <= 26) dp[i] += dp[i - 2];  // decode as pair
    }
    return dp[n];
}
// Time: O(n), Space: O(n) or O(1) with two variables
```

## Spring Boot Common Interview Questions
```java
// Q: What is @Transactional propagation?
// REQUIRED (default): join existing tx or create new
// REQUIRES_NEW: always new tx; outer tx suspended
// SUPPORTS: use existing tx if present; non-tx otherwise
// NOT_SUPPORTED: always non-tx; outer tx suspended
// NEVER: must have no tx; throw if outer tx exists
// MANDATORY: must have outer tx; throw if none

// Q: What is @Async and when does @Transactional not work with it?
@Async  // runs in separate thread from ThreadPoolTaskExecutor
public CompletableFuture<String> sendEmail(String to) { ... }
// @Transactional in caller: transaction bound to calling thread
// @Async: new thread — no transaction context shared
// Fix: @Transactional in the @Async method itself

// Q: What is the N+1 problem and how to fix it?
// N+1: 1 query for orders + N queries for each order's customer
// Fix: @Query with JOIN FETCH or @EntityGraph
@Query("SELECT o FROM Order o JOIN FETCH o.customer WHERE o.status = :status")
List<Order> findByStatusWithCustomer(@Param("status") OrderStatus status);
```

## Common Mistakes
1. **Self-invocation bypasses @Transactional:** calling a transactional method within the same class skips the proxy. Use a separate bean.
2. **@Async on private methods:** AOP proxy can't intercept private methods. Must be public.
3. **readOnly = true on modifying operations:** Spring may skip flushing dirty-checked entities.
""",
"mcqs": [
  {"id":"d82q1","prompt":"What does @SpringBootApplication do?","options":["Starts the app","Combines @Configuration (bean definitions), @ComponentScan (scans the package tree for @Component), and @EnableAutoConfiguration (conditionally configures beans based on classpath). All three in one annotation","Only enables auto-configuration","Configures the web server"],"correctAnswer":"Combines @Configuration (bean definitions), @ComponentScan (scans the package tree for @Component), and @EnableAutoConfiguration (conditionally configures beans based on classpath). All three in one annotation","explanation":"@SpringBootApplication on main class: Angular scans all @Component/@Service/@Repository/@Controller in that package and sub-packages. Auto-configuration inspects the classpath and creates beans you'd otherwise configure manually."},
  {"id":"d82q2","prompt":"What is the default transaction propagation and what does it mean?","options":["REQUIRES_NEW","REQUIRED — join an existing transaction if one exists; create a new one if not. Most services use this. The transaction boundary is the outermost @Transactional method","No default propagation","SUPPORTS is the default"],"correctAnswer":"REQUIRED — join an existing transaction if one exists; create a new one if not. Most services use this. The transaction boundary is the outermost @Transactional method","explanation":"ServiceA.createOrder() @Transactional calls ServiceB.deductInventory() @Transactional. Both share the SAME transaction (REQUIRED). If B throws: A's work also rolls back. REQUIRES_NEW: B would have its own transaction, A's not affected by B's rollback."},
  {"id":"d82q3","prompt":"Why does calling a @Transactional method from within the same class not work?","options":["Spring bug","Spring uses AOP proxy — @Transactional works by wrapping the bean in a proxy that opens/closes transactions. Self-invocation bypasses the proxy (calling `this.method()` calls the real object, not the proxy). Fix: inject the same bean or use self-injection","@Transactional works everywhere","Private methods cause this issue"],"correctAnswer":"Spring uses AOP proxy — @Transactional works by wrapping the bean in a proxy that opens/closes transactions. Self-invocation bypasses the proxy (calling `this.method()` calls the real object, not the proxy). Fix: inject the same bean or use self-injection","explanation":"Proxy intercepts external calls. Internal calls: this.doSomething() → hits the real object, proxy skipped. Same issue with @Async, @Cacheable. Fix: @Autowired ApplicationContext ctx; ctx.getBean(OrderService.class).doSomething()."},
  {"id":"d82q4","prompt":"What does `SessionCreationPolicy.STATELESS` do in Spring Security?","options":["Disables HTTP sessions","Tells Spring Security never to create or use an HTTP session for storing authentication. Required for JWT-based REST APIs — each request must carry the JWT token since no session stores the auth state","STATELESS prevents logout","Only affects cookies"],"correctAnswer":"Tells Spring Security never to create or use an HTTP session for storing authentication. Required for JWT-based REST APIs — each request must carry the JWT token since no session stores the auth state","explanation":"Default Spring Security: stores authentication in HttpSession (JSESSIONID cookie). STATELESS: no session, no cookie. Every request authenticated via JWT in Authorization header. Required for scalable, horizontally-scaled APIs."},
  {"id":"d82q5","prompt":"What is @ConditionalOnMissingBean used for in auto-configuration?","options":["Removes existing beans","Prevents auto-configuration from overriding a user-defined bean — if the user defines their own DataSource bean, Spring Boot's DataSourceAutoConfiguration skips creating one. 'Configure it for me only if I haven't already'","Conditionally removes beans","Only used in tests"],"correctAnswer":"Prevents auto-configuration from overriding a user-defined bean — if the user defines their own DataSource bean, Spring Boot's DataSourceAutoConfiguration skips creating one. 'Configure it for me only if I haven't already'","explanation":"Auto-configuration is opt-out: if you define the bean yourself, the auto-configuration backs off. @ConditionalOnMissingBean(DataSource.class): only create the default if no DataSource bean is present in the context."},
  {"id":"d82q6","prompt":"When must you specify `rollbackFor` in @Transactional?","options":["Always","Only for CHECKED exceptions — Spring defaults to rolling back on RuntimeException and Error (unchecked). Checked exceptions (IOException, custom checked exceptions) don't trigger rollback unless explicitly specified: @Transactional(rollbackFor = OrderException.class)","rollbackFor is deprecated","Only for database errors"],"correctAnswer":"Only for CHECKED exceptions — Spring defaults to rolling back on RuntimeException and Error (unchecked). Checked exceptions (IOException, custom checked exceptions) don't trigger rollback unless explicitly specified: @Transactional(rollbackFor = OrderException.class)","explanation":"Business exception extending RuntimeException: auto-rollback. Business exception extending Exception: NO auto-rollback (transaction commits). Common interview gotcha: custom checked exceptions that should roll back transactions must use rollbackFor."},
  {"id":"d82q7","prompt":"What is the N+1 query problem and how is JOIN FETCH a solution?","options":["11 database queries","1 query fetches N entities → N separate queries to load each entity's association = N+1 queries total. JOIN FETCH or @EntityGraph loads everything in ONE query with a SQL JOIN","N+1 is a Spring bug","Only affects @ManyToMany"],"correctAnswer":"1 query fetches N entities → N separate queries to load each entity's association = N+1 queries total. JOIN FETCH or @EntityGraph loads everything in ONE query with a SQL JOIN","explanation":"findAll() → SELECT * FROM orders (1 query) → for each order, SELECT customer WHERE id=? (N queries). 100 orders = 101 queries. JOIN FETCH: SELECT o, c FROM Order o JOIN FETCH o.customer — 1 query, all data loaded."},
  {"id":"d82q8","prompt":"What does Propagation.REQUIRES_NEW do?","options":["Requires an existing transaction","Suspends any existing transaction and starts a BRAND NEW transaction. The new transaction commits/rolls back independently of the outer transaction. Use case: audit logging that must persist even if the main operation rolls back","REQUIRES_NEW is the default","Same as REQUIRED"],"correctAnswer":"Suspends any existing transaction and starts a BRAND NEW transaction. The new transaction commits/rolls back independently of the outer transaction. Use case: audit logging that must persist even if the main operation rolls back","explanation":"Order creation fails → outer transaction rolls back. Audit log (REQUIRES_NEW): committed before outer rolls back. Result: order not created, but audit record persists. Without REQUIRES_NEW, the audit log would also roll back."},
  {"id":"d82q9","prompt":"What is the Decode Ways problem and its DP approach?","options":["Decode a cipher","Count the number of ways to decode a digit string where 1-26 map to A-Z. DP: dp[i] = ways to decode s[0..i-1]. At each position, check if single digit (1-9) or two digits (10-26) form valid letters","Use recursion only","Binary search approach"],"correctAnswer":"Count the number of ways to decode a digit string where 1-26 map to A-Z. DP: dp[i] = ways to decode s[0..i-1]. At each position, check if single digit (1-9) or two digits (10-26) form valid letters","explanation":"dp[0]=1 (empty), dp[1]=1 (first char). For i>=2: if s[i-1]!='0': dp[i]+=dp[i-1]. If s[i-2..i-1] in 10-26: dp[i]+=dp[i-2]. '226' → 3 ways: 2|2|6, 22|6, 2|26."},
  {"id":"d82q10","prompt":"What is @Scope('prototype') and when do you use it?","options":["Global singleton","New instance created every time the bean is injected or retrieved from the context. Use for: stateful beans, objects with mutable state that should not be shared (form handlers, request-specific processors)","Prototype is deprecated","One instance per request"],"correctAnswer":"New instance created every time the bean is injected or retrieved from the context. Use for: stateful beans, objects with mutable state that should not be shared (form handlers, request-specific processors)","explanation":"Singleton: shared — if it has mutable state, concurrent requests corrupt each other. Prototype: each injection gets a fresh instance. Warning: injecting a prototype into a singleton breaks the prototype scope — use ObjectProvider or ApplicationContext.getBean()."}
],
"writtenConceptQuestions": [
  "Explain Spring Boot auto-configuration: how does @ConditionalOnClass/@ConditionalOnMissingBean work?",
  "Show SecurityFilterChain configuration for a JWT REST API with role-based access control.",
  "What is @Transactional propagation? Show REQUIRED vs REQUIRES_NEW with an audit log example.",
  "Explain the self-invocation proxy problem. Show the fix using self-injection.",
  "Solve Decode Ways. Trace dp array for '226'. Show time and space complexity.",
  "What are bean scopes? When do you use prototype scope instead of singleton?",
  "Show N+1 problem in JPA and fix with JOIN FETCH. Show the SQL generated in both cases."
],
"businessScenarios": [
  "An order creation service calls a notification service in the same class with @Transactional. Notifications still send even when orders fail. Fix the self-invocation proxy problem.",
  "Audit logs are being rolled back along with failed orders. Add REQUIRES_NEW propagation to the audit service to ensure audit records always persist.",
  "A customer API is slow due to 50 queries per request. The Order→Customer relationship is LAZY loaded. Fix with @EntityGraph or JOIN FETCH."
]
},

"day-083": {
"notes": """# Angular Mock Interview Preparation: Deep Dive Q&A

## Change Detection Deep Dive
```typescript
// Q: Explain Angular's change detection mechanism
// Zone.js monkey-patches browser APIs (setTimeout, click, XHR, Promise)
// On any async event: Zone.js notifies Angular → CD runs from root down

// Default CD: checks every component
// OnPush: skips component unless:
//   1. @Input reference changed
//   2. Component event fired
//   3. async pipe emitted
//   4. markForCheck() called

// Q: What happens with an Observable inside OnPush?
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<p>{{ items$ | async | json }}</p>`
})
export class ListComponent {
  items$ = this.service.getItems();  // async pipe handles subscription AND markForCheck()
}

// Q: How do signals improve on Zone.js?
count = signal(0);
doubleCount = computed(() => count() * 2);
// count.set(1): Angular knows EXACTLY which templates depend on count → only those updated
// No zone scanning — surgical updates
```

## RxJS in Angular — Patterns
```typescript
// Q: switchMap vs exhaustMap in practice
// Search (switchMap): cancel previous, use latest
// Login button (exhaustMap): ignore clicks while request in-flight

// Q: How to combine multiple HTTP calls
// Parallel: forkJoin({ user$, orders$, products$ })
// Sequential: user$ → switchMap(user => getOrdersFor(user.id))
// Conditional: if (user.isPremium) → premiumOrders$ else → standardOrders$

// Q: Memory leaks — common interview question
@Component({ ... })
export class MyComponent implements OnDestroy {
  private destroy$ = new Subject<void>();

  ngOnInit() {
    this.service.stream$
      .pipe(takeUntil(this.destroy$))
      .subscribe(data => this.data = data);
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

## Dependency Injection Deep Dive
```typescript
// Q: Explain the injector hierarchy
// Root → Environment (route) → Element (component) → Directive

// Q: Why expose asObservable() not Subject?
// BehaviorSubject exposes next() — any component can modify state
// asObservable() read-only — only service can emit

// Q: What is the difference between providers at root vs component?
// Root: singleton across app
// Component providers: each instance gets its own service — fresh state
```

## DSA Topic: Jump Game II (Greedy)
```java
// Problem: minimum jumps to reach end of array
// LeetCode 45 — each element is max jump distance
public int jump(int[] nums) {
    int jumps = 0, currentEnd = 0, farthest = 0;

    for (int i = 0; i < nums.length - 1; i++) {
        farthest = Math.max(farthest, i + nums[i]);  // how far can we reach from here?

        if (i == currentEnd) {        // we've exhausted current jump range
            jumps++;                  // must jump
            currentEnd = farthest;   // new range = farthest we can reach
        }
    }
    return jumps;
}
// Greedy: at each jump, choose the position that gets us farthest
// Time: O(n), Space: O(1)
// Key insight: we don't need to know exactly which index to jump to —
//              just track the farthest reachable position in current range
```

## Angular Interview Q&A
```typescript
// Q: How does Angular DI differ from direct instantiation?
// new Service(): tightly coupled, no mock in tests, no lifecycle management
// @Injectable + inject(): singleton, mockable, lifecycle managed, lazy

// Q: Standalone components vs NgModule
// NgModule: requires declaration + imports in module file
// Standalone: self-contained, imports declared in @Component, no module needed

// Q: What is the async pipe and why is it preferred over subscribe()?
// async: auto-subscribes, auto-unsubscribes on destroy, markForCheck for OnPush
// subscribe(): manual unsubscribe needed, no automatic OnPush integration

// Q: How do you share state between unrelated components?
// Service with BehaviorSubject or Signal exposed as readonly
// Both components inject the same service (singleton)
// Changes by one → all subscribers update
```

## Common Angular Interview Mistakes
1. **Not knowing when ngOnChanges fires:** before ngOnInit AND on every @Input change.
2. **Confusing template reference variable with @ViewChild:** #ref in template is template-only; @ViewChild brings it to TypeScript.
3. **Not explaining OnPush trade-offs:** immutable inputs required, object mutation breaks it.
""",
"mcqs": [
  {"id":"d83q1","prompt":"How does Zone.js trigger Angular change detection?","options":["Angular polls every 16ms","Zone.js monkey-patches browser async APIs (setTimeout, Promise, click events, XHR). When any patched operation completes, Zone.js notifies Angular → CD runs from root component down the tree","Zone.js requires JVM","Zone.js is optional for all apps"],"correctAnswer":"Zone.js monkey-patches browser async APIs (setTimeout, Promise, click events, XHR). When any patched operation completes, Zone.js notifies Angular → CD runs from root component down the tree","explanation":"Zone.js wraps browser APIs. Any async operation completion → NgZone.run() → ApplicationRef.tick() → check all components from root. Without Zone.js: must manually call markForCheck() or detectChanges() (signals-based apps)."},
  {"id":"d83q2","prompt":"What does the async pipe do that manual subscribe() doesn't?","options":["async pipe is faster","Automatic subscription management: subscribes on use, marks OnPush components for check on emission, and unsubscribes when the component is destroyed — no memory leaks, no manual takeUntil required","async is only for HTTP","async pipe caches responses"],"correctAnswer":"Automatic subscription management: subscribes on use, marks OnPush components for check on emission, and unsubscribes when the component is destroyed — no memory leaks, no manual takeUntil required","explanation":"subscribe(): you manage the Subscription. Forget unsubscribe → memory leak. async pipe: Angular manages lifecycle. Also: with OnPush, async pipe calls markForCheck() when new value arrives — subscribe() does not."},
  {"id":"d83q3","prompt":"What is the Jump Game II problem and why is greedy optimal?","options":["Maximize jumps","Minimum jumps to reach the last index. Greedy: at each jump boundary, choose the position that extends reach farthest. O(n) time because we never revisit a position. DP works but is O(n²)","Jump in order","Binary search approach"],"correctAnswer":"Minimum jumps to reach the last index. Greedy: at each jump boundary, choose the position that extends reach farthest. O(n) time because we never revisit a position. DP works but is O(n²)","explanation":"Track: farthest reachable from current range. When we exhaust current range (i == currentEnd): must jump, new range extends to farthest. Count jumps. Greedy is valid: always jump to maximize next range."},
  {"id":"d83q4","prompt":"Why must Angular standalone components import their dependencies in @Component?","options":["TypeScript requirement","Without NgModule, there's no module to inherit dependencies from — each standalone component is self-contained and must explicitly declare its imports (RouterLink, CommonModule, etc.) so Angular knows what's available in its template","Standalone requires more imports","Only affects directives"],"correctAnswer":"Without NgModule, there's no module to inherit dependencies from — each standalone component is self-contained and must explicitly declare its imports (RouterLink, CommonModule, etc.) so Angular knows what's available in its template","explanation":"NgModule: imports declared once, all components in the module inherit them. Standalone: each component is its own 'module'. More explicit, better tree-shaking, clearer dependency graph."},
  {"id":"d83q5","prompt":"How do you share state between two sibling components with no parent-child relationship?","options":["Use @Input","Create a shared service with BehaviorSubject or Signal marked as providedIn:'root'. Both components inject it. Component A calls service.update(value), Component B's subscription/signal receives the update","Use EventEmitter globally","Services can't share state"],"correctAnswer":"Create a shared service with BehaviorSubject or Signal marked as providedIn:'root'. Both components inject it. Component A calls service.update(value), Component B's subscription/signal receives the update","explanation":"BehaviorSubject approach: CartService.items$ (BehaviorSubject). HeaderComponent subscribes for badge count. CartPageComponent subscribes for full list. CartService.addItem() → both update simultaneously."},
  {"id":"d83q6","prompt":"What is the difference between `ngOnChanges` and `ngOnInit`?","options":["Same lifecycle hook","ngOnChanges: called before ngOnInit AND whenever any @Input changes — receives SimpleChanges with old/new values. ngOnInit: called once after first ngOnChanges — component is fully initialized, good for initial data loading","ngOnInit runs before ngOnChanges","ngOnChanges requires @Input"],"correctAnswer":"ngOnChanges: called before ngOnInit AND whenever any @Input changes — receives SimpleChanges with old/new values. ngOnInit: called once after first ngOnChanges — component is fully initialized, good for initial data loading","explanation":"Order: ngOnChanges(first) → ngOnInit → [ngOnChanges on each input change]. Use ngOnChanges to react to input updates without reinitializing the whole component. Use ngOnInit for one-time setup."},
  {"id":"d83q7","prompt":"When does `detectChanges()` cause `ExpressionChangedAfterItHasBeenCheckedError`?","options":["Always in production","When detectChanges() changes a binding that Angular already checked in the CURRENT CD cycle — Angular detects the post-check change in dev mode and throws. Fix: use async update or markForCheck()","Only in tests","Expression error requires DOM access"],"correctAnswer":"When detectChanges() changes a binding that Angular already checked in the CURRENT CD cycle — Angular detects the post-check change in dev mode and throws. Fix: use async update or markForCheck()","explanation":"Angular's dev mode: runs CD twice to catch mutations during CD. If you change a binding inside ngAfterViewInit and call detectChanges() synchronously → Angular sees the value changed after it checked. Fix: setTimeout(() => this.value = x) or markForCheck()."},
  {"id":"d83q8","prompt":"What is an Angular interceptor and what Angular concept enables it?","options":["A route guard","AOP-like middleware for HttpClient requests/responses. Enabled by the HttpInterceptorFn type and withInterceptors() in provideHttpClient. Chain pattern: each interceptor calls next(req) to pass to the next interceptor or the actual HTTP backend","Interceptors replace services","HttpClient doesn't use interceptors"],"correctAnswer":"AOP-like middleware for HttpClient requests/responses. Enabled by the HttpInterceptorFn type and withInterceptors() in provideHttpClient. Chain pattern: each interceptor calls next(req) to pass to the next interceptor or the actual HTTP backend","explanation":"Similar to Spring's Filter chain. Use for: auth headers, error handling, logging, loading indicators — applied to ALL requests without modifying individual service calls."},
  {"id":"d83q9","prompt":"What does `ChangeDetectorRef.detach()` do and when is it used?","options":["Destroys the component","Removes the component from Angular's change detection tree — it will NEVER update automatically. Call detectChanges() manually when you want to update. Use for maximum performance in static/rarely-updated components","detach() prevents memory leaks","Same as OnPush"],"correctAnswer":"Removes the component from Angular's change detection tree — it will NEVER update automatically. Call detectChanges() manually when you want to update. Use for maximum performance in static/rarely-updated components","explanation":"Dashboard with 100 charts: even OnPush checks 100 components on every event. cdr.detach() + cdr.detectChanges() only when data arrives: zero overhead between updates. Nuclear option for performance."},
  {"id":"d83q10","prompt":"How does Angular's router handle lazy loading at runtime?","options":["Pre-downloads all routes","On navigation to a lazy route, Angular's router fetches the JavaScript chunk via dynamic import(), registers the component/routes, then activates the route — transparent to the user","Router stores all chunks in memory","Lazy loading requires a module"],"correctAnswer":"On navigation to a lazy route, Angular's router fetches the JavaScript chunk via dynamic import(), registers the component/routes, then activates the route — transparent to the user","explanation":"Network tab: navigate to /admin → browser downloads admin.chunk.js. Router shows a loading state (NavigationStart event), then activates. Subsequent visits: chunk is cached. No extra configuration needed — just loadComponent/loadChildren with dynamic import."}
],
"writtenConceptQuestions": [
  "Explain Angular change detection: Zone.js, OnPush, signals. How does each trigger updates?",
  "Show the takeUntil pattern for preventing memory leaks. Compare to async pipe approach.",
  "Solve Jump Game II. Trace the algorithm on [2,3,1,1,4]. Show greedy logic.",
  "Design a shared CartService using signals. Show two unrelated components consuming it.",
  "Explain injector hierarchy: root vs component-level providers. Show an example where they differ.",
  "What is the ExpressionChangedAfterItHasBeenCheckedError? Show a common scenario and fix.",
  "Show the complete flow: user lands on /orders → authGuard → lazy loads chunk → resolver fetches data → component renders."
],
"businessScenarios": [
  "A notification feed component subscribes to a WebSocket stream but memory usage grows over time — subscriptions leak. Add takeUntil cleanup.",
  "An admin dashboard checks every component on every mouse move. Implement detach() for charts that only update on new data.",
  "A shared filter state needs to sync between the sidebar filter component and the main product grid. Design using a signal-based FilterStateService."
]
},

"day-084": {
"notes": """# SQL Mock Interview Preparation: Advanced Queries and Optimization

## Window Functions — Essential for Interviews
```sql
-- ROW_NUMBER — unique rank per row
SELECT
    customer_id,
    order_id,
    order_date,
    total,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
FROM orders;
-- rn=1 for each customer's most recent order

-- Get most recent order per customer (classic interview problem)
SELECT customer_id, order_id, total
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
    FROM orders
) ranked
WHERE rn = 1;

-- RANK vs DENSE_RANK vs ROW_NUMBER
-- 1,1,3 (RANK — skips 2), 1,1,2 (DENSE_RANK — no skip), 1,2,3 (ROW_NUMBER — always unique)

-- Running total
SELECT
    order_date,
    total,
    SUM(total) OVER (ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM orders;

-- LAG / LEAD — compare with previous/next row
SELECT
    order_date,
    total,
    LAG(total) OVER (ORDER BY order_date)  AS prev_total,
    total - LAG(total) OVER (ORDER BY order_date) AS change
FROM daily_sales;
```

## Indexes — Query Optimization
```sql
-- Composite index — column order matters
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);
-- Covers: WHERE customer_id = ? AND order_date > ?
-- Covers: WHERE customer_id = ?
-- Does NOT efficiently cover: WHERE order_date > ? (without customer_id filter)
-- Rule: most selective/frequently filtered column first

-- EXPLAIN ANALYZE — understand query plan
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 'C-001' AND status = 'PENDING';
-- Look for: Seq Scan (bad) vs Index Scan (good), rows, actual time

-- Covering index — includes all queried columns, avoids table lookup
CREATE INDEX idx_orders_covering ON orders (customer_id, status) INCLUDE (order_id, total);
-- Query can be satisfied entirely from index — no heap access
```

## CTEs and Recursive Queries
```sql
-- CTE — readable, reusable within query
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(total) AS revenue
    FROM orders
    WHERE status = 'COMPLETED'
    GROUP BY 1
),
ranked_months AS (
    SELECT *,
        RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
    FROM monthly_revenue
)
SELECT month, revenue, revenue_rank
FROM ranked_months
WHERE revenue_rank <= 3;

-- Recursive CTE — hierarchical data (org chart, categories)
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, 0 AS depth
    FROM categories
    WHERE parent_id IS NULL     -- root categories
    UNION ALL
    SELECT c.id, c.name, c.parent_id, ct.depth + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT id, LPAD('', depth * 2, ' ') || name AS indented_name, depth
FROM category_tree
ORDER BY depth, name;
```

## DSA Topic: Meeting Rooms II (Min-Heap)
```java
// Problem: minimum number of conference rooms required
// LeetCode 253
public int minMeetingRooms(int[][] intervals) {
    if (intervals.length == 0) return 0;

    Arrays.sort(intervals, (a, b) -> a[0] - b[0]);  // sort by start time
    PriorityQueue<Integer> heap = new PriorityQueue<>();  // min-heap of end times

    for (int[] meeting : intervals) {
        // If earliest-ending meeting ends before this one starts → reuse the room
        if (!heap.isEmpty() && heap.peek() <= meeting[0]) {
            heap.poll();  // free the room
        }
        heap.offer(meeting[1]);  // assign this meeting's end time
    }
    return heap.size();  // rooms in use = heap size
}
// Time: O(n log n), Space: O(n)
```

## SQL Interview Q&A
```sql
-- Q: Difference between WHERE and HAVING?
SELECT customer_id, COUNT(*) AS order_count
FROM orders
WHERE status = 'COMPLETED'        -- filter rows BEFORE grouping
GROUP BY customer_id
HAVING COUNT(*) > 5;              -- filter groups AFTER aggregation

-- Q: Find customers who ordered every product
SELECT customer_id
FROM order_items oi
JOIN products p ON oi.product_id = p.id
GROUP BY customer_id
HAVING COUNT(DISTINCT oi.product_id) = (SELECT COUNT(*) FROM products);

-- Q: Second highest salary
SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);
-- Or with DENSE_RANK:
SELECT salary FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS dr FROM employees
) WHERE dr = 2;
```

## Common Mistakes
1. **Using `!=` with NULL:** `NULL != 'value'` is NULL (not TRUE). Use `IS NOT NULL`.
2. **Index not used due to function on column:** `WHERE LOWER(email) = ?` prevents index use. Fix: functional index or stored lowercase.
3. **N+1 in SQL:** selecting from a table in a subquery that runs per-row. Rewrite as JOIN.
""",
"mcqs": [
  {"id":"d84q1","prompt":"What is the difference between RANK(), DENSE_RANK(), and ROW_NUMBER()?","options":["Identical functions","ROW_NUMBER: always unique sequential (1,2,3). RANK: skips after ties (1,1,3 — no 2). DENSE_RANK: no skipping after ties (1,1,2). Use DENSE_RANK for top-N per group without gaps","DENSE_RANK requires unique values","ROW_NUMBER is for sorting only"],"correctAnswer":"ROW_NUMBER: always unique sequential (1,2,3). RANK: skips after ties (1,1,3 — no 2). DENSE_RANK: no skipping after ties (1,1,2). Use DENSE_RANK for top-N per group without gaps","explanation":"Scores: 100, 100, 90. RANK: 1,1,3. DENSE_RANK: 1,1,2. ROW_NUMBER: 1,2,3 (arbitrary order for ties). Use case: top 3 products per category → DENSE_RANK ≤ 3 (includes all ties at 3rd position)."},
  {"id":"d84q2","prompt":"What does PARTITION BY do in a window function?","options":["Splits the table","Divides rows into independent groups — the window function resets for each partition. ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY date): row numbers restart at 1 for each customer","PARTITION BY is like GROUP BY","Requires an index"],"correctAnswer":"Divides rows into independent groups — the window function resets for each partition. ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY date): row numbers restart at 1 for each customer","explanation":"Without PARTITION BY: ROW_NUMBER() over all rows. With PARTITION BY customer_id: row numbers reset per customer — customer A has 1,2,3 and customer B also has 1,2,3. Equivalent to GROUP BY but without collapsing rows."},
  {"id":"d84q3","prompt":"What is a covering index?","options":["An index on all columns","An index that contains ALL columns needed by a query — query can be answered entirely from the index without accessing the table heap. Fastest possible index. CREATE INDEX ... INCLUDE (col1, col2) adds non-key columns","Covering indexes require InnoDB","Only for SELECT *"],"correctAnswer":"An index that contains ALL columns needed by a query — query can be answered entirely from the index without accessing the table heap. Fastest possible read. CREATE INDEX ... INCLUDE (col1, col2) adds non-key columns","explanation":"Query: SELECT order_id, total FROM orders WHERE customer_id = 'C-1'. Index on (customer_id) INCLUDE (order_id, total): full answer in index, no heap read (index-only scan). Without INCLUDE: index finds rows, then fetches each row from heap."},
  {"id":"d84q4","prompt":"What is the difference between WHERE and HAVING?","options":["Both filter rows","WHERE filters individual rows BEFORE GROUP BY aggregation. HAVING filters groups AFTER aggregation. WHERE cannot use aggregate functions. HAVING cannot reference non-grouped columns","HAVING is deprecated","They run simultaneously"],"correctAnswer":"WHERE filters individual rows BEFORE GROUP BY aggregation. HAVING filters groups AFTER aggregation. WHERE cannot use aggregate functions. HAVING cannot reference non-grouped columns","explanation":"ORDER: FROM → WHERE (filter rows) → GROUP BY → HAVING (filter groups) → SELECT → ORDER BY. Use WHERE when possible — filters earlier, fewer rows to aggregate. HAVING needed for conditions on aggregated values (COUNT, SUM, AVG)."},
  {"id":"d84q5","prompt":"What does a CTE (WITH clause) provide over subqueries?","options":["CTEs are always faster","Readability and reusability within the query — complex logic can be named and referenced multiple times. Recursive CTEs enable hierarchical queries (org charts, category trees) not possible with regular subqueries","CTEs replace all JOINs","CTEs require PostgreSQL"],"correctAnswer":"Readability and reusability within the query — complex logic can be named and referenced multiple times. Recursive CTEs enable hierarchical queries (org charts, category trees) not possible with regular subqueries","explanation":"CTE vs subquery: functionally equivalent for non-recursive. CTE: named, reusable in same query, reads top-to-bottom. Recursive CTE: UNION ALL references itself — only way to traverse tree structures without procedural code."},
  {"id":"d84q6","prompt":"What is the Meeting Rooms II problem and what data structure solves it?","options":["Schedule meetings optimally","Find the minimum number of rooms for N meetings. Min-heap of end times: sort meetings by start, for each meeting check if any room is free (heap.peek() <= start). If yes, reuse room (poll). Always add end time. Heap size = rooms needed","Binary search approach","Use a stack"],"correctAnswer":"Find the minimum number of rooms for N meetings. Min-heap of end times: sort meetings by start, for each meeting check if any room is free (heap.peek() <= start). If yes, reuse room (poll). Always add end time. Heap size = rooms needed","explanation":"Sort by start: process in order. Min-heap: O(1) access to earliest-ending meeting. If it ends before current starts: reuse its room. Otherwise: new room needed. Final heap size = concurrent meetings peak = rooms needed."},
  {"id":"d84q7","prompt":"Why does `WHERE LOWER(email) = ?` prevent index usage on the email column?","options":["LOWER is not a function","Applying a function to an indexed column prevents the index from being used — the index stores original values, not lowercased ones. Fix: store emails lowercase always, or create a functional index: CREATE INDEX ON users (LOWER(email))","WHERE clauses don't use indexes","LOWER requires full table scan always"],"correctAnswer":"Applying a function to an indexed column prevents the index from being used — the index stores original values, not lowercased ones. Fix: store emails lowercase always, or create a functional index: CREATE INDEX ON users (LOWER(email))","explanation":"Index on email: stored as 'User@Example.com'. LOWER(email) = 'user@example.com': index doesn't help — must compute LOWER for every row. Functional index on LOWER(email): stores lowercased values, query uses index."},
  {"id":"d84q8","prompt":"What does LAG() window function do?","options":["Returns last row","Accesses a value from a PREVIOUS row within the partition without a self-join. LAG(total) OVER (ORDER BY date): returns the total from the previous row. LAG(total, 2): two rows back. Useful for period-over-period comparisons","LAG delays query execution","LAG is for time series only"],"correctAnswer":"Accesses a value from a PREVIOUS row within the partition without a self-join. LAG(total) OVER (ORDER BY date): returns the total from the previous row. LAG(total, 2): two rows back. Useful for period-over-period comparisons","explanation":"Month-over-month revenue change: SELECT month, revenue, revenue - LAG(revenue) OVER (ORDER BY month) AS change. Without window function: self-join on orders table — complex and slower."},
  {"id":"d84q9","prompt":"Why does `NULL != 'value'` not return TRUE in SQL?","options":["SQL bug","NULL represents UNKNOWN — any comparison with NULL yields NULL (not TRUE or FALSE). Use IS NULL / IS NOT NULL. WHERE email != 'test@example.com': rows with email = NULL are excluded because NULL != 'test' is NULL (not TRUE)","NULL equals empty string","Only affects indexes"],"correctAnswer":"NULL represents UNKNOWN — any comparison with NULL yields NULL (not TRUE or FALSE). Use IS NULL / IS NOT NULL. WHERE email != 'test@example.com': rows with email = NULL are excluded because NULL != 'test' is NULL (not TRUE)","explanation":"Three-valued logic: TRUE, FALSE, NULL. NULL + anything = NULL. WHERE filters keep only TRUE — NULLs dropped. Fix: WHERE email != 'test@example.com' OR email IS NULL to include rows with null email."},
  {"id":"d84q10","prompt":"What does EXPLAIN ANALYZE show and what should you look for?","options":["Shows table schema","The query execution plan with actual vs estimated row counts and timing. Look for: Seq Scan (full table scan — usually bad for large tables), Index Scan vs Index-Only Scan, rows estimate accuracy, nested loop vs hash join cost","EXPLAIN changes the query","Only works with PostgreSQL"],"correctAnswer":"The query execution plan with actual vs estimated row counts and timing. Look for: Seq Scan (full table scan — usually bad for large tables), Index Scan vs Index-Only Scan, rows estimate accuracy, nested loop vs hash join cost","explanation":"Seq Scan on orders (1M rows) in WHERE clause: missing index. Index Scan: good. Rows=1 actual=10000: bad statistics, run ANALYZE. Hash Join vs Nested Loop: Hash better for large joins. Actual time: find slow nodes."}
],
"writtenConceptQuestions": [
  "Show ROW_NUMBER, RANK, DENSE_RANK differences with a scores example. Show getting top N per group.",
  "Write a query using a CTE and window functions to find the top 3 revenue months.",
  "Explain composite index column ordering. Show index on (customer_id, order_date) and which queries use it.",
  "Solve Meeting Rooms II with a min-heap. Trace the algorithm on [[0,30],[5,10],[15,20]].",
  "Show LAG() for month-over-month sales comparison. What self-join would this replace?",
  "What is a covering index? Show CREATE INDEX with INCLUDE and the resulting query plan change.",
  "Show WHERE vs HAVING with an example filtering orders before and after aggregation."
],
"businessScenarios": [
  "A monthly report needs the top 3 revenue customers per region. Write using DENSE_RANK() with PARTITION BY region.",
  "A products API query takes 3 seconds on a table with 5M rows. Run EXPLAIN ANALYZE and identify the missing index.",
  "An HR system stores organizational hierarchy. Write a recursive CTE to traverse all employees under a given manager."
]
},

"day-085": {
"notes": """# DSA Mock Interview Preparation: Core Patterns and Problems

## Core DSA Patterns
```
Pattern             | Trigger Words                     | Data Structure
--------------------|-----------------------------------|----------------
Two Pointers        | sorted array, pairs, palindrome   | array
Sliding Window      | subarray, substring, max/min      | array/string
Binary Search       | sorted, find value, O(log n)      | array
BFS/DFS             | graph, tree, shortest path        | queue/stack
Dynamic Programming | optimal, count ways, max/min      | array/matrix
Heap                | k-th largest/smallest, streaming  | PriorityQueue
Hash Map            | count, frequency, pair sum        | HashMap
Stack               | valid brackets, next greater      | Stack
Monotonic Stack     | next/previous greater/smaller     | Stack
Greedy              | interval, optimal local choice    | sort + iterate
```

## DSA Topic: Missing Number (Bit Manipulation / Math)
```java
// LeetCode 268 — find missing number in [0..n] array
// Approach 1: XOR (no overflow)
public int missingNumber(int[] nums) {
    int result = nums.length;  // XOR with n
    for (int i = 0; i < nums.length; i++) {
        result ^= i ^ nums[i];  // XOR all indices and values
    }
    return result;
    // XOR properties: a^a=0, a^0=a, XOR is commutative and associative
    // All present numbers cancel out; missing number remains
}

// Approach 2: Gauss sum
public int missingNumber2(int[] nums) {
    int n = nums.length;
    int expected = n * (n + 1) / 2;  // sum of 0..n
    int actual = Arrays.stream(nums).sum();
    return expected - actual;
}
// Both: O(n) time, O(1) space
```

## Two Pointers Pattern
```java
// Valid Palindrome II (at most one deletion)
public boolean validPalindrome(String s) {
    int l = 0, r = s.length() - 1;
    while (l < r) {
        if (s.charAt(l) != s.charAt(r)) {
            // Try skipping left char OR right char
            return isPalindrome(s, l + 1, r) || isPalindrome(s, l, r - 1);
        }
        l++; r--;
    }
    return true;
}

private boolean isPalindrome(String s, int l, int r) {
    while (l < r) {
        if (s.charAt(l++) != s.charAt(r--)) return false;
    }
    return true;
}
```

## Sliding Window Pattern
```java
// Minimum Window Substring
public String minWindow(String s, String t) {
    Map<Character, Integer> need = new HashMap<>();
    for (char c : t.toCharArray()) need.merge(c, 1, Integer::sum);

    int have = 0, required = need.size();
    int left = 0, minLen = Integer.MAX_VALUE, minL = 0;

    Map<Character, Integer> window = new HashMap<>();
    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        window.merge(c, 1, Integer::sum);
        if (need.containsKey(c) && window.get(c).equals(need.get(c))) have++;

        while (have == required) {  // valid window — try to shrink
            if (right - left + 1 < minLen) { minLen = right - left + 1; minL = left; }
            char l = s.charAt(left++);
            window.merge(l, -1, Integer::sum);
            if (need.containsKey(l) && window.get(l) < need.get(l)) have--;
        }
    }
    return minLen == Integer.MAX_VALUE ? "" : s.substring(minL, minL + minLen);
}
// Time: O(|s| + |t|), Space: O(|t|)
```

## Graph BFS — Shortest Path
```java
// Shortest path in unweighted graph — BFS always gives optimal
public int shortestPath(int[][] grid, int[] start, int[] end) {
    int rows = grid.length, cols = grid[0].length;
    boolean[][] visited = new boolean[rows][cols];
    Queue<int[]> queue = new LinkedList<>();
    queue.offer(new int[]{start[0], start[1], 0});  // [row, col, distance]
    visited[start[0]][start[1]] = true;

    int[][] dirs = {{0,1},{0,-1},{1,0},{-1,0}};
    while (!queue.isEmpty()) {
        int[] curr = queue.poll();
        if (curr[0] == end[0] && curr[1] == end[1]) return curr[2];

        for (int[] d : dirs) {
            int nr = curr[0] + d[0], nc = curr[1] + d[1];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols
                && grid[nr][nc] == 0 && !visited[nr][nc]) {
                visited[nr][nc] = true;
                queue.offer(new int[]{nr, nc, curr[2] + 1});
            }
        }
    }
    return -1;
}
```

## Common Interview DSA Mistakes
1. **Not handling edge cases:** empty array, single element, all same values.
2. **Integer overflow:** `left + right` overflows. Use `left + (right - left) / 2` in binary search.
3. **Modifying while iterating:** use index-based loops or collect changes first.
""",
"mcqs": [
  {"id":"d85q1","prompt":"What is the XOR trick for finding a missing number?","options":["XOR all elements with their index","XOR all numbers 0..n with all array elements. Paired numbers cancel (a^a=0). Only the missing number is left — it has no pair. O(n) time, O(1) space, no overflow risk","XOR computes the sum","XOR only works for integers"],"correctAnswer":"XOR all numbers 0..n with all array elements. Paired numbers cancel (a^a=0). Only the missing number is left — it has no pair. O(n) time, O(1) space, no overflow risk","explanation":"result = n; for i: result ^= i ^ nums[i]. This XORs all of {0,1,..,n} with all of nums. Every number except the missing one appears twice → XOR to 0. Missing: appears once → survives. Cleaner than Gauss sum which can overflow for large n."},
  {"id":"d85q2","prompt":"When do you use BFS vs DFS for graph problems?","options":["Interchangeable","BFS: shortest path in unweighted graphs (explores level by level), connectivity, minimum steps. DFS: cycle detection, topological sort, paths in weighted graphs (when backtracking needed), exploring all paths","DFS is always better","BFS requires more memory"],"correctAnswer":"BFS: shortest path in unweighted graphs (explores level by level), connectivity, minimum steps. DFS: cycle detection, topological sort, paths in weighted graphs (when backtracking needed), exploring all paths","explanation":"BFS explores all nodes at distance k before distance k+1 → guarantees shortest path in unweighted. DFS: explores one path fully → finds a path but not guaranteed shortest. BFS memory: O(width). DFS memory: O(depth/height)."},
  {"id":"d85q3","prompt":"What is the sliding window pattern and when does it apply?","options":["A database window function","Maintains a window (contiguous subarray/substring) that expands right and shrinks left based on a condition. Used for: longest/shortest subarray with property, minimum window containing all required characters. O(n) vs O(n²) brute force","Sliding window requires sorting","Only for arrays of fixed size"],"correctAnswer":"Maintains a window (contiguous subarray/substring) that expands right and shrinks left based on a condition. Used for: longest/shortest subarray with property, minimum window containing all required characters. O(n) vs O(n²) brute force","explanation":"Each element enters window once (right pointer) and exits once (left pointer) → O(n). Brute force: check all O(n²) subarrays → O(n²). Trigger: 'longest subarray with sum ≤ k', 'minimum window substring'."},
  {"id":"d85q4","prompt":"Why use `left + (right - left) / 2` instead of `(left + right) / 2` in binary search?","options":["Identical mathematically","(left + right) can overflow a 32-bit integer when both are large. left + (right - left) / 2 always stays within bounds. Example: left=2^30, right=2^30+1 → left+right overflows int","left + right is simpler","Only relevant in C++"],"correctAnswer":"(left + right) can overflow a 32-bit integer when both are large. left + (right - left) / 2 always stays within bounds. Example: left=2^30, right=2^30+1 → left+right overflows int","explanation":"int max = 2^31-1 ≈ 2.1B. Two large indices: 1.5B + 1.5B = 3B > max → overflow → negative → crash. left + (right-left)/2 = left + small_number → safe. Standard interview trap."},
  {"id":"d85q5","prompt":"What is the two-pointer pattern and when does it apply?","options":["Two separate arrays","Two indices moving toward each other (or in same direction) on a sorted array or string. Reduces O(n²) brute force to O(n). Applies: pair sum in sorted array, palindrome check, container with most water, trapping rain water","Two pointers require extra memory","Only for sorted arrays"],"correctAnswer":"Two indices moving toward each other (or in same direction) on a sorted array or string. Reduces O(n²) brute force to O(n). Applies: pair sum in sorted array, palindrome check, container with most water, trapping rain water","explanation":"Two Sum sorted: left=0, right=n-1. sum<target: left++. sum>target: right--. Sum==target: found. O(n). Without two pointers: O(n²) nested loops. Also fast/slow pointer: detect cycle in linked list."},
  {"id":"d85q6","prompt":"What is dynamic programming and how do you identify a DP problem?","options":["Programming dynamically","Break problem into overlapping subproblems — solve each once and store results. Identify by: 'count ways', 'minimum cost', 'maximum value', 'can we reach'. Key: optimal substructure (optimal solution uses optimal sub-solutions)","DP only works on arrays","DP requires recursion"],"correctAnswer":"Break problem into overlapping subproblems — solve each once and store results. Identify by: 'count ways', 'minimum cost', 'maximum value', 'can we reach'. Key: optimal substructure (optimal solution uses optimal sub-solutions)","explanation":"DP templates: 1D (Fibonacci, Climbing Stairs), 2D (LCS, Edit Distance), 0/1 Knapsack, unbounded Knapsack. If recursion has repeated subproblems → memoize. Bottom-up DP: build solution from base cases."},
  {"id":"d85q7","prompt":"What is a monotonic stack and what problems does it solve?","options":["A sorted stack","A stack that maintains elements in monotonically increasing or decreasing order. Elements are popped when they violate the monotonic property. Solves: next greater element, largest rectangle in histogram, trapping rain water in O(n)","Monotonic stack requires sorting","Same as min-heap"],"correctAnswer":"A stack that maintains elements in monotonically increasing or decreasing order. Elements are popped when they violate the monotonic property. Solves: next greater element, largest rectangle in histogram, trapping rain water in O(n)","explanation":"Next Greater Element: iterate right-to-left, maintain decreasing stack. For each element, pop until stack.peek() > current → that's the next greater. Push current. O(n) vs O(n²) brute force."},
  {"id":"d85q8","prompt":"When should you use a min-heap (PriorityQueue) in an interview problem?","options":["Sorting arrays","When you need efficient access to the MINIMUM (or maximum) element among a dynamic set. Common uses: k-th largest/smallest, merge k sorted lists, Dijkstra's algorithm, scheduling problems","Heap is only for sorting","PriorityQueue is O(1) for all operations"],"correctAnswer":"When you need efficient access to the MINIMUM (or maximum) element among a dynamic set. Common uses: k-th largest/smallest, merge k sorted lists, Dijkstra's algorithm, scheduling problems","explanation":"PriorityQueue: offer O(log n), peek O(1), poll O(log n). K-th largest in stream: maintain min-heap of size k — if element > heap.peek(), poll and offer. heap.peek() = k-th largest. Meeting Rooms II: min-heap of end times."},
  {"id":"d85q9","prompt":"What is the time complexity of the sliding window minimum window substring?","options":["O(n²)","O(|s| + |t|) — the right pointer traverses s once, the left pointer traverses s at most once (each character enters and exits the window at most once). HashMap operations O(1). Total: O(2|s| + |t|) = O(|s| + |t|)","O(|s| * |t|)","O(n log n)"],"correctAnswer":"O(|s| + |t|) — the right pointer traverses s once, the left pointer traverses s at most once (each character enters and exits the window at most once). HashMap operations O(1). Total: O(2|s| + |t|) = O(|s| + |t|)","explanation":"Right pointer: 0 to |s|-1 (one pass). Left pointer: 0 to at most |s|-1 (shrinks after valid window found). Each character: added to window once, removed at most once. HashMap: O(1) per operation. |t| for initial frequency map."},
  {"id":"d85q10","prompt":"What edge cases should you ALWAYS check in DSA interviews?","options":["None needed","Empty input (empty array/string/null), single element, all same elements, negative numbers, integer overflow in sums/indices, sorted/reverse-sorted arrays (worst case for some algorithms), duplicates","Only check null","Edge cases reduce score"],"correctAnswer":"Empty input (empty array/string/null), single element, all same elements, negative numbers, integer overflow in sums/indices, sorted/reverse-sorted arrays (worst case for some algorithms), duplicates","explanation":"Interviewers deliberately test edge cases. State them upfront: 'I'll handle the empty array case first.' Shows systematic thinking. Common fails: null check, single element off-by-one, overflow in mid calculation, negative numbers breaking abs value assumptions."}
],
"writtenConceptQuestions": [
  "Solve Missing Number with both XOR and Gauss sum approaches. Compare pros and cons.",
  "Show the sliding window pattern for Minimum Window Substring. Trace on s='ADOBECODEBANC', t='ABC'.",
  "Explain BFS for shortest path in grid. Show the visited array trick to prevent revisiting.",
  "What is the DSA pattern selection process? Show pattern matching for 5 different problem types.",
  "Show the two-pointer approach for Valid Palindrome II (at most one deletion).",
  "Explain monotonic stack. Show Next Greater Element using it.",
  "What is the binary search mid calculation overflow problem? Show the safe formula."
],
"businessScenarios": [
  "A warehouse system needs to find which SKU is missing from a sequence of barcode scans (0 to N). Implement using XOR for O(n) time and O(1) space.",
  "A conference scheduling system needs the minimum number of meeting rooms. Implement Meeting Rooms II with a min-heap.",
  "A search engine needs to find the shortest path between concept nodes in a knowledge graph. Implement BFS for minimum hops."
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
