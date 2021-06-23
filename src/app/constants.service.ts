import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ConstantsService {

  public kBackendURL = "http://192.168.0.22:5000/"; // TODO!!!
  public kNumChannels = 3;

  constructor() { }
}
