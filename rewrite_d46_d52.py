"""Rewrite days 46-52: Spring Boot Core (DTOs, Validation, Exception Handling, Logging, Config, JPA, Hibernate)."""
import json, os
DATA_DIR = "backend/data/curriculum"

CURRICULUM = {

"day-046": {
"notes": """# DTOs (Data Transfer Objects): Design, Mapping, and Best Practices

## Why DTOs? The Problem with Exposing Entities
Exposing JPA entities directly in REST APIs creates multiple problems:
- **Security:** entity may have fields (password hash, internal IDs, audit fields) that should never be sent to clients
- **Coupling:** API shape is locked to DB schema — changing a column name breaks the API
- **Circular references:** bidirectional JPA relationships (Order↔OrderItems) cause infinite JSON serialization
- **Lazy loading:** serializing an entity outside a transaction triggers LazyInitializationException

```java
// WRONG — entity exposed directly (security + coupling risk)
@GetMapping("/{id}")
public User getUser(@PathVariable Long id) {
    return userRepo.findById(id).orElseThrow(); // exposes passwordHash, role, audit fields
}

// CORRECT — DTO shields the entity
@GetMapping("/{id}")
public UserDto getUser(@PathVariable Long id) {
    return userService.findById(id); // returns only what the client needs
}
```

## Defining DTOs with Records (Java 16+)
```java
// Response DTO — what the client receives
public record UserDto(
    String id,
    String firstName,
    String lastName,
    String email,
    String role,
    LocalDateTime createdAt
) {}

// Request DTO — what the client sends for creation
public record CreateUserRequest(
    @NotBlank String firstName,
    @NotBlank String lastName,
    @Email @NotBlank String email,
    @Size(min=8) String password
) {}

// Update DTO — for partial updates (fields nullable = optional)
public record UpdateUserRequest(
    String firstName,
    String lastName
) {}
```

## Manual Mapping — Simple and Transparent
```java
@Component
public class UserMapper {
    public UserDto toDto(User user) {
        return new UserDto(
            user.getId().toString(),
            user.getFirstName(),
            user.getLastName(),
            user.getEmail(),
            user.getRole().name(),
            user.getCreatedAt()
        );
    }

    public User toEntity(CreateUserRequest req, PasswordEncoder encoder) {
        User user = new User();
        user.setFirstName(req.firstName());
        user.setLastName(req.lastName());
        user.setEmail(req.email().toLowerCase());
        user.setPasswordHash(encoder.encode(req.password()));
        user.setRole(Role.USER);
        return user;
    }
}
```

## MapStruct — Compile-Time Code Generation
```java
// MapStruct generates the implementation at compile time — zero reflection, fast
@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface ProductMapper {
    // Property names match — mapped automatically
    ProductDto toDto(Product product);

    // Rename mapping
    @Mapping(source = "productCode", target = "sku")
    @Mapping(target = "price", expression = "java(product.getPrice().toString())")
    ProductSummaryDto toSummaryDto(Product product);

    // List mapping — calls toDto() for each element
    List<ProductDto> toDtoList(List<Product> products);
}

// Usage in service:
@Service
public class ProductService {
    private final ProductRepository repo;
    private final ProductMapper mapper;

    public List<ProductDto> findAll() {
        return mapper.toDtoList(repo.findAll());
    }
}
```

## DTO Projection in Spring Data JPA
Avoid loading the full entity when only a few fields are needed:
```java
// Interface projection — Spring Data generates a proxy
public interface ProductSummary {
    String getId();
    String getName();
    BigDecimal getPrice();
}

// Repository query returns projection directly — no entity loaded
public interface ProductRepository extends JpaRepository<Product, String> {
    List<ProductSummary> findAllByCategory(String category);

    // Class-based projection (record) — better for complex transformations
    @Query("SELECT new com.example.dto.ProductSummaryDto(p.id, p.name, p.price) " +
           "FROM Product p WHERE p.category = :category")
    List<ProductSummaryDto> findSummaryByCategory(@Param("category") String category);
}
```

## Request vs Response vs Command DTOs — Naming Convention
```java
// Queries (read) — *Response or *Dto suffix
record OrderResponse(String id, String status, BigDecimal total, List<OrderItemResponse> items) {}

// Commands (write) — *Request suffix
record CreateOrderRequest(String customerId, List<CreateOrderItemRequest> items) {}
record UpdateOrderStatusRequest(String status) {}

// Internal service DTOs — *Dto suffix
record OrderSummaryDto(String id, BigDecimal total, int itemCount) {}
```

## Common Mistakes
1. **Updating entities from request DTOs without validation:** always validate before mapping to entity.
2. **Returning entities from @Service methods:** services should return DTOs, not entities — entities leak outside transaction.
3. **One DTO fits all:** use separate DTOs for create/update/read — they have different field sets.
4. **Mapping in controller:** mapping should happen in the service or a dedicated mapper layer, not in controller code.
""",
"mcqs": [
  {"id":"d46q1","prompt":"Why should JPA entities NOT be returned directly from REST controllers?","options":["Entities are not serializable","Entities may expose sensitive fields, cause LazyInitializationException outside transactions, and tightly couple the API to the DB schema","Jackson cannot serialize JPA entities","Entities lack JSON annotations"],"correctAnswer":"Entities may expose sensitive fields, cause LazyInitializationException outside transactions, and tightly couple the API to the DB schema","explanation":"Returning entities: 1) passwordHash appears in JSON (security), 2) lazy-loaded collections accessed after the transaction closes throw LazyInitializationException, 3) bidirectional @OneToMany causes infinite recursion, 4) renaming a DB column breaks the API. DTOs solve all four."},
  {"id":"d46q2","prompt":"What is a DTO interface projection in Spring Data JPA?","options":["A DTO class annotated with @Projection","An interface whose getters map to entity fields — Spring Data generates a proxy and only loads the specified columns from DB","A Spring-generated entity subclass","An AOP proxy for DTO transformation"],"correctAnswer":"An interface whose getters map to entity fields — Spring Data generates a proxy and only loads the specified columns from DB","explanation":"interface ProductSummary { String getId(); String getName(); } — Spring Data creates a proxy at runtime. findAllProjectedBy() returns these proxies loading only id and name columns. More efficient than loading full entities for list views."},
  {"id":"d46q3","prompt":"What does `@Mapper(componentModel = 'spring')` in MapStruct do?","options":["Makes the mapper a REST controller","Generates the mapper implementation as a Spring @Component — injectable via @Autowired or constructor injection","Enables XML configuration","Registers the mapper in the BeanFactory as a singleton scope"],"correctAnswer":"Generates the mapper implementation as a Spring @Component — injectable via @Autowired or constructor injection","explanation":"Without componentModel='spring', MapStruct generates a plain class. With componentModel='spring', it adds @Component so Spring detects and manages it. You can then @Autowired ProductMapper mapper in services."},
  {"id":"d46q4","prompt":"What is the benefit of using Java records for DTOs vs regular classes?","options":["Records are serialized faster","Records auto-generate constructor, getters, equals, hashCode, toString — immutable by default, less boilerplate, perfect for data carriers","Records support JPA annotations","Records are required for Spring Boot 3"],"correctAnswer":"Records auto-generate constructor, getters, equals, hashCode, toString — immutable by default, less boilerplate, perfect for data carriers","explanation":"A record UserDto(String id, String name) auto-generates: all-args constructor, id()/name() accessors, equals(), hashCode(), toString(). Immutability is enforced (no setters). Perfect for DTOs which are pure data carriers with no business logic."},
  {"id":"d46q5","prompt":"What is a class-based JPQL projection (`SELECT new com.example.dto.Dto(...)`)? When is it needed?","options":["Creates a new entity from JPQL","Constructs DTO objects directly in the JPQL query using a constructor expression — needed when you need computed fields, joins, or constructor logic not possible with interface projections","Requires a no-arg constructor","Only works with native SQL"],"correctAnswer":"Constructs DTO objects directly in the JPQL query using a constructor expression — needed when you need computed fields, joins, or constructor logic not possible with interface projections","explanation":"SELECT new com.example.dto.OrderSummaryDto(o.id, o.total, SIZE(o.items)) creates DTOs directly in the DB query. Advantages: constructor can transform data, supports aggregate functions (SIZE, SUM), and is efficient (only selected columns loaded)."},
  {"id":"d46q6","prompt":"Where in a Spring Boot application should entity-to-DTO mapping happen?","options":["In the @Controller/@RestController method","In the @Service or a dedicated @Component mapper — not in the controller, not in the repository","In the JPA @Repository","In the @Configuration class"],"correctAnswer":"In the @Service or a dedicated @component mapper — not in the controller, not in the repository","explanation":"Controllers handle HTTP concerns. Repositories handle DB concerns. Mapping is a business layer concern. Centralised in a @Component mapper (or MapStruct): reusable across multiple services, easily testable, and doesn't leak entity types into the HTTP layer."},
  {"id":"d46q7","prompt":"What does `unmappedTargetPolicy = ReportingPolicy.IGNORE` in @Mapper do?","options":["Ignores null values","Suppresses compile-time warnings/errors for DTO fields that have no corresponding source field — useful when DTO has fewer fields than the entity","Makes all mappings optional","Ignores validation annotations"],"correctAnswer":"Suppresses compile-time warnings/errors for DTO fields that have no corresponding source field — useful when DTO has fewer fields than the entity","explanation":"By default, MapStruct warns (or errors) on unmapped target fields. ReportingPolicy.IGNORE silences this. Use ReportingPolicy.ERROR during development to catch accidentally missed fields."},
  {"id":"d46q8","prompt":"Why use separate request DTOs for create and update operations?","options":["Required by Spring Boot","Create may require all fields (mandatory), while update may have all fields optional (partial update semantics) — they have different validation constraints","Mapper limitation","Spring Data requires different DTOs"],"correctAnswer":"Create may require all fields (mandatory), while update may have all fields optional (partial update semantics) — they have different validation constraints","explanation":"CreateProductRequest: @NotBlank String name, @NotNull BigDecimal price — all mandatory. UpdateProductRequest: String name (nullable), BigDecimal price (nullable) — only provided fields change. Sharing one DTO forces compromise — use separate types."},
  {"id":"d46q9","prompt":"What problem does a DTO prevent when serializing a bidirectional JPA relationship?","options":["Eager loading","Infinite recursion — Order has List<OrderItem>, each OrderItem has back-reference to Order, Jackson serializes recursively until StackOverflowError","Lazy loading","Cascade operations"],"correctAnswer":"Infinite recursion — Order has List<OrderItem>, each OrderItem has back-reference to Order, Jackson serializes recursively until StackOverflowError","explanation":"@OneToMany bidirectional: Order.items → each Item.order → the same Order → its items again... Jackson follows references infinitely. DTOs break the cycle: OrderDto.items contains OrderItemDto (no back-reference). @JsonIgnore or @JsonManagedReference are workarounds but DTOs are the clean solution."},
  {"id":"d46q10","prompt":"What is the purpose of `@Mapping(source = 'productCode', target = 'sku')` in MapStruct?","options":["Creates a new field","Maps a field with a different name in source (productCode) to target (sku) — without this, MapStruct can't find the match","Ignores the field","Validates the mapping"],"correctAnswer":"Maps a field with a different name in source (productCode) to target (sku) — without this, MapStruct can't find the match","explanation":"MapStruct matches by name by default. If entity.productCode should map to dto.sku, you must specify @Mapping(source='productCode', target='sku'). Without it, sku in the DTO remains null (or is reported as unmapped)."}
],
"writtenConceptQuestions": [
  "List 4 specific problems caused by returning JPA entities from REST controllers. Show a concrete example of each problem.",
  "Design DTOs for a Product resource: CreateProductRequest (with validation), UpdateProductRequest (partial), ProductResponse (full), and ProductSummaryDto (for list views).",
  "Show a manual mapper component: entity→DTO and CreateRequest→entity. Where should mapping happen in the layered architecture?",
  "Explain MapStruct: how it works (compile-time generation), @Mapper annotation options, and @Mapping for field name differences.",
  "What are interface projections in Spring Data JPA? Show a repository method returning a projection with 3 fields from a 20-field entity.",
  "Explain class-based JPQL projections (SELECT new ...). When are they needed over interface projections?",
  "Why should create and update DTOs be separate types? Show the validation difference between CreateOrderRequest and UpdateOrderRequest."
],
"businessScenarios": [
  "An API returns full User entities including passwordHash and internalAdminNotes. Security team flags this in a pen test. Redesign with UserResponse DTO containing only safe fields.",
  "A product list endpoint loads full Product entities (30 fields each) for a list view that only shows id, name, and price. Optimize using interface projection — show the query difference.",
  "A mapper class is 200 lines of boilerplate copy-assign code. Replace with MapStruct @Mapper and show before/after code comparison."
]
},

"day-047": {
"notes": """# Bean Validation: @Valid, Constraint Annotations, Custom Validators, and Error Handling

## Jakarta Bean Validation Annotations
```java
public record CreateProductRequest(
    @NotNull(message = "Name is required")
    @NotBlank(message = "Name cannot be blank")
    @Size(min = 2, max = 100, message = "Name must be between 2 and 100 characters")
    String name,

    @NotNull
    @DecimalMin(value = "0.01", message = "Price must be greater than 0")
    @DecimalMax(value = "999999.99")
    BigDecimal price,

    @NotNull
    @Min(value = 0, message = "Stock cannot be negative")
    Integer stockCount,

    @Email(message = "Invalid email format")
    String contactEmail,

    @Pattern(regexp = "^[A-Z]{2,3}$", message = "Category code must be 2-3 uppercase letters")
    String categoryCode,

    @Future(message = "Launch date must be in the future")
    LocalDate launchDate,

    @NotEmpty(message = "At least one tag required")
    @Size(max = 10, message = "Cannot have more than 10 tags")
    List<@NotBlank @Size(max = 30) String> tags  // validates each element
) {}
```

## @Valid vs @Validated
```java
// @Valid — standard Jakarta (triggers validation on @RequestBody)
@PostMapping
public ResponseEntity<ProductDto> create(@RequestBody @Valid CreateProductRequest req) { ... }

// @Validated — Spring's annotation, enables method-level validation and group support
@Service
@Validated  // enables method parameter validation
public class ProductService {
    public ProductDto create(@Valid CreateProductRequest req) {  // validated when called
        ...
    }
    // Without @Validated on the class, @Valid on method params is ignored
}
```

## Custom Constraint — @Annotation + ConstraintValidator
```java
// 1. Define the annotation
@Documented
@Constraint(validatedBy = UniqueEmailValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
public @interface UniqueEmail {
    String message() default "Email already registered";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

// 2. Implement the validator — can inject Spring beans
@Component
public class UniqueEmailValidator implements ConstraintValidator<UniqueEmail, String> {
    private final UserRepository userRepo;

    public UniqueEmailValidator(UserRepository userRepo) {
        this.userRepo = userRepo;
    }

    @Override
    public boolean isValid(String email, ConstraintValidatorContext ctx) {
        if (email == null) return true; // let @NotBlank handle null
        return !userRepo.existsByEmail(email.toLowerCase());
    }
}

// 3. Use it
public record RegisterRequest(
    @NotBlank
    @Email
    @UniqueEmail  // DB check at validation time
    String email,
    @Size(min=8) String password
) {}
```

## Class-Level Validation — Cross-Field Constraints
```java
// Validates relationship between fields
@Documented
@Constraint(validatedBy = DateRangeValidator.class)
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface ValidDateRange {
    String message() default "End date must be after start date";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
    String startDate();
    String endDate();
}

@Component
public class DateRangeValidator implements ConstraintValidator<ValidDateRange, Object> {
    private String startField, endField;

    @Override
    public void initialize(ValidDateRange ann) {
        startField = ann.startDate();
        endField = ann.endDate();
    }

    @Override
    public boolean isValid(Object obj, ConstraintValidatorContext ctx) {
        // Use reflection or getter to get field values
        try {
            LocalDate start = (LocalDate) obj.getClass().getDeclaredField(startField).get(obj);
            LocalDate end   = (LocalDate) obj.getClass().getDeclaredField(endField).get(obj);
            return start == null || end == null || !end.isBefore(start);
        } catch (Exception e) { return true; }
    }
}

@ValidDateRange(startDate = "startDate", endDate = "endDate")
public record DateRangeRequest(
    @NotNull LocalDate startDate,
    @NotNull LocalDate endDate
) {}
```

## Handling Validation Errors — @ExceptionHandler
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidation(MethodArgumentNotValidException ex) {
        Map<String, String> errors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .collect(Collectors.toMap(
                FieldError::getField,
                FieldError::getDefaultMessage,
                (first, second) -> first // keep first error per field
            ));
        return new ErrorResponse("VALIDATION_ERROR", "Request validation failed", errors);
    }

    // For @Validated method-level validation
    @ExceptionHandler(ConstraintViolationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleConstraintViolation(ConstraintViolationException ex) {
        Map<String, String> errors = ex.getConstraintViolations()
            .stream()
            .collect(Collectors.toMap(
                v -> v.getPropertyPath().toString(),
                ConstraintViolation::getMessage,
                (a, b) -> a
            ));
        return new ErrorResponse("VALIDATION_ERROR", "Constraint violation", errors);
    }
}
```

## Validation Groups — Conditional Validation
```java
public interface OnCreate {}
public interface OnUpdate {}

public class Product {
    @NotNull(groups = OnCreate.class)  // required only on create
    @Null(groups = OnUpdate.class)     // must be null on update
    private String id;

    @NotBlank(groups = {OnCreate.class, OnUpdate.class})
    private String name;
}

// @Validated with group
@PutMapping("/{id}")
public ProductDto update(@Validated(OnUpdate.class) @RequestBody Product product) { ... }
```

## Common Mistakes
1. **@NotBlank vs @NotNull vs @NotEmpty:** NotNull: not null. NotEmpty: not null and not empty string/collection. NotBlank: not null, not empty, not all whitespace. Use @NotBlank for String fields.
2. **Ignoring ConstraintViolationException:** @Validated method-level throws ConstraintViolationException, not MethodArgumentNotValidException — different handler needed.
3. **Validating in service when controller already validates:** don't double-validate at every layer unless service is a public API entry point.
""",
"mcqs": [
  {"id":"d47q1","prompt":"What is the difference between @NotNull, @NotEmpty, and @NotBlank?","options":["Identical","@NotNull: field is not null; @NotEmpty: not null AND not empty string/collection; @NotBlank: not null, not empty, and not all whitespace — use @NotBlank for String text fields","@NotBlank is for collections only","@NotEmpty only works with List"],"correctAnswer":"@NotNull: field is not null; @NotEmpty: not null AND not empty string/collection; @NotBlank: not null, not empty, and not all whitespace — use @NotBlank for String text fields","explanation":"For a String ' ' (spaces only): @NotNull passes (not null), @NotEmpty passes (not empty), @NotBlank FAILS (all whitespace). Use @NotBlank for user-input text. Use @NotEmpty for collections/arrays. Use @NotNull for any object reference."},
  {"id":"d47q2","prompt":"What does `@Valid` do when placed before a @RequestBody parameter?","options":["Validates only the top-level fields","Triggers Bean Validation on the deserialized object — processes all constraint annotations (@NotBlank, @Email, etc.) and throws MethodArgumentNotValidException if any fail","Makes the request body optional","Validates the Content-Type header"],"correctAnswer":"Triggers Bean Validation on the deserialized object — processes all constraint annotations (@NotBlank, @Email, etc.) and throws MethodArgumentNotValidException if any fail","explanation":"@Valid activates the validation framework. Jackson deserializes the JSON body first, then validation runs. If any @NotBlank, @Size, @Email etc. fail, Spring throws MethodArgumentNotValidException with all field errors before the controller method body executes."},
  {"id":"d47q3","prompt":"What are the three required elements in a custom constraint annotation?","options":["@Target, @Retention, @Constraint","message(), groups(), payload() — all three must be present in every constraint annotation; otherwise the annotation is not a valid constraint","@NotNull, @NotBlank, @Valid","@Component, @Service, @Repository"],"correctAnswer":"message(), groups(), payload() — all three must be present in every constraint annotation; otherwise the annotation is not a valid constraint","explanation":"Bean Validation spec requires: String message() default '...'; Class<?>[] groups() default {}; Class<? extends Payload>[] payload() default {};. Plus @Constraint(validatedBy=...) to link to the validator. Without these three, the annotation is not a valid constraint."},
  {"id":"d47q4","prompt":"What class do you implement to write a custom constraint validator?","options":["ConstraintProcessor<A, T>","ConstraintValidator<A extends Annotation, T> — A is the annotation type, T is the type being validated; implement isValid(T value, ConstraintValidatorContext ctx)","AbstractValidator<T>","AnnotationProcessor<T>"],"correctAnswer":"ConstraintValidator<A extends Annotation, T> — A is the annotation type, T is the validator type; implement isValid(T value, ConstraintValidatorContext ctx)","explanation":"ConstraintValidator<UniqueEmail, String>: A=UniqueEmail (the annotation), T=String (the annotated field type). isValid() returns true if the value is valid. ConstraintValidatorContext allows custom error messages. Can be a Spring @Component to inject repositories/services."},
  {"id":"d47q5","prompt":"How do you validate that a list's elements pass a constraint (e.g., each tag in List<String> is @NotBlank)?","options":["@NotBlank List<String> validates all elements","Declare the annotation on the type parameter: List<@NotBlank @Size(max=30) String> tags — Bean Validation processes each element","Use a custom class-level validator","Spring validates collections automatically without annotations"],"correctAnswer":"Declare the annotation on the type parameter: List<@NotBlank @Size(max=30) String> tags — Bean Validation processes each element","explanation":"Jakarta Bean Validation 2.0+ supports container element validation. List<@NotBlank String> tags applies @NotBlank to each element in the list. This also works for Map values: Map<String, @NotNull BigDecimal> prices."},
  {"id":"d47q6","prompt":"What exception does @Validated method-level validation throw (as opposed to @RequestBody @Valid)?","options":["MethodArgumentNotValidException","ConstraintViolationException — thrown by the Bean Validation framework directly when @Validated method parameter constraints fail","IllegalArgumentException","HandlerMethodValidationException"],"correctAnswer":"ConstraintViolationException — thrown by the Bean Validation framework directly when @Validated method parameter constraints fail","explanation":"@RequestBody @Valid: Spring MVC catches the validation failure and wraps it in MethodArgumentNotValidException. @Validated on the class with @Valid on method params: the AOP interceptor throws ConstraintViolationException directly. Both need handlers in @RestControllerAdvice."},
  {"id":"d47q7","prompt":"What is a class-level constraint validator used for?","options":["Validating static fields","Validating relationships between multiple fields on the same object — e.g., end date must be after start date","Validating nested objects","Replacing @Valid"],"correctAnswer":"Validating relationships between multiple fields on the same object — e.g., end date must be after start date","explanation":"Field-level validators see only one field. Class-level validators (@Target(TYPE)) receive the whole object, enabling cross-field validation: startDate < endDate, password == confirmPassword, discount < basePrice. The @Constraint annotation is placed on the class declaration."},
  {"id":"d47q8","prompt":"What are validation groups and when are they useful?","options":["Groups of validators that run in parallel","Marker interfaces that allow different validation rules for the same class in different contexts — e.g., create requires @NotNull id, update requires @Null id","@Validated groups for performance","Groups are deprecated in Jakarta Validation 3"],"correctAnswer":"Marker interfaces that allow different validation rules for the same class in different contexts — e.g., create requires @NotNull id, update requires @Null id","explanation":"@NotNull(groups=OnCreate.class) means: only validate this constraint when the OnCreate group is active. @Validated(OnCreate.class) activates only OnCreate group constraints. Different REST operations (POST vs PUT) activate different groups on the same DTO class."},
  {"id":"d47q9","prompt":"A custom @UniqueEmail validator needs to query the database. How can it access a Spring repository?","options":["Static field injection","Implement the validator as a Spring @Component — Spring injects it and dependency injection is available","Use ApplicationContext.getBean()","Custom validators cannot access Spring beans"],"correctAnswer":"Implement the validator as a Spring @Component — Spring injects it and dependency injection is available","explanation":"When Spring detects a @Component that implements ConstraintValidator, it manages it as a Spring bean. Constructor injection, @Autowired, @Value all work. Spring registers it with the Validator — no manual wiring needed."},
  {"id":"d47q10","prompt":"What is the correct error response structure for a validation failure?","options":["Throw 500 Internal Server Error","Return 400 Bad Request with a map of {fieldName: errorMessage} pairs so the client knows which specific fields failed and why","Return 400 with the full exception message","Return 422 with an empty body"],"correctAnswer":"Return 400 Bad Request with a map of {fieldName: errorMessage} pairs so the client knows which specific fields failed and why","explanation":"Good validation errors are actionable: {fieldErrors: {email: 'Invalid email format', name: 'must not be blank'}}. The client (Angular form) can highlight each invalid field. A generic 'Bad request' message forces the client to guess which fields to fix."}
],
"writtenConceptQuestions": [
  "Show a complete CreateOrderRequest record with 6 different constraint annotations. Include nested validation on a List<OrderItemRequest>.",
  "Explain the difference between @NotNull, @NotEmpty, and @NotBlank. For which Java types is each appropriate?",
  "Write a custom @UniqueEmail constraint: the annotation and the ConstraintValidator implementation that queries a UserRepository.",
  "Show the @ExceptionHandler for both MethodArgumentNotValidException (from @RequestBody @Valid) and ConstraintViolationException (from @Validated method params).",
  "What are class-level constraints? Write a @ValidDateRange constraint that validates endDate is after startDate on a DateRangeRequest.",
  "Explain validation groups with OnCreate and OnUpdate interfaces. Show how @Validated(OnCreate.class) activates only create-specific rules.",
  "What does `List<@NotBlank @Size(max=30) String> tags` validate? How does container element validation work in Jakarta Bean Validation 2?"
],
"businessScenarios": [
  "A user registration form submits an email that's already taken. The current API returns 500 (DB unique constraint). Add a @UniqueEmail custom validator that returns 400 with message 'Email already registered' before hitting the DB.",
  "A promotion creation API has startDate and endDate fields. Users submit endDate before startDate and get a 500 from business logic. Add a class-level @ValidDateRange constraint.",
  "An order API validation returns 400 but the error body is just 'Bad Request'. Angular form doesn't know which fields to highlight. Fix the @ExceptionHandler to return {fieldErrors: {fieldName: message}} structure."
]
},

"day-048": {
"notes": """# Spring Boot Exception Handling: @RestControllerAdvice, ProblemDetail, and Error Design

## @RestControllerAdvice — Centralized Error Handling
`@RestControllerAdvice` is `@ControllerAdvice` + `@ResponseBody`. All @ExceptionHandler methods in this class apply to all @RestController methods across the application — no duplication.

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    // Domain not-found → 404
    @ExceptionHandler(NotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(NotFoundException ex, HttpServletRequest req) {
        log.warn("Not found at {}: {}", req.getRequestURI(), ex.getMessage());
        return new ErrorResponse("NOT_FOUND", ex.getMessage());
    }

    // Bean Validation failure → 400
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidation(MethodArgumentNotValidException ex) {
        Map<String, String> fieldErrors = ex.getBindingResult().getFieldErrors()
            .stream().collect(Collectors.toMap(
                FieldError::getField, FieldError::getDefaultMessage, (a,b)->a));
        return new ErrorResponse("VALIDATION_ERROR", "Validation failed", fieldErrors);
    }

    // JSON parse error → 400
    @ExceptionHandler(HttpMessageNotReadableException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleBadJson(HttpMessageNotReadableException ex) {
        return new ErrorResponse("MALFORMED_REQUEST", "Request body cannot be parsed");
    }

    // Wrong HTTP method → 405
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    @ResponseStatus(HttpStatus.METHOD_NOT_ALLOWED)
    public ErrorResponse handleMethodNotAllowed(HttpRequestMethodNotSupportedException ex) {
        return new ErrorResponse("METHOD_NOT_ALLOWED", "HTTP method not supported: " + ex.getMethod());
    }

    // Catch-all → 500 (never expose internal details)
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleUnexpected(Exception ex, HttpServletRequest req) {
        log.error("Unexpected error at {}", req.getRequestURI(), ex); // full trace in logs
        return new ErrorResponse("INTERNAL_ERROR", "An unexpected error occurred");
    }
}
```

## Error Response Design
```java
// Standard error response — consistent shape clients can rely on
public record ErrorResponse(
    String code,
    String message,
    Map<String, String> fieldErrors,
    String timestamp,
    String path
) {
    // Convenience constructors
    public ErrorResponse(String code, String message) {
        this(code, message, null, Instant.now().toString(), null);
    }
    public ErrorResponse(String code, String message, Map<String, String> fieldErrors) {
        this(code, message, fieldErrors, Instant.now().toString(), null);
    }
}
```

## ProblemDetail — RFC 7807 (Spring Boot 3+)
Spring Boot 3 supports RFC 7807 Problem Details out of the box:
```java
@ExceptionHandler(NotFoundException.class)
public ProblemDetail handleNotFound(NotFoundException ex, HttpServletRequest req) {
    ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
    pd.setTitle("Resource Not Found");
    pd.setType(URI.create("https://api.example.com/errors/not-found"));
    pd.setProperty("errorCode", ex.getErrorCode());
    pd.setProperty("timestamp", Instant.now().toString());
    return pd;
}
// Response:
// { "type": "https://api.example.com/errors/not-found",
//   "title": "Resource Not Found",
//   "status": 404,
//   "detail": "Order not found: order-123",
//   "errorCode": "NOT_FOUND",
//   "timestamp": "2024-06-15T14:30:00Z" }

// Enable problem details globally:
// application.properties: spring.mvc.problemdetails.enabled=true
```

## Exception Hierarchy in Service Layer
```java
// Base
public class AppException extends RuntimeException {
    private final String code;
    private final HttpStatus status;
    public AppException(String code, String message, HttpStatus status) {
        super(message); this.code = code; this.status = status;
    }
}

// Specific exceptions
public class NotFoundException extends AppException {
    public NotFoundException(String entity, Object id) {
        super("NOT_FOUND", entity + " not found: " + id, HttpStatus.NOT_FOUND);
    }
}
public class BusinessException extends AppException {
    public BusinessException(String message) {
        super("BUSINESS_ERROR", message, HttpStatus.UNPROCESSABLE_ENTITY);
    }
}

// Generic handler using the base class
@ExceptionHandler(AppException.class)
public ResponseEntity<ErrorResponse> handleApp(AppException ex) {
    return ResponseEntity
        .status(ex.getStatus())
        .body(new ErrorResponse(ex.getCode(), ex.getMessage()));
}
```

## Exception Handling for Async and Scheduled Methods
```java
// @Async methods — exceptions don't propagate to the caller thread
// Catch in the Future or use UncaughtExceptionHandler
@Async
public CompletableFuture<Void> sendEmailAsync(String to, String subject) {
    return CompletableFuture.runAsync(() -> emailClient.send(to, subject))
        .exceptionally(ex -> {
            log.error("Async email failed to {}: {}", to, ex.getMessage());
            return null;
        });
}

// @Scheduled methods — exceptions swallow silently by default; always log
@Scheduled(cron = "0 0 * * * *")
public void hourlyReport() {
    try {
        reportService.generate();
    } catch (Exception e) {
        log.error("Hourly report failed", e); // without this, failure is invisible
    }
}
```

## Common Mistakes
1. **Multiple @RestControllerAdvice classes with overlapping handlers:** only one handler per exception type should exist. Use one global advice class.
2. **Returning 200 OK with error body:** always use the correct HTTP status.
3. **Logging without the exception object:** `log.error("Failed: " + e.getMessage())` loses the stack trace. Use `log.error("Failed", e)`.
4. **Not handling HttpMessageNotReadableException:** malformed JSON returns a Spring default error format instead of your API format.
""",
"mcqs": [
  {"id":"d48q1","prompt":"What is the difference between @ControllerAdvice and @RestControllerAdvice?","options":["@RestControllerAdvice handles more exception types","@RestControllerAdvice = @ControllerAdvice + @ResponseBody — all @ExceptionHandler methods automatically serialize return values to JSON instead of view names","@ControllerAdvice only works with @Controller","@RestControllerAdvice only handles REST exceptions"],"correctAnswer":"@RestControllerAdvice = @ControllerAdvice + @ResponseBody — all @ExceptionHandler methods automatically serialize return values to JSON instead of view names","explanation":"@ControllerAdvice handles both MVC view controllers and REST controllers. Return type is interpreted as a view name unless @ResponseBody is added per method. @RestControllerAdvice adds @ResponseBody globally — every handler method returns JSON directly."},
  {"id":"d48q2","prompt":"In what order does Spring pick which @ExceptionHandler to call when an exception is thrown?","options":["The first handler registered wins","Most specific exception type first: an ExceptionHandler(NotFoundException.class) takes priority over ExceptionHandler(Exception.class) for a NotFoundException","Alphabetical by exception class name","All handlers run in parallel"],"correctAnswer":"Most specific exception type first: an ExceptionHandler(NotFoundException.class) takes priority over ExceptionHandler(Exception.class) for a NotFoundException","explanation":"Spring finds the most specific handler: 1) exact exception type match, 2) superclass match, 3) further up the hierarchy. NotFoundException extends RuntimeException extends Exception — the NotFoundException handler wins. ExceptionHandler(Exception.class) is the fallback."},
  {"id":"d48q3","prompt":"What does RFC 7807 ProblemDetail provide over a custom ErrorResponse record?","options":["Faster serialization","A standardized JSON error format (type, title, status, detail, instance) recognized by clients and tools without custom parsing","Required by Spring Boot 3","Automatic exception logging"],"correctAnswer":"A standardized JSON error format (type, title, status, detail, instance) recognized by clients and tools without custom parsing","explanation":"RFC 7807 defines a media type application/problem+json with standard fields: type (URI), title, status, detail, instance. Client libraries and API gateways can parse problem details without custom code. Spring Boot 3 supports it natively via ProblemDetail class."},
  {"id":"d48q4","prompt":"What is the correct log pattern when logging an exception?","options":["log.error('Error: ' + e.getMessage())","log.error('Error processing request', e) — pass the exception as the last argument; SLF4J/Logback includes the full stack trace","log.error(e.toString())","log.error(e.getStackTrace().toString())"],"correctAnswer":"log.error('Error processing request', e) — pass the exception as the last argument; SLF4J/Logback includes the full stack trace","explanation":"log.error('message', e): SLF4J recognizes the last Throwable argument and appends the full stack trace to the log entry. log.error('message: ' + e.getMessage()) logs only the message string — the stack trace is lost, making debugging extremely hard."},
  {"id":"d48q5","prompt":"Why should a catch-all @ExceptionHandler(Exception.class) never return internal details?","options":["Performance reason","Stack traces and class names expose internal architecture, library versions, and attack surfaces — log internally, return a generic message to clients","Exception.class handler doesn't run for checked exceptions","Spring requires a generic message"],"correctAnswer":"Stack traces and class names expose internal architecture, library versions, and attack surfaces — log internally, return a generic message to clients","explanation":"Returning 'org.hibernate.exception.ConstraintViolationException at com.example...' tells attackers which DB library, ORM version, and package structure you use. Log the full trace for developers (log.error(..., ex)) but return only 'An unexpected error occurred' to clients."},
  {"id":"d48q6","prompt":"What happens to exceptions thrown in @Async methods without explicit handling?","options":["They propagate to the caller thread","They are silently swallowed unless the returned CompletableFuture/Future is observed — the caller may never know the operation failed","Spring automatically logs them","They trigger the @ExceptionHandler in @RestControllerAdvice"],"correctAnswer":"They are silently swallowed unless the returned CompletableFuture/Future is observed — the caller may never know the operation failed","explanation":"@Async methods run on a separate thread. If the method returns void, exceptions are lost (only logged by Spring's AsyncUncaughtExceptionHandler). If it returns CompletableFuture, the exception is stored in the future and rethrown on .get(). Always handle exceptionally() or observe the future."},
  {"id":"d48q7","prompt":"What exception does Spring throw when a client sends malformed JSON in a @RequestBody?","options":["JsonParseException","HttpMessageNotReadableException — thrown when Jackson cannot deserialize the request body; handle in @ExceptionHandler to return 400 in your API format","MethodArgumentNotValidException","IllegalArgumentException"],"correctAnswer":"HttpMessageNotReadableException — thrown when Jackson cannot deserialize the request body; handle in @ExceptionHandler to return 400 in your API format","explanation":"@RequestBody with an invalid JSON body: Spring throws HttpMessageNotReadableException before even reaching the controller method. Without a handler, Spring returns its default error format. Add @ExceptionHandler(HttpMessageNotReadableException.class) → 400 MALFORMED_REQUEST."},
  {"id":"d48q8","prompt":"What is the benefit of using a base AppException with a HttpStatus field?","options":["Enforces singleton pattern","A single @ExceptionHandler(AppException.class) can handle all domain exceptions — uses ex.getStatus() for the response code and ex.getCode() for the error code, eliminating per-exception handlers","AppException is required by Spring","HttpStatus field enables HATEOAS"],"correctAnswer":"A single @ExceptionHandler(AppException.class) can handle all domain exceptions — uses ex.getStatus() for the response code and ex.getCode() for the error code, eliminating per-exception handlers","explanation":"With status and code in the base exception, one handler: ResponseEntity.status(ex.getStatus()).body(new ErrorResponse(ex.getCode(), ex.getMessage())) handles all AppException subclasses. Specific handlers remain for exceptions needing special logic (e.g., MethodArgumentNotValidException with field errors)."},
  {"id":"d48q9","prompt":"Why should @Scheduled methods always wrap their body in try-catch?","options":["Performance requirement","Uncaught exceptions in @Scheduled methods are logged by Spring but the scheduled task continues to run on subsequent cycles — the failure may go unnoticed without explicit logging/alerting","@Scheduled requires try-catch","Exceptions in @Scheduled stop the scheduler"],"correctAnswer":"Uncaught exceptions in @Scheduled methods are logged by Spring but the scheduled task continues to run on subsequent cycles — the failure may go unnoticed without explicit logging/alerting","explanation":"Unlike web requests (where @ExceptionHandler catches everything), scheduled tasks run detached from any request context. An exception in @Scheduled is logged at ERROR level by Spring's scheduler, but without explicit catch-and-alert, the failure may not be noticed. Add catch: log.error('Task failed', e) and optionally trigger an alert."},
  {"id":"d48q10","prompt":"What HTTP status does @ExceptionHandler(HttpRequestMethodNotSupportedException.class) typically return?","options":["404 Not Found","405 Method Not Allowed — the URL exists but the HTTP method (GET/POST/etc.) is not supported","400 Bad Request","500 Internal Server Error"],"correctAnswer":"405 Method Not Allowed — the URL exists but the HTTP method (GET/POST/etc.) is not supported","explanation":"405 Method Not Allowed: request URL matches a handler but the HTTP method doesn't. Spring throws HttpRequestMethodNotSupportedException. Without a custom handler, Spring returns its default error page. Map it to 405 with a consistent JSON response and an Allow header listing supported methods."}
],
"writtenConceptQuestions": [
  "Write a complete @RestControllerAdvice covering: NotFoundException→404, ValidationException→400 with field errors, HttpMessageNotReadableException→400, and Exception→500.",
  "Design an exception hierarchy: AppException base with HttpStatus and code fields, then NotFoundException, BusinessException, ConflictException subclasses. Show the single generic handler.",
  "What is RFC 7807 ProblemDetail? Show a NotFoundException mapped to ProblemDetail with type URI, title, and custom errorCode property.",
  "Explain why `log.error('Failed: ' + e.getMessage())` is wrong. What is lost and what is the correct pattern?",
  "How do exceptions in @Async methods behave? Show a CompletableFuture.exceptionally() handler for an async email send.",
  "What is HttpMessageNotReadableException? Show when it's thrown and the @ExceptionHandler that returns 400 MALFORMED_REQUEST.",
  "Why should the catch-all Exception handler never expose stack traces or class names in the response? Show a secure catch-all."
],
"businessScenarios": [
  "A mobile app shows 'Internal Server Error' for all API failures. The backend returns stack traces in error responses. Replace with a @RestControllerAdvice that maps domain exceptions to status codes and returns structured {code, message} — no internal details to clients.",
  "A payment processing service has 15 different exception classes each with its own @ExceptionHandler duplicated across 3 controllers. Consolidate using a base AppException class and one @RestControllerAdvice.",
  "Scheduled report generation silently fails at 2 AM. Support team discovers 3 days later when clients complain. Add try-catch with ERROR logging and an alerting hook (call alertService.sendAlert()) on exception."
]
},

"day-049": {
"notes": """# Logging in Spring Boot: SLF4J, Logback, Structured Logging, and Production Patterns

## SLF4J — Logging Facade
SLF4J (Simple Logging Facade for Java) is an abstraction — write `log.info(...)` and the actual implementation (Logback, Log4j2, JUL) is plugged in at runtime. Spring Boot bundles Logback by default.
```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OrderService {
    private static final Logger log = LoggerFactory.getLogger(OrderService.class);
    // or with Lombok:
    // @Slf4j on the class — injects `log` field automatically
}
```

## Log Levels — When to Use Each
```java
// TRACE — most verbose, method entry/exit, loop iterations (almost never in production)
log.trace("Entering calculatePrice() with {} items", items.size());

// DEBUG — diagnostic info useful during development and debugging
log.debug("Order {} status changed: {} → {}", orderId, oldStatus, newStatus);

// INFO — business-significant events (the default production level)
log.info("Order {} created by user {} for ${}", orderId, userId, total);
log.info("User {} logged in from {}", userId, ipAddress);

// WARN — recoverable issues, degraded mode, deprecated usage
log.warn("Payment retry #{} for order {} — previous attempt failed", attempt, orderId);
log.warn("Cache miss rate {}% exceeds threshold", missRate);

// ERROR — failures requiring attention (send to alerting, PagerDuty)
log.error("Failed to process payment for order {}", orderId, exception); // pass exception as last arg!
```

## Parameterized Logging — Never Concatenate
```java
// WRONG — string concatenation runs even when DEBUG is disabled
log.debug("Processing order: " + order.toString()); // toString() called regardless

// CORRECT — parameterized; {} substitution only if the level is active
log.debug("Processing order: {}", order);

// Multiple parameters
log.info("User {} created order {} with {} items totaling ${}",
    userId, orderId, items.size(), total);

// Exception parameter — always last (SLF4J prints stack trace)
log.error("Order processing failed for {}", orderId, exception);
```

## Logback Configuration — logback-spring.xml
```xml
<!-- src/main/resources/logback-spring.xml -->
<configuration>
    <springProperty scope="context" name="appName" source="spring.application.name"/>

    <!-- Console appender (dev) -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{ISO8601} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- Rolling file appender (prod) -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/${appName}.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/${appName}.%d{yyyy-MM-dd}.log.gz</fileNamePattern>
            <maxHistory>30</maxHistory>  <!-- keep 30 days -->
        </rollingPolicy>
        <encoder>
            <pattern>%d{ISO8601} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- Package-level control -->
    <logger name="com.example.app" level="DEBUG"/>      <!-- your code: DEBUG -->
    <logger name="org.springframework" level="WARN"/>   <!-- Spring: only WARN+ -->
    <logger name="org.hibernate.SQL" level="DEBUG"/>    <!-- show SQL -->

    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
</configuration>
```

## MDC — Mapped Diagnostic Context for Correlation
MDC adds key-value pairs to every log line in the current thread — essential for tracing a request across log entries:
```java
// In a filter/interceptor — set MDC at request start
@Component
public class RequestLoggingFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res,
                                    FilterChain chain) throws IOException, ServletException {
        String requestId = UUID.randomUUID().toString();
        String userId = extractUserId(req);
        MDC.put("requestId", requestId);
        MDC.put("userId", userId);
        MDC.put("path", req.getRequestURI());
        try {
            chain.doFilter(req, res);
        } finally {
            MDC.clear(); // MUST clear to prevent leaks in thread pool reuse
        }
    }
}

// In logback pattern: include MDC fields
// %d{ISO8601} [%X{requestId}] [user:%X{userId}] %-5level %logger - %msg%n
// Log output: 2024-06-15 14:30:01 [req-abc123] [user:user-456] INFO OrderService - Order created
```

## Structured Logging — JSON for ELK/Splunk
```java
// logstash-logback-encoder: logs JSON instead of text (better for log aggregators)
// <dependency>net.logstash.logback:logstash-logback-encoder:7.4</dependency>
// <appender class="ch.qos.logback.core.ConsoleAppender">
//   <encoder class="net.logstash.logback.encoder.LogstashEncoder"/>
// </appender>
// Output: {"@timestamp":"2024-06-15T14:30:01Z","level":"INFO","message":"Order created",
//           "requestId":"abc123","userId":"user-456","logger":"com.example.OrderService"}
```

## Logging in Spring Boot Properties
```properties
# application.properties — quick level control without XML
logging.level.root=WARN
logging.level.com.example=DEBUG
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.springframework.web=INFO

# Log to file
logging.file.name=logs/application.log
logging.logback.rollingpolicy.max-history=30
logging.logback.rollingpolicy.file-name-pattern=logs/app-%d{yyyy-MM-dd}.log.gz
```

## Common Mistakes
1. **String concatenation in log statements:** wastes CPU on string building when level is off.
2. **Logging sensitive data:** never log passwords, tokens, PII, credit card numbers.
3. **Forgetting MDC.clear():** MDC is ThreadLocal — not clearing it leaks context to the next request on the same thread.
4. **Catching and logging without re-throwing:** `catch (Exception e) { log.error("...", e); }` swallows the exception. Log AND throw unless you're handling it.
""",
"mcqs": [
  {"id":"d49q1","prompt":"Why use parameterized logging `log.debug('Order: {}', order)` instead of `log.debug('Order: ' + order)`?","options":["Parameterized is more readable","String concatenation runs even when DEBUG is disabled, wasting CPU and memory; parameterized logging skips substitution if the level is not active","Parameterized logging is required by SLF4J","Concatenation causes NPE if order is null"],"correctAnswer":"String concatenation runs even when DEBUG is disabled, wasting CPU and memory; parameterized logging skips substitution if the level is not active","explanation":"log.debug('val: ' + expensive.toString()): expensive.toString() called always, even if DEBUG is off. log.debug('val: {}', expensive): expensive.toString() is only called when DEBUG is active. For heavy objects or tight loops, this matters."},
  {"id":"d49q2","prompt":"What does MDC (Mapped Diagnostic Context) do?","options":["Maps log levels to HTTP status codes","Stores key-value pairs (requestId, userId) in a ThreadLocal context that are automatically included in every log line for that thread — enables tracing a request across log entries","Provides a configuration map for loggers","MDC is a logging library"],"correctAnswer":"Stores key-value pairs (requestId, userId) in a ThreadLocal context that are automatically included in every log line for that thread — enables tracing a request across log entries","explanation":"MDC.put('requestId', 'abc123') — every subsequent log.info/debug/error on that thread includes [requestId=abc123]. In production, this lets you grep all log lines for a single request. Logback pattern %X{requestId} injects the MDC value."},
  {"id":"d49q3","prompt":"Why MUST you call MDC.clear() in a finally block?","options":["MDC becomes null without clearing","MDC is ThreadLocal — thread pool threads are reused; without clearing, the next request on the same thread gets the previous request's MDC values (wrong requestId, wrong userId)","MDC.clear() improves performance","Spring requires it"],"correctAnswer":"MDC is ThreadLocal — thread pool threads are reused; without clearing, the next request on the same thread gets the previous request's MDC values (wrong requestId, wrong userId)","explanation":"Tomcat's thread pool reuses threads. MDC.put() in request #1, no MDC.clear() — next request on the same thread has MDC from request #1. Logs show wrong requestId. MDC.clear() in finally block guarantees a clean slate for the next request."},
  {"id":"d49q4","prompt":"Which log level is appropriate for a successful user login event in production?","options":["TRACE","DEBUG","INFO — business-significant event that should appear in production logs","ERROR"],"correctAnswer":"INFO — business-significant event that should appear in production logs","explanation":"INFO: business events (user login, order created, payment processed). These are the events you want visible in production logs. DEBUG: developer diagnostics (only enable when debugging). TRACE: too verbose for production. WARN/ERROR: only for problems."},
  {"id":"d49q5","prompt":"What does `log.error('Failed for {}', orderId, exception)` do compared to `log.error('Failed for ' + orderId, exception)`?","options":["Identical output","Parameterized: substitution only if ERROR is active; also SLF4J correctly identifies the last Throwable argument and logs the stack trace","Concatenated form loses the stack trace","Exception must be the first argument"],"correctAnswer":"Parameterized: substitution only if ERROR is active; also SLF4J correctly identifies the last Throwable argument and logs the stack trace","explanation":"SLF4J convention: last argument of type Throwable → print stack trace. log.error('Failed for {}', orderId, exception): {} is filled with orderId, exception is recognized as Throwable and stack trace is appended. Works with both parameterized and concatenated forms — parameterized is preferred for consistency."},
  {"id":"d49q6","prompt":"What is structured logging (JSON logs) and why is it preferred for cloud deployments?","options":["Logs stored in a database","Log lines emitted as JSON objects — each field (timestamp, level, message, MDC values) is a JSON key-value pair parseable by log aggregators (ELK, Splunk, Datadog) without regex","Required for Docker","JSON is compressed more efficiently"],"correctAnswer":"Log lines emitted as JSON objects — each field (timestamp, level, message, MDC values) is a JSON key-value pair parseable by log aggregators (ELK, Splunk, Datadog) without regex","explanation":"Text logs: 'INFO 2024-06-15 Order created' — aggregators parse with regex (fragile, slow). JSON logs: {timestamp:'2024-06-15', level:'INFO', message:'Order created', orderId:'123'} — parsed natively, all fields queryable, MDC context automatically included."},
  {"id":"d49q7","prompt":"What does `<logger name='org.hibernate.SQL' level='DEBUG'/>` in logback.xml enable?","options":["Hibernate query cache debugging","Prints all SQL statements that Hibernate executes to the log — essential for N+1 detection and query debugging","Enables query statistics","Logs Hibernate configuration"],"correctAnswer":"Prints all SQL statements that Hibernate executes to the log — essential for N+1 detection and query debugging","explanation":"org.hibernate.SQL at DEBUG level shows each SQL query. Combine with org.hibernate.type.descriptor.sql at TRACE to see bind parameter values. Essential for detecting N+1 queries, missing indexes, and unexpected joins in development. Never enable in production (too verbose, leaks query patterns)."},
  {"id":"d49q8","prompt":"What security risk does logging create if not handled carefully?","options":["Log files can be deleted","Accidentally logging passwords, tokens, PII, or credit card numbers — log files may be accessible to many people and are often shipped to log aggregators","Logging consumes too much CPU","Logs can be tampered with"],"correctAnswer":"Accidentally logging passwords, tokens, PII, or credit card numbers — log files may be accessible to many people and are often shipped to log aggregators","explanation":"log.info('User login: email={} password={}', email, password) — password visible in logs. Never log: passwords, auth tokens, session IDs, credit card numbers, SSN. These appear in ELK, Splunk, Datadog, and potentially developer workstations — a GDPR/PCI violation."},
  {"id":"d49q9","prompt":"What is the difference between INFO, WARN, and ERROR log levels?","options":["Only the label differs","INFO: normal business events; WARN: degraded but functional (retry, fallback, threshold exceeded); ERROR: failure requiring human attention or automated alerting","DEBUG and INFO are identical","ERROR stops the application"],"correctAnswer":"INFO: normal business events; WARN: degraded but functional (retry, fallback, threshold exceeded); ERROR: failure requiring human attention or automated alerting","explanation":"Use WARN for: cache miss rate high, retry attempt, near threshold. Use ERROR for: DB connection failed, payment processing failed, unhandled exception. ERRORs should trigger PagerDuty/alerting. WARNs are for monitoring dashboards. INFO is the narrative of what the system is doing."},
  {"id":"d49q10","prompt":"What does `@Slf4j` (Lombok) do on a class?","options":["Implements Serializable","Injects `private static final Logger log = LoggerFactory.getLogger(ClassName.class)` automatically — no boilerplate declaration needed","Marks the class for logging proxy","Creates a logging aspect"],"correctAnswer":"Injects `private static final Logger log = LoggerFactory.getLogger(ClassName.class)` automatically — no boilerplate declaration needed","explanation":"Lombok's @Slf4j annotation generates the standard logger field at compile time. Instead of declaring `private static final Logger log = LoggerFactory.getLogger(OrderService.class)`, just add @Slf4j and use log.info() directly. Also @Log4j2 for Log4j2, @CommonsLog for Apache Commons."}
],
"writtenConceptQuestions": [
  "Show a Spring Boot filter that sets MDC requestId, userId, and path at the start of each request and clears MDC in a finally block.",
  "Explain the 5 log levels with a concrete example for each. What events belong at WARN vs ERROR?",
  "Why is parameterized logging important? Show a benchmark scenario where concatenation wastes CPU in a high-throughput loop.",
  "Show a logback-spring.xml with console (dev), rolling file (prod), and JSON encoder (cloud). Include package-level level control.",
  "What sensitive data should never be logged? Show 3 examples of dangerous log statements and their secure alternatives.",
  "Show how to configure SQL logging in development using Hibernate logger. What are the performance implications in production?",
  "Explain structured (JSON) logging. Why is it better for cloud-native applications? Show the logstash-logback-encoder configuration."
],
"businessScenarios": [
  "Support team needs to trace all log entries for a specific user's failing request. Currently logs have no correlation. Add MDC with requestId and userId in a servlet filter so support can grep by requestId.",
  "A GDPR audit discovers that user passwords and email addresses appear in application logs. Identify 4 types of sensitive data and show how to redact them or use safe placeholder logging.",
  "Production server has 500GB of log files with no rotation. Add rolling policy to logback-spring.xml: daily rotation, gzip compression, 30-day retention, max 2GB total size."
]
},

"day-050": {
"notes": """# Spring Boot Configuration: Properties, YAML, Profiles, and Externalized Config

## application.properties vs application.yml
Both configure Spring Boot applications. YAML is preferred for nested config.
```properties
# application.properties — flat key=value
spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
spring.datasource.username=user
spring.datasource.password=secret
spring.jpa.hibernate.ddl-auto=validate
app.payment.api-key=sk-live-abc123
app.payment.timeout-seconds=30
```
```yaml
# application.yml — hierarchical, less repetition
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: user
    password: secret
  jpa:
    hibernate:
      ddl-auto: validate
app:
  payment:
    api-key: sk-live-abc123
    timeout-seconds: 30
```

## @ConfigurationProperties — Typed Configuration
```java
@ConfigurationProperties(prefix = "app.payment")
@Component  // or add @EnableConfigurationProperties(PaymentConfig.class) on a @Configuration
@Validated  // enables Bean Validation on configuration properties
public class PaymentConfig {
    @NotBlank
    private String apiKey;

    @Min(1) @Max(300)
    private int timeoutSeconds = 30;

    @NotNull
    private String baseUrl;

    private boolean sandboxMode = false;

    // Lists and maps work too
    private List<String> allowedCurrencies = List.of("USD", "EUR");
    private Map<String, String> endpoints = new HashMap<>();

    // getters and setters required (or use @ConstructorBinding for records)
}
```

## Spring Profiles — Environment-Specific Configuration
```yaml
# application.yml — base config (shared)
spring:
  application:
    name: order-service
server:
  port: 8080

---
# application-dev.yml — development overrides
spring:
  config:
    activate:
      on-profile: dev
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
  jpa:
    hibernate:
      ddl-auto: create-drop

---
# application-prod.yml — production config
spring:
  config:
    activate:
      on-profile: prod
  datasource:
    url: ${DB_URL}          # from environment variable
    username: ${DB_USER}
    password: ${DB_PASS}
  jpa:
    hibernate:
      ddl-auto: validate    # NEVER create/update in prod
```

## Configuration Precedence (lowest to highest)
1. Default properties (Spring Boot defaults)
2. `application.properties/yml` in resources
3. Profile-specific: `application-{profile}.properties/yml`
4. Environment variables
5. Command-line args: `--app.payment.timeout-seconds=60`
6. Java system properties: `-Dapp.payment.timeout-seconds=60`

```bash
# Override at deployment time (highest priority)
java -jar app.jar --spring.profiles.active=prod --app.payment.api-key=sk-live-xyz
```

## Environment Variables — Relaxed Binding
Spring Boot's relaxed binding maps environment variable naming conventions:
```
APP_PAYMENT_API_KEY=sk-live-xyz
# maps to: app.payment.api-key (kebab-case)
# maps to: app.payment.apiKey (camelCase)
# maps to: app.payment.api_key (snake_case)
# All three map to the same property
```

## @Value — Direct Property Injection
```java
@Service
public class EmailService {
    @Value("${email.smtp.host}")
    private String smtpHost;

    @Value("${email.smtp.port:587}")  // default 587
    private int smtpPort;

    @Value("${email.from:noreply@example.com}")
    private String fromAddress;

    @Value("${app.features.email-enabled:true}")
    private boolean emailEnabled;

    // SpEL expression
    @Value("#{${app.payment.timeout-seconds} * 1000}")
    private long timeoutMs;
}
```

## Configuration in Tests
```java
// Override properties in a specific test
@SpringBootTest
@TestPropertySource(properties = {
    "app.payment.sandbox-mode=true",
    "app.payment.api-key=sk-test-123"
})
class PaymentServiceIntegrationTest { ... }

// Or use a test application.properties file
// src/test/resources/application-test.properties
// Activated by @ActiveProfiles("test")
@SpringBootTest
@ActiveProfiles("test")
class OrderServiceTest { ... }
```

## Secrets Management — Never Hardcode Secrets
```yaml
# WRONG — secrets in application.yml committed to git
spring:
  datasource:
    password: SuperSecret123

# CORRECT — reference environment variables
spring:
  datasource:
    password: ${DB_PASSWORD}  # set in deployment environment (Railway, K8s secret, AWS SSM)
```

## Common Mistakes
1. **Hardcoding secrets in properties files:** commit to git → exposed. Always use `${ENV_VAR}`.
2. **`ddl-auto: create-drop` in prod:** drops and recreates all tables on startup. Use `validate` in prod.
3. **Duplicating properties across profiles:** put shared config in the base `application.yml`, only override what differs per profile.
4. **@Value not working:** occurs when used in a class not managed by Spring (e.g., `new MyService()` instead of injection).
""",
"mcqs": [
  {"id":"d50q1","prompt":"What is the property value precedence order in Spring Boot?","options":["application.yml always wins","Command-line args > environment variables > profile-specific properties > application.yml — higher priority sources override lower ones","application.yml > environment variables","All sources merge with no override"],"correctAnswer":"Command-line args > environment variables > profile-specific properties > application.yml — higher priority sources override lower ones","explanation":"Priority (highest first): command-line args → Java system properties → environment variables → profile-specific yml/properties → application.yml → Spring Boot defaults. This allows deployment-time config override without changing code."},
  {"id":"d50q2","prompt":"What does `${DB_PASSWORD}` in application.yml do?","options":["Evaluates a SpEL expression","References the DB_PASSWORD environment variable — if not set, startup fails with a missing property error","Creates a DB_PASSWORD environment variable","Generates a random password"],"correctAnswer":"References the DB_PASSWORD environment variable — if not set, startup fails with a missing property error","explanation":"${ENV_VAR} in Spring properties resolves to the environment variable's value at startup. If the variable isn't set, Spring throws IllegalArgumentException: 'Could not resolve placeholder DB_PASSWORD'. Use ${DB_PASSWORD:default} to provide a fallback."},
  {"id":"d50q3","prompt":"What does Spring Boot's relaxed binding mean for environment variable names?","options":["All properties are case-insensitive","APP_PAYMENT_API_KEY (uppercase with underscores) maps to app.payment.api-key, app.payment.apiKey, and app.payment.api_key — Spring normalizes naming conventions","Environment variables must match exactly","Relaxed binding is deprecated"],"correctAnswer":"APP_PAYMENT_API_KEY (uppercase with underscores) maps to app.payment.api-key, app.payment.apiKey, and app.payment.api_key — Spring normalizes naming conventions","explanation":"Environment variables can't contain hyphens. Spring's relaxed binding normalizes: APP_PAYMENT_API_KEY → any of the equivalent property forms. This lets you use standard env var naming (SCREAMING_SNAKE_CASE) and it maps to kebab-case properties."},
  {"id":"d50q4","prompt":"Why is `spring.jpa.hibernate.ddl-auto=create-drop` dangerous in production?","options":["It creates too many tables","It drops ALL tables and recreates them on EVERY startup — all data is permanently deleted when the app restarts","It creates duplicate tables","ddl-auto doesn't affect production"],"correctAnswer":"It drops ALL tables and recreates them on EVERY startup — all data is permanently deleted when the app restarts","explanation":"create-drop: creates schema on startup, drops on shutdown. Used for testing with fresh data. In prod: any restart (deploy, crash recovery) wipes the database. Use validate in prod (checks schema matches entities, fails fast if not) or none (no DDL operations — managed by Flyway/Liquibase)."},
  {"id":"d50q5","prompt":"What does `@ConfigurationProperties(prefix = 'app.payment')` do?","options":["Sets the payment prefix for all beans","Binds all properties starting with app.payment.* to the annotated class fields — apiKey binds from app.payment.api-key, timeoutSeconds from app.payment.timeout-seconds","Validates payment configuration","Creates a payment endpoint at /app/payment"],"correctAnswer":"Binds all properties starting with app.payment.* to the annotated class fields — apiKey binds from app.payment.api-key, timeoutSeconds from app.payment.timeout-seconds","explanation":"@ConfigurationProperties(prefix='app.payment') binds all matching properties using relaxed binding. paymentConfig.apiKey gets the value of app.payment.api-key. Supports nested objects, lists, and maps. Much cleaner than multiple @Value annotations for related config."},
  {"id":"d50q6","prompt":"What is the purpose of @ActiveProfiles('test') in a test class?","options":["Runs tests only on test machines","Activates the 'test' Spring profile — loads application-test.properties/yml and activates @Profile('test') beans (mock services, in-memory DB)","Makes tests run faster","Required for @SpringBootTest"],"correctAnswer":"Activates the 'test' Spring profile — loads application-test.properties/yml and activates @Profile('test') beans (mock services, in-memory DB)","explanation":"@ActiveProfiles('test') tells Spring to activate the 'test' profile. This loads application-test.properties (or yml) which overrides dev/prod settings. @Profile('test') beans (H2 DataSource, mock EmailService) are created. Keeps test config separate from production config."},
  {"id":"d50q7","prompt":"What does `@Value('#{${timeout} * 1000}')` inject?","options":["The string '#{${timeout} * 1000}'","Evaluates the SpEL expression: reads the 'timeout' property and multiplies it by 1000 — converts seconds to milliseconds as a long","Injects 1000 regardless","Throws an error because SpEL can't multiply"],"correctAnswer":"Evaluates the SpEL expression: reads the 'timeout' property and multiplies it by 1000 — converts seconds to milliseconds as a long","explanation":"@Value supports Spring Expression Language (SpEL) with #{...}. #{${timeout} * 1000}: outer #{} is SpEL, inner ${timeout} resolves the property first, then * 1000 is computed. Result: if timeout=30, injects 30000 (30 seconds in milliseconds)."},
  {"id":"d50q8","prompt":"What is a profile-specific properties file like `application-prod.yml`?","options":["The main production config file","A file that overrides application.yml settings when the 'prod' profile is active — activated by spring.profiles.active=prod or SPRING_PROFILES_ACTIVE=prod","A required file for production deployments","A file that replaces application.yml"],"correctAnswer":"A file that overrides application.yml settings when the 'prod' profile is active — activated by spring.profiles.active=prod or SPRING_PROFILES_ACTIVE=prod","explanation":"Spring Boot loads: application.yml (always) + application-{activeProfile}.yml (when profile is active). Profile-specific file settings override base settings. Best practice: put shared config in application.yml, put environment-specific overrides in application-dev.yml, application-prod.yml."},
  {"id":"d50q9","prompt":"Why does @Value not work in a class instantiated with `new MyService()`?","options":["@Value only works in @Service classes","@Value injection is performed by Spring's dependency injection mechanism — only works in Spring-managed beans. Objects created with `new` bypass Spring and never have their @Value fields populated","@Value requires @Autowired","new MyService() triggers a different injection mechanism"],"correctAnswer":"@Value injection is performed by Spring's dependency injection mechanism — only works in Spring-managed beans. Objects created with `new` bypass Spring and never have their @Value fields populated","explanation":"Spring's injection (both @Autowired and @Value) happens via BeanPostProcessor after the bean is created by the Spring container. new MyService() creates a plain Java object — Spring has no opportunity to inject. All Spring annotations require the bean to be Spring-managed."},
  {"id":"d50q10","prompt":"What configuration should NEVER be committed to a git repository?","options":["Logging configuration","Secrets: database passwords, API keys, JWT secret, OAuth client secrets — use environment variables or secret management systems instead","Server port number","Spring profile names"],"correctAnswer":"Secrets: database passwords, API keys, JWT secret, OAuth client secrets — use environment variables or secret management systems instead","explanation":"Secrets in git are compromised forever — even if deleted, they exist in history. Use: environment variables (docker/Railway env vars), HashiCorp Vault, AWS Secrets Manager, Kubernetes Secrets, or .env files (in .gitignore). Reference in properties: password: ${DB_PASSWORD}."}
],
"writtenConceptQuestions": [
  "Show a three-profile configuration: application.yml (shared), application-dev.yml (H2, create-drop), application-prod.yml (PostgreSQL env vars, validate).",
  "Explain @ConfigurationProperties with validation. Show a PaymentConfig class with @NotBlank, @Min, and a List<String> field.",
  "What is Spring Boot's relaxed binding? Show how APP_PAYMENT_API_KEY maps to app.payment.api-key in a @ConfigurationProperties class.",
  "List the configuration precedence order from lowest to highest. Show a case where an environment variable overrides application.yml.",
  "Why should secrets never be in application.yml? Show the correct pattern using environment variable references.",
  "What does @TestPropertySource do in a @SpringBootTest? Show a test that overrides payment sandbox mode.",
  "What are the 5 values for spring.jpa.hibernate.ddl-auto? When should each be used (dev/test/prod)?"
],
"businessScenarios": [
  "A developer commits application-prod.yml containing the production database password to GitHub. How did this happen (explain the mistake) and how do you prevent it going forward using environment variables and .gitignore?",
  "A Spring Boot app runs on Railway (free tier). It needs different DB URLs for staging and production. Design a profile-based configuration where Railway injects DATABASE_URL env var and profiles control which URL is used.",
  "A new service has 15 @Value annotations for payment config across 4 different classes. Consolidate into a single @ConfigurationProperties PaymentConfig class with @Validated constraints."
]
},

"day-051": {
"notes": """# Spring Data JPA: Entity Design, Repositories, and JPQL Queries

## JPA Entity Fundamentals
```java
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)   // UUID primary key (recommended for distributed systems)
    private String id;

    @Column(name = "customer_id", nullable = false, length = 36)
    private String customerId;

    @Column(name = "total_amount", precision = 10, scale = 2)
    private BigDecimal totalAmount;

    @Enumerated(EnumType.STRING)   // store as "PENDING" not ordinal 0 (fragile)
    @Column(nullable = false, length = 20)
    private OrderStatus status = OrderStatus.PENDING;

    @Column(name = "created_at", updatable = false)
    private Instant createdAt;

    @Column(name = "updated_at")
    private Instant updatedAt;

    @PrePersist
    void prePersist() { this.createdAt = this.updatedAt = Instant.now(); }

    @PreUpdate
    void preUpdate() { this.updatedAt = Instant.now(); }
}
```

## @GeneratedValue Strategies
```java
// IDENTITY — DB auto-increment (MySQL, PostgreSQL SERIAL) — no sequence, immediate INSERT
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;

// SEQUENCE — DB sequence (recommended for PostgreSQL with batch inserts)
@GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "order_seq")
@SequenceGenerator(name = "order_seq", sequenceName = "order_seq", allocationSize = 50)
private Long id;  // allocationSize=50 batches 50 IDs per DB call (performance)

// UUID — database-independent, no sequence needed
@GeneratedValue(strategy = GenerationType.UUID)
private String id;
```

## Spring Data JPA Repository
```java
// JpaRepository<Entity, ID> provides: save, findById, findAll, delete, count, existsById
public interface OrderRepository extends JpaRepository<Order, String> {

    // Derived query methods — Spring generates SQL from method name
    List<Order> findByCustomerId(String customerId);
    List<Order> findByStatus(OrderStatus status);
    Optional<Order> findByIdAndCustomerId(String id, String customerId);
    boolean existsByCustomerIdAndStatus(String customerId, OrderStatus status);
    long countByStatus(OrderStatus status);

    // Sorting and pagination
    Page<Order> findByStatus(OrderStatus status, Pageable pageable);
    List<Order> findByStatusOrderByCreatedAtDesc(OrderStatus status);

    // Date range
    List<Order> findByCreatedAtBetween(Instant from, Instant to);
    List<Order> findByTotalAmountGreaterThanEqual(BigDecimal minAmount);

    // Custom JPQL
    @Query("SELECT o FROM Order o WHERE o.customerId = :customerId AND o.status != 'CANCELLED' ORDER BY o.createdAt DESC")
    List<Order> findActiveOrdersByCustomer(@Param("customerId") String customerId);

    // JPQL with DTO projection
    @Query("SELECT new com.example.dto.OrderSummaryDto(o.id, o.totalAmount, o.status) FROM Order o WHERE o.customerId = :customerId")
    List<OrderSummaryDto> findOrderSummaries(@Param("customerId") String customerId);

    // Native SQL (last resort — breaks portability)
    @Query(value = "SELECT * FROM orders WHERE EXTRACT(MONTH FROM created_at) = :month", nativeQuery = true)
    List<Order> findByMonth(@Param("month") int month);

    // Modifying queries
    @Modifying
    @Transactional
    @Query("UPDATE Order o SET o.status = :status WHERE o.id = :id")
    int updateStatus(@Param("id") String id, @Param("status") OrderStatus status);
}
```

## Pagination and Sorting
```java
// Service layer — pagination
public Page<OrderDto> findAll(int page, int size, String sortBy) {
    Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, sortBy));
    return orderRepo.findAll(pageable).map(mapper::toDto);
}

// Controller
@GetMapping
public Page<OrderDto> list(
        @RequestParam(defaultValue="0") int page,
        @RequestParam(defaultValue="20") int size,
        @RequestParam(defaultValue="createdAt") String sort) {
    return orderService.findAll(page, size, sort);
}
// Response: { content: [...], totalElements: 1200, totalPages: 60, number: 0, size: 20 }
```

## @Embedded and @Embeddable — Value Objects
```java
@Embeddable
public class Address {
    private String street;
    private String city;
    private String postalCode;
    private String country;
}

@Entity
public class Customer {
    @Id private String id;
    private String name;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "street", column = @Column(name = "billing_street")),
        @AttributeOverride(name = "city",   column = @Column(name = "billing_city"))
    })
    private Address billingAddress;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "street", column = @Column(name = "shipping_street")),
        @AttributeOverride(name = "city",   column = @Column(name = "shipping_city"))
    })
    private Address shippingAddress;
}
```

## Common Mistakes
1. **@Enumerated without STRING:** default is ORDINAL (0,1,2). If you reorder the enum, all stored values become wrong. Always use EnumType.STRING.
2. **Missing @Column(updatable=false) on createdAt:** Hibernate updates createdAt on every flush without this.
3. **Using IDENTITY strategy with batch inserts:** IDENTITY requires a DB round-trip per insert (to get the generated ID). SEQUENCE with allocationSize=50 batches 50 inserts efficiently.
4. **findAll() without pagination:** loading all rows from a large table crashes the server with OOM.
""",
"mcqs": [
  {"id":"d51q1","prompt":"Why use @Enumerated(EnumType.STRING) instead of the default EnumType.ORDINAL?","options":["STRING is faster","ORDINAL stores as 0,1,2 — reordering enum values silently corrupts all stored data; STRING stores 'PENDING','ACTIVE' — renaming is explicit and safe","STRING stores less data","ORDINAL is deprecated"],"correctAnswer":"ORDINAL stores as 0,1,2 — reordering enum values silently corrupts all stored data; STRING stores 'PENDING','ACTIVE' — renaming is explicit and safe","explanation":"ORDINAL: Status.PENDING=0, ACTIVE=1. Add CANCELLED before ACTIVE → ACTIVE becomes 1 (was ACTIVE), CANCELLED becomes 1. All rows with value 1 now mean CANCELLED. This silent corruption is extremely dangerous. Always use STRING."},
  {"id":"d51q2","prompt":"What does `@Column(name = 'created_at', updatable = false)` do?","options":["Prevents the column from being created","Excludes the column from UPDATE SQL statements — Hibernate won't modify it after initial insert","Makes the column read-only from the DB","Prevents null values"],"correctAnswer":"Excludes the column from UPDATE SQL statements — Hibernate won't modify it after initial insert","explanation":"updatable=false: Hibernate omits this column from generated UPDATE statements. Without it, calling save() on an existing entity would update createdAt. Combined with @PrePersist setting the value once, updatable=false ensures it's set on INSERT and never changed."},
  {"id":"d51q3","prompt":"What is the difference between findById(id) and getReferenceById(id)?","options":["getReferenceById is deprecated","findById(id) executes an immediate SELECT and returns Optional<T>; getReferenceById(id) returns a Hibernate proxy with no SQL — SELECT runs only when a non-id field is accessed","They are identical","getReferenceById always returns null"],"correctAnswer":"findById(id) executes an immediate SELECT and returns Optional<T>; getReferenceById(id) returns a Hibernate proxy with no SQL — SELECT runs only when a non-id field is accessed","explanation":"getReferenceById: lazy proxy. Use when you only need the reference for a foreign key association: order.setCustomer(customerRepo.getReferenceById(customerId)) — no SELECT needed, just sets the FK. findById: use when you need the actual entity data."},
  {"id":"d51q4","prompt":"What does a Spring Data derived query `findByStatusAndCreatedAtBetween(status, from, to)` generate?","options":["A custom error","SELECT * FROM entity WHERE status = ? AND created_at BETWEEN ? AND ?","findBy only supports one condition","Spring Data doesn't support date range queries"],"correctAnswer":"SELECT * FROM entity WHERE status = ? AND created_at BETWEEN ? AND ?","explanation":"Spring Data parses the method name: findBy + Status + And + CreatedAt + Between → WHERE status = ? AND created_at BETWEEN ? AND ?. Keywords: And, Or, Between, GreaterThan, LessThan, Like, In, IsNull, OrderBy, Containing, StartingWith, etc."},
  {"id":"d51q5","prompt":"What does `@GeneratedValue(strategy = GenerationType.SEQUENCE, ...)` with `allocationSize = 50` optimize?","options":["Uses 50 threads for insertion","Reserves 50 IDs from the sequence per DB call — Hibernate allocates IDs in memory without a DB round-trip per insert, enabling batch inserts","Creates 50 sequences","allocationSize reduces the table size"],"correctAnswer":"Reserves 50 IDs from the sequence per DB call — Hibernate allocates IDs in memory without a DB round-trip per insert, enabling batch inserts","explanation":"IDENTITY: one DB call per INSERT to get the auto-generated ID. SEQUENCE with allocationSize=50: one DB call reserves 50 IDs (1-50), next 50 inserts use cached values (1,2,3...). On DB restart: next 50 from the sequence. Dramatically improves bulk insert performance."},
  {"id":"d51q6","prompt":"What does Page<OrderDto> findAll(Pageable pageable) return?","options":["Only the current page of data","Page object containing: current page items (content), totalElements, totalPages, pageNumber, pageSize — all pagination metadata in one query","A list of all orders","Pageable configuration only"],"correctAnswer":"Page object containing: current page items (content), totalElements, totalPages, pageNumber, pageSize — all pagination metadata in one query","explanation":"Spring Data's Page<T> executes two queries: SELECT ... LIMIT size OFFSET page*size for data and SELECT COUNT(*) for totalElements. The response includes content, page metadata (number, size, totalPages, totalElements, first, last). Client can build pagination UI without a separate count call."},
  {"id":"d51q7","prompt":"What is @Embeddable used for?","options":["Marking a class for inheritance","Defines a value object that maps to columns in the parent entity's table — no separate table, multiple instances use @AttributeOverrides to disambiguate column names","Creates a secondary table","Makes the class serializable"],"correctAnswer":"Defines a value object that maps to columns in the parent entity's table — no separate table, multiple instances use @AttributeOverrides to disambiguate column names","explanation":"@Embeddable Address maps its fields to the Customer table's columns. @AttributeOverrides allows two Address instances (billing, shipping) with different column names (billing_street vs shipping_street). The Address object doesn't have its own table or ID."},
  {"id":"d51q8","prompt":"What does @Modifying on a @Query method require and why?","options":["@Modifying needs @Async","@Modifying signals Hibernate to execute an UPDATE/DELETE instead of a SELECT. Combined with @Transactional — without a transaction, modifying queries fail","@Transactional is not needed","@Modifying only works with native queries"],"correctAnswer":"@Modifying signals Hibernate to execute an UPDATE/DELETE instead of a SELECT. Combined with @Transactional — without a transaction, modifying queries fail","explanation":"Without @Modifying, Spring Data treats all @Query methods as SELECT queries. @Modifying tells Hibernate to run executeUpdate() instead of getResultList(). @Transactional ensures the update runs within a transaction (required for DML). Add @Modifying(clearAutomatically=true) to evict cached entities."},
  {"id":"d51q9","prompt":"Why is `orderRepo.findAll()` dangerous for production tables with millions of rows?","options":["findAll() throws an exception for large tables","It loads ALL rows into memory at once — OutOfMemoryError for tables with millions of rows. Always use pagination: findAll(Pageable) or findAll(Specification, Pageable)","findAll() only loads 1000 rows by default","Hibernate limits findAll to 10000 rows"],"correctAnswer":"It loads ALL rows into memory at once — OutOfMemoryError for tables with millions of rows. Always use pagination: findAll(Pageable) or findAll(Specification, Pageable)","explanation":"findAll() executes SELECT * FROM orders with no LIMIT. A table with 5 million rows loads 5 million entities into memory simultaneously → heap exhaustion. Use PageRequest.of(page, size) for paginated access. For full-table processing, use Stream<T> with scrolling."},
  {"id":"d51q10","prompt":"What does `@PrePersist` callback do in a JPA entity?","options":["Runs before the entity class is loaded","Runs before the entity is inserted for the first time — used to set createdAt, generate IDs, or validate state","Runs before every SELECT","Runs after insertion is complete"],"correctAnswer":"Runs before the entity is inserted for the first time — used to set createdAt, generate IDs, or validate state","explanation":"JPA lifecycle callbacks: @PrePersist (before INSERT), @PostPersist (after INSERT), @PreUpdate (before UPDATE), @PostUpdate, @PreRemove (before DELETE), @PostRemove, @PostLoad (after SELECT). @PrePersist is the right place for auto-setting createdAt = Instant.now()."}
],
"writtenConceptQuestions": [
  "Design a Product JPA entity with all relevant annotations: UUID ID, columns with constraints, @Enumerated, @PrePersist/@PreUpdate for timestamps.",
  "Show a ProductRepository with 6 derived query methods, 2 @Query JPQL methods (one with DTO projection), and one @Modifying update method.",
  "Explain the difference between GenerationType.IDENTITY and SEQUENCE. When should each be used? What is allocationSize optimization?",
  "Show a pagination-enabled service method and controller using Page<T> and Pageable. What does the JSON response look like?",
  "What is @Embeddable? Design a Customer entity with billingAddress and shippingAddress using the same Address @Embeddable with @AttributeOverrides.",
  "Why is @Enumerated(EnumType.STRING) critical? Show the silent data corruption bug with ORDINAL when an enum value is inserted.",
  "What is getReferenceById() vs findById()? Show a use case where the proxy is sufficient (setting a FK) vs when you need the real entity."
],
"businessScenarios": [
  "A findAll() call in a product catalog service crashes the server when the table reaches 500K rows. Fix with pagination: add Pageable to the service and repository, return Page<ProductDto>, and update the controller.",
  "An ORDER_STATUS column stores 0,1,2 integers. A developer adds REFUNDED between PENDING and COMPLETED. All existing COMPLETED orders (value=2) now show as REFUNDED. Migrate to STRING enum with a data migration script.",
  "A reporting query runs JPQL loading full Order entities to extract 3 fields for a CSV. Optimize using a DTO projection in @Query (SELECT new ...) to reduce data transfer from DB."
]
},

"day-052": {
"notes": """# Hibernate: Session Management, N+1 Problem, Caching, and Performance

## How Hibernate Works with Spring
Spring Data JPA uses Hibernate as the default JPA provider. Each request gets a Hibernate Session (created from SessionFactory). The Session is a first-level cache (identity map) — loading the same entity twice in one transaction returns the same instance.

```java
// First-level cache (Session-scoped, automatic)
Order o1 = orderRepo.findById("1").get(); // SELECT query executes
Order o2 = orderRepo.findById("1").get(); // NO query — returns same instance from cache
assert o1 == o2; // true — identical Java object
```

## Lazy vs Eager Loading
```java
@Entity
public class Order {
    @Id private String id;

    @OneToMany(mappedBy = "order", fetch = FetchType.LAZY)   // default for collections
    private List<OrderItem> items;                            // loaded on access

    @ManyToOne(fetch = FetchType.LAZY)   // recommended (even for @ManyToOne)
    @JoinColumn(name = "customer_id")
    private Customer customer;           // EAGER by default — change to LAZY!
}

// FetchType.EAGER (@ManyToOne default): loads related entity with a JOIN always
// FetchType.LAZY (collection default): loads related data only when accessed
```

## The N+1 Problem — Most Common JPA Performance Issue
```java
// N+1 PROBLEM — 1 query for orders + N queries for each order's items
List<Order> orders = orderRepo.findAll(); // SELECT * FROM orders (1 query)
for (Order order : orders) {
    order.getItems().size(); // SELECT * FROM order_items WHERE order_id=? (N queries!)
}
// 100 orders = 101 queries total

// FIX 1: @EntityGraph
@EntityGraph(attributePaths = {"items"})
List<Order> findAll(); // Single JOIN query: SELECT o.*, i.* FROM orders o LEFT JOIN order_items i...

// FIX 2: JPQL JOIN FETCH
@Query("SELECT DISTINCT o FROM Order o JOIN FETCH o.items WHERE o.status = :status")
List<Order> findWithItemsByStatus(@Param("status") OrderStatus status);

// FIX 3: @BatchSize — grouped lazy loading (N/batch_size + 1 queries)
@BatchSize(size = 20)
@OneToMany(mappedBy = "order")
private List<OrderItem> items; // loads items for 20 orders at a time

// Detect N+1 in dev:
// spring.jpa.properties.hibernate.generate_statistics=true
// logging.level.org.hibernate.SQL=DEBUG
// spring-boot-actuator's /actuator/metrics/hibernate.query.count
```

## Second-Level Cache — Across Sessions
```java
// First-level cache: per Session (automatic)
// Second-level cache: across Sessions, per EntityManagerFactory

// Enable in application.properties:
spring.jpa.properties.hibernate.cache.use_second_level_cache=true
spring.jpa.properties.hibernate.cache.region.factory_class=org.hibernate.cache.ehcache.EhCacheRegionFactory
spring.jpa.properties.javax.persistence.sharedCache.mode=ENABLE_SELECTIVE

// Mark entity as cacheable
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Category { ... }

// Query cache — caches query result sets
@Query("SELECT c FROM Category c")
@QueryHints(@QueryHint(name = "org.hibernate.cacheable", value = "true"))
List<Category> findAllCached();
```

## Dirty Checking — How Hibernate Detects Changes
Hibernate compares entity state to its snapshot at flush time. Any changed field triggers an UPDATE:
```java
@Transactional
public void updateOrderStatus(String id, OrderStatus newStatus) {
    Order order = orderRepo.findById(id).orElseThrow(); // loaded, snapshot taken
    order.setStatus(newStatus); // modify the entity
    // NO explicit save() needed — dirty checking updates at transaction commit
} // transaction commits → Hibernate detects change → UPDATE order SET status=? WHERE id=?
```

## Optimistic Locking — Concurrent Modification Prevention
```java
@Entity
public class Order {
    @Id private String id;

    @Version  // optimistic lock — Hibernate checks this on every UPDATE
    private int version;

    private OrderStatus status;
}

// Thread 1: reads order (version=1), Thread 2: reads order (version=1)
// Thread 1: updates order → version becomes 2
// Thread 2: tries to update order (version=1) → Hibernate throws OptimisticLockException
// because DB has version=2, not 1

// Handle in service:
try {
    orderService.updateStatus(id, newStatus);
} catch (OptimisticLockException e) {
    throw new ConflictException("Order was modified concurrently, please retry");
}
```

## @Transactional Propagation and Isolation
```java
// Propagation types (how a transaction behaves when calling another transactional method)
@Transactional(propagation = Propagation.REQUIRED)     // default: join existing or create new
@Transactional(propagation = Propagation.REQUIRES_NEW) // always create new transaction (suspend current)
@Transactional(propagation = Propagation.NOT_SUPPORTED)// run outside any transaction
@Transactional(propagation = Propagation.SUPPORTS)     // use transaction if available, else no transaction

// Read-only optimization
@Transactional(readOnly = true)  // tells Hibernate skip dirty checking → faster
public List<OrderDto> findAll() { ... }
```

## Common Mistakes
1. **Calling save() inside a @Transactional method:** unnecessary — dirty checking handles updates. save() is needed only for new entities.
2. **EAGER on @OneToMany:** loads the collection for every load of the parent, even when not needed.
3. **LazyInitializationException:** accessing lazy-loaded collections after the transaction closes. Fix: use @Transactional, JOIN FETCH, or projections.
4. **No @Version:** concurrent updates silently overwrite each other without optimistic locking.
""",
"mcqs": [
  {"id":"d52q1","prompt":"What is Hibernate's first-level cache?","options":["A Redis cache for entities","A per-Session identity map — loading the same entity twice in one transaction returns the same Java instance without a second SQL query","A cache of JPQL query results","A cache shared across all user sessions"],"correctAnswer":"A per-Session identity map — loading the same entity twice in one transaction returns the same Java instance without a second SQL query","explanation":"First-level cache is automatic, always active, Session-scoped. orderRepo.findById('1') twice → one SELECT, same object reference. This prevents duplicate state within a transaction and reduces DB round-trips. Cleared when the Session closes."},
  {"id":"d52q2","prompt":"What is the N+1 query problem?","options":["Running 1 query that returns N+1 rows","1 query to load N parent entities, then N separate queries to load each parent's children — total N+1 queries instead of 1 JOIN query","N+1 table joins in one query","A database index problem"],"correctAnswer":"1 query to load N parent entities, then N separate queries to load each parent's children — total N+1 queries instead of 1 JOIN query","explanation":"findAll() → 1 query: SELECT * FROM orders. Then for each order: order.getItems() triggers SELECT * FROM order_items WHERE order_id=?. 100 orders = 101 queries. Fix with JOIN FETCH or @EntityGraph to load in 1 query."},
  {"id":"d52q3","prompt":"What is the difference between @EntityGraph and JOIN FETCH?","options":["Identical","@EntityGraph is declarative (defined on method/entity), reusable across methods; JOIN FETCH is in JPQL and tightly coupled to the query string — both generate a JOIN to load related data eagerly","@EntityGraph is for @ManyToMany only","JOIN FETCH always creates a Cartesian product"],"correctAnswer":"@EntityGraph is declarative (defined on method/entity), reusable across methods; JOIN FETCH is in JPQL and tightly coupled to the query string — both generate a JOIN to load related data eagerly","explanation":"@EntityGraph on a repository method dynamically adds eager loading to that method. JOIN FETCH requires writing the JPQL explicitly. @EntityGraph is preferred for existing derived queries; JOIN FETCH for complex filtering queries."},
  {"id":"d52q4","prompt":"What is dirty checking in Hibernate?","options":["Finding corrupt entities","Hibernate takes a snapshot of entity state when loaded and compares it at flush time — changed fields trigger an UPDATE automatically without calling save()","Checking for dirty reads in transactions","Finding entities with null fields"],"correctAnswer":"Hibernate takes a snapshot of entity state when loaded and compares it at flush time — changed fields trigger an UPDATE automatically without calling save()","explanation":"Load entity → Hibernate stores a snapshot. Before transaction commits (flush), Hibernate compares current state to snapshot. Different fields → generates UPDATE SQL. This is why you don't need orderRepo.save(order) after order.setStatus(SHIPPED) inside a @Transactional method."},
  {"id":"d52q5","prompt":"What does `@Version` on an entity field do?","options":["Stores the entity version number for display","Enables optimistic locking — Hibernate includes version in UPDATE WHERE clause. If another transaction updated first, the version changed and Hibernate throws OptimisticLockException instead of silently overwriting","Creates a DB trigger","Tracks the audit version history"],"correctAnswer":"Enables optimistic locking — Hibernate includes version in UPDATE WHERE clause. If another transaction updated first, the version changed and Hibernate throws OptimisticLockException instead of silently overwriting","explanation":"@Version: UPDATE order SET status=?, version=2 WHERE id=? AND version=1. If another transaction changed version to 2 before this one, 0 rows are updated → OptimisticLockException. Prevents last-write-wins data corruption in concurrent updates."},
  {"id":"d52q6","prompt":"Why is `@Transactional(readOnly = true)` important for read operations?","options":["Prevents data modification in read methods","Tells Hibernate to skip dirty checking (no entity snapshots needed) and can enable performance optimizations in JDBC drivers — meaningfully faster for large result sets","Required for @Query methods","Makes SELECT queries run in parallel"],"correctAnswer":"Tells Hibernate to skip dirty checking (no entity snapshots needed) and can enable performance optimizations in JDBC drivers — meaningfully faster for large result sets","explanation":"readOnly=true: Hibernate skips creating entity snapshots (no dirty-check comparison at flush). Some JDBC drivers optimize connection handling for read-only transactions. Spring Data uses readOnly=true by default on repository select methods. Explicitly use it on service read methods."},
  {"id":"d52q7","prompt":"What is LazyInitializationException and when does it occur?","options":["A lazy bean initialization error","Accessing a lazy-loaded collection after the Hibernate Session (transaction) is closed — the proxy can no longer execute a SELECT to load the data","A NullPointerException for lazy fields","An exception thrown during lazy bean creation"],"correctAnswer":"Accessing a lazy-loaded collection after the Hibernate Session (transaction) is closed — the proxy can no longer execute a SELECT to load the data","explanation":"@OneToMany with LAZY: order.getItems() is a proxy. If you access it after the @Transactional method returns (Session closed), Hibernate can't execute the SELECT. Fix: load within transaction using JOIN FETCH, @EntityGraph, or DTO projection. Never access lazy collections outside @Transactional."},
  {"id":"d52q8","prompt":"What does `Propagation.REQUIRES_NEW` do when a @Transactional method calls another @Transactional method?","options":["Joins the existing transaction","Suspends the current transaction and starts a completely new one — changes in the inner transaction commit independently even if the outer transaction rolls back","Creates a savepoint","Requires a new database connection"],"correctAnswer":"Suspends the current transaction and starts a completely new one — changes in the inner transaction commit independently even if the outer transaction rolls back","explanation":"REQUIRES_NEW: inner transaction commits before outer finishes. Use case: audit logging — log the attempt even if the main transaction fails. Default REQUIRED: inner method joins outer transaction; inner rollback rolls back outer too."},
  {"id":"d52q9","prompt":"What is the second-level cache in Hibernate?","options":["The DB query plan cache","A shared cache across Sessions (requests) — entities cached after first load and reused across multiple Sessions without a DB query. Configured with providers like EhCache","The JVM method call cache","A cache within a single @Transactional method"],"correctAnswer":"A shared cache across Sessions (requests) — entities cached after first load and reused across multiple Sessions without a DB query. Configured with providers like EhCache","explanation":"First-level: per Session (transaction). Second-level: per SessionFactory (shared across all requests). Category lookup → first request queries DB, subsequent requests get from cache. Best for rarely-changing reference data (categories, config, currencies). Requires @Cache annotation on entity."},
  {"id":"d52q10","prompt":"A service loads an Order inside @Transactional, modifies a field, and never calls save(). Does the DB get updated?","options":["No — must call save()","Yes — Hibernate's dirty checking detects the modification at flush time (end of transaction) and generates UPDATE SQL automatically","Only if @Modifying is present","Only if flush() is called explicitly"],"correctAnswer":"Yes — Hibernate's dirty checking detects the modification at flush time (end of transaction) and generates UPDATE SQL automatically","explanation":"Inside @Transactional, Hibernate manages the entity. At flush (transaction commit), it compares current state to the snapshot taken at load time. If any field differs, Hibernate generates UPDATE SQL. Calling save() on a managed entity is redundant (harmless but unnecessary)."}
],
"writtenConceptQuestions": [
  "Explain the N+1 problem with a concrete example. Show all three fixes: JOIN FETCH, @EntityGraph, and @BatchSize, and when to use each.",
  "What is dirty checking? Show a @Transactional method that updates an entity field without calling save() and explain exactly when the UPDATE SQL is generated.",
  "Explain optimistic locking (@Version). Show the concurrent update scenario, the OptimisticLockException, and how to handle it with a 409 Conflict response.",
  "What is LazyInitializationException? Show the exact code that triggers it and three ways to fix it.",
  "Describe the first-level and second-level caches. What are the scope and lifetime of each? When does the second-level cache help?",
  "What is @Transactional(readOnly = true)? Why should all read operations use it? Show the performance impact.",
  "Explain Propagation.REQUIRED vs REQUIRES_NEW. Show an audit log example where REQUIRES_NEW is necessary."
],
"businessScenarios": [
  "A product listing API takes 2 seconds to load 100 products. Enabling SQL logging reveals 101 queries (1 for products + 100 for each product's category). Fix with @EntityGraph or JOIN FETCH and show the before/after query count.",
  "Two customer service agents try to update the same order simultaneously. The last update silently overwrites the first. Add @Version for optimistic locking and return 409 Conflict to the second agent with a 'Please refresh and retry' message.",
  "A reporting service calls findAll() on a 2M row table, causing an OOM crash. Redesign to process in pages of 1000 using JPA Scrollable Results or paginated findAll(), processing each page without holding all in memory."
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
