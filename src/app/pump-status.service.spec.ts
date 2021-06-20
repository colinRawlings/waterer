import { TestBed } from '@angular/core/testing';

import { PumpStatusService } from './pump-status.service';

describe('PumpStatusService', () => {
  let service: PumpStatusService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PumpStatusService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
