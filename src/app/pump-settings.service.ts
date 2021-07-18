import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { ConstantsService } from './constants.service';

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

  constructor(private http: HttpClient, private constantsService: ConstantsService) {}

  getSettings(channel: number): Observable<keyable> {
    return this.http.get(`${this.constantsService.kBackendURL}settings/${channel}`);
  }

  setSettings(channel: number, settings: keyable): Observable<keyable> {
    return this.http.post(`${this.constantsService.kBackendURL}set_settings/${channel}`, settings);
  }

  // TODO: Set settings
}
