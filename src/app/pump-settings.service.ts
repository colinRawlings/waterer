import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';

interface keyable {
  [key: string]: any;
}

@Injectable({
  providedIn: 'root'
})
export class PumpSettingsService {

  constructor(private http: HttpClient) { }

  getSettings(channel: number): Observable<keyable>{
    return this.http.get(`http://127.0.0.1:5000/settings/${channel}`);
  }

  // TODO: Set settings
}
