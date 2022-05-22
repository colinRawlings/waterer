import { Injectable, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NotifierService } from 'angular-notifier';
import { EnvService } from './env.service';
import {
  interval,
  Observable,
  Subject,
} from 'rxjs';

interface keyable {
  [key: string]: any;
}

@Injectable({
  providedIn: 'root'
})
export class ConstantsService {

  private isReadySubject: Subject<boolean>;
  public isReady$: Observable<boolean>;
  public isReady: boolean;

  public numChannels: number = 0;
  public kBackendURL: string;

  constructor(
    private env: EnvService,
    private notifierService: NotifierService,
    private http: HttpClient) {

    console.log(`Constructing constants service`);

    this.isReady = false;
    this.isReadySubject = new Subject<boolean>();
    this.isReady$ = this.isReadySubject.asObservable();

    this.numChannels = 0;

    this.kBackendURL = `http://${env.apiUrl}/`;
  }

  public Init(): void {
    this.http.get(this.kBackendURL).subscribe(
      (data: keyable) => {
        this.numChannels = data.num_pumps;
        this.isReady = true;
        this.isReadySubject.next(this.isReady);
        console.log(`Init'd constants service`);
      },
      (err) => this.notifierService.notify('error', `HTTP Error:  ${err.message}`)
    )

  }

}
