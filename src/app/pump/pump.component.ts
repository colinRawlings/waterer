import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface keyable {
  [key: string]: any;
}

@Component({
  selector: 'app-pump',
  templateUrl: './pump.component.html',
  styleUrls: ['./pump.component.css'],
})
export class PumpComponent implements OnInit {
  public x: number[] = [];
  public y: number[] = [];
  graph = {
    data: [{ x: this.x, y: this.y, type: 'scatter' }],
    layout: {
      autosize: true,
      title: 'Voltage',
      font: { family: 'Roboto, "Helvetica Neue", sans-serif' },
      margin: { t: 50, b: 20, l: 40, r: 40 },
    },
  };

  @Input()
  channel: number;

  ngOnInit(): void {
    this.http
      .get(`http://127.0.0.1:5000/settings/${this.channel}`)
      .subscribe((data: keyable) => {
        this.settings = data.data;
      });
  }

  voltage: number;
  counter: number;
  settings: keyable;

  constructor(private http: HttpClient) {
    this.settings = {};
    this.voltage = -1;
    this.counter = 0;
  }

  onTurnOn(): void {
    this.http
      .get(`http://127.0.0.1:5000/turn_on/${this.channel}`)
      .subscribe((data: keyable) => {});
  }

  onTurnOff(): void {
    this.http
      .get(`http://127.0.0.1:5000/turn_off/${this.channel}`)
      .subscribe((data: keyable) => {});
  }

  onSettingsChange(): void{
    console.log(`Feedback: ${this.settings.feedback_active}`);
  }

}
