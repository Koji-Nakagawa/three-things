import { Component, Output, EventEmitter } from '@angular/core';
import { UserService } from '../user.service';

@Component({
  selector: 'app-delete-account',
  templateUrl: './delete-account.component.html',
  styleUrls: ['./delete-account.component.css']
})
export class DeleteAccountComponent {
  @Output() messageSender = new EventEmitter();

  constructor(
    private userService: UserService,
  ) { }

  confirm(email, password){
    let promise = new Promise((resolve, reject) => {
      let credential = this.userService.getCredentials(email, password);
      resolve(credential);
    });

    promise.then( (credential) => {
      this.userService.reauthenticate(credential).then( ()=> {
        if(confirm("Your account will be permanently deleted. Are you sure you want to delete the account?")){
            this.userService.deleteAccount();
        }
      }), function(error){
        //error
        console.log(error);
      }
    }).catch(
      (reason) => {
        console.log(reason);
      });
  }
}
