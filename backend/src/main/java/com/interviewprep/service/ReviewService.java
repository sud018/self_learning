package com.interviewprep.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.interviewprep.model.ReviewModels.DayReview;
import com.interviewprep.model.ReviewModels.DraftAnswers;
import com.interviewprep.model.ReviewModels.SaveDayReviewRequest;
import com.interviewprep.model.ReviewModels.SaveDraftRequest;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class ReviewService {

  private final Path reviewsDir;
  private final ObjectMapper mapper;

  public ReviewService(@Value("${app.data-dir}") String dataDir) throws IOException {
    this.reviewsDir = Path.of(dataDir).resolve("reviews");
    Files.createDirectories(reviewsDir);
    this.mapper = new ObjectMapper().registerModule(new JavaTimeModule()).findAndRegisterModules();
  }

  public synchronized DayReview save(SaveDayReviewRequest req) {
    DayReview review = new DayReview(
        req.email(),
        req.dayId(),
        req.topic(),
        LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")),
        req.mcqScore(),
        req.mcqTotal(),
        req.mcqResults(),
        req.writtenAnswers()
    );
    Path file = fileFor(req.email(), req.dayId());
    try {
      mapper.writeValue(file.toFile(), review);
    } catch (IOException e) {
      throw new IllegalStateException("Could not save review for " + req.dayId(), e);
    }
    return review;
  }

  public DayReview findByEmailAndDay(String email, String dayId) {
    Path file = fileFor(email, dayId);
    if (!Files.exists(file)) return null;
    try {
      return mapper.readValue(file.toFile(), DayReview.class);
    } catch (IOException e) {
      return null;
    }
  }

  public List<DayReview> findAllByEmail(String email) {
    List<DayReview> results = new ArrayList<>();
    try (var paths = Files.list(reviewsDir)) {
      String prefix = sanitize(email) + "_";
      paths.filter(p -> p.getFileName().toString().startsWith(prefix))
           .sorted()
           .forEach(p -> {
             try {
               results.add(mapper.readValue(p.toFile(), DayReview.class));
             } catch (IOException ignored) {}
           });
    } catch (IOException e) {
      return results;
    }
    return results;
  }

  public synchronized void saveDraft(SaveDraftRequest req) {
    DraftAnswers draft = new DraftAnswers(
        req.email(), req.dayId(),
        LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")),
        req.writtenAnswers(), req.mcqAnswers(), req.notesCompleted(), req.sqlSolved()
    );
    try {
      mapper.writeValue(draftFileFor(req.email(), req.dayId()).toFile(), draft);
    } catch (IOException e) {
      throw new IllegalStateException("Could not save draft for " + req.dayId(), e);
    }
  }

  public DraftAnswers loadDraft(String email, String dayId) {
    Path file = draftFileFor(email, dayId);
    if (!Files.exists(file)) return null;
    try {
      return mapper.readValue(file.toFile(), DraftAnswers.class);
    } catch (IOException e) {
      return null;
    }
  }

  private Path fileFor(String email, String dayId) {
    return reviewsDir.resolve(sanitize(email) + "_" + sanitize(dayId) + ".json");
  }

  private Path draftFileFor(String email, String dayId) {
    return reviewsDir.resolve("draft_" + sanitize(email) + "_" + sanitize(dayId) + ".json");
  }

  private String sanitize(String s) {
    return s.replaceAll("[^a-zA-Z0-9._-]", "_");
  }
}
