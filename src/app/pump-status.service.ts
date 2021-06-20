import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { interval, Observable, Observer, Subject, Subscription, throwError } from 'rxjs';
import { NotifierService } from 'angular-notifier';
import { ConstantsService } from './constants.service';

import { map, concatAll, retry } from 'rxjs/operators';

interface keyable {
  [key: string]: any;
}

@Injectable({
  providedIn: 'root',
})
export class PumpStatusService {

  private statusSubjects: Subject<keyable>[] = [];
  public statuses$: Observable<keyable>[] = [];
  private subscriptionsMap: keyable = {};

  constructor(
    private http: HttpClient,
    private notifierService: NotifierService,
    private constantsService: ConstantsService,
  ) {
    for (let p=0; p< this.constantsService.kNumChannels;++p){
      this.statusSubjects.push(new Subject<keyable>());
      this.statuses$.push(this.statusSubjects[p].asObservable())
    }
  }

  //

  getStatus(channel: number): Observable<keyable> {
    return this.http.get(`${this.constantsService.kBackendURL}status/${channel}`);
  }

  startDataStream(): void {
    for (let channel = 0; channel < this.constantsService.kNumChannels; channel++) {
      this.subscriptionsMap[`${channel}`] = this.getStatusStream(channel).subscribe((data: keyable) => {
        this.statusSubjects[channel].next(data);
      });
    }
  }

  stopDataStream(): void {
    for (let channel = 0; channel < this.constantsService.kNumChannels; channel++) {
    this.subscriptionsMap[`${channel}`].unsubscribe();
    }
  }

  getStatusStream(channel: number) {
    return interval(5000).pipe(
      map((index: number) => {
        return this.http.get(`${this.constantsService.kBackendURL}status/${channel}`);
      }),
      concatAll(), retry()
    );
  }
}
