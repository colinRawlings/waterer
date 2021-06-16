import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NotifierService } from 'angular-notifier';

interface keyable {
  [key: string]: any  
}
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {

  private readonly notifier: NotifierService;

  title = 'waterer';
  public autoUpdate: boolean;
  public autoSwitchGraphs: boolean;


  connect_info: string;

  constructor(private http: HttpClient, notifierService: NotifierService) {  
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
  };

  onAutoUpdateChange(): void{
    this.notifier.notify('success', 'You are awesome! I mean it!');
    // TODO
  };

  onAutoSwitchGraphsChange(): void{
    // TODO 
  };
}
