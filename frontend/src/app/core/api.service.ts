import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  dashboard(email: string) {
    return this.get<any>('/dashboard', { email });
  }

  todayAssignment(email: string) {
    return this.get<any>('/assignments/today', { email });
  }

  loadAssignment(email: string, assignmentId: string) {
    return this.get<any>('/assignments/load', { email, assignmentId });
  }

  submitAssignment(payload: any) {
    return this.post<any>('/assignments/submit', payload);
  }

  dayStatus(email: string) {
    return this.get<any[]>('/assignments/day-status', { email });
  }

  missedDay(payload: { email: string; assignmentId?: string; reason: string }) {
    return this.post<any>('/assignments/missed-day', payload);
  }

  roadmap() {
    return this.get<any[]>('/roadmap');
  }

  codingProblems() {
    return this.get<any[]>('/coding/problems');
  }

  codingProgress(email: string) {
    return this.get<{ solvedProblemIds: string[] }>('/coding/progress', { email });
  }

  markCodingSolved(payload: { email: string; problemId: string }) {
    return this.post<{ solvedProblemIds: string[] }>('/coding/mark-solved', payload);
  }

  runCode(payload: { email: string; problemId: string; code: string }) {
    return this.post<any>('/coding/run', payload);
  }

  submitCode(payload: { email: string; problemId: string; code: string }) {
    return this.post<any>('/coding/submit', payload);
  }

  saveDayReview(payload: {
    email: string; dayId: string; topic: string;
    mcqScore: number; mcqTotal: number;
    mcqResults: any[]; writtenAnswers: Record<string, string>;
  }) {
    return this.post<any>('/review', payload);
  }

  getDayReview(email: string, dayId: string) {
    return this.get<any>('/review', { email, dayId });
  }

  resetProgress(email: string) {
    const url = `${environment.apiUrl}/assignments/reset-progress?email=${encodeURIComponent(email)}`;
    return new Observable<void>((subscriber) => {
      fetch(url, { method: 'POST' })
        .then((res) => {
          if (!res.ok) throw new Error(`Reset failed: ${res.status}`);
          subscriber.next();
          subscriber.complete();
        })
        .catch((err) => subscriber.error(err));
    });
  }

  getAllReviews(email: string) {
    return this.get<any[]>('/review/all', { email });
  }

  private get<T>(path: string, params: Record<string, string> = {}) {
    const query = new URLSearchParams(params).toString();
    const url = `${environment.apiUrl}${path}${query ? `?${query}` : ''}`;
    return this.request<T>(url);
  }

  private post<T>(path: string, payload: unknown) {
    return this.request<T>(`${environment.apiUrl}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  }

  private request<T>(url: string, options: RequestInit = {}) {
    return new Observable<T>((subscriber) => {
      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), 8000);

      fetch(url, { ...options, signal: controller.signal })
        .then(async (response) => {
          if (!response.ok) {
            let message = `API failed: ${response.status} ${response.statusText}`;
            try {
              const errorBody = await response.json();
              message = errorBody?.message || message;
            } catch {
            }
            throw new Error(message);
          }
          return response.json() as Promise<T>;
        })
        .then((data) => {
          subscriber.next(data);
          subscriber.complete();
        })
        .catch((error) => subscriber.error(error))
        .finally(() => window.clearTimeout(timeoutId));

      return () => {
        window.clearTimeout(timeoutId);
        controller.abort();
      };
    });
  }
}
