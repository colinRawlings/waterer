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
import { MatSliderModule } from '@angular/material/slider';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';
import { NgxMaterialTimepickerModule } from 'ngx-material-timepicker';

import { NotifierModule } from 'angular-notifier';
import { FlexLayoutModule } from '@angular/flex-layout';

import * as PlotlyJS from 'plotly.js-dist';
import { PlotlyModule } from 'angular-plotly.js';

import { AppComponent } from './app.component';
import { PumpComponent } from './pump/pump.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ManualPumpControlsComponent } from './manual-pump-controls/manual-pump-controls.component';
import { PumpSettingsComponent } from './pump-settings/pump-settings.component';
import { EnvServiceProvider } from './env.service.provider';
import { LogsComponent } from './logs/logs.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

PlotlyModule.plotlyjs = PlotlyJS;

@NgModule({
  declarations: [
    AppComponent,
    PumpComponent,
    ManualPumpControlsComponent,
    PumpSettingsComponent,
    LogsComponent,
  ],
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
    MatTooltipModule,
    MatTabsModule,
    MatCardModule,
    MatIconModule,
    MatSliderModule,
    MatGridListModule,
    MatExpansionModule,
    NgxMaterialTimepickerModule,
    BrowserAnimationsModule,
    NotifierModule.withConfig({
      // Custom options in here
      theme: 'material',
    }),
    NgbModule,
  ],
  providers: [EnvServiceProvider],
  bootstrap: [AppComponent],
})
export class AppModule {}
