import { Component, OnDestroy, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ConstantsService } from './constants.service';
import { NotifierService } from 'angular-notifier';
import { PumpStatusService } from './pump-status.service';

interface keyable {
  [key: string]: any;
}
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit, OnDestroy {

  title = 'waterer';
  public autoUpdate: boolean;
  public autoSwitchGraphs: boolean;
  public channels: number[];

  connect_info: string;

  constructor(
    private http: HttpClient,
    private notifierService: NotifierService,
    private statusService: PumpStatusService,
    private constantsService: ConstantsService
  ) {
    this.connect_info = '';
    this.autoUpdate = true;
  }

  ngOnInit(): void {
    this.http.get(this.constantsService.kBackendURL).subscribe(
      (data: keyable) => {
        this.connect_info = `${data.data}`;
      },
      (err) => this.notifierService.notify('error', `HTTP Error:  ${err.message}`)
    );

    this.channels = [];
    for(let channel = 0; channel < this.constantsService.kNumChannels; channel++){
      this.channels.push(channel);
    }

    this.onAutoUpdateChange();
  }

  ngOnDestroy(): void {
    this.statusService.stopDataStream();
  }

  onAutoUpdateChange(): void {
    if (this.autoUpdate) {
      this.statusService.startDataStream();
    } else {
      this.statusService.stopDataStream();
    }
  }

  onAutoSwitchGraphsChange(): void {
    this.notifierService.notify("error", "TODO");
  }
}
