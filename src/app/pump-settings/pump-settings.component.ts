import { Component, Input, OnInit } from '@angular/core';
import { NotifierService } from 'angular-notifier';
import { PumpSettingsService } from '../pump-settings.service';
import { PumpStatusService } from '../pump-status.service';

interface keyable {
  [key: string]: any;
}

@Component({
  selector: 'app-pump-settings',
  templateUrl: './pump-settings.component.html',
  styleUrls: ['./pump-settings.component.css']
})
export class PumpSettingsComponent implements OnInit {

  @Input()
  channel: number;

  constructor(private notifierService: NotifierService, private settingsService: PumpSettingsService, private statusService: PumpStatusService) {
    this.settings = {};
  }

  settings: keyable;

  private status: keyable;

  ngOnInit(): void {
    this.settingsService.allSettings$[this.channel].subscribe(
      (data: keyable) => {
        this.settings = data.data;
      }
    )

    this.settingsService.updateSettings(this.channel);

    this.statusService.statuses$[this.channel].subscribe((data: keyable) => {
      this.status = data.data;
    });
  }

  onTakeCurrentHumidityAsDry(): void {
    this.settings.dry_humidity_V = this.status.rel_humidity_V;
    this.onSettingsChange();
  }

  onTakeCurrentHumidityAsWet(): void {
    this.settings.wet_humidity_V = this.status.rel_humidity_V;
    this.onSettingsChange();
  }

  onSettingsChange(): void {
    this.settingsService.setSettings(this.channel, this.settings).subscribe(
      (data: keyable) => {
        this.settings = data.data;
        this.notifierService.notify('success', `${this.channel}: Settings updated`);
        this.settingsService.updateSettings(this.channel);
      },
      (error: keyable) => {
        this.notifierService.notify('error', `setSettings Error:  ${error.message}`);
      }
    )
  }

}
