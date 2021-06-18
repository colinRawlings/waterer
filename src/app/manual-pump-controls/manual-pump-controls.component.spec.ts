import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManualPumpControlsComponent } from './manual-pump-controls.component';

describe('ManualPumpControlsComponent', () => {
  let component: ManualPumpControlsComponent;
  let fixture: ComponentFixture<ManualPumpControlsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ManualPumpControlsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ManualPumpControlsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
