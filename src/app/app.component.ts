import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface keyable {
  [key: string]: any  
}
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'waterer';

  connect_info: string;

  constructor(private http: HttpClient) {
    this.connect_info = "";
  }

  ngOnInit(): void {
    this.http.get('http://127.0.0.1:5000/')
    .subscribe((data:keyable)=>{
      this.connect_info = `${data.data}`;
    })


  }
}
