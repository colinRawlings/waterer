import { Component, OnDestroy, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ConstantsService } from './constants.service';
import { NotifierService } from 'angular-notifier';
import { PumpStatusService } from './pump-status.service';
import packageInfo  from '../../package.json';

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

  public arduino_address: string;
  public frontend_version: string = packageInfo.version;
  public backend_version: string;

  constructor(
    private http: HttpClient,
    private notifierService: NotifierService,
    private statusService: PumpStatusService,
    private constantsService: ConstantsService
  ) {
    this.arduino_address = '';
    this.autoUpdate = true;
  }

  ngOnInit(): void {
    this.http.get(this.constantsService.kBackendURL).subscribe(
      (data: keyable) => {
        this.arduino_address = `${data.data.arduino_address}`;
        this.backend_version = `${data.data.version}`;
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

  onSaveUserSettings(): void {
    this.http.get(`${this.constantsService.kBackendURL}save_settings`).subscribe(
      (data: keyable) => {
        this.notifierService.notify('success', `Saved settings to ${data.data}`);
      },
      (err) => this.notifierService.notify('error', `HTTP Error:  ${err.message}`)
    );
  }

  onSaveHistory(): void {
    this.http.get(`${this.constantsService.kBackendURL}save_history`).subscribe(
      (data: keyable) => {
        this.notifierService.notify('success', `Saved history to ${data.data}`);
      },
      (err) => this.notifierService.notify('error', `HTTP Error:  ${err.message}`)
    );
  }
}
