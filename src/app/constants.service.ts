import { Injectable } from '@angular/core';
import { EnvService } from './env.service';

@Injectable({
  providedIn: 'root'
})
export class ConstantsService {

  public kBackendURL: string;
  public kNumChannels = 1;

  constructor(private env: EnvService) {
    this.kBackendURL = `http://${env.apiUrl}/`;
   }
}
