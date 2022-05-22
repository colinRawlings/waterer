import { Component, OnDestroy, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ConstantsService } from './constants.service';
import { NotifierService } from 'angular-notifier';
import { PumpStatusService } from './pump-status.service';
import packageInfo from '../../package.json';
import { Subscription } from 'rxjs';

interface keyable {
  [key: string]: any;
}
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit, OnDestroy {

  private constantsIsReadySubscription: Subscription;
  private statusIsReadySubscription: Subscription;

  //

  title = 'waterer';
  public autoUpdate: boolean;
  public autoSwitchGraphs: boolean;
  public channels: number[] = [];
  public numChannels: number = 0;

  public devices: string[];
  public frontend_version: string = packageInfo.version;
  public backend_version: string;

  constructor(
    private http: HttpClient,
    private notifierService: NotifierService,
    private statusService: PumpStatusService,
    private constantsService: ConstantsService
  ) {
    this.devices = [];
    this.autoUpdate = true;
  }

  ngOnInit(): void {

    console.log(`ngOnInit App Component`);

    if (this.constantsService.isReady) {
      this.Init();
    } else {
      this.constantsIsReadySubscription = this.constantsService.isReady$.subscribe((constantsIsReady: boolean) => {
        if(!constantsIsReady) console.error("Constants notified not-ready");
        this.constantsIsReadySubscription.unsubscribe();
        this.Init();
      })
      this.constantsService.Init();
    }

  }

  public Init(): void {
    this.channels = [];
    for (let channel = 0; channel < this.constantsService.numChannels; channel++) {
      this.channels.push(channel);
    }

    this.http.get(this.constantsService.kBackendURL).subscribe(
      (data: keyable) => {
        this.devices = data.device_info;
        this.backend_version = `${data.version}`;

        this.onAutoUpdateChange();
      },
      (err) => this.notifierService.notify('error', `HTTP Error:  ${err.message}`)
    );
  }

  ngOnDestroy(): void {
    this.statusService.stopDataStream();
  }

  onAutoUpdateChange(): void {
    if (this.statusService.isReady) {
      this.doAutoUpdateChange();
    } else {
      this.statusIsReadySubscription = this.statusService.isReady$.subscribe((statusIsReady: boolean) => {
        if(!statusIsReady) console.error("Status notified not-ready");
        this.statusIsReadySubscription.unsubscribe();
        this.doAutoUpdateChange();
      })
      this.statusService.Init();
    }
  }

  doAutoUpdateChange(): void {
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
