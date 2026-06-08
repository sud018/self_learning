package com.interviewprep.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.interviewprep.model.Assignment;
import com.interviewprep.model.Assignment.Question;
import com.interviewprep.model.AttemptModels.Answer;
import com.interviewprep.model.AttemptModels.SubmitAssignmentResponse;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class AssignmentService {
  private final ProgressService progressService;
  private final Path curriculumDir;
  private final ObjectMapper mapper;

  public AssignmentService(ProgressService progressService, @Value("${app.data-dir}") String dataDir) {
    this.progressService = progressService;
    this.curriculumDir = Path.of(dataDir).resolve("curriculum");
    this.mapper = new ObjectMapper().registerModule(new JavaTimeModule()).findAndRegisterModules();
  }

  public Assignment nextForUser(String email) {
    return assignments().stream()
        .filter(assignment -> !progressService.hasCompletedAssignment(email, assignment.id())
            && !progressService.hasMissedAssignment(email, assignment.id()))
        .findFirst()
        .orElse(assignments().get(assignments().size() - 1));
  }

  public boolean hasUncompletedAssignment(String email) {
    return assignments().stream()
        .anyMatch(assignment -> !progressService.hasCompletedAssignment(email, assignment.id())
            && !progressService.hasMissedAssignment(email, assignment.id()));
  }

  public List<Assignment> assignments() {
    if (!Files.exists(curriculumDir)) {
      throw new IllegalStateException("Curriculum folder not found: " + curriculumDir);
    }
    try (var paths = Files.list(curriculumDir)) {
      List<Assignment> assignments = paths
          .filter(path -> path.getFileName().toString().matches("day-\\d{3}\\.json"))
          .sorted(Comparator.comparing(path -> path.getFileName().toString()))
          .map(this::readAssignment)
          .toList();
      if (assignments.isEmpty()) {
        throw new IllegalStateException("No day-XXX.json curriculum files found in " + curriculumDir);
      }
      return assignments;
    } catch (IOException error) {
      throw new IllegalStateException("Could not read curriculum files", error);
    }
  }

  public SubmitAssignmentResponse submit(String email, String assignmentId, boolean notesCompleted, List<Answer> answers, int codingSolved, int sqlSolved) {
    Assignment assignment = assignments().stream()
        .filter(item -> item.id().equals(assignmentId))
        .findFirst()
        .orElseThrow(() -> new IllegalArgumentException("Unknown assignment"));

    if (progressService.hasCompletedAssignment(email, assignmentId)) {
      return new SubmitAssignmentResponse(100, 0, 0, progressService.ensureProgress(email).totalPoints,
          hasUncompletedAssignment(email), List.of("You already completed this day. Load the next day to continue."));
    }

    int correct = 0;
    List<String> feedback = new ArrayList<>();
    for (Question question : assignment.conceptualQuestions()) {
      String submitted = answers.stream()
          .filter(answer -> answer.questionId().equals(question.id()))
          .map(Answer::answer)
          .findFirst()
          .orElse("");
      if (question.correctAnswer().equalsIgnoreCase(submitted)) {
        correct++;
      } else {
        feedback.add(question.prompt() + " Correct answer: " + question.correctAnswer() + ". " + question.explanation());
      }
    }

    int score = (int) Math.round((correct * 100.0) / assignment.conceptualQuestions().size());
    int safeSqlSolved = Math.max(0, Math.min(sqlSolved, assignment.sqlPractice().size()));
    int earned = 0;
    if (notesCompleted) earned += 10;
    if (score >= 60) earned += 20;
    earned += safeSqlSolved * 15;
    if (notesCompleted && score >= 60 && safeSqlSolved > 0) earned += 25;
    int lost = score < 50 ? 10 : 0;
    int total = progressService.completeDay(email, assignmentId, earned, lost).totalPoints;
    if (feedback.isEmpty()) {
      feedback.add("Strong attempt. Load the next day when you are ready.");
    }
    return new SubmitAssignmentResponse(score, earned, lost, total, hasUncompletedAssignment(email), feedback);
  }

  private Assignment readAssignment(Path path) {
    try {
      return mapper.readValue(path.toFile(), Assignment.class);
    } catch (IOException error) {
      throw new IllegalStateException("Could not read curriculum file " + path.getFileName(), error);
    }
  }
}
