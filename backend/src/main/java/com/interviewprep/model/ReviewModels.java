package com.interviewprep.model;

import java.util.List;
import java.util.Map;

public class ReviewModels {

  public record McqResult(
      String questionId,
      String prompt,
      String userAnswer,
      String correctAnswer,
      String explanation,
      boolean correct
  ) {}

  public record SaveDayReviewRequest(
      String email,
      String dayId,
      String topic,
      int mcqScore,
      int mcqTotal,
      List<McqResult> mcqResults,
      Map<String, String> writtenAnswers
  ) {}

  public record DayReview(
      String email,
      String dayId,
      String topic,
      String savedAt,
      int mcqScore,
      int mcqTotal,
      List<McqResult> mcqResults,
      Map<String, String> writtenAnswers
  ) {}
}
