import { TestBed } from '@angular/core/testing';

import { PumpSettingsService } from './pump-settings.service';

describe('PumpSettingsService', () => {
  let service: PumpSettingsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PumpSettingsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
