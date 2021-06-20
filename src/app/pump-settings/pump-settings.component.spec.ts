import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PumpSettingsComponent } from './pump-settings.component';

describe('PumpSettingsComponent', () => {
  let component: PumpSettingsComponent;
  let fixture: ComponentFixture<PumpSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PumpSettingsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PumpSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
