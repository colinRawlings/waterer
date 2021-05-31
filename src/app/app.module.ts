import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule  } from '@angular/common/http';

import { AppComponent } from './app.component';
import { PumpComponent } from './pump/pump.component';

@NgModule({
  declarations: [
    AppComponent,
    PumpComponent
  ],
  imports: [
    BrowserModule, HttpClientModule 
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
