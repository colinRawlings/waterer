import { Injectable, Optional } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {
  interval,
  Observable,
  Subject,
  Subscription,
} from 'rxjs';
import { NotifierService } from 'angular-notifier';
import { ConstantsService } from './constants.service';
// import { assert } from 'console';

import { map, concatAll, retry } from 'rxjs/operators';

interface keyable {
  [key: string]: any;
}

type Nullable<T> = T | null;

@Injectable({
  providedIn: 'root',
})
export class PumpStatusService {

  private isReadySubject: Subject<boolean>;
  public isReady$: Observable<boolean>;
  public isReady: boolean;
  
  private constantsIsReadySubscription: Subscription;

  //

  private statusSubjects: Subject<keyable>[] = [];
  public statuses$: Observable<keyable>[] = [];
  private subscriptionsMap: keyable = {};

  public lastUpdateTime: Nullable<number>[] = [];

  constructor(
    private http: HttpClient,
    private notifierService: NotifierService,
    private constantsService: ConstantsService
  ) {

    console.log(`Constructing status service`);

    this.isReady = false;
    this.isReadySubject = new Subject<boolean>();
    this.isReady$ = this.isReadySubject.asObservable();

    if (constantsService.isReady) {
      this.Init();
    } else {
      this.constantsIsReadySubscription = constantsService.isReady$.subscribe((constantsIsReady: boolean) => {
        if(!constantsIsReady) console.error("Constants notified not-ready");
        this.constantsIsReadySubscription.unsubscribe();
        this.Init();
      })
      this.constantsService.Init();
    }

  }

  public Init(): void {
    for (let p = 0; p < this.constantsService.numChannels; ++p) {
      this.statusSubjects.push(new Subject<keyable>());
      this.statuses$.push(this.statusSubjects[p].asObservable());
      this.lastUpdateTime.push(null);
    }

    this.isReady = true;
    this.isReadySubject.next(this.isReady);
    console.log('Init d status service');
  }


  //

  getStatus(channel: number): Observable<keyable> {
    return this.http.get(
      `${this.constantsService.kBackendURL}status/${channel}`
    );
  }

  clearStatusHistory(channel: number): Observable<keyable> {
    return this.http.get(
      `${this.constantsService.kBackendURL}clear_status/${channel}`
    );
  }

  getStatusHistory(
    channel: number,
    earliest_time: number
  ): Observable<keyable> {
    return this.http.post(
      `${this.constantsService.kBackendURL}get_status_since/${channel}`,
      { earliest_time: null }
    );
  }

  startDataStream(): void {
    if(!this.isReady) console.error('status service was not ready for startDataStream');
  
    for (
      let channel = 0;
      channel < this.constantsService.numChannels;
      channel++
    ) {
      this.subscriptionsMap[`${channel}`] = this.getStatusStream(
        channel
      ).subscribe((data: keyable) => {
        this.statusSubjects[channel].next(data);
      });
    }
  }

  stopDataStream(): void {
    if(!this.isReady) console.error('status service was not ready for stopDataStream');

    for (
      let channel = 0;
      channel < this.constantsService.numChannels;
      channel++
    ) {
      this.subscriptionsMap[`${channel}`].unsubscribe();
    }
  }

  getStatusStream(channel: number) {
    if(!this.isReady) console.error('status service was not ready for getStatusStream');

    return interval(5000).pipe(
      map((index: number) => {

        const earliest_time = this.lastUpdateTime[channel];
        this.lastUpdateTime[channel] = Date.now() * 0.001;

        return this.http.post(
          `${this.constantsService.kBackendURL}get_status_since/${channel}`,
          { earliest_time: earliest_time }
        );
      }),
      concatAll(),
      retry()
    );
  }
}
