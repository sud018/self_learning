"""Rewrite days 57-60: Testing, MockMvc, Kafka, Microservices."""
import json, os
DATA_DIR = "backend/data/curriculum"

CURRICULUM = {

"day-057": {
"notes": """# Testing in Spring Boot: Unit Tests, @DataJpaTest, @SpringBootTest, and Test Slices

## Test Pyramid — What to Test and How
```
        /\\
       /E2E\\        (few — slow, expensive, brittle)
      /------\\
     /Integration\\  (some — @SpringBootTest, @DataJpaTest)
    /------------\\
   /  Unit Tests  \\ (many — fast, isolated, Mockito)
  /----------------\\
```

## Unit Tests with Mockito
```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock private OrderRepository orderRepo;
    @Mock private InventoryService inventoryService;
    @Mock private OrderMapper mapper;
    @InjectMocks private OrderService orderService;

    @Test
    void createOrder_savesOrderAndReturnsDto() {
        // Arrange
        CreateOrderRequest req = new CreateOrderRequest("cust-1",
            List.of(new CreateOrderItemRequest("prod-1", 2)));
        Order order = new Order("cust-1");
        OrderDto dto = new OrderDto("order-1", "PENDING", BigDecimal.TEN);

        when(orderRepo.save(any(Order.class))).thenReturn(order);
        when(mapper.toDto(order)).thenReturn(dto);

        // Act
        OrderDto result = orderService.create(req);

        // Assert
        assertThat(result).isEqualTo(dto);
        verify(orderRepo).save(any(Order.class));
        verify(inventoryService).deductStock(req.items());
    }

    @Test
    void createOrder_whenInventoryFails_rollsBackAndThrows() {
        doThrow(new InsufficientStockException("prod-1"))
            .when(inventoryService).deductStock(any());

        assertThatThrownBy(() -> orderService.create(new CreateOrderRequest("c1", List.of())))
            .isInstanceOf(InsufficientStockException.class);
        verify(orderRepo, never()).save(any()); // should not save if inventory fails
    }
}
```

## @DataJpaTest — Repository Layer Testing
```java
@DataJpaTest  // loads only JPA/DB layer, uses H2 in-memory DB by default
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
// ^ remove to use actual DB (Testcontainers) instead of H2
class OrderRepositoryTest {

    @Autowired private OrderRepository orderRepo;
    @Autowired private TestEntityManager em;

    @Test
    void findByCustomerId_returnsOnlyCustomersOrders() {
        // Arrange — persist test data
        Order order1 = em.persistAndFlush(new Order("cust-1"));
        Order order2 = em.persistAndFlush(new Order("cust-2"));

        // Act
        List<Order> results = orderRepo.findByCustomerId("cust-1");

        // Assert
        assertThat(results).hasSize(1)
            .extracting(Order::getCustomerId)
            .containsOnly("cust-1");
    }

    @Test
    void countByStatus_returnsCorrectCount() {
        em.persistAndFlush(new Order("c1", OrderStatus.PENDING));
        em.persistAndFlush(new Order("c2", OrderStatus.PENDING));
        em.persistAndFlush(new Order("c3", OrderStatus.COMPLETED));

        assertThat(orderRepo.countByStatus(OrderStatus.PENDING)).isEqualTo(2);
    }
}
```

## @SpringBootTest — Full Integration Test
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
class OrderIntegrationTest {

    @Autowired private TestRestTemplate restTemplate;
    @Autowired private OrderRepository orderRepo;

    @Test
    void createOrder_endToEnd() {
        CreateOrderRequest req = new CreateOrderRequest("cust-1",
            List.of(new CreateOrderItemRequest("prod-1", 1)));

        ResponseEntity<OrderDto> response = restTemplate.postForEntity(
            "/api/orders", req, OrderDto.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody().status()).isEqualTo("PENDING");
        assertThat(orderRepo.count()).isEqualTo(1);
    }
}
```

## Testcontainers — Real DB in Tests
```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = Replace.NONE)  // don't replace with H2
@Testcontainers
class ProductRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired private ProductRepository productRepo;

    @Test
    void save_persistsWithUUID() {
        Product p = productRepo.save(new Product("Laptop", new BigDecimal("999.99")));
        assertThat(p.getId()).isNotNull().hasSize(36); // UUID format
    }
}
```

## AssertJ — Fluent Assertions
```java
// AssertJ is much more readable than JUnit 5 assertions
assertThat(result).isNotNull();
assertThat(result.getId()).isEqualTo("order-1");
assertThat(result.getItems()).hasSize(3).extracting(OrderItem::getProductId)
    .containsExactlyInAnyOrder("prod-1", "prod-2", "prod-3");
assertThat(result.getTotal()).isGreaterThan(BigDecimal.ZERO);
assertThatThrownBy(() -> service.findById("non-existent"))
    .isInstanceOf(NotFoundException.class)
    .hasMessageContaining("non-existent");
```

## Common Mistakes
1. **@SpringBootTest for every test:** slow (loads full context). Use @DataJpaTest or unit tests for isolated tests.
2. **Using H2 for production DB tests:** H2 has different SQL dialect — use Testcontainers for real DB behaviour.
3. **Not resetting state between tests:** @DirtiesContext reloads context (very slow). Use @Transactional on test class (rolls back after each test) or @BeforeEach cleanup.
""",
"mcqs": [
  {"id":"d57q1","prompt":"What does `@DataJpaTest` load compared to `@SpringBootTest`?","options":["They are identical","@DataJpaTest loads only JPA components (entities, repositories, Hibernate) — much faster. @SpringBootTest loads the full application context including controllers, services, security","@DataJpaTest skips Hibernate","@SpringBootTest is always required"],"correctAnswer":"@DataJpaTest loads only JPA components (entities, repositories, Hibernate) — much faster. @SpringBootTest loads the full application context including controllers, services, security","explanation":"Test slices: @DataJpaTest (JPA only), @WebMvcTest (MVC layer only), @JsonTest (JSON serialization only). Each loads a fraction of the context — much faster than @SpringBootTest. Use the right slice for what you're testing."},
  {"id":"d57q2","prompt":"What does `@InjectMocks` do in a Mockito test?","options":["Injects the real Spring context","Creates an instance of the annotated class and injects all @Mock fields as constructor arguments (or setter/field injection) — the class under test is real, dependencies are mocked","Marks the class as injectable","@InjectMocks creates a spy on the class"],"correctAnswer":"Creates an instance of the annotated class and injects all @Mock fields as constructor arguments (or setter/field injection) — the class under test is real, dependencies are mocked","explanation":"@Mock creates mock implementations. @InjectMocks creates the real OrderService and injects the @Mock fields. The service code runs normally; only its dependencies are mocked. No Spring context needed — fast unit test."},
  {"id":"d57q3","prompt":"What is the purpose of `TestEntityManager` in @DataJpaTest?","options":["A mock for EntityManager","A test-specific wrapper around EntityManager that provides helpers like persistAndFlush() — inserts test data directly bypassing the repository layer","Replaces the repository in tests","TestEntityManager creates in-memory tables"],"correctAnswer":"A test-specific wrapper around EntityManager that provides helpers like persistAndFlush() — inserts test data directly bypassing the repository layer","explanation":"em.persistAndFlush(entity): persists and immediately flushes to the in-memory DB. Bypasses the repository (so you're testing the repository in isolation, not the data setup). em.find(Entity.class, id) retrieves directly for verification."},
  {"id":"d57q4","prompt":"Why use Testcontainers instead of H2 for JPA tests?","options":["H2 is slower","H2 has a different SQL dialect — queries using PostgreSQL-specific syntax (JSONB, pg_trgm, ILIKE) fail on H2. Testcontainers runs a real PostgreSQL Docker container for authentic testing","Testcontainers is easier to set up","H2 doesn't support JPA"],"correctAnswer":"H2 has a different SQL dialect — queries using PostgreSQL-specific syntax (JSONB, pg_trgm, ILIKE) fail on H2. Testcontainers runs a real PostgreSQL Docker container for authentic testing","explanation":"H2 compatibility mode helps but isn't perfect. Native SQL queries, DB functions, and constraint behavior can differ. Testcontainers spins a real PostgreSQL container for tests — same DB as production. @DynamicPropertySource wires the container's URL into Spring properties."},
  {"id":"d57q5","prompt":"What does `verify(orderRepo, never()).save(any())` assert?","options":["orderRepo.save() was called once","orderRepo.save() was NEVER called during the test — used to verify that a side effect did NOT happen when it shouldn't","save() returned null","orderRepo is null"],"correctAnswer":"orderRepo.save() was NEVER called during the test — used to verify that a side effect did NOT happen when it shouldn't","explanation":"verify(mock, never()): asserts zero interactions. verify(mock, times(2)): exactly twice. verify(mock): exactly once (default). In the exception test: verify that save() wasn't called because the service should abort before saving when inventory fails."},
  {"id":"d57q6","prompt":"What does `@SpringBootTest(webEnvironment = RANDOM_PORT)` do differently from the default?","options":["Uses port 8080","Starts a real embedded web server on a random port — allows full HTTP integration tests with TestRestTemplate. Default MOCK doesn't start a real server","Uses a mock server","Requires no port configuration"],"correctAnswer":"Starts a real embedded web server on a random port — allows full HTTP integration tests with TestRestTemplate. Default MOCK doesn't start a real server","explanation":"RANDOM_PORT: real Tomcat starts, HTTP requests go through the full stack. MOCK: MockMvc-based (no real server). DEFINED_PORT: uses server.port. NONE: no web context. For end-to-end HTTP tests, use RANDOM_PORT with TestRestTemplate."},
  {"id":"d57q7","prompt":"What does `assertThatThrownBy(() -> service.findById('x')).isInstanceOf(NotFoundException.class)` verify?","options":["The method returns null","The lambda throws an exception, and that exception is of type NotFoundException — AssertJ fluent exception assertion","The method completes without exception","NotFoundException is a Spring class"],"correctAnswer":"The lambda throws an exception, and that exception is of type NotFoundException — AssertJ fluent exception assertion","explanation":"assertThatThrownBy captures the exception thrown by the lambda. .isInstanceOf(NotFoundException.class) checks the type. Chain: .hasMessageContaining('x') checks the message. Much more readable than try-catch with assertThat in tests."},
  {"id":"d57q8","prompt":"Why is adding `@Transactional` to a test class useful?","options":["Makes tests faster","Wraps each test in a transaction that is rolled back after the test — database is clean for the next test without manual cleanup","@Transactional is required for JPA tests","Tests run in parallel with @Transactional"],"correctAnswer":"Wraps each test in a transaction that is rolled back after the test — database is clean for the next test without manual cleanup","explanation":"Without @Transactional on the test: data inserted by test1 remains for test2, causing ordering dependencies and flaky tests. With @Transactional: Spring rolls back the transaction after each @Test method — clean state every time. Works for @DataJpaTest and @SpringBootTest with MOCK environment."},
  {"id":"d57q9","prompt":"What is the test pyramid principle for Spring Boot applications?","options":["Write equal numbers of unit, integration, and E2E tests","Many fast unit tests (Mockito), some integration tests (@DataJpaTest/@WebMvcTest), few full E2E tests (@SpringBootTest RANDOM_PORT) — faster feedback, cheaper to run","Only write @SpringBootTest tests","Write only integration tests"],"correctAnswer":"Many fast unit tests (Mockito), some integration tests (@DataJpaTest/@WebMvcTest), few full E2E tests (@SpringBootTest RANDOM_PORT) — faster feedback, cheaper to run","explanation":"Unit tests: milliseconds each, 100s of them. @DataJpaTest: seconds each, test each repository. @WebMvcTest: seconds each, test each controller. @SpringBootTest: 10-30 seconds, run for critical user journeys only. The pyramid keeps total test time manageable."},
  {"id":"d57q10","prompt":"What does `@DynamicPropertySource` do in Testcontainers tests?","options":["Sets test data dynamically","Wires Testcontainer's runtime properties (JDBC URL, username, password) into Spring's property system — Spring uses the container's connection instead of configured values","Creates dynamic test data","Registers test-specific beans"],"correctAnswer":"Wires Testcontainer's runtime properties (JDBC URL, username, password) into Spring's property system — Spring uses the container's connection instead of configured values","explanation":"The container starts on a random port. @DynamicPropertySource: registry.add('spring.datasource.url', postgres::getJdbcUrl) tells Spring to use the container's URL at runtime. This overrides application.properties datasource settings for the test."}
],
"writtenConceptQuestions": [
  "Show a complete Mockito unit test for OrderService.create(): arrange mocks, act, assert result, verify interactions, and test the exception path.",
  "Write a @DataJpaTest for OrderRepository: setup test data with TestEntityManager, test findByCustomerId, countByStatus, and a custom @Query method.",
  "Show a Testcontainers test with PostgreSQLContainer, @DynamicPropertySource, and @AutoConfigureTestDatabase(replace=NONE). When is this needed over H2?",
  "What is the test pyramid? Show the distribution of test types for a Spring Boot application with 50 unit tests, 10 @DataJpaTest, and 3 @SpringBootTest.",
  "Show assertThatThrownBy for testing exceptions, and extracting() with containsExactlyInAnyOrder for testing collections.",
  "What is @ActiveProfiles('test') used for in integration tests? Show a test application-test.yml that uses H2 instead of PostgreSQL.",
  "Why is @Transactional on test classes useful? Show the database isolation it provides between tests."
],
"businessScenarios": [
  "A CI pipeline takes 15 minutes because all tests use @SpringBootTest. Profile the test suite and migrate repository tests to @DataJpaTest (5s each) and service tests to Mockito unit tests (10ms each).",
  "Tests pass on H2 but fail in production with PostgreSQL — a native query uses ILIKE which H2 doesn't support. Migrate to Testcontainers with a real PostgreSQL container.",
  "Test data bleeds between tests — test B fails because test A left a record in the DB. Add @Transactional to the test class or add @BeforeEach cleanup to show both solutions."
]
},

"day-058": {
"notes": """# MockMvc: Testing Spring MVC Controllers Without a Running Server

## What is MockMvc?
MockMvc allows you to test Spring MVC controllers by dispatching requests through the DispatcherServlet without starting a real HTTP server. It tests the full MVC stack: routing, filters, argument resolution, validation, and serialization.

## @WebMvcTest — Controller Slice
```java
@WebMvcTest(OrderController.class)    // loads only MVC layer for OrderController
class OrderControllerTest {

    @Autowired private MockMvc mockMvc;
    @Autowired private ObjectMapper objectMapper;

    @MockBean private OrderService orderService;   // mock the service dependency
    @MockBean private JwtService jwtService;        // mock security dependencies
    @MockBean private UserDetailsService userDetailsService;

    @Test
    @WithMockUser(roles = "USER")  // simulate authenticated user
    void getOrder_whenExists_returns200WithDto() throws Exception {
        OrderDto dto = new OrderDto("order-1", "PENDING", new BigDecimal("99.99"));
        when(orderService.findById("order-1")).thenReturn(dto);

        mockMvc.perform(get("/api/orders/order-1")
                .header("Authorization", "Bearer fake-token")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value("order-1"))
            .andExpect(jsonPath("$.status").value("PENDING"))
            .andExpect(jsonPath("$.total").value(99.99));
    }
}
```

## Testing POST with Request Body
```java
@Test
@WithMockUser(roles = "USER")
void createOrder_withValidBody_returns201() throws Exception {
    CreateOrderRequest req = new CreateOrderRequest("cust-1",
        List.of(new CreateOrderItemRequest("prod-1", 2)));
    OrderDto created = new OrderDto("new-order", "PENDING", new BigDecimal("39.98"));

    when(orderService.create(any())).thenReturn(created);

    mockMvc.perform(post("/api/orders")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(req)))   // serialize req to JSON
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.id").value("new-order"))
        .andExpect(header().string("Location", containsString("/api/orders/new-order")));
}

@Test
@WithMockUser
void createOrder_withBlankCustomerId_returns400WithFieldError() throws Exception {
    CreateOrderRequest invalidReq = new CreateOrderRequest("", List.of());

    mockMvc.perform(post("/api/orders")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(invalidReq)))
        .andExpect(status().isBadRequest())
        .andExpect(jsonPath("$.fieldErrors.customerId").exists())
        .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));
}
```

## Testing Error Responses
```java
@Test
@WithMockUser
void getOrder_whenNotFound_returns404() throws Exception {
    when(orderService.findById("bad-id"))
        .thenThrow(new NotFoundException("Order", "bad-id"));

    mockMvc.perform(get("/api/orders/bad-id"))
        .andExpect(status().isNotFound())
        .andExpect(jsonPath("$.code").value("NOT_FOUND"))
        .andExpect(jsonPath("$.message").value(containsString("bad-id")));
}
```

## MockMvc — Common Methods
```java
// Request builders
mockMvc.perform(get("/api/orders"))
mockMvc.perform(post("/api/orders").content(json).contentType(APPLICATION_JSON))
mockMvc.perform(put("/api/orders/{id}", "order-1").content(json).contentType(APPLICATION_JSON))
mockMvc.perform(delete("/api/orders/{id}", "order-1"))
mockMvc.perform(patch("/api/orders/{id}/status", "order-1"))

// Request configuration
.header("Authorization", "Bearer " + token)
.param("page", "0").param("size", "10")    // query parameters
.accept(MediaType.APPLICATION_JSON)

// Response assertions
.andExpect(status().isOk())
.andExpect(status().isCreated())
.andExpect(status().isNotFound())
.andExpect(status().isBadRequest())
.andExpect(content().contentType(MediaType.APPLICATION_JSON))
.andExpect(jsonPath("$.id").value("order-1"))
.andExpect(jsonPath("$.items").isArray())
.andExpect(jsonPath("$.items.length()").value(3))
.andExpect(jsonPath("$.items[0].productId").value("prod-1"))
.andExpect(header().exists("Location"))
.andDo(print()) // prints request and response to console (debug)
```

## Testing Security — @WithMockUser and @WithUserDetails
```java
// @WithMockUser — simple mock, no UserDetailsService needed
@Test
@WithMockUser(username = "admin@example.com", roles = {"ADMIN"})
void adminEndpoint_withAdminRole_returns200() throws Exception { ... }

// @WithMockUser without roles — default role is USER
@Test
@WithMockUser
void userEndpoint_withUserRole_returns200() throws Exception { ... }

// Test unauthenticated access
@Test
void protectedEndpoint_withoutToken_returns401() throws Exception {
    mockMvc.perform(get("/api/orders"))
        .andExpect(status().isUnauthorized());
}

// Test forbidden access (authenticated but wrong role)
@Test
@WithMockUser(roles = "USER")
void adminEndpoint_withUserRole_returns403() throws Exception {
    mockMvc.perform(delete("/api/admin/users/1"))
        .andExpect(status().isForbidden());
}
```

## Standalone MockMvc — Without Spring Context
```java
// Faster: no Spring context, just the controller
@BeforeEach
void setUp() {
    mockMvc = MockMvcBuilders.standaloneSetup(new OrderController(orderService))
        .setControllerAdvice(new GlobalExceptionHandler())
        .build();
}
// Use when you don't need security or Spring boot context
```

## Common Mistakes
1. **Forgetting `@MockBean` for service dependencies:** @WebMvcTest does not create @Service beans — must mock them with @MockBean.
2. **Missing `contentType(APPLICATION_JSON)` on POST:** Spring returns 415 Unsupported Media Type without it.
3. **`andExpect(jsonPath('$.field').value(99.99))` with BigDecimal:** Jackson may serialize as 99.99 or 99.990000 — use `isNumber()` or compare as string.
""",
"mcqs": [
  {"id":"d58q1","prompt":"What is the main advantage of @WebMvcTest over @SpringBootTest for controller tests?","options":["@WebMvcTest supports more HTTP methods","@WebMvcTest loads only the MVC layer (controller, filters, DispatcherServlet) — much faster since it skips JPA, services, security config beans not related to the controller under test","@SpringBootTest doesn't support MockMvc","@WebMvcTest tests run in parallel"],"correctAnswer":"@WebMvcTest loads only the MVC layer (controller, filters, DispatcherServlet) — much faster since it skips JPA, services, security config beans not related to the controller under test","explanation":"@SpringBootTest: full context load (10-30s). @WebMvcTest: only MVC beans for the specified controller (1-3s). @WebMvcTest doesn't create @Service or @Repository beans — use @MockBean for those. Much faster feedback for controller-specific tests."},
  {"id":"d58q2","prompt":"What does `@MockBean` do in a @WebMvcTest test?","options":["Creates a real Spring bean","Creates a Mockito mock AND registers it in the Spring application context — replaces any existing bean of that type in the context","@MockBean is identical to @Mock","Creates a test database"],"correctAnswer":"Creates a Mockito mock AND registers it in the Spring application context — replaces any existing bean of that type in the context","explanation":"@Mock (Mockito): creates a mock, not in Spring context (for @InjectMocks unit tests). @MockBean (Spring): creates a mock AND registers it as the Spring bean. In @WebMvcTest, the controller is autowired by Spring — dependencies must be in the context, so @MockBean is required."},
  {"id":"d58q3","prompt":"What does `jsonPath('$.items[0].productId').value('prod-1')` verify?","options":["The items array has one element","The first element of the 'items' JSON array has a field 'productId' equal to 'prod-1'","items is not empty","productId is at index 1"],"correctAnswer":"The first element of the 'items' JSON array has a field 'productId' equal to 'prod-1'","explanation":"JsonPath: $ is root. $.items is the items array. $.items[0] is first element. $.items[0].productId is the productId field of the first item. .value('prod-1') asserts it equals that string. Use jsonPath('$.items.length()').value(3) to check array size."},
  {"id":"d58q4","prompt":"What does `.andDo(print())` do in a MockMvc chain?","options":["Prints the test result to the screen","Prints the complete HTTP request and response (headers, status, body) to the console — essential for debugging failing tests","Required for JSON assertions","Prints only if the test fails"],"correctAnswer":"Prints the complete HTTP request and response (headers, status, body) to the console — essential for debugging failing tests","explanation":"print() outputs: MockHttpServletRequest (method, URL, headers, body), Handler (controller method), MockHttpServletResponse (status, headers, body). Add .andDo(print()) when a test fails mysteriously — see the actual response to understand what went wrong."},
  {"id":"d58q5","prompt":"What does `@WithMockUser(roles = 'USER')` do?","options":["Creates a real user in the database","Populates the SecurityContext with a mock Authentication of a user with ROLE_USER — no actual authentication happens, no UserDetailsService called","Logs in via the login endpoint","Requires @SpringBootTest"],"correctAnswer":"Populates the SecurityContext with a mock Authentication of a user with ROLE_USER — no actual authentication happens, no UserDetailsService called","explanation":"@WithMockUser shortcuts the authentication process for testing authorization. The SecurityContext gets a pre-built authentication with the specified username/roles. Spring Security's authorization checks (hasRole, @PreAuthorize) see this user. No JWT filter, no UserDetailsService invoked."},
  {"id":"d58q6","prompt":"What HTTP status does a controller return when @RequestBody JSON is malformed (missing closing brace)?","options":["500 Internal Server Error","400 Bad Request — Spring throws HttpMessageNotReadableException which maps to 400","404 Not Found","200 with null fields"],"correctAnswer":"400 Bad Request — Spring throws HttpMessageNotReadableException which maps to 400","explanation":"Jackson cannot parse the malformed JSON → HttpMessageNotReadableException. Handled by @ExceptionHandler → 400 Bad Request. Test this: .content('{invalid json}') → andExpect(status().isBadRequest()). Important to verify your error handler formats this correctly."},
  {"id":"d58q7","prompt":"What must you add when posting JSON in a MockMvc test?","options":["Nothing extra needed","`.contentType(MediaType.APPLICATION_JSON)` — without it, Spring returns 415 Unsupported Media Type because the controller's @PostMapping expects JSON content","The Accept header","A session ID"],"correctAnswer":"`.contentType(MediaType.APPLICATION_JSON)` — without it, Spring returns 415 Unsupported Media Type because the controller's @PostMapping expects JSON content","explanation":"Content-Type header tells Spring what format the request body is. @PostMapping with @RequestBody expects Content-Type: application/json. Without it: 415 Unsupported Media Type. Also set Accept: application/json if the method uses produces."},
  {"id":"d58q8","prompt":"What is the difference between standaloneSetup MockMvc and @WebMvcTest?","options":["Identical","standaloneSetup: creates MockMvc from controller directly, no Spring context — very fast, manual wiring. @WebMvcTest: Spring loads MVC context including security filters, auto-configuration — slower but more realistic","standaloneSetup requires a running server","@WebMvcTest doesn't support MockMvc"],"correctAnswer":"standaloneSetup: creates MockMvc from controller directly, no Spring context — very fast, manual wiring. @WebMvcTest: Spring loads MVC context including security filters, auto-configuration — slower but more realistic","explanation":"standaloneSetup: MockMvcBuilders.standaloneSetup(controller).setControllerAdvice(handler).build(). No security, no auto-configuration. Test pure controller logic. @WebMvcTest: full MVC stack with security — test authorization, filters, auto-configured Jackson settings."},
  {"id":"d58q9","prompt":"How do you test that an endpoint returns a 403 Forbidden when accessed with insufficient role?","options":["Manually remove authentication","@WithMockUser(roles='USER') on a test for an admin endpoint — the controller's hasRole('ADMIN') check fails and Spring Security returns 403","Test 403 by not providing credentials","403 requires a real server"],"correctAnswer":"@WithMockUser(roles='USER') on a test for an admin endpoint — the controller's hasRole('ADMIN') check fails and Spring Security returns 403","explanation":"@WithMockUser(roles='USER') creates authentication with ROLE_USER. The admin endpoint requires ROLE_ADMIN. Spring Security evaluates the authorization rule and denies access → 403. andExpect(status().isForbidden()) verifies this. Separates 401 (unauthenticated) from 403 (unauthorized)."},
  {"id":"d58q10","prompt":"What does `objectMapper.writeValueAsString(req)` do in a MockMvc POST test?","options":["Validates the request object","Serializes the Java object to a JSON string — used as the request body for .content(json). The ObjectMapper in tests uses the same Jackson configuration as the application","Encrypts the request","Converts the object to XML"],"correctAnswer":"Serializes the Java object to a JSON string — used as the request body for .content(json). The ObjectMapper in tests uses the same Jackson configuration as the application","explanation":"In @WebMvcTest, @Autowired ObjectMapper gives you the application's Jackson configuration (date format, null handling, etc.). Using it to serialize ensures the request body matches exactly what a real client would send."}
],
"writtenConceptQuestions": [
  "Show a complete @WebMvcTest for OrderController: test GET by ID (200), GET not found (404 with error body), POST valid (201 with Location), POST invalid (400 with field errors).",
  "Explain @MockBean vs @Mock. When do you use each? Show why @Mock doesn't work in @WebMvcTest.",
  "Show testing security with MockMvc: authenticated user (200), unauthenticated (401), wrong role (403). Use @WithMockUser.",
  "What is jsonPath() and how do you test arrays? Show verifying an orders list with size, first element fields, and nested fields.",
  "Show standaloneSetup MockMvc: build from controller + exception handler, no Spring context. When is this preferred over @WebMvcTest?",
  "How do you test that a validation error returns the correct field error structure? Show POST with blank required field → 400 with {fieldErrors: {fieldName: message}}.",
  "What does .andDo(print()) help with? Show how to use it to debug a failing test."
],
"businessScenarios": [
  "A controller test uses @SpringBootTest for all 30 controller tests, taking 8 minutes total. Migrate to @WebMvcTest slices — show the test class restructuring and explain the speedup.",
  "A POST endpoint returns 415 Unsupported Media Type in tests. The developer forgot contentType(). Show the fix and explain what Content-Type header does.",
  "An admin-only DELETE endpoint is accidentally accessible to regular users in production. Add MockMvc tests for 200 (admin), 403 (regular user), and 401 (no auth) to catch this regression."
]
},

"day-059": {
"notes": """# Apache Kafka in Spring Boot: Topics, Producers, Consumers, and Consumer Groups

## Why Kafka? Event-Driven Architecture
Kafka is a distributed event streaming platform. Instead of services calling each other synchronously, services publish events to topics and other services consume them asynchronously. This decouples producers from consumers.

```
OrderService → [order.created topic] → InventoryService (deducts stock)
                                    → EmailService (sends confirmation)
                                    → AnalyticsService (updates metrics)
```

## Core Concepts
- **Topic**: named stream of records (like a queue with replay). Partitioned for parallelism.
- **Partition**: ordered, immutable sequence of records. Each partition is consumed by one consumer per group.
- **Consumer Group**: multiple consumers sharing the work of a topic. Each partition assigned to one consumer.
- **Offset**: position of a message in a partition. Consumer commits offset to track progress.
- **Producer**: writes records to topics.
- **Broker**: Kafka server. Production = cluster of brokers.

## Spring Kafka Setup
```yaml
# application.yml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      acks: all          # wait for all replicas to acknowledge (durability)
      retries: 3
    consumer:
      group-id: order-service
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      auto-offset-reset: earliest   # start from beginning if no offset stored
      properties:
        spring.json.trusted.packages: com.example.events
```

## KafkaTemplate — Producing Events
```java
@Service
@RequiredArgsConstructor
public class OrderEventPublisher {
    private final KafkaTemplate<String, OrderCreatedEvent> kafkaTemplate;

    public void publishOrderCreated(Order order) {
        OrderCreatedEvent event = new OrderCreatedEvent(
            order.getId(),
            order.getCustomerId(),
            order.getTotalAmount(),
            Instant.now()
        );

        // key = orderId (ensures all events for the same order go to the same partition)
        kafkaTemplate.send("order.created", order.getId(), event)
            .whenComplete((result, ex) -> {
                if (ex != null) {
                    log.error("Failed to publish order.created for {}", order.getId(), ex);
                } else {
                    log.info("Published order.created: offset={}, partition={}",
                        result.getRecordMetadata().offset(),
                        result.getRecordMetadata().partition());
                }
            });
    }
}

// Event record — must be serializable
public record OrderCreatedEvent(
    String orderId,
    String customerId,
    BigDecimal total,
    Instant createdAt
) {}
```

## @KafkaListener — Consuming Events
```java
@Component
@Slf4j
public class InventoryEventListener {

    @KafkaListener(
        topics = "order.created",
        groupId = "inventory-service",
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void onOrderCreated(
            @Payload OrderCreatedEvent event,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset) {

        log.info("Received order.created: orderId={}, partition={}, offset={}",
            event.orderId(), partition, offset);
        try {
            inventoryService.deductStock(event.orderId());
        } catch (InsufficientStockException e) {
            // publish compensating event
            kafkaTemplate.send("order.stock-failed", event.orderId(),
                new StockFailedEvent(event.orderId(), e.getMessage()));
        }
    }
}
```

## Consumer Groups — Parallel Processing
```
Topic: order.created (3 partitions)

Group: inventory-service (3 consumers)
  Consumer-1 → Partition 0
  Consumer-2 → Partition 1
  Consumer-3 → Partition 2

Group: email-service (1 consumer)
  Consumer-1 → Partition 0, 1, 2 (all partitions)

Messages in each partition are processed in order within the partition.
```

## Dead Letter Topic — Handling Consumer Failures
```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, OrderCreatedEvent>
        kafkaListenerContainerFactory(ConsumerFactory<String, OrderCreatedEvent> cf) {

    ConcurrentKafkaListenerContainerFactory<String, OrderCreatedEvent> factory =
        new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConsumerFactory(cf);

    // Retry 3 times, then send to DLT (Dead Letter Topic)
    factory.setCommonErrorHandler(new DefaultErrorHandler(
        new DeadLetterPublishingRecoverer(kafkaTemplate,
            (record, ex) -> new TopicPartition("order.created.DLT", record.partition())),
        new FixedBackOff(1000L, 3)  // 1 second delay, 3 retries
    ));
    return factory;
}
// Failed messages after 3 retries → order.created.DLT for manual inspection/replay
```

## Kafka vs REST — When to Use Each
| | Kafka | REST |
|---|---|---|
| Coupling | Loose (producer doesn't know consumers) | Tight (caller knows endpoint) |
| Failure handling | Consumer can retry, replay | Caller must handle immediately |
| Use case | Events, notifications, analytics | Queries, commands with immediate response |
| Order guarantee | Per-partition order | None |
| Throughput | Millions/second | Thousands/second |

## Common Mistakes
1. **No key on producer:** all messages go to one partition — no parallelism. Use a domain key (orderId, customerId).
2. **Auto-commit enabled (default):** offset committed even if processing fails — message is lost. Use manual ack or set `enable-auto-commit: false`.
3. **Processing non-idempotent operations without deduplication:** if a message is redelivered (after crash), it may be processed twice — use idempotency keys.
""",
"mcqs": [
  {"id":"d59q1","prompt":"What is a Kafka consumer group and why is it useful?","options":["A group of Kafka brokers","Multiple consumer instances sharing the work of a topic — each partition is assigned to one consumer in the group, enabling horizontal scaling and parallel processing","A group of topics consumed together","Consumer groups are for ordering guarantees"],"correctAnswer":"Multiple consumer instances sharing the work of a topic — each partition is assigned to one consumer in the group, enabling horizontal scaling and parallel processing","explanation":"Consumer group: 3 consumers in 'inventory-service' group with 3 partitions → one partition per consumer (parallel processing). Add a 4th consumer → one consumer is idle (only 3 partitions). Different groups independently consume the same topic (inventory + email both get every message)."},
  {"id":"d59q2","prompt":"Why use a message key (e.g., orderId) when producing to Kafka?","options":["Keys are required by Kafka","Keys route messages for the same entity to the same partition — ensures ordering for that entity. All events for order-123 are in partition 2 in sequence","Keys encrypt the message","Keys determine the consumer group"],"correctAnswer":"Keys route messages for the same entity to the same partition — ensures ordering for that entity. All events for order-123 are in partition 2 in sequence","explanation":"Kafka guarantees ordering within a partition, not across partitions. Using orderId as key: all events for order-123 (CREATED, UPDATED, SHIPPED) go to the same partition in order. Without a key, events are round-robin distributed — ordering lost."},
  {"id":"d59q3","prompt":"What does `auto-offset-reset: earliest` mean for a new consumer group?","options":["Start consuming from the latest messages only","Start from the beginning of the topic — process all historical messages from offset 0","Reset offsets daily","earliest is the default"],"correctAnswer":"Start from the beginning of the topic — process all historical messages from offset 0","explanation":"earliest: new consumer group starts from the oldest available message. latest: start from the newest (miss historical messages). Use earliest for new services that need to process past events. Use latest when historical events are irrelevant (e.g., real-time dashboard)."},
  {"id":"d59q4","prompt":"What is a Dead Letter Topic (DLT) in Kafka?","options":["A topic for deleted messages","A topic where messages that failed processing after all retries are sent — allows manual inspection and replay without blocking the main topic","A Kafka admin feature","DLT stores compressed messages"],"correctAnswer":"A topic where messages that failed processing after all retries are sent — allows manual inspection and replay without blocking the main topic","explanation":"Without DLT: a poison pill message (always fails) blocks the partition — no subsequent messages processed. With DLT: after N retries, the failing message moves to order.created.DLT. The main topic continues. Operations team inspects DLT, fixes the issue, and replays messages."},
  {"id":"d59q5","prompt":"What does `acks: all` mean in Kafka producer configuration?","options":["Send without waiting for acknowledgment","Wait for all in-sync replicas to write the message before acknowledging the producer — highest durability guarantee","acks: all is the default","Only the leader broker acknowledges"],"correctAnswer":"Wait for all in-sync replicas to write the message before acknowledging the producer — highest durability guarantee","explanation":"acks=0: fire and forget (fastest, can lose messages). acks=1: leader acknowledges (default for older clients). acks=all or -1: all in-sync replicas acknowledge (highest durability). If a broker fails, the message is safe on other replicas. Use acks=all for financial/critical data."},
  {"id":"d59q6","prompt":"What is the risk of Kafka's default auto-commit offset behavior?","options":["Offsets aren't committed","Offsets are committed on a schedule regardless of processing success — if the consumer crashes after commit but before processing completes, the message is lost (at-most-once semantics)","Auto-commit is too slow","Auto-commit causes duplicate processing"],"correctAnswer":"Offsets are committed on a schedule regardless of processing success — if the consumer crashes after commit but before processing completes, the message is lost (at-most-once semantics)","explanation":"auto.commit.interval.ms=5000 (default): Kafka commits offsets every 5 seconds. If crash happens after commit but before processing: message was 'consumed' (offset committed) but never actually processed. Fix: manual acknowledgment after successful processing (at-least-once)."},
  {"id":"d59q7","prompt":"What is at-least-once delivery in Kafka and what problem does it create?","options":["Each message delivered exactly once","Messages are delivered at least once but may be delivered multiple times on failure/retry — consumer must be idempotent (handle duplicate messages safely)","Messages may be lost","Only one consumer receives each message"],"correctAnswer":"Messages are delivered at least once but may be delivered multiple times on failure/retry — consumer must be idempotent (handle duplicate messages safely)","explanation":"At-least-once: commit offset AFTER processing. If crash after processing but before commit: message redelivered → processed twice. Solution: idempotent consumer (check if message was already processed using a unique messageId in DB). True exactly-once requires Kafka transactions."},
  {"id":"d59q8","prompt":"How does @KafkaListener handle concurrent consumption?","options":["Single-threaded always","concurrency property: @KafkaListener(concurrency='3') creates 3 consumer threads, each assigned to a different partition","@KafkaListener is always multi-threaded","Concurrency is set by the consumer group"],"correctAnswer":"concurrency property: @KafkaListener(concurrency='3') creates 3 consumer threads, each assigned to a different partition","explanation":"@KafkaListener(concurrency='3'): three consumer thread instances, each consuming from one partition. For optimal parallelism, concurrency should equal the number of partitions. More threads than partitions: extra threads idle."},
  {"id":"d59q9","prompt":"What is the difference between Kafka and a traditional message queue (RabbitMQ)?","options":["Kafka is faster only","Kafka retains messages for a configurable time (replay possible); queues delete messages after consumption. Kafka maintains offset per consumer group — multiple groups read independently. Queues: round-robin to one consumer","Kafka requires more memory","RabbitMQ supports more message types"],"correctAnswer":"Kafka retains messages for a configurable time (replay possible); queues delete messages after consumption. Kafka maintains offset per consumer group — multiple groups read independently. Queues: round-robin to one consumer","explanation":"Kafka log retention (default 7 days): replay past events by resetting offset. New service added: reads all historical events from the beginning. Traditional queue: message consumed → deleted. Kafka is append-only log; queues are point-to-point or pub/sub without replay."},
  {"id":"d59q10","prompt":"What does the Kafka partition key determine?","options":["Message size limit","Which partition the message is routed to — same key always goes to the same partition (murmur2 hash of key % numPartitions), ensuring ordering for that key","The consumer group","Message priority"],"correctAnswer":"Which partition the message is routed to — same key always goes to the same partition (murmur2 hash of key % numPartitions), ensuring ordering for that key","explanation":"key=orderId → hash(orderId) % partitionCount = partition number. Same orderId always → same partition → ordered processing. Different orderIds → distributed across partitions → parallelism. No key → round-robin across partitions (no ordering guarantee, but balanced load)."}
],
"writtenConceptQuestions": [
  "Show a Kafka producer in Spring Boot: KafkaTemplate.send() with key, event object, and a whenComplete() callback for success/failure logging.",
  "Show a @KafkaListener that consumes OrderCreatedEvent and deducts inventory. Show handling InsufficientStockException by publishing a compensating event.",
  "Explain consumer groups with a diagram: topic with 3 partitions, 3 consumers in inventory-service group (one per partition), 1 consumer in email-service group (all partitions).",
  "What is a Dead Letter Topic? Show the ConcurrentKafkaListenerContainerFactory with FixedBackOff(1000, 3) and DeadLetterPublishingRecoverer.",
  "Explain at-least-once vs exactly-once delivery. How do you make a Kafka consumer idempotent?",
  "What does acks=all mean? Show producer config for maximum durability.",
  "When should you choose Kafka over REST for inter-service communication? Give 3 concrete scenarios."
],
"businessScenarios": [
  "Order creation synchronously calls 3 downstream services (inventory, email, analytics). If any one fails, the whole transaction fails. Redesign using Kafka: order service publishes order.created, each downstream service consumes independently.",
  "A consumer crashes after committing the offset but before updating inventory. Orders are 'consumed' but inventory not deducted. Implement idempotent processing using a ProcessedEvent DB table with messageId uniqueness check.",
  "A new analytics service needs to process all historical orders (6 months of data). Design the solution: auto-offset-reset=earliest for the new consumer group, topic retention set to 6 months, and replay mechanics."
]
},

"day-060": {
"notes": """# Microservices: Principles, Decomposition, and Inter-Service Communication

## What Are Microservices?
A microservices architecture structures an application as a collection of small, independently deployable services. Each service owns its data store, has a single responsibility, and communicates via APIs or events.

```
Monolith:                          Microservices:
+-------------------------+        +----------+  +----------+  +----------+
|  OrderService           |        |  Order   |  | Inventory|  |  User    |
|  InventoryService       |  →     |  Service |  | Service  |  | Service  |
|  UserService            |        | (DB: PG) |  | (DB: PG) |  | (DB: PG) |
|  PaymentService         |        +----------+  +----------+  +----------+
|  One shared DB          |             ↕ Kafka / REST ↕
+-------------------------+        +----------+  +----------+
                                   | Payment  |  |Notific.  |
                                   | Service  |  | Service  |
                                   +----------+  +----------+
```

## Decomposition Strategies
```
1. By Business Capability:
   - Order Service: create, update, track orders
   - Inventory Service: stock management, reservations
   - Payment Service: charge, refund, payment methods
   - User Service: registration, auth, profiles

2. By Subdomain (Domain-Driven Design):
   - Bounded Contexts become services
   - Each service has its own ubiquitous language
   - Avoid "distributed monolith" — services that can't deploy independently
```

## Synchronous Communication — RestTemplate and WebClient
```java
// RestTemplate (older, blocking — Spring 6 recommends WebClient)
@Service
public class OrderService {
    private final RestTemplate restTemplate;
    private final String inventoryUrl;

    public boolean checkStock(String productId, int quantity) {
        StockResponse response = restTemplate.getForObject(
            inventoryUrl + "/api/inventory/{productId}",
            StockResponse.class,
            productId
        );
        return response != null && response.available() >= quantity;
    }
}

@Configuration
public class RestTemplateConfig {
    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
            .setConnectTimeout(Duration.ofSeconds(5))
            .setReadTimeout(Duration.ofSeconds(10))
            .build();
    }
}

// WebClient (reactive, non-blocking — preferred in Spring Boot 3)
@Service
public class InventoryClient {
    private final WebClient webClient;

    public InventoryClient(@Value("${inventory.service.url}") String baseUrl) {
        this.webClient = WebClient.builder().baseUrl(baseUrl).build();
    }

    public Mono<StockResponse> getStock(String productId) {
        return webClient.get()
            .uri("/api/inventory/{productId}", productId)
            .retrieve()
            .onStatus(HttpStatusCode::is4xxClientError,
                resp -> Mono.error(new NotFoundException("Product", productId)))
            .bodyToMono(StockResponse.class)
            .timeout(Duration.ofSeconds(5));
    }

    // Blocking call when you need the result synchronously
    public StockResponse getStockSync(String productId) {
        return getStock(productId).block();
    }
}
```

## Service Discovery — Why Hard-Coded URLs Don't Scale
```yaml
# PROBLEM: hard-coded URLs
inventory.service.url=http://inventory-service:8082

# SOLUTION with Spring Cloud Eureka:
# Services register themselves on startup
# Callers look up 'inventory-service' → Eureka returns available instances

# application.yml (Eureka client)
eureka:
  client:
    service-url:
      defaultZone: http://eureka-server:8761/eureka/
  instance:
    prefer-ip-address: true
```

## Circuit Breaker — Resilience4j
```java
// Prevents cascading failures: if inventory-service is down, don't keep waiting
@Service
public class OrderService {

    @CircuitBreaker(name = "inventoryService", fallbackMethod = "inventoryFallback")
    @TimeLimiter(name = "inventoryService")
    public boolean checkInventory(String productId, int qty) {
        return inventoryClient.getStock(productId).available() >= qty;
    }

    // Called when circuit is open or timeout occurs
    public boolean inventoryFallback(String productId, int qty, Exception e) {
        log.warn("Inventory service unavailable, allowing order: {}", e.getMessage());
        return true; // fail open (allow order) or fail closed (reject order) based on business rules
    }
}

# application.yml — circuit breaker config
resilience4j.circuitbreaker.instances.inventoryService:
  registerHealthIndicator: true
  slidingWindowSize: 10
  failureRateThreshold: 50   # open circuit if 50% of last 10 calls fail
  waitDurationInOpenState: 10s
  permittedNumberOfCallsInHalfOpenState: 3
```

## API Gateway — Single Entry Point
```
Client → API Gateway (port 8080) → Route to:
                                   → /api/orders/**    → Order Service :8081
                                   → /api/inventory/** → Inventory Service :8082
                                   → /api/users/**     → User Service :8083

API Gateway responsibilities:
- Authentication/JWT validation (once, not per service)
- Rate limiting
- Request routing
- SSL termination
- Load balancing
```

## Data Management — Database per Service
```java
// Each service has its OWN database — no shared DB
// Order Service: orders DB (PostgreSQL)
// Inventory Service: inventory DB (PostgreSQL)
// User Service: users DB (PostgreSQL)

// Cross-service data = denormalize or use events
// Instead of JOIN orders + users → Order stores customerEmail (denormalized)
// Or: Order Service queries User Service via REST for user details

// Saga Pattern for distributed transactions:
// 1. Order Service creates order (PENDING)
// 2. Publishes order.created event
// 3. Inventory Service reserves stock → publishes inventory.reserved
// 4. Payment Service charges card → publishes payment.completed
// 5. Order Service marks order CONFIRMED
// On any failure → compensating events to undo previous steps
```

## Common Mistakes
1. **Distributed monolith:** services that need to deploy together (shared DB, synchronous calls everywhere) have microservice complexity with monolith coupling. Split by real autonomy.
2. **Synchronous calls for everything:** chain of 5 services each calling the next = total latency sum + cascade failure risk. Use async events where response isn't needed immediately.
3. **Not handling network failures:** services will fail. Add timeouts, retries, and circuit breakers to all inter-service calls.
4. **Shared database across services:** loses service autonomy — schema changes in one service break others.
""",
"mcqs": [
  {"id":"d60q1","prompt":"What is the 'database per service' principle in microservices?","options":["All services share one DB for simplicity","Each service owns its own database schema — no other service accesses it directly. Cross-service data access goes through APIs or events. Ensures service autonomy and independent schema evolution","Services share a DB but use different schemas","One DB per team, not per service"],"correctAnswer":"Each service owns its own database schema — no other service accesses it directly. Cross-service data access goes through APIs or events. Ensures service autonomy and independent schema evolution","explanation":"Shared DB: Service A changes a table → Service B breaks. DB per service: each service's DB is an implementation detail. Services communicate via APIs/events, not by reading each other's tables. This enables independent deployment and technology choice."},
  {"id":"d60q2","prompt":"What is a circuit breaker pattern and why is it needed in microservices?","options":["A security pattern for API keys","Monitors call failure rate to a service; if failures exceed threshold, it 'opens' the circuit and returns fallback immediately without waiting for timeout — prevents cascading failures","A deployment pattern","Circuit breakers are for databases only"],"correctAnswer":"Monitors call failure rate to a service; if failures exceed threshold, it 'opens' the circuit and returns fallback immediately without waiting for timeout — prevents cascading failures","explanation":"Without circuit breaker: Inventory Service down → 50 threads waiting 30s for timeout → connection pool exhausted → Order Service also down → cascade failure. With circuit breaker: after 50% failure rate, circuit opens → instant fallback → Order Service stays up. Resilience4j implements this in Spring Boot."},
  {"id":"d60q3","prompt":"What is a 'distributed monolith' and why should it be avoided?","options":["A monolith deployed across multiple servers","Services that are deployed separately but are so tightly coupled (shared DB, synchronous chains, deploy-together) that they have microservice complexity without microservice benefits","A monolith with microservice naming conventions","Distributed monolith is an anti-pattern in databases only"],"correctAnswer":"Services that are deployed separately but are so tightly coupled (shared DB, synchronous chains, deploy-together) that they have microservice complexity without microservice benefits","explanation":"Distributed monolith: 10 services that all share one database and must deploy in sequence. You have: network latency of microservices, distributed transaction complexity, but none of the autonomy/scalability benefits. Worse than a real monolith. Fix: each service owns its data, deploys independently."},
  {"id":"d60q4","prompt":"What is the Saga pattern for distributed transactions?","options":["A distributed lock mechanism","A sequence of local transactions where each step publishes an event. If a step fails, compensating events undo previous steps — achieves eventual consistency without a distributed lock","A two-phase commit protocol","Saga is for Kafka only"],"correctAnswer":"A sequence of local transactions where each step publishes an event. If a step fails, compensating events undo previous steps — achieves eventual consistency without a distributed lock","explanation":"Traditional ACID: impossible across services without distributed transactions (slow, complex). Saga: each service commits locally and publishes event. On failure: compensating transactions (cancel reservation, refund payment). Choreography: services react to events. Orchestration: a saga orchestrator directs the flow."},
  {"id":"d60q5","prompt":"What is the difference between RestTemplate and WebClient?","options":["RestTemplate is newer","RestTemplate: synchronous/blocking — thread waits for response. WebClient: asynchronous/reactive (Project Reactor) — non-blocking, can handle thousands of concurrent requests with fewer threads","WebClient only works with Kafka","RestTemplate is deprecated in Spring 5"],"correctAnswer":"RestTemplate: synchronous/blocking — thread waits for response. WebClient: asynchronous/reactive (Project Reactor) — non-blocking, can handle thousands of concurrent requests with fewer threads","explanation":"RestTemplate: one thread per request, blocked during HTTP call. WebClient: reactive, uses event loop — thread released while waiting for response, reassigned when response arrives. Spring 6/Boot 3 recommends WebClient even in non-reactive apps for its flexibility and deprecates RestTemplate maintenance."},
  {"id":"d60q6","prompt":"What is service discovery and why is it needed?","options":["Finding bugs in services","A mechanism where services register their network location (IP:port) and clients look up services by name — needed because microservice instances start on dynamic ports and scale horizontally","Service discovery is for databases","Needed only for Kubernetes deployments"],"correctAnswer":"A mechanism where services register their network location (IP:port) and clients look up services by name — needed because microservice instances start on dynamic ports and scale horizontally","explanation":"Hard-coded URL: inventory-service:8082 fails if port changes, service moves, or you add a second instance. Eureka: services register on startup (instance 1: 10.0.0.1:8082, instance 2: 10.0.0.2:8082). Caller asks 'inventory-service' → Eureka returns available instances → client load balances."},
  {"id":"d60q7","prompt":"What responsibility does an API Gateway take on?","options":["Replacing individual services","Single entry point that handles: routing requests to backend services, authentication/JWT validation, rate limiting, SSL termination, and load balancing — clients talk to one URL","API Gateway is a message broker","API Gateway stores data"],"correctAnswer":"Single entry point that handles: routing requests to backend services, authentication/JWT validation, rate limiting, SSL termination, and load balancing — clients talk to one URL","explanation":"Without gateway: mobile app hardcodes 5 service URLs, handles auth for each. With gateway: one URL (api.example.com), JWT validated once, requests routed. Spring Cloud Gateway, Kong, and AWS API Gateway are implementations. Hides backend topology from clients."},
  {"id":"d60q8","prompt":"When should you use asynchronous communication (Kafka) vs synchronous (REST) between microservices?","options":["Always use REST","Kafka: when response isn't needed immediately, for events, notifications, processing pipelines. REST: when you need an immediate response (real-time query, user-facing request-response)","Always use Kafka","Kafka is only for logging"],"correctAnswer":"Kafka: when response isn't needed immediately, for events, notifications, processing pipelines. REST: when you need an immediate response (real-time query, user-facing request-response)","explanation":"REST: 'Is this product in stock?' — need answer now to show user. Kafka: 'Order was created' — inventory, email, analytics can process asynchronously. Kafka enables services to be down and catch up later. REST requires the downstream service to be available."},
  {"id":"d60q9","prompt":"What problem does denormalization solve in microservices data management?","options":["Removes the need for databases","Stores copies of data from other services locally — avoids synchronous cross-service calls for frequently needed data. Order stores customerName instead of querying User Service for every order display","Denormalization is only for performance","Denormalization replaces Kafka"],"correctAnswer":"Stores copies of data from other services locally — avoids synchronous cross-service calls for frequently needed data. Order stores customerName instead of querying User Service for every order display","explanation":"Order Service needs customer name for order display. Option 1: REST call to User Service per request (latency, coupling, availability dependency). Option 2: denormalize — store customerName in orders table. Tradeoff: if customer changes name, old orders show old name (eventual consistency). Often acceptable for historical data."},
  {"id":"d60q10","prompt":"What does `@CircuitBreaker(fallbackMethod = 'inventoryFallback')` do when the inventory service is down?","options":["Retries indefinitely","After the circuit opens (too many failures), calls the fallbackMethod directly without attempting the real call — returns a default response immediately instead of timing out","Throws an exception immediately","Restarts the inventory service"],"correctAnswer":"After the circuit opens (too many failures), calls the fallbackMethod directly without attempting the real call — returns a default response immediately instead of timing out","explanation":"Circuit states: CLOSED (normal), OPEN (fallback only), HALF-OPEN (test calls). When OPEN: no calls to inventory service, fallback returns immediately (e.g., assume stock available or return cached data). After waitDurationInOpenState, moves to HALF-OPEN to test if service recovered."}
],
"writtenConceptQuestions": [
  "Draw and explain the microservices architecture for an e-commerce system: 5 services, their responsibilities, communication patterns, and databases.",
  "Show a WebClient-based InventoryClient: GET stock, error handling for 4xx, timeout, and a blocking fallback for synchronous code.",
  "Explain the Saga pattern. Show an order creation saga: Order → Inventory → Payment → Confirm, with compensating events on failure.",
  "What is a circuit breaker? Show Resilience4j configuration and a Spring Boot service with fallback method.",
  "Explain service discovery. What problem does it solve? Show Eureka client configuration and how load balancing works.",
  "What is an API Gateway? Show routing configuration for 3 services with authentication handled at the gateway layer.",
  "When to decompose a monolith vs keep it? What signals indicate a feature should be its own service?"
],
"businessScenarios": [
  "A flash sale causes 10,000 concurrent requests to hit the inventory service. The order service has no circuit breaker — inventory timeouts cascade into order service failures. Add Resilience4j circuit breaker with fallback that allows orders and reconciles stock asynchronously.",
  "Two teams need to deploy Order Service and User Service independently but they share a database — one schema change by User team breaks Order Service. Design the migration: separate databases, add customerEmail column to orders, use events to keep denormalized data consistent.",
  "A REST call chain: Order → Inventory → Warehouse → Shipping adds 400ms latency. The shipping notification doesn't need to be synchronous. Redesign: Order publishes order.confirmed event, Shipping Service consumes it asynchronously, reducing user-facing latency to 100ms."
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
