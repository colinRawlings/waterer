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
import { MatGridListModule } from '@angular/material/grid-list';
import {MatListModule} from '@angular/material/list';
import {MatIconModule} from '@angular/material/icon';
import { NotifierModule } from 'angular-notifier';


import * as PlotlyJS from 'plotly.js-dist';
import { PlotlyModule } from 'angular-plotly.js';

import { AppComponent } from './app.component';
import { PumpComponent } from './pump/pump.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

PlotlyModule.plotlyjs = PlotlyJS;

@NgModule({
  declarations: [AppComponent, PumpComponent],
  imports: [
    FormsModule,
    BrowserModule,
    HttpClientModule,
    PlotlyModule,
    MatSlideToggleModule,
    MatInputModule,
    MatButtonModule,
    MatListModule,
    MatTabsModule,
    MatCardModule,
    MatIconModule,
    MatGridListModule,
    MatExpansionModule,
    BrowserAnimationsModule,
    NotifierModule.withConfig({
      // Custom options in here
      theme: "material"
    })
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
