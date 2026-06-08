package com.interviewprep.model;

import java.util.Map;

public record Dashboard(
    int todaysTargetPoints,
    int earnedToday,
    int lostToday,
    int totalPoints,
    int weeklyPoints,
    int monthlyPoints,
    int streakCount,
    int missedDays,
    int completedDays,
    int interviewReadiness,
    Map<String, Integer> progress
) {}
