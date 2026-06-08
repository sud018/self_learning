import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../core/api.service';

@Component({
  selector: 'app-roadmap',
  imports: [CommonModule],
  template: `
    <section class="page">
      <div class="page-header">
        <div>
          <h1>Learning Roadmap</h1>
          <p>Beginner basics to interview-ready Java full-stack coverage.</p>
        </div>
      </div>
      @if (loading) {
        <article class="card empty-state">
          <h2>Loading roadmap...</h2>
          <p>Getting the Java full-stack learning modules.</p>
        </article>
      }
      @if (error) {
        <article class="card warning empty-state">
          <h2>Backend API is not reachable</h2>
          <p>{{ error }}</p>
        </article>
      }
      <div class="grid roadmap">
        @for (module of modules; track module.name) {
          <article class="card">
            <h2>{{ module.name }}</h2>
            <ul class="topic-list">
              @for (topic of module.topics; track topic) {
                <li>{{ topic }}</li>
              }
            </ul>
          </article>
        }
      </div>
    </section>
  `
})
export class RoadmapComponent implements OnInit {
  modules: any[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService, private cd: ChangeDetectorRef) {}

  ngOnInit() {
    this.api.roadmap().subscribe({
      next: (modules) => {
        this.modules = modules;
        this.loading = false;
        this.cd.detectChanges();
      },
      error: () => {
        this.loading = false;
        this.error = 'Start the Spring Boot backend on port 8082, then refresh this page.';
        this.cd.detectChanges();
      }
    });
  }
}
