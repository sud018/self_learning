import { Injectable, computed } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class UserContextService {
  readonly email = computed(() => 'personal-user');
}
