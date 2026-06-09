package com.interviewprep.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.interviewprep.model.Dashboard;
import com.interviewprep.model.ProgressState;
import com.interviewprep.model.ProgressState.MissedAssignment;
import com.interviewprep.model.ProgressState.MissedDay;
import com.interviewprep.model.ProgressState.PointEvent;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import org.springframework.stereotype.Service;

@Service
public class ProgressService {
  private static final String PROGRESS_FILE = "progress.txt";
  private static final int DAILY_TARGET = 100;
  private static final Set<String> VALID_REASONS = Set.of(
      "health issue", "emergency", "work priority", "family emergency", "travel", "internet", "system issue");
  private final FileStore fileStore;

  public ProgressService(FileStore fileStore) {
    this.fileStore = fileStore;
  }

  public ProgressState ensureProgress(String email) {
    return find(email).map(this::normalize).orElseGet(() -> {
      ProgressState state = ProgressState.fresh(email);
      save(state);
      return state;
    });
  }

  public Dashboard dashboard(String email) {
    ProgressState state = ensureProgress(email);
    int earnedToday = state.events.stream()
        .filter(event -> event.date().equals(LocalDate.now()) && event.points() > 0)
        .mapToInt(PointEvent::points)
        .sum();
    int lostToday = state.events.stream()
        .filter(event -> event.date().equals(LocalDate.now()) && event.points() < 0)
        .mapToInt(PointEvent::points)
        .sum();
    int progressAverage = (int) state.progress.values().stream().mapToInt(Integer::intValue).average().orElse(0);
    int readiness = Math.min(100, (progressAverage + state.streakCount * 3 + state.completedDays * 2) / 2);
    return new Dashboard(DAILY_TARGET, earnedToday, Math.abs(lostToday), state.totalPoints, state.weeklyPoints,
        state.monthlyPoints, state.streakCount, state.missedDays, state.completedDays, readiness, state.progress);
  }

  public ProgressState addPoints(String email, String source, int points) {
    ProgressState state = ensureProgress(email);
    state.totalPoints += points;
    state.weeklyPoints += points;
    state.monthlyPoints += points;
    state.events.add(new PointEvent(LocalDate.now(), source, points));
    save(state);
    return state;
  }

  public boolean hasPointEvent(String email, String source) {
    return ensureProgress(email).events.stream()
        .anyMatch(event -> event.source().equalsIgnoreCase(source));
  }

  public List<String> solvedCodingProblemIds(String email) {
    return new ArrayList<>(ensureProgress(email).solvedCodingProblemIds);
  }

  public boolean markCodingProblemSolved(String email, String problemId) {
    ProgressState state = ensureProgress(email);
    if (state.solvedCodingProblemIds.contains(problemId)) {
      return false;
    }
    state.solvedCodingProblemIds.add(problemId);
    save(state);
    return true;
  }

  public boolean hasCompletedAssignment(String email, String assignmentId) {
    return ensureProgress(email).completedAssignmentIds.contains(assignmentId);
  }

  public boolean hasMissedAssignment(String email, String assignmentId) {
    return missedAssignment(email, assignmentId).isPresent();
  }

  public Optional<MissedAssignment> missedAssignment(String email, String assignmentId) {
    return ensureProgress(email).missedAssignments.stream()
        .filter(missed -> missed.assignmentId().equals(assignmentId))
        .findFirst();
  }

  public ProgressState completeDay(String email, String assignmentId, int earned, int lost) {
    ProgressState state = ensureProgress(email);
    if (state.completedAssignmentIds.contains(assignmentId)) {
      return state;
    }
    state.totalPoints += earned - lost;
    state.weeklyPoints += earned - lost;
    state.monthlyPoints += earned - lost;
    state.events.add(new PointEvent(LocalDate.now(), "Daily assignment", earned));
    if (lost > 0) {
      state.events.add(new PointEvent(LocalDate.now(), "Low score penalty", -lost));
    }
    state.completedDays++;
    if (state.lastCompletedDate != null && state.lastCompletedDate.equals(LocalDate.now().minusDays(1))) {
      state.streakCount++;
    } else if (state.lastCompletedDate == null || !state.lastCompletedDate.equals(LocalDate.now())) {
      state.streakCount = 1;
    }
    if (state.streakCount > 0 && state.streakCount % 5 == 0) {
      state.totalPoints += 50;
      state.weeklyPoints += 50;
      state.monthlyPoints += 50;
      state.events.add(new PointEvent(LocalDate.now(), "5 day streak bonus", 50));
    }
    state.lastCompletedDate = LocalDate.now();
    state.completedAssignmentIds.add(assignmentId);
    state.progress.replaceAll((name, value) -> Math.min(100, value + 3));
    save(state);
    return state;
  }

  public MissedDayResult missedDay(String email, String reason) {
    ProgressState state = ensureProgress(email);
    boolean excused = isValidReason(reason);
    int penalty = excused ? 0 : 30;
    if (!excused) {
      state.totalPoints -= penalty;
      state.weeklyPoints -= penalty;
      state.monthlyPoints -= penalty;
      state.missedDays++;
      state.events.add(new PointEvent(LocalDate.now(), "Missed day penalty", -penalty));
    }
    state.missedDayReasons.add(new MissedDay(LocalDate.now(), reason, excused, penalty));
    save(state);
    return new MissedDayResult(excused, penalty, state.totalPoints);
  }

  public MissedDayResult missedDay(String email, String assignmentId, String reason) {
    ProgressState state = ensureProgress(email);
    Optional<MissedAssignment> existing = state.missedAssignments.stream()
        .filter(missed -> missed.assignmentId().equals(assignmentId))
        .findFirst();
    if (existing.isPresent()) {
      MissedAssignment missed = existing.get();
      return new MissedDayResult(missed.excused(), missed.penalty(), state.totalPoints);
    }

    boolean excused = isValidReason(reason);
    int penalty = excused ? 0 : 30;
    if (!excused) {
      state.totalPoints -= penalty;
      state.weeklyPoints -= penalty;
      state.monthlyPoints -= penalty;
      state.events.add(new PointEvent(LocalDate.now(), "Missed day penalty: " + assignmentId, -penalty));
    }
    state.missedDays++;
    state.missedAssignments.add(new MissedAssignment(assignmentId, LocalDate.now(), reason, excused, penalty));
    state.missedDayReasons.add(new MissedDay(LocalDate.now(), reason, excused, penalty));
    save(state);
    return new MissedDayResult(excused, penalty, state.totalPoints);
  }

  public void resetProgress(String email) {
    List<ProgressState> states = new ArrayList<>(all());
    states.removeIf(existing -> existing.email.equalsIgnoreCase(email));
    fileStore.writeList(PROGRESS_FILE, states);
  }

  private boolean isValidReason(String reason) {
    String normalized = reason == null ? "" : reason.toLowerCase();
    return VALID_REASONS.stream().anyMatch(normalized::contains);
  }

  private Optional<ProgressState> find(String email) {
    return all().stream().filter(state -> state.email.equalsIgnoreCase(email)).findFirst();
  }

  private void save(ProgressState state) {
    List<ProgressState> states = new ArrayList<>(all());
    states.removeIf(existing -> existing.email.equalsIgnoreCase(state.email));
    states.add(state);
    fileStore.writeList(PROGRESS_FILE, states);
  }

  private List<ProgressState> all() {
    return fileStore.readList(PROGRESS_FILE, new TypeReference<>() {});
  }

  private ProgressState normalize(ProgressState state) {
    if (state.completedAssignmentIds == null) {
      state.completedAssignmentIds = new ArrayList<>();
    }
    if (state.solvedCodingProblemIds == null) {
      state.solvedCodingProblemIds = new ArrayList<>();
    }
    if (state.events == null) {
      state.events = new ArrayList<>();
    }
    if (state.missedDayReasons == null) {
      state.missedDayReasons = new ArrayList<>();
    }
    if (state.missedAssignments == null) {
      state.missedAssignments = new ArrayList<>();
    }
    if (state.progress == null || hasNoActivity(state)) {
      state.progress = ProgressState.fresh(state.email).progress;
      save(state);
    }
    return state;
  }

  private boolean hasNoActivity(ProgressState state) {
    return state.totalPoints == 0
        && state.weeklyPoints == 0
        && state.monthlyPoints == 0
        && state.streakCount == 0
        && state.missedDays == 0
        && state.completedDays == 0
        && state.lastCompletedDate == null
        && state.completedAssignmentIds.isEmpty()
        && state.solvedCodingProblemIds.isEmpty()
        && state.events.isEmpty()
        && state.missedDayReasons.isEmpty()
        && state.missedAssignments.isEmpty();
  }

  public record MissedDayResult(boolean excused, int penalty, int totalPoints) {}
}
