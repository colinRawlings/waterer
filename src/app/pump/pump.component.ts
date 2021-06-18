import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { update } from 'plotly.js-dist';
import { PumpStatusService } from '../pump-status.service';
import { NotifierService } from 'angular-notifier';

interface keyable {
  [key: string]: any;
}
@Component({
  selector: 'app-pump',
  templateUrl: './pump.component.html',
  styleUrls: ['./pump.component.css'],
})
export class PumpComponent implements OnInit {
  public time: Date[] = [];
  public rel_humidity_V: number[] = [];
  public rel_humidity_pcnt: number[] = [];
  public pump_running: number[] = [];
  public display_voltage: boolean;
  private kHumidityColor = 'rgb(0, 0, 200)'
  private kPumpColor = 'rgb(50, 200, 50)'

  private kLayout = {
    autosize: true,
    title: 'pump',
    yaxis: { title: 'Humidity' ,
    titlefont: { color: this.kHumidityColor },
    tickfont: { color: this.kHumidityColor },},
    yaxis2: {
      title: 'Pump Running',
      titlefont: { color: this.kPumpColor },
      tickfont: { color: this.kPumpColor },
      overlaying: 'y',
      side: 'right',
      range: [0, 1]
    },
    font: { family: 'Roboto, "Helvetica Neue", sans-serif' },
    margin: { t: 50, b: 100, l: 40, r: 40 },
  };

  private kConfig = {
    responsive: false,
  };

  graph = {
    data: [
      {
        x: this.time,
        y: this.rel_humidity_V,
        type: 'scatter',
        name: 'humidity',
        marker: {
          color: this.kHumidityColor,
        }
      },
      {
        x: this.time,
        y: this.pump_running,
        type: 'scatter',
        yaxis: 'y2',
        name: 'running',
        marker: {
          color: this.kPumpColor,
        }
      },
    ],
    layout: this.kLayout,
    config: this.kConfig,
  };

  @Input()
  channel: number;

  ngOnInit(): void {
    this.statusService.statuses$[this.channel].subscribe((data: keyable) => {
      this.onReceivedStatusData(data);
      // this.notifierService.notify('success',`${this.channel}: Data in pump-component:  ${data.data.rel_humidity_pcnt}`)
    });
  }

  status: keyable;

  constructor(
    private http: HttpClient,
    private notifierService: NotifierService,
    private statusService: PumpStatusService
  ) {
    this.status = {};
  }

  // Graph

  updateGraph(): void {
    let data = [];

    if (this.display_voltage) {
      data.push({
        x: this.time.slice(),
        y: this.rel_humidity_V.slice(),
        type: 'scatter',
        name: 'humidity',
        marker: {
          color: this.kHumidityColor,
        }
      });
    } else {
      data.push({
        x: this.time.slice(),
        y: this.rel_humidity_pcnt.slice(),
        type: 'scatter',
        name: 'humidity',
        marker: {
          color: this.kHumidityColor,
        }
      });
    }

    data.push({
      x: this.time.slice(),
      y: this.pump_running.slice(),
      type: 'scatter',
      yaxis: 'y2',
      name: 'running',
      marker: {
        color: this.kPumpColor,
      }
    });

    this.graph = { data: data, layout: this.kLayout, config: this.kConfig };
  }

  onDisplayVoltageChange(): void {
    this.updateGraph();
  }

  onReceivedStatusData(data: keyable): void {
    this.status = data.data;

    this.time.push(new Date(this.status.epoch_time * 1000));
    this.rel_humidity_V.push(this.status.rel_humidity_V);
    this.rel_humidity_pcnt.push(this.status.rel_humidity_pcnt);
    if (this.status.pump_running) {
      this.pump_running.push(1);
    } else {
      this.pump_running.push(0);
    }

    this.updateGraph();
  }

  onGetStatus(): void {
    this.http
      .get(`http://127.0.0.1:5000/status/${this.channel}`)
      .subscribe((data) => this.onReceivedStatusData(data));
  }
}
