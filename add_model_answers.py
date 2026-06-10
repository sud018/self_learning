#!/usr/bin/env python3
"""Add writtenModelAnswers and businessModelAnswers to all 90 curriculum JSON files."""
import json, os, glob

CURRICULUM_DIR = "backend/data/curriculum"

# Generic answers for Q4-Q10 (same structure every day, references "today's topic")
GENERIC = {
    "q4":  "In an order or customer workflow, misusing this concept can cause incorrect totals, wrong status updates, or missing customer records — directly harming business trust. Understanding it correctly ensures data integrity and reliable workflows that users depend on.",
    "q5":  "Spring Boot relies on Java as its foundation, so this concept appears in service beans, entity classes, and utility methods. Knowing it well prevents subtle bugs in backend logic that are hard to debug when an API returns wrong data.",
    "q6":  "Angular should show a spinner or disabled button while the request is in progress, display the data clearly on success, and show a user-friendly message with a retry option on error. Never leave the user staring at a blank screen — always communicate the state.",
    "q7":  "A useful SQL pattern for this day is: SELECT customer_id, COUNT(*) as total FROM orders WHERE status = 'active' GROUP BY customer_id ORDER BY total DESC. This shows which customers have the most active orders, helping the business prioritize support and retention.",
    "q8":  "Always test null/empty input, a single-element collection or string, boundary values (min and max), duplicate values, negative numbers where applicable, and large inputs near the constraint limit. Edge cases are where most production bugs hide.",
    "q9":  "In an interview I would say: state the data structure or algorithm, explain why it is the best fit for this problem, walk through one example manually before coding, write clean code with meaningful names, and state time and space complexity at the end.",
    "q10": "Five-point summary: (1) define the concept clearly, (2) explain why Java or the framework needs it, (3) describe how it works internally step by step, (4) give a real full-stack project usage example, (5) name the most common mistake and how to avoid it.",
    "b2":  "Check the server logs first to find which request triggered the wrong data. Then query the database directly to compare expected vs actual values. Add structured logging to the relevant service method (log inputs, outputs, and any validation failures) so future issues can be diagnosed in minutes, not hours.",
    "b3":  "The API response would be: { \"metric\": \"active_orders\", \"value\": 142, \"period\": \"2024-06-09\" }. The service runs: SELECT COUNT(*) FROM orders WHERE status='active' AND DATE(created_at)=CURDATE(). This gives the manager a daily health indicator without needing database access."
}

# Topic-specific answers: [q1 (explain), q2 (where in full-stack), q3 (what goes wrong), b1 (product owner questions)]
TOPIC_ANSWERS = {
    1: {
        "q1": "Java source code is compiled by javac into bytecode (.class files), which the JVM then interprets or JIT-compiles into machine code. JDK is the development kit containing javac and tools; JRE is the runtime with the JVM; JVM is the engine that runs bytecode on any OS. This is why Java is 'write once, run anywhere'.",
        "q2": "In a Spring Boot project, the JVM runs the entire backend server. javac compiles your classes during the build, and the JVM manages memory, garbage collection, and thread execution at runtime. Knowing JDK vs JRE matters when configuring CI/CD pipelines and Docker images.",
        "q3": "Using JRE-only in a Docker image (no javac) breaks the Java code compiler in the application. Misunderstanding heap vs stack causes memory leaks or StackOverflowError. Not knowing the classpath leads to ClassNotFoundException that is hard to debug.",
        "b1": "Ask: What should the program do? What inputs does it take and what outputs should it produce? What Java version is the target environment? Are there any existing classes or libraries to reuse? What counts as a successful test run?"
    },
    2: {
        "q1": "Variables are named containers that hold values of a specific data type. Primitive types (int, double, boolean, char) are stored directly on the stack; reference types (String, Object) are stored as pointers to heap memory. Operators (+, -, *, /, %, ==, !=, &&, ||) perform calculations and comparisons on these values.",
        "q2": "Variables and data types appear in every layer: service fields store business objects, method parameters pass data, and local variables hold intermediate results. Choosing the wrong type (int vs long for large IDs, String vs BigDecimal for money) causes silent bugs in production.",
        "q3": "Using int instead of long for large IDs causes overflow and wrong record lookups. Using float/double for monetary values causes rounding errors that accumulate over thousands of transactions. Comparing objects with == instead of equals() causes logic failures.",
        "b1": "Ask: What values does the feature store? What is the maximum value for numeric fields (to choose int vs long)? Does money need to be precise (use BigDecimal)? Are there nullable fields? What is the source of the input — user form, external API, or database?"
    },
    3: {
        "q1": "Control flow determines which statements execute based on conditions. if/else evaluates a boolean and runs one of two paths. switch matches a value against constant cases. for loops iterate a known number of times; while loops continue while a condition is true; do-while always runs at least once.",
        "q2": "Control flow appears in every service method: if/else for validation and business rules, for loops to process order items, while loops for retry logic. Wrong conditions cause business rules to be bypassed, wrong data to be returned, or infinite loops that crash the server.",
        "q3": "Off-by-one errors in loop bounds cause missing the last item or processing one too many. Using = (assignment) instead of == (comparison) in a condition is a silent bug. Not handling the else case for a condition causes NullPointerException when the expected branch is skipped.",
        "b1": "Ask: What are all the conditions that affect the behavior? What happens in each case (approved, pending, rejected)? What is the default behavior when no condition matches? Are conditions mutually exclusive? Will new conditions be added in the future (suggesting a more flexible design)?"
    },
    4: {
        "q1": "A method is a named, reusable block of code that takes parameters as input and returns a result. It promotes DRY (Don't Repeat Yourself) — write the logic once and call it from anywhere. Methods have a return type (or void), a name, and a parameter list that defines what callers must provide.",
        "q2": "In Spring Boot, service methods encapsulate business logic (calculateDiscount, validateOrder). Controller methods handle HTTP requests. Repository methods query the database. Good method names like createOrder(CreateOrderRequest) make code self-documenting and easy to maintain.",
        "q3": "Methods with too many parameters (more than 3-4) become hard to call correctly and easy to mis-order arguments. Methods that do too many things violate the Single Responsibility Principle, making them hard to test. Missing null checks for parameters cause NullPointerException in production.",
        "b1": "Ask: What single action should this method perform? What inputs are needed? What should it return? What happens if the input is null or invalid? Should it be reusable across multiple features or specific to one? What should happen on failure — throw exception or return an error?"
    },
    5: {
        "q1": "String is an immutable sequence of characters in Java, stored in the String pool to save memory. Important methods: length(), charAt(int), substring(int, int), equals(String), equalsIgnoreCase(), contains(), split(), trim(), toUpperCase(), and replace(). Since String is immutable, every modification creates a new object — use StringBuilder for heavy concatenation.",
        "q2": "Strings are everywhere in full-stack development: parsing HTTP request parameters, building SQL queries, validating email/phone formats, serializing JSON, and logging. Incorrect String handling causes NullPointerException, incorrect comparisons, and SQL injection when user input is not sanitized.",
        "q3": "Comparing Strings with == checks object identity, not value equality, causing silent logic bugs when two equal strings are different objects. Not trimming user input causes validation to fail for a trailing space. Not escaping special characters in SQL strings causes SQL injection vulnerabilities.",
        "b1": "Ask: Where does the string input come from — user input, database, or external API? Does it need validation (email format, length limit)? Should comparison be case-sensitive? Are there special characters that need escaping? Will this be displayed in a UI (watch for XSS) or stored in a database (watch for SQL injection)?"
    },
    6: {
        "q1": "An array is a fixed-size, contiguous block of memory holding elements of the same type. Declare with int[] nums = new int[5] or String[] names = {\"Alice\", \"Bob\"}. Access by zero-based index (nums[0]). Arrays are fast for random access (O(1)) but cannot change size after creation.",
        "q2": "Arrays appear in Java when processing fixed-size data sets, in DSA algorithm solutions, and as return types for multi-value methods. Spring Boot typically uses List instead of raw arrays in API responses, but arrays are common in coding challenges and algorithm implementations.",
        "q3": "Accessing an index outside the array bounds throws ArrayIndexOutOfBoundsException — the most common array bug. Not initializing array elements (they default to 0/null) causes unexpected null results. Using array length instead of array.length - 1 in loops causes off-by-one errors.",
        "b1": "Ask: Is the size fixed at compile time or does it grow dynamically (if dynamic, prefer ArrayList)? What type of elements does it store? Should duplicates be allowed? Does the order matter? Should elements be sorted? What happens when the array is empty — return null, empty array, or throw an exception?"
    },
    7: {
        "q1": "Java reads input with Scanner (System.in for console, new Scanner(file) for files) and writes output with System.out.println() for console or PrintWriter/FileWriter for files. Debugging means finding why code behaves incorrectly — use System.out.println() to print variables, or an IDE debugger to set breakpoints and step through execution.",
        "q2": "I/O appears in Spring Boot when reading configuration files, writing log files, processing uploaded files, and in testing (reading test data files). Understanding Scanner and PrintWriter helps debug standalone Java tools and batch processing jobs.",
        "q3": "Not closing Scanner or FileWriter causes resource leaks that degrade performance over time. Reading a line as a number without try-catch causes NumberFormatException if the input is not a valid number. Debugging with System.out.println left in production code clutters logs and can expose sensitive data.",
        "b1": "Ask: Where does the input come from — user, file, database, or API? What format is the input (CSV, JSON, plain text)? How large can the input be (affects memory strategy)? What should happen on malformed input? Should the output be stored, displayed, or sent to another system?"
    },
    8: {
        "q1": "Object-oriented thinking means modeling the real world as objects that have state (fields) and behavior (methods). A Customer object has name, email, address (state) and placeOrder(), cancelOrder() (behavior). Classes are the blueprints; objects are the instances. OOP promotes reusability, clarity, and separation of concerns.",
        "q2": "In a Spring Boot project, every entity (@Entity) is an object, every service (@Service) is an object with business behavior, and every DTO is an object that carries data. Object thinking determines how you design your class hierarchy, relationships, and which class owns which responsibility.",
        "q3": "Putting logic in the wrong class (e.g., calculating order totals in the controller) makes code hard to reuse and test. Creating too many fine-grained objects increases complexity. Not thinking about relationships between objects leads to redundant data and inconsistent state across the system.",
        "b1": "Ask: What are the main entities in this feature? What state does each entity hold? What actions (methods) can each entity perform? How do the entities relate to each other? Who is responsible for each business rule — which class owns the logic? What changes might happen in the future that this design should accommodate?"
    },
    9: {
        "q1": "Mini project thinking means taking a business requirement and designing a small working application from scratch. You identify entities, define their relationships, plan the data flow, and connect frontend, backend, and database in a simple but complete feature. The goal is to practice turning a requirement into working code.",
        "q2": "In a real project, this mindset applies to every feature: you sketch the Angular component → API endpoint → service method → repository query → database table flow. It prevents building pieces in isolation that don't connect at the end.",
        "q3": "Building each layer in isolation without testing the connection leads to integration bugs discovered late. Not defining the API contract (request/response structure) early causes frontend and backend to be incompatible. Skipping validation means invalid data reaches the database.",
        "b1": "Ask: What is the one user action this mini project supports? What data does the user input, and what do they expect to see? What is the simplest database schema that supports this? What API endpoints are needed? What should happen when the data is invalid or the operation fails?"
    },
    10: {
        "q1": "Day 10 is a self-assessment covering all Phase 1 Java foundations: JDK/JRE/JVM, variables and data types, control flow, methods, strings, arrays, I/O, and basic OOP. The goal is to identify which concepts feel confident and which need reinforcement before moving to OOP in Phase 2.",
        "q2": "All Phase 1 foundations underpin every part of a Java full-stack project. JVM knowledge helps with deployment, variables and types appear in every class, control flow is in every service method, and OOP thinking structures the entire codebase.",
        "q3": "Skipping Phase 1 revision leads to OOP learning on a shaky foundation, causing confusion when inheritance and polymorphism build on concepts like methods and objects that are not fully internalized yet.",
        "b1": "Ask: Which Phase 1 concepts do I feel most uncertain about? Can I write a complete Java class from scratch without notes? Can I explain JVM, arrays, and String behavior in an interview? What gaps exist between what I can explain and what I can code?"
    },
    11: {
        "q1": "A class is a blueprint that defines the structure (fields) and behavior (methods) of objects. It groups related data and logic together. You define it with the class keyword, and all objects created from that class share the same structure but have their own field values.",
        "q2": "In Spring Boot, every @Entity is a class mapping to a database table, every @Service is a class with business logic, and every DTO is a class defining the API contract. Poorly designed classes (too large, too many responsibilities) make the codebase hard to maintain and test.",
        "q3": "Classes with too many responsibilities (violating Single Responsibility Principle) become hard to change — fixing one thing breaks another. Public fields instead of private + getter/setter remove encapsulation. Static state in a class causes bugs in multithreaded Spring Boot applications.",
        "b1": "Ask: What single responsibility should this class have? What fields does it need? What methods will it expose? Should it be a value object (immutable) or a mutable entity? Does it extend another class or implement an interface? How will it be tested in isolation?"
    },
    12: {
        "q1": "An object is a specific instance of a class created with the new keyword. Each object has its own copy of instance fields and can call the methods defined in its class. Objects live on the heap, are referenced by variables, and are automatically garbage-collected when no longer reachable.",
        "q2": "In Spring Boot, the IoC container creates and manages bean objects (services, repositories, controllers) automatically. JPA creates entity objects mapped to database rows. Understanding object lifecycle helps you understand bean scope and when to use @Transient vs persistent fields.",
        "q3": "Modifying a shared object reference passed to a method changes the original object unexpectedly (pass-by-reference behavior). Returning null instead of an Optional or empty object causes NullPointerException in the caller. Creating too many large objects in a tight loop causes GC pressure and performance degradation.",
        "b1": "Ask: Who creates this object? Who owns it and is responsible for its lifecycle? Should it be immutable (no setters)? Which fields are required at creation time? How will this object be serialized (JSON, database)? Should there be a builder pattern for complex construction?"
    },
    13: {
        "q1": "A constructor is a special method that initializes an object's fields when it is created with new. It has the same name as the class and no return type. Java provides a default no-arg constructor if you define none. You can overload constructors to support multiple initialization patterns.",
        "q2": "In Spring Boot, @Service and @Component beans often use constructor injection: Spring calls the constructor and injects dependencies. JPA entities commonly use no-arg constructors (required by JPA). DTOs use all-args constructors for clean creation in service methods.",
        "q3": "Missing no-arg constructor on a JPA entity causes a Hibernate instantiation error at runtime. Doing complex logic in a constructor (like calling a database) makes testing difficult. Not initializing required fields in the constructor leads to NullPointerException when the object is used.",
        "b1": "Ask: What data is required to create a valid object? What should the object look like immediately after construction — fully ready to use? Should I provide a builder pattern for many optional fields? Does JPA need a no-arg constructor? Which dependencies should be injected via the constructor?"
    },
    14: {
        "q1": "Inheritance allows a child class to extend a parent class, inheriting all its non-private fields and methods and adding its own. Use the extends keyword. Employee extends Person, inheriting name and email while adding salary and department. A child object is also of the parent type (is-a relationship).",
        "q2": "In Spring Boot, BaseEntity (id, createdAt, updatedAt) is extended by all entity classes. A BaseService with common CRUD logic can be extended by specific services. In Angular, a BaseComponent with shared lifecycle logic can be extended by feature components.",
        "q3": "Deep inheritance hierarchies (more than 2-3 levels) make code hard to follow and change. Inheriting from a class when composition would be better violates good design. Not calling super() in the child constructor skips parent initialization. Overriding methods incorrectly breaks the Liskov Substitution Principle.",
        "b1": "Ask: Is this truly an is-a relationship, or would composition (has-a) be better? What common behavior should the parent define? Which methods should be abstract (forced implementation) vs concrete (default behavior)? How many levels of inheritance are needed? Will this hierarchy be stable or change frequently?"
    },
    15: {
        "q1": "Polymorphism means 'many forms' — the same method call behaves differently depending on the actual object type at runtime. A parent-type variable can hold a child object (upcasting), and calling an overridden method dispatches to the child's implementation. This enables writing flexible code that works with any subtype.",
        "q2": "In Spring Boot, service interfaces (OrderService) allow multiple implementations (OrderServiceImpl, CachedOrderServiceImpl) that can be swapped without changing controllers. In Angular, dependency injection provides polymorphism — inject a service interface and swap implementations in tests.",
        "q3": "Casting to the wrong subtype without instanceof check throws ClassCastException at runtime. Overriding a method with a different signature creates overloading, not overriding — the parent version is called unexpectedly. Not using @Override means a typo in the method name creates a new method silently.",
        "b1": "Ask: Does this behavior need to change based on the type of object? Are there multiple implementations that share the same interface? Can I define a common contract (method signature) that all implementations must follow? Will I need to add new implementations in the future without changing existing code?"
    },
    16: {
        "q1": "Abstraction hides complexity by exposing only what the caller needs to know. In Java, abstract classes provide partial implementation; interfaces provide pure contracts. A caller uses a PaymentService interface without knowing whether it calls Stripe, PayPal, or a mock. Abstraction reduces coupling between components.",
        "q2": "In Spring Boot, service interfaces abstract business logic from controllers. Repository interfaces (JpaRepository) abstract database queries. Angular services abstract HTTP calls from components. This lets you swap implementations (e.g., mock in tests, real in production) without changing calling code.",
        "q3": "Too much abstraction (over-engineering) makes code harder to understand without benefit. Exposing implementation details through a public interface (leaky abstraction) defeats the purpose. Not abstracting I/O and external services makes unit testing impossible.",
        "b1": "Ask: What does the caller need to know, and what should be hidden? Can I define a clean interface that won't need to change even if the implementation changes? How will I test this — do I need a mock or fake? Are there multiple current or future implementations that justify an interface?"
    },
    17: {
        "q1": "Encapsulation protects an object's internal state by making fields private and exposing them only through public getter/setter methods. The class controls validation in setters (e.g., rejecting negative prices), hiding how data is stored internally. This is the 'information hiding' principle.",
        "q2": "In Spring Boot entities, fields are private and accessed via getters/setters (or Lombok's @Getter/@Setter). DTOs use private fields with controlled access. Encapsulation prevents external code from setting an Order's status directly to 'SHIPPED' without going through the business logic that validates the transition.",
        "q3": "Public fields allow any code to change state directly, bypassing validation and breaking invariants. Over-using setters on entities allows the database to be updated from anywhere in the codebase, making auditing changes difficult. Exposing mutable collections directly (via getters) allows callers to modify internal state.",
        "b1": "Ask: Which fields should never be directly modified by outside code? What validation logic should run before a field is changed? Should the setter exist at all, or should state changes happen only through specific business methods? Can I return an immutable view of a collection instead of the mutable internal list?"
    },
    18: {
        "q1": "An interface defines a contract: a set of method signatures that any implementing class must provide. Unlike abstract classes, a class can implement multiple interfaces. Interfaces enable polymorphism (code depends on the interface, not the class) and are the basis of Spring Boot's dependency injection.",
        "q2": "Spring Boot services are often interface + implementation pairs (OrderService + OrderServiceImpl). Spring injects the interface, allowing easy testing with mocks. Repository interfaces (JpaRepository) are implemented automatically by Spring Data. Angular uses TypeScript interfaces to define data shapes.",
        "q3": "Implementing an interface but leaving methods as empty stubs (do nothing) violates the contract and causes silent failures. Adding a new method to a widely-used interface breaks all implementing classes (use default methods to add non-breaking new behavior in Java 8+). Confusing interface with abstract class leads to wrong design choices.",
        "b1": "Ask: What contract should all implementations guarantee? Are there multiple current or future implementations? Should this be an interface (pure contract) or abstract class (partial implementation with shared state)? Will the interface be stable, or will new methods be added often? How will mocks implement this interface in tests?"
    },
    19: {
        "q1": "An abstract class is a class that cannot be instantiated and may contain abstract (unimplemented) methods that subclasses must implement. It can also have concrete methods, fields, and constructors, allowing shared behavior across subclasses. Use when subclasses share common code but must each implement specific behavior.",
        "q2": "In Spring Boot, abstract base service classes define common CRUD logic that concrete services inherit. BaseEntity is an abstract class with id, createdAt, updatedAt fields shared by all entities. Abstract classes are useful when you need both shared implementation and enforced override contracts.",
        "q3": "Choosing abstract class over interface prevents implementing multiple contracts (Java allows only single inheritance). Not declaring necessary methods as abstract means subclasses aren't forced to implement them. Instantiating an abstract class directly (without a subclass) causes a compile error that's confusing for beginners.",
        "b1": "Ask: Do the subclasses share common code that belongs in a base class? Should some methods be defined but not implemented (abstract)? Should this be an abstract class (shared state + behavior) or an interface (pure contract)? How many levels of inheritance will this create? Will subclasses be tested independently?"
    },
    20: {
        "q1": "OOP Mock Interview day consolidates all eight OOP principles: Classes, Objects, Constructors, Inheritance, Polymorphism, Abstraction, Encapsulation, and Interfaces. A well-structured interview answer gives a definition, a real project example, the internal working, and the business reason for the design choice.",
        "q2": "All OOP concepts appear together in a Spring Boot project: Entity classes (encapsulation), inheritance for base entities, polymorphism through service interfaces, abstraction through repository interfaces, and constructors for dependency injection. Showing how they connect demonstrates senior-level thinking.",
        "q3": "Explaining OOP concepts in isolation without a real project example sounds memorized rather than understood. Confusing abstraction and encapsulation (both hide information but at different levels) is a common mistake. Not connecting OOP to testability and maintainability misses the interviewer's real question.",
        "b1": "Ask: Can you explain how OOP is applied in your current project's architecture? Can you design a simple class hierarchy for an order management system? How would you use polymorphism to add a new payment method without modifying existing code? Why would you choose an interface over an abstract class here?"
    },
    21: {
        "q1": "The Java Collections Framework provides interfaces (Collection, List, Set, Map, Queue) and implementations (ArrayList, HashSet, HashMap, LinkedList, TreeMap) for storing and manipulating groups of objects. The correct choice depends on whether you need ordering, uniqueness, key-value pairs, or fast lookups.",
        "q2": "Collections are the backbone of Java backend development: List<Order> for ordered result sets, Set<String> for unique values (email addresses), Map<String, User> for fast user lookups by ID, and Queue for background task processing in Spring Boot services.",
        "q3": "Using the wrong collection (ArrayList when you need unique values, HashMap when you need sorted keys) causes incorrect behavior or performance issues. Not specifying the generic type (raw List instead of List<Customer>) causes ClassCastException at runtime. Modifying a collection while iterating with a for-each loop causes ConcurrentModificationException.",
        "b1": "Ask: Does the collection need to preserve insertion order? Should duplicates be allowed? Do I need to look up elements by a key? How large can this collection grow? Will it be read more often than modified? Is thread safety required? Does the collection need to be sorted?"
    },
    22: {
        "q1": "List is an ordered, indexed Collection that allows duplicate elements and null values. Elements maintain their insertion order and can be accessed by zero-based index. The main implementations are ArrayList (array-backed, fast get), LinkedList (node-based, fast add/remove at ends), and Vector (thread-safe, legacy).",
        "q2": "List is used in Spring Boot for ordered result sets from JPA queries (List<Order> findByStatus('active')), for method parameters and return types in service layers, and in Angular for displaying lists of items in @for loops with a defined sequence.",
        "q3": "Using List when uniqueness is required allows duplicate entries — use Set instead. Calling get(index) without checking size() first causes IndexOutOfBoundsException. Sorting a List with Collections.sort() modifies the original; if the original order must be preserved, sort a copy.",
        "b1": "Ask: Is order important for this collection? Can there be duplicates? Will the most common operation be get-by-index, iterate, or search? How large can the list grow? Will it be modified frequently after creation? Should it be immutable (List.of()) or mutable?"
    },
    23: {
        "q1": "ArrayList is a resizable array backed by a dynamic array internally. It provides O(1) amortized add at the end, O(1) get by index, and O(n) add/remove in the middle (elements must shift). It is the default List choice for most situations where you read more often than you insert or delete in the middle.",
        "q2": "ArrayList is the most common return type for Spring Data JPA queries, service method results, and controller response lists. In Angular, component properties typed as arrays (or typed as Observable<Item[]>) are rendered with @for in templates.",
        "q3": "Using ArrayList in performance-critical code with frequent middle insertions/deletions causes O(n) performance — use LinkedList instead. Not initializing with an expected capacity for large lists causes multiple costly array copies as it grows. Calling remove(int index) on an ArrayList modifies indices of subsequent elements.",
        "b1": "Ask: How many elements are expected? Will the list be mostly read (ArrayList) or frequently restructured (LinkedList)? Should the initial capacity be set for efficiency? Should elements be sorted? Will this list be passed to the frontend — what DTO format is needed? Is thread safety needed (use Collections.synchronizedList)?"
    },
    24: {
        "q1": "LinkedList is a doubly-linked list where each element (node) holds a reference to the previous and next nodes. It provides O(1) add/remove at the head or tail and O(n) random access. It also implements Deque, making it useful as a stack or queue data structure.",
        "q2": "LinkedList is useful in backend processing queues, implementing undo/redo functionality, and in algorithms where frequent insertions/deletions at arbitrary positions are needed. As a Queue or Deque, it supports FIFO task processing patterns.",
        "q3": "Using LinkedList when random access is needed (frequent get(index)) causes O(n) performance instead of O(1) with ArrayList. LinkedList uses more memory per element (two pointers per node) than ArrayList. Iterating a LinkedList with an index-based loop is significantly slower than with an iterator.",
        "b1": "Ask: Will elements be added or removed primarily at the start or end (LinkedList advantage)? Is random access by index common (ArrayList advantage)? Is this used as a Queue (FIFO) or Stack (LIFO)? How large will the list be? Is memory overhead a concern? Is thread safety needed?"
    },
    25: {
        "q1": "Set is a Collection that does not allow duplicate elements — adding an existing element is silently ignored. It uses equals() and hashCode() to check uniqueness. Main implementations: HashSet (unordered, O(1)), LinkedHashSet (insertion-ordered), and TreeSet (sorted, O(log n)).",
        "q2": "Set is used in Spring Boot to enforce uniqueness: storing unique role names for a user, unique product category IDs in a request, or tracking which assignments a user has already completed. It prevents accidental duplicates without requiring explicit duplicate checking.",
        "q3": "A class used as a Set element must correctly implement hashCode() and equals() — if they are inconsistent, the Set will contain 'duplicates' that are logically equal but hash differently. Iterating a HashSet in a specific order is unreliable — use LinkedHashSet or TreeSet if order matters.",
        "b1": "Ask: Must each element be unique? Is the uniqueness based on the entire object or a specific field? Do I need the elements in sorted or insertion order? How large can the set grow? Will I need to check if an element exists frequently (Set's strength)? Does the element class have correct hashCode and equals?"
    },
    26: {
        "q1": "HashSet stores unique elements in a hash table, providing O(1) average-case performance for add, remove, and contains. Internally it is backed by a HashMap where elements are the keys. Two objects that are equals() must return the same hashCode() — violating this breaks HashSet correctness.",
        "q2": "HashSet is used in Spring Boot services for fast duplicate detection (has this email been used?), storing unique IDs of processed events, and caching unique values. It is the standard choice when you need fast membership testing without caring about order.",
        "q3": "If a mutable object is added to a HashSet and then its fields are changed (altering its hashCode), the Set can no longer find it, causing memory leaks. A class missing hashCode() uses the default (object identity), causing semantically equal objects to be treated as different. HashSet is not thread-safe — use CopyOnWriteArraySet in concurrent contexts.",
        "b1": "Ask: Does this class have correct hashCode() and equals() based on business identity? Is the element mutable (avoid putting mutable objects in HashSet)? Will elements be added and checked concurrently? Is insertion order ever needed? Is a sorted set needed for display?"
    },
    27: {
        "q1": "Map stores key-value pairs where each key is unique. Common operations: put(key, value) to store, get(key) to retrieve, containsKey(key) to check, and entrySet() to iterate all pairs. Main implementations: HashMap (fastest, unordered), LinkedHashMap (insertion-ordered), and TreeMap (sorted by key).",
        "q2": "Map is used everywhere in Spring Boot: caching objects by ID (Map<Long, Customer>), grouping orders by status (Map<String, List<Order>>), building HTTP response headers, and in Spring's ApplicationContext which maps bean names to bean instances. Maps are the backbone of lookups and groupings.",
        "q3": "Using a Map when a list with index lookup would suffice adds unnecessary complexity. Not handling the null return from get(key) causes NullPointerException when the key is absent (use getOrDefault). Modifying a Map while iterating its entrySet causes ConcurrentModificationException.",
        "b1": "Ask: What is the natural key for this data? Is the key globally unique? How many entries are expected? Will I look up values by key frequently? Do I need keys in sorted or insertion order? Should missing keys return null, a default, or throw an exception? Is thread safety required?"
    },
    28: {
        "q1": "HashMap stores key-value pairs in a hash table, providing O(1) average-case get, put, and remove. It uses hashCode() to determine bucket placement and equals() to resolve collisions. Keys and values can be null. HashMap is not ordered and is not thread-safe.",
        "q2": "HashMap is the default Map choice in Spring Boot services: mapping customer IDs to customer objects for fast lookup, building response maps, and storing configuration key-value pairs. Spring Boot's application context is itself a large HashMap of bean names to beans.",
        "q3": "A mutable key whose hashCode changes after being added breaks the Map — the entry becomes unreachable. Using a HashMap in a multithreaded Spring Bean without synchronization causes data corruption — use ConcurrentHashMap. Not handling null values returned by get() for missing keys is the most common HashMap NPE.",
        "b1": "Ask: Is this data keyed by a stable, unique identifier? Is thread safety required? Are there many concurrent reads (ConcurrentHashMap), or is single-threaded use fine (HashMap)? Should missing keys return a default value (getOrDefault)? Does the key class have correct hashCode and equals?"
    },
    29: {
        "q1": "TreeMap is a Map implementation backed by a Red-Black tree that keeps keys sorted in natural order or by a provided Comparator. All operations (get, put, remove) are O(log n). It provides additional navigation methods: firstKey(), lastKey(), headMap(), tailMap(), and floorKey().",
        "q2": "TreeMap is useful in Spring Boot when data must be returned in sorted key order: a price list sorted by product code, log entries sorted by timestamp, or a schedule sorted by date. It eliminates the need to sort after building the Map.",
        "q3": "Using TreeMap with a key type that doesn't implement Comparable and without providing a Comparator throws ClassCastException at runtime. TreeMap's O(log n) performance is slower than HashMap's O(1) — only use it when sorted order is genuinely needed. TreeMap keys cannot be null.",
        "b1": "Ask: Does the output need to be in sorted key order? What is the sort order (natural, reverse, custom)? How large is the map? Would a HashMap + sort step be simpler? Does the key type implement Comparable? Are navigation operations (firstKey, headMap) needed, or just basic get/put?"
    },
    30: {
        "q1": "Day 30 assesses mastery of the Java Collections Framework combined with SQL. You should be able to choose the right collection (List, Set, Map), understand their time complexities, and write SQL queries (SELECT, JOIN, GROUP BY) that answer real business questions without looking at notes.",
        "q2": "Collections and SQL together represent the two most common data manipulation tools in Java backend development. A service method might use a HashMap for in-memory grouping and also run a SQL GROUP BY query for database-level aggregation — knowing both allows you to choose the most efficient approach.",
        "q3": "Fetching all rows from the database into a List and then filtering in Java when a SQL WHERE clause would be more efficient wastes resources. Using a List where uniqueness is needed causes duplicates in reports. Not using an index on the SQL column being filtered causes slow queries on large tables.",
        "b1": "Ask: Should this grouping happen in SQL (faster for large data) or in Java (needed for complex business logic)? What SQL query would answer this business question? Which collection is the right in-memory structure? How will this data be returned to the frontend?"
    },
    31: {
        "q1": "Exception handling lets Java programs respond to errors gracefully instead of crashing. A try block contains code that might fail; catch blocks handle specific exception types; finally runs cleanup code regardless. throw signals an error; throws declares checked exceptions. Custom exceptions add business context.",
        "q2": "In Spring Boot, exception handling is implemented globally with @ControllerAdvice + @ExceptionHandler to catch exceptions from any controller and return structured JSON error responses. Service methods throw custom exceptions (OrderNotFoundException), and the global handler maps them to HTTP 404, 400, or 500 status codes.",
        "q3": "Catching Exception (the base class) and doing nothing (empty catch block) silently swallows errors and makes debugging nearly impossible. Re-throwing a checked exception as a RuntimeException without logging it loses the original context. Not providing a response body for error responses leaves the frontend with no information to display.",
        "b1": "Ask: What can go wrong in this method? Should the error be recoverable (catch and handle) or unrecoverable (let it propagate)? What HTTP status code should this error return? What information should the error response include? Should the error be logged? Will the frontend need to display a specific message?"
    },
    32: {
        "q1": "Generics allow you to write type-safe, reusable code by parameterizing classes and methods with type variables, e.g., List<Customer>, Optional<Order>, or Pair<String, Integer>. The compiler enforces types at compile time, preventing ClassCastException at runtime. Wildcards (? extends T, ? super T) allow flexible type bounds.",
        "q2": "Generics are everywhere in Spring Boot: service methods return Optional<Entity>, repository methods are typed (JpaRepository<Customer, Long>), and REST controllers use ResponseEntity<ResponseDTO>. Custom generic utility classes like ApiResponse<T> allow reusable response wrappers.",
        "q3": "Using raw types (List instead of List<String>) bypasses type safety and causes ClassCastException at runtime. Confusing ? extends T (read-only) with ? super T (write-only) leads to compiler errors. Overcomplicating generic bounds makes code unreadable — prefer simple types when generics add no value.",
        "b1": "Ask: Will this class or method work identically for multiple types? Can I use a specific type instead of a generic to keep it simpler? What are the type bounds — should it accept any type, or only subtypes of a specific class? Will wildcard types be needed for collection parameters?"
    },
    33: {
        "q1": "Java 8 introduced Lambda expressions, the Stream API, functional interfaces, Optional, the new Date/Time API, and default methods in interfaces. These features enable a more functional programming style — code that focuses on what to compute rather than how to loop through data. Java 8 is the baseline for modern Java backend development.",
        "q2": "Java 8 features are used throughout Spring Boot: Streams process lists of entities in service methods, Lambdas are passed to sort(), filter(), and map(), Optional wraps nullable return values from repositories, and LocalDate replaces Date in entity classes. Understanding Java 8 is essential for reading any modern Java codebase.",
        "q3": "Overusing Streams for simple loops (where a for-each is clearer) reduces readability. Not handling the empty Optional (calling get() without isPresent() check) causes NoSuchElementException — the same bug as null but with a better name. Using Date instead of LocalDate in new code introduces timezone and threading issues.",
        "b1": "Ask: Which Java 8 feature is most applicable here: Stream for data transformation, Lambda for callback behavior, Optional for nullable returns, or LocalDate for date handling? Can this loop be replaced with a Stream pipeline for clarity? Would Optional prevent null checks elsewhere in the code?"
    },
    34: {
        "q1": "A lambda expression is an anonymous function written as (parameters) -> body. It can replace verbose anonymous inner class implementations of functional interfaces. Lambda makes code shorter: list.sort((a, b) -> a.getName().compareTo(b.getName())) instead of a full anonymous Comparator class.",
        "q2": "Lambdas appear in Spring Boot in Stream pipelines (filter, map, reduce), Comparator definitions, event listeners, and anywhere a functional interface is expected. In Angular, arrow functions are TypeScript's equivalent and are used extensively in Observable pipes and component methods.",
        "q3": "Lambdas that are too complex (multiple lines, multiple conditions) should be extracted into a named method for clarity. Capturing a non-effectively-final variable in a lambda causes a compile error — use a local copy. Lambdas make stack traces less readable — add meaningful method names when debugging is important.",
        "b1": "Ask: Is there a functional interface here that a lambda can implement? Will this lambda be reused — if so, extract it as a named method reference. Is the lambda body short and clear, or should it be a named method? Are captured variables effectively final? Will this lambda need to throw checked exceptions?"
    },
    35: {
        "q1": "A functional interface has exactly one abstract method, making it the target for a lambda or method reference. Key built-in examples: Predicate<T> (test, returns boolean), Function<T,R> (apply, transforms T to R), Consumer<T> (accept, performs action), and Supplier<T> (get, produces a value). Mark with @FunctionalInterface to enforce the single-method rule at compile time.",
        "q2": "Functional interfaces appear in Spring Boot in Stream pipeline operations (Predicate for filter, Function for map), in validation logic, and when passing behavior as a parameter to a method. In Angular, TypeScript's type system uses similar patterns with function type signatures.",
        "q3": "Not annotating a custom functional interface with @FunctionalInterface means adding a second abstract method accidentally compiles without error but breaks lambda assignment silently. Confusing Consumer (void) with Function (returns value) causes compiler errors that are confusing without knowing the interface types.",
        "b1": "Ask: Am I passing behavior as a parameter (use a functional interface)? Which built-in functional interface fits — Predicate (yes/no), Function (transform), Consumer (side effect), or Supplier (provide)? Should I create a custom functional interface, or reuse a standard one? Will this be used with lambdas or method references?"
    },
    36: {
        "q1": "The Stream API processes collections in a declarative pipeline: source (collection.stream()), intermediate operations (filter, map, sorted, distinct, limit), and terminal operation (collect, forEach, count, reduce, findFirst). Streams are lazy — intermediate operations are only executed when a terminal operation is called. They don't modify the source collection.",
        "q2": "Streams are used heavily in Spring Boot service methods: filtering orders by status, transforming entity lists to DTO lists with map(), grouping results with Collectors.groupingBy(), and computing totals with Collectors.summingInt(). They replace verbose for-loops with readable one-liners.",
        "q3": "Calling a terminal operation twice on the same Stream throws IllegalStateException — streams cannot be reused. Using a Stream when a simple for-loop is clearer adds unnecessary complexity. Streams with side effects (modifying an external list inside forEach) are incorrect — use forEach for pure side effects only.",
        "b1": "Ask: Can this collection processing be expressed as filter → transform → collect? Which terminal operation gives the needed result: list, count, sum, or group? Are there performance concerns (parallel stream)? Is the collection large enough to justify streaming, or is a simple loop clearer? Can I chain multiple operations into one pipeline?"
    },
    37: {
        "q1": "Optional<T> is a container that either holds a non-null value or is empty, preventing NullPointerException. Use Optional.of(value) for guaranteed non-null, Optional.ofNullable(value) for possibly-null, and Optional.empty() for absent values. Use orElse(), orElseGet(), map(), filter(), and ifPresent() to work with the value safely.",
        "q2": "Spring Data JPA repository methods return Optional<Entity> for findById() — this forces the caller to handle the absence case explicitly instead of checking for null. Service methods should propagate Optional or throw a meaningful exception (EntityNotFoundException) when the value is absent.",
        "q3": "Calling optional.get() without checking isPresent() causes NoSuchElementException — the same bug as null but harder to trace. Using Optional as a method parameter or field defeats its purpose. Returning Optional.empty() to indicate an error that should be an exception confuses callers about the semantics.",
        "b1": "Ask: Can this value be absent, or is absence a programming error? If absent is a valid state, use Optional — if it should never happen, throw an exception. Should the caller decide what happens when absent, or should this method handle it? Will Optional be serialized to JSON (Spring handles this, but it needs configuration)?"
    },
    38: {
        "q1": "The Java Date/Time API (java.time, introduced in Java 8) provides immutable, thread-safe date and time classes. LocalDate (date only), LocalTime (time only), LocalDateTime (date + time), ZonedDateTime (with timezone), and Instant (machine timestamp). Use DateTimeFormatter for parsing and formatting strings to/from dates.",
        "q2": "In Spring Boot, LocalDate is used in entity fields (with @Column) for dates without timezone. Instant is used for audit timestamps. ZonedDateTime is needed for scheduling across timezones. Spring's Jackson integration auto-serializes LocalDate to ISO 8601 JSON strings with the JavaTimeModule configuration.",
        "q3": "Using the legacy Date or Calendar class causes threading issues and confusing API behavior. Not registering JavaTimeModule with Jackson causes JSON serialization to fail for LocalDate fields. Storing ZonedDateTime without the timezone offset causes wrong times when servers are in different timezones.",
        "b1": "Ask: Should this date include time (LocalDateTime) or just a date (LocalDate)? Is timezone needed (ZonedDateTime)? How should it be serialized to JSON? What format does the frontend expect? Should the date be immutable? How will date comparison and arithmetic be performed?"
    },
    39: {
        "q1": "The Comparable<T> interface defines the natural ordering of objects. Implement compareTo(T other) in the class itself to return negative (less than), zero (equal), or positive (greater than). Classes like Integer, String, and LocalDate already implement Comparable. Collections.sort() and TreeSet use compareTo() automatically.",
        "q2": "In Spring Boot, entity classes that need natural sorting (Product by price, Employee by name) implement Comparable. JPA query results can be sorted with ORDER BY SQL, but Comparable is useful when sorting happens in Java after loading from the database.",
        "q3": "Implementing compareTo inconsistently with equals (two objects that are equals() but compareTo() returns non-zero) violates the contract and causes bugs in TreeSet and TreeMap. Not handling null in compareTo throws NullPointerException. Overcomplicating compareTo with many fields is better done with Comparator.comparing() chained comparisons.",
        "b1": "Ask: Does this class have a natural, single ordering that makes sense for all use cases? Is this ordering stable (won't change)? Should I implement Comparable (natural order in the class) or use Comparator (flexible, external sorting)? How does this interact with equals() and hashCode() — are they consistent?"
    },
    40: {
        "q1": "Comparator<T> defines custom sorting logic external to the class, by implementing compare(T o1, T o2). Use Comparator.comparing(keyExtractor) for concise lambda-based comparators, .reversed() to flip the order, and .thenComparing() to add secondary sort criteria. Pass a Comparator to Collections.sort(), TreeMap, or PriorityQueue.",
        "q2": "Comparator is used in Spring Boot when you need to sort entities in multiple different ways: by price ascending, by name, or by most recent order date. Multiple Comparators can be defined as constants for reuse. Stream's sorted() method accepts a Comparator for inline sorting.",
        "q3": "A Comparator that returns 0 inconsistently (equal for sort but not for equals) causes TreeSet to treat them as equal and deduplicate objects incorrectly. Chaining comparators in the wrong order produces incorrect sort results. Implementing compare() with subtraction (a.id - b.id) causes integer overflow for large values — use Integer.compare() instead.",
        "b1": "Ask: Are there multiple ways to sort this collection in different contexts (use Comparator, not Comparable)? What is the primary sort key? Is a secondary sort needed for ties? Should null values be sorted first or last (Comparator.nullsFirst/nullsLast)? Will this Comparator be reused or is it a one-time sort?"
    },
    41: {
        "q1": "Dependency Injection (DI) is a design pattern where an object receives its dependencies from an external source instead of creating them itself. Instead of new OrderRepository() inside a service, Spring injects the repository via the constructor. This makes classes loosely coupled, easily testable, and replaceable.",
        "q2": "DI is the foundation of Spring Boot — every @Service, @Repository, and @Controller bean is injected where needed. Constructor injection (preferred) makes dependencies explicit and immutable. In Angular, services are injected into components via the constructor, following the same pattern.",
        "q3": "Circular dependencies (A depends on B, B depends on A) cause Spring to fail on startup. Field injection (@Autowired on a field) makes testing harder because dependencies can't be injected without the Spring context. Creating a new service instance with new instead of injecting it bypasses Spring's management entirely.",
        "b1": "Ask: What dependencies does this class need to do its job? Should those dependencies be injected (Spring manages) or created locally (short-lived objects)? Is constructor injection preferred over field injection for testability? Does this create a circular dependency? Will I need to mock this dependency in tests?"
    },
    42: {
        "q1": "A Spring Bean is an object whose lifecycle is managed by the Spring IoC container — creation, dependency wiring, and destruction. Beans are defined with @Component, @Service, @Repository, @Controller, or @Bean in a @Configuration class. The container creates one instance by default (singleton scope) and injects it wherever @Autowired or constructor injection is used.",
        "q2": "Every Spring Boot application consists entirely of beans working together. The @Service bean contains business logic, the @Repository bean accesses the database, and the @Controller bean handles HTTP. Understanding bean scopes (singleton, prototype, request) prevents bugs from shared mutable state.",
        "q3": "Singleton beans with mutable state cause race conditions in multithreaded Spring Boot applications. @Bean methods in non-@Configuration classes are not intercepted by CGLIB and create new instances each time — the method must be in a @Configuration class for singleton behavior. Prototype-scoped beans injected into singleton beans only get one prototype instance.",
        "b1": "Ask: Should this bean be a singleton (one instance shared) or prototype (new instance each time)? Does the bean hold mutable state that varies per request (use request scope instead)? Should it be a @Component, @Service, or @Repository to communicate its intent? Will it need lazy initialization (@Lazy) for startup performance?"
    },
    43: {
        "q1": "A Spring Boot Controller handles incoming HTTP requests and returns responses. @RestController combines @Controller and @ResponseBody, returning JSON directly. Each method is mapped to a URL and HTTP method with @GetMapping, @PostMapping, etc. Controllers should be thin — delegate all logic to a @Service.",
        "q2": "Controllers are the entry point of every REST API in Spring Boot. They define the API contract: URLs, HTTP methods, request body structure, and response structure. In a full-stack app, Angular's HttpClient sends requests to controller endpoints, and the controller delegates to the service layer.",
        "q3": "Putting business logic directly in the controller makes it untestable with unit tests and mixes HTTP concerns with domain concerns. Not using a response DTO and returning the JPA entity directly exposes internal database structure to the API consumer. Not validating the @RequestBody allows invalid data to reach the service layer.",
        "b1": "Ask: What URL should this endpoint use? What HTTP method is semantically correct for this action? What request body format does the frontend send? What response structure does the frontend need? What HTTP status code should success and each error case return? Which @Service method implements the business logic?"
    },
    44: {
        "q1": "REST (Representational State Transfer) is an architectural style for designing APIs over HTTP. It uses URLs to identify resources (/api/orders/123), HTTP methods for actions (GET=read, POST=create, PUT=update, DELETE=delete), and HTTP status codes to indicate outcomes (200=OK, 201=Created, 404=Not Found, 400=Bad Request).",
        "q2": "REST APIs are the communication layer between Angular frontend and Spring Boot backend. Every feature requires designing REST endpoints: what URL, what method, what request body, what response body, and what error cases. Good REST design makes the frontend simpler and the API self-documenting.",
        "q3": "Using POST for every operation (including reads) breaks REST semantics and makes caching impossible. Returning 200 OK for errors (with an error flag in the body) confuses HTTP clients and monitoring tools. Not versioning APIs (/api/v1/) makes it impossible to change the contract without breaking existing clients.",
        "b1": "Ask: What resource is this endpoint acting on? Which HTTP method correctly represents the action (read=GET, create=POST, replace=PUT, partial update=PATCH, remove=DELETE)? What is the resource URL structure? What HTTP status codes correspond to success and each failure? What does the request and response JSON look like?"
    },
    45: {
        "q1": "@RequestMapping and its shortcuts (@GetMapping, @PostMapping, @PutMapping, @DeleteMapping, @PatchMapping) map HTTP requests to controller methods. @PathVariable extracts segments from the URL (/orders/{id}), @RequestParam extracts query string parameters (?status=active), and @RequestBody deserializes the JSON request body into a Java object.",
        "q2": "Request mapping annotations define the contract between Angular and Spring Boot. Angular's HttpClient sends GET /api/orders?status=active and the @GetMapping('/orders') method with @RequestParam String status receives it. Correct mappings prevent 404 and 405 Method Not Allowed errors in production.",
        "q3": "A mismatch between the Angular request URL and the Spring @RequestMapping path causes 404. Using @RequestParam for large payloads (use @RequestBody instead) has URL length limits. Not matching the @PathVariable name to the path template variable name (e.g., {id} and @PathVariable Long orderId) causes a missing binding error.",
        "b1": "Ask: Should the ID be in the path (/orders/123, use @PathVariable) or in a query param (/orders?id=123, use @RequestParam)? Is the request data in the URL or in the request body? What URL path matches the resource hierarchy? Does the path need to be versioned? What does the Angular service method need to call?"
    },
    46: {
        "q1": "A DTO (Data Transfer Object) is a plain Java class used to transfer data between layers without exposing internal entity structure. Use a request DTO for incoming data (what the client sends), a response DTO for outgoing data (what the client receives), and separate DTOs for each operation to avoid over-posting or under-returning.",
        "q2": "DTOs are the API contract in Spring Boot. The controller receives CreateOrderRequest (request DTO) and returns OrderSummaryResponse (response DTO). This decouples the API from the JPA entity, preventing accidental exposure of sensitive fields like passwords, internal IDs, or audit timestamps.",
        "q3": "Returning JPA entities directly from controllers exposes the database schema, causes lazy-loading exceptions (LazyInitializationException), and prevents the API from evolving independently of the database. Using one DTO for all operations (create, update, response) causes over-posting attacks where clients set fields they shouldn't.",
        "b1": "Ask: What fields does the frontend actually need in the response? Should the request DTO match the entity, or is a different shape needed? Are there sensitive fields that should never leave the backend? Should validation annotations go on the request DTO? How does this DTO's structure affect the Angular TypeScript interface?"
    },
    47: {
        "q1": "Spring Boot Validation uses javax.validation annotations on DTO fields: @NotNull (not null), @NotBlank (not null, not whitespace), @Size(min, max), @Email, @Min, @Max, @Pattern. Add @Valid to the @RequestBody parameter in the controller to trigger validation. On failure, Spring throws MethodArgumentNotValidException.",
        "q2": "Validation is the first line of defense in the API layer. In a Spring Boot order service, the CreateOrderRequest is validated (@NotNull orderId, @Min(1) quantity) before reaching the service. A @ControllerAdvice handles MethodArgumentNotValidException and returns a 400 Bad Request with field-level error messages.",
        "q3": "Skipping input validation lets invalid data reach the service and database, causing constraint violations, data corruption, or security issues. Validating inside the service instead of in the DTO couples validation logic to business logic and makes it hard to test. Not returning field-level error messages in the 400 response makes debugging difficult for the frontend.",
        "b1": "Ask: What fields are required vs optional? What are the size or format constraints for each field? What should the error message say for each validation failure? Should custom validation logic be added with a @Constraint annotation? How will the frontend display the field-level errors?"
    },
    48: {
        "q1": "Spring Boot exception handling uses @ControllerAdvice + @ExceptionHandler to globally catch exceptions thrown from any controller and return consistent JSON error responses. Define custom exception classes (ResourceNotFoundException, ValidationException) and map them to HTTP status codes in the @ControllerAdvice.",
        "q2": "A global exception handler is one of the most important components in a Spring Boot API. It ensures every error — 404 for missing resources, 400 for invalid input, 500 for unexpected failures — returns a consistent error DTO (timestamp, status, message, path) instead of Spring's default HTML error page or a raw stack trace.",
        "q3": "Not having a global exception handler means different controllers return different error formats, making the frontend unable to reliably parse errors. Catching and swallowing exceptions (empty catch block) hides bugs. Returning a 200 status with an error flag in the body violates REST semantics and breaks monitoring tools.",
        "b1": "Ask: What exceptions can this service method throw? What HTTP status code should each exception map to? What error message should be visible to the client (no stack traces in production)? Should the exception be logged with full stack trace? Is there a global @ControllerAdvice, or does each controller need its own exception handling?"
    },
    49: {
        "q1": "Logging in Spring Boot uses SLF4J as the abstraction layer with Logback as the default implementation. Inject a logger with private static final Logger log = LoggerFactory.getLogger(YourClass.class). Log levels: TRACE, DEBUG, INFO, WARN, ERROR. Use structured logging (include userId, orderId) to make log messages searchable in production.",
        "q2": "Logging is the primary debugging tool in production Spring Boot applications. Log at INFO for normal business events (order created, payment processed), WARN for recoverable issues (retry attempted), and ERROR for unexpected failures with the exception object for stack trace. Never log passwords, tokens, or PII.",
        "q3": "Logging too little means production bugs are invisible and undebuggable. Logging too much (DEBUG in production) floods the log storage and hides important messages. Logging sensitive data (passwords, credit card numbers) violates security and compliance rules. Using System.out.println instead of a logger loses log level, timestamp, and correlation ID.",
        "b1": "Ask: What events in this flow are important to trace in production? What context (user ID, order ID, request ID) should be included in each log statement? What log level is appropriate — INFO for normal flow, WARN for degraded, ERROR for failures? Will this be sent to a centralized log aggregator (ELK, Splunk)? Is sensitive data accidentally included?"
    },
    50: {
        "q1": "Spring Boot configuration uses application.properties or application.yml to set properties like server.port, spring.datasource.url, and custom properties. Inject individual values with @Value('${property.name}'). Group related properties with @ConfigurationProperties into a type-safe class. Use Spring profiles (dev, prod) for environment-specific settings.",
        "q2": "Configuration drives the behavior of a Spring Boot application without changing code. In a full-stack app: the database URL comes from config (different per environment), the JWT secret is a config value (injected via @Value), and feature flags are config properties checked in service code. Never hardcode environment-specific values in source code.",
        "q3": "Hardcoding environment-specific values (database passwords, API keys) in source code is a security violation. Not externalizing configuration means changing a port or URL requires rebuilding the application. Using @Value for complex grouped properties (use @ConfigurationProperties instead) makes the code cluttered and properties untraceable.",
        "b1": "Ask: What values will differ between development, staging, and production environments? Are any values sensitive (passwords, keys) that must not be in source control? Should these be grouped into a @ConfigurationProperties class? What is the default value when the property is absent? How will Railway/cloud environment variables override these values?"
    },
    51: {
        "q1": "JPA (Jakarta Persistence API) is the Java standard for Object-Relational Mapping. Map a Java class to a database table with @Entity, @Table. Map fields to columns with @Column. Define the primary key with @Id and @GeneratedValue. Spring Data JPA's JpaRepository provides findById, findAll, save, delete, and custom derived query methods automatically.",
        "q2": "JPA is the bridge between Spring Boot's Java objects and the relational database. Every database table in the application corresponds to a @Entity class. Repository interfaces extending JpaRepository<Entity, ID> provide CRUD without writing SQL. This simplifies 80% of database interactions in a typical business application.",
        "q3": "Not adding @Entity causes Spring to ignore the class entirely. Using a mutable primary key causes JPA to re-insert rows instead of updating. The N+1 query problem (one query to fetch N entities, then N queries for each relationship) silently degrades performance — use JOIN FETCH or @EntityGraph to prevent it.",
        "b1": "Ask: What table does this entity map to? What is the primary key strategy (auto-generated, UUID, natural key)? Which fields should be nullable? Are there relationships to other entities (@OneToMany, @ManyToOne)? What fetch strategy is appropriate (LAZY vs EAGER)? What JPA queries are needed beyond basic CRUD?"
    },
    52: {
        "q1": "Hibernate is the most popular JPA implementation. It translates @Entity annotations to SQL DDL and Java operations to SQL DML (INSERT, UPDATE, DELETE, SELECT). Hibernate manages the EntityManager, first-level cache (session cache), and second-level cache. Spring Boot auto-configures Hibernate via spring.jpa properties.",
        "q2": "In Spring Boot, Hibernate runs behind the scenes for every JPA operation. Understanding Hibernate helps you debug generated SQL (spring.jpa.show-sql=true), configure the DDL strategy (create, validate, update), and understand when Hibernate flushes changes to the database within a transaction.",
        "q3": "The LazyInitializationException occurs when accessing a LAZY-loaded relationship outside a transaction — the Hibernate session is already closed. Not understanding Hibernate's flush behavior causes changes to be lost or double-saved. The N+1 problem from lazy loading in loops is a top performance issue in production Spring Boot apps.",
        "b1": "Ask: Should Hibernate generate the schema (ddl-auto=update) or use Flyway/Liquibase migrations? Is lazy loading needed for this relationship? Where in the application lifecycle are Hibernate sessions open? Is spring.jpa.show-sql enabled in dev to verify the generated SQL? Are there any N+1 query patterns in this feature?"
    },
    53: {
        "q1": "JPA maps relationships between entities: @ManyToOne (many orders per customer, foreign key on order), @OneToMany (customer has many orders, inverse side), @OneToOne (user has one profile), @ManyToMany (orders have many products, join table). The owning side has @JoinColumn; the inverse side has mappedBy. FetchType.LAZY avoids loading related data unnecessarily.",
        "q2": "Relationships are at the core of business data modeling in Spring Boot. An Order has a @ManyToOne Customer and @OneToMany OrderItems. Getting this right determines whether queries are efficient and whether Hibernate generates correct SQL. Wrong fetch types cause either the N+1 problem (LAZY) or unnecessarily large queries (EAGER).",
        "q3": "Bidirectional relationships require careful management of both sides — forgetting to set the inverse side causes the relationship to not be persisted. EAGER fetching on @OneToMany loads entire collections every time the parent is loaded, causing memory and performance issues. Circular relationships in bidirectional @OneToMany cause infinite recursion in Jackson JSON serialization.",
        "b1": "Ask: What is the cardinality between these two entities? Which side owns the foreign key? Should the relationship be LAZY or EAGER? In bidirectional relationships, which side is the owning side? Does the JSON serialization need to avoid infinite recursion (@JsonIgnore, @JsonManagedReference)? Are cascade operations needed (save parent → save children)?"
    },
    54: {
        "q1": "A database transaction groups multiple operations into a single atomic unit — all succeed or all fail (rollback). Spring's @Transactional annotation manages transactions declaratively on service methods. Key properties: propagation (REQUIRED: join or create), isolation (READ_COMMITTED: default), and readOnly (true for read-only optimizations).",
        "q2": "In a Spring Boot order service, creating an order involves: saving the order, deducting inventory, and recording a payment — all in one @Transactional method. If payment fails, the entire transaction rolls back, preventing partial data. @Transactional(readOnly=true) on query methods improves performance.",
        "q3": "@Transactional only works on public methods called through the Spring proxy — calling a @Transactional method from within the same class bypasses the proxy and the transaction. Not marking service methods as @Transactional when they modify multiple tables risks partial updates on failure. Rolling back only for RuntimeException by default — checked exceptions don't trigger rollback unless rollbackFor is specified.",
        "b1": "Ask: Does this operation modify multiple tables that must succeed or fail together? What propagation behavior is needed (join existing transaction or create new)? Should failures roll back for checked exceptions too? Is this method read-only (set readOnly=true)? What isolation level prevents the specific concurrency issue you're trying to avoid?"
    },
    55: {
        "q1": "Spring Security provides authentication (who are you?) and authorization (what can you do?) for Spring Boot applications. It works through a filter chain that intercepts every HTTP request. Configure it with a SecurityFilterChain bean that defines which URLs require authentication and which roles can access which endpoints.",
        "q2": "Spring Security is added to every production Spring Boot API to protect endpoints. A typical configuration requires authentication for all /api/** endpoints, permits public access to /api/auth/login, and uses a JWT filter to validate tokens on each request. Role-based access control (@PreAuthorize) restricts actions by user role.",
        "q3": "Permitting all requests (httpSecurity.permitAll()) accidentally removes all security. Not disabling CSRF for stateless REST APIs causes all POST requests to fail with 403 (CSRF token not found). Storing passwords in plaintext instead of using BCryptPasswordEncoder is a critical security vulnerability.",
        "b1": "Ask: Which endpoints should be public (login, registration) and which require authentication? What roles exist, and which endpoints are restricted to which roles? Is the API stateless (JWT) or session-based? Should CSRF protection be enabled? How will the security configuration change between dev and production environments?"
    },
    56: {
        "q1": "A JWT (JSON Web Token) is a base64-encoded, signed token with three parts: header (algorithm), payload (claims: userId, roles, expiry), and signature (HMAC or RSA). After login, the server generates a JWT and returns it; the client stores it and sends it in the Authorization: Bearer <token> header on every request. The server validates the signature without a database lookup.",
        "q2": "JWT is the standard authentication mechanism for stateless Spring Boot REST APIs consumed by Angular frontends. After login, Angular stores the JWT (memory or localStorage), an Angular HTTP interceptor adds it to every request, and Spring Security's JWT filter validates it and sets the security context.",
        "q3": "Storing JWT in localStorage exposes it to XSS attacks — use HttpOnly cookies or in-memory storage. Not setting a short expiry (exp claim) means stolen tokens are valid indefinitely. Storing sensitive data in the JWT payload is unsafe because the payload is only base64-encoded, not encrypted — anyone can decode it.",
        "b1": "Ask: What claims should be in the JWT payload (userId, roles, expiry)? What is the appropriate token expiry time? Where should the Angular app store the token? How will the token be refreshed before expiry? What should happen when the token is invalid or expired — redirect to login? How will the JWT secret be stored securely?"
    },
    57: {
        "q1": "Spring Boot testing uses JUnit 5 for assertions, Mockito for mocking, @SpringBootTest for full integration tests, @WebMvcTest for controller tests with MockMvc, @DataJpaTest for repository tests with an in-memory database, and @MockBean to replace real beans with mocks in the Spring context.",
        "q2": "Testing is how you verify that your Spring Boot API works correctly before deploying. Unit tests cover service logic in isolation (no Spring context, fast). Integration tests with @SpringBootTest verify the complete flow from controller to database. CI/CD pipelines run tests automatically on every commit to catch regressions.",
        "q3": "Not testing edge cases (empty input, duplicate requests) means bugs are discovered in production. Over-relying on integration tests (slow, brittle) instead of unit tests for logic makes the test suite slow. Tests that don't assert meaningful behavior (only verify no exception) give false confidence.",
        "b1": "Ask: What are the critical paths that must be tested? Should this be a unit test (service logic only) or integration test (full stack)? Which dependencies need to be mocked? What edge cases must be covered (empty, null, invalid, duplicate)? What assertions prove the behavior is correct? Should tests be run in CI/CD?"
    },
    58: {
        "q1": "MockMvc is a Spring Test utility for testing @RestController methods without starting a real HTTP server. Use perform(get('/api/orders').param('status', 'active')) and chain andExpect(status().isOk()).andExpect(jsonPath('$[0].id').value(1)). Combine with @WebMvcTest and @MockBean to isolate the controller layer.",
        "q2": "MockMvc tests verify the API contract: that the correct URL, method, and JSON response are returned for each endpoint. In a Spring Boot order service, MockMvc tests confirm that GET /api/orders?status=active returns the expected JSON list with the correct fields and a 200 status.",
        "q3": "Not mocking the @Service with @MockBean means the test becomes an integration test requiring the full context and database. Not testing error scenarios (404 for missing resource, 400 for invalid input) leaves error handling untested. Using jsonPath() assertions that are too broad (exists but doesn't check value) gives false confidence.",
        "b1": "Ask: What HTTP method and URL does this endpoint handle? What request body or params does it accept? What response body and status code should it return? What happens on invalid input (400) or missing resource (404)? Which service methods need to be mocked with @MockBean? Is authentication needed in the test?"
    },
    59: {
        "q1": "Apache Kafka is a distributed, fault-tolerant event streaming platform. Producers publish messages to named topics; multiple consumer groups can independently read from those topics. Messages are retained for a configurable period, allowing replay. Spring Boot integrates with @KafkaListener on consumer methods and KafkaTemplate for producers.",
        "q2": "In a Spring Boot microservices system, Kafka decouples services: when an order is created, the Order Service publishes an OrderCreated event to a Kafka topic, and the Inventory Service, Email Service, and Analytics Service each consume it independently. This enables async communication without tight coupling.",
        "q3": "Consumers that process messages too slowly fall behind the partition offset, causing message lag. Not handling deserialization errors causes a consumer to get stuck on a bad message indefinitely — add a dead-letter topic. At-least-once delivery (Kafka's default) means your consumer must be idempotent to handle duplicate messages.",
        "b1": "Ask: Which events need to be decoupled from the request-response cycle? What is the message schema (use a schema registry for Avro)? How many partitions are needed for throughput? Should the consumer be idempotent? What happens if a message fails — dead-letter queue? Is guaranteed ordering needed (single partition)?"
    },
    60: {
        "q1": "Microservices architecture splits a monolithic application into small, independently deployable services, each owning a specific business domain and its own database. Services communicate via REST or messaging (Kafka). Benefits: independent scaling, independent deployment, and technology flexibility. Challenges: distributed system complexity and network failures.",
        "q2": "In a full-stack Java project, microservices means the Order Service, User Service, and Payment Service are separate Spring Boot applications. An API Gateway (Spring Cloud Gateway) routes requests from the Angular frontend to the correct service. Service discovery (Eureka) allows services to find each other dynamically.",
        "q3": "Splitting too early into microservices before understanding the domain boundaries creates the wrong boundaries that are expensive to fix. Not handling network failures (use Resilience4j circuit breaker) makes the system fragile. Distributed transactions across services are extremely complex — prefer eventual consistency with Saga pattern.",
        "b1": "Ask: Is the system large enough to justify microservices complexity? Where are the clear business domain boundaries? How will services communicate (REST or events)? How will the Angular frontend know which service URL to call? How will distributed tracing work across services? Is a database per service needed, or can they share?"
    },
    61: {
        "q1": "An Angular component is the fundamental building block of the UI. Each component has a TypeScript class (state + logic), an HTML template (view), and optional CSS styles. Components are identified by a selector (@Component({ selector: 'app-orders' })) used as a custom HTML tag. Components manage their own state and communicate via @Input and @Output.",
        "q2": "Every page and UI element in an Angular frontend is a component. A Spring Boot API result is displayed through a component that holds the data in a property, calls a service to fetch it, and renders it in the template. Components integrate with services, routing, and forms to create the complete frontend.",
        "q3": "Putting HTTP calls directly in a component instead of a service makes the component untestable and logic non-reusable. Not unsubscribing from Observables in ngOnDestroy causes memory leaks in single-page applications. Mutating @Input() properties in the child component breaks the one-directional data flow and confuses change detection.",
        "b1": "Ask: What state does this component manage? What data does it receive from a parent (@Input)? What events does it emit to the parent (@Output)? Which service does it depend on for data? What lifecycle hooks are needed (ngOnInit for data loading, ngOnDestroy for cleanup)? What are the loading, success, and error states?"
    },
    62: {
        "q1": "Angular templates are enhanced HTML that render component state. Use {{ expression }} for text interpolation, [property]='expr' for one-way property binding, (event)='handler()' for event binding, @if for conditional rendering, and @for for list rendering. Templates update automatically when the component state changes via Angular's change detection.",
        "q2": "Templates define exactly what the user sees and how they interact with the Angular application. A Spring Boot API response is rendered through a template: @for (order of orders) to list orders, @if (loading) to show a spinner, and [class.active]='selected' to highlight the selected item.",
        "q3": "Complex logic (calculations, filtering) directly in templates is slow and untestable — move it to the component class or a pipe. Not using trackBy in @for loops causes Angular to re-render the entire list on every change, degrading performance for large lists. Calling methods with side effects directly in template expressions runs on every change detection cycle.",
        "b1": "Ask: What data from the component class needs to be displayed? Are there conditional elements (loading, empty state, error)? Is a list rendered (use @for with trackBy)? What user events need to be captured (click, input, submit)? Are there dynamic CSS classes or styles based on state? Should this use the async pipe for Observables?"
    },
    63: {
        "q1": "Angular data binding connects the component TypeScript class to the HTML template in four ways: interpolation {{ value }} for text, property binding [prop]='expr' for DOM properties, event binding (event)='handler()' for user actions, and two-way binding [(ngModel)]='field' for form inputs (syncs in both directions).",
        "q2": "Data binding is what makes Angular pages dynamic. When a Spring Boot API response arrives, the component updates a property (this.orders = orders), and the template's @for binding automatically re-renders the list. Form bindings capture user input in real time, enabling live validation feedback.",
        "q3": "Using string concatenation ('myValue: ' + value) in templates instead of interpolation is less efficient and harder to read. Two-way binding with [(ngModel)] on a complex object causes deep equality checks that degrade performance — consider reactive forms for complex forms. Event binding without stopping propagation ((click)='save(); $event.stopPropagation()') causes parent click handlers to fire unexpectedly.",
        "b1": "Ask: Which properties should be displayed in the template (use interpolation)? Which DOM attributes should be bound to component state ([disabled], [class])? Which user events need handlers ((click), (input), (submit))? Is two-way binding needed for a form field ([(ngModel)])? Should the async pipe be used to subscribe to an Observable directly in the template?"
    },
    64: {
        "q1": "Angular directives extend HTML behavior. Structural directives change the DOM structure (@if adds/removes elements based on a condition, @for renders a list, @switch for multiple cases). Attribute directives change appearance or behavior without changing the DOM structure ([ngClass] adds CSS classes dynamically, [ngStyle] applies inline styles).",
        "q2": "Directives are used throughout Angular templates. @if (loading) shows a spinner while data loads. @for (order of orders; track order.id) renders the orders list. [ngClass]='{'active': isSelected}' highlights selected items. Custom directives encapsulate reusable DOM behavior like auto-focus or click-outside detection.",
        "q3": "Not using trackBy with @for causes Angular to destroy and recreate all list DOM nodes on every change, degrading performance. Missing @else in @if can leave the user with a blank area when the condition is false. Complex attribute directive logic that belongs in the component class makes templates hard to read and debug.",
        "b1": "Ask: Is this element conditionally shown or hidden (@if)? Does the template iterate over a list (@for)? Can I add trackBy to the @for to improve performance? Are there dynamic CSS classes ([ngClass]) or styles ([ngStyle]) based on component state? Is there repeated DOM manipulation logic that should be a custom attribute directive?"
    },
    65: {
        "q1": "An Angular service is a TypeScript class decorated with @Injectable that provides reusable logic, HTTP calls, or shared state to components. Services are injected via constructor injection. The providedIn: 'root' option makes the service a singleton shared across the entire application.",
        "q2": "Services are the bridge between Angular components and the Spring Boot API. Every HTTP call (HttpClient.get(), .post()) should live in a service, not a component. Shared state like the currently logged-in user or a loading flag is also kept in a service so multiple components can access it.",
        "q3": "Putting HTTP calls or business logic directly in components makes them untestable and logic non-reusable across the app. Multiple instances of a service (not using providedIn: 'root') cause data inconsistency between components. Not cleaning up Subjects or Subscriptions in a service causes memory leaks in long-running applications.",
        "b1": "Ask: Is this logic used in multiple components (extract to a service)? Does this service need to be a singleton or can it be scoped per component? What state should this service hold? How will it communicate changes to subscribers (BehaviorSubject)? How will this service be mocked in component unit tests?"
    },
    66: {
        "q1": "Angular's Dependency Injection (DI) framework provides services and values to components and other services through constructor injection. Angular's injector resolves the declared types in a constructor and provides the correct instance. @Injectable({ providedIn: 'root' }) registers the service as a singleton in the root injector.",
        "q2": "DI makes Angular components testable and loosely coupled. In a component test, provide a mock service instead of the real one using TestBed.overrideProvider(). A component declares constructor(private orderService: OrderService) and Angular's injector automatically provides the singleton — no new OrderService() needed.",
        "q3": "Forgetting @Injectable on a service causes Angular to fail when it tries to inject it. Providing the same service at both the root and component level creates two instances, causing state inconsistency. Circular dependencies (ServiceA injects ServiceB, ServiceB injects ServiceA) cause a circular dependency error at runtime.",
        "b1": "Ask: Where should this service be provided — root (global singleton) or component (scoped instance)? How will it be mocked in tests? Does it have any dependencies that also need to be injected? Are there any circular dependency risks? Should the service be lazy-loaded (provided in a lazy-loaded module)?"
    },
    67: {
        "q1": "Angular routing maps URL paths to components using a Routes array. RouterLink navigates declaratively (<a routerLink='/orders'>), Router.navigate() navigates programmatically. ActivatedRoute provides route params (:id) and query params (?status=active). Route guards (CanActivate) protect routes. Lazy loading loads modules on demand.",
        "q2": "Routing defines the navigation structure of the Angular SPA. Each page is a route: /dashboard maps to DashboardComponent, /orders/:id maps to OrderDetailComponent. Spring Boot's SPA controller must forward all non-API paths to index.html so Angular's router handles them. Without this, refreshing /orders/123 returns 404 from the server.",
        "q3": "Forgetting to add new Angular routes to Spring Boot's SpaController causes 404 on browser refresh or direct URL access. Not using routerLinkActive to highlight the current nav item confuses users. Not reading route params in ngOnInit (only in the constructor) causes the component to not react to parameter changes when navigating from one detail page to another.",
        "b1": "Ask: What URL structure best represents this resource? Should the route ID be in the path (/orders/123) or a query param (/orders?id=123)? Does this route need a guard (CanActivate for auth)? Does it need a resolver (CanDeactivate for unsaved changes)? Is this module large enough to warrant lazy loading? Does the server need updating to handle this new route?"
    },
    68: {
        "q1": "Reactive Forms in Angular are driven by TypeScript: FormControl (single input), FormGroup (group of controls), and FormArray (dynamic list). FormBuilder simplifies creation. Subscribe to .valueChanges Observable for real-time validation. Add validators (Validators.required, Validators.email) in the TypeScript class, not HTML.",
        "q2": "Reactive forms are used in Spring Boot integration for complex Angular forms: a multi-field order form with cross-field validation (delivery date must be after order date), dynamic address fields (FormArray for multiple addresses), and programmatic population of form values from an API response (form.patchValue(order)).",
        "q3": "Not calling form.patchValue() or form.setValue() when loading data for an edit form leaves the form empty. Accessing form.value before the user submits captures partially filled data — always use form.valid to check first. Not disabling the submit button when the form is invalid allows submission of invalid data and confusing validation messages.",
        "b1": "Ask: Does the form have complex cross-field validation? Does the form need to be built dynamically (FormArray)? Does it need to be pre-populated from an API call? Is programmatic control (disable fields, reset, patch values) needed? How will validation errors be displayed for each field? Should the submit button be disabled when the form is invalid?"
    },
    69: {
        "q1": "Template-driven forms use HTML directives: ngForm, ngModel, and ngModelGroup. Angular automatically creates a FormControl for each input with ngModel. Validation uses HTML5 attributes (required, minlength, email) or Angular validators as directives. Access the form's validity with #myForm='ngForm' template reference variable.",
        "q2": "Template-driven forms are suitable for simple Angular forms with minimal logic: a login form with email and password, a simple search input, or a contact form. They're faster to set up for straightforward cases but harder to unit test and less flexible than reactive forms for complex, dynamic validation.",
        "q3": "Template-driven forms are difficult to unit test because the FormControl instances are created by Angular in the template, not in TypeScript. Two-way binding [(ngModel)] on complex nested objects causes deep mutability that's hard to track. Template-driven forms don't support dynamic form fields well — use reactive forms for FormArray patterns.",
        "b1": "Ask: Is this form simple with 3-5 fields and straightforward validation (use template-driven)? Or does it have complex cross-field validation, dynamic fields, or needs to be driven by API data (use reactive)? Does this form need unit tests? How will validation error messages be displayed? Is there existing Angular project convention to follow?"
    },
    70: {
        "q1": "Angular's HttpClient sends HTTP requests to the Spring Boot backend and returns Observables. Inject it into a service: constructor(private http: HttpClient). Make requests: http.get<T>(url), http.post<T>(url, body), http.put<T>(url, body), http.delete<T>(url). Use .pipe(map(), catchError()) to transform responses and handle errors.",
        "q2": "HttpClient is the connector between Angular and Spring Boot in a full-stack application. Every API call (load orders, submit form, delete record) goes through HttpClient. The response Observable is either subscribed to in the service or returned to the component that subscribes with the async pipe.",
        "q3": "Not including HttpClientModule (or provideHttpClient()) in the app config causes a NullInjectorError. Not handling errors with catchError causes unhandled Observable errors that crash the subscription silently. Not unsubscribing from HTTP Observables (though they complete automatically, open subscriptions from retry or interval operators can leak).",
        "b1": "Ask: What is the base URL for the backend API? Should the service handle error mapping or return the raw error? Should HTTP headers (auth token, Content-Type) be added in the service or an interceptor? How should the loading state be managed — in the service or the component? Should responses be cached (shareReplay)?"
    },
    71: {
        "q1": "RxJS (Reactive Extensions for JavaScript) is a library for async and event-based programming using Observables. Key operators: map (transform), filter (select), switchMap (cancel previous, use latest), mergeMap (handle all), debounceTime (delay), distinctUntilChanged (skip duplicates), combineLatest (join multiple streams), and catchError (handle errors).",
        "q2": "RxJS operators are used throughout Angular: switchMap for HTTP calls that should cancel previous (search box), combineLatest to combine route params with service data, debounceTime on search input to avoid calling the API on every keystroke, and share to multicast a single HTTP call to multiple subscribers.",
        "q3": "Using switchMap when you should use mergeMap (or vice versa) causes either dropped requests or race conditions. Not catching errors in the pipe with catchError causes the Observable to terminate on the first error, leaving the UI in a broken loading state. Deep nesting of operators (callback hell) defeats the purpose of RxJS — use the pipe() pattern.",
        "b1": "Ask: Does this async operation cancel the previous one on a new trigger (use switchMap)? Should all async operations be processed in parallel (mergeMap)? Does the UI need to react to multiple async sources simultaneously (combineLatest)? Is debouncing needed to limit API calls from user input? Should errors terminate the stream or be recovered (catchError + return EMPTY)?"
    },
    72: {
        "q1": "An Observable represents a stream of values over time — zero, one, or many. Create with Observable.create(), of(), from(), or HttpClient methods. Subscribe with .subscribe({ next, error, complete }) or the async pipe in templates. Observables are lazy (nothing happens until subscribed) and can be disposed by unsubscribing.",
        "q2": "Observables are the core of Angular's async model. Every HttpClient request returns an Observable. Component lifecycle triggers can be modeled as Observables. The async pipe in templates subscribes and unsubscribes automatically. Understanding Observables is essential for every Angular developer working with Spring Boot APIs.",
        "q3": "Memory leaks from not unsubscribing are the most common Observable bug in Angular. Use takeUntil(this.destroy$) with ngOnDestroy, or use the async pipe. Calling subscribe() inside subscribe() (nested subscriptions) is an anti-pattern — use operators like switchMap instead. Hot Observables (Subjects) replay or not replay based on type — understand BehaviorSubject vs Subject.",
        "b1": "Ask: Is this a single-value Observable (HTTP response) or a multi-value stream (real-time events)? Does the component need to manage the subscription lifecycle manually or can the async pipe handle it? Should the Observable be shared between multiple subscribers (shareReplay)? Does the stream need to emit a default value before the first real value (BehaviorSubject)?"
    },
    73: {
        "q1": "A Subject is both an Observable (can be subscribed to) and an Observer (can emit values). BehaviorSubject holds the current value and emits it to new subscribers immediately. ReplaySubject replays the last N emissions to new subscribers. AsyncSubject emits only the last value when complete. Use Subjects for component-to-component communication.",
        "q2": "Subjects are used in Angular services to share state and events: a CartService uses BehaviorSubject<CartItem[]> to hold the cart contents and emit updates to all subscribed components. A loading service uses Subject<boolean> to broadcast loading state. BehaviorSubject is the standard choice for app state in services.",
        "q3": "Not calling .complete() on Subjects when the service is destroyed causes memory leaks. Exposing the Subject directly as a public property allows any component to emit values, breaking the single-source-of-truth principle — expose the Subject only as an Observable (asObservable()). Using Subject when BehaviorSubject is needed means new subscribers miss the current state.",
        "b1": "Ask: Should new subscribers receive the current value immediately (BehaviorSubject) or only future values (Subject)? Should the subject emit values from multiple places or only from one service (expose as Observable)? Does this need to complete and clean up? Is the state shared across the entire app (root-provided service) or local to a feature?"
    },
    74: {
        "q1": "Route Guards in Angular control navigation. CanActivate prevents navigating to a route if the user doesn't meet conditions (not logged in). CanDeactivate prevents navigating away from a route (unsaved form changes). Guards are classes or functions that return boolean, UrlTree, or Observable<boolean>. Register them in the route definition.",
        "q2": "Guards are essential for security in Angular applications. An AuthGuard checks if a JWT token is present and valid before allowing access to /dashboard. An UnsavedChangesGuard prevents users from accidentally losing form data. Guards work together with Spring Boot's JWT validation — Angular guards prevent the user from even reaching the page.",
        "q3": "Angular guards are client-side only and can be bypassed — always validate authorization on the Spring Boot backend too. Not redirecting to the login page (returning UrlTree to /login) when a guard fails leaves the user on a blank route. Guards that make HTTP calls must return an Observable<boolean> and handle errors — returning false is not enough.",
        "b1": "Ask: Which routes require the user to be authenticated? Which routes require specific roles? Is there a guard for preventing navigation away from unsaved changes? Does the guard need to make an HTTP call to verify permissions? What should happen when the guard fails — redirect to login or show an unauthorized page? Is the check also enforced on the backend?"
    },
    75: {
        "q1": "Angular HTTP Interceptors intercept all HttpClient requests and responses, allowing you to add headers, handle errors, or show loading indicators globally. Implement the HttpInterceptor interface with the intercept(req, next) method. Clone the request to add headers (e.g., Authorization: Bearer token) and use next.handle(modified_req) to continue.",
        "q2": "Interceptors eliminate repetitive code across services. A single AuthInterceptor adds the JWT token to every request, replacing manual header setting in each service method. A LoadingInterceptor shows a global spinner on every request. An ErrorInterceptor catches 401 responses and redirects to the login page.",
        "q3": "Cloning the request incorrectly (not using req.clone({ headers: ... })) sends the unmodified request without the added headers. Interceptors that don't call next.handle() block all HTTP requests. Adding the Authorization header to third-party API calls accidentally exposes the JWT token to external servers — check the URL before adding sensitive headers.",
        "b1": "Ask: Should this behavior apply to every HTTP request (use an interceptor) or only specific calls (add headers in the service)? Should the interceptor add auth headers only for backend API calls? How does the interceptor handle 401 responses — refresh token or redirect to login? Should a loading spinner be tied to HTTP request lifecycle?"
    },
    76: {
        "q1": "Angular authentication typically uses JWT: the login form calls the auth API, receives a JWT, stores it in localStorage or memory, and the HttpInterceptor adds it to all subsequent requests. An AuthGuard checks token presence and validity for protected routes. On logout, clear the token and navigate to the login page.",
        "q2": "Authentication connects Angular to Spring Boot's Spring Security: the Angular login form calls POST /api/auth/login, Spring Boot validates credentials and returns a JWT, the Angular app stores it, and every subsequent API call includes it in the Authorization header for Spring Security's JWT filter to validate.",
        "q3": "Storing JWT in localStorage exposes it to XSS — prefer HttpOnly cookies for production. Not checking token expiry (exp claim) before making API calls leads to 401 errors that surprise the user — check expiry and refresh before the call. Keeping the token after logout (not clearing localStorage) allows others to reuse the session on a shared computer.",
        "b1": "Ask: Where should the JWT be stored (localStorage vs memory vs HttpOnly cookie)? How long should the session last before re-authentication is required? Is a token refresh mechanism needed? How does the Angular app detect that the token has expired — an interceptor catching 401? What should the UI show while checking authentication status on startup?"
    },
    77: {
        "q1": "State management organizes shared application state so multiple Angular components can read and update it consistently. Simple: a service with BehaviorSubject. Moderate: NgRx with Store (single source of truth), Actions (events), Reducers (pure state transitions), Selectors (computed views), and Effects (async side effects like HTTP). Choose complexity based on app scale.",
        "q2": "State management becomes essential in large Angular applications with Spring Boot backends: a shopping cart shared across many components, user authentication state needed everywhere, or loading states that multiple components must react to. Without state management, duplicated local state causes UI inconsistency.",
        "q3": "Over-engineering small apps with NgRx adds boilerplate without benefit — use a service with BehaviorSubject for simple shared state. Mutating NgRx state directly in a component (instead of dispatching actions) breaks the Redux pattern and makes time-travel debugging and state history useless. Storing everything in global state (including UI-only state) makes the store a mess.",
        "b1": "Ask: Is this state shared across many components or just within a feature (local state is fine)? How complex are the state transitions — simple set/clear, or complex conditional logic? Does async data fetching need to be coordinated with state changes (NgRx Effects)? Does the team have NgRx experience? Is time-travel debugging or state history needed?"
    },
    78: {
        "q1": "Angular performance optimizations: OnPush change detection (component only re-checks when @Input references change, not on every app-wide tick), trackBy in @for (prevents DOM re-creation when list data changes), lazy loading (load feature modules only when needed), avoid heavy computations in templates (move to pure pipes or component methods), and preloading strategies.",
        "q2": "Performance matters when Angular apps grow. A dashboard fetching large lists from Spring Boot APIs needs virtual scrolling for long lists, OnPush to prevent unnecessary re-renders, and lazy loading so the initial bundle doesn't include all modules. Poor performance directly impacts user experience and perceived API speed.",
        "q3": "Not using trackBy in @for loops causes Angular to destroy and recreate all DOM nodes when the list data reference changes (even if items are the same). Using ChangeDetectionStrategy.OnPush without properly triggering change detection (using ChangeDetectorRef.markForCheck()) causes the view to not update when state changes. Large bundles from eager-loading all modules slow the initial page load.",
        "b1": "Ask: Is the app experiencing slow rendering? Are large lists being rendered without virtual scrolling? Is the initial bundle too large (check with ng build --stats-json)? Are there unnecessary API calls due to missing debouncing? Which components would benefit from OnPush? Where can pure pipes replace method calls in templates?"
    },
    79: {
        "q1": "Lazy loading in Angular loads feature module JavaScript bundles only when the user navigates to that feature's route, reducing the initial app bundle size. Configure with loadChildren: () => import('./admin/admin.module').then(m => m.AdminModule) in the route definition. Standalone components use loadComponent() instead.",
        "q2": "Lazy loading is critical for large Angular applications with Spring Boot backends. An admin module, a reporting module, and a settings module are rarely visited — lazy loading them means users who never access admin don't download that code. Faster initial load improves perceived performance and user retention.",
        "q3": "Forgetting to add lazy-loaded routes to Spring Boot's SpaController causes 404 on direct URL access or refresh. Not configuring a PreloadingStrategy means lazy modules are only loaded on first visit — users experience a delay. Putting too much in one lazy module (a 'mega-module') defeats the purpose — split by feature with clear boundaries.",
        "b1": "Ask: Which features are visited infrequently (good candidates for lazy loading)? How large are the current bundles? Should preloading be enabled so lazy modules load in the background after initial load? Does the lazy module need its own providers or routing? Does the Spring Boot SpaController need updating to serve the new routes?"
    },
    80: {
        "q1": "Angular testing uses Jasmine for test suites (describe/it/expect) and Karma as the test runner. TestBed configures a testing Angular module. ComponentFixture provides access to the component instance and DOM. Use spyOn and jasmine.createSpyObj to mock services. For E2E tests, Cypress tests full user flows in a browser.",
        "q2": "Testing Angular components verifies that templates render correctly based on component state, that user interactions trigger the right methods, and that service calls produce the expected UI changes. Integration with Spring Boot APIs is tested by mocking HTTP calls with HttpClientTestingModule and HttpTestingController.",
        "q3": "Not calling fixture.detectChanges() after setting component properties means the template doesn't update and assertions on the DOM fail. Testing with the real service instead of a spy makes component tests dependent on backend availability. Over-testing implementation details (which method was called) instead of user-visible behavior makes tests brittle.",
        "b1": "Ask: What user-visible behavior needs to be verified? What services need to be mocked? Should the test verify the template output or the component method behavior? How will async operations (HTTP calls, timers) be handled in the test? Is there a need for E2E tests with Cypress for critical user flows? How will this test run in CI/CD?"
    },
    81: {
        "q1": "Java Mock Interviews combine all Java fundamentals: OOP, Collections, Streams, Exception Handling, Generics, String manipulation, multithreading basics, and Java 8+ features. Practice answering each question with a definition, real project example, internal working, common mistake, and business impact — in under 2 minutes without notes.",
        "q2": "In a real interview, Java questions test your depth of understanding: 'Why is String immutable?' tests JVM internals; 'When would you use LinkedList over ArrayList?' tests performance reasoning; 'How does HashMap handle collisions?' tests data structure knowledge. Connecting answers to real project experience separates average from strong candidates.",
        "q3": "Memorized definitions without examples sound rehearsed and fail follow-up questions. Not connecting Java concepts to Spring Boot or real projects misses the 'so what?' that interviewers look for. Confusing Java 8 Stream operations (lazy vs eager) or Optional semantics in a live coding exercise shows surface-level knowledge.",
        "b1": "Ask: Can I explain JVM memory model and garbage collection without notes? Can I write a custom Comparator and use it with Stream.sorted() live? Can I explain what happens when two equal HashMap keys are inserted? Can I explain the difference between Comparable and Comparator with a real example? Have I practiced these answers aloud until they sound natural?"
    },
    82: {
        "q1": "Spring Boot Mock Interviews test: REST API design (URLs, methods, status codes), Bean lifecycle and scopes, dependency injection, JPA/Hibernate (entities, relationships, N+1 problem), transactions, exception handling with @ControllerAdvice, Spring Security with JWT, validation with @Valid, logging, and testing with MockMvc.",
        "q2": "Interviewers ask Spring Boot questions to verify that you can design and implement production-quality APIs. 'How would you handle a 404 for a missing order?' tests exception handling. 'What is the N+1 problem and how do you fix it?' tests JPA knowledge. 'How does @Transactional work?' tests transaction understanding.",
        "q3": "Explaining Spring Boot features without connecting them to why they exist (what problem they solve) sounds memorized. Not knowing how Spring Boot auto-configuration works or what happens during context startup shows surface-level knowledge. Confusing @Component, @Service, @Repository, and @Controller (they all create beans, but the semantic and proxy behavior differ) suggests incomplete understanding.",
        "b1": "Ask: Can I draw the full request lifecycle from HTTP request to database and back? Can I explain how @Transactional works and when it does NOT work? Can I design a complete REST API for an order management system with proper DTOs, validation, exception handling, and security? Have I practiced these with a timer?"
    },
    83: {
        "q1": "Angular Mock Interviews test: Component lifecycle (ngOnInit, ngOnDestroy), change detection (Default vs OnPush), data binding (@Input, @Output, two-way), services and DI, routing (params, guards), reactive forms, HTTP client, RxJS (switchMap, combineLatest, BehaviorSubject), lazy loading, and testing with TestBed.",
        "q2": "Angular interview questions verify that you can build and maintain complex SPAs. 'How does Angular change detection work?' tests framework internals. 'When would you use switchMap vs mergeMap?' tests RxJS understanding. 'How do you prevent memory leaks in Angular?' tests lifecycle management. Connecting answers to real app architecture is key.",
        "q3": "Not being able to explain the Angular change detection cycle (zones, OnPush) suggests a gap in understanding. Confusing template-driven and reactive forms without knowing when to use each is a common weakness. Not understanding the difference between Subject, BehaviorSubject, and ReplaySubject causes incorrect RxJS usage in interviews.",
        "b1": "Ask: Can I explain the full lifecycle of an Angular component from creation to destruction? Can I write an HTTP service with error handling, loading state, and BehaviorSubject for shared state? Can I implement a route guard that checks JWT validity? Can I explain OnPush change detection and when to use markForCheck()?"
    },
    84: {
        "q1": "SQL Mock Interviews test: SELECT with WHERE, GROUP BY, HAVING, ORDER BY, LIMIT; JOIN types (INNER, LEFT, RIGHT, FULL OUTER); subqueries and CTEs; aggregate functions (COUNT, SUM, AVG, MAX, MIN); window functions (ROW_NUMBER, RANK, LAG); indexes and query optimization; and translating business questions into correct SQL.",
        "q2": "SQL interview questions test whether you can retrieve the right data from a relational database efficiently. 'Find the top 5 customers by total order value' tests GROUP BY + ORDER BY + LIMIT. 'Find customers who have never placed an order' tests LEFT JOIN with WHERE IS NULL. Real business query translation is the most valuable interview skill.",
        "q3": "Writing SELECT * in interview queries signals poor practice — always specify columns. Not knowing the difference between WHERE (filter rows before grouping) and HAVING (filter groups after GROUP BY) causes incorrect query results. Confused about INNER vs LEFT JOIN (especially for 'find records with no match') is the most common SQL interview mistake.",
        "b1": "Ask: Can I write a SQL query to find the second highest salary without using a subquery? Can I explain what a query execution plan shows and when to add an index? Can I write a self-join to find employees who earn more than their manager? Can I write a CTE to find month-over-month revenue change? Have I practiced these on paper without running them?"
    },
    85: {
        "q1": "DSA Mock Interviews test core patterns: Two Pointers (two-sum, container with most water), Sliding Window (max sum subarray, longest substring), HashMap for fast lookups, Stack/Queue (valid parentheses, BFS), Binary Search (search in sorted array), Recursion/DFS (tree traversal, backtracking), and Dynamic Programming (climb stairs, coin change).",
        "q2": "DSA questions are live-coding problems under time pressure. The interview assesses how you think, not just whether you get the answer: state the approach before coding, mention time and space complexity, handle edge cases aloud, and write clean readable code. Practice Striver 75 problems until each pattern feels automatic.",
        "q3": "Jumping straight to code without stating the approach first signals poor problem-solving habits. Not stating time and space complexity is an automatic negative signal. Writing correct but O(n²) solutions when O(n) with a HashMap is possible shows pattern blindness. Not handling edge cases (empty input, single element, all duplicates) misses points even when the main logic is correct.",
        "b1": "Ask: Can I solve Two Sum in O(n) with a HashMap and explain why? Can I identify that 'maximum sum subarray' is a sliding window problem? Can I implement BFS for a tree level-order traversal? Can I explain the difference between recursion and dynamic programming? Have I timed myself solving Striver 75 problems and reviewed solutions I couldn't complete?"
    },
    86: {
        "q1": "A Full Stack Mini Project connects Angular frontend → Spring Boot REST API → JPA/Hibernate → relational database in a single working feature. Choose a focused domain (order management, task tracker, inventory). Design the entity, repository, service, controller, DTO, and Angular component all the way through. The goal is a complete, running application.",
        "q2": "The mini project demonstrates all skills: Angular makes HTTP calls to the Spring Boot API, the API validates inputs with @Valid, the service processes business logic with @Transactional, JPA saves to the database, and the response DTO is rendered in the Angular template. A working end-to-end feature is the best portfolio evidence.",
        "q3": "Building the backend and frontend separately without testing the integration until the end leads to incompatible API contracts. Not handling loading and error states in Angular makes the UI feel broken. Using a monolithic service method that does everything (validate + query + transform + notify) makes the code untestable and fragile.",
        "b1": "Ask: What is the single feature I will build end-to-end? What is the API contract (request/response JSON)? What is the database schema? What Angular components and services are needed? Have I handled loading, success, error, and empty states in the UI? Is validation done on both the Angular form and the Spring Boot service? Can I demo it live without notes?"
    },
    87: {
        "q1": "Resume questions ask you to explain your projects, technologies, and contributions clearly. Use the STAR format (Situation, Task, Action, Result) for each project story. Quantify impact where possible: 'reduced API response time from 2 seconds to 200ms using caching' is stronger than 'improved performance'. Be specific about YOUR contribution, not the team's.",
        "q2": "In a Java full-stack interview, resume questions test depth: 'You mentioned JPA — explain the N+1 problem you faced.' or 'You built a REST API — how did you handle authentication?'. Every item on your resume should have a 2-minute explanation covering the problem, your technical decision, and the outcome.",
        "q3": "Listing technologies you used but cannot explain in depth is a common resume mistake. Saying 'I worked on a project' without specifying your individual contribution raises doubts. Not preparing follow-up technical questions for each resume item means you'll be caught off guard in the interview.",
        "b1": "Ask: For each resume project, can I explain the architecture in 2 minutes? Can I explain why I chose specific technologies? Can I answer 'what was the hardest part?' What technical decision am I most proud of and why? What would I do differently now? What quantifiable impact did the project have?"
    },
    88: {
        "q1": "Behavioral questions assess how you handle real situations using the STAR format: Situation (context), Task (your responsibility), Action (specific steps you took), Result (measurable outcome). Common themes: handling conflict, learning from failure, working under pressure, leading without authority, and adapting to change.",
        "q2": "Behavioral questions are equally important as technical questions in full-stack interviews. 'Tell me about a time you delivered under a tight deadline' is answered with a specific story, not a generic answer. Strong stories demonstrate ownership, teamwork, problem-solving under pressure, and continuous learning — all valued in full-stack developers.",
        "q3": "Generic answers ('I always try my best') without specific stories are unconvincing and forgettable. Not preparing 5-7 diverse stories in advance means reusing the same story for every question, which is noticeable. Stories that blame teammates or the company for failures signal poor self-awareness — always reflect on your own role and learning.",
        "b1": "Ask: Do I have a specific story for: a conflict with a teammate, a technical failure I fixed, a time I learned a new technology quickly, a time I improved a process, and a time I explained a complex technical concept to a non-technical stakeholder? Are my stories under 2 minutes with clear results? Have I practiced them aloud?"
    },
    89: {
        "q1": "System Design basics cover: gathering functional and non-functional requirements, designing the high-level architecture (client, API layer, services, database, cache, CDN), choosing storage (SQL vs NoSQL), discussing scalability (horizontal scaling, load balancing), reliability (replication, failover), and key trade-offs (CAP theorem, consistency vs availability).",
        "q2": "For a full-stack Java developer, system design questions focus on designing REST API architectures: how would you design an order management system? The answer covers: Angular SPA → API Gateway → Spring Boot services → JPA → PostgreSQL, with Redis caching, Kafka for async events, and JWT for auth. Showing how all layers connect demonstrates senior thinking.",
        "q3": "Not clarifying requirements before designing leads to the wrong system. Jumping to solutions ('I'll use Kafka') without explaining why signals pattern-following without understanding. Not discussing trade-offs (SQL vs NoSQL, consistency vs availability) suggests a one-size-fits-all mindset. Ignoring scalability and failure modes in the design is a missed opportunity.",
        "b1": "Ask: What are the functional requirements (what must it do)? What are the non-functional requirements (scale, latency, availability)? What is the read-to-write ratio? Does consistency or availability matter more in failure scenarios? What is the expected data volume? How will the system be monitored? Can I draw this architecture in 5 minutes and explain each decision?"
    },
    90: {
        "q1": "Day 90 Final Assessment covers all 90 days: Java fundamentals, OOP, Collections, Java 8 (Streams, Lambda, Optional), Spring Boot (REST, JPA, Security, Testing), Angular (Components, Services, RxJS, Forms, Routing), SQL (SELECT, JOINs, GROUP BY), and DSA (key patterns). Treat it as a complete mock interview — no notes, structured answers, real-time explanation.",
        "q2": "The final assessment demonstrates readiness for a Java full-stack developer role. Strong performance means you can explain the full request lifecycle (Angular → Spring Boot → JPA → DB → response → Angular), design a complete feature from scratch, solve a DSA problem with explanation, and handle behavioral questions with specific STAR stories.",
        "q3": "Gaps identified in the final assessment point to which days to revisit. Not connecting concepts across layers (showing Java knowledge without connecting to Spring Boot, or Angular knowledge without connecting to REST APIs) suggests studying in silos rather than as a full-stack developer. Nervousness is normal — practice explaining aloud consistently builds confidence.",
        "b1": "Ask: Can I explain the complete request flow in a full-stack Java application without notes? Can I design a feature end-to-end (entity → API → Angular component)? Can I solve a medium DSA problem in 20 minutes while explaining my approach? Can I answer 3 behavioral questions with specific stories? Am I ready to apply for Java full-stack developer roles?"
    }
}

# Generic Q2, Q3 by category (topic-specific versions for key ones, generic for the rest)
# For most topics, we use topic-aware generic answers
# Q2: where does it appear in full stack
GENERIC_Q2_JAVA = "In a Spring Boot full-stack project, this Java concept forms part of the service and domain layer. Understanding it prevents production bugs that are hard to trace when unexpected behavior surfaces in API responses or data processing."
GENERIC_Q2_SPRINGBOOT = "This Spring Boot concept directly shapes how the backend API is built, configured, and secured. Angular depends on the API contract it defines, and production reliability depends on using it correctly."
GENERIC_Q2_ANGULAR = "This Angular concept is used in every interactive frontend feature that communicates with the Spring Boot backend. Incorrect usage causes UI inconsistencies, memory leaks, or failed API calls that are difficult to debug."
GENERIC_Q3_JAVA = "Misunderstanding this concept causes runtime errors, incorrect business logic, or performance degradation that often only surfaces under production load. The worst bugs are the silent ones — wrong results with no error."
GENERIC_Q3_SPRINGBOOT = "Misunderstanding this concept causes incorrect API behavior, security vulnerabilities, or data integrity issues in the Spring Boot backend. These bugs often affect multiple users and are discovered late in production."
GENERIC_Q3_ANGULAR = "Misunderstanding this concept causes memory leaks, broken UI states, or failed API calls in the Angular application. These bugs are hard to reproduce locally and often appear under specific user navigation patterns."

def get_q2(day_num, topic_answers):
    return topic_answers.get("q2", GENERIC_Q2_JAVA if day_num <= 40 else (GENERIC_Q2_SPRINGBOOT if day_num <= 60 else GENERIC_Q2_ANGULAR))

def get_q3(day_num, topic_answers):
    return topic_answers.get("q3", GENERIC_Q3_JAVA if day_num <= 40 else (GENERIC_Q3_SPRINGBOOT if day_num <= 60 else GENERIC_Q3_ANGULAR))


def build_written_model_answers(day_num, written_questions):
    ta = TOPIC_ANSWERS.get(day_num, {})
    answers = []
    for i, q in enumerate(written_questions):
        qi = i + 1
        if qi == 1:
            answers.append(ta.get("q1", f"This topic ({q[:40]}...) is a foundational concept. Define it clearly, give a simple real-world analogy, then explain the Java or framework-level detail. A strong answer has: definition → how it works → where it is used → common mistake."))
        elif qi == 2:
            answers.append(get_q2(day_num, ta))
        elif qi == 3:
            answers.append(get_q3(day_num, ta))
        elif qi == 4:
            answers.append(GENERIC["q4"])
        elif qi == 5:
            answers.append(GENERIC["q5"])
        elif qi == 6:
            answers.append(GENERIC["q6"])
        elif qi == 7:
            answers.append(GENERIC["q7"])
        elif qi == 8:
            answers.append(GENERIC["q8"])
        elif qi == 9:
            answers.append(GENERIC["q9"])
        elif qi == 10:
            answers.append(GENERIC["q10"])
        else:
            answers.append("Review today's notes carefully and write a structured answer: define, explain, example, production impact.")
    return answers


def build_business_model_answers(day_num, business_questions):
    ta = TOPIC_ANSWERS.get(day_num, {})
    answers = []
    for i, q in enumerate(business_questions):
        bi = i + 1
        if bi == 1:
            answers.append(ta.get("b1", "Ask: What is the scope of this feature? What data does it read or write? What are the validation rules? What should happen on error? Who are the users and what is the expected load? What does success look like from a business perspective?"))
        elif bi == 2:
            answers.append(GENERIC["b2"])
        elif bi == 3:
            answers.append(GENERIC["b3"])
        else:
            answers.append("Approach this scenario methodically: identify the business question, design the data query, define the API response, and explain the business value of the metric.")
    return answers


# Process all curriculum files
files = sorted(glob.glob(os.path.join(CURRICULUM_DIR, "day-*.json")))
print(f"Found {len(files)} curriculum files")

for f in files:
    with open(f) as fh:
        data = json.load(fh)

    # Extract day number from id or filename
    fname = os.path.basename(f)
    day_num = int(fname.replace("day-", "").replace(".json", ""))

    written_qs = data.get("writtenConceptQuestions", [])
    business_qs = data.get("businessScenarios", [])

    data["writtenModelAnswers"] = build_written_model_answers(day_num, written_qs)
    data["businessModelAnswers"] = build_business_model_answers(day_num, business_qs)

    with open(f, "w") as fh:
        json.dump(data, fh, indent=2)

    print(f"  day-{day_num:03d}: added {len(data['writtenModelAnswers'])} written + {len(data['businessModelAnswers'])} business answers")

print("Done!")
