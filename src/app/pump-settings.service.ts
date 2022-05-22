import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ConstantsService } from './constants.service';
import { NotifierService } from 'angular-notifier';

import {
  Observable,
  Subject,
  Subscription,
} from 'rxjs';

interface keyable {
  [key: string]: any;
}

@Injectable({
  providedIn: 'root',
})
export class PumpSettingsService {

  private isReadySubject: Subject<boolean>;
  public isReady$: Observable<boolean>;
  public isReady: boolean;

  private constantsIsReadySubscription: Subscription;


  private settingsSubjects: Subject<keyable>[] = [];
  public allSettings$: Observable<keyable>[] = [];

  constructor(
    private http: HttpClient,
    private constantsService: ConstantsService,
    private notifierService: NotifierService) {

    console.log(`Constructing settings service`);

    this.isReady = false;
    this.isReadySubject = new Subject<boolean>();
    this.isReady$ = this.isReadySubject.asObservable();

    if (constantsService.isReady) {
      this.Init();
    } else {
      this.constantsIsReadySubscription = constantsService.isReady$.subscribe((constantsIsReady: boolean)=>{
        if(!constantsIsReady) console.error("Constants notified not-ready");
        this.constantsIsReadySubscription.unsubscribe();
        this.Init();
      })
      this.constantsService.Init();
    }
  }

  public Init(): void {
    for (let p = 0; p < this.constantsService.numChannels; ++p) {
      this.settingsSubjects.push(new Subject<keyable>());
      this.allSettings$.push(this.settingsSubjects[p].asObservable());
    }

    this.isReady = true;
    this.isReadySubject.next(this.isReady);
    console.log(`Init'd settings service`);
  }

  public updateSettings(channel: number): void {
    this.getSettings(channel).subscribe(data => {
      this.settingsSubjects[channel].next(data)
    },
      (error: keyable) => {
        this.notifierService.notify('error', `getSettings Error:  ${error.message}`);
      })
  }

  private getSettings(channel: number): Observable<keyable> {
    return this.http.get(`${this.constantsService.kBackendURL}settings/${channel}`);
  }

  setSettings(channel: number, settings: keyable): Observable<keyable> {
    return this.http.post(`${this.constantsService.kBackendURL}set_settings/${channel}`, settings);
  }
}
