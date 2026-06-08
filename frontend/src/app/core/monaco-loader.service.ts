import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class MonacoLoaderService {
  private promise: Promise<void> | null = null;

  load(): Promise<void> {
    if (this.promise) return this.promise;
    this.promise = new Promise<void>((resolve, reject) => {
      if ((window as any).monaco) { resolve(); return; }
      const script = document.createElement('script');
      script.src = '/vs/loader.js';
      script.onload = () => {
        (window as any).require.config({ paths: { vs: '/vs' } });
        (window as any).require(['vs/editor/editor.main'], () => resolve());
      };
      script.onerror = () => reject(new Error('Monaco loader.js failed to load'));
      document.head.appendChild(script);
    });
    return this.promise;
  }
}
