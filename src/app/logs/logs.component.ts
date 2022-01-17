import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ConstantsService } from '../constants.service';
import { NotifierService } from 'angular-notifier';

interface keyable {
  [key: string]: any;
}
@Component({
  selector: 'app-logs',
  templateUrl: './logs.component.html',
  styleUrls: ['./logs.component.css']
})
export class LogsComponent implements OnInit {

  public numberLogLines: number = 100;
  public serviceLogs: string

  constructor(
    private http: HttpClient,
    private notifierService: NotifierService,
    private constantsService: ConstantsService
  ) { }

  ngOnInit(): void {
  }

onGetLogs():void{
  this.http.get(`${this.constantsService.kBackendURL}service_logs/${this.numberLogLines}`).subscribe(
    (data: keyable) => {
      this.notifierService.notify('success', `Updated service logs`);
      this.serviceLogs = data.data;
    },
    (err) => this.notifierService.notify('error', `HTTP Error:  ${err.message}`)
  );
}

}
