import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ConstantsService } from './constants.service';
import { NotifierService } from 'angular-notifier';

import {
  Observable,
  Subject,
} from 'rxjs';

interface keyable {
  [key: string]: any;
}

@Injectable({
  providedIn: 'root',
})
export class PumpSettingsService {

  // TODO follow the pattern in the status service to have
  // subscriptions to subjects not observables so that new
  // values can be pushed to components ... 

  private settingsSubjects: Subject<keyable>[] = [];
  public allSettings$: Observable<keyable>[] = [];

  constructor(
    private http: HttpClient,
    private constantsService: ConstantsService,
    private notifierService: NotifierService) {
    for (let p = 0; p < this.constantsService.kNumChannels; ++p) {
      this.settingsSubjects.push(new Subject<keyable>());
      this.allSettings$.push(this.settingsSubjects[p].asObservable());
    }
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
