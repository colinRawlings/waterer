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

  private numChannelsSubject: Subject<number>;
  public numChannels$: Observable<number>;
  public numChannels: number = -1;

  public kBackendURL: string;

  constructor(
    private env: EnvService,
    private notifierService: NotifierService,
    private http: HttpClient) {

    this.numChannelsSubject = new Subject<number>();
    this.numChannels$ = this.numChannelsSubject.asObservable();
    this.numChannels = -1;

    this.kBackendURL = `http://${env.apiUrl}/`;
  }
  
  public update(): void{
    this.http.get(this.kBackendURL).subscribe(
      (data: keyable) => {
        this.numChannels = data.num_pumps;
        this.numChannelsSubject.next(this.numChannels);
      },
      (err) => this.notifierService.notify('error', `HTTP Error:  ${err.message}`)
    )
    
  }

}
