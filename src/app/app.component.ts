import { Component, OnDestroy, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NotifierService } from 'angular-notifier';
import { PumpStatusService } from './pump-status.service';

interface keyable {
  [key: string]: any  
}
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {

  private readonly notifier: NotifierService;

  title = 'waterer';
  public autoUpdate: boolean;
  public autoSwitchGraphs: boolean;


  connect_info: string;

  constructor(private http: HttpClient, notifierService: NotifierService, private statusService: PumpStatusService) {  
    this.connect_info = "";
    this.autoUpdate = true;

    this.notifier = notifierService;
  }

  ngOnInit(): void {
    this.http.get('http://127.0.0.1:5000/')
    .subscribe((data:keyable)=>{
      this.connect_info = `${data.data}`;
    },
    err => this.notifier.notify('error',`HTTP Error:  ${err.message}`)
    )

    this.onAutoUpdateChange();

  };

  ngOnDestroy(): void{
    this.statusService.stopDataStream();
  }

  onAutoUpdateChange(): void{
    if (this.autoUpdate){
      this.statusService.startDataStream();
    } else {
      this.statusService.stopDataStream();
    }
  };

  onAutoSwitchGraphsChange(): void{
    // TODO 
  };
}
