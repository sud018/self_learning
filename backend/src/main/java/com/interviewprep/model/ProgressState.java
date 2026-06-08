package com.interviewprep.model;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ProgressState {
  public String email;
  public int totalPoints;
  public int weeklyPoints;
  public int monthlyPoints;
  public int streakCount;
  public int missedDays;
  public int completedDays;
  public LocalDate lastCompletedDate;
  public List<String> completedAssignmentIds = new ArrayList<>();
  public List<String> solvedCodingProblemIds = new ArrayList<>();
  public Map<String, Integer> progress = new HashMap<>();
  public List<PointEvent> events = new ArrayList<>();
  public List<MissedDay> missedDayReasons = new ArrayList<>();
  public List<MissedAssignment> missedAssignments = new ArrayList<>();

  public static ProgressState fresh(String email) {
    ProgressState state = new ProgressState();
    state.email = email;
    state.progress.put("Java", 0);
    state.progress.put("Spring Boot", 0);
    state.progress.put("Angular", 0);
    state.progress.put("SQL", 0);
    state.progress.put("Data Structures", 0);
    return state;
  }

  public record PointEvent(LocalDate date, String source, int points) {}
  public record MissedDay(LocalDate date, String reason, boolean excused, int penalty) {}
  public record MissedAssignment(String assignmentId, LocalDate date, String reason, boolean excused, int penalty) {}
}
