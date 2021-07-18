import { Injectable } from '@angular/core';
import { EnvService } from './env.service';

@Injectable({
  providedIn: 'root'
})
export class ConstantsService {

  public kBackendURL: string;
  public kNumChannels = 3;

  constructor(private env: EnvService) {
    this.kBackendURL = `http://${env.apiUrl}/`;
   }
}
