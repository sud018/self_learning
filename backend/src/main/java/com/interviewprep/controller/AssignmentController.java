package com.interviewprep.controller;

import com.interviewprep.model.Assignment;
import com.interviewprep.model.AttemptModels.DayStatusResponse;
import com.interviewprep.model.AttemptModels.MissedDayRequest;
import com.interviewprep.model.AttemptModels.MissedDayResponse;
import com.interviewprep.model.AttemptModels.SubmitAssignmentRequest;
import com.interviewprep.model.AttemptModels.SubmitAssignmentResponse;
import com.interviewprep.model.ProgressState.MissedAssignment;
import com.interviewprep.service.AssignmentService;
import com.interviewprep.service.ProgressService;
import com.interviewprep.service.ProgressService.MissedDayResult;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/assignments")
public class AssignmentController {
  private final AssignmentService assignmentService;
  private final ProgressService progressService;

  public AssignmentController(AssignmentService assignmentService, ProgressService progressService) {
    this.assignmentService = assignmentService;
    this.progressService = progressService;
  }

  @GetMapping("/today")
  Assignment today(@RequestParam String email) {
    return assignmentService.nextForUser(email);
  }

  @GetMapping("/load")
  Assignment load(@RequestParam String email, @RequestParam String assignmentId) {
    return assignmentService.assignments().stream()
        .filter(a -> a.id().equals(assignmentId))
        .findFirst()
        .orElseThrow(() -> new IllegalArgumentException("Unknown assignment: " + assignmentId));
  }

  @GetMapping("/day-status")
  List<DayStatusResponse> dayStatus(@RequestParam String email) {
    List<Assignment> assignments = assignmentService.assignments();
    List<DayStatusResponse> statuses = new ArrayList<>();
    for (int index = 0; index < assignments.size(); index++) {
      Assignment assignment = assignments.get(index);
      Optional<MissedAssignment> missed = progressService.missedAssignment(email, assignment.id());
      String status = "pending";
      String reason = "";
      boolean excused = false;
      int penalty = 0;
      if (progressService.hasCompletedAssignment(email, assignment.id())) {
        status = "done";
      } else if (missed.isPresent()) {
        status = "missed";
        reason = missed.get().reason();
        excused = missed.get().excused();
        penalty = missed.get().penalty();
      }
      statuses.add(new DayStatusResponse(assignment.id(), index + 1, assignment.topic(), status, reason, excused, penalty));
    }
    return statuses;
  }

  @PostMapping("/submit")
  SubmitAssignmentResponse submit(@RequestBody SubmitAssignmentRequest request) {
    return assignmentService.submit(request.email(), request.assignmentId(), request.notesCompleted(), request.answers(), request.codingSolved(), request.sqlSolved());
  }

  @PostMapping("/reset-progress")
  void resetProgress(@RequestParam String email) {
    progressService.resetProgress(email);
  }

  @PostMapping("/missed-day")
  MissedDayResponse missedDay(@RequestBody MissedDayRequest request) {
    String assignmentId = request.assignmentId();
    if (assignmentId == null || assignmentId.isBlank()) {
      assignmentId = assignmentService.nextForUser(request.email()).id();
    }
    MissedDayResult result = progressService.missedDay(request.email(), assignmentId, request.reason());
    String message = result.excused()
        ? "Reason accepted. Day marked missed with 0 point penalty."
        : "Reason marked invalid. Day marked missed and a 30 point penalty was applied.";
    return new MissedDayResponse(result.excused(), result.penalty(), result.totalPoints(), message);
  }
}
