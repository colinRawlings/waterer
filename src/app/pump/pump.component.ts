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

  public x: number[] = []
  public y: number[] = []
  graph = {
    data: [
      { x: this.x, y: this.y, type: 'scatter' },
    ],
    layout: {
      autosize: true,
      title: 'Voltage',
      font: { family: 'Roboto, "Helvetica Neue", sans-serif' },
      margin: { t: 50, b: 20, l: 40, r: 40 },
    }
  };
  
  @Input()
  channel:number; 

  connect_info: string;
  result: string;
  voltage: number;
  counter: number;

  constructor(private http: HttpClient) {
    this.connect_info = "";
    this.result="";
    this.voltage=-1;
    this.counter=0;
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

  onGetVoltage(): void{
    this.http.get('http://127.0.0.1:5000/get_voltage')
    .subscribe((data:keyable)=>{
      this.voltage = data.data;
       
      this.counter += 1;

      this.x.push(this.counter);
      this.y.push(this.voltage);

      this.graph.data = [{ x: this.x.slice(), y: this.y.slice(), type: 'scatter' }]

    })
  }

}
