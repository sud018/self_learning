package com.interviewprep.model;

import java.util.List;

public class AttemptModels {
  public record Answer(String questionId, String answer) {}
  public record SubmitAssignmentRequest(String email, String assignmentId, boolean notesCompleted, List<Answer> answers, int codingSolved, int sqlSolved) {}
  public record SubmitAssignmentResponse(int scorePercent, int earnedPoints, int lostPoints, int totalPoints, boolean nextAssignmentAvailable, List<String> feedback) {}
  public record MissedDayRequest(String email, String assignmentId, String reason) {}
  public record MissedDayResponse(boolean excused, int penalty, int totalPoints, String message) {}
  public record DayStatusResponse(String assignmentId, int dayNumber, String topic, String status, String reason, boolean excused, int penalty) {}
}
