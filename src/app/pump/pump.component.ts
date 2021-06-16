import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { update } from 'plotly.js-dist';

interface keyable {
  [key: string]: any;
}

@Component({
  selector: 'app-pump',
  templateUrl: './pump.component.html',
  styleUrls: ['./pump.component.css'],
})
export class PumpComponent implements OnInit {
  public time: number[] = [];
  public rel_humidity_V: number[] = [];
  public rel_humidity_pcnt: number[] = [];
  public display_voltage: boolean;

  graph = {
    data: [{ x: this.time, y: this.rel_humidity_V, type: 'scatter' }],
    layout: {
      autosize: true,
      title: 'Voltage',
      font: { family: 'Roboto, "Helvetica Neue", sans-serif' },
      margin: { t: 50, b: 20, l: 40, r: 40 },
    },
    config: {
      responsive: true
    }
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

  status: keyable;
  settings: keyable;

  constructor(private http: HttpClient) {
    this.settings = {};
    this.status = {};
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

  // Settings: TODO spread to own component

  onSettingsChange(): void {
    console.log(`Feedback: ${this.settings.feedback_active}`);
  }

  onTakeCurrentHumidityAsDry(): void{
    console.log(`TODO: take dry`);
  }

  onTakeCurrentHumidityAsWet(): void{
    console.log(`TODO: take wet`);
  }

  // Graph

  updateGraph(): void{
    if (this.display_voltage) {
      this.graph.data = [
        {
          x: this.time.slice(),
          y: this.rel_humidity_V.slice(),
          type: 'scatter',
        },
      ];
    } else {
      this.graph.data = [
        {
          x: this.time.slice(),
          y: this.rel_humidity_pcnt.slice(),
          type: 'scatter',
        },
      ];
    }
  };

  onDisplayVoltageChange(): void{
    this.updateGraph();
  };

  onGetStatus(): void {
    this.http
      .get(`http://127.0.0.1:5000/status/${this.channel}`)
      .subscribe((data: keyable) => {
        this.status = data.data;

        this.time.push(this.status.epoch_time);
        this.rel_humidity_V.push(this.status.rel_humidity_V);
        this.rel_humidity_pcnt.push(this.status.rel_humidity_pcnt);

        this.updateGraph();
      });
  }


}
