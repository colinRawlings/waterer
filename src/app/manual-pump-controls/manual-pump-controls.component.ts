import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NotifierService } from 'angular-notifier';
import { PumpStatusService } from '../pump-status.service';

interface keyable {
  [key: string]: any;
}

@Component({
  selector: 'app-manual-pump-controls',
  templateUrl: './manual-pump-controls.component.html',
  styleUrls: ['./manual-pump-controls.component.css'],
})
export class ManualPumpControlsComponent implements OnInit {
  private readonly notifier: NotifierService;

  @Input()
  channel: number;

  ngOnInit(): void {}

  constructor(private http: HttpClient, notifierService: NotifierService, private statusService: PumpStatusService) {
    this.notifier = notifierService;
  }

  onTurnOn(): void {
    this.http.get(`http://127.0.0.1:5000/turn_on/${this.channel}`).subscribe(
      (data: keyable) => {
        this.notifier.notify('success', `Turned on pump ${this.channel}`);
      },
      (error: keyable) => {
        this.notifier.notify('error', `Turn On Error:  ${error.message}`);
      }
    );
  }

  onTurnOff(): void {
    this.http.get(`http://127.0.0.1:5000/turn_off/${this.channel}`).subscribe(
      (data: keyable) => {
        this.notifier.notify('success', `Turned off pump ${this.channel}`);
      },
      (error: keyable) => {
        this.notifier.notify('error', `Turn-Off Error:  ${error.message}`);
      }
    );
  }

  onGetStatus(): void{
    this.statusService.getStatus(this.channel).subscribe(
      (data: keyable) => {
        this.notifier.notify('success', `Channel ${this.channel}: ${JSON.stringify(data.data)}`);
      },
      (error: keyable) => {
        this.notifier.notify('error', `getStatus Error:  ${error.message}`);
      }
    )
  }
}
