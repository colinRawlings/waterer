import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ConstantsService {

  public kBackendURL = "http://localhost:5000/";
  public kNumChannels = 3;

  constructor() { }
}
