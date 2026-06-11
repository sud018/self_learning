"""Rewrite days 38-45: Date API, Comparable, Comparator, Spring Boot core."""
import json, os
DATA_DIR = "backend/data/curriculum"

CURRICULUM = {

"day-038": {
"notes": """# Java Date/Time API (java.time): Complete Reference

## Why the New API?
`java.util.Date` and `Calendar` are mutable, confusing (month is 0-indexed), not thread-safe, and mix date/time/timezone concerns. `java.time` (JSR-310, Java 8) provides immutable, thread-safe types with clear naming.

## Core Types and Their Roles
```java
// LocalDate — date without time, without timezone
LocalDate today = LocalDate.now();
LocalDate birthday = LocalDate.of(1990, Month.JUNE, 15); // Month enum, no 0-indexing
LocalDate parsed = LocalDate.parse("2024-06-15"); // ISO-8601 default format

// LocalTime — time without date, without timezone
LocalTime now = LocalTime.now();
LocalTime meeting = LocalTime.of(14, 30, 0);  // 14:30:00
LocalTime end = meeting.plusHours(1).plusMinutes(30); // 16:00:00 (immutable — new object)

// LocalDateTime — date + time, without timezone
LocalDateTime dt = LocalDateTime.of(today, meeting);    // combine LocalDate + LocalTime
LocalDateTime fromStr = LocalDateTime.parse("2024-06-15T14:30:00");

// ZonedDateTime — date + time + timezone (use for user-facing times)
ZonedDateTime london = ZonedDateTime.now(ZoneId.of("Europe/London"));
ZonedDateTime utc    = ZonedDateTime.now(ZoneId.of("UTC"));
ZonedDateTime convertedToNY = london.withZoneSameInstant(ZoneId.of("America/New_York"));

// Instant — Unix timestamp (nanosecond precision, UTC-based machine time)
Instant now2 = Instant.now();
Instant fromEpoch = Instant.ofEpochSecond(1717344000L);
long epochMs = now2.toEpochMilli();
// Use Instant for database storage (UTC), ZonedDateTime for display
```

## Period and Duration
```java
// Period — date-based (years, months, days)
LocalDate start = LocalDate.of(2024, 1, 1);
LocalDate end   = LocalDate.of(2025, 3, 15);
Period period = Period.between(start, end);  // 1 year, 2 months, 14 days
period.getYears();   // 1
period.getMonths();  // 2
period.getDays();    // 14

// Duration — time-based (seconds, nanoseconds)
Instant t1 = Instant.now();
// ... operation ...
Instant t2 = Instant.now();
Duration elapsed = Duration.between(t1, t2);
elapsed.toMillis();      // milliseconds
elapsed.toSeconds();     // seconds
elapsed.toMinutes();     // minutes

// Useful factory methods
Duration oneHour = Duration.ofHours(1);
Period twoWeeks  = Period.ofWeeks(2);   // 14 days
```

## Date Arithmetic — Immutable Fluent API
```java
LocalDate d = LocalDate.of(2024, 6, 15);
d.plusDays(10)             // 2024-06-25
 .plusMonths(1)            // 2024-07-25
 .minusYears(1)            // 2023-07-25
 .with(DayOfWeek.MONDAY)   // adjust to that week's Monday
 .withDayOfMonth(1)        // first of the month

// TemporalAdjusters
LocalDate nextMonday = LocalDate.now().with(TemporalAdjusters.next(DayOfWeek.MONDAY));
LocalDate firstDayOfMonth = LocalDate.now().with(TemporalAdjusters.firstDayOfMonth());
LocalDate lastDayOfYear   = LocalDate.now().with(TemporalAdjusters.lastDayOfYear());
```

## DateTimeFormatter — Formatting and Parsing
```java
// Predefined formatters
DateTimeFormatter iso = DateTimeFormatter.ISO_LOCAL_DATE;        // "2024-06-15"
DateTimeFormatter isoTime = DateTimeFormatter.ISO_LOCAL_DATE_TIME; // "2024-06-15T14:30:00"

// Custom formatters — immutable, thread-safe (unlike SimpleDateFormat)
DateTimeFormatter custom = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm");
String formatted = LocalDateTime.now().format(custom); // "15/06/2024 14:30"
LocalDateTime parsed = LocalDateTime.parse("15/06/2024 14:30", custom);

// Locale-sensitive
DateTimeFormatter localeFormatter = DateTimeFormatter
    .ofLocalizedDate(FormatStyle.FULL)
    .withLocale(Locale.UK); // "Saturday, 15 June 2024"
```

## Java Time in Spring Boot / JPA
```java
// application.properties — configure Jackson to serialize java.time
spring.jackson.serialization.write-dates-as-timestamps=false
// Dependency: com.fasterxml.jackson.datatype:jackson-datatype-jsr310

// JPA — map Instant to TIMESTAMP column
@Column(name = "created_at")
private Instant createdAt;

@PrePersist
void prePersist() { this.createdAt = Instant.now(); }

// REST — Instant serializes as ISO-8601: "2024-06-15T14:30:00Z"
```

## Common Mistakes
1. **Using LocalDateTime for timezone-sensitive code:** A meeting at 14:00 London needs `ZonedDateTime` — LocalDateTime has no timezone and daylight saving shifts can shift the wrong time.
2. **Storing ZonedDateTime in DB:** Store `Instant` (UTC) in DB, convert to `ZonedDateTime` for display.
3. **SimpleDateFormat in multithreaded code:** not thread-safe. Use `DateTimeFormatter` which is immutable and thread-safe.
4. **Converting `Date` incorrectly:** `date.toInstant()` → `Instant` is correct. `new Date(localDate)` doesn't exist.
""",
"mcqs": [
  {"id":"d38q1","prompt":"What is the difference between LocalDateTime and ZonedDateTime?","options":["LocalDateTime has timezone; ZonedDateTime doesn't","LocalDateTime has no timezone — it cannot represent an unambiguous instant; ZonedDateTime includes timezone and can represent an exact instant","LocalDateTime is immutable; ZonedDateTime is mutable","They are identical in modern JVMs"],"correctAnswer":"LocalDateTime has no timezone — it cannot represent an unambiguous instant; ZonedDateTime includes timezone and can represent an exact instant","explanation":"'2024-06-15T14:30' in LocalDateTime is ambiguous — 14:30 where? ZonedDateTime adds ZoneId: '2024-06-15T14:30+01:00[Europe/London]' is unambiguous. For cross-timezone scheduling, always use ZonedDateTime."},
  {"id":"d38q2","prompt":"What is `Instant` and when should you use it?","options":["A snapshot of the stack trace","A UTC-based timestamp with nanosecond precision — use for machine timestamps, DB storage, and event sourcing where timezone is irrelevant","A timezone-aware date","A replacement for System.currentTimeMillis()"],"correctAnswer":"A UTC-based timestamp with nanosecond precision — use for machine timestamps, DB storage, and event sourcing where timezone is irrelevant","explanation":"Instant represents a point on the UTC timeline. Use for: createdAt/updatedAt DB columns, event sourcing timestamps, measuring elapsed time. Not for user-facing times (use ZonedDateTime). Instant.now().toEpochMilli() replaces System.currentTimeMillis() in typed code."},
  {"id":"d38q3","prompt":"What is the difference between Period and Duration?","options":["Identical","Period is date-based (years, months, days) for calendar calculations; Duration is time-based (seconds, nanos) for elapsed time measurement","Period is deprecated","Duration only works with Instant"],"correctAnswer":"Period is date-based (years, months, days) for calendar calculations; Duration is time-based (seconds, nanos) for elapsed time measurement","explanation":"Period.between(date1, date2) gives 1 year, 2 months, 14 days — uses calendar semantics. Duration.between(instant1, instant2) gives exact nanoseconds/seconds. Period.ofMonths(3) adds calendar months (variable days); Duration.ofDays(90) adds exact 90*24*60*60 seconds."},
  {"id":"d38q4","prompt":"Why is `DateTimeFormatter` preferred over `SimpleDateFormat`?","options":["DateTimeFormatter is faster","SimpleDateFormat is not thread-safe (shared instance causes data corruption in concurrent code); DateTimeFormatter is immutable and thread-safe","DateTimeFormatter supports more patterns","SimpleDateFormat doesn't support Java 8"],"correctAnswer":"SimpleDateFormat is not thread-safe (shared instance causes data corruption in concurrent code); DateTimeFormatter is immutable and thread-safe","explanation":"SimpleDateFormat keeps internal parse state as mutable fields — sharing one instance across threads causes wrong dates or exceptions. DateTimeFormatter is immutable — safe to share as a static final constant. Also: java.time types only work with DateTimeFormatter."},
  {"id":"d38q5","prompt":"What does `LocalDate.now().with(TemporalAdjusters.next(DayOfWeek.MONDAY))` return?","options":["Last Monday","Next Monday after today (or today if today is Monday?)","The nearest Monday","Monday of next month"],"correctAnswer":"Next Monday after today (or today if today is Monday?)","explanation":"TemporalAdjusters.next(MONDAY) returns the next Monday strictly after today. If today is Monday, it returns next week's Monday. Use nextOrSame(MONDAY) to include today if today is already Monday."},
  {"id":"d38q6","prompt":"In JPA, should you store `ZonedDateTime` or `Instant` as a created_at column?","options":["ZonedDateTime to preserve timezone","Instant — stores as UTC timestamp; retrieve and convert to ZonedDateTime for display. Storing timezone in DB column is complex and often unnecessary","Either — they serialize identically","LocalDateTime — timezone is the application's concern"],"correctAnswer":"Instant — stores as UTC timestamp; retrieve and convert to ZonedDateTime for display. Storing timezone in DB column is complex and often unnecessary","explanation":"DB TIMESTAMP/UTC stores UTC epoch. Map to Instant in JPA. When displaying to users, convert: instant.atZone(user.getTimezone()). Storing ZonedDateTime adds timezone complexity to the DB schema. Exception: if you need to preserve the original timezone (e.g., log when user set an alarm in their local time)."},
  {"id":"d38q7","prompt":"What Spring Boot property makes `Instant` serialize as '2024-06-15T14:30:00Z' instead of a number?","options":["spring.serialization.dates=iso","spring.jackson.serialization.write-dates-as-timestamps=false","spring.json.instant=iso8601","jackson.date-format=iso"],"correctAnswer":"spring.jackson.serialization.write-dates-as-timestamps=false","explanation":"By default, Jackson serializes Instant as a numeric epoch (1718460600.0). Setting write-dates-as-timestamps=false enables ISO-8601 string format. Also needs jackson-datatype-jsr310 on classpath (included with spring-boot-starter-web)."},
  {"id":"d38q8","prompt":"What does `Duration.between(t1, t2).toMinutes()` return for a 90-second gap?","options":["90","1 — integer division truncates to whole minutes","1.5","90.0"],"correctAnswer":"1 — integer division truncates to whole minutes","explanation":"Duration.toMinutes() returns long (whole minutes, truncated). 90 seconds = 1 minute 30 seconds → toMinutes() = 1. Use toSeconds() for exact seconds, or compute manually: duration.toSeconds() / 60.0 for fractional minutes."},
  {"id":"d38q9","prompt":"How do you convert a legacy `java.util.Date` to `java.time.Instant`?","options":["Instant.from(date)","date.toInstant()","LocalDate.from(date)","Instant.of(date.getTime())"],"correctAnswer":"date.toInstant()","explanation":"Date.toInstant() was added in Java 8 as a bridge. Then: instant.atZone(ZoneId.systemDefault()).toLocalDateTime() for LocalDateTime. For reverse: Date.from(instant)."},
  {"id":"d38q10","prompt":"What is wrong with `LocalDateTime.of(2024, 3, 10, 2, 30)` in New York?","options":["Nothing","In New York, March 10 2024 at 02:30 does not exist — daylight saving time 'springs forward' from 02:00 to 03:00, creating a gap. ZonedDateTime handles this.","LocalDateTime doesn't accept integer months","2024-03-10 is a holiday"],"correctAnswer":"In New York, March 10 2024 at 02:30 does not exist — daylight saving time 'springs forward' from 02:00 to 03:00, creating a gap. ZonedDateTime handles this.","explanation":"DST gaps: clocks jump from 01:59 to 03:00. LocalDateTime.of(2024, 3, 10, 2, 30) represents a local time that never existed in America/New_York. ZonedDateTime.of(localDt, ZoneId.of('America/New_York')) adjusts to the nearest valid time."}
],
"writtenConceptQuestions": [
  "Explain the four main java.time types: LocalDate, LocalTime, LocalDateTime, ZonedDateTime, and Instant. When do you use each?",
  "What is the difference between Period and Duration? Show a business example for each — calculating contract expiry vs measuring API response time.",
  "Show a complete DateTimeFormatter example: parse from a custom pattern, format for display, and convert between timezones.",
  "Why is SimpleDateFormat dangerous in a Spring Boot web application? Show the thread-safety bug and the DateTimeFormatter fix.",
  "Explain how to store and retrieve dates in JPA: Instant for DB storage, ZonedDateTime for display. Show the @PrePersist pattern.",
  "What are TemporalAdjusters? Show 3 practical examples: next business day, last day of month, first Monday of next month.",
  "How do you convert between legacy java.util.Date and java.time types? Show the bridge methods in both directions."
],
"businessScenarios": [
  "A subscription service shows contract expiry dates to users in their local timezone, but stores dates in a MySQL UTC column. Show the complete data flow: Instant in DB, ZonedDateTime conversion, ISO-8601 JSON response.",
  "A scheduler runs at 02:30 daily and fails twice a year in the US due to DST changes. Fix by using Instant-based scheduling and explain why LocalDateTime-based cron jobs have this problem.",
  "A reporting API returns `createdAt` as 1717344000000 (epoch millis). Client teams report it's confusing. Change the serialization to ISO-8601 string without changing the DB schema or storage format."
]
},

"day-039": {
"notes": """# Comparable: Natural Ordering, Contract Rules, and Usage in Collections

## The Comparable Interface
```java
public interface Comparable<T> {
    int compareTo(T other); // returns: negative if this < other, 0 if equal, positive if this > other
}
```
Classes implementing Comparable define their **natural order** — the default ordering used by sorting algorithms, TreeSet, TreeMap, and Collections.sort() without an explicit Comparator.

## Implementing compareTo Correctly
```java
public class Product implements Comparable<Product> {
    private final String name;
    private final BigDecimal price;
    private final int stockQuantity;

    @Override
    public int compareTo(Product other) {
        // Primary: order by price ascending
        int cmp = this.price.compareTo(other.price);
        if (cmp != 0) return cmp;
        // Secondary: by name alphabetically (tiebreaker)
        return this.name.compareTo(other.name);
    }
}

// Numeric comparison — avoid subtraction (overflow risk!)
// WRONG: return this.stockQuantity - other.stockQuantity; // overflow if negative
// CORRECT:
return Integer.compare(this.stockQuantity, other.stockQuantity); // safe for all values
```

## The compareTo Contract (Must Follow)
1. **Antisymmetry:** `x.compareTo(y)` must be negative when `y.compareTo(x)` is positive
2. **Transitivity:** if `x > y` and `y > z`, then `x > z`
3. **Reflexivity:** `x.compareTo(x) == 0`
4. **Strongly recommended — consistency with equals:** `x.compareTo(y) == 0` should imply `x.equals(y)`

```java
// VIOLATION: inconsistency with equals
BigDecimal a = new BigDecimal("1.0");
BigDecimal b = new BigDecimal("1.00");
a.compareTo(b); // 0 — equal by value
a.equals(b);    // false — different scale!
// This is why TreeSet<BigDecimal> and HashSet<BigDecimal> can hold different sizes for same set
```

## Natural Ordering in Collections
```java
// TreeSet uses compareTo() — maintains sorted order
TreeSet<Product> catalog = new TreeSet<>();
catalog.add(new Product("Laptop", new BigDecimal("999.99"), 5));
catalog.add(new Product("Mouse",  new BigDecimal("25.00"), 50));
catalog.add(new Product("Keyboard", new BigDecimal("75.00"), 20));
// Iteration order: Mouse(25.00) → Keyboard(75.00) → Laptop(999.99)

// TreeMap uses key.compareTo() for ordering
TreeMap<Product, String> inventory = new TreeMap<>(); // keys sorted by Product.compareTo()

// Collections.sort — uses compareTo when no Comparator provided
List<Product> products = new ArrayList<>(catalog);
Collections.sort(products); // sorts by natural order (price ascending, then name)
```

## Comparable with Generics — Bounded Type Parameters
```java
// Generic max method using Comparable constraint
public static <T extends Comparable<T>> T max(List<T> list) {
    if (list.isEmpty()) throw new IllegalArgumentException("Empty list");
    T max = list.get(0);
    for (T item : list) {
        if (item.compareTo(max) > 0) max = item;
    }
    return max;
}

// Works with any Comparable type:
max(List.of(3, 1, 4, 1, 5)); // Integer.compareTo() → 5
max(List.of("banana", "apple", "cherry")); // String.compareTo() → "cherry"
max(List.of(product1, product2)); // Product.compareTo() → most expensive
```

## Comparable vs Comparator — When to Use Which
| Aspect | Comparable | Comparator |
|---|---|---|
| Location | Defined IN the class | Defined OUTSIDE |
| Purpose | Natural (default) ordering | Alternate orderings |
| Method | `compareTo(T other)` | `compare(T o1, T o2)` |
| Collections | TreeSet/TreeMap default | Pass to TreeSet(cmp), Collections.sort(list, cmp) |
| Multiple orderings | One | Unlimited |

## Common Mistakes
1. **Integer subtraction for comparison:** `return a.id - b.id;` overflows when id values differ by more than `Integer.MAX_VALUE`. Use `Integer.compare(a.id, b.id)`.
2. **Null comparisons:** `compareTo(null)` should throw `NullPointerException` per the contract — not return 0 or -1.
3. **Not implementing equals consistently:** if `a.compareTo(b) == 0` but `!a.equals(b)`, TreeSet and TreeMap treat them as equal (uses compareTo for uniqueness), while HashSet treats them as different.
""",
"mcqs": [
  {"id":"d39q1","prompt":"What does `compareTo(T other)` return when `this` is greater than `other`?","options":["true","A positive integer","0","A negative integer"],"correctAnswer":"A positive integer","explanation":"compareTo contract: negative if this < other, 0 if equal, positive if this > other. The actual value doesn't matter (1 or 1000) — only the sign. Sorted collections and Arrays.sort() check only the sign."},
  {"id":"d39q2","prompt":"Why is `return this.id - other.id` dangerous as a compareTo implementation?","options":["Subtraction isn't allowed","Integer overflow: if this.id = Integer.MAX_VALUE and other.id = -1, the subtraction overflows to a negative number, reversing the comparison","id might be null","It doesn't satisfy antisymmetry"],"correctAnswer":"Integer overflow: if this.id = Integer.MAX_VALUE and other.id = -1, the subtraction overflows to a negative number, reversing the comparison","explanation":"For IDs in range [-2B, 2B], subtraction can overflow. Integer.MAX_VALUE - (-1) = Integer.MIN_VALUE (negative!). Always use Integer.compare(this.id, other.id) which handles all values safely."},
  {"id":"d39q3","prompt":"A class implements Comparable<T>. What collection maintains elements in natural order using compareTo?","options":["ArrayList","HashSet","TreeSet — elements sorted by compareTo, no duplicates (compareTo==0 considered duplicate)","LinkedList"],"correctAnswer":"TreeSet — elements sorted by compareTo, no duplicates (compareTo==0 considered duplicate)","explanation":"TreeSet uses the element's compareTo() to sort and determine uniqueness. If compareTo() returns 0 for two elements, TreeSet treats them as duplicates (one is not added), even if equals() returns false."},
  {"id":"d39q4","prompt":"What is the 'consistency with equals' recommendation for compareTo?","options":["compareTo must call equals internally","x.compareTo(y) == 0 should imply x.equals(y) and vice versa — if violated, behavior in SortedSets/Maps is surprising","equals must return 0 for consistency","They must be identical implementations"],"correctAnswer":"x.compareTo(y) == 0 should imply x.equals(y) and vice versa — if violated, behavior in SortedSets/Maps is surprising","explanation":"TreeSet uses compareTo for uniqueness. If compareTo says 0 but equals says false, TreeSet refuses the duplicate while HashSet accepts both. BigDecimal violates this: new BigDecimal('1.0') and '1.00' compareTo to 0 but equals() false."},
  {"id":"d39q5","prompt":"How do you add a multi-key sort in compareTo (primary: price, secondary: name)?","options":["Use two separate compareTo calls in a list","Compare by primary key; if result != 0 return it; otherwise compare by secondary key and return that result","Sort by name first, then price second","Multi-key sort requires Comparator, not Comparable"],"correctAnswer":"Compare by primary key; if result != 0 return it; otherwise compare by secondary key and return that result","explanation":"Multi-key: int cmp = primary.compareTo(otherPrimary); if (cmp != 0) return cmp; return secondary.compareTo(otherSecondary); Chain as many keys as needed. The first non-zero result determines order; 0 means equal on that key, try next."},
  {"id":"d39q6","prompt":"What does `Collections.sort(list)` require from list elements?","options":["Nothing — it sorts all lists","Elements must implement Comparable<T> — ClassCastException if they don't","Elements must implement Serializable","Elements must override hashCode()"],"correctAnswer":"Elements must implement Comparable<T> — ClassCastException if they don't","explanation":"Collections.sort(List<T>) requires T to extend Comparable<T>. If T doesn't implement Comparable, a ClassCastException is thrown at runtime. Collections.sort(list, comparator) does NOT require Comparable — the Comparator provides the ordering."},
  {"id":"d39q7","prompt":"What should `x.compareTo(null)` return according to the Comparable contract?","options":["0 — null is equal to nothing","Return -1 — null sorts before all values","Throw NullPointerException — specified by the Comparable contract","Return Integer.MIN_VALUE"],"correctAnswer":"Throw NullPointerException — specified by the Comparable contract","explanation":"Javadoc for Comparable: 'Note that null is not an instance of any class, and e.compareTo(null) should throw a NullPointerException even though e.equals(null) returns false.' Unlike Comparator.nullsFirst/Last, Comparable itself doesn't handle null."},
  {"id":"d39q8","prompt":"A Product implements Comparable<Product> by price. Two Products with the same price but different names are added to a TreeSet. How many elements does the TreeSet contain?","options":["2 — because they have different names","1 — TreeSet uses compareTo for uniqueness; if compareTo returns 0, the second is treated as a duplicate","Depends on hashCode","TreeSet throws an exception for equal elements"],"correctAnswer":"1 — TreeSet uses compareTo for uniqueness; if compareTo returns 0, the second is treated as a duplicate","explanation":"TreeSet doesn't use equals() for uniqueness — it uses compareTo(). If compareTo() returns 0 for two objects, TreeSet treats them as the same element. For Products with the same price but different names, if compareTo only uses price, TreeSet accepts only one. Fix: add name as a secondary key in compareTo."},
  {"id":"d39q9","prompt":"What is the generic constraint `<T extends Comparable<T>>` used for?","options":["T must be a subtype of Comparable but not Comparable itself","T must implement Comparable<T> — guarantees compareTo(T) is available, enabling generic sorting and max/min algorithms","T must extend java.lang.Object","Compile-time type erasure prevention"],"correctAnswer":"T must implement Comparable<T> — guarantees compareTo(T) is available, enabling generic sorting and max/min algorithms","explanation":"<T extends Comparable<T>> bounds T to types that can compare to themselves. This enables writing generic algorithms: public <T extends Comparable<T>> T max(List<T> list) that works for Integer, String, or any Comparable class."},
  {"id":"d39q10","prompt":"When does Comparable give more accurate results than Comparator in a TreeMap?","options":["Never — they are equivalent","When the class's natural order (compareTo) perfectly matches the TreeMap's lookup requirement — using a different Comparator in TreeMap creates a tree where compareTo=0 elements are treated differently than Comparator=0 elements","When elements are primitives","When the TreeMap has more than 1000 entries"],"correctAnswer":"When the class's natural order (compareTo) perfectly matches the TreeMap's lookup requirement — using a different Comparator in TreeMap creates a tree where compareTo=0 elements are treated differently than Comparator=0 elements","explanation":"TreeMap uses the Comparator (if provided) or compareTo (if not) for BOTH sorting AND lookups. If you add with one ordering and lookup with another, you may not find elements. Consistency between Comparable, Comparator, and equals matters for correct Map/Set behaviour."}
],
"writtenConceptQuestions": [
  "Explain the Comparable contract: antisymmetry, transitivity, reflexivity, and consistency with equals. Show a BigDecimal example that violates consistency with equals.",
  "Implement Comparable<Employee> with natural order: primary sort by department, secondary by salary descending, tertiary by name.",
  "Why is integer subtraction dangerous in compareTo? Show the overflow scenario and the safe Integer.compare() alternative.",
  "What is the difference between Comparable and Comparator in terms of purpose and placement? When would you use each?",
  "Show how TreeSet uses compareTo for uniqueness. Show a bug where Products with the same price but different names get de-duplicated, and the fix.",
  "Write a generic method `<T extends Comparable<T>> List<T> topN(List<T> items, int n)` that returns the top N items in natural order.",
  "Explain `compareTo(null)` behaviour per the Comparable contract. How does this differ from Comparator.nullsFirst()?"
],
"businessScenarios": [
  "A Product catalog uses a TreeSet<Product> with Comparable by price only. Adding two different products at the same price loses one. Business rule: same price → sort alphabetically by name. Fix the compareTo to use price then name.",
  "An event scheduling system sorts Event objects by startTime using `startTime.getTime() - other.startTime.getTime()`. Events with timestamps > 68 years apart sort incorrectly due to overflow. Fix with Long.compare().",
  "A leaderboard stores players in a TreeMap<Player, Score>. Players are found by email but sorted by rank. Show how inconsistent Comparable (rank) and equals (email) breaks TreeMap.get() and how to fix it."
]
},

"day-040": {
"notes": """# Comparator: Chaining, Lambda Comparators, and Custom Ordering

## Creating Comparators with Comparator.comparing()
```java
// Comparator.comparing(keyExtractor) — most common pattern
Comparator<Order> byTotal = Comparator.comparing(Order::getTotal);
Comparator<String> byLength = Comparator.comparingInt(String::length);
Comparator<Employee> bySalary = Comparator.comparingDouble(Employee::getSalary);

// Chaining with thenComparing — multi-key sort
Comparator<Employee> byDeptThenSalaryDesc = Comparator
    .comparing(Employee::getDepartment)                // primary: dept alphabetically
    .thenComparing(Comparator.comparingDouble(Employee::getSalary).reversed()) // secondary: salary descending
    .thenComparing(Employee::getName);                 // tertiary: name alphabetically

List<Employee> sorted = employees.stream()
    .sorted(byDeptThenSalaryDesc)
    .collect(toList());
```

## reversed(), naturalOrder(), reverseOrder()
```java
// reversed — flips an existing Comparator
Comparator<Order> byTotalDesc = Comparator.comparing(Order::getTotal).reversed();

// naturalOrder — uses Comparable.compareTo()
Comparator<String> natural = Comparator.naturalOrder();  // A < B < C...
List<String> names = List.of("Charlie", "Alice", "Bob");
names.stream().sorted(Comparator.naturalOrder()).collect(toList()); // [Alice, Bob, Charlie]

// reverseOrder — reverse of natural order
names.stream().sorted(Comparator.reverseOrder()).collect(toList()); // [Charlie, Bob, Alice]
```

## Null-Safe Comparators
```java
// nullsFirst — null elements sort before non-null
Comparator<Order> byTotalNullFirst = Comparator.nullsFirst(
    Comparator.comparing(Order::getTotal)
);

// nullsLast — null elements sort after non-null
Comparator<String> byNameNullLast = Comparator.nullsLast(
    Comparator.naturalOrder()
);

List<String> withNulls = Arrays.asList("Alice", null, "Bob", null, "Charlie");
withNulls.sort(Comparator.nullsFirst(Comparator.naturalOrder()));
// Result: [null, null, Alice, Bob, Charlie]
```

## Using Comparators in Collections
```java
// TreeSet/TreeMap with custom Comparator
TreeSet<Order> ordersByTotal = new TreeSet<>(Comparator.comparing(Order::getTotal));
TreeMap<String, Order> byCustomerName = new TreeMap<>(Comparator.reverseOrder());

// PriorityQueue — min-heap by default (natural order), max-heap with reversed()
PriorityQueue<Order> smallestFirst = new PriorityQueue<>(Comparator.comparing(Order::getTotal));
PriorityQueue<Order> largestFirst  = new PriorityQueue<>(Comparator.comparing(Order::getTotal).reversed());
```

## Comparator as Lambda — When compareTo is Not Enough
```java
// Custom sort by string length then alphabetically
Comparator<String> byLengthThenAlpha = (s1, s2) -> {
    int cmp = Integer.compare(s1.length(), s2.length());
    return cmp != 0 ? cmp : s1.compareTo(s2);
};

// Comparator on a derived property
Comparator<Product> byTagCount = Comparator.comparingInt(p -> p.getTags().size());

// Comparator with Enum order
Comparator<Order> byStatusPriority = Comparator.comparingInt(
    o -> statusPriority.getOrDefault(o.getStatus(), 99)
);
Map<OrderStatus, Integer> statusPriority = Map.of(
    OrderStatus.URGENT, 0, OrderStatus.PROCESSING, 1, OrderStatus.COMPLETE, 2
);
```

## Comparator in Spring Boot — Sorting Service Results
```java
@Service
public class ProductService {
    // Sorting strategy pattern — caller chooses sort
    public List<ProductDto> findAll(String sortBy) {
        List<Product> products = productRepo.findAll();
        Comparator<Product> comparator = switch (sortBy) {
            case "price"    -> Comparator.comparing(Product::getPrice);
            case "name"     -> Comparator.comparing(Product::getName);
            case "newest"   -> Comparator.comparing(Product::getCreatedAt).reversed();
            case "popular"  -> Comparator.comparingInt(Product::getSalesCount).reversed();
            default         -> Comparator.comparing(Product::getName);
        };
        return products.stream()
            .sorted(comparator)
            .map(mapper::toDto)
            .collect(toList());
    }
}
```

## Comparator Composition — Readable Complex Sorts
```java
// A single readable comparator for a complex sort
Comparator<Product> catalogSort = Comparator
    .comparing(Product::getCategory)
    .thenComparing(Comparator.comparingInt(Product::getStockCount).reversed()) // in-stock first
    .thenComparing(Product::getPrice)
    .thenComparing(Product::getName);
```
""",
"mcqs": [
  {"id":"d40q1","prompt":"What does `Comparator.comparing(Order::getTotal).reversed()` do?","options":["Compares by negative total","Creates a Comparator that sorts Orders from highest total to lowest","Compares in natural order then reverses","reversed() only works with primitives"],"correctAnswer":"Creates a Comparator that sorts Orders from highest total to lowest","explanation":"Comparator.comparing(Order::getTotal) creates an ascending comparator. .reversed() wraps it, flipping the comparison result (positive↔negative). Result: largest total first."},
  {"id":"d40q2","prompt":"What is `thenComparing()` used for?","options":["Running a second sort on a separate list","Adding a secondary (tiebreaker) sort key that applies when the primary comparator returns 0","Combining two Comparators with OR logic","Sorting in reverse"],"correctAnswer":"Adding a secondary (tiebreaker) sort key that applies when the primary comparator returns 0","explanation":"thenComparing creates a composed Comparator: if the primary returns 0 (equal on primary key), the secondary comparator is used. Chains any number of keys: .comparing(A).thenComparing(B).thenComparing(C)."},
  {"id":"d40q3","prompt":"What does `Comparator.nullsFirst(Comparator.naturalOrder())` do with a list containing null elements?","options":["Throws NullPointerException","Sorts null elements before all non-null elements in natural order","Sorts null elements after non-null","Removes null elements"],"correctAnswer":"Sorts null elements before all non-null elements in natural order","explanation":"nullsFirst wraps any Comparator and treats null as less than all non-null values. nullsLast treats null as greater. Without this, sorting a list with nulls throws NullPointerException at the comparison step."},
  {"id":"d40q4","prompt":"How do you create a `PriorityQueue<Order>` that always returns the highest-total order first?","options":["new PriorityQueue<>(Collections.reverseOrder())","new PriorityQueue<>(Comparator.comparing(Order::getTotal).reversed()) — max-heap by total","new PriorityQueue<>() with Comparable implemented","PriorityQueue sorts by insertion order"],"correctAnswer":"new PriorityQueue<>(Comparator.comparing(Order::getTotal).reversed()) — max-heap by total","explanation":"PriorityQueue is a min-heap by default (smallest element at head). To make it a max-heap, provide a reversed comparator. The comparator defines what 'first' means: here, highest total is 'smallest' in the reversed comparator, so it's at the head."},
  {"id":"d40q5","prompt":"What is the difference between `Comparator.naturalOrder()` and Comparable?","options":["naturalOrder is for Comparables","naturalOrder() creates a Comparator that delegates to compareTo() — useful when you need a Comparator object but want natural ordering","They are identical","naturalOrder creates an immutable Comparator"],"correctAnswer":"naturalOrder() creates a Comparator that delegates to compareTo() — useful when you need a Comparator object but want natural ordering","explanation":"Some APIs require a Comparator object (TreeSet(Comparator), Collections.sort(list, comparator)). naturalOrder() gives you a Comparator that calls compareTo(). Without it, you'd have to pass null (some APIs interpret null as natural order) or write (a,b) -> a.compareTo(b)."},
  {"id":"d40q6","prompt":"What does `Comparator.comparingInt(Product::getStockCount).reversed()` do inside a product sort chain?","options":["Sorts by stock ascending","Sorts by stock count with highest stock first — in-stock products appear before low-stock products","Filters products with zero stock","reversed() doesn't work with comparingInt"],"correctAnswer":"Sorts by stock count with highest stock first — in-stock products appear before low-stock products","explanation":"comparingInt extracts an int key and creates a Comparator. reversed() flips to descending. Result: products with 100 stock sort before products with 5 stock. Useful for a catalog where availability matters."},
  {"id":"d40q7","prompt":"A `switch` on sortBy string creates a Comparator dynamically. What design pattern is this?","options":["Singleton","Strategy Pattern — the sorting algorithm is selected at runtime based on a parameter","Factory Pattern","Observer Pattern"],"correctAnswer":"Strategy Pattern — the sorting algorithm is selected at runtime based on a parameter","explanation":"Strategy pattern: an algorithm (sorting behaviour) is encapsulated in an object (Comparator) and selected at runtime. The service doesn't hard-code the sort; the caller (or query param) determines which Comparator to use."},
  {"id":"d40q8","prompt":"What happens if you add two elements where the Comparator returns 0 to a TreeSet?","options":["Both are stored","Only the first is stored — TreeSet uses the Comparator for uniqueness, not equals()","TreeSet throws IllegalStateException","The second replaces the first"],"correctAnswer":"Only the first is stored — TreeSet uses the Comparator for uniqueness, not equals()","explanation":"TreeSet (and TreeMap keys) use the Comparator for both ordering AND uniqueness. If comparator.compare(a, b) == 0, they are considered duplicates. This can conflict with equals() — two distinct objects that sort to the same position cannot both be in the TreeSet."},
  {"id":"d40q9","prompt":"What does `.thenComparing(Comparator.comparing(Employee::getSalary).reversed())` achieve in a chain?","options":["Sorts by name reversed","Applies a descending salary sort as a secondary key — higher salary ranks first within the same primary key","Compares salary and then reverses the entire chain","reversed() negates all comparisons"],"correctAnswer":"Applies a descending salary sort as a secondary key — higher salary ranks first within the same primary key","explanation":"Wrapping reversed() inside thenComparing is correct: the secondary key (salary) is sorted descending independently. Without wrapping: .thenComparing(Employee::getSalary).reversed() would reverse the ENTIRE comparison chain, not just salary."},
  {"id":"d40q10","prompt":"What does `Comparator.comparingInt(o -> statusPriority.getOrDefault(o.getStatus(), 99))` achieve?","options":["Standard enum ordering","Custom priority ordering where statuses are assigned integer priorities — URGENT(0) sorts before PROCESSING(1), unknown statuses sort last (99)","Sorts by status name alphabetically","Doesn't work because getOrDefault isn't a method reference"],"correctAnswer":"Custom priority ordering where statuses are assigned integer priorities — URGENT(0) sorts before PROCESSING(1), unknown statuses sort last (99)","explanation":"This pattern converts an enum/string to an integer priority for sorting. URGENT gets priority 0 (first), PROCESSING 1, COMPLETE 2, anything unknown 99 (last). More flexible than enum's natural ordinal ordering."}
],
"writtenConceptQuestions": [
  "Show a complete multi-key Comparator for Employee: primary by department, secondary by salary descending, tertiary by name. Use Comparator.comparing chaining.",
  "What is the difference between Comparator.reversed() applied to the whole chain vs only to thenComparing? Show a case where placement matters.",
  "Explain nullsFirst vs nullsLast. Show sorting a list of strings with null elements using both, and what happens without null-safe handling.",
  "Implement a dynamic sort for a product catalog: caller passes sortBy='price'|'name'|'stock'|'newest'. Use switch expression with Comparator.",
  "How does TreeSet use a Comparator for uniqueness? Show a case where two distinct products (different names, same price) get lost in a TreeSet<Product> sorted by price.",
  "Show a PriorityQueue used as a min-heap and max-heap for processing orders by total. Show poll() returning the correct element for each.",
  "What is Comparator.naturalOrder() for? When do you need a Comparator object but want natural ordering?"
],
"businessScenarios": [
  "A product search API returns results sorted by relevance by default. Users can request sort by price ascending, price descending, or newest. Implement sortable service using the Strategy pattern with Comparator.",
  "A logistics system needs to sort delivery packages: priority packages first (enum ordinal doesn't match priority), then by weight ascending. Use a Map<Priority, Integer> + Comparator.comparingInt to define custom priority ordering.",
  "A salary report sorts employees by department then salary descending. Currently it's two nested sorts causing the second to discard the first. Fix using single Comparator.comparing().thenComparing() chain."
]
},

"day-041": {
"notes": """# Spring Boot Dependency Injection: @Autowired, Constructor Injection, and Qualifiers

## What is Dependency Injection?
DI is an application of the Inversion of Control principle: objects don't create their dependencies — the framework creates them and injects them. This decouples classes from their concrete dependencies, enabling testing, swapping implementations, and lifecycle management.

```java
// WITHOUT DI — tightly coupled, untestable:
public class OrderService {
    private final OrderRepository repo = new OrderRepositoryImpl(); // hard-coded
    private final EmailService email = new EmailServiceImpl(); // can't swap in tests
}

// WITH DI — loosely coupled, testable:
@Service
public class OrderService {
    private final OrderRepository repo;    // interface, not impl
    private final EmailService email;       // interface, not impl

    // Constructor injection — Spring provides the implementations
    public OrderService(OrderRepository repo, EmailService email) {
        this.repo = repo;
        this.email = email;
    }
}
```

## Three Injection Styles
```java
// 1. CONSTRUCTOR INJECTION — recommended
@Service
public class UserService {
    private final UserRepository userRepo;
    private final PasswordEncoder encoder;

    // @Autowired optional when single constructor (Spring 4.3+)
    public UserService(UserRepository userRepo, PasswordEncoder encoder) {
        this.userRepo = userRepo;
        this.encoder = encoder;
    }
}

// 2. FIELD INJECTION — avoid (not testable without Spring context)
@Service
public class UserService {
    @Autowired private UserRepository userRepo; // can't inject in unit tests without MockitoAnnotations
    @Autowired private PasswordEncoder encoder;
}

// 3. SETTER INJECTION — for optional dependencies
@Service
public class NotificationService {
    private MetricsCollector metrics;

    @Autowired(required = false) // optional — null if no bean of this type
    public void setMetrics(MetricsCollector metrics) {
        this.metrics = metrics;
    }
}
```

## @Qualifier and @Primary — Resolving Ambiguity
```java
// Multiple beans of the same type
@Component("mysqlUserRepo")
public class MySQLUserRepository implements UserRepository { ... }

@Component("mongoUserRepo")
public class MongoUserRepository implements UserRepository { ... }

// @Qualifier — specify which bean by name
@Service
public class UserService {
    private final UserRepository repo;

    public UserService(@Qualifier("mysqlUserRepo") UserRepository repo) {
        this.repo = repo;
    }
}

// @Primary — default bean when no qualifier specified
@Primary
@Component
public class MySQLUserRepository implements UserRepository { ... }

// @Primary makes MySQLUserRepository the default; MongoUserRepository needs @Qualifier
```

## @Value — Injecting Properties
```java
@Service
public class PaymentService {
    @Value("${payment.api.key}")    // from application.properties
    private String apiKey;

    @Value("${payment.timeout:30}") // default value 30 if not found
    private int timeoutSeconds;

    @Value("${app.features.enabled:false}")
    private boolean featureEnabled;
}
```

## @ConfigurationProperties — Typed Property Binding
```java
@ConfigurationProperties(prefix = "app.payment")
@Component // or use @EnableConfigurationProperties on a config class
public class PaymentConfig {
    private String apiKey;
    private int timeoutSeconds = 30;     // default
    private String baseUrl;
    private boolean sandboxMode = false;
    // getters and setters required
}
// application.properties:
// app.payment.api-key=sk-live-...
// app.payment.timeout-seconds=60
// app.payment.base-url=https://api.payment.com
```

## Circular Dependencies — Detection and Resolution
```java
// CIRCULAR: A needs B, B needs A → Spring throws BeanCurrentlyInCreationException
@Service class A { A(B b) {} }
@Service class B { B(A a) {} }

// Fix 1: refactor to eliminate the cycle (best)
// Fix 2: @Lazy breaks the cycle — injects a proxy, real object created on first use
@Service class A {
    A(@Lazy B b) {} // B is a proxy until actually called
}
```

## Testing with DI — Mockito Integration
```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock private OrderRepository orderRepo;  // mock — no real implementation needed
    @Mock private EmailService emailService;
    @InjectMocks private OrderService orderService; // constructor-injected with mocks

    @Test
    void createOrder_savesAndSendsEmail() {
        Order order = new Order("user1", BigDecimal.TEN);
        when(orderRepo.save(any())).thenReturn(order);
        orderService.createOrder(order);
        verify(emailService).sendConfirmation(order);
    }
}
```
""",
"mcqs": [
  {"id":"d41q1","prompt":"Why is constructor injection preferred over field injection in Spring Boot?","options":["Constructor injection is faster","Constructor injection makes dependencies explicit, enables immutable fields (final), allows unit testing without a Spring context (plain constructor call), and fails fast at startup if a dependency is missing","Field injection is deprecated","Spring only supports constructor injection in Java 21"],"correctAnswer":"Constructor injection makes dependencies explicit, enables immutable fields (final), allows unit testing without a Spring context (plain constructor call), and fails fast at startup if a dependency is missing","explanation":"Field injection: you can't inject without @Autowired processing (needs Spring context or MockitoAnnotations). Constructor injection: dependencies are explicit in the constructor signature, fields can be final, and you can unit test with new OrderService(mockRepo, mockEmail) directly."},
  {"id":"d41q2","prompt":"What does `@Autowired(required = false)` do?","options":["Makes injection mandatory","Makes the dependency optional — injects null (or doesn't call the setter) if no matching bean is found, without throwing a startup exception","Allows multiple beans to be injected","Marks the bean as optional for lazy loading"],"correctAnswer":"Makes the dependency optional — injects null (or doesn't call the setter) if no matching bean is found, without throwing a startup exception","explanation":"By default, @Autowired requires a matching bean (throws NoSuchBeanDefinitionException if missing). required=false makes it optional: if no bean matches, the field stays null (constructor/setter not called). Use for optional integrations like metrics, audit, or feature modules."},
  {"id":"d41q3","prompt":"What does @Primary on a Spring bean do?","options":["Makes the bean a singleton","Marks a bean as the default candidate when multiple beans of the same type exist — wins in ambiguous @Autowired without a @Qualifier","Gives the bean higher priority in startup order","Primary beans start before other beans"],"correctAnswer":"Marks a bean as the default candidate when multiple beans of the same type exist — wins in ambiguous @Autowired without a @Qualifier","explanation":"When Spring finds multiple beans of the requested type, @Primary designates one as the default. @Qualifier('name') overrides @Primary for specific injection points. Use @Primary for 'the main implementation' and @Qualifier when you specifically need the alternative."},
  {"id":"d41q4","prompt":"What is `BeanCurrentlyInCreationException` in Spring Boot?","options":["A null pointer during bean creation","A circular dependency — Bean A needs Bean B which needs Bean A, forming a cycle Spring cannot resolve with constructor injection","A missing @Bean method","An exception thrown when a bean is created twice"],"correctAnswer":"A circular dependency — Bean A needs Bean B which needs Bean A, forming a cycle Spring cannot resolve with constructor injection","explanation":"Constructor injection circular dependencies cannot be resolved — A requires B to exist before A is created, but B requires A. Spring detects this and throws BeanCurrentlyInCreationException at startup. Fix: redesign to eliminate the cycle (usually a missing third class or responsibility overlap), or use @Lazy as a workaround."},
  {"id":"d41q5","prompt":"What does `@Value('${payment.timeout:30}')` inject?","options":["The literal string '${payment.timeout:30}'","The value of payment.timeout from application.properties; if not found, defaults to 30","30 always, ignoring the property","Throws PropertyNotFoundException if not set"],"correctAnswer":"The value of payment.timeout from application.properties; if not found, defaults to 30","explanation":"@Value uses Spring Expression Language: ${propertyName} reads from properties. :defaultValue after the property name provides a default if the property is missing. So payment.timeout:30 reads payment.timeout, or injects 30 if not configured."},
  {"id":"d41q6","prompt":"With @InjectMocks in Mockito, how does injection work when the class has a constructor with parameters?","options":["@InjectMocks always uses field injection","Mockito uses the largest constructor and passes @Mock fields matching the constructor's parameter types","@InjectMocks doesn't work with constructor injection","Requires @Spy on the constructor"],"correctAnswer":"Mockito uses the largest constructor and passes @Mock fields matching the constructor's parameter types","explanation":"Mockito's @InjectMocks tries injection strategies in order: 1) largest constructor that Mockito can fill with @Mock/@Spy fields, 2) setter injection, 3) field injection. With constructor injection, it automatically passes matching @Mock fields."},
  {"id":"d41q7","prompt":"What is `@ConfigurationProperties(prefix = 'app.payment')` better at than `@Value`?","options":["@ConfigurationProperties is faster","Binds a group of related properties to a typed POJO with validation, IDE completion, and relaxed binding — avoids 10+ @Value annotations in one class","@ConfigurationProperties supports SpEL expressions","@Value doesn't work with Spring Boot"],"correctAnswer":"Binds a group of related properties to a typed POJO with validation, IDE completion, and relaxed binding — avoids 10+ @Value annotations in one class","explanation":"@ConfigurationProperties: binds all app.payment.* properties to a PaymentConfig class automatically. Supports JSR-303 validation (@NotNull, @Min), IDE completion, and relaxed binding (api-key → apiKey). For multiple related properties, @ConfigurationProperties is cleaner than scattered @Value annotations."},
  {"id":"d41q8","prompt":"Why is field injection not unit-testable without Spring context or Mockito's @InjectMocks?","options":["Field injection uses private fields that can't be accessed","You cannot construct the class and inject dependencies via the constructor — you must start Spring or use reflection/Mockito to inject into private fields","Field injection requires interface-based dependencies","Field injection doesn't work with interface types"],"correctAnswer":"You cannot construct the class and inject dependencies via the constructor — you must start Spring or use reflection/Mockito to inject into private fields","explanation":"new OrderService() with field-injected @Autowired fields creates the object with null fields. You can't pass mocks via constructor. Either MockitoAnnotations.openMocks(this) uses reflection to inject, or you use @SpringBootTest which starts a full context — slow. Constructor injection: new OrderService(mockRepo) — fast, simple."},
  {"id":"d41q9","prompt":"What is the purpose of `@Qualifier` vs `@Primary`?","options":["Identical — both select a bean by name","@Primary designates a default bean for all injection points; @Qualifier targets a SPECIFIC injection point — overrides @Primary for that point","@Qualifier is for multiple beans; @Primary is for single beans","@Primary is deprecated in Spring Boot 3"],"correctAnswer":"@Primary designates a default bean for all injection points; @Qualifier targets a SPECIFIC injection point — overrides @Primary for that point","explanation":"@Primary: 'When in doubt, use me.' Applied once on the bean. @Qualifier: 'At this specific injection point, use this specific bean.' Applied at each injection point where the default is wrong. They work together: @Primary is the default, @Qualifier overrides it."},
  {"id":"d41q10","prompt":"When does Spring inject dependencies — at startup or on first use?","options":["On first use (lazy by default)","At startup (eager by default) — unless @Lazy is applied, beans are instantiated and wired when the ApplicationContext starts","At compile time","When the first HTTP request arrives"],"correctAnswer":"At startup (eager by default) — unless @Lazy is applied, beans are instantiated and wired when the ApplicationContext starts","explanation":"Spring's default is eager initialization: all singleton beans are created and injected at startup. This means missing dependencies, misconfigurations, and circular dependencies are detected immediately at startup (fail-fast). @Lazy defers bean creation until first use — useful for expensive beans or breaking circular dependencies."}
],
"writtenConceptQuestions": [
  "Compare all three injection styles (constructor, field, setter): show the code, explain testability, immutability implications, and when to use each.",
  "Explain @Qualifier and @Primary with a real scenario: two DataSource beans (primary DB and read replica). Show how the service chooses the read replica for query methods.",
  "What is a circular dependency in Spring Boot? Show BeanCurrentlyInCreationException scenario and two resolution strategies.",
  "Explain @Value vs @ConfigurationProperties. Show migrating 5 scattered @Value annotations in a PaymentService to a typed PaymentConfig POJO.",
  "Show a complete Mockito unit test for a service with two constructor-injected dependencies: @Mock, @InjectMocks, when(), verify().",
  "What does @Autowired(required = false) solve? Show an optional MetricsCollector that may or may not be on the classpath.",
  "Explain DI's role in the Inversion of Control principle. What problem does DI solve that constructing dependencies directly doesn't?"
],
"businessScenarios": [
  "A new service needs to use either a Kafka or SQS message publisher depending on environment. Both implement MessagePublisher. Design with @Primary on the default (Kafka) and @Profile-based conditional beans for SQS in test.",
  "A UserService uses field injection — all 6 @Autowired fields make it a 300-line test requiring @SpringBootTest. Refactor to constructor injection and rewrite the test as a plain unit test with Mockito.",
  "A startup CircularDependencyException blocks deployment: OrderService needs PaymentService which needs OrderService. Identify why, extract the common logic into a third class OrderPaymentCoordinator, and fix the cycle."
]
},

"day-042": {
"notes": """# Spring Beans: @Bean, Stereotypes, Scopes, and Lifecycle

## Bean Stereotypes — @Component and its Specialisations
```java
@Component   // generic Spring-managed component
@Service     // business logic layer — semantic annotation, same as @Component
@Repository  // data access layer — adds persistence exception translation
@Controller  // Spring MVC web layer
@RestController // @Controller + @ResponseBody

// These are all @Component specialisations — scanned via @ComponentScan
// Difference: @Repository wraps persistence exceptions in Spring's DataAccessException hierarchy
@Repository
public class OrderRepositoryImpl implements OrderRepository {
    // DataAccessException translation: SQL/JPA exceptions → Spring's unchecked hierarchy
    public Order save(Order order) { ... }
}
```

## @Bean — Manual Bean Definition
```java
@Configuration
public class AppConfig {

    // Method name becomes bean name (default)
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }

    // Custom name + destroy method
    @Bean(name = "asyncExecutor", destroyMethod = "shutdown")
    public ExecutorService executorService() {
        return Executors.newFixedThreadPool(10);
    }

    // @Bean with dependency injection via parameters
    @Bean
    public OrderMapper orderMapper(ModelMapper modelMapper) {
        return new OrderMapper(modelMapper); // Spring injects modelMapper @Bean
    }
}
```

## Bean Scopes
```java
// @Scope values:
@Scope("singleton")   // DEFAULT — one instance per ApplicationContext, shared
@Scope("prototype")   // new instance every time the bean is requested
@Scope("request")     // one instance per HTTP request (web apps)
@Scope("session")     // one instance per HTTP session (web apps)
@Scope("application") // one instance per ServletContext

// Prototype example — stateful beans, commands, DTOs built by Spring
@Component
@Scope("prototype")
public class OrderProcessor {
    private final List<String> processingLog = new ArrayList<>(); // per-instance state
    public void process(Order order) { processingLog.add("Processing: " + order.getId()); }
}

// Injecting prototype into singleton — use ObjectProvider to get new instance each time
@Service
public class BatchService {
    @Autowired
    private ObjectProvider<OrderProcessor> processorProvider;

    public void processBatch(List<Order> orders) {
        OrderProcessor processor = processorProvider.getObject(); // NEW instance each call
        orders.forEach(processor::process);
    }
}
```

## Bean Lifecycle
```java
@Component
public class DataSourceConnectionPool implements InitializingBean, DisposableBean {

    // Lifecycle hook options:
    // 1. @PostConstruct — JSR-250, runs after injection, before bean is used
    @PostConstruct
    public void init() {
        log.info("Initialising connection pool with {} connections", poolSize);
        // set up connections, validate config
    }

    // 2. @PreDestroy — runs before bean is destroyed (context closes)
    @PreDestroy
    public void cleanup() {
        log.info("Shutting down connection pool");
        // release resources, close connections
    }

    // 3. InitializingBean.afterPropertiesSet() — Spring-specific interface
    @Override
    public void afterPropertiesSet() { /* alternative to @PostConstruct */ }

    // 4. DisposableBean.destroy() — Spring-specific interface
    @Override
    public void destroy() { /* alternative to @PreDestroy */ }
}
// Order: constructor → @Autowired → @PostConstruct → [use] → @PreDestroy
```

## Conditional Beans — @Profile, @Conditional
```java
@Bean
@Profile("dev")       // only created when spring.profiles.active=dev
public DataSource devDataSource() { return new EmbeddedDatabaseBuilder()...build(); }

@Bean
@Profile("prod")
public DataSource prodDataSource() { return new HikariDataSource(prodConfig); }

// @ConditionalOnProperty — create bean only if property is set/true
@Bean
@ConditionalOnProperty(name = "app.cache.enabled", havingValue = "true")
public CacheManager cacheManager() { return new ConcurrentMapCacheManager(); }

// @ConditionalOnMissingBean — provide default, let users override
@Bean
@ConditionalOnMissingBean(PasswordEncoder.class) // create only if no PasswordEncoder exists
public PasswordEncoder defaultEncoder() { return new BCryptPasswordEncoder(); }
```

## Common Mistakes
1. **Non-singleton @Bean method in non-@Configuration class:** If `AppConfig` is `@Component` instead of `@Configuration`, `@Bean` methods are not proxied — each call creates a new instance instead of returning the singleton.
2. **Using `@Scope("prototype")` on a service injected into a singleton:** The prototype is injected once at startup — you always get the same instance. Use `ObjectProvider` or `ApplicationContext.getBean()`.
3. **Logic in @PostConstruct that depends on another bean's @PostConstruct:** Initialization order between beans isn't guaranteed. Use `@DependsOn("otherBean")` or redesign.
""",
"mcqs": [
  {"id":"d42q1","prompt":"What is the difference between @Service and @Component?","options":["@Service is for web controllers","They are functionally identical as component stereotypes — @Service communicates developer intent (business logic layer) and may receive additional AOP-based features in frameworks","@Service is required for @Transactional to work","@Component creates a prototype scope bean"],"correctAnswer":"They are functionally identical as component stereotypes — @Service communicates developer intent (business logic layer) and may receive additional AOP-based features in frameworks","explanation":"@Service, @Repository, @Controller, @RestController are all specialisations of @Component — all detected by @ComponentScan. @Repository adds exception translation. @Service is semantic: 'this is business logic.' Use appropriate stereotypes for code readability and potential AOP targeting."},
  {"id":"d42q2","prompt":"What is the default bean scope in Spring Boot?","options":["prototype — new instance per request","singleton — one instance per ApplicationContext, shared across all injection points","request — one per HTTP request","session — one per user session"],"correctAnswer":"singleton — one instance per ApplicationContext, shared across all injection points","explanation":"Spring beans are singletons by default. One instance is created at startup and shared everywhere. This is why service beans must be stateless — any instance variable is shared across all threads handling requests simultaneously."},
  {"id":"d42q3","prompt":"What does @PostConstruct do?","options":["Creates the bean post-constructor","Runs a method after all dependencies are injected but before the bean is used — for initialization logic that requires injected dependencies","Marks a method as a factory method","Post-processes the bean after the context is fully started"],"correctAnswer":"Runs a method after all dependencies are injected but before the bean is used — for initialization logic that requires injected dependencies","explanation":"The constructor runs before injection. @PostConstruct runs after injection — when injected fields are available. Use for: opening connections, validating config, warming caches. Order: constructor → dependency injection → @PostConstruct."},
  {"id":"d42q4","prompt":"Why is `@Bean` in a `@Component` class (not `@Configuration`) a potential bug?","options":["@Bean only works in @Configuration","Without @Configuration's CGLIB proxy, @Bean methods are called as plain Java methods — each call creates a new instance instead of returning the Spring singleton","@Component beans can't use @Bean","@Bean is ignored in @Component classes"],"correctAnswer":"Without @Configuration's CGLIB proxy, @Bean methods are called as plain Java methods — each call creates a new instance instead of returning the Spring singleton","explanation":"@Configuration wraps the class in a CGLIB subclass that intercepts @Bean method calls and returns the existing singleton from the context. In a plain @Component, @Bean methods are not intercepted — calling them directly creates new instances, breaking singleton behaviour and cross-@Bean dependencies."},
  {"id":"d42q5","prompt":"How do you get a new prototype-scoped bean instance every time you need one from a singleton service?","options":["Use @Scope('prototype') on the singleton","Inject ObjectProvider<PrototypeBean> and call .getObject() to get a fresh instance each time","Prototype injection into singletons always creates a new instance","Use @Autowired with @Qualifier('prototype')"],"correctAnswer":"Inject ObjectProvider<PrototypeBean> and call .getObject() to get a fresh instance each time","explanation":"Direct @Autowired of a prototype into a singleton: Spring injects once at startup — same instance forever. ObjectProvider.getObject() asks the context for a fresh prototype instance each call. Alternatively: ApplicationContext.getBean(PrototypeBean.class) or @Lookup method injection."},
  {"id":"d42q6","prompt":"What does `@Profile('prod')` on a @Bean method do?","options":["Marks the bean as production-ready","Creates the bean ONLY when spring.profiles.active=prod — different beans for different environments without code changes","Optimizes the bean for production performance","Disables the bean in test profiles"],"correctAnswer":"Creates the bean ONLY when spring.profiles.active=prod — different beans for different environments without code changes","explanation":"@Profile allows environment-specific bean creation. dev profile → H2 in-memory DB. prod profile → HikariCP PostgreSQL connection. test profile → mocked beans. Set active profile: spring.profiles.active=prod in application.properties or -Dspring.profiles.active=prod at runtime."},
  {"id":"d42q7","prompt":"What is `@ConditionalOnMissingBean`?","options":["Creates a bean only when its type is missing","Creates a bean only when no other bean of the specified type exists — used by auto-configuration to provide defaults that users can override by declaring their own","Prevents bean creation in test contexts","Checks for missing optional dependencies"],"correctAnswer":"Creates a bean only when no other bean of the specified type exists — used by auto-configuration to provide defaults that users can override by declaring their own","explanation":"Spring Boot auto-configuration uses @ConditionalOnMissingBean extensively: if you declare a PasswordEncoder @Bean yourself, Spring Boot's default PasswordEncoder is NOT created. Your custom bean takes priority. This is how Spring Boot's convention-over-configuration works."},
  {"id":"d42q8","prompt":"In what order does Spring execute bean lifecycle callbacks?","options":["@PostConstruct → constructor → @Autowired → @PreDestroy","constructor → @Autowired/dependency injection → @PostConstruct → [application runs] → @PreDestroy","@PreDestroy → @PostConstruct → constructor","constructor → @PostConstruct → @Autowired"],"correctAnswer":"constructor → @Autowired/dependency injection → @PostConstruct → [application runs] → @PreDestroy","explanation":"Lifecycle order: 1) Constructor (bean created), 2) @Autowired dependencies injected, 3) @PostConstruct (initialization with injected deps available), 4) Application uses the bean, 5) Context closes → @PreDestroy (cleanup). If you access @Autowired fields in the constructor, they are null."},
  {"id":"d42q9","prompt":"What does `@Bean(destroyMethod = 'shutdown')` do?","options":["Kills the JVM when the bean shuts down","Calls the bean's shutdown() method when the ApplicationContext is closed — for resource cleanup of externally managed objects","Marks the bean as disposable","@Bean doesn't support destroyMethod"],"correctAnswer":"Calls the bean's shutdown() method when the ApplicationContext is closed — for resource cleanup of externally managed objects","explanation":"For beans not managed by Spring's lifecycle interfaces (@PreDestroy), destroyMethod specifies which method to call on context close. Common for ExecutorService.shutdown(), HikariDataSource.close(), or other third-party resources that need explicit cleanup."},
  {"id":"d42q10","prompt":"What is @Repository's additional feature vs @Component?","options":["Automatically creates CRUD methods","Translates persistence-specific exceptions (JDBC SQLException, JPA PersistenceException) into Spring's DataAccessException hierarchy","Creates an in-memory repository for testing","@Repository enables lazy loading"],"correctAnswer":"Translates persistence-specific exceptions (JDBC SQLException, JPA PersistenceException) into Spring's DataAccessException hierarchy","explanation":"@Repository enables Spring's PersistenceExceptionTranslationPostProcessor which wraps persistence exceptions in Spring's unchecked DataAccessException hierarchy. This means service code doesn't need to catch JDBC or JPA specific exceptions — it catches DataAccessException, abstracting the persistence technology."}
],
"writtenConceptQuestions": [
  "Explain the four Spring stereotype annotations (@Component, @Service, @Repository, @Controller) and what distinguishes them beyond semantics.",
  "What is the difference between @Component-detected beans and @Bean-defined beans? When would you use @Bean instead of @Component?",
  "Explain all four bean scopes: singleton, prototype, request, session. Show a case where prototype scope is necessary and how to inject it into a singleton correctly.",
  "Show the complete bean lifecycle: constructor, @Autowired, @PostConstruct, [use], @PreDestroy. Show a connection pool that opens on @PostConstruct and closes on @PreDestroy.",
  "What is @ConditionalOnProperty? Show a feature flag that enables a caching bean only when app.cache.enabled=true.",
  "Explain the @Configuration CGLIB proxy and why @Bean in @Component is different. Show the bug and how to fix it.",
  "What does @Profile allow? Show a DataSource bean configured for three profiles: dev (H2), test (testcontainers), prod (HikariCP PostgreSQL)."
],
"businessScenarios": [
  "A Spring Boot app's connection pool is not cleaned up when the application shuts down — DBCP connections stay open. Add @PreDestroy (or destroyMethod) to ensure the pool closes on context shutdown.",
  "A feature flag system: send emails via real SMTP in prod, log-only in dev, mock in tests. Design using @Profile on three EmailService beans without if-statements in the service.",
  "A new MessageQueue integration should activate only when app.messaging.enabled=true. Use @ConditionalOnProperty so the bean isn't created in environments without the queue configured, avoiding startup errors."
]
},

"day-043": {
"notes": """# Spring Boot Controllers: @RestController, Path Variables, Request Params, and Request Body

## @RestController vs @Controller
```java
// @Controller — returns view names for template rendering (Thymeleaf, etc.)
@Controller
public class PageController {
    @GetMapping("/home")
    public String home(Model model) {
        model.addAttribute("user", userService.getCurrentUser());
        return "home"; // template name: home.html (Thymeleaf)
    }
}

// @RestController = @Controller + @ResponseBody
// — every method returns JSON/XML, not view name
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    @GetMapping("/{id}")
    public OrderDto getOrder(@PathVariable String id) {
        return orderService.findById(id); // serialized to JSON automatically
    }
}
```

## @PathVariable — URL Path Extraction
```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    // Simple path variable
    @GetMapping("/{id}")
    public UserDto getUser(@PathVariable String id) { ... }
    // GET /api/users/abc123 → id = "abc123"

    // Multiple path variables
    @GetMapping("/{userId}/orders/{orderId}")
    public OrderDto getUserOrder(
            @PathVariable String userId,
            @PathVariable String orderId) { ... }
    // GET /api/users/u1/orders/o99 → userId="u1", orderId="o99"

    // Optional path variable with required=false
    @GetMapping({"/", "/{id}"})
    public Object get(@PathVariable(required = false) String id) {
        return id == null ? userService.findAll() : userService.findById(id);
    }
}
```

## @RequestParam — Query Parameters
```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    // Required query param
    @GetMapping("/search")
    public List<ProductDto> search(@RequestParam String keyword) { ... }
    // GET /api/products/search?keyword=laptop

    // Optional with default
    @GetMapping
    public Page<ProductDto> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "name") String sortBy) { ... }
    // GET /api/products → page=0, size=20, sortBy=name
    // GET /api/products?page=2&size=10&sortBy=price → page=2, size=10, sortBy=price

    // Multiple values for same param
    @GetMapping("/filter")
    public List<ProductDto> filter(@RequestParam List<String> categories) { ... }
    // GET /api/products/filter?categories=electronics&categories=clothing
}
```

## @RequestBody — Deserializing JSON Body
```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    // POST with JSON body
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public OrderDto createOrder(@RequestBody @Valid CreateOrderRequest request) {
        return orderService.create(request);
    }

    // PUT — full update
    @PutMapping("/{id}")
    public OrderDto updateOrder(@PathVariable String id,
                                @RequestBody @Valid UpdateOrderRequest request) {
        return orderService.update(id, request);
    }

    // PATCH — partial update
    @PatchMapping("/{id}/status")
    public OrderDto updateStatus(@PathVariable String id,
                                 @RequestBody UpdateStatusRequest request) {
        return orderService.updateStatus(id, request.getStatus());
    }
}

// Request DTO with validation
public record CreateOrderRequest(
    @NotBlank String customerId,
    @NotEmpty List<@Valid OrderItemRequest> items,
    @NotNull String shippingAddress
) {}
```

## @ModelAttribute and @RequestHeader
```java
// @RequestHeader — extract HTTP headers
@GetMapping("/me")
public UserDto getProfile(@RequestHeader("Authorization") String authHeader) {
    String token = authHeader.replace("Bearer ", "");
    return userService.fromToken(token);
}

// @CookieValue
@GetMapping("/session")
public SessionDto getSession(@CookieValue(value = "SESSION", required = false) String sessionId) { ... }
```

## Error Handling in Controller — @Valid + MethodArgumentNotValidException
```java
// In GlobalExceptionHandler:
@ExceptionHandler(MethodArgumentNotValidException.class)
@ResponseStatus(HttpStatus.BAD_REQUEST)
public ErrorResponse handleValidationErrors(MethodArgumentNotValidException e) {
    Map<String, String> errors = e.getBindingResult()
        .getFieldErrors().stream()
        .collect(Collectors.toMap(
            FieldError::getField,
            FieldError::getDefaultMessage,
            (a, b) -> a // merge function for duplicate field errors
        ));
    return new ErrorResponse("VALIDATION_ERROR", "Invalid request", errors);
}
```
""",
"mcqs": [
  {"id":"d43q1","prompt":"What is the difference between @Controller and @RestController?","options":["@RestController handles more HTTP methods","@RestController combines @Controller + @ResponseBody — every method returns data serialized as JSON/XML; @Controller returns view names for template rendering","@RestController requires JSON input","@Controller is deprecated in Spring Boot 3"],"correctAnswer":"@RestController combines @Controller + @ResponseBody — every method returns data serialized as JSON/XML; @Controller returns view names for template rendering","explanation":"@Controller: method return value is the view name ('home' → home.html). @RestController: return value is serialized to response body (JSON by default with Jackson). Use @RestController for REST APIs, @Controller for server-rendered web apps."},
  {"id":"d43q2","prompt":"What does `@PathVariable String id` extract from `GET /api/orders/order-123`?","options":["'api'","'order-123' — the segment of the URL path matching the {id} template variable","'orders'","The entire URL path"],"correctAnswer":"'order-123' — the segment of the URL path matching the {id} template variable","explanation":"@PathVariable binds a URL template variable {id} to a method parameter. GET /api/orders/order-123 with @GetMapping('/{id}') injects 'order-123' as the id parameter. The name must match the {name} in the URL pattern, or use @PathVariable('variableName')."},
  {"id":"d43q3","prompt":"What does `@RequestParam(defaultValue = '0') int page` do when no page parameter is provided?","options":["Throws MissingServletRequestParameterException","Injects 0 — the defaultValue is used when the parameter is absent","Injects null","Returns an error response"],"correctAnswer":"Injects 0 — the defaultValue is used when the parameter is absent","explanation":"defaultValue makes the parameter optional: if ?page= is not in the query string, page is 0. Without defaultValue and without required=false, the parameter is mandatory and throws MissingServletRequestParameterException if absent."},
  {"id":"d43q4","prompt":"What does `@RequestBody @Valid CreateOrderRequest request` do?","options":["Reads the request URL","Deserializes the JSON request body into CreateOrderRequest, then runs @NotBlank/@NotNull validation annotations — throws MethodArgumentNotValidException if validation fails","@Valid is optional","Only validates primitive fields"],"correctAnswer":"Deserializes the JSON request body into CreateOrderRequest, then runs @NotBlank/@NotNull validation annotations — throws MethodArgumentNotValidException if validation fails","explanation":"@RequestBody: Jackson deserializes JSON body to the Java type. @Valid: triggers Bean Validation (JSR-303) on the deserialized object. If validation fails, Spring throws MethodArgumentNotValidException with field-level errors. Handled by @ExceptionHandler in @RestControllerAdvice."},
  {"id":"d43q5","prompt":"What HTTP method and path does `@PatchMapping('/{id}/status')` map to?","options":["PUT /id/status","PATCH /{id}/status — for partial updates (update one field without sending the full object)","GET /{id}/status","POST /{id}/status"],"correctAnswer":"PATCH /{id}/status — for partial updates (update one field without sending the full object)","explanation":"@PatchMapping maps HTTP PATCH method. PATCH = partial update (change only specified fields). PUT = full update (replace the entire resource). PATCH /orders/123/status with body {status: 'SHIPPED'} updates only status, not the whole order."},
  {"id":"d43q6","prompt":"How do you extract multiple values for the same query parameter? (`?tags=java&tags=spring`)","options":["@RequestParam String tags (returns first only)","@RequestParam List<String> tags — Spring collects all values for the same parameter into the list","@RequestParam String[] tags only","Use a custom ArgumentResolver"],"correctAnswer":"@RequestParam List<String> tags — Spring collects all values for the same parameter into the list","explanation":"For multi-value parameters (?tags=java&tags=spring), declare @RequestParam List<String> tags. Spring collects all values for 'tags' into the list: ['java', 'spring']. Also works with Set<String> or String[]."},
  {"id":"d43q7","prompt":"What does `@RequestHeader('Authorization') String authHeader` do?","options":["Checks the Authorization header is valid","Extracts the value of the HTTP Authorization header from the request into the authHeader parameter","Sets the Authorization header on the response","@RequestHeader is not a valid annotation"],"correctAnswer":"Extracts the value of the HTTP Authorization header from the request into the authHeader parameter","explanation":"@RequestHeader maps an HTTP header to a method parameter. GET /api/me with header Authorization: Bearer eyJ... → authHeader = 'Bearer eyJ...'. Use required=false for optional headers."},
  {"id":"d43q8","prompt":"What exception does `@RequestBody @Valid` throw when Bean Validation constraints fail?","options":["IllegalArgumentException","MethodArgumentNotValidException — contains BindingResult with all field-level validation errors","NullPointerException","ValidationException"],"correctAnswer":"MethodArgumentNotValidException — contains BindingResult with all field-level validation errors","explanation":"@Valid triggers Bean Validation. On failure: MethodArgumentNotValidException wrapping a BindingResult. BindingResult.getFieldErrors() returns all field violations. Handle in @ExceptionHandler(MethodArgumentNotValidException.class) to return structured error responses."},
  {"id":"d43q9","prompt":"A class is annotated with @RequestMapping('/api/orders') and a method with @GetMapping('/{id}'). What is the effective path?","options":["/id","GET /api/orders/{id} — class-level and method-level @RequestMapping are combined","/api/orders/id","/{id} overrides /api/orders"],"correctAnswer":"GET /api/orders/{id} — class-level and method-level @RequestMapping are combined","explanation":"Class-level @RequestMapping defines the base path for all methods. Method-level @GetMapping/@PostMapping etc. append to it. @RequestMapping('/api/orders') + @GetMapping('/{id}') = GET /api/orders/{id}. This avoids repeating '/api/orders' in every method."},
  {"id":"d43q10","prompt":"What is the purpose of `@ResponseStatus(HttpStatus.CREATED)` on a @PostMapping method?","options":["Documents the status code","Sets the HTTP response status to 201 Created — appropriate for successful resource creation (the default is 200 OK)","Required for POST methods","201 is the only valid response for POST"],"correctAnswer":"Sets the HTTP response status to 201 Created — appropriate for successful resource creation (the default is 200 OK)","explanation":"Without @ResponseStatus, all successful responses return 200 OK. @ResponseStatus(HttpStatus.CREATED) returns 201 for POST. HTTP semantics: 201 = new resource created, 200 = request processed, 204 = success, no content. Use ResponseEntity.status(201) for dynamic status."}
],
"writtenConceptQuestions": [
  "Show a complete REST controller for an Order resource: GET all (with pagination), GET by id, POST (create with validation), PUT (update), DELETE.",
  "Explain @PathVariable vs @RequestParam. Show a search endpoint using both: GET /api/products/{categoryId}/items?keyword=x&page=0&size=10.",
  "What is @RequestBody? Show Jackson deserializing a JSON POST body into a record with @Valid constraints.",
  "Show @ExceptionHandler for MethodArgumentNotValidException that returns field-level error map {fieldName: errorMessage}.",
  "What is the difference between PUT and PATCH? Show a product endpoint that supports both: PUT for full update, PATCH for partial status update.",
  "Explain @RequestHeader. Show a security use case: extract Bearer token from Authorization header in every request.",
  "Show class-level @RequestMapping combined with method-level @GetMapping, @PostMapping, @DeleteMapping for a /api/users resource."
],
"businessScenarios": [
  "A mobile app sends POST /api/orders with a missing required field (customerId). Currently returns a 500 with a Java stack trace. Add @Valid and a proper @ExceptionHandler that returns {fieldErrors: {customerId: 'must not be blank'}}.",
  "A product search endpoint supports 8 optional query parameters. Currently uses HttpServletRequest.getParameter() for each. Refactor to @RequestParam with defaultValue, producing clean method signature.",
  "A controller has hardcoded /v1/ paths everywhere. Client needs to call /v2/ with a new response format. Add class-level @RequestMapping and show versioned controllers: /v1/orders and /v2/orders mapping to different controller classes."
]
},

"day-044": {
"notes": """# REST APIs in Spring Boot: ResponseEntity, HTTP Methods, Status Codes, Content Negotiation

## ResponseEntity — Full Control Over HTTP Responses
```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    // 200 OK with body
    @GetMapping("/{id}")
    public ResponseEntity<OrderDto> getOrder(@PathVariable String id) {
        return ResponseEntity.ok(orderService.findById(id));
    }

    // 201 Created with Location header
    @PostMapping
    public ResponseEntity<OrderDto> createOrder(@RequestBody @Valid CreateOrderRequest req) {
        OrderDto created = orderService.create(req);
        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(created.id())
            .toUri();
        return ResponseEntity.created(location).body(created);
    }

    // 204 No Content for DELETE
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOrder(@PathVariable String id) {
        orderService.delete(id);
        return ResponseEntity.noContent().build();
    }

    // 404 conditionally
    @GetMapping("/{id}/details")
    public ResponseEntity<OrderDetailsDto> getDetails(@PathVariable String id) {
        return orderService.findDetails(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
```

## HTTP Methods — Semantics and Idempotency
| Method | Semantics | Idempotent | Safe | Body |
|---|---|---|---|---|
| GET | Read | ✅ | ✅ | No |
| POST | Create | ❌ | ❌ | Yes |
| PUT | Full Replace | ✅ | ❌ | Yes |
| PATCH | Partial Update | ❌* | ❌ | Yes |
| DELETE | Delete | ✅ | ❌ | No |
| HEAD | Like GET, no body | ✅ | ✅ | No |
| OPTIONS | List allowed methods | ✅ | ✅ | No |

*PATCH can be made idempotent by design.

```java
// Idempotent PUT — calling twice has same result as calling once
@PutMapping("/{id}")
public ResponseEntity<OrderDto> fullUpdate(@PathVariable String id,
                                           @RequestBody UpdateOrderRequest req) {
    // replaces ALL fields — same body, same result on repeat
    return ResponseEntity.ok(orderService.fullReplace(id, req));
}

// Non-idempotent PATCH — calling twice may have different results
@PatchMapping("/{id}/items/add")
public ResponseEntity<OrderDto> addItem(@PathVariable String id,
                                        @RequestBody AddItemRequest req) {
    // adds an item — calling twice adds the item twice
    return ResponseEntity.ok(orderService.addItem(id, req));
}
```

## HTTP Status Codes — Complete Reference
```java
// 2xx Success
200 OK          // GET/PUT/PATCH success with body
201 Created     // POST success — include Location header
202 Accepted    // async processing started — result not yet available
204 No Content  // DELETE/PUT success with no body

// 3xx Redirect
301 Moved Permanently  // permanent redirect
302 Found              // temporary redirect

// 4xx Client Error
400 Bad Request        // malformed request, validation failure
401 Unauthorized       // missing/invalid authentication
403 Forbidden          // authenticated but lacks permission
404 Not Found          // resource doesn't exist
405 Method Not Allowed // e.g., POST to read-only endpoint
409 Conflict           // duplicate key, concurrent modification
422 Unprocessable Entity // valid JSON but business rule violation
429 Too Many Requests  // rate limited

// 5xx Server Error
500 Internal Server Error // unexpected exception
503 Service Unavailable   // maintenance, overload
```

## Content Negotiation — produces and consumes
```java
// produces — what response format this method produces
@GetMapping(value = "/{id}", produces = {MediaType.APPLICATION_JSON_VALUE, MediaType.APPLICATION_XML_VALUE})
public OrderDto getOrder(@PathVariable String id) { ... }
// Client sends: Accept: application/xml → returns XML (needs Jackson XML dependency)
// Client sends: Accept: application/json → returns JSON

// consumes — what request format this method accepts
@PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
public ResponseEntity<OrderDto> createOrder(@RequestBody CreateOrderRequest req) { ... }
// Only accepts JSON body — 415 Unsupported Media Type for other content types

// Multiple formats
@PostMapping(consumes = {MediaType.APPLICATION_JSON_VALUE, MediaType.APPLICATION_XML_VALUE},
             produces = MediaType.APPLICATION_JSON_VALUE)
public ResponseEntity<OrderDto> create(@RequestBody CreateOrderRequest req) { ... }
```

## HATEOAS — Hypermedia Links in Responses
```java
// Basic link-enriched response (Spring HATEOAS)
@GetMapping("/{id}")
public EntityModel<OrderDto> getWithLinks(@PathVariable String id) {
    OrderDto order = orderService.findById(id);
    return EntityModel.of(order,
        linkTo(methodOn(OrderController.class).getWithLinks(id)).withSelfRel(),
        linkTo(methodOn(OrderController.class).deleteOrder(id)).withRel("delete"),
        linkTo(methodOn(OrderController.class).updateStatus(id, null)).withRel("update-status")
    );
}
// Response: { "id": "123", ..., "_links": { "self": {"href": "/api/orders/123"}, ... }}
```

## Common Mistakes
1. **Using 200 for all successful responses:** use 201 for creation, 204 for no-content responses.
2. **Not including Location header on 201:** per HTTP spec, 201 should include a Location header with the new resource URL.
3. **Using GET for state changes:** GET must be safe (no side effects). Use POST/PUT/PATCH for mutations.
4. **Returning 200 with error body:** `return ResponseEntity.ok(ErrorResponse("ERROR", msg))` confuses clients — always return the appropriate 4xx/5xx status code.
""",
"mcqs": [
  {"id":"d44q1","prompt":"What HTTP status code should a successful POST (create) return?","options":["200 OK","201 Created — indicates a new resource was created, typically with Location header pointing to it","204 No Content","202 Accepted"],"correctAnswer":"201 Created — indicates a new resource was created, typically with Location header pointing to it","explanation":"POST for creation: 201 Created. Include Location header with the URL of the new resource. 200 OK is for GET/PUT/PATCH that return a body. 204 is for no-content responses. 202 is for async where processing hasn't completed yet."},
  {"id":"d44q2","prompt":"What is idempotency in HTTP methods?","options":["The request never fails","Calling the same request multiple times produces the same result as calling it once — no additional side effects after the first call","All HTTP methods are idempotent","Only GET is idempotent"],"correctAnswer":"Calling the same request multiple times produces the same result as calling it once — no additional side effects after the first call","explanation":"Idempotent: GET, PUT, DELETE. PUT /orders/123 {status:SHIPPED} twice → same result as once (second call finds it already SHIPPED). POST is NOT idempotent: POST /orders twice creates two orders. Idempotency matters for retries after network failures."},
  {"id":"d44q3","prompt":"What HTTP status code means 'authenticated but not authorized'?","options":["401 Unauthorized","403 Forbidden — the client is authenticated (we know who you are) but lacks permission","404 Not Found","400 Bad Request"],"correctAnswer":"403 Forbidden — the client is authenticated (we know who you are) but lacks permission","explanation":"401 Unauthorized: not authenticated (no credentials or invalid credentials — should prompt login). 403 Forbidden: authenticated but insufficient permissions (logged in but accessing another user's data). The naming is historical — 401 means 'unauthenticated' in practice."},
  {"id":"d44q4","prompt":"What does `ResponseEntity.created(location).body(dto)` do?","options":["Returns 200 with body","Returns 201 Created with the Location header set to location URI and the DTO as the response body","Returns 302 redirect to location","Returns 201 with empty body and location header only"],"correctAnswer":"Returns 201 Created with the Location header set to location URI and the DTO as the response body","explanation":"ResponseEntity.created(URI) sets status 201 and Location header. .body(dto) sets the response body. This is the RESTful standard for resource creation: client knows the resource was created (201) and where to find it (Location)."},
  {"id":"d44q5","prompt":"What does `produces = MediaType.APPLICATION_JSON_VALUE` on a method do?","options":["Forces the client to send JSON","Declares that this method can produce JSON responses — the framework returns 406 Not Acceptable if the client's Accept header requests a format this method can't produce","Makes the response faster","Required for JSON responses to work"],"correctAnswer":"Declares that this method can produce JSON responses — the framework returns 406 Not Acceptable if the client's Accept header requests a format this method can't produce","explanation":"produces restricts content negotiation: only serve this method if the client accepts this media type. If client sends Accept: application/xml but the method only produces JSON, Spring returns 406 Not Acceptable. Omitting produces means the method handles any Accept type."},
  {"id":"d44q6","prompt":"What is the correct response for `DELETE /api/orders/123` when successful?","options":["200 OK with deleted order","204 No Content — success but no body to return","404 Not Found","200 OK with empty JSON {}"],"correctAnswer":"204 No Content — success but no body to return","explanation":"204 No Content: operation succeeded but there's no content to return in the body. Appropriate for DELETE (resource is gone), and for PUT/PATCH when you don't return the updated resource. ResponseEntity.noContent().build() in Spring Boot."},
  {"id":"d44q7","prompt":"What is 422 Unprocessable Entity vs 400 Bad Request?","options":["Identical","400 Bad Request: syntactically malformed request (can't parse); 422 Unprocessable Entity: syntactically valid but semantically invalid (business rule violation like 'order date cannot be in the past')","422 is for server errors","400 is for authentication failures"],"correctAnswer":"400 Bad Request: syntactically malformed request (can't parse); 422 Unprocessable Entity: syntactically valid but semantically invalid (business rule violation like 'order date cannot be in the past')","explanation":"400: JSON is malformed, required fields missing (validation failure at parsing/annotation level). 422: the request body parses correctly but the business logic rejects it (insufficient stock, date conflict). Some APIs use 400 for both — 422 is more precise."},
  {"id":"d44q8","prompt":"What is HATEOAS in REST API design?","options":["A CSS framework for APIs","Hypermedia As The Engine Of Application State — including links in responses that describe what actions are available next, making the API self-discoverable","A security standard","Stands for HTTP API Transport Encoding and Schema"],"correctAnswer":"Hypermedia As The Engine Of Application State — including links in responses that describe what actions are available next, making the API self-discoverable","explanation":"HATEOAS adds _links to responses: {id:'123', status:'PENDING', _links:{self:{href:'/orders/123'}, cancel:{href:'/orders/123/cancel'}, pay:{href:'/orders/123/pay'}}}. Clients discover available actions from the response rather than hard-coding URLs. Spring HATEOAS library provides EntityModel, CollectionModel."},
  {"id":"d44q9","prompt":"What does `return ResponseEntity.ok(ErrorResponse('ERROR', msg))` get wrong?","options":["ErrorResponse is not serializable","It returns HTTP 200 OK with an error message — clients that check status code before reading body will treat this as success","ok() doesn't accept ErrorResponse","The body should be a String"],"correctAnswer":"It returns HTTP 200 OK with an error message — clients that check status code before reading body will treat this as success","explanation":"HTTP clients, monitoring tools, and load balancers use status codes to determine success/failure. Returning 200 with an error body is misleading. Return the appropriate error status: ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse) or use @ResponseStatus in @ExceptionHandler."},
  {"id":"d44q10","prompt":"What does `ServletUriComponentsBuilder.fromCurrentRequest().path('/{id}').buildAndExpand(id).toUri()` create?","options":["A redirect URL","The URI of the newly created resource based on the current request URL + id — used for the Location header in 201 Created responses","A URL to the current endpoint documentation","An absolute URL to an external service"],"correctAnswer":"The URI of the newly created resource based on the current request URL + id — used for the Location header in 201 Created responses","explanation":"If the request is POST /api/orders, fromCurrentRequest() captures /api/orders, .path('/{id}') appends /{id}, .buildAndExpand('order-123') fills in the id → /api/orders/order-123. This URI is set as the Location header in the 201 response so clients know where the new resource lives."}
],
"writtenConceptQuestions": [
  "Show a complete CRUD REST controller using ResponseEntity: GET (200), POST (201+Location), PUT (200), PATCH (200), DELETE (204).",
  "Explain idempotency. Which HTTP methods are idempotent? Give a real scenario where idempotency matters (retry logic after network failure).",
  "What are the HTTP status codes for: success with body, success without body, creation, async accepted, not found, invalid input, unauthorized, forbidden, conflict, rate limited?",
  "Explain content negotiation (produces/consumes). Show a controller that returns JSON or XML based on Accept header.",
  "What is HATEOAS? Show an order response with _links for self, cancel, and pay actions.",
  "When is 422 Unprocessable Entity more appropriate than 400 Bad Request? Show a business rule violation (duplicate order reference) returning 422.",
  "Show how to build the Location header using ServletUriComponentsBuilder in a POST endpoint that creates a new user."
],
"businessScenarios": [
  "A client reports that their monitoring shows 100% success rate even when orders fail to create. Investigation reveals the API returns 200 OK with {error: 'Insufficient stock'}. Fix to return 422 with proper error structure.",
  "A mobile app retries failed requests. DELETE /api/orders/123 returns 404 on the retry (already deleted). The app crashes. Fix: make DELETE idempotent by returning 204 whether the order existed or was already deleted.",
  "An API is being consumed by 3 clients. Client A needs JSON, Client B needs XML, Client C needs CSV. Design content negotiation using produces on the controller and Accept header on clients without duplicating business logic."
]
},

"day-045": {
"notes": """# Request Mapping: @RequestMapping Deep Dive, URL Patterns, and Method-Level Configuration

## @RequestMapping — The Foundation
`@RequestMapping` is the parent annotation for all HTTP method-specific mappings. It maps HTTP requests to handler methods based on URL, method, headers, parameters, and content type.
```java
// Class-level @RequestMapping — base path for all methods
@RestController
@RequestMapping(
    value = "/api/v1/orders",
    produces = MediaType.APPLICATION_JSON_VALUE
)
public class OrderController {
    // All methods inherit /api/v1/orders base path and JSON produces
}

// Method-level overrides and specifics
@RequestMapping(
    value = "/{id}",
    method = RequestMethod.GET,
    produces = {MediaType.APPLICATION_JSON_VALUE, MediaType.APPLICATION_XML_VALUE}
)
public OrderDto getOrder(@PathVariable String id) { ... }
// Equivalent shorthand: @GetMapping(value = "/{id}", produces = {...})
```

## URL Pattern Matching
```java
// Exact match
@GetMapping("/status")   // matches: /api/orders/status

// Path variable
@GetMapping("/{id}")     // matches: /api/orders/abc123

// Multiple path variables
@GetMapping("/{userId}/orders/{orderId}")

// Wildcard — single path segment
@GetMapping("/*/details") // matches: /admin/details, /user/details

// Double wildcard — multiple segments
@GetMapping("/**")       // matches anything under the base path

// Optional extension
@GetMapping("/report.{format}")  // matches /report.pdf, /report.csv
// @PathVariable String format → "pdf" or "csv"

// Regular expression in path variable
@GetMapping("/{id:[0-9]+}")    // only matches numeric IDs
@GetMapping("/{name:[a-z-]+}") // only lowercase letters and hyphens
```

## Versioning Strategies
```java
// Strategy 1: URL path versioning (most visible, easiest to test in browser)
@RequestMapping("/api/v1/orders") // v1
@RequestMapping("/api/v2/orders") // v2

// Strategy 2: Header versioning
@GetMapping(value = "/orders", headers = "X-API-Version=1")
@GetMapping(value = "/orders", headers = "X-API-Version=2")

// Strategy 3: Accept header versioning (media type)
@GetMapping(value = "/orders", produces = "application/vnd.company.v1+json")
@GetMapping(value = "/orders", produces = "application/vnd.company.v2+json")

// Strategy 4: Request parameter versioning
@GetMapping(value = "/orders", params = "version=1")
@GetMapping(value = "/orders", params = "version=2")
```

## Request Mapping Conditions — headers, params, consumes
```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    // Method restricted by HTTP header presence
    @GetMapping(value = "/admin", headers = "X-Admin-Key")
    public List<OrderDto> adminView(@RequestHeader("X-Admin-Key") String key) { ... }

    // Method restricted by query param value
    @GetMapping(params = "type=express")
    public List<OrderDto> expressOrders() { ... }
    // Matches: GET /api/orders?type=express

    // Method restricted by request content type
    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<OrderDto> createFromJson(@RequestBody CreateOrderRequest req) { ... }

    @PostMapping(consumes = MediaType.APPLICATION_FORM_URLENCODED_VALUE)
    public ResponseEntity<OrderDto> createFromForm(@ModelAttribute CreateOrderRequest req) { ... }
}
```

## Common Mapping Configuration Patterns
```java
// Base class for versioned controllers
@RestController
@RequestMapping(
    value = "/api/v1",
    produces = MediaType.APPLICATION_JSON_VALUE
)
public abstract class BaseV1Controller {}

@RequestMapping("/orders")
public class OrderV1Controller extends BaseV1Controller {
    // effective: /api/v1/orders
}

// Spring CORS configuration at controller level
@RestController
@RequestMapping("/api/orders")
@CrossOrigin(origins = "https://app.example.com", maxAge = 3600)
public class OrderController { ... }

// Global CORS configuration (preferred)
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://app.example.com")
            .allowedMethods("GET", "POST", "PUT", "DELETE", "PATCH")
            .allowedHeaders("*")
            .maxAge(3600);
    }
}
```

## RequestMappingHandlerMapping — How Spring Resolves Requests
1. At startup: Spring scans all @Controller/@RestController beans and registers their @RequestMapping metadata.
2. On each request: `DispatcherServlet` delegates to `RequestMappingHandlerMapping` which finds the best matching handler method.
3. Specificity wins: `/api/orders/active` is more specific than `/api/orders/{id}` — exact matches beat patterns.
4. Ambiguity: if two methods match equally, Spring throws `AmbiguousHandlerMethodMappingException`.

```java
// Order of specificity (most → least):
// 1. Exact path + exact method + header/param conditions
// 2. Exact path + exact method
// 3. Pattern match (wildcard/path variable) + method
// 4. Pattern match only
@GetMapping("/active")  // takes priority over /{id} for GET /orders/active
public List<OrderDto> getActive() { ... }

@GetMapping("/{id}")    // matches everything else
public OrderDto getById(@PathVariable String id) { ... }
```

## Common Mistakes
1. **Ambiguous mappings:** two methods with the same URL + method → startup error. One must add headers/params condition.
2. **Missing class-level @RequestMapping:** copying the full path in every method instead of using class-level base path.
3. **Method not allowed confusion:** endpoint exists but with wrong HTTP method → 405 Not Allowed (not 404).
4. **CORS misconfiguration:** missing @CrossOrigin or WebMvcConfigurer causes browser preflight failures silently appearing as network errors.
""",
"mcqs": [
  {"id":"d45q1","prompt":"What does `@GetMapping('/{id:[0-9]+}')` match?","options":["All paths with any {id}","Only paths where {id} consists entirely of digits — e.g., /123 but not /abc or /12x","Paths starting with a digit","IDs longer than 9 characters"],"correctAnswer":"Only paths where {id} consists entirely of digits — e.g., /123 but not /abc or /12x","explanation":"Regex in path variables: {id:[0-9]+} requires id to match the regex [0-9]+ (one or more digits). /123 matches; /abc doesn't (returns 404, not a 400 — the path just doesn't match this method). Useful for distinguishing numeric IDs from named paths like /active."},
  {"id":"d45q2","prompt":"If a controller has both `@GetMapping('/active')` and `@GetMapping('/{id}')`, which matches `GET /api/orders/active`?","options":["{id} matches because 'active' is a valid string","Both match — Spring picks randomly","/active is more specific — exact matches take priority over pattern matches like {id}","Spring throws AmbiguousHandlerMethodMappingException"],"correctAnswer":"/active is more specific — exact matches take priority over pattern matches like {id}","explanation":"Spring's request mapping uses specificity: exact path > path with variables > wildcards. /active matches exactly; /{id} is a pattern. GET /orders/active → handled by @GetMapping('/active'). GET /orders/xyz → handled by @GetMapping('/{id}')."},
  {"id":"d45q3","prompt":"What is API versioning via URL path (`/api/v1/orders` vs `/api/v2/orders`) and its main trade-off?","options":["Fastest versioning method","Most visible and easiest to test — URLs are bookmarkable and work in browsers; trade-off: URL changes break REST principle that URIs should be stable","Required by HTTP specification","Only approach supported by Spring Boot"],"correctAnswer":"Most visible and easiest to test — URLs are bookmarkable and work in browsers; trade-off: URL changes break REST principle that URIs should be stable","explanation":"URL path versioning: developer-friendly (test in browser, Postman, curl with no special headers). Trade-off: URI should identify a resource, not its version. /api/v1/orders and /api/v2/orders are the same resource in two formats. Header versioning (Accept: application/vnd.api.v2+json) is more RESTful but harder to test."},
  {"id":"d45q4","prompt":"What does `@GetMapping(headers = 'X-API-Version=2')` match?","options":["Requests with any X-API-Version header","Only requests where the X-API-Version header has the value '2'","Requests without any headers","GET requests to any path"],"correctAnswer":"Only requests where the X-API-Version header has the value '2'","explanation":"headers condition restricts matching by header value. GET /api/orders with header X-API-Version: 2 → matches. Without the header or with a different value → doesn't match this method (Spring tries other handlers or returns 404/405)."},
  {"id":"d45q5","prompt":"What HTTP status code does Spring return when a URL matches but the HTTP method doesn't?","options":["404 Not Found","405 Method Not Allowed — the resource exists but does not support the requested HTTP method","400 Bad Request","500 Internal Server Error"],"correctAnswer":"405 Method Not Allowed — the resource exists but does not support the requested HTTP method","explanation":"404: the URL pattern doesn't match any handler. 405: the URL matches a handler, but the HTTP method (GET/POST/PUT/DELETE) doesn't match any method on that handler. Spring also adds an Allow response header listing the supported methods."},
  {"id":"d45q6","prompt":"How does `@CrossOrigin(origins = 'https://app.example.com')` help a browser-based Angular app?","options":["Adds authentication to the API","Allows the browser's CORS preflight request to succeed — without it, browsers block cross-origin API calls from JavaScript","Encrypts cross-origin requests","Required for HTTP/2"],"correctAnswer":"Allows the browser's CORS preflight request to succeed — without it, browsers block cross-origin API calls from JavaScript","explanation":"CORS (Cross-Origin Resource Sharing): browsers block JS requests to different origins (protocol+domain+port) unless the server sends Access-Control-Allow-Origin headers. @CrossOrigin adds these headers. Without CORS config, Angular app at https://app.example.com can't call https://api.example.com from JavaScript."},
  {"id":"d45q7","prompt":"What is `AmbiguousHandlerMethodMappingException` and when does it occur?","options":["When a path variable has an ambiguous type","At startup when two handler methods have equally specific mappings for the same URL+method combination — Spring cannot determine which to call","When the request body can't be parsed","When @RequestMapping is used without a value"],"correctAnswer":"At startup when two handler methods have equally specific mappings for the same URL+method combination — Spring cannot determine which to call","explanation":"Spring validates mappings at startup. If two methods match GET /api/orders with equal specificity, it throws AmbiguousHandlerMethodMappingException. Fix: differentiate with headers=, params=, produces=, or path patterns. This is a startup failure (fail-fast) not a runtime error."},
  {"id":"d45q8","prompt":"What is the purpose of class-level `@RequestMapping('/api/v1/orders')`?","options":["Restricts the class to one endpoint","Defines a base path that all method-level mappings append to — avoids repeating the base path in every method annotation","Sets the API version for documentation","Required for Spring MVC to detect the controller"],"correctAnswer":"Defines a base path that all method-level mappings append to — avoids repeating the base path in every method annotation","explanation":"Class-level: @RequestMapping('/api/v1/orders'). Method: @GetMapping('/{id}'). Effective URL: /api/v1/orders/{id}. Without class-level mapping, every method would need @GetMapping('/api/v1/orders/{id}'). Class-level also lets you change the base path in one place."},
  {"id":"d45q9","prompt":"What does `@GetMapping(params = 'type=express')` match?","options":["All GET requests","GET requests to any URL with query parameter type=express","GET requests without a type parameter","GET requests with any type parameter"],"correctAnswer":"GET requests to any URL with query parameter type=express","explanation":"params condition restricts by query parameter value. GET /api/orders?type=express matches; GET /api/orders?type=standard doesn't match this method. Useful for routing requests with different params to different handler methods without complex if-else logic."},
  {"id":"d45q10","prompt":"In Spring's request matching, what takes highest priority for choosing a handler method?","options":["Alphabetical order","Most specific match: exact path + HTTP method + header/param conditions beats patterns","First registered handler wins","Most recently added handler"],"correctAnswer":"Most specific match: exact path + HTTP method + header/param conditions beats patterns","explanation":"Specificity order: 1) exact path + method + all conditions, 2) exact path + method, 3) path pattern + method, 4) path pattern only. Spring's HandlerMapping scores each candidate and picks the highest score. Two methods with the same score → AmbiguousHandlerMethodMappingException."}
],
"writtenConceptQuestions": [
  "Show a complete @RestController demonstrating class-level @RequestMapping and 5 methods with different HTTP methods, path variables, and request params.",
  "Explain the 4 API versioning strategies (URL path, header, media type, request param). Show each as a Spring Boot mapping. Which do you recommend and why?",
  "What URL patterns does Spring support? Show exact, path variable, wildcard (*), double wildcard (**), and regex constraints in path variables.",
  "What is CORS and why does it matter for Angular → Spring Boot API calls? Show both @CrossOrigin and global WebMvcConfigurer CORS configuration.",
  "Explain RequestMappingHandlerMapping specificity rules. Show a case where /active and /{id} coexist correctly, and a case that causes AmbiguousHandlerMethodMappingException.",
  "Show mapping conditions: headers=, params=, consumes=, produces=. Show a controller that handles the same URL path differently based on Accept header.",
  "What HTTP status codes does Spring return for: URL not found, URL exists but wrong HTTP method, request body deserialization failure, validation failure?"
],
"businessScenarios": [
  "An API has /api/orders and needs to launch a breaking v2 with a different response format. Design URL path versioning (/v1 and /v2) using class-level @RequestMapping with shared service layer — no code duplication in business logic.",
  "An Angular SPA on https://shop.example.com calls https://api.shop.example.com. All API calls fail silently in the browser with CORS preflight errors. Add global CORS configuration that allows the front-end origin.",
  "A payment endpoint has two methods both mapped to POST /api/payments — one for JSON, one for form data. Fix the ambiguity using consumes condition and show how Spring routes each request to the correct method."
]
}

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
