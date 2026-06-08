package com.interviewprep.model;

import java.util.List;

public record Assignment(
    String id,
    String topic,
    String notes,
    List<Question> conceptualQuestions,
    List<String> writtenConceptQuestions,
    List<String> businessScenarios,
    List<DsaProblem> dsaPractice,
    List<CodingTask> codingTasks,
    List<String> sqlPractice,
    List<String> springBootScenarios,
    List<String> angularQuestions
) {
  public record Question(String id, String prompt, List<String> options, String correctAnswer, String explanation) {}
  public record DsaProblem(
      String id,
      String title,
      String difficulty,
      String statement,
      List<String> examples,
      List<String> constraints,
      List<String> hints,
      String expectedTimeComplexity,
      String expectedSpaceComplexity
  ) {}
  public record CodingTask(
      String id,
      String category,
      String difficulty,
      String title,
      String statement,
      List<String> examples,
      List<String> constraints,
      List<String> testCases,
      int targetMinutes,
      String starterCode
  ) {}
}
