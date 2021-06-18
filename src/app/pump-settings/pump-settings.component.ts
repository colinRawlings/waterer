import { Component, Input, OnInit } from '@angular/core';
import { NotifierService } from 'angular-notifier';
import { PumpSettingsService } from '../pump-settings.service';

interface keyable {
  [key: string]: any;
}

@Component({
  selector: 'app-pump-settings',
  templateUrl: './pump-settings.component.html',
  styleUrls: ['./pump-settings.component.css']
})
export class PumpSettingsComponent implements OnInit {
  private readonly notifier: NotifierService;
  
  @Input()
  channel: number;

  constructor(notifierService: NotifierService, private settingsService: PumpSettingsService) {
    this.notifier = notifierService;
    this.settings = {};
  }

  settings: keyable;

  ngOnInit(): void {
    this.settingsService.getSettings(this.channel).subscribe(
      (data: keyable) => {
        this.settings = data.data;
      },
      (error: keyable) => {
        this.notifier.notify('error', `getSettings Error:  ${error.message}`);
      }
    )
  }

  onTakeCurrentHumidityAsDry(): void{
    console.log(`TODO: take dry`);
  }

  onTakeCurrentHumidityAsWet(): void{
    console.log(`TODO: take wet`);
  }

  onSettingsChange(): void {
    console.log(`Feedback: ${this.settings.feedback_active}`);
  }

}
