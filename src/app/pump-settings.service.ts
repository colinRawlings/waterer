import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';

interface keyable {
  [key: string]: any;
}

@Injectable({
  providedIn: 'root',
})
export class PumpSettingsService {
  constructor(private http: HttpClient) {}

  getSettings(channel: number): Observable<keyable> {
    return this.http.get(`http://127.0.0.1:5000/settings/${channel}`);
  }

  setSettings(channel: number, settings: keyable): Observable<keyable> {
    return this.http.post(
      `http://127.0.0.1:5000/set_settings/${channel}`,
      settings
    );
  }

  // TODO: Set settings
}
