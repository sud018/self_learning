import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter, Routes } from '@angular/router';
import { AppComponent } from './app/app.component';
import { DashboardComponent } from './app/pages/dashboard/dashboard.component';
import { DailyAssignmentComponent } from './app/pages/daily-assignment/daily-assignment.component';
import { RoadmapComponent } from './app/pages/roadmap/roadmap.component';
import { CodingPracticeComponent } from './app/pages/coding-practice/coding-practice.component';
import { MissedDayComponent } from './app/pages/missed-day/missed-day.component';

const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'daily', component: DailyAssignmentComponent },
  { path: 'roadmap', component: RoadmapComponent },
  { path: 'coding', component: CodingPracticeComponent },
  { path: 'missed-day', component: MissedDayComponent },
  { path: '**', redirectTo: 'dashboard' }
];

bootstrapApplication(AppComponent, {
  providers: [provideRouter(routes), provideHttpClient()]
}).catch((error) => console.error(error));
