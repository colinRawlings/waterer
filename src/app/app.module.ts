import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatTabsModule } from '@angular/material/tabs';
import { MatSliderModule } from '@angular/material/slider'
import { MatGridListModule } from '@angular/material/grid-list';
import {MatListModule} from '@angular/material/list';
import {MatIconModule} from '@angular/material/icon';
import { NotifierModule } from 'angular-notifier';
import { FlexLayoutModule } from "@angular/flex-layout";

import * as PlotlyJS from 'plotly.js-dist';
import { PlotlyModule } from 'angular-plotly.js';

import { AppComponent } from './app.component';
import { PumpComponent } from './pump/pump.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ManualPumpControlsComponent } from './manual-pump-controls/manual-pump-controls.component';
import { PumpSettingsComponent } from './pump-settings/pump-settings.component';
import { EnvServiceProvider } from './env.service.provider';

PlotlyModule.plotlyjs = PlotlyJS;

@NgModule({
  declarations: [AppComponent, PumpComponent, ManualPumpControlsComponent, PumpSettingsComponent],
  imports: [
    FormsModule,
    BrowserModule,
    HttpClientModule,
    PlotlyModule,
    MatSlideToggleModule,
    FlexLayoutModule,
    MatInputModule,
    MatButtonModule,
    MatListModule,
    MatTabsModule,
    MatCardModule,
    MatIconModule,
    MatSliderModule,
    MatGridListModule,
    MatExpansionModule,
    BrowserAnimationsModule,
    NotifierModule.withConfig({
      // Custom options in here
      theme: "material"
    })
  ],
  providers: [EnvServiceProvider],
  bootstrap: [AppComponent],
})
export class AppModule {}
