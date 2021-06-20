import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NotifierService } from 'angular-notifier';
import { PumpStatusService } from '../pump-status.service';
import { ConstantsService } from '../constants.service';

interface keyable {
  [key: string]: any;
}

@Component({
  selector: 'app-manual-pump-controls',
  templateUrl: './manual-pump-controls.component.html',
  styleUrls: ['./manual-pump-controls.component.css'],
})
export class ManualPumpControlsComponent implements OnInit {

  @Input()
  channel: number;

  ngOnInit(): void {}

  constructor(
    private http: HttpClient,
    private notifierService: NotifierService,
    private statusService: PumpStatusService,
    private constantsService: ConstantsService
  ) {}

  onTurnOn(): void {
    this.http.get(`${this.constantsService.kBackendURL}turn_on/${this.channel}`).subscribe(
      (data: keyable) => {
        this.notifierService.notify('success', `Turned on pump ${this.channel}`);
      },
      (error: keyable) => {
        this.notifierService.notify('error', `Turn On Error:  ${error.message}`);
      }
    );
  }

  onTurnOff(): void {
    this.http.get(`${this.constantsService.kBackendURL}turn_off/${this.channel}`).subscribe(
      (data: keyable) => {
        this.notifierService.notify('success', `Turned off pump ${this.channel}`);
      },
      (error: keyable) => {
        this.notifierService.notify('error', `Turn-Off Error:  ${error.message}`);
      }
    );
  }

  onGetStatus(): void {
    this.statusService.getStatus(this.channel).subscribe(
      (data: keyable) => {
        this.notifierService.notify(
          'success',
          `Channel ${this.channel}: ${JSON.stringify(data.data)}`
        );
      },
      (error: keyable) => {
        this.notifierService.notify('error', `getStatus Error:  ${error.message}`);
      }
    );
  }
}
