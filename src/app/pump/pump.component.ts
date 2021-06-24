import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
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
  public humidity_time: Date[] = [];
  public pump_status_time: Date[] = [];

  public rel_humidity_V: number[] = [];
  public rel_humidity_pcnt: number[] = [];
  public pump_running: number[] = [];
  public display_voltage: boolean;
  private kHumidityColor = 'rgb(0, 0, 200)';
  private kPumpColor = 'rgb(50, 200, 50)';
  private kHumidityMarker = {
    color: this.kHumidityColor,
  };

  private kLayout = {
    autosize: true,
    title: 'pump',
    yaxis: {
      title: 'Humidity',
      titlefont: { color: this.kHumidityColor },
      tickfont: { color: this.kHumidityColor },
    },
    yaxis2: {
      title: 'Pump Running',
      titlefont: { color: this.kPumpColor },
      tickfont: { color: this.kPumpColor },
      overlaying: 'y',
      side: 'right',
      range: [0, 1],
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
        x: this.humidity_time,
        y: this.rel_humidity_V,
        type: 'scatter',
        name: 'humidity',
        marker: {
          color: this.kHumidityColor,
        },
      },
      {
        x: this.pump_status_time,
        y: this.pump_running,
        type: 'scatter',
        yaxis: 'y2',
        name: 'running',
        marker: {
          color: this.kPumpColor,
        },
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
        x: this.humidity_time.slice(),
        y: this.rel_humidity_V.slice(),
        type: 'scatter',
        name: 'humidity',
        marker: this.kHumidityMarker,
      });
    } else {
      data.push({
        x: this.humidity_time.slice(),
        y: this.rel_humidity_pcnt.slice(),
        type: 'scatter',
        name: 'humidity',
        marker: this.kHumidityMarker,
      });
    }

    data.push({
      x: this.pump_status_time.slice(),
      y: this.pump_running.slice(),
      type: 'scatter',
      yaxis: 'y2',
      name: 'running',
      marker: {
        color: this.kPumpColor,
      },
    });

    this.graph = { data: data, layout: this.kLayout, config: this.kConfig };
  }

  onDisplayVoltageChange(): void {
    this.updateGraph();
  }

  castPumpStatus(pump_status: boolean): number {
    if(pump_status){
      return 1;
    } else {
      return 0;
    }
  }

  appendPumpRunningSample(sample: boolean): void {
    this.pump_running.push(this.castPumpStatus(sample));
  }

  onReceivedStatusData(data: keyable): void {
    this.status = data.data;

    this.humidity_time.push(new Date(this.status.epoch_time * 1000));
    this.rel_humidity_V.push(this.status.rel_humidity_V);
    this.rel_humidity_pcnt.push(this.status.rel_humidity_pcnt);

    const lastIndex = this.pump_running.length - 1;
    if (lastIndex < 2) {
      this.pump_status_time.push(new Date(this.status.epoch_time * 1000));
      this.appendPumpRunningSample(this.status.pump_running);
    } else {
      if (this.pump_running[lastIndex] == this.castPumpStatus(this.status.pump_status)) {
        this.pump_status_time[lastIndex] = new Date(
          this.status.epoch_time * 1000
        );
      } else {
        this.pump_status_time.push(new Date(this.status.epoch_time * 1000));
        this.appendPumpRunningSample(this.status.pump_running);
      }
    }

    this.updateGraph();
  }
}
