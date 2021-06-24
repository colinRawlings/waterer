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
  public rel_humidity_V: number[] = [];
  public rel_humidity_V_epoch_time: Date[] = [];

  public rel_humidity_pcnt: number[] = [];
  public rel_humidity_pcnt_epoch_time: Date[] = [];

  public pump_running: number[] = [];
  public pump_running_epoch_time: Date[] = [];

  public display_voltage: boolean;
  private kHumidityColor = 'rgb(0, 0, 200)';
  private kPumpColor = 'rgb(50, 200, 50)';
  private kHumidityMarker = {
    color: this.kHumidityColor,
  };

  private resetGraphCounter = 0;
  private resetGraphInterval = 1000;

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
    data: [{}, {}],
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
        x: this.rel_humidity_V_epoch_time.slice(),
        y: this.rel_humidity_V.slice(),
        type: 'scatter',
        name: 'humidity',
        marker: this.kHumidityMarker,
      });
    } else {
      data.push({
        x: this.rel_humidity_pcnt_epoch_time.slice(),
        y: this.rel_humidity_pcnt.slice(),
        type: 'scatter',
        name: 'humidity',
        marker: this.kHumidityMarker,
      });
    }

    data.push({
      x: this.pump_running_epoch_time.slice(),
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
    if (pump_status) {
      return 1;
    } else {
      return 0;
    }
  }

  appendPumpRunningSample(sample: boolean): void {
    this.pump_running.push(this.castPumpStatus(sample));
  }

  castEpochTimesToDates(times: number[]): Date[]{
    let dates=[];

    for (const time of times) {
      dates.push(new Date(time));
    }

    return dates;
  }

  onResetGraph():void{
    this.rel_humidity_V = [];
    this.rel_humidity_V_epoch_time = [];
  
    this.rel_humidity_pcnt = [];
    this.rel_humidity_pcnt_epoch_time = [];
  
    this.pump_running = [];
    this.pump_running_epoch_time = [];

    this.resetGraphCounter=0;
    this.statusService.lastUpdateTime[this.channel]=null;
  }

  onReceivedStatusData(data: keyable): void {

    if (this.resetGraphCounter==this.resetGraphInterval){
      this.onResetGraph();
      return;
    }

    this.resetGraphCounter += 1;

    this.rel_humidity_V = this.rel_humidity_V.concat(data.data.rel_humidity_V);
    this.rel_humidity_V_epoch_time = this.rel_humidity_V_epoch_time.concat(
      this.castEpochTimesToDates(data.data.rel_humidity_V_epoch_time)
    );

    this.rel_humidity_pcnt = this.rel_humidity_pcnt.concat(
      data.data.rel_humidity_pcnt
    );
    this.rel_humidity_pcnt_epoch_time =
      this.rel_humidity_pcnt_epoch_time.concat(
        this.castEpochTimesToDates(data.data.rel_humidity_pcnt_epoch_time)
      );

    const lastIndex = this.pump_running.length - 1;

    const new_pump_times = this.castEpochTimesToDates(data.data.pump_running_epoch_time);


    if (
      lastIndex > 2 &&
      this.pump_running[lastIndex - 1] == this.pump_running[lastIndex] &&
      data.data.pump_running.length > 0 &&
      this.pump_running[lastIndex] == data.data.pump_running[0]
    ) {
      if (data.data.pump_running.length == 1) {
        this.pump_running_epoch_time[lastIndex] =
          new_pump_times[0];
      } else {
        this.pump_running_epoch_time[lastIndex] =
          new_pump_times[0];
        this.pump_running = this.pump_running.concat(
          data.data.pump_running.slice(1)
        );
        this.pump_running_epoch_time = this.pump_running_epoch_time.concat(
          new_pump_times.slice(1)
        );
      }
    } else {
      this.pump_running = this.pump_running.concat(data.data.pump_running);
      this.pump_running_epoch_time = this.pump_running_epoch_time.concat(
        new_pump_times
      );
    }

    this.updateGraph();
  }
}
