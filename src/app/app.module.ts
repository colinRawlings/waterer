import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule  } from '@angular/common/http';

import * as PlotlyJS from 'plotly.js-dist';
import { PlotlyModule } from 'angular-plotly.js';

import { AppComponent } from './app.component';
import { PumpComponent } from './pump/pump.component';

PlotlyModule.plotlyjs = PlotlyJS;

@NgModule({
  declarations: [
    AppComponent,
    PumpComponent
  ],
  imports: [
    BrowserModule, HttpClientModule, PlotlyModule 
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
