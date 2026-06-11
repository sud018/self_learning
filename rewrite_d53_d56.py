"""Rewrite days 53-56: JPA Relationships, Transactions, Spring Security, JWT."""
import json, os
DATA_DIR = "backend/data/curriculum"

CURRICULUM = {

"day-053": {
"notes": """# JPA Relationships: @OneToMany, @ManyToOne, @ManyToMany, Cascade, and Orphan Removal

## @ManyToOne and @OneToMany — The Most Common Relationship
```java
// PARENT side (@OneToMany) — owns nothing, maps back to child
@Entity
public class Order {
    @Id private String id;

    @OneToMany(mappedBy = "order",           // "order" = field name in OrderItem
               cascade = CascadeType.ALL,    // persist/merge/remove propagates to items
               orphanRemoval = true,         // removing item from list deletes it from DB
               fetch = FetchType.LAZY)       // don't load items unless accessed
    private List<OrderItem> items = new ArrayList<>();

    // Helper methods to keep both sides in sync
    public void addItem(OrderItem item) {
        items.add(item);
        item.setOrder(this);
    }
    public void removeItem(OrderItem item) {
        items.remove(item);
        item.setOrder(null);
    }
}

// CHILD side (@ManyToOne) — owns the FK column
@Entity
@Table(name = "order_items")
public class OrderItem {
    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @ManyToOne(fetch = FetchType.LAZY)      // LAZY: don't load Order when loading item
    @JoinColumn(name = "order_id", nullable = false)  // FK column in order_items table
    private Order order;

    private String productId;
    private int quantity;
    private BigDecimal unitPrice;
}
```

## CascadeType — Propagating Operations
```java
CascadeType.PERSIST   // save parent → save children
CascadeType.MERGE     // update parent → update children
CascadeType.REMOVE    // delete parent → delete children (use with care!)
CascadeType.REFRESH   // refresh parent → refresh children
CascadeType.DETACH    // detach parent → detach children
CascadeType.ALL       // all of the above

// Example: CascadeType.ALL + orphanRemoval
Order order = new Order("customer-1");
order.addItem(new OrderItem("prod-1", 2, new BigDecimal("19.99")));
orderRepo.save(order);   // saves Order AND OrderItem (PERSIST cascade)

order.removeItem(item);  // removeItem → orphanRemoval deletes from DB at flush
```

## @OneToOne — Shared PK vs FK Strategy
```java
// Strategy 1: separate FK column (more common)
@Entity
public class User {
    @Id private String id;

    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private UserProfile profile;
}

@Entity
public class UserProfile {
    @Id private String id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", unique = true)  // unique constraint ensures 1-to-1
    private User user;
    private String bio;
    private String avatarUrl;
}

// Strategy 2: shared primary key (profile uses same PK as user)
@Entity
public class UserProfile {
    @Id private String userId;   // same value as User.id

    @OneToOne
    @MapsId                      // profile PK is mapped from user FK
    @JoinColumn(name = "user_id")
    private User user;
}
```

## @ManyToMany — Junction Table
```java
@Entity
public class Product {
    @Id private String id;

    @ManyToMany
    @JoinTable(name = "product_tags",
               joinColumns = @JoinColumn(name = "product_id"),
               inverseJoinColumns = @JoinColumn(name = "tag_id"))
    private Set<Tag> tags = new HashSet<>();  // Set prevents duplicate tags
}

@Entity
public class Tag {
    @Id private String id;
    private String name;

    @ManyToMany(mappedBy = "tags")   // non-owning side
    private Set<Product> products = new HashSet<>();
}

// @ManyToMany with extra columns on the join table → use a join entity instead
@Entity
@Table(name = "order_products")
public class OrderProduct {
    @Id private String id;

    @ManyToOne @JoinColumn(name = "order_id")   private Order order;
    @ManyToOne @JoinColumn(name = "product_id") private Product product;
    private int quantity;
    private BigDecimal negotiatedPrice;  // extra column — impossible with plain @ManyToMany
}
```

## Bidirectional vs Unidirectional
```java
// Unidirectional @ManyToOne — simpler, most use cases
@Entity
public class Comment {
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "post_id")
    private Post post;  // navigate from comment → post
    // Can't navigate post → comments without querying
}

// Bidirectional — more complex, keep both sides in sync
// The @OneToMany side must use mappedBy to point to the owning side
// Always update BOTH sides or Hibernate's first-level cache shows stale data
```

## Common Mistakes
1. **Missing mappedBy on @OneToMany:** without mappedBy, Hibernate creates a junction table. Only the @ManyToOne side owns the FK.
2. **Forgetting helper methods:** setting only one side of a bidirectional relationship — the other side stays null in memory (even if DB is correct) until the session reloads.
3. **CascadeType.REMOVE on @ManyToMany:** removes the tag entity entirely, not just the junction table row.
4. **EAGER on @OneToMany:** loads all children every time the parent loads — O(N) queries for a list of parents.
""",
"mcqs": [
  {"id":"d53q1","prompt":"In a bidirectional @OneToMany/@ManyToOne, which side owns the foreign key column?","options":["@OneToMany — it's the parent","@ManyToOne — it owns the FK column (JoinColumn). @OneToMany uses mappedBy to reference the owning side's field name","Both sides own the FK","Neither — a junction table stores it"],"correctAnswer":"@ManyToOne — it owns the FK column (JoinColumn). @OneToMany uses mappedBy to reference the owning side's field name","explanation":"The owning side has @JoinColumn — it controls the FK column in the DB. @OneToMany(mappedBy='order') means 'the Order field in OrderItem owns this relationship.' Without mappedBy, JPA creates an extra junction table."},
  {"id":"d53q2","prompt":"What does `orphanRemoval = true` do?","options":["Removes orphaned records from all tables","When a child entity is removed from the parent's collection, it is automatically deleted from the DB — even without explicitly calling delete()","Prevents insertion of orphan records","orphanRemoval only works with @OneToOne"],"correctAnswer":"When a child entity is removed from the parent's collection, it is automatically deleted from the DB — even without explicitly calling delete()","explanation":"order.removeItem(item) → item is detached from the parent collection. With orphanRemoval=true, Hibernate issues DELETE FROM order_items WHERE id=? at flush. Without it, item remains in DB with a null FK (or causes a constraint violation)."},
  {"id":"d53q3","prompt":"Why should @ManyToMany use `Set<Tag>` instead of `List<Tag>`?","options":["Set is faster","List allows duplicate entries — the same tag can appear twice in a product's tag list. Set enforces uniqueness and also avoids Hibernate's extra DELETE+INSERT when reordering","Set uses less memory","Hibernate only supports Set for @ManyToMany"],"correctAnswer":"List allows duplicate entries — the same tag can appear twice in a product's tag list. Set enforces uniqueness and also avoids Hibernate's extra DELETE+INSERT when reordering","explanation":"With List, if you add the same tag twice, Hibernate inserts duplicate junction rows. Also, Hibernate has a known issue with @ManyToMany List: on any modification it deletes all rows and re-inserts — extremely inefficient. Use Set."},
  {"id":"d53q4","prompt":"When should you use a join entity instead of @ManyToMany?","options":["Always — @ManyToMany is deprecated","When the junction table has extra columns (quantity, price, date) — @ManyToMany cannot map extra columns; the join entity (@ManyToOne on both sides + extra fields) handles this","When there are more than 1000 entities","For bidirectional relationships only"],"correctAnswer":"When the junction table has extra columns (quantity, price, date) — @ManyToMany cannot map extra columns; the join entity (@ManyToOne on both sides + extra fields) handles this","explanation":"@ManyToMany only maps the junction table's two FK columns. OrderProduct with quantity and negotiatedPrice requires a full entity: @ManyToOne to Order, @ManyToOne to Product, plus extra fields. This is the standard pattern for 'rich' many-to-many relationships."},
  {"id":"d53q5","prompt":"What happens if you forget `mappedBy` on the @OneToMany side?","options":["A compile error","Hibernate creates an extra junction table (order_order_items or similar) in addition to the FK column in order_items — data is stored twice","The relationship is ignored","Only the @ManyToOne side persists"],"correctAnswer":"Hibernate creates an extra junction table (order_order_items or similar) in addition to the FK column in order_items — data is stored twice","explanation":"Without mappedBy, Hibernate treats @OneToMany as the owning side and creates a junction table. The @ManyToOne side also has its own FK. Both store the same relationship redundantly. Always add mappedBy='fieldName' to the @OneToMany side."},
  {"id":"d53q6","prompt":"Why is `CascadeType.REMOVE` on @ManyToMany dangerous?","options":["It has no effect on @ManyToMany","It deletes the related entities (e.g., Tag objects) entirely from the DB — not just the junction table row. A tag deleted because one product removes it disappears for ALL products","CascadeType.REMOVE is only for @OneToOne","It causes a StackOverflowError"],"correctAnswer":"It deletes the related entities (e.g., Tag objects) entirely from the DB — not just the junction table row. A tag deleted because one product removes it disappears for ALL products","explanation":"product.getTags().remove(tag) with CascadeType.REMOVE → Hibernate deletes the Tag entity, not just the product_tags row. The tag vanishes from all other products too. For @ManyToMany, only cascade PERSIST and MERGE. Let the junction table row be deleted by the collection management, not the entity."},
  {"id":"d53q7","prompt":"What is the purpose of helper methods (addItem/removeItem) in a bidirectional relationship?","options":["Required by JPA spec","Keeps both sides of the relationship in sync in memory — without them, the in-memory object graph is inconsistent (one side reflects the change, the other doesn't) until the session reloads from DB","Helper methods trigger cascade operations","They replace @JoinColumn"],"correctAnswer":"Keeps both sides of the relationship in sync in memory — without them, the in-memory object graph is inconsistent (one side reflects the change, the other doesn't) until the session reloads from DB","explanation":"order.getItems().add(item) adds to the collection, but item.getOrder() is still null in memory. The DB may be correct (after save/flush), but within the same transaction, item.getOrder() == null. Helper methods: items.add(item); item.setOrder(this) — both sides updated atomically."},
  {"id":"d53q8","prompt":"What does `@MapsId` do in a @OneToOne relationship?","options":["Maps the ID to a sequence","Makes the child entity use the same primary key as the parent entity — the child's PK is the FK pointing to the parent","Generates a UUID for the child","@MapsId is only for @ManyToOne"],"correctAnswer":"Makes the child entity use the same primary key as the parent entity — the child's PK is the FK pointing to the parent","explanation":"@MapsId: UserProfile.userId = User.id. No separate PK generation — the PK is shared with the parent. Efficient: only one row per user in user_profiles, no extra unique constraint needed (the PK IS the FK). Simplifies lookups: profileRepo.findById(userId)."},
  {"id":"d53q9","prompt":"For a @OneToOne relationship, which side should be LAZY and which should own the FK?","options":["Both sides should be EAGER","The owning side has @JoinColumn; both sides should be LAZY (FetchType.LAZY) — the non-owning side (mappedBy) is particularly important to make LAZY because Hibernate always checks for the associated entity","Only the owning side needs LAZY","@OneToOne cannot be LAZY"],"correctAnswer":"The owning side has @JoinColumn; both sides should be LAZY (FetchType.LAZY) — the non-owning side (mappedBy) is particularly important to make LAZY because Hibernate always checks for the associated entity","explanation":"@OneToOne LAZY on non-owning side requires bytecode enhancement (Hibernate instruments the class) or a proxy. Without it, Hibernate loads the associated entity regardless. For @OneToOne, the owning side is easier to make lazy. Prefer @OneToOne on the less-frequently-loaded entity as the owning side."},
  {"id":"d53q10","prompt":"What SQL does `CascadeType.PERSIST` generate when saving a new Order with two new OrderItems?","options":["Three separate INSERT statements","One INSERT for Order and two INSERTs for OrderItems — all in one transaction. Without PERSIST cascade, items must be saved explicitly","CascadeType.PERSIST only affects the parent","One batch INSERT for all three"],"correctAnswer":"One INSERT for Order and two INSERTs for OrderItems — all in one transaction. Without PERSIST cascade, items must be saved explicitly","explanation":"orderRepo.save(order) with CascadeType.PERSIST or ALL: Hibernate cascades the PERSIST operation to all items in order.items. Generates INSERT INTO orders + 2x INSERT INTO order_items. Without cascade, only the Order is saved and item FKs would point to a non-existent order."}
],
"writtenConceptQuestions": [
  "Show a complete Order/OrderItem bidirectional @OneToMany/@ManyToOne mapping with addItem/removeItem helper methods, cascade ALL, and orphanRemoval.",
  "Explain CascadeType options. When is CascadeType.REMOVE dangerous? Show the bug with @ManyToMany cascade remove.",
  "Design a Product/Tag @ManyToMany with a junction table. Show when to use Set vs List and why the List has a Hibernate bug.",
  "Show a join entity for Order/Product with quantity and price fields. Explain why plain @ManyToMany can't handle this.",
  "What is orphanRemoval? Show removing an item from an order and the resulting SQL without calling delete explicitly.",
  "Explain @MapsId for @OneToOne shared primary key. Show User/UserProfile with shared PK and how findById(userId) works on the profile.",
  "What is the difference between the owning side and the inverse side of a JPA relationship? Which side controls the FK column?"
],
"businessScenarios": [
  "An order management system creates an order and manually saves each OrderItem separately (5 save() calls per order). Redesign with CascadeType.ALL so one orderRepo.save(order) persists the entire aggregate.",
  "A product catalog has @ManyToMany(cascade=ALL) between Product and Tag. Deleting a product removes all its tags from the system, breaking other products. Fix by removing CascadeType.REMOVE from the @ManyToMany.",
  "An order item update adds new items but orphaned items remain in the DB with null FKs. Add orphanRemoval=true and update the helper method so removed items are cleaned up automatically."
]
},

"day-054": {
"notes": """# Transactions in Spring Boot: @Transactional, Propagation, Isolation, and Rollback Rules

## @Transactional — How It Works
Spring AOP wraps the method in a transaction proxy. The transaction begins before the method executes and commits (or rolls back) when it returns.
```java
@Service
public class OrderService {

    // Starts a transaction, commits on success, rolls back on RuntimeException
    @Transactional
    public OrderDto createOrder(CreateOrderRequest req) {
        Order order = new Order(req.customerId());
        req.items().forEach(item -> order.addItem(new OrderItem(item)));
        Order saved = orderRepo.save(order);                 // INSERT
        inventoryService.deductStock(req.items());           // UPDATE inventory
        notificationService.scheduleConfirmation(saved.getId()); // INSERT notification
        return mapper.toDto(saved);
        // All three operations commit together — or all roll back
    }
}
```

## Rollback Rules — What Triggers Rollback
```java
// DEFAULT: rolls back on unchecked exceptions (RuntimeException and its subclasses)
// DEFAULT: does NOT roll back on checked exceptions (IOException, SQLException)

// Override rollback rules:
@Transactional(rollbackFor = IOException.class)         // roll back for IOException too
@Transactional(noRollbackFor = BusinessException.class) // don't roll back for BusinessException

// Example: checked exception that SHOULD roll back
@Transactional(rollbackFor = Exception.class)
public void importFromFile(Path file) throws IOException {
    List<Product> products = parseFile(file);  // throws IOException
    productRepo.saveAll(products);
    // IOException rolls back the saveAll even though it's checked
}
```

## Propagation — How Nested Transactions Behave
```java
// REQUIRED (default) — join existing or create new
@Transactional(propagation = Propagation.REQUIRED)
public void serviceMethodA() {
    serviceMethodB(); // B joins A's transaction — same commit/rollback
}

// REQUIRES_NEW — always start fresh, suspend outer
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void auditLog(String event) {
    // Committed independently — audit saved even if outer tx rolls back
    auditRepo.save(new AuditEntry(event));
}

// SUPPORTS — use current tx if available, else no tx
// NOT_SUPPORTED — suspend current tx, run without tx
// NEVER — fail if a tx exists
// MANDATORY — fail if NO tx exists
// NESTED — nested savepoint (rollback to savepoint, not entire tx)
```

## Self-Invocation Problem
```java
@Service
public class OrderService {
    // PROBLEM: calling another @Transactional method on 'this' bypasses the proxy
    public void createAndNotify(CreateOrderRequest req) {
        createOrder(req);       // direct call — NO transaction! proxy is bypassed
        sendNotification(req);
    }

    @Transactional
    public OrderDto createOrder(CreateOrderRequest req) { ... }
}

// FIXES:
// Fix 1: inject self and call through the proxy
@Autowired private OrderService self; // Spring injects the proxy
self.createOrder(req);

// Fix 2: extract to a separate bean
// Fix 3: use ApplicationContext.getBean(OrderService.class).createOrder(req)
```

## Isolation Levels — Handling Concurrent Transactions
```java
// READ_UNCOMMITTED — can read dirty (uncommitted) data from other tx (fastest, least safe)
// READ_COMMITTED  — only reads committed data; non-repeatable reads possible (PostgreSQL default)
// REPEATABLE_READ — same rows always return same data within a tx; phantom reads possible (MySQL default)
// SERIALIZABLE    — strictest; full isolation; slowest

@Transactional(isolation = Isolation.REPEATABLE_READ)
public ReportDto generateMonthlyReport() {
    // Multiple reads within this tx always return the same data
    BigDecimal revenue  = orderRepo.sumRevenue(month);
    long orderCount     = orderRepo.countByMonth(month);
    // Without REPEATABLE_READ, a concurrent insert between the two reads would give inconsistent stats
    return new ReportDto(revenue, orderCount);
}
```

## Read-Only Transactions
```java
@Transactional(readOnly = true)
public List<OrderDto> findAll() {
    // Hibernate skips dirty-check snapshot: faster
    // Some JDBC drivers optimize: no write lock on connection
    return orderRepo.findAll().stream().map(mapper::toDto).collect(toList());
}
```

## Transaction Boundary Best Practices
```java
// Keep transactions as SHORT as possible — long transactions hold DB locks
@Transactional
public void processPayment(String orderId) {
    Order order = orderRepo.findById(orderId).orElseThrow();
    order.setStatus(PROCESSING);
    // DON'T do: call external payment API inside transaction — holds DB lock during HTTP call
}

// Correct: call external API OUTSIDE the transaction
public void processPayment(String orderId) {
    PaymentResult result = paymentGateway.charge(order); // outside @Transactional
    updateOrderStatus(orderId, result);                   // short @Transactional
}

@Transactional
private void updateOrderStatus(String orderId, PaymentResult result) { ... }
```

## Common Mistakes
1. **@Transactional on private methods:** AOP proxies cannot intercept private method calls. Use protected or public.
2. **Self-invocation:** `this.transactionalMethod()` bypasses the proxy — no transaction started.
3. **Checked exceptions don't roll back by default:** must add `rollbackFor = Exception.class` or use unchecked exceptions.
4. **Long transactions with external HTTP calls:** holds DB connections and locks during network latency.
""",
"mcqs": [
  {"id":"d54q1","prompt":"What does @Transactional do by default when a RuntimeException is thrown?","options":["Commits the transaction","Rolls back the entire transaction — all DB changes in that method and any REQUIRED-propagated methods are undone","Logs the exception and commits","Retries the operation"],"correctAnswer":"Rolls back the entire transaction — all DB changes in that method and any REQUIRED-propagated methods are undone","explanation":"Default rollback rule: RuntimeException (unchecked) → rollback. Checked exceptions (IOException, etc.) → commit by default. To roll back on checked exceptions: @Transactional(rollbackFor = IOException.class)."},
  {"id":"d54q2","prompt":"Why does calling a @Transactional method via `this.method()` not start a transaction?","options":["this. is not allowed in Spring","Spring @Transactional works via AOP proxy — calling through `this` bypasses the proxy and calls the raw method directly without transaction management","@Transactional only works on injected beans","Private methods can be transactional with this."],"correctAnswer":"Spring @Transactional works via AOP proxy — calling through `this` bypasses the proxy and calls the raw method directly without transaction management","explanation":"Spring wraps your bean in a proxy. When an external caller calls orderService.create(), it goes through the proxy (which starts a transaction). When your own code calls this.create(), it skips the proxy entirely — no transaction. Fix: inject self and call via the proxy, or restructure into separate beans."},
  {"id":"d54q3","prompt":"What does `Propagation.REQUIRES_NEW` do?","options":["Requires a new database connection","Suspends the current transaction and starts a completely new independent transaction — the new transaction can commit even if the outer transaction later rolls back","Creates a savepoint in the current transaction","REQUIRES_NEW is only for read operations"],"correctAnswer":"Suspends the current transaction and starts a completely new independent transaction — the new transaction can commit even if the outer transaction later rolls back","explanation":"Use case: audit logging. auditLog() with REQUIRES_NEW commits its audit entry regardless of what happens in the calling transaction. If createOrder() rolls back, the audit entry (recording the attempt) is still saved."},
  {"id":"d54q4","prompt":"What is a non-repeatable read and which isolation level prevents it?","options":["Reading a null value","A transaction reads the same row twice and gets different results because another transaction modified it between reads. REPEATABLE_READ and SERIALIZABLE isolation levels prevent this","Reading from a deleted table","Reading uncommitted data"],"correctAnswer":"A transaction reads the same row twice and gets different results because another transaction modified it between reads. REPEATABLE_READ and SERIALIZABLE isolation levels prevent this","explanation":"Non-repeatable read: read price=100, another tx updates price=200, read price=100 again in same tx → 200 (different!). REPEATABLE_READ: first read creates a snapshot; all subsequent reads in the tx see the same snapshot. Prevents price changing mid-transaction."},
  {"id":"d54q5","prompt":"Why should external API calls NOT be made inside a @Transactional method?","options":["External calls throw exceptions","The transaction holds a DB connection and DB locks during the entire HTTP call duration — a slow API (2+ seconds) blocks connections in the pool and starves other requests","External calls don't support transactions","@Transactional doesn't work with RestTemplate"],"correctAnswer":"The transaction holds a DB connection and DB locks during the entire HTTP call duration — a slow API (2+ seconds) blocks connections in the pool and starves other requests","explanation":"DB connection pools (HikariCP default: 10 connections). If 10 requests each wait 2s for an external API inside @Transactional, all 10 connections are busy — the 11th request waits indefinitely. Keep transactions short: call the API first, then start the transaction just for the DB writes."},
  {"id":"d54q6","prompt":"What does `@Transactional(readOnly = true)` optimize?","options":["Prevents any writes inside the method","Skips Hibernate's dirty-check snapshot creation, reducing memory and CPU — also hints to JDBC drivers for connection optimization","Makes reads faster by using a read replica automatically","Required for all select operations"],"correctAnswer":"Skips Hibernate's dirty-check snapshot creation, reducing memory and CPU — also hints to JDBC drivers for connection optimization","explanation":"Without readOnly=true, Hibernate copies every loaded entity into a snapshot for dirty checking. readOnly=true skips this — no snapshots, no dirty check. For methods loading 1000 entities, this saves significant memory. PostgreSQL/MySQL drivers may also use read-only connection optimizations."},
  {"id":"d54q7","prompt":"What is the default isolation level for most production databases?","options":["SERIALIZABLE","READ_COMMITTED — PostgreSQL's default. MySQL defaults to REPEATABLE_READ","READ_UNCOMMITTED","Spring always uses SERIALIZABLE"],"correctAnswer":"READ_COMMITTED — PostgreSQL's default. MySQL defaults to REPEATABLE_READ","explanation":"READ_COMMITTED (PostgreSQL default): reads only see committed data. Non-repeatable reads are possible (same row read twice may differ). REPEATABLE_READ (MySQL/InnoDB default): prevents non-repeatable reads, allows phantom reads. Most apps work fine with READ_COMMITTED; use REPEATABLE_READ or SERIALIZABLE only when needed."},
  {"id":"d54q8","prompt":"What does `@Transactional` on a private method do?","options":["Creates a transaction as expected","Nothing — Spring AOP cannot create a proxy for private methods. The annotation is silently ignored","Throws a compile error","Works only in @Service classes"],"correctAnswer":"Nothing — Spring AOP cannot create a proxy for private methods. The annotation is silently ignored","explanation":"Spring's AOP proxy (CGLIB) works by subclassing your bean. Private methods cannot be overridden in subclasses — the proxy cannot intercept the call. @Transactional on private methods is silently ignored. Use public or protected."},
  {"id":"d54q9","prompt":"What is a dirty read and which isolation level allows it?","options":["Reading a null value","Reading uncommitted data from another transaction — if that transaction rolls back, you read data that never officially existed. READ_UNCOMMITTED allows this","Reading deleted rows","Non-repeatable reads"],"correctAnswer":"Reading uncommitted data from another transaction — if that transaction rolls back, you read data that never officially existed. READ_UNCOMMITTED allows this","explanation":"READ_UNCOMMITTED: tx A updates order status to SHIPPED but hasn't committed. tx B reads status=SHIPPED. tx A rolls back (status stays PENDING). tx B acted on data that never officially existed. Almost never used in production — no real performance benefit over READ_COMMITTED."},
  {"id":"d54q10","prompt":"What is `Propagation.NESTED` and how does it differ from REQUIRES_NEW?","options":["Identical to REQUIRES_NEW","NESTED creates a savepoint within the current transaction — rolling back the nested part returns to the savepoint without affecting the outer tx; REQUIRES_NEW creates a completely separate transaction that commits independently","NESTED creates a sub-transaction in a different DB","NESTED only works with JPA"],"correctAnswer":"NESTED creates a savepoint within the current transaction — rolling back the nested part returns to the savepoint without affecting the outer tx; REQUIRES_NEW creates a completely separate transaction that commits independently","explanation":"NESTED: if the nested part fails, rollback to the savepoint, outer tx can still commit. REQUIRES_NEW: if the inner tx commits and the outer rolls back, the inner's changes persist. Use NESTED when you want partial rollback within a transaction."}
],
"writtenConceptQuestions": [
  "Show a createOrder() method with @Transactional that saves an order, deducts inventory, and schedules a notification — all atomically. Show what happens when inventoryService throws RuntimeException.",
  "Explain the self-invocation problem with Spring @Transactional. Show the bug and three ways to fix it.",
  "Describe all Propagation types with a one-line use case for each. Show REQUIRES_NEW for audit logging that persists even on outer transaction rollback.",
  "What are the four isolation levels? Show a report generation bug (inconsistent stats) and fix with REPEATABLE_READ.",
  "Why should @Transactional methods never make external HTTP calls? Show the connection pool exhaustion scenario.",
  "What rollback rules apply to checked vs unchecked exceptions by default? Show a file import method that should roll back on IOException.",
  "What does readOnly=true optimize? Show a service read method with and without readOnly and explain the performance difference."
],
"businessScenarios": [
  "An order creation fails halfway through (inventory deduction throws): the order is saved but inventory isn't deducted. This leaves a corrupted state. Add @Transactional so both operations are atomic.",
  "An audit service needs to log every order creation attempt even when the order creation fails. Currently the audit record is rolled back with the order. Fix using REQUIRES_NEW propagation.",
  "A payment processing method calls an external Stripe API inside @Transactional — 30-second timeouts are exhausting the DB connection pool. Extract the Stripe call outside the transaction boundary."
]
},

"day-055": {
"notes": """# Spring Security: Authentication, Authorization, and SecurityFilterChain

## The Security Filter Chain
Spring Security is a chain of servlet filters. Every HTTP request passes through them in order:
```
Request → SecurityContextPersistenceFilter → UsernamePasswordAuthenticationFilter
        → ExceptionTranslationFilter → FilterSecurityInterceptor → Controller
```
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())           // disable for REST APIs (use JWT instead)
            .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()           // public endpoints
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.GET, "/api/products/**").hasAnyRole("USER","ADMIN")
                .requestMatchers("/api/orders/**").authenticated()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12); // cost factor 12 = ~300ms per hash
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config)
            throws Exception {
        return config.getAuthenticationManager();
    }
}
```

## UserDetailsService — Loading Users
```java
@Service
public class UserDetailsServiceImpl implements UserDetailsService {

    private final UserRepository userRepo;

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        User user = userRepo.findByEmail(email.toLowerCase())
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + email));

        return org.springframework.security.core.userdetails.User.builder()
            .username(user.getEmail())
            .password(user.getPasswordHash())   // already BCrypt-hashed
            .roles(user.getRole().name())        // ADMIN → ROLE_ADMIN
            .accountLocked(!user.isActive())
            .build();
    }
}
```

## Password Encoding
```java
// Registration — encode password before saving
@Transactional
public UserDto register(RegisterRequest req) {
    if (userRepo.existsByEmail(req.email())) {
        throw new ConflictException("Email already registered");
    }
    User user = new User();
    user.setEmail(req.email().toLowerCase());
    user.setPasswordHash(passwordEncoder.encode(req.password())); // BCrypt hash
    user.setRole(Role.USER);
    return mapper.toDto(userRepo.save(user));
}

// Login — verify password
@Transactional(readOnly = true)
public AuthResponse login(LoginRequest req) {
    User user = userRepo.findByEmail(req.email())
        .orElseThrow(() -> new UnauthorizedException("Invalid credentials"));
    if (!passwordEncoder.matches(req.password(), user.getPasswordHash())) {
        throw new UnauthorizedException("Invalid credentials"); // same message — no enumeration
    }
    String token = jwtService.generateToken(user);
    return new AuthResponse(token, mapper.toDto(user));
}
```

## Method-Level Security
```java
@Configuration
@EnableMethodSecurity    // enables @PreAuthorize, @PostAuthorize, @Secured
public class MethodSecurityConfig {}

@RestController
public class OrderController {
    @GetMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or @orderSecurityService.isOwner(#id, authentication)")
    public OrderDto getOrder(@PathVariable String id) { ... }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteOrder(@PathVariable String id) { ... }
}

// Custom security expression
@Service("orderSecurityService")
public class OrderSecurityService {
    public boolean isOwner(String orderId, Authentication auth) {
        return orderRepo.existsByIdAndCustomerEmail(orderId, auth.getName());
    }
}
```

## Getting the Current User
```java
// From SecurityContext (available anywhere in the request thread)
Authentication auth = SecurityContextHolder.getContext().getAuthentication();
String username = auth.getName();

// In controller via @AuthenticationPrincipal
@GetMapping("/me")
public UserDto getProfile(@AuthenticationPrincipal UserDetails userDetails) {
    return userService.findByEmail(userDetails.getUsername());
}
```

## Common Mistakes
1. **Returning different error messages for wrong user vs wrong password:** helps attackers enumerate valid emails. Always return "Invalid credentials" for both.
2. **Storing plain-text passwords:** always BCrypt with cost ≥ 10. Never MD5/SHA-1.
3. **csrf().disable() without JWT:** CSRF protection is essential for cookie-based session auth. Only disable for stateless JWT APIs.
4. **permitAll() before authenticated() but anyRequest() order:** Spring evaluates rules top-to-bottom — put specific rules before generic ones.
""",
"mcqs": [
  {"id":"d55q1","prompt":"What does `SessionCreationPolicy.STATELESS` do?","options":["Disables sessions entirely in the app","Tells Spring Security to never create or use HTTP sessions — each request must carry credentials (JWT token) in the header. Required for stateless REST APIs","Makes sessions expire immediately","Forces re-authentication every request"],"correctAnswer":"Tells Spring Security to never create or use HTTP sessions — each request must carry credentials (JWT token) in the header. Required for stateless REST APIs","explanation":"STATELESS: no HttpSession created for security context storage. Every request is independent — the JWT filter validates the token on each request. This makes the API horizontally scalable (no session affinity needed)."},
  {"id":"d55q2","prompt":"Why should login failure return 'Invalid credentials' for both wrong email AND wrong password?","options":["Simpler code","Returning 'User not found' vs 'Wrong password' lets attackers enumerate valid email addresses. A uniform message prevents this user enumeration attack","Better UX","Required by OWASP"],"correctAnswer":"Returning 'User not found' vs 'Wrong password' lets attackers enumerate valid email addresses. A uniform message prevents this user enumeration attack","explanation":"Attacker tries john@example.com: 'User not found' → user doesn't exist. Tries jane@example.com: 'Wrong password' → valid account found. Attacker now has a valid email to brute-force. Always return the same message for both failure cases."},
  {"id":"d55q3","prompt":"What does `BCryptPasswordEncoder(12)` do — what is the significance of 12?","options":["Creates 12 hash variants","12 is the cost factor (work factor) — BCrypt performs 2^12 iterations, making each hash ~300ms. Higher cost slows brute-force attacks but also slows legitimate logins","Generates a 12-character password","12 is the salt length"],"correctAnswer":"12 is the cost factor (work factor) — BCrypt performs 2^12 iterations, making each hash ~300ms. Higher cost slows brute-force attacks but also slows legitimate logins","explanation":"BCrypt cost factor: 10 ≈ 100ms, 12 ≈ 300ms, 14 ≈ 1200ms. 300ms per login is acceptable UX. An attacker attempting 1M passwords/second slows to ~3,333/second. Increase cost as hardware gets faster to maintain the same security margin."},
  {"id":"d55q4","prompt":"What is `@PreAuthorize('hasRole(\"ADMIN\") or @orderSecurityService.isOwner(#id, authentication)')` doing?","options":["Checks a database role","Evaluates a SpEL expression before the method executes: grants access if user has ADMIN role OR if the custom isOwner() service method returns true","@PreAuthorize only works with roles","#id refers to the method return value"],"correctAnswer":"Evaluates a SpEL expression before the method executes: grants access if user has ADMIN role OR if the custom isOwner() service method returns true","explanation":"@PreAuthorize uses SpEL. #id binds to the method parameter named id. @orderSecurityService resolves the Spring bean. authentication is the current SecurityContext authentication. This enables fine-grained access control that can't be expressed with simple URL patterns."},
  {"id":"d55q5","prompt":"What does `UserDetailsService.loadUserByUsername()` return?","options":["The User entity from the database","A UserDetails object — Spring's security abstraction containing username, encoded password, and granted authorities. Spring Security uses it to authenticate and authorize, not your domain User entity","The username as a String","An Authentication object"],"correctAnswer":"A UserDetails object — Spring's security abstraction containing username, encoded password, and granted authorities. Spring Security uses it to authenticate and authorize, not your domain User entity","explanation":"Spring Security doesn't know about your User JPA entity. loadUserByUsername() bridges your user store to Spring Security's UserDetails interface. The returned UserDetails.getPassword() must be the BCrypt-hashed password for passwordEncoder.matches() to work."},
  {"id":"d55q6","prompt":"Why should CSRF protection NOT be disabled for cookie-based authentication?","options":["CSRF is not a real attack","CSRF attacks trick a logged-in user's browser into making requests using their session cookie. Without CSRF tokens, a malicious site can submit forms on behalf of the user using their cookie","CSRF slows performance","Cookie authentication is deprecated"],"correctAnswer":"CSRF attacks trick a logged-in user's browser into making requests using their session cookie. Without CSRF tokens, a malicious site can submit forms on behalf of the user using their cookie","explanation":"CSRF: user logs into bank.com (cookie set), visits evil.com, which has a hidden form posting to bank.com/transfer. Browser sends the bank cookie → transfer executes. CSRF tokens prevent this. For JWT (Authorization header), CSRF is irrelevant — browsers don't auto-send headers from other sites."},
  {"id":"d55q7","prompt":"What does `@EnableMethodSecurity` enable?","options":["Enables the security filter chain","Enables @PreAuthorize, @PostAuthorize, @Secured, @RolesAllowed annotations on methods — method-level authorization in addition to URL-based rules","Enables HTTPS","Enables CSRF protection"],"correctAnswer":"Enables @PreAuthorize, @PostAuthorize, @Secured, @RolesAllowed annotations on methods — method-level authorization in addition to URL-based rules","explanation":"Without @EnableMethodSecurity, @PreAuthorize annotations on methods are silently ignored. With it, Spring creates AOP proxies around annotated methods that evaluate the security expression before (Pre) or after (Post) execution. Replaces the older @EnableGlobalMethodSecurity."},
  {"id":"d55q8","prompt":"What is the difference between `hasRole('ADMIN')` and `hasAuthority('ROLE_ADMIN')`?","options":["Identical","hasRole('ADMIN') automatically prepends 'ROLE_' → checks for 'ROLE_ADMIN'. hasAuthority('ROLE_ADMIN') checks the exact authority string. Spring Security prefixes roles with ROLE_ by convention","hasAuthority is deprecated","hasRole only works with @Secured"],"correctAnswer":"hasRole('ADMIN') automatically prepends 'ROLE_' → checks for 'ROLE_ADMIN'. hasAuthority('ROLE_ADMIN') checks the exact authority string. Spring Security prefixes roles with ROLE_ by convention","explanation":"By convention, roles are prefixed with ROLE_. User.roles('ADMIN') stores ROLE_ADMIN. hasRole('ADMIN') = hasAuthority('ROLE_ADMIN'). For fine-grained permissions (READ_PRODUCTS, WRITE_ORDERS) without the prefix, use hasAuthority()."},
  {"id":"d55q9","prompt":"What is `@AuthenticationPrincipal` in a controller method parameter?","options":["Injects the request principal string","Injects the current user's UserDetails (or custom principal) object directly from the SecurityContext — cleaner than SecurityContextHolder.getContext().getAuthentication()","Creates a new authentication","Required for all authenticated endpoints"],"correctAnswer":"Injects the current user's UserDetails (or custom principal) object directly from the SecurityContext — cleaner than SecurityContextHolder.getContext().getAuthentication()","explanation":"@AuthenticationPrincipal UserDetails user in a controller method: Spring resolves the current user from SecurityContext and injects it. If using a custom UserDetailsImpl, type it as @AuthenticationPrincipal UserDetailsImpl user to access custom fields like userId."},
  {"id":"d55q10","prompt":"Why does the order of `authorizeHttpRequests` rules matter?","options":["Order is alphabetical","Spring Security evaluates rules top-to-bottom and stops at the first match — specific rules must come before general ones, or they may never be reached","All rules are evaluated","Order only matters for ADMIN rules"],"correctAnswer":"Spring Security evaluates rules top-to-bottom and stops at the first match — specific rules must come before general ones, or they may never be reached","explanation":"If anyRequest().authenticated() comes before .requestMatchers('/api/auth/**').permitAll(), the general rule matches first and /api/auth requires authentication — login is impossible. Always: most specific first, most general last."}
],
"writtenConceptQuestions": [
  "Show a complete SecurityFilterChain: STATELESS, CSRF disabled, permitAll for /api/auth/**, hasRole('ADMIN') for admin paths, authenticated() for everything else, with a JWT filter.",
  "Implement UserDetailsService.loadUserByUsername() loading a user from UserRepository. Show how roles map to Spring Security authorities.",
  "Show registration and login: BCrypt encode on save, passwordEncoder.matches() on login, same error message for wrong email/password.",
  "Explain @PreAuthorize with a custom security expression bean. Show an order endpoint accessible by ADMIN or the order owner.",
  "What is the self-invocation problem with @PreAuthorize? When does method security not work?",
  "Explain CSRF: what the attack is, why JWT APIs don't need CSRF protection, and when you must keep it enabled.",
  "Show getting the current authenticated user: via SecurityContextHolder, via @AuthenticationPrincipal, and via a custom getCurrentUser() utility."
],
"businessScenarios": [
  "Users can view other users' orders by guessing order IDs. Add @PreAuthorize that allows ADMIN full access and regular users only their own orders using a custom isOwner() service method.",
  "The login endpoint returns 'User not found' for non-existent emails, enabling user enumeration. Fix to return 'Invalid credentials' for all authentication failures.",
  "A public product catalog endpoint is accidentally protected by .authenticated(). The rule order is wrong — anyRequest().authenticated() comes before the permitAll() rule. Fix the rule ordering."
]
},

"day-056": {
"notes": """# JWT in Spring Boot: Token Generation, Validation Filter, and Refresh Tokens

## What is JWT?
A JSON Web Token has three Base64URL-encoded parts separated by dots:
```
Header.Payload.Signature
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzE3MzQ0MDAwLCJleHAiOjE3MTczNTEyMDB9.abc123...

Header:  { "alg": "HS256", "typ": "JWT" }
Payload: { "sub": "user@example.com", "role": "USER", "iat": 1717344000, "exp": 1717351200 }
Signature: HMACSHA256(base64(header) + "." + base64(payload), secretKey)
```
The server verifies the signature without a DB lookup — stateless authentication.

## JwtService — Token Generation and Validation
```java
@Service
public class JwtService {
    @Value("${app.jwt.secret}")           private String secret;
    @Value("${app.jwt.expiration-ms:3600000}") private long expirationMs; // 1 hour

    // Generate token
    public String generateToken(User user) {
        return Jwts.builder()
            .subject(user.getEmail())
            .claim("role", user.getRole().name())
            .claim("userId", user.getId())
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expirationMs))
            .signWith(getSigningKey(), Jwts.SIG.HS256)
            .compact();
    }

    // Extract claims
    public String extractEmail(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public boolean isTokenValid(String token, UserDetails userDetails) {
        String email = extractEmail(token);
        return email.equals(userDetails.getUsername()) && !isTokenExpired(token);
    }

    private boolean isTokenExpired(String token) {
        return extractClaim(token, Claims::getExpiration).before(new Date());
    }

    private <T> T extractClaim(String token, Function<Claims, T> resolver) {
        Claims claims = Jwts.parser()
            .verifyWith(getSigningKey())
            .build()
            .parseSignedClaims(token)
            .getPayload();
        return resolver.apply(claims);
    }

    private SecretKey getSigningKey() {
        byte[] keyBytes = Decoders.BASE64.decode(secret);
        return Keys.hmacShaKeyFor(keyBytes);
    }
}
```

## JWT Authentication Filter
```java
@Component
@RequiredArgsConstructor
public class JwtAuthFilter extends OncePerRequestFilter {
    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest req,
                                    HttpServletResponse res,
                                    FilterChain chain)
            throws ServletException, IOException {
        String authHeader = req.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            chain.doFilter(req, res);   // no token — let next filter handle (may return 401)
            return;
        }

        String token = authHeader.substring(7); // strip "Bearer "
        try {
            String email = jwtService.extractEmail(token);

            if (email != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                UserDetails userDetails = userDetailsService.loadUserByUsername(email);

                if (jwtService.isTokenValid(token, userDetails)) {
                    UsernamePasswordAuthenticationToken authToken =
                        new UsernamePasswordAuthenticationToken(
                            userDetails, null, userDetails.getAuthorities());
                    authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(req));
                    SecurityContextHolder.getContext().setAuthentication(authToken);
                }
            }
        } catch (JwtException e) {
            // Invalid/expired token — SecurityContext stays empty → 401 from filter chain
            log.debug("Invalid JWT: {}", e.getMessage());
        }
        chain.doFilter(req, res);
    }
}
```

## Auth Controller — Login and Registration
```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @PostMapping("/register")
    @ResponseStatus(HttpStatus.CREATED)
    public UserDto register(@RequestBody @Valid RegisterRequest req) {
        return authService.register(req);
    }

    @PostMapping("/login")
    public AuthResponse login(@RequestBody @Valid LoginRequest req) {
        return authService.login(req);
    }

    @PostMapping("/refresh")
    public AuthResponse refresh(@RequestBody RefreshRequest req) {
        return authService.refreshToken(req.refreshToken());
    }
}

public record AuthResponse(String accessToken, String refreshToken, UserDto user) {}
```

## Refresh Token Pattern
```java
// Access token: short-lived (15-60 min), stored in memory
// Refresh token: long-lived (7-30 days), stored in DB, used to get new access token
@Entity
public class RefreshToken {
    @Id private String id;
    @Column(unique = true) private String token;
    private String userEmail;
    private Instant expiresAt;
    private boolean revoked = false;
}

@Service
public class AuthService {
    public AuthResponse refreshToken(String refreshToken) {
        RefreshToken stored = refreshTokenRepo.findByToken(refreshToken)
            .orElseThrow(() -> new UnauthorizedException("Invalid refresh token"));
        if (stored.isRevoked() || stored.getExpiresAt().isBefore(Instant.now())) {
            throw new UnauthorizedException("Refresh token expired or revoked");
        }
        User user = userRepo.findByEmail(stored.getUserEmail()).orElseThrow();
        String newAccessToken = jwtService.generateToken(user);
        return new AuthResponse(newAccessToken, refreshToken, mapper.toDto(user));
    }
}
```

## Security Configuration for JWT
```properties
# application.properties — JWT secret (use 256-bit Base64-encoded key)
app.jwt.secret=404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970
app.jwt.expiration-ms=3600000
```

## Common Mistakes
1. **Storing JWT secret in code:** must be in environment variable, not committed to git.
2. **Short secret keys:** HS256 requires at least 256 bits (32 bytes). Weak keys are brute-forceable.
3. **No token expiration:** tokens without `exp` claim never expire — stolen tokens work forever.
4. **Storing sensitive data in JWT payload:** payload is Base64-decoded, not encrypted. Never put passwords, PII, or secrets in claims.
5. **Not validating token issuer (iss):** in multi-service setups, validate that the token was issued by your auth service.
""",
"mcqs": [
  {"id":"d56q1","prompt":"What are the three parts of a JWT token?","options":["Header, Body, Footer","Header (algorithm), Payload (claims), Signature — separated by dots, each Base64URL encoded","Token type, claims, expiry","Subject, issuer, audience"],"correctAnswer":"Header (algorithm), Payload (claims), Signature — separated by dots, each Base64URL encoded","explanation":"Header: {alg:'HS256', typ:'JWT'}. Payload: {sub:'user@example.com', exp:...}. Signature: HMAC-SHA256 of header.payload using the secret key. The server verifies by recomputing the signature — if it matches, the token is authentic and unmodified."},
  {"id":"d56q2","prompt":"Why does JWT enable stateless authentication?","options":["JWTs are stored in a database","The server verifies the JWT signature locally without querying a session store — all needed claims are in the token itself","JWTs don't expire","Stateless means no security"],"correctAnswer":"The server verifies the JWT signature locally without querying a session store — all needed claims are in the token itself","explanation":"Traditional sessions: server stores session data, looks up session ID on each request (DB/Redis hit). JWT: server recomputes signature and checks expiry — no DB lookup. Token carries userId, role, email — everything needed for the request. Scales horizontally without session sharing."},
  {"id":"d56q3","prompt":"What does `OncePerRequestFilter` guarantee for the JWT filter?","options":["The filter runs once per JVM startup","The filter executes exactly once per request, even in filter chains with forwards/includes — prevents double-authentication","The filter is cached after first execution","Ensures JWT is validated once per session"],"correctAnswer":"The filter executes exactly once per request, even in filter chains with forwards/includes — prevents double-authentication","explanation":"Spring MVC can forward requests internally (error pages, etc.) which can trigger filters multiple times. OncePerRequestFilter stores a request attribute to skip re-execution on the same request. For JWT authentication, double-execution would be harmless but wasteful."},
  {"id":"d56q4","prompt":"What happens when the JWT filter encounters an invalid/expired token?","options":["Returns 401 immediately from the filter","Catches the JwtException, leaves SecurityContext empty, and calls chain.doFilter() — the next filter (ExceptionTranslationFilter) generates the 401 response","Throws an exception to the controller","Redirects to the login page"],"correctAnswer":"Catches the JwtException, leaves SecurityContext empty, and calls chain.doFilter() — the next filter (ExceptionTranslationFilter) generates the 401 response","explanation":"The JWT filter is not responsible for sending the response. It either sets the Authentication in SecurityContext (valid token) or doesn't (invalid token). With no Authentication in context, Spring Security's ExceptionTranslationFilter generates a 401 Unauthorized when the request reaches a protected resource."},
  {"id":"d56q5","prompt":"Why is the JWT payload NOT encrypted?","options":["Encryption is optional","The payload is Base64URL encoded (not encrypted) — anyone with the token can decode and read the claims. Only the signature prevents modification. Never put passwords, PII, or secrets in claims","JWT uses AES encryption by default","Only RS256 tokens are encrypted"],"correctAnswer":"The payload is Base64URL encoded (not encrypted) — anyone with the token can decode and read the claims. Only the signature prevents modification. Never put passwords, PII, and secrets in claims","explanation":"Base64 decode the payload in any browser console. Safe to put: userId, email, role, permissions. Never put: password hash, SSN, credit card numbers. If you need encrypted payloads, use JWE (JSON Web Encryption) — separate from JWT/JWS."},
  {"id":"d56q6","prompt":"What is the refresh token pattern and why use short-lived access tokens?","options":["Refresh tokens are just another access token","Short access tokens (15-60min) limit exposure if stolen. Refresh tokens (7-30 days, stored in DB) can be revoked. Client uses refresh token to get a new access token without re-login","Refresh tokens replace passwords","Only used for OAuth2"],"correctAnswer":"Short access tokens (15-60min) limit exposure if stolen. Refresh tokens (7-30 days, stored in DB) can be revoked. Client uses refresh token to get a new access token without re-login","explanation":"Stolen access token: usable for only 15-60 minutes (limited damage window). Refresh tokens in DB can be revoked: logout invalidates the refresh token → attacker can't get new access tokens. Short-lived + revocable refresh tokens = better security than long-lived access tokens."},
  {"id":"d56q7","prompt":"What minimum key size is required for HS256 JWT signing?","options":["64 bits","256 bits (32 bytes) — the same length as the hash output. Shorter keys are brute-forceable. Use a cryptographically random 256-bit key","128 bits","512 bits"],"correctAnswer":"256 bits (32 bytes) — the same length as the hash output. Shorter keys are brute-forceable. Use a cryptographically random 256-bit key","explanation":"HMAC-SHA256 security is bounded by the key length. A 128-bit key has 2^128 brute-force space but weakens the HMAC. RFC 7518 requires the key to be at least as long as the hash output (256 bits for HS256). Generate with: `openssl rand -base64 32`."},
  {"id":"d56q8","prompt":"Why should the JWT secret be stored in an environment variable?","options":["Environment variables are faster","Committing secrets to git exposes them permanently (even after deletion, they exist in history). Environment variables are injected at runtime and not part of the codebase","Spring requires env vars for security config","Environment variables are encrypted automatically"],"correctAnswer":"Committing secrets to git exposes them permanently (even after deletion, they exist in history). Environment variables are injected at runtime and not part of the codebase","explanation":"If app.jwt.secret=... appears in application.properties committed to git: anyone with repo access has the key. Can forge any JWT. Even a private repo is a risk (supply chain attack, insider threat). Use: APP_JWT_SECRET env var → referenced as ${APP_JWT_SECRET} in properties."},
  {"id":"d56q9","prompt":"What claim in a JWT controls token expiration?","options":["expiry","exp — a Unix timestamp (seconds since epoch). Jwts.parser().verifyWith(key) automatically validates exp and throws ExpiredJwtException if the token is past expiration","ttl","expiresIn"],"correctAnswer":"exp — a Unix timestamp (seconds since epoch). Jwts.parser().verifyWith(key) automatically validates exp and throws ExpiredJwtException if the token is past expiration","explanation":"Standard JWT claims: sub (subject/username), iat (issued at), exp (expiration), nbf (not before), iss (issuer), aud (audience). JJWT's parseSignedClaims() automatically checks exp and throws ExpiredJwtException — you don't need to check manually."},
  {"id":"d56q10","prompt":"In the JWT filter, why check `SecurityContextHolder.getContext().getAuthentication() == null`?","options":["To prevent NullPointerException","To avoid re-authenticating a request that already has authentication set (e.g., by a previous filter) — only authenticate if not already authenticated","Authentication is null for all requests","Security context is always empty initially"],"correctAnswer":"To avoid re-authenticating a request that already has authentication set (e.g., by a previous filter) — only authenticate if not already authenticated","explanation":"If another filter (e.g., OAuth2) already set the authentication, the JWT filter should not overwrite it. Checking for null ensures JWT authentication only runs when no authentication exists. This also prevents processing the JWT twice."}
],
"writtenConceptQuestions": [
  "Show a complete JwtService: generateToken() with sub, role, userId claims and expiry; extractEmail(); isTokenValid(); using JJWT library.",
  "Write a JwtAuthFilter extending OncePerRequestFilter: extract Bearer token, validate, set SecurityContext authentication.",
  "Show the complete auth flow: POST /api/auth/login → validate credentials → generate JWT → return AuthResponse.",
  "Explain the refresh token pattern. Show the RefreshToken entity and the refreshToken() service method.",
  "What claims are safe to put in a JWT payload? What should never be there? Show a payload with appropriate claims.",
  "How do you revoke a JWT? (JWTs are stateless — explain the limitations and the refresh token database approach.)",
  "What is the difference between HS256 (symmetric) and RS256 (asymmetric) JWT signing? When do you use each?"
],
"businessScenarios": [
  "Users are forced to re-login every 15 minutes, causing complaints. Implement the refresh token pattern: 15-minute access tokens + 7-day refresh tokens stored in DB with revocation on logout.",
  "A JWT secret 'mysecret' is hardcoded in application.properties and committed to GitHub. Immediate actions: rotate the secret (all existing tokens invalid), move to environment variable, scan git history.",
  "An admin revokes a user's access but the user's JWT still works for 1 hour (token expiration). Design a token blacklist (Redis set of revoked JTI claims) that enables immediate revocation."
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
