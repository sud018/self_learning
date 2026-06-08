package com.interviewprep.service;

import com.interviewprep.model.RoadmapModels.RoadmapModule;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class RoadmapService {
  public List<RoadmapModule> roadmap() {
    return List.of(
        new RoadmapModule("Java", List.of("Basics", "OOP", "Collections", "Exceptions", "Streams", "Multithreading", "Java 8+", "Design patterns", "Interview coding")),
        new RoadmapModule("Spring Boot", List.of("REST APIs", "Dependency Injection", "Spring MVC", "JPA/Hibernate", "Security", "Validation", "Exception handling", "Microservices basics", "Kafka basics", "Testing", "Real-time scenarios")),
        new RoadmapModule("Angular", List.of("TypeScript basics", "Components", "Templates", "Directives", "Services", "Routing", "Forms", "HTTP calls", "Observables", "Authentication flow", "Interview UI tasks")),
        new RoadmapModule("SQL", List.of("Select queries", "Joins", "Group by", "Subqueries", "Indexes", "Transactions", "Interview queries")),
        new RoadmapModule("DSA", List.of("Arrays", "Strings", "HashMap", "Stack", "Queue", "Linked List", "Recursion", "Sorting", "Searching", "Trees basics", "Interview patterns"))
    );
  }
}
