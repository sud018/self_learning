package com.interviewprep.controller;

import com.interviewprep.model.ReviewModels.DayReview;
import com.interviewprep.model.ReviewModels.SaveDayReviewRequest;
import com.interviewprep.service.ReviewService;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/review")
public class ReviewController {

  private final ReviewService reviewService;

  public ReviewController(ReviewService reviewService) {
    this.reviewService = reviewService;
  }

  @PostMapping
  DayReview save(@RequestBody SaveDayReviewRequest request) {
    return reviewService.save(request);
  }

  @GetMapping
  ResponseEntity<DayReview> get(@RequestParam String email, @RequestParam String dayId) {
    DayReview review = reviewService.findByEmailAndDay(email, dayId);
    return review != null ? ResponseEntity.ok(review) : ResponseEntity.notFound().build();
  }

  @GetMapping("/all")
  List<DayReview> all(@RequestParam String email) {
    return reviewService.findAllByEmail(email);
  }
}
