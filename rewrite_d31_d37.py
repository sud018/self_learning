"""Rewrite days 31-37: Advanced Java (Exceptions → Optional)."""
import json, os
DATA_DIR = "backend/data/curriculum"

CURRICULUM = {

"day-031": {
"notes": """# Exception Handling: Advanced Patterns, Hierarchy Design, and Spring Boot Integration

## Exception Hierarchy Design
Well-designed exception hierarchies communicate domain meaning and allow callers to choose the specificity they need:
```java
// Base domain exception — all business errors extend this
public class DomainException extends RuntimeException {
    private final String errorCode;
    public DomainException(String errorCode, String message) {
        super(message); this.errorCode = errorCode;
    }
    public DomainException(String errorCode, String message, Throwable cause) {
        super(message, cause); this.errorCode = errorCode;
    }
    public String getErrorCode() { return errorCode; }
}

public class NotFoundException extends DomainException {
    public NotFoundException(String entity, Object id) {
        super("NOT_FOUND", entity + " not found: " + id);
    }
}
public class ConflictException extends DomainException {
    public ConflictException(String message) { super("CONFLICT", message); }
}
public class ValidationException extends DomainException {
    private final Map<String, String> fieldErrors;
    public ValidationException(Map<String, String> errors) {
        super("VALIDATION_ERROR", "Validation failed");
        this.fieldErrors = errors;
    }
    public Map<String, String> getFieldErrors() { return fieldErrors; }
}
```

## Re-Throwing vs Wrapping vs Swallowing
```java
// SWALLOWING — almost always wrong
try { risky(); } catch (IOException e) {} // bug hidden forever

// RE-THROWING — when you can't handle, let it propagate
try { risky(); } catch (IOException e) { throw e; }

// WRAPPING — translate to domain exception (preferred for service layers)
try {
    jdbcTemplate.update(sql, params);
} catch (DataAccessException e) {
    throw new RepositoryException("Failed to save order", e); // e = cause preserved
}

// TRANSLATING with context — best
try {
    return userRepo.findById(id).orElseThrow();
} catch (EmptyResultDataAccessException e) {
    throw new NotFoundException("User", id); // wrap with semantic context
}
```

## try-with-resources Internals
`AutoCloseable.close()` is called in reverse order of opening, even if body throws. If both body AND close throw, the close exception is suppressed (accessible via `getSuppressed()`):
```java
try (
    Connection conn = dataSource.getConnection();    // opened first, closed last
    PreparedStatement ps = conn.prepareStatement(sql) // closed first
) {
    // use ps
} // ps.close() then conn.close() — both called even if exception thrown
// If ps.close() throws and body already threw, body exception is primary;
// ps.close() exception is added as suppressed
```

## @RestControllerAdvice — Centralised HTTP Error Mapping
```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(NotFoundException e) {
        return new ErrorResponse(e.getErrorCode(), e.getMessage());
    }

    @ExceptionHandler(ValidationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidation(ValidationException e) {
        return new ErrorResponse(e.getErrorCode(), e.getMessage(), e.getFieldErrors());
    }

    @ExceptionHandler(ConflictException.class)
    @ResponseStatus(HttpStatus.CONFLICT)
    public ErrorResponse handleConflict(ConflictException e) {
        return new ErrorResponse(e.getErrorCode(), e.getMessage());
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleUnexpected(Exception e, HttpServletRequest req) {
        log.error("Unexpected error at {}", req.getRequestURI(), e);
        return new ErrorResponse("INTERNAL_ERROR", "An unexpected error occurred");
    }
}

public record ErrorResponse(String code, String message, Map<String, String> fieldErrors) {
    public ErrorResponse(String code, String message) { this(code, message, null); }
}
```

## Exception Handling in Async and Streams
```java
// Streams can't throw checked exceptions — wrap them
orders.stream()
    .map(o -> {
        try { return processOrder(o); }
        catch (IOException e) { throw new UncheckedIOException(e); } // wrap checked as unchecked
    })
    .collect(toList());

// CompletableFuture — handle() processes both result and exception
CompletableFuture.supplyAsync(() -> paymentService.charge(order))
    .handle((result, ex) -> {
        if (ex != null) return PaymentResult.failed(ex.getMessage());
        return result;
    });
```

## Common Mistakes
1. **Catching `Throwable` or `Error`:** catches OOM and SOE — prevents JVM from shutting down cleanly.
2. **Exception message with null:** `throw new NotFoundException("Order", null)` → message contains "null". Validate before constructing.
3. **Logging AND re-throwing:** double-logs the same error. Log only at the top-level handler.
4. **Empty catch in tests:** `@Test void test() { try { ... } catch (Exception e) {} }` — test always passes even when exception thrown.
""",
"mcqs": [
  {"id":"d31q1","prompt":"What is the difference between exception wrapping and re-throwing?","options":["Identical","Wrapping creates a new exception with the original as cause (translates to domain exception); re-throwing propagates the same exception unchanged","Re-throwing loses the stack trace","Wrapping requires checked exceptions"],"correctAnswer":"Wrapping creates a new exception with the original as cause (translates to domain exception); re-throwing propagates the same exception unchanged","explanation":"Wrapping: throw new DomainException('msg', originalException). The original is preserved as cause() for logging. Re-throwing: throw e or throw (catches and rethrows same instance). Wrapping translates between abstraction layers."},
  {"id":"d31q2","prompt":"In try-with-resources with multiple resources, what is the closing order?","options":["Opening order","Reverse opening order — last opened is closed first","Random","All closed simultaneously"],"correctAnswer":"Reverse opening order — last opened is closed first","explanation":"Resources are closed in reverse declaration order. If Connection is first and PreparedStatement is second, PS closes first then Connection. This mirrors stack-based cleanup and ensures statements are closed before their connection."},
  {"id":"d31q3","prompt":"What happens to close() exceptions when the try block also throws?","options":["close() exception replaces the try block exception","close() exception is suppressed — attached to the primary exception via addSuppressed()","Both exceptions are thrown simultaneously","close() exception is lost entirely"],"correctAnswer":"close() exception is suppressed — attached to the primary exception via addSuppressed()","explanation":"try-with-resources: if body throws AND close() throws, the body exception is primary. The close exception is added as suppressed (retrievable via getSuppressed()). This preserves both exceptions without losing either."},
  {"id":"d31q4","prompt":"Why should you NOT log AND re-throw the same exception?","options":["Logging is slow","It creates duplicate log entries for the same error — once at the catch site and again at the top-level handler","Re-throwing requires checked exceptions","Only one log level can be used per exception"],"correctAnswer":"It creates duplicate log entries for the same error — once at the catch site and again at the top-level handler","explanation":"Log once at the place where you handle it, or re-throw and let the top-level handler log it. Both logging and re-throwing creates 2+ log entries for one error, confusing support staff and filling logs with duplicates."},
  {"id":"d31q5","prompt":"Which HTTP status code should `NotFoundException extends DomainException` map to in @ExceptionHandler?","options":["400 Bad Request","401 Unauthorized","404 Not Found","500 Internal Server Error"],"correctAnswer":"404 Not Found","explanation":"HTTP 404 means the requested resource does not exist on the server. NotFoundException maps to 404. ValidationException → 400, ConflictException → 409, AuthenticationException → 401, AuthorizationException → 403."},
  {"id":"d31q6","prompt":"How do you throw a checked exception inside a Stream.map() operation?","options":["Declare throws in the lambda","Wrap the checked exception in an unchecked one (UncheckedIOException for IOException)","Use parallel streams","Checked exceptions cannot occur inside streams"],"correctAnswer":"Wrap the checked exception in an unchecked one (UncheckedIOException for IOException)","explanation":"Lambda functional interfaces (Function, Predicate) don't declare checked exceptions. Wrapping in RuntimeException or UncheckedIOException lets it propagate. Alternatively, wrap the lambda in a helper method that handles the checked exception."},
  {"id":"d31q7","prompt":"What does `CompletableFuture.handle((result, ex) -> ...)` do differently from `.thenApply()`?","options":["handle() runs on a different thread","handle() receives both the result (if success) and the exception (if failed) — processes both cases; thenApply() only runs on success","thenApply() is faster","They are identical"],"correctAnswer":"handle() receives both the result (if success) and the exception (if failed) — processes both cases; thenApply() only runs on success","explanation":"handle() is the recovery mechanism for CompletableFuture. Both result and ex are provided (one will be null). It can convert a failure into a default result, translate the exception, or log it. thenApply() skips execution if the future completed exceptionally."},
  {"id":"d31q8","prompt":"A service layer catches a DataAccessException and creates `throw new DomainException('msg')` without passing the original. What is lost?","options":["Nothing important","The original stack trace and root cause — support cannot diagnose the actual database error","The HTTP status code","The error code"],"correctAnswer":"The original stack trace and root cause — support cannot diagnose the actual database error","explanation":"Always pass the original exception as cause: throw new DomainException('msg', e). Without it, the full stack trace of the original DataAccessException is lost. Support sees 'Failed to save order' but not which SQL failed or why."},
  {"id":"d31q9","prompt":"What is the purpose of a base DomainException class in an application?","options":["Required by Spring Boot","Allows @ExceptionHandler to catch all domain errors with one handler, provides a common errorCode field, and organises the hierarchy","Makes exceptions serializable","Provides automatic HTTP mapping"],"correctAnswer":"Allows @ExceptionHandler to catch all domain errors with one handler, provides a common errorCode field, and organises the hierarchy","explanation":"With a base DomainException, you can have one @ExceptionHandler(DomainException.class) that handles all domain errors, using the errorCode field to determine the response. More specific handlers for NotFoundException, ValidationException override this for custom behaviour."},
  {"id":"d31q10","prompt":"An @ExceptionHandler(Exception.class) in @RestControllerAdvice catches all unhandled exceptions. What should it always do?","options":["Return 404","Return a stack trace in the response","Log the exception with ERROR level and return a generic 500 response without internal details","Throw a new exception"],"correctAnswer":"Log the exception with ERROR level and return a generic 500 response without internal details","explanation":"The catch-all handler: 1) logs the full exception for debugging (log.error('Unexpected', e)), 2) returns a generic 500 response that doesn't expose stack traces or internal details to clients (security risk). Internal error details should never appear in API responses."}
],
"writtenConceptQuestions": [
  "Design a complete exception hierarchy for an order management system with a base DomainException, NotFoundException, ValidationException (with field errors map), and ConflictException.",
  "Explain try-with-resources: what AutoCloseable is, the closing order for multiple resources, and how suppressed exceptions work.",
  "What is the difference between swallowing, re-throwing, and wrapping exceptions? When is each appropriate in a Spring Boot service layer?",
  "Show a complete @RestControllerAdvice that maps NotFoundException→404, ValidationException→400, ConflictException→409, and all other exceptions→500.",
  "How do you handle checked exceptions inside Stream.map()? Show UncheckedIOException wrapping and a helper method approach.",
  "Why is logging AND re-throwing the same exception wrong? Show the duplicate log problem and the correct pattern.",
  "Explain CompletableFuture.handle() vs thenApply() for exception recovery. Show a payment service that returns a PaymentResult.failed() on exception."
],
"businessScenarios": [
  "A production service shows duplicate error logs: the same exception appears 3 times in logs — once from the repository, once from the service, once from the controller. Fix the logging to appear exactly once.",
  "An API returns full Java stack traces in its JSON error responses. Security team flags this as a vulnerability (exposes internal class names and library versions). Fix the @RestControllerAdvice to return only errorCode and message.",
  "A bulk import service processes 10,000 records. Any IOException causes the stream to fail. Redesign so each record's errors are collected individually and the successful records are saved, returning a report of successes and failures."
]
},

"day-032": {
"notes": """# Generics: Advanced Wildcards, Generic Methods, and Type Inference

## Generic Methods — Type Parameters on Methods
```java
// Generic method: type parameter before return type
public static <T> Optional<T> firstMatch(List<T> list, Predicate<T> predicate) {
    return list.stream().filter(predicate).findFirst();
}

// Type inference — compiler deduces T from arguments
Optional<Order> found = firstMatch(orders, o -> o.getTotal().compareTo(limit) > 0);
// T inferred as Order

// Multiple type parameters
public static <K, V> Map<V, K> invertMap(Map<K, V> original) {
    Map<V, K> result = new HashMap<>();
    original.forEach((k, v) -> result.put(v, k));
    return result;
}
Map<String, Integer> original = Map.of("a", 1, "b", 2);
Map<Integer, String> inverted = invertMap(original); // inferred K=String, V=Integer
```

## PECS Deep Dive — Producer Extends, Consumer Super
The rule for when to use upper vs lower bounded wildcards:
```java
// PRODUCER (reads FROM the collection) → ? extends T
public static double sumPrices(List<? extends Number> prices) {
    return prices.stream().mapToDouble(Number::doubleValue).sum();
}
sumPrices(new ArrayList<Integer>());  // OK
sumPrices(new ArrayList<Double>());   // OK
// prices.add(1.0); // COMPILE ERROR — can't add to producer (unknown exact type)

// CONSUMER (writes INTO the collection) → ? super T
public static void fillWithZeros(List<? super Integer> list, int count) {
    for (int i = 0; i < count; i++) list.add(0); // OK — can add Integer
}
fillWithZeros(new ArrayList<Integer>());  // OK
fillWithZeros(new ArrayList<Number>());   // OK
fillWithZeros(new ArrayList<Object>());   // OK
// Integer x = list.get(0); // COMPILE ERROR — can only read as Object from consumer
```

## Bounded Type Parameters vs Wildcards
```java
// Bounded type parameter — use when T needs to be referenced elsewhere in the signature
public static <T extends Comparable<T>> T max(List<T> list) {
    return list.stream().max(Comparator.naturalOrder()).orElseThrow();
}

// Wildcard — use when the type doesn't need to be named
public static double sum(List<? extends Number> numbers) { ... }
// vs
public static <T extends Number> double sum(List<T> numbers) { ... } // same effect, more verbose
```
Rule: if you need to use T in multiple places in the signature, use a bounded parameter. If you just need to say "some subtype of X", use a wildcard.

## Generic Classes with Multiple Bounds
```java
// T must implement both Comparable<T> and Serializable
public class SortableCache<T extends Comparable<T> & Serializable> {
    private final TreeMap<T, T> store = new TreeMap<>();
    public void put(T item) { store.put(item, item); }
    public T getFloor(T key) { return store.floorKey(key); }
}
```

## Type Tokens — Working Around Erasure
Type erasure prevents `new T()` and `instanceof List<String>`. Type tokens pass the Class object explicitly:
```java
public class TypeSafeContainer {
    private final Map<Class<?>, Object> container = new HashMap<>();

    public <T> void put(Class<T> type, T value) {
        container.put(type, value);
    }

    public <T> T get(Class<T> type) {
        return type.cast(container.get(type)); // safe cast using type token
    }
}

TypeSafeContainer c = new TypeSafeContainer();
c.put(String.class, "hello");
c.put(Integer.class, 42);
String s = c.get(String.class); // no cast, type-safe
```
Spring's `ParameterizedTypeReference<T>` is a type token for working with generic types in RestTemplate/WebClient.

## Generic Variance — Invariance of Java Generics
```java
// Arrays are COVARIANT (unsafe):
String[] strings = new String[3];
Object[] objects = strings; // compiles
objects[0] = 42; // compiles! but throws ArrayStoreException at runtime

// Generics are INVARIANT (safe):
List<String> stringList = new ArrayList<>();
List<Object> objectList = stringList; // COMPILE ERROR — invariant prevents this bug
// If allowed: objectList.add(42) would corrupt stringList at runtime
```

## Generics in Spring Boot
```java
// Generic response wrapper
public record ApiResponse<T>(T data, String message, boolean success) {
    public static <T> ApiResponse<T> ok(T data) {
        return new ApiResponse<>(data, "Success", true);
    }
    public static <T> ApiResponse<T> error(String message) {
        return new ApiResponse<>(null, message, false);
    }
}

// Controller using generic response
@GetMapping("/{id}")
public ResponseEntity<ApiResponse<OrderDto>> getOrder(@PathVariable String id) {
    return ResponseEntity.ok(ApiResponse.ok(orderService.findById(id)));
}

// Spring's ParameterizedTypeReference for RestTemplate
ResponseEntity<List<OrderDto>> response = restTemplate.exchange(
    url, HttpMethod.GET, null,
    new ParameterizedTypeReference<List<OrderDto>>() {} // preserves List<OrderDto> type at runtime
);
```
""",
"mcqs": [
  {"id":"d32q1","prompt":"What does the PECS rule stand for?","options":["Parameters Extend Constraints Successfully","Producer Extends, Consumer Super — use ? extends T when reading, ? super T when writing","Polymorphic Erasure Causes Subtypes","Private Encapsulated Classes Simplify"],"correctAnswer":"Producer Extends, Consumer Super — use ? extends T when reading, ? super T when writing","explanation":"PECS guides wildcard choice: if the collection produces (you read from it), use ? extends T. If it consumes (you write to it), use ? super T. If both, use T directly."},
  {"id":"d32q2","prompt":"Why can't you call `list.add(element)` on a `List<? extends Number>`?","options":["add() doesn't work with wildcards","The compiler doesn't know the exact type — if it's List<Integer>, adding a Double would corrupt it","Number is abstract","add() requires a cast"],"correctAnswer":"The compiler doesn't know the exact type — if it's List<Integer>, adding a Double would corrupt it","explanation":"List<? extends Number> could be a List<Integer>, List<Double>, or any Number subtype. Adding is unsafe because you'd be putting the wrong type in. The compiler blocks all adds (except null) to prevent type corruption."},
  {"id":"d32q3","prompt":"What is a type token and why is it needed?","options":["A UUID for tracking types","A Class<T> object passed explicitly to work around type erasure — allows type-safe cast and instanceof at runtime","A string representation of a type","A token for Spring Security type checking"],"correctAnswer":"A Class<T> object passed explicitly to work around type erasure — allows type-safe cast and instanceof at runtime","explanation":"Type erasure removes generic type info at runtime. Class<T> is a reifiable type — it survives. Passing Class<T> explicitly enables type.cast(), type.isInstance(), and reflection-based operations that generics alone cannot provide."},
  {"id":"d32q4","prompt":"Why are Java generics invariant while arrays are covariant?","options":["Historical accident","Generics are invariant by design to prevent type corruption at compile time; array covariance is a Java 1.0 mistake that causes ArrayStoreException at runtime","Generics can't be covariant due to erasure","Arrays use covariance for performance"],"correctAnswer":"Generics are invariant by design to prevent type corruption at compile time; array covariance is a Java 1.0 mistake that causes ArrayStoreException at runtime","explanation":"Array covariance (String[] is-a Object[]) allows `Object[] arr = new String[]; arr[0] = 42;` which compiles but throws ArrayStoreException at runtime. Generics fixed this: List<String> is NOT a List<Object>, preventing the compile-time escape and eliminating the runtime check."},
  {"id":"d32q5","prompt":"When should you use a bounded type parameter `<T extends Number>` vs a wildcard `<? extends Number>`?","options":["They are identical","Use bounded parameter when T is referenced multiple times in the signature (return type, multiple parameters); use wildcard when the type only appears once and doesn't need naming","Wildcards are deprecated","Bounded parameters only work on classes"],"correctAnswer":"Use bounded parameter when T is referenced multiple times in the signature (return type, multiple parameters); use wildcard when the type only appears once and doesn't need naming","explanation":"public <T extends Comparable<T>> T max(List<T> list) — T is needed as both parameter and return type. public void process(List<? extends Number> list) — the type is only used once and doesn't need a name. Named type parameters are more powerful; wildcards are more concise."},
  {"id":"d32q6","prompt":"What does `<T extends Comparable<T> & Serializable>` mean?","options":["T must extend Comparable or implement Serializable","T must implement both Comparable<T> AND Serializable — multiple bounds with & operator","T can be compared to Serializable objects","Syntax error"],"correctAnswer":"T must implement both Comparable<T> AND Serializable — multiple bounds with & operator","explanation":"Multiple bounds: T extends A & B means T must satisfy all bounds. The class bound (if any) must come first; interfaces follow with &. This lets you call both compareTo() and serialization methods on T."},
  {"id":"d32q7","prompt":"What is Spring's ParameterizedTypeReference<List<OrderDto>> used for?","options":["Serializing lists to JSON","Preserving the generic type information at runtime when making HTTP calls with RestTemplate/WebClient — working around type erasure","Creating parameterized beans","Validating generic types"],"correctAnswer":"Preserving the generic type information at runtime when making HTTP calls with RestTemplate/WebClient — working around type erasure","explanation":"new ParameterizedTypeReference<List<OrderDto>>() {} creates an anonymous subclass, which captures the generic type parameter in its class metadata. Spring reads this via reflection to know that the response should be deserialized as List<OrderDto>, not just List."},
  {"id":"d32q8","prompt":"Type inference for a generic method `<T> List<T> repeat(T item, int n)` — what is T when calling `repeat(\"hello\", 3)`?","options":["Object","String — compiler infers T from the argument type","Needs explicit: repeat.(String)(\"hello\",3)","Cannot infer — must specify"],"correctAnswer":"String — compiler infers T from the argument type","explanation":"Java's type inference since Java 7 (diamond operator) and improved in Java 8/10 deduces T from method arguments. Since item is 'hello' (String), T is inferred as String. The return type List<String> is also inferred."},
  {"id":"d32q9","prompt":"A generic `ApiResponse<T>` record has `static <T> ApiResponse<T> ok(T data)`. What does the diamond `<>` on `new ApiResponse<>(data, ...)` represent?","options":["An empty generic type","Diamond operator — compiler infers T from the constructor argument type","A wildcard","Required syntax with no type inference"],"correctAnswer":"Diamond operator — compiler infers T from the constructor argument type","explanation":"The diamond operator <> was added in Java 7 for type inference on constructor calls. new ApiResponse<>(data, 'Success', true) infers T from data's type. Without diamond, you'd write new ApiResponse<T>(data, ...) with explicit type."},
  {"id":"d32q10","prompt":"Why is `List<Object>` NOT a supertype of `List<String>` even though `Object` is a supertype of `String`?","options":["A bug in the Java compiler","Allowing this would break type safety: you could add Integer to the List<Object> reference, corrupting the List<String>","Lists don't support subtyping","Generics only work with interfaces"],"correctAnswer":"Allowing this would break type safety: you could add Integer to the List<Object> reference, corrupting the List<String>","explanation":"If List<String> extends List<Object>, then: List<Object> ref = new ArrayList<String>(); ref.add(42); String s = ref.get(0) → ClassCastException. Generics are invariant to prevent this. Use List<? extends Object> (= List<?>) if you need a read-only supertype."}
],
"writtenConceptQuestions": [
  "Explain PECS (Producer Extends, Consumer Super) with two concrete method examples — one reading from a collection and one writing to it. Show what breaks if the wrong wildcard is used.",
  "Write a generic method `<T extends Comparable<T>> T clamp(T value, T min, T max)` that returns value constrained to [min,max]. Show type inference in action.",
  "What is a type token? Show a type-safe heterogeneous container using Class<T> as key.",
  "Explain why Java generics are invariant while arrays are covariant. Show the ArrayStoreException bug that invariant generics prevent.",
  "Describe the difference between bounded type parameters and wildcards. Show a case where you must use a bounded parameter (T appears in return type).",
  "How does Spring's ParameterizedTypeReference work around type erasure for HTTP response deserialization?",
  "Write a generic `Result<T>` class with success/failure states, a value field, an error message field, and static factory methods ok(T) and error(String)."
],
"businessScenarios": [
  "A utility method `copyList(List source, List destination)` uses raw types. It compiles but causes ClassCastException at runtime when a List<String> is copied to a List<Integer>. Rewrite using proper generics with wildcards.",
  "A Spring Boot service needs to deserialize different JSON response types from an external API. `restTemplate.getForObject(url, List.class)` returns `List<LinkedHashMap>` instead of `List<OrderDto>`. Fix using ParameterizedTypeReference.",
  "A reporting service has 5 overloaded methods summing prices from List<Integer>, List<Long>, List<Double>, List<BigDecimal>, List<Float>. Collapse to one generic method using PECS."
]
},

"day-033": {
"notes": """# Java 8 Comprehensive Overview: All Features Working Together

## What Java 8 Changed
Java 8 (March 2014) was the most significant Java release since Java 5. It introduced: lambda expressions, functional interfaces, Stream API, Optional, default/static interface methods, new Date/Time API, CompletableFuture improvements, and Nashorn JS engine.

## Feature Integration — How They Work Together
Lambda → Functional Interface → Stream → Collector forms a complete data-processing pipeline:
```java
// These four Java 8 features combine into one readable pipeline:
Map<String, DoubleSummaryStatistics> salesByRegion = orders.stream()  // Stream API
    .filter(o -> o.getStatus() == Status.COMPLETED)                    // Lambda
    .collect(Collectors.groupingBy(                                    // Collector
        Order::getRegion,                                              // Method reference
        Collectors.summarizingDouble(o -> o.getTotal().doubleValue())  // Downstream collector
    ));
// Result: {NORTH→{count=150,sum=45000.00,avg=300.00,...}, SOUTH→{...}}
```

## Default Methods — Backward-Compatible API Evolution
```java
// Java 8 added 75+ default methods to existing interfaces without breaking implementations
List<String> list = new ArrayList<>(Arrays.asList("c","a","b"));
list.sort(Comparator.naturalOrder());          // NEW: List.sort() default method
list.forEach(System.out::println);             // NEW: Iterable.forEach() default method
list.removeIf(s -> s.equals("a"));            // NEW: Collection.removeIf() default method
list.replaceAll(String::toUpperCase);          // NEW: List.replaceAll() default method

Map<String, Integer> map = new HashMap<>();
map.computeIfAbsent("key", k -> 0);           // NEW: Map compute methods
map.merge("key", 1, Integer::sum);             // NEW: Map.merge()
map.getOrDefault("missing", -1);               // NEW: Map.getOrDefault()
```

## Method References — Four Forms
```java
// 1. Static method reference
Function<String, Integer> parseInt = Integer::parseInt;
// equivalent to: s -> Integer.parseInt(s)

// 2. Instance method on parameter
Function<String, String> upper = String::toUpperCase;
// equivalent to: s -> s.toUpperCase()

// 3. Instance method on specific object
List<String> log = new ArrayList<>();
Consumer<String> addToLog = log::add;
// equivalent to: s -> log.add(s)

// 4. Constructor reference
Supplier<ArrayList<String>> listFactory = ArrayList::new;
// equivalent to: () -> new ArrayList<>()
Function<Integer, int[]> arrayMaker = int[]::new;
// equivalent to: n -> new int[n]
```

## Collectors — Full Toolkit
```java
List<Order> orders = ...;

// Basic collectors
Collectors.toList()         // mutable list
Collectors.toSet()          // HashSet (deduplication)
Collectors.toUnmodifiableList() // immutable list (Java 10)
Collectors.joining(", ", "[", "]") // string concatenation: "[a, b, c]"
Collectors.counting()       // Long count

// Grouping
Collectors.groupingBy(Order::getStatus)               // Map<Status, List<Order>>
Collectors.groupingBy(Order::getStatus, counting())   // Map<Status, Long>
Collectors.partitioningBy(o -> o.getTotal() > 100)    // Map<Boolean, List<Order>>

// Aggregating
Collectors.summingDouble(o -> o.getTotal().doubleValue())
Collectors.averagingDouble(o -> o.getTotal().doubleValue())
Collectors.summarizingDouble(...)  // count+sum+min+max+avg in one pass

// Transforming
Collectors.toMap(Order::getId, Order::getStatus)       // Map<String, Status>
Collectors.toMap(Order::getId, o -> o,
    (existing, replacement) -> existing)               // merge function for duplicate keys

// Collecting to a specific type
Collectors.toCollection(TreeSet::new)  // TreeSet
```

## CompletableFuture — Asynchronous Composition
```java
CompletableFuture<User> userFuture =
    CompletableFuture.supplyAsync(() -> userService.findById(userId));

CompletableFuture<List<Order>> ordersFuture =
    CompletableFuture.supplyAsync(() -> orderService.findByUser(userId));

// Combine two futures when both complete
CompletableFuture<UserDashboard> dashboard =
    userFuture.thenCombine(ordersFuture, (user, orders) ->
        new UserDashboard(user, orders));

// Run in sequence
CompletableFuture<PaymentResult> result =
    CompletableFuture.supplyAsync(() -> orderService.create(cart))
        .thenApply(order -> paymentService.charge(order))
        .thenApply(payment -> notificationService.confirm(payment))
        .exceptionally(ex -> PaymentResult.failed(ex.getMessage()));
```

## Common Mistakes
1. **Stream terminal operation forgotten:** `orders.stream().filter(o -> true)` — no terminal operation, nothing executes.
2. **null in Collectors.toMap():** `toMap(Order::getId, Order::getNullableField)` — throws NPE if any value is null. Use toMap with a merge function or filter nulls first.
3. **Using forEach for transformation:** `forEach` is for side effects. Use `map` + `collect` to build new collections.
4. **Parallel stream without thread safety:** `parallelStream()` shares work across ForkJoinPool threads — any state mutation in lambdas must be thread-safe.
""",
"mcqs": [
  {"id":"d33q1","prompt":"What are the four types of method references in Java 8?","options":["static, instance, lambda, abstract","Static method, instance method on parameter, instance method on specific object, constructor reference","Public, private, protected, default","Bound, unbound, static, generic"],"correctAnswer":"Static method, instance method on parameter, instance method on specific object, constructor reference","explanation":"Four forms: 1) ClassName::staticMethod (Integer::parseInt), 2) ClassName::instanceMethod (String::toUpperCase — called on stream element), 3) object::instanceMethod (list::add — called on captured object), 4) ClassName::new (ArrayList::new)."},
  {"id":"d33q2","prompt":"What does `Collectors.toMap(Order::getId, o -> o, (e, r) -> e)` do?","options":["Creates a map of id→order, throwing on duplicate keys","Creates a map of id→order; if duplicate keys exist, keeps the existing entry","Creates a map of order→id","Filters duplicate orders"],"correctAnswer":"Creates a map of id→order; if duplicate keys exist, keeps the existing entry","explanation":"The third argument to toMap() is a merge function called when duplicate keys exist. (e, r) -> e means 'keep existing, discard replacement'. Without it, toMap throws IllegalStateException for duplicate keys."},
  {"id":"d33q3","prompt":"What does `Collectors.partitioningBy(o -> o.getTotal() > 100)` produce?","options":["List<Order> where total > 100","Map<Boolean, List<Order>> with two groups: true (total>100) and false (total<=100)","Set<Boolean>","Sorted list partitioned at 100"],"correctAnswer":"Map<Boolean, List<Order>> with two groups: true (total>100) and false (total<=100)","explanation":"partitioningBy is a specialised groupingBy that always produces a Map<Boolean, List<T>> with two keys: true and false. More efficient than groupingBy when you need exactly two groups based on a predicate."},
  {"id":"d33q4","prompt":"A stream pipeline has `filter()`, `map()`, `sorted()` but no terminal operation. What executes?","options":["filter() runs, then map(), then sorted() waits","Nothing — stream operations are lazy and only execute when a terminal operation (collect, count, forEach) is called","sorted() triggers execution because it needs to see all elements","map() always executes immediately"],"correctAnswer":"Nothing — stream operations are lazy and only execute when a terminal operation (collect, count, forEach) is called","explanation":"Intermediate operations (filter, map, sorted, distinct) are lazy — they build a pipeline description. Execution only begins when a terminal operation is called. This enables short-circuiting: if findFirst() is the terminal, processing stops after the first match."},
  {"id":"d33q5","prompt":"What does `CompletableFuture.thenCombine(otherFuture, biFunction)` do?","options":["Runs after either future completes","Waits for BOTH futures to complete then applies biFunction to both results","Runs the two futures sequentially","Cancels one future if the other completes first"],"correctAnswer":"Waits for BOTH futures to complete then applies biFunction to both results","explanation":"thenCombine runs both futures concurrently (if submitted to a thread pool) and when BOTH complete, applies the combining function. Perfect for aggregating results from two independent async calls (user + orders fetch in parallel)."},
  {"id":"d33q6","prompt":"Which Java 8 addition let you add `stream()`, `forEach()`, `removeIf()` to Collection without breaking existing implementations?","options":["Generics","Default methods in interfaces","Sealed interfaces","New abstract Collection class"],"correctAnswer":"Default methods in interfaces","explanation":"Default methods provide implementations in interfaces that implementing classes inherit. Java 8 added 75+ default methods to Collection, List, Map, Iterable, etc. All existing custom implementations inherited these methods without any code change."},
  {"id":"d33q7","prompt":"What is `Collectors.summarizingDouble()` and when is it useful?","options":["Rounds doubles to 2 decimal places","Computes count, sum, min, max, and average in a single stream pass","Converts doubles to summaries","Groups by double value"],"correctAnswer":"Computes count, sum, min, max, and average in a single stream pass","explanation":"summarizingDouble returns a DoubleSummaryStatistics containing all five aggregates. More efficient than running 5 separate stream pipelines. Used with groupingBy to get statistics per group: Map<String, DoubleSummaryStatistics> statsByRegion."},
  {"id":"d33q8","prompt":"What is wrong with `orders.parallelStream().forEach(o -> globalList.add(o))`?","options":["parallelStream() doesn't support forEach","ArrayList is not thread-safe — concurrent adds from multiple threads corrupt the list","parallelStream always runs on the main thread","forEach is not a terminal operation"],"correctAnswer":"ArrayList is not thread-safe — concurrent adds from multiple threads corrupt the list","explanation":"parallelStream() processes elements on multiple ForkJoinPool threads concurrently. ArrayList.add() is not synchronized — concurrent structural modifications cause data loss or ConcurrentModificationException. Fix: use collect(toList()) which thread-safely accumulates results."},
  {"id":"d33q9","prompt":"What does `int[]::new` as a method reference mean?","options":["An array of method references","A constructor reference for int[] — equivalent to n -> new int[n]","A static method called 'new' on int[]","Syntax error"],"correctAnswer":"A constructor reference for int[] — equivalent to n -> new int[n]","explanation":"Array constructor references take the array length as argument: int[]::new is IntFunction<int[]>: n -> new int[n]. Used in Stream.toArray(int[]::new) to create a typed array from a stream."},
  {"id":"d33q10","prompt":"Which Collector produces a String 'a, b, c' from a stream of [a, b, c]?","options":["Collectors.toString()","Collectors.joining(', ')","Collectors.toList().toString()","Collectors.concat()"],"correctAnswer":"Collectors.joining(', ')","explanation":"Collectors.joining(delimiter) concatenates stream elements (must be String or CharSequence) with the delimiter. joining(', ', '[', ']') produces '[a, b, c]' with prefix and suffix. The stream must be of String type."}
],
"writtenConceptQuestions": [
  "Show all four method reference forms with a real example of each, and the equivalent lambda expression.",
  "Explain lazy evaluation in streams. Show a pipeline where short-circuiting with findFirst() means not all elements are processed.",
  "Describe Collectors.groupingBy() with a downstream collector. Show a query that produces Map<String, DoubleSummaryStatistics> (sales stats by region).",
  "What is CompletableFuture.thenCombine()? Show fetching user + orders in parallel and combining into a dashboard object.",
  "Explain why parallelStream() with mutable shared state is dangerous. Show the thread-safety bug and the correct collect() approach.",
  "What Java 8 default methods were added to Map? Show practical examples of getOrDefault, merge, computeIfAbsent, and replaceAll.",
  "Show Collectors.toMap() with a merge function. What exception does it throw without one and when does that exception occur?"
],
"businessScenarios": [
  "A reporting endpoint generates 5 separate DB queries to get: total orders, total revenue, average order value, max order, min order. Rewrite as one stream pipeline using summarizingDouble() to get all five in one pass over the already-loaded orders list.",
  "A Spring Boot service fetches user profile and order history from two separate microservices. Currently sequential (600ms total). Redesign using CompletableFuture to fetch both in parallel (300ms target).",
  "A migration script reads 500,000 records and builds a Map<String, Product> using toMap(). After 100,000 records it throws IllegalStateException: Duplicate key 'P-001'. Fix using merge function and explain why duplicates exist."
]
},

"day-034": {
"notes": """# Lambda Expressions: Closures, Effectively Final, Performance, and Advanced Patterns

## Closures — Capturing Variables
A lambda can capture variables from its enclosing scope. Captured variables must be **effectively final** (never reassigned after the lambda captures them):
```java
String prefix = "Order-"; // effectively final — never reassigned
List<String> ids = orders.stream()
    .map(o -> prefix + o.getId()) // captures prefix — OK
    .collect(toList());

// COMPILE ERROR: prefix must be effectively final
String prefix = "Order-";
prefix = "Shipment-"; // reassignment makes it NOT effectively final
orders.stream().map(o -> prefix + o.getId()); // error

// WORKAROUND for mutable capture: use an array or AtomicReference
int[] counter = {0}; // array itself is effectively final; elements are mutable
orders.forEach(o -> counter[0]++); // mutates element, not the variable
```

## Why Effectively Final? Thread Safety and Correctness
Lambdas may execute on different threads (parallel streams, CompletableFuture). If captured variables were mutable, different threads could see different values — a data race. Effectively final guarantees the captured value is stable.

## Lambda Internals — How the JVM Executes Lambdas
Lambdas are NOT anonymous inner classes. They use `invokedynamic` bytecode instruction:
1. First call: `LambdaMetafactory` creates a class implementing the functional interface.
2. Subsequent calls: the generated class is reused (no new object created for non-capturing lambdas).
Non-capturing lambda (no closure): same lambda object reused across calls — zero allocation.
Capturing lambda: new instance per call to hold captured state.

## Lambda Composition
```java
Function<String, String> trim = String::trim;
Function<String, String> upper = String::toUpperCase;
Function<String, String> trimThenUpper = trim.andThen(upper);
// trimThenUpper.apply("  hello  ") → "HELLO"

Function<String, String> upperThenTrim = trim.compose(upper);
// compose: f.compose(g) means g first then f
// upperThenTrim.apply("  hello  ") → "  HELLO  ".trim() → "  HELLO  "
// (trim after upper: trim("  hello  ".toUpperCase()))

Predicate<String> notEmpty = s -> !s.isEmpty();
Predicate<String> notBlank = s -> !s.isBlank();
Predicate<String> valid = notEmpty.and(notBlank);  // both must be true
Predicate<String> either = notEmpty.or(notBlank);  // either must be true
Predicate<String> empty  = notEmpty.negate();       // inverts
```

## Currying and Partial Application
```java
// Currying: transform a two-argument function into a chain of one-argument functions
Function<Integer, Function<Integer, Integer>> add = a -> b -> a + b;
Function<Integer, Integer> add5 = add.apply(5); // partial application
add5.apply(3);  // 8
add5.apply(10); // 15

// Useful in Spring Boot for building validators or mappers with context:
Function<String, Function<Order, OrderDto>> toDtoWithBase =
    baseUrl -> order -> new OrderDto(order.getId(), baseUrl + "/" + order.getId());
Function<Order, OrderDto> toDto = toDtoWithBase.apply("https://api.example.com/orders");
```

## Lambdas vs Anonymous Inner Classes
```java
// Anonymous inner class — separate class file generated, creates a new object each time
Runnable r1 = new Runnable() {
    @Override public void run() { System.out.println("hello"); }
};

// Lambda — invokedynamic, non-capturing → same object reused
Runnable r2 = () -> System.out.println("hello");
```
Key difference: `this` in an anonymous inner class refers to the anonymous class instance. `this` in a lambda refers to the **enclosing class** instance. No separate class file for lambdas.

## Advanced Lambda Patterns in Spring Boot
```java
// Strategy injection via lambda
@Service
public class PricingService {
    public BigDecimal calculatePrice(Product product,
                                     Function<Product, BigDecimal> pricingStrategy) {
        return pricingStrategy.apply(product);
    }
}
// At call site:
pricingService.calculatePrice(product, p -> p.getBasePrice().multiply(new BigDecimal("1.2")));

// Decorator via lambda
public <T> T withTransaction(Supplier<T> operation) {
    txManager.begin();
    try { T result = operation.get(); txManager.commit(); return result; }
    catch (Exception e) { txManager.rollback(); throw e; }
}
Order saved = withTransaction(() -> orderRepo.save(order));
```
""",
"mcqs": [
  {"id":"d34q1","prompt":"What does 'effectively final' mean for a variable captured by a lambda?","options":["Declared with the final keyword","Never assigned after its initial declaration (compiler verifies this, even without explicit final)","Thread-safe by default","Stored in the String pool"],"correctAnswer":"Never assigned after its initial declaration (compiler verifies this, even without explicit final)","explanation":"Effectively final: a variable that is never reassigned after initialisation. The compiler checks this and allows capture without explicit final. If you reassign the variable anywhere, it loses effectively-final status and cannot be captured."},
  {"id":"d34q2","prompt":"What does `this` refer to inside a lambda expression?","options":["The lambda object itself","The enclosing class instance (same as outside the lambda)","null","A new anonymous class instance"],"correctAnswer":"The enclosing class instance (same as outside the lambda)","explanation":"Unlike anonymous inner classes where `this` refers to the anonymous instance, a lambda's `this` refers to the enclosing class. This is why lambdas are said to be 'transparent' — they don't create a new `this` scope."},
  {"id":"d34q3","prompt":"What bytecode instruction do lambdas use that makes them more efficient than anonymous inner classes?","options":["invokevirtual","invokedynamic — generates the implementation class lazily on first call and reuses it","invokestatic","invokeinterface"],"correctAnswer":"invokedynamic — generates the implementation class lazily on first call and reuses it","explanation":"invokedynamic delegates lambda creation to LambdaMetafactory at the first call. Non-capturing lambdas return the same singleton instance on every call — zero allocation. Anonymous inner classes always generate a .class file and create a new object."},
  {"id":"d34q4","prompt":"What does `Function<String, String> pipeline = trim.andThen(upper)` do?","options":["Applies upper first, then trim","Applies trim first, then passes the result to upper","Applies both in parallel","Returns a Predicate that tests both conditions"],"correctAnswer":"Applies trim first, then passes the result to upper","explanation":"andThen composes left-to-right: f.andThen(g) means apply f first, then g. Opposite of compose: f.compose(g) means g first, then f. Think of andThen as a pipeline: step 1 (f) then step 2 (g)."},
  {"id":"d34q5","prompt":"Why is capturing a mutable counter in a lambda dangerous in a parallel stream?","options":["Lambdas can't capture integers","Multiple threads increment the same variable concurrently — result is unpredictable due to data races","Parallel streams don't support lambdas","Counter values are boxed, causing NPE"],"correctAnswer":"Multiple threads increment the same variable concurrently — result is unpredictable due to data races","explanation":"Even with the int[] counter workaround, parallelStream tasks on multiple threads increment counter[0] concurrently — a data race. Use AtomicInteger or collect().size() for thread-safe counting in parallel streams."},
  {"id":"d34q6","prompt":"What is partial application (currying) in the context of Java lambdas?","options":["Applying a function to part of a list","Fixing some arguments of a multi-argument function to create a new function with fewer arguments","Partial compilation of lambdas","Using only some methods of a functional interface"],"correctAnswer":"Fixing some arguments of a multi-argument function to create a new function with fewer arguments","explanation":"Currying transforms f(a,b) into a -> b -> result. Partial application fixes one argument: add5 = add.apply(5) creates a function that always adds 5. Useful for creating specialised functions from general ones, e.g., a locale-specific formatter."},
  {"id":"d34q7","prompt":"What does `Predicate<String> valid = notEmpty.and(notBlank)` produce?","options":["A Predicate that tests only notBlank","A Predicate that returns true only if both notEmpty AND notBlank return true","A Predicate that returns true if either returns true","A compiled Predicate chain"],"correctAnswer":"A Predicate that returns true only if both notEmpty AND notBlank return true","explanation":"Predicate.and() creates a short-circuit conjunction: returns true only if both predicates return true. If the first returns false, the second is not evaluated. Predicate.or() is a disjunction; negate() inverts."},
  {"id":"d34q8","prompt":"You write `orders.stream().map(o -> heavyComputation(o))`. The lambda captures no variables. How many lambda objects are allocated across 1000 stream operations?","options":["1000 — one per map call","1 — the lambda singleton is reused (invokedynamic optimization for non-capturing lambdas)","0 — lambdas have no heap allocation","Depends on the JVM"],"correctAnswer":"1 — the lambda singleton is reused (invokedynamic optimization for non-capturing lambdas)","explanation":"Non-capturing lambdas don't hold any state. The JVM (via LambdaMetafactory) can return the same instance every time since all calls produce identical behaviour. This is one of the key performance advantages of lambdas over anonymous inner classes."},
  {"id":"d34q9","prompt":"A lambda `Function<Order, String>` needs access to a `baseUrl` String that changes between requests. Can it capture `baseUrl`?","options":["Yes, if baseUrl is a field (not a local variable)","Yes if baseUrl is effectively final at the point of lambda creation","No — lambdas cannot capture Strings","Only if baseUrl is static"],"correctAnswer":"Yes if baseUrl is effectively final at the point of lambda creation","explanation":"If baseUrl is a field (instance or static), the lambda captures `this` and accesses baseUrl through the reference. If baseUrl is a local variable, it must be effectively final at the point the lambda is created. Fields can change after capture — only local variable capture requires effectively-final."},
  {"id":"d34q10","prompt":"What is the decorator-via-lambda pattern in Spring Boot?","options":["Replacing @Decorator annotation","Wrapping an operation Supplier<T> in cross-cutting logic (transaction, timing, retry) without modifying the operation itself","Generating decorators at compile time","Using @Around in AOP"],"correctAnswer":"Wrapping an operation Supplier<T> in cross-cutting logic (transaction, timing, retry) without modifying the operation itself","explanation":"withTransaction(() -> repo.save(order)) takes the operation as a lambda and wraps it in transaction management. The operation doesn't know about transactions. This is a lighter alternative to AOP @Transactional when you need runtime flexibility."}
],
"writtenConceptQuestions": [
  "Explain 'effectively final' with three examples: one that is effectively final, one that is not (reassigned), and one using the int[] workaround.",
  "What is the difference between `this` in an anonymous inner class vs in a lambda? Show a case where this difference matters.",
  "Describe Function.andThen() vs Function.compose(). Show a pipeline: trim → toUpperCase → substring(0,10), and show what each approach produces.",
  "Explain lambda performance: non-capturing vs capturing lambda object allocation. When are lambdas more efficient than anonymous inner classes?",
  "Show currying in Java 8: a Function<String, Function<Order, OrderDto>> that partially applies a base URL to create a DTO mapper.",
  "Describe the decorator-via-lambda pattern: show a withRetry(Supplier<T>) wrapper that retries on exception up to 3 times.",
  "What is Predicate composition? Show a validation chain that validates a string is not blank, has length < 100, and matches a regex."
],
"businessScenarios": [
  "A Spring Boot filter needs to apply different pricing strategies at runtime based on customer type. Implement using Function<Product, BigDecimal> strategies injected via a Map<CustomerType, Function<Product, BigDecimal>>.",
  "A service method executes a database operation with retry logic. Currently a 80-line method with try-catch and loops. Refactor using a generic `withRetry(Supplier<T>, int maxAttempts)` lambda decorator.",
  "A reporting pipeline builds a Function<Order, ReportRow> mapper, but the mapper needs access to currency exchange rates that change daily. Show how to curry the exchange rate into the mapper function so the rate is fixed for each report run."
]
},

"day-035": {
"notes": """# Functional Interfaces: Built-in Types, Specialised Variants, and Composition

## The Four Core Functional Interfaces
```java
// Predicate<T> — T → boolean (filtering, testing)
Predicate<String> isValidEmail = s -> s != null && s.contains("@") && s.contains(".");
Predicate<Order> isLarge = o -> o.getTotal().compareTo(new BigDecimal("1000")) > 0;

// Function<T, R> — T → R (transformation/mapping)
Function<Order, OrderDto> toDto = order -> new OrderDto(order.getId(), order.getTotal());
Function<String, Integer> strLen = String::length;

// Consumer<T> — T → void (side effects)
Consumer<Order> saveToDb = orderRepo::save;
Consumer<String> logInfo = message -> log.info("Processing: {}", message);

// Supplier<T> — () → T (lazy computation, factory)
Supplier<List<Order>> emptyList = ArrayList::new;
Supplier<LocalDateTime> now = LocalDateTime::now;
```

## Specialised Primitive Functional Interfaces
Avoid boxing overhead for primitives with specialised interfaces:
```java
// Without specialisation (boxes int to Integer):
Function<Integer, Integer> doubleIt = n -> n * 2; // Integer boxing every call

// Specialised (no boxing):
IntUnaryOperator doubleIt = n -> n * 2;  // int → int, zero boxing
IntFunction<String> intToStr = n -> "Value: " + n; // int → String
ToIntFunction<String> strToLen = String::length;    // String → int
IntPredicate isEven = n -> n % 2 == 0;             // int → boolean
IntConsumer printInt = System.out::println;         // int → void
IntSupplier random = () -> ThreadLocalRandom.current().nextInt(100);

// Available for int, long, double:
LongUnaryOperator, LongBinaryOperator, DoublePredicate, etc.
```

## BiFunction, BiPredicate, BiConsumer
For functions taking two arguments:
```java
BiFunction<String, Integer, String> repeat = (s, n) -> s.repeat(n);
repeat.apply("ab", 3); // "ababab"

BiPredicate<String, Integer> longerThan = (s, n) -> s.length() > n;
longerThan.test("hello", 3); // true

BiConsumer<String, Integer> printNTimes = (s, n) -> {
    for (int i = 0; i < n; i++) System.out.println(s);
};

// BinaryOperator<T> = BiFunction<T,T,T>
BinaryOperator<Integer> add = Integer::sum;
BinaryOperator<String> concat = String::concat;

// UnaryOperator<T> = Function<T,T>
UnaryOperator<String> trim = String::trim;
```

## Custom Functional Interfaces
```java
@FunctionalInterface
public interface Transformer<I, O, C> {
    O transform(I input, C context) throws TransformationException;
    // Can have default and static methods
    static <I, O, C> Transformer<I, O, C> noOp() {
        return (input, ctx) -> (O) input;
    }
}

// Usage with checked exception
Transformer<Order, OrderDto, String> mapper = (order, locale) -> {
    try { return buildDto(order, locale); }
    catch (ParseException e) { throw new TransformationException(e); }
};
```

## Functional Interface in Spring Events and Validation
```java
// Spring @EventListener as functional interface
@EventListener
public Consumer<OrderCreatedEvent> onOrderCreated() {
    return event -> notificationService.notify(event.getOrder());
}

// Bean Validation custom constraint using functional interface
@FunctionalInterface
public interface Validator<T> {
    ValidationResult validate(T value);

    default Validator<T> and(Validator<T> other) {
        return value -> {
            ValidationResult r = this.validate(value);
            return r.isValid() ? other.validate(value) : r;
        };
    }
}

// Usage
Validator<Order> notEmpty = o -> o.getItems().isEmpty()
    ? ValidationResult.error("Items required") : ValidationResult.ok();
Validator<Order> validTotal = o -> o.getTotal().signum() > 0
    ? ValidationResult.ok() : ValidationResult.error("Total must be positive");
Validator<Order> fullValidation = notEmpty.and(validTotal);
```

## Common Mistakes
1. **Choosing Function over Predicate for boolean tests:** use `Predicate<T>` for `T → boolean`, not `Function<T, Boolean>`. Predicate supports and/or/negate composition.
2. **Ignoring primitive specialisations in tight loops:** boxing 10 million ints in `Function<Integer, Integer>` creates 10 million heap allocations. Use `IntUnaryOperator`.
3. **Checked exceptions in functional interfaces:** standard functional interfaces don't declare checked exceptions. Wrap them or create a custom interface.
4. **Stateful lambdas in parallel streams:** lambdas passed to stream operations should be stateless. `n -> list.add(n)` mutates shared state and is thread-unsafe in parallel.
""",
"mcqs": [
  {"id":"d35q1","prompt":"What is the signature of `BiFunction<String, Integer, String>`?","options":["(String) → Integer → String","(String, Integer) → String","(String, Integer) → void","(Integer, String) → String"],"correctAnswer":"(String, Integer) → String","explanation":"BiFunction<T, U, R> has apply(T t, U u) returning R. BiFunction<String, Integer, String> takes a String and Integer and returns a String. Example: (s, n) -> s.repeat(n)."},
  {"id":"d35q2","prompt":"Why use `IntUnaryOperator` instead of `Function<Integer, Integer>`?","options":["IntUnaryOperator has more methods","IntUnaryOperator avoids autoboxing/unboxing of int — no heap allocation for each operation","Function<Integer, Integer> doesn't work with streams","IntUnaryOperator is faster due to JIT optimization only"],"correctAnswer":"IntUnaryOperator avoids autoboxing/unboxing of int — no heap allocation for each operation","explanation":"Function<Integer, Integer> boxes every int to Integer (heap object) and unboxes the result. IntUnaryOperator int → int operates on primitives directly. For 10 million calls in a tight loop, this saves 20 million allocations."},
  {"id":"d35q3","prompt":"What does `@FunctionalInterface` annotation do?","options":["Makes all methods default","Generates the implementation at compile time","Instructs the compiler to verify the interface has exactly one abstract method — compile error if not","Marks the interface as thread-safe"],"correctAnswer":"Instructs the compiler to verify the interface has exactly one abstract method — compile error if not","explanation":"@FunctionalInterface is a verification annotation. It fails to compile if the interface has 0 or 2+ abstract methods. It doesn't change runtime behaviour — an interface with one abstract method IS functional regardless of the annotation."},
  {"id":"d35q4","prompt":"What is the difference between `Consumer<T>` and `Function<T, Void>`?","options":["Identical","Consumer.accept() returns void; Function<T,Void>.apply() must return null (Void) — Consumer is preferred for side effects because you can't accidentally return a value","Consumer is slower","Function<T,Void> doesn't compile"],"correctAnswer":"Consumer.accept() returns void; Function<T,Void>.apply() must return null (Void) — Consumer is preferred for side effects because you can't accidentally return a value","explanation":"Consumer<T> has void accept(T t). Using Function<T,Void> is legal but awkward — you must explicitly return null. Consumer composes with andThen(); it's the correct abstraction for side-effectful operations."},
  {"id":"d35q5","prompt":"What does `Predicate<T>.negate()` return?","options":["null for all inputs","A new Predicate that returns !original.test(t) for every input","Removes the predicate from a chain","A Predicate that always returns false"],"correctAnswer":"A new Predicate that returns !original.test(t) for every input","explanation":"negate() returns a new Predicate that inverts the result. isActive.negate() is equivalent to t -> !isActive.test(t). Combined with and/or for readable Boolean logic: isValid.and(isActive.negate()) = 'valid but not active'."},
  {"id":"d35q6","prompt":"Why should lambdas passed to `parallelStream()` be stateless?","options":["parallelStream() doesn't support stateful lambdas","Stateful lambdas accessing shared mutable state from multiple threads create data races — results are unpredictable","Stateful lambdas are slower","parallelStream() copies lambda state per thread"],"correctAnswer":"Stateful lambdas accessing shared mutable state from multiple threads create data races — results are unpredictable","explanation":"parallelStream distributes elements across ForkJoinPool threads. If a lambda mutates shared state (e.g., a counter, a list), multiple threads modify it concurrently without synchronisation. Use collect() for accumulation, which handles thread safety via Collector's combiner."},
  {"id":"d35q7","prompt":"What is `BinaryOperator<T>` equivalent to?","options":["BiFunction<T, T, Boolean>","BiFunction<T, T, T> — both inputs and the output are the same type","UnaryOperator<T> applied twice","Predicate<T> for two inputs"],"correctAnswer":"BiFunction<T, T, T> — both inputs and the output are the same type","explanation":"BinaryOperator<T> extends BiFunction<T,T,T>: T apply(T t1, T t2). Examples: Integer::sum (BinaryOperator<Integer>), String::concat (BinaryOperator<String>). Used in Stream.reduce() as the accumulator."},
  {"id":"d35q8","prompt":"A Transformer functional interface declares `O transform(I input) throws ParseException`. Can it be used as a lambda target?","options":["Yes — any functional interface works","No — only @FunctionalInterface interfaces work with lambdas","Yes, but the lambda must catch or declare ParseException","Checked exceptions prevent lambda usage entirely"],"correctAnswer":"Yes, but the lambda must catch or declare ParseException","explanation":"A custom functional interface CAN declare checked exceptions. Lambdas implementing it must handle those exceptions (catch or the lambda's functional method must declare throws — not possible in lambda syntax, so catch inside the lambda). Standard Java FI (Function, Consumer) don't declare checked exceptions."},
  {"id":"d35q9","prompt":"What is the composable Validator pattern (Validator.and() default method)?","options":["A Spring annotation","A custom functional interface with a default and() method that chains validators left-to-right, short-circuiting on first failure","A JPA validation mechanism","Hibernate Validator extension"],"correctAnswer":"A custom functional interface with a default and() method that chains validators left-to-right, short-circuiting on first failure","explanation":"Defining a default and() on a Validator interface: notEmpty.and(validTotal).and(inStock) creates a chain where each validator runs only if previous passed. This gives composable business rules without inheritance or complex frameworks."},
  {"id":"d35q10","prompt":"What is `Supplier<T>` used for in lazy evaluation?","options":["Supplying database connections","Deferring expensive computation until the result is actually needed — the computation is wrapped in a Supplier and called only when .get() is invoked","Providing default values for null fields","Creating singletons"],"correctAnswer":"Deferring expensive computation until the result is actually needed — the computation is wrapped in a Supplier and called only when .get() is invoked","explanation":"Optional.orElseGet(Supplier<T>) vs orElse(T): orElse always evaluates the default value even if the Optional is present. orElseGet(supplier) calls supplier.get() only if the Optional is empty. This matters when the default is expensive to compute."}
],
"writtenConceptQuestions": [
  "Explain all four core functional interfaces (Predicate, Function, Consumer, Supplier) with their signatures, use cases, and composition methods.",
  "When should you use primitive specialised functional interfaces (IntPredicate, LongFunction, etc.)? Show a benchmark scenario explaining the boxing overhead.",
  "Write a custom @FunctionalInterface Transformer<I, O> that declares a checked TransformationException. Show how to use it as a lambda.",
  "Explain Predicate composition: and(), or(), negate(). Show building a complex product filter: in stock AND price < 100 AND NOT discontinued.",
  "Compare Consumer.andThen() with Function.andThen(). What is the difference and when do you use each?",
  "What is BinaryOperator<T>? Show its use in Stream.reduce() to sum a list of BigDecimal values.",
  "Explain the difference between orElse(defaultValue) and orElseGet(supplier) in Optional. When does the performance difference matter?"
],
"businessScenarios": [
  "A validation service has 12 separate if-statement validators for Order objects, all returning boolean. Refactor using Predicate composition where each validator is a Predicate<Order> and the full validation is a composed AND chain.",
  "A data pipeline processes 50 million integers, applying Function<Integer, Integer> transformations. Profiling shows 40% of time is spent in GC from Integer boxing. Migrate to IntUnaryOperator and show the before/after.",
  "A pricing engine needs to apply different combinations of discount rules (bulk discount AND holiday AND loyalty) that vary per customer segment. Design using composable Predicate<Order> and Function<Order, BigDecimal> that can be assembled at runtime."
]
},

"day-036": {
"notes": """# Streams: Advanced Operations, Parallel Streams, and Custom Collectors

## flatMap — Flattening Nested Structures
```java
// flatMap(f) applies f to each element where f returns a Stream, then flattens
List<Order> orders = ...;
List<OrderItem> allItems = orders.stream()
    .flatMap(o -> o.getItems().stream())  // each Order produces a Stream<OrderItem>
    .collect(toList());                    // flattened into one List<OrderItem>

// Optional.flatMap — prevents Optional<Optional<T>>
Optional<String> email = userRepo.findById(id)    // Optional<User>
    .flatMap(User::getOptionalEmail)               // flatMap prevents Optional<Optional<String>>
    .map(String::toLowerCase);
```

## reduce() — Custom Aggregation
```java
// reduce(identity, accumulator)
BigDecimal total = orders.stream()
    .map(Order::getTotal)
    .reduce(BigDecimal.ZERO, BigDecimal::add); // identity=ZERO, accumulator=add

// reduce(accumulator) — returns Optional (stream may be empty)
Optional<Order> largestOrder = orders.stream()
    .reduce((a, b) -> a.getTotal().compareTo(b.getTotal()) >= 0 ? a : b);

// Three-argument reduce for parallel: reduce(identity, accumulator, combiner)
// combiner merges partial results from parallel sub-streams
int sum = IntStream.rangeClosed(1, 100)
    .parallel()
    .reduce(0, Integer::sum); // 0 is identity, Integer::sum accumulates and combines
```

## collect() with Custom Collector
```java
// Collector.of(supplier, accumulator, combiner, finisher)
Collector<Order, BigDecimal[], BigDecimal> avgTotalCollector = Collector.of(
    () -> new BigDecimal[]{BigDecimal.ZERO, BigDecimal.ZERO}, // [sum, count]
    (acc, o) -> { acc[0] = acc[0].add(o.getTotal()); acc[1] = acc[1].add(BigDecimal.ONE); },
    (a, b) -> new BigDecimal[]{a[0].add(b[0]), a[1].add(b[1])}, // combiner for parallel
    acc -> acc[1].compareTo(BigDecimal.ZERO) == 0 ? BigDecimal.ZERO : acc[0].divide(acc[1], 2, HALF_UP)
);
BigDecimal avgTotal = orders.stream().collect(avgTotalCollector);
```

## Parallel Streams — When and How
```java
// When to use parallel:
// 1. Large data (>10,000 elements) where processing is CPU-bound
// 2. Operations are stateless and independent
// 3. No shared mutable state
List<String> processed = largeList.parallelStream()
    .filter(s -> s.length() > 5)        // stateless — safe
    .map(String::toUpperCase)            // stateless — safe
    .collect(toList());                  // thread-safe reduction

// When NOT to use parallel:
// 1. Small datasets (overhead > gain)
// 2. Ordered output required from ordered operations (use forEachOrdered)
// 3. I/O-bound operations (parallel shares ForkJoinPool — I/O blocks threads)
// 4. Synchronized operations

// The ForkJoinPool: parallelStream() uses ForkJoinPool.commonPool() (default size = CPU cores - 1)
// Custom pool for isolation:
ForkJoinPool pool = new ForkJoinPool(4);
pool.submit(() -> orders.parallelStream().map(this::processOrder).collect(toList())).get();
```

## Numeric Streams — IntStream, LongStream, DoubleStream
```java
// IntStream.range and rangeClosed
IntStream.range(1, 5)          // 1,2,3,4 (exclusive end)
IntStream.rangeClosed(1, 5)    // 1,2,3,4,5 (inclusive end)

// Statistics
IntStream.of(1,2,3,4,5).average();   // OptionalDouble(3.0)
IntStream.of(1,2,3,4,5).sum();       // 15
IntStream.of(1,2,3,4,5).summaryStatistics(); // count=5, sum=15, min=1, max=5, average=3.0

// Boxing/unboxing
IntStream.rangeClosed(1, 100)
    .boxed()                           // IntStream → Stream<Integer>
    .collect(toList());

Stream<Integer> ints = Stream.of(1, 2, 3);
IntStream intStream = ints.mapToInt(Integer::intValue); // Stream<Integer> → IntStream
```

## Stream Short-Circuit Operations
```java
// anyMatch, allMatch, noneMatch — stop as soon as result is determined
boolean hasLargeOrder = orders.stream()
    .anyMatch(o -> o.getTotal().compareTo(limit) > 0); // stops at first match

boolean allPaid = orders.stream()
    .allMatch(o -> o.getStatus() != Status.PENDING); // stops at first non-match

// findFirst vs findAny
Optional<Order> first = orders.stream()
    .filter(o -> o.getStatus() == Status.PENDING)
    .findFirst();  // first in encounter order — deterministic

Optional<Order> any = orders.parallelStream()
    .filter(o -> o.getStatus() == Status.PENDING)
    .findAny();    // first found by any thread — non-deterministic, faster in parallel
```

## Streams in Spring Boot — Service Layer Patterns
```java
@Service
public class OrderService {
    // Entity → DTO transformation
    public List<OrderDto> findAll() {
        return orderRepo.findAll().stream()
            .map(mapper::toDto)
            .collect(toUnmodifiableList());
    }

    // Aggregation
    public Map<String, BigDecimal> revenueByRegion() {
        return orderRepo.findAll().stream()
            .collect(groupingBy(Order::getRegion,
                mapping(Order::getTotal,
                    reducing(BigDecimal.ZERO, BigDecimal::add))));
    }
}
```
""",
"mcqs": [
  {"id":"d36q1","prompt":"What is the difference between `map()` and `flatMap()` in streams?","options":["Identical","map() applies a function returning T; flatMap() applies a function returning Stream<T> and flattens all returned streams into one","flatMap() works on nested lists; map() works on flat lists","map() is for transformations; flatMap() is for filtering"],"correctAnswer":"map() applies a function returning T; flatMap() applies a function returning Stream<T> and flattens all returned streams into one","explanation":"map(f) transforms each element with f. If f returns a Stream, you get Stream<Stream<T>>. flatMap(f) maps then flattens: Stream<Stream<T>> → Stream<T>. Essential for working with nested collections (orders → items, users → emails)."},
  {"id":"d36q2","prompt":"What does `reduce(BigDecimal.ZERO, BigDecimal::add)` do on a stream of BigDecimals?","options":["Returns the first element","Sums all elements starting from ZERO as the identity","Finds the maximum BigDecimal","Subtracts all elements from ZERO"],"correctAnswer":"Sums all elements starting from ZERO as the identity","explanation":"reduce(identity, accumulator): starts with identity (ZERO), applies accumulator(running, next) = ZERO.add(first).add(second)... Building the sum element by element. identity must satisfy accumulator(identity, x) == x."},
  {"id":"d36q3","prompt":"When is parallel stream actually faster than sequential?","options":["Always — more threads means more speed","For large datasets (>10,000 elements) with CPU-bound, stateless, independent operations where the work per element outweighs thread coordination overhead","For any stream with more than 100 elements","When the JVM has multiple CPUs available"],"correctAnswer":"For large datasets (>10,000 elements) with CPU-bound, stateless, independent operations where the work per element outweighs thread coordination overhead","explanation":"Parallel stream splits data, submits to ForkJoinPool, and merges results. For small datasets or cheap operations, coordination overhead exceeds gains. For I/O-bound work, threads block and don't improve throughput. Profile before adding parallelism."},
  {"id":"d36q4","prompt":"What does `IntStream.rangeClosed(1, 100).sum()` compute?","options":["Average of 1 to 100","Sum of integers 1 through 100 inclusive = 5050","Count of integers from 1 to 100","Maximum value"],"correctAnswer":"Sum of integers 1 through 100 inclusive = 5050","explanation":"rangeClosed(1, 100) creates an IntStream of 1,2,...,100. sum() is a terminal operation returning the total. No boxing — works on primitives directly. result = 1+2+...+100 = 5050 (Gauss formula: n*(n+1)/2 = 100*101/2 = 5050)."},
  {"id":"d36q5","prompt":"What is the combiner argument in `Stream.reduce(identity, accumulator, combiner)` used for?","options":["Nothing — only needed in sequential streams","Merging partial results from parallel sub-streams — required for parallel reduce when the accumulator type differs from the stream element type","Providing a default value","Sorting the results"],"correctAnswer":"Merging partial results from parallel sub-streams — required for parallel reduce when the accumulator type differs from the stream element type","explanation":"In parallel, the stream is split into sub-streams. Each sub-stream accumulates independently. The combiner merges sub-stream results into the final result. For sequential streams, the combiner is never called."},
  {"id":"d36q6","prompt":"What is the difference between `findFirst()` and `findAny()` in a parallel stream?","options":["findFirst() is faster","findFirst() returns the first element in encounter order (deterministic); findAny() returns whichever thread finds a match first (non-deterministic, potentially faster)","findAny() requires sorted stream","They are identical in parallel streams"],"correctAnswer":"findFirst() returns the first element in encounter order (deterministic); findAny() returns whichever thread finds a match first (non-deterministic, potentially faster)","explanation":"In parallel, findFirst() must coordinate to ensure the 'first' in source order is returned — adds synchronisation overhead. findAny() accepts whichever thread finds a match first — cheaper. Use findAny() in parallel when you don't care which matching element is returned."},
  {"id":"d36q7","prompt":"Why is `stream.forEach(list::add)` incorrect in a parallel stream?","options":["forEach doesn't support method references","ArrayList is not thread-safe — concurrent adds from multiple threads corrupt the list. Use collect(toList()) instead","forEach is a non-terminal operation","list.add() returns boolean which forEach ignores"],"correctAnswer":"ArrayList is not thread-safe — concurrent adds from multiple threads corrupt the list. Use collect(toList()) instead","explanation":"parallelStream uses multiple threads. Calling list.add() on a shared ArrayList from multiple threads simultaneously causes ArrayIndexOutOfBoundsException or lost elements. collect(toList()) creates thread-local partial lists and merges them safely."},
  {"id":"d36q8","prompt":"What does `orders.stream().map(Order::getTotal).mapToDouble(BigDecimal::doubleValue).average()` return?","options":["A double","OptionalDouble — empty if stream is empty","DoubleSummaryStatistics","double or null"],"correctAnswer":"OptionalDouble — empty if stream is empty","explanation":"average() is a terminal operation on DoubleStream that returns OptionalDouble. It's Optional because the stream might be empty (no elements to average). Use .orElse(0.0) to get a default value."},
  {"id":"d36q9","prompt":"What is the purpose of the `Collector.of()` method?","options":["Registering a collector with the JVM","Creating a custom Collector by specifying supplier (container factory), accumulator (add element to container), combiner (merge containers), and finisher (transform final container)","Converting arrays to collectors","Parallel-safe collection only"],"correctAnswer":"Creating a custom Collector by specifying supplier (container factory), accumulator (add element to container), combiner (merge containers), and finisher (transform final container)","explanation":"Collector.of(supplier, accumulator, combiner, finisher) builds a custom terminal operation. supplier creates the mutable result container, accumulator adds elements, combiner merges for parallel, finisher transforms the container to the final result."},
  {"id":"d36q10","prompt":"In Spring Boot service layer, why use `collect(toUnmodifiableList())` instead of `collect(toList())`?","options":["toUnmodifiableList is faster","Returns an immutable list that prevents callers from accidentally modifying the service result — defensive programming","toList() doesn't work in Java 10+","No practical difference"],"correctAnswer":"Returns an immutable list that prevents callers from accidentally modifying the service result — defensive programming","explanation":"Service methods should protect their results. collect(toUnmodifiableList()) (Java 10) returns an immutable list. If a controller or test calls list.add(), it throws UnsupportedOperationException immediately rather than silently corrupting data."}
],
"writtenConceptQuestions": [
  "Explain flatMap() with two examples: flattening orders→items, and Optional.flatMap() preventing Optional<Optional<T>>.",
  "Describe reduce() with identity and accumulator. Show summing BigDecimal values. What is the three-argument form for and when is the combiner called?",
  "When should you use parallelStream()? List 4 conditions where it helps and 4 where it hurts. Show a concrete benchmark scenario.",
  "Explain IntStream, LongStream, DoubleStream. What boxing overhead do they avoid? Show converting between boxed and primitive streams.",
  "Build a custom Collector using Collector.of() that computes the weighted average of Order totals weighted by item count.",
  "What is the difference between findFirst() and findAny()? When does the distinction matter?",
  "Show a complete Spring Boot service using groupingBy + mapping + reducing to compute revenue by region from a list of orders."
],
"businessScenarios": [
  "An order analytics service runs 6 separate stream passes over a list of 200,000 orders to compute: count, sum, min, max, avg, and count by region. Consolidate into 2 passes maximum using summarizingDouble and groupingBy.",
  "A batch processing job maps 1 million records with an expensive CPU transformation using sequential stream, taking 4 minutes. Rewrite with parallelStream() correctly (stateless lambda, collect instead of forEach). Estimate expected speedup on an 8-core machine.",
  "A flattening bug: code uses `orders.stream().map(Order::getItems)` and then tries to collect to List<OrderItem> — but it collects List<List<OrderItem>> instead. Identify the issue and fix with flatMap()."
]
},

"day-037": {
"notes": """# Optional: Idiomatic Patterns, Anti-Patterns, and Design Principles

## What Optional Is and Is Not
`Optional<T>` is a container that either holds a value or is empty. It is NOT a replacement for null — it is a **return type signal** that communicates "this method may not produce a result."

**Use Optional:**
- As a method return type when absence is a legitimate outcome
- Repository findById methods: `Optional<User> findById(Long id)`
- Service lookups where not-found is expected

**Do NOT use Optional:**
- As a field type in a class
- As a method parameter: `void process(Optional<String> name)` — use overloading instead
- In collections: `List<Optional<T>>` — use filter on the stream instead
- For performance-critical code (Optional is a heap allocation)

## Idiomatic Usage Patterns
```java
Optional<User> opt = userRepo.findById(id);

// PATTERN 1: orElseThrow — required resource
User user = opt.orElseThrow(() -> new NotFoundException("User", id));

// PATTERN 2: orElse — default value (always evaluated!)
String name = opt.map(User::getName).orElse("Anonymous");

// PATTERN 3: orElseGet — lazy default (only evaluated if empty)
String expensiveDefault = opt.map(User::getName)
    .orElseGet(() -> computeExpensiveDefault()); // lambda called only if empty

// PATTERN 4: ifPresent — conditional side effect
opt.ifPresent(u -> log.info("User {} logged in", u.getName()));

// PATTERN 5: ifPresentOrElse (Java 9) — both branches
opt.ifPresentOrElse(
    u -> log.info("Found: {}", u.getName()),
    () -> log.warn("User not found: {}", id)
);

// PATTERN 6: map + filter — transform and gate
Optional<String> verifiedEmail = opt
    .map(User::getEmail)
    .filter(e -> e.endsWith("@company.com"));

// PATTERN 7: flatMap — chain Optionals
Optional<String> phone = opt
    .flatMap(User::getOptionalPhone) // User::getOptionalPhone returns Optional<String>
    .map(String::trim);
// Without flatMap: opt.map(User::getOptionalPhone) → Optional<Optional<String>>
```

## Optional Chaining — Complex Lookups
```java
// Find department head's email for a given employee ID
Optional<String> deptHeadEmail = employeeRepo.findById(empId)
    .map(Employee::getDepartment)             // Optional<Department>
    .map(Department::getHead)                 // Optional<User>
    .map(User::getEmail);                     // Optional<String>
// No NPE risk — each step handles absence

// vs. old null-check chain:
Employee emp = employeeRepo.findById(empId);
if (emp != null) {
    Department dept = emp.getDepartment();
    if (dept != null) {
        User head = dept.getHead();
        if (head != null) { email = head.getEmail(); }
    }
}
```

## Optional in Spring Boot
```java
// Spring Data JPA auto-generates Optional-returning methods
Optional<Product> product = productRepo.findById(productId);    // built-in
Optional<User> user = userRepo.findByEmail(email);              // derived query

// Service layer — translate Optional to domain exception
@Service
public class OrderService {
    public OrderDto findById(String id) {
        return orderRepo.findById(id)
            .map(orderMapper::toDto)
            .orElseThrow(() -> new NotFoundException("Order", id));
    }
}

// Controller — let @ExceptionHandler handle the NotFoundException
@GetMapping("/{id}")
public ResponseEntity<OrderDto> get(@PathVariable String id) {
    return ResponseEntity.ok(orderService.findById(id)); // NotFoundException → 404 via @ExceptionHandler
}
```

## Anti-Patterns
```java
// ANTI-PATTERN 1: isPresent() + get() — defeats the purpose
if (opt.isPresent()) { return opt.get(); }  // same as null check
// FIX: return opt.orElseThrow(() -> new NotFoundException(...));

// ANTI-PATTERN 2: Optional as parameter
public void sendEmail(Optional<String> email) { ... }
// FIX: two overloads
public void sendEmail(String email) { ... }
public void sendEmail() { /* use default */ }

// ANTI-PATTERN 3: Optional field
public class User {
    private Optional<String> middleName; // WRONG — use @Nullable String instead
}

// ANTI-PATTERN 4: orElse(new Object()) for expensive objects
Optional<Report> report = opt.map(this::generateExpensiveReport)
    .orElse(generateExpensiveReport()); // WRONG: generateExpensiveReport() called even if opt is present!
// FIX: orElseGet(() -> generateExpensiveReport())
```
""",
"mcqs": [
  {"id":"d37q1","prompt":"What is the difference between `orElse(defaultValue)` and `orElseGet(supplier)`?","options":["Identical","orElse evaluates defaultValue unconditionally; orElseGet calls supplier.get() only if the Optional is empty","orElseGet is for checked exceptions","orElse is deprecated in Java 11"],"correctAnswer":"orElse evaluates defaultValue unconditionally; orElseGet calls supplier.get() only if the Optional is empty","explanation":"orElse(T value): T is evaluated before the method call — always. orElseGet(Supplier<T>): supplier.get() is only called when the Optional is empty. For expensive defaults (DB query, file read), orElseGet avoids unnecessary work."},
  {"id":"d37q2","prompt":"Why should Optional not be used as a method parameter?","options":["Optional parameters don't compile","It forces callers to wrap every argument in Optional.of() or Optional.ofNullable(), which is more verbose than just passing null or using overloading","Optional parameters cause NPE","Spring Boot doesn't support Optional parameters"],"correctAnswer":"It forces callers to wrap every argument in Optional.of() or Optional.ofNullable(), which is more verbose than just passing null or using overloading","explanation":"Optional as parameter: caller must write method(Optional.of(value)) or method(Optional.empty()). Cleaner: overload method(T value) and method(). Or accept T and handle null internally. Optional's purpose is communicating absence in return values, not in parameters."},
  {"id":"d37q3","prompt":"What does `Optional.flatMap(User::getOptionalPhone)` do when `getOptionalPhone()` returns `Optional<String>`?","options":["Returns Optional<Optional<String>>","Flattens the nested Optional — returns Optional<String> directly","Throws NPE if getOptionalPhone returns empty","Converts Optional to Stream"],"correctAnswer":"Flattens the nested Optional — returns Optional<String> directly","explanation":"If map() is used: opt.map(User::getOptionalPhone) → Optional<Optional<String>>. flatMap() applies the function and flattens: Optional<Optional<String>> → Optional<String>. Essential when the mapping function itself returns an Optional."},
  {"id":"d37q4","prompt":"What is wrong with `Optional<String> field` in a JPA entity class?","options":["Optional doesn't implement Serializable","Optional fields break JPA/Hibernate serialization, waste memory on every entity instance, and Optional is designed as a return type signal, not a field type","JPA requires primitive fields","Optional fields don't work with @Column"],"correctAnswer":"Optional fields break JPA/Hibernate serialization, waste memory on every entity instance, and Optional is designed as a return type signal, not a field type","explanation":"Hibernate cannot map Optional fields to columns. Optional is not Serializable. It adds a heap allocation per field per entity instance. The idiomatic alternative: private String middleName; (nullable field) with getOptionalMiddleName() returning Optional.ofNullable(middleName)."},
  {"id":"d37q5","prompt":"What does the chain `opt.map(f1).filter(p).map(f2).orElseThrow()` do if `opt` is empty?","options":["Throws NullPointerException at first map()","f1, p, and f2 are skipped; orElseThrow() throws NoSuchElementException or the provided exception","Returns null from f1","orElseThrow() is not called"],"correctAnswer":"f1, p, and f2 are skipped; orElseThrow() throws NoSuchElementException or the provided exception","explanation":"All Optional pipeline operations (map, filter, flatMap) are no-ops when the Optional is empty — they return Optional.empty() immediately. The terminal orElseThrow() detects the empty Optional and throws. No NPE anywhere in the chain."},
  {"id":"d37q6","prompt":"When should you use `Optional.ofNullable(value)` vs `Optional.of(value)`?","options":["Always use ofNullable","Optional.of(value) throws NPE if value is null — use when you know value is non-null; ofNullable(value) returns empty Optional for null — use when null is a legitimate input","of() is deprecated","ofNullable is slower"],"correctAnswer":"Optional.of(value) throws NPE if value is null — use when you know value is non-null; ofNullable(value) returns empty Optional for null — use when null is a legitimate input","explanation":"Optional.of(null) throws NullPointerException immediately — use when null would be a programming error. Optional.ofNullable(value) wraps any value including null: returns empty for null. Use ofNullable when wrapping values from legacy APIs that may return null."},
  {"id":"d37q7","prompt":"What does `ifPresentOrElse(consumer, emptyAction)` do that `ifPresent()` doesn't?","options":["It is faster","Executes the consumer if present OR executes emptyAction if empty — handles both branches; ifPresent() only handles the present case","It throws if empty instead of doing nothing","Supports multiple consumers"],"correctAnswer":"Executes the consumer if present OR executes emptyAction if empty — handles both branches; ifPresent() only handles the present case","explanation":"ifPresent() ignores the empty case silently. ifPresentOrElse() (Java 9) provides an else branch: present → run consumer, empty → run emptyAction. Useful for logging/alerting when a value is missing."},
  {"id":"d37q8","prompt":"In Spring Data JPA, `findById(Long id)` returns `Optional<T>`. How should a service use this?","options":["Unwrap with .get() directly","Chain: findById(id).orElseThrow(() -> new NotFoundException(entity, id)) — throws domain exception if not found","Use isPresent() then get()","Return the Optional directly from the service"],"correctAnswer":"Chain: findById(id).orElseThrow(() -> new NotFoundException(entity, id)) — throws domain exception if not found","explanation":"Service layer translates Optional to domain exceptions. Controllers and callers don't see Optional — they get the entity directly or a domain exception is thrown and handled by @ExceptionHandler. This keeps Optional as a return-type tool, not a data transport."},
  {"id":"d37q9","prompt":"What is the output of `Optional.empty().orElse(\"default\").length()`?","options":["NullPointerException","7 — \"default\".length()","Optional[7]","0"],"correctAnswer":"7 — \"default\".length()","explanation":"Optional.empty().orElse(\"default\") returns the String \"default\". Calling .length() on it returns 7. orElse() on an empty Optional always returns the provided value. The method chain is: empty→orElse→returns String→.length()→7."},
  {"id":"d37q10","prompt":"What does `Optional.or(supplier)` (Java 9) do differently from `orElseGet()`?","options":["Identical","or(supplier) returns Optional<T> — the supplier provides another Optional (useful for fallback chain of Optionals); orElseGet returns T directly","or() is for parallel streams","orElseGet throws if supplier returns null"],"correctAnswer":"or(supplier) returns Optional<T> — the supplier provides another Optional (useful for fallback chain of Optionals); orElseGet returns T directly","explanation":"Optional.or() (Java 9) takes a Supplier<Optional<T>> and returns Optional<T>. This enables fallback chains: findInCache(id).or(() -> findInDB(id)).or(() -> findInArchive(id)).orElseThrow(). orElseGet returns the unwrapped value directly."}
],
"writtenConceptQuestions": [
  "List 4 correct uses of Optional and 4 anti-patterns with explanations. Show the fix for each anti-pattern.",
  "Explain the Optional pipeline: map, filter, flatMap, orElse, orElseGet, orElseThrow. Show a deep-chain example navigating Employee→Department→Head→Email.",
  "What is the difference between orElse() and orElseGet()? Show a case where orElse() causes an unnecessary expensive operation.",
  "Describe Optional.flatMap() and when it is needed vs map(). Show the nested Optional bug that flatMap() solves.",
  "How should Spring Data JPA Optional return values be handled in a service layer? Show the full chain from repository to controller.",
  "What is Optional.or() (Java 9)? Show a three-level fallback: check cache, then DB, then archive.",
  "Explain why Optional fields in JPA entities are wrong. Show the correct pattern: nullable field + Optional-returning getter."
],
"businessScenarios": [
  "A user service returns null when user not found. Three different callers each null-check differently — some forget and NPE. Migrate findById() to return Optional<User> and update each caller idiomatically.",
  "An order service has `Optional<Order> opt = findById(id); if (opt.isPresent()) { return process(opt.get()); } return null;`. This returns null! Rewrite using map() + orElseThrow().",
  "A configuration service looks up a value: first in request context, then in user preferences, then in system defaults, returning Optional.empty() if all are absent. Implement using Optional.or() chain without nested if-statements."
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
