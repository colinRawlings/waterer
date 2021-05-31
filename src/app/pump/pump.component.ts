import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';


interface keyable {
  [key: string]: any  
}

@Component({
  selector: 'app-pump',
  templateUrl: './pump.component.html',
  styleUrls: ['./pump.component.css']
})
export class PumpComponent implements OnInit {

  @Input()
  channel:number;

  connect_info: string;
  result: string;

  constructor(private http: HttpClient) {
    this.connect_info = "";
    this.result="";
  }

  ngOnInit(): void {
    this.http.get('http://127.0.0.1:5000/')
    .subscribe((data:keyable)=>{
      this.connect_info = `${data.data}`;
    })
  }

  onTurnOn(): void{
    this.http.get('http://127.0.0.1:5000/turn_on')
    .subscribe((data:keyable)=>{
      this.result = `${data.data}`;
    })
  }

  onTurnOff(): void{
    this.http.get('http://127.0.0.1:5000/turn_off')
    .subscribe((data:keyable)=>{
      this.result = `${data.data}`;
    })
  }

}
