// This event listener is triggered when the DOM has been loaded.
document.addEventListener('DOMContentLoaded', function() {

  function show_blocks(){

    // Getting styles ready.
    document.querySelector('#emails-view').style.display = 'block';
    if (document.querySelector('#for_emails')){
      document.querySelector('#for_emails').style.display = 'block';
    }
    if (document.querySelector('.in_view')){
      document.querySelector('.in_view').style.display = 'none';
    }
  }
  
  // By default, load the mailbox.
  load_mailbox('inbox')
  
  
  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => {
    load_mailbox('inbox');
    show_blocks()
  });
  document.querySelector('#sent').addEventListener('click', () => {
    load_mailbox('sent');
    show_blocks();
  });
  document.querySelector('#archived').addEventListener('click', () => {

    // Wait for the API to update first.
    setTimeout(()=>{
      load_mailbox('archive');
      show_blocks();
    }, 200)
  });
  document.querySelector('#compose').addEventListener('click', () => {

    // Get the compose form ready..
    compose_email();
    document.querySelector('#compose-form').onsubmit = function(){
      
      // When the compose form has been submitted, send a POST request to the API.
      fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: document.querySelector('#compose-recipients').value,
            subject: document.querySelector('#compose-subject').value,
            body: document.querySelector('#compose-body').value
        })
      })
      // Convert the response to JSON...
      .then(response => response.json())

      // And then load the "sent" mailbox.
      .then(result => {
          // Print result
          console.log(result);
          load_mailbox('sent');
      });

      // This is so the form doesn't actually submit.
      return false;
    }
  });
});


// Global Variable made to keep track of the last mailbox.
var last_mailbox = 'Inbox';

// Main Function

function main(mailbox){
  if (document.querySelector('#for_emails')){
    document.querySelector('#for_emails').remove();
  }
  var elem = document.createElement('div');
  elem.id = 'for_emails';
  document.querySelector('.container').append(elem);

  // Fetch the mailbox from the API
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(data => {
    var i=0;
    // For each element
    data.forEach((element) => {

      // Add a div, and set it's id to the element's id given in the api.
      var e = document.createElement('div');
      e.id = element.id;  

      // Add various styles
      e.style.border = "1px solid black";
      e.style.padding = '7px';

      // Check the localStorage to see if it has been read
      if (localStorage.getItem(e.id.toString())){
        e.style.backgroundColor = '#d3d3d3';
      }

      // ..or the api itself.
      fetch(`/emails/${e.id}`)
      .then(response => response.json())
      .then((email) => {
        if (email["read"]){
          localStorage.setItem(e.id.toString(), 'c');
          e.style.backgroundColor = '#d3d3d3';
        }
      })
      
      // This event listener is triggered when a div is clicked
      e.addEventListener('click', function(){
        // If the email hasn't been read yet, set it to be 
        if (!localStorage.getItem(e.id.toString())){

          // Every email is unique, so we can manipulate that.
          localStorage.setItem(e.id.toString(), 'c');
          e.style.backgroundColor = '#d3d3d3';
          update_read(e.id);
        
        }
          // Call show_email anyway.

        show_email(element.id, mailbox);
      })
        
      // InnerHTML for the div
       e.innerHTML = `
        <p style="font-size:13px;font-weight:bold;display:inline;">${data[i]["sender"]}</p>
        <p style="font-size:13px;display:inline;margin-left:5px;">${data[i]["subject"]}</p>
        <p style="font-size:13px;display:inline;float:right;">${data[i]["timestamp"]}</p>
        `;

      // Append the "child" div to it's parent.
      document.querySelector('#for_emails').append(e);
      // The "i" variable is unused here, but it's here just for debugging.
      ++i;
      })
      // After the child divs are done loading, the last_mailbox can be changed, since it isn't needed anymore. 
      last_mailbox = mailbox.charAt(0).toUpperCase() + mailbox.slice(1);
    })
}
function show_email(id, mailbox){
  // Clear screen
  
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#for_emails').style.display = 'none';

  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    if (document.querySelector('.in_view')!==null){
      document.querySelector('.in_view').remove();
    }
    if (document.querySelector('.in_view')===null){
      // Create a div
      var div = document.createElement('div');

      // Give a class to the div
      div.className = 'in_view';

      let i = 1;
      let stra = "";
      email["recipients"].forEach((e) => {
        stra += `${e}`
        if (i != email["recipients"].length){
          stra += ', ' 
        }
        i++;
      })
      console.log(stra);
      console.log(email);
      // Add HTML to the div
      var email_str = JSON.stringify(email)
      
      div.innerHTML = `
      <strong style="display:inline;">From: </strong><p style="display:inline;">${email["sender"]}</p>
      <br>
      <strong style="display:inline;">To: </strong><p style="display:inline;">${stra}</p>
      <br>
      <strong style="display:inline;">Subject: </strong><p style="display:inline;">${email["subject"]}</p>
      <br>
      <strong style="display:inline;">Timestamp: </strong><p style="display:inline;">${email["timestamp"]}</p>
      <br>
      <button class="btn btn-sm btn-outline-primary" onclick='reply(${email_str})'>Reply</button>`
      if (mailbox !== 'sent'){
        var a;
        var d;
        fetch(`/emails/${id}`)
        .then(response => response.json())
        .then(data => {
          d = data["archived"];
          data["archived"] === true ? a = "Unarchive" : a = "Archive"
          div.innerHTML += `
          <button class="btn btn-sm btn-outline-primary" onclick='archive(${email["id"]}, ${d})' id="to_archive">${a}</button>
          <hr>
          <p>${email["body"]}</p>
          `;
        })
      }
      else{
        div.innerHTML += `
          <hr>
          <p>${email["body"]}</p>
        `;
      }
      // Append the div to container
      document.querySelector('.container').appendChild(div);
    }
  });
}
// Archive the message
function archive(id, bool){
  function change_archive_state(id, b){
    fetch(`/emails/${id}`,{
      method : 'PUT',
      body : JSON.stringify({
        archived: b
      })
    })
  }
  if (document.querySelector('#to_archive').innerHTML === "Archive"){
    change_archive_state(id, !bool)
    document.querySelector('#to_archive').innerHTML = 'Unarchive';
  }
  else{
    change_archive_state(id, !bool)
    document.querySelector('#to_archive').innerHTML = 'Archive';
  }
  // Gets the inbox page after 1 second(api needs to reload)
  setTimeout(()=>{
    load_mailbox('inbox');
  }, 1000)
}
// Reply to the message
function reply(email){

  // Hides div
  document.querySelector('.in_view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  document.querySelector('#compose-recipients').value = email["sender"];
  
  if (email["subject"].includes("Re: ")){
    document.querySelector('#compose-subject').value = email["subject"];
  }
  else{
    document.querySelector('#compose-subject').value = `Re: ${email["subject"]}`;
  }
  document.querySelector('#compose-body').value += `
  On ${email["timestamp"]} ${email["sender"]} wrote:
  ______________________________________________________
  ${email["body"]}
  ______________________________________________________
  `;

  document.querySelector('#compose-form').onsubmit = () => {    
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: document.querySelector('#compose-recipients').value,
          subject: document.querySelector('#compose-subject').value,
          body: document.querySelector('#compose-body').value
      })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result);
        load_mailbox('sent');
    });
    return false;
  }

}


function update_read(id){
  // Fetches email with a particular id.

  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })
}

function compose_email() {

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#for_emails').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    // If there is an in-view div, make it invisible
    if (document.querySelector('.in_view')){
      document.querySelector('.in_view').style.display = 'none';
    }

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
}
function load_mailbox(mailbox) {
    if (document.querySelector('#for_emails')){
      document.querySelector('#for_emails').style.display = 'block';
    }
    if (document.querySelector('.in_view')){
      document.querySelector('.in_view').style.display = 'none';
    }
    // Show the mailbox and hide other views
    document.querySelector('#compose-view').style.display = 'none' 
    document.querySelector('#emails-view').style.display = 'block';

    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
    if (mailbox === "archive"){
      if (document.querySelector('#for_emails')){
        document.querySelector('#for_emails').remove();
      }
      // Main
      main(mailbox)
    }
    else{
      if ((document.querySelector('#emails-view').innerHTML === `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>` || document.querySelector('#emails-view').innerHTML !== `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`) && document.querySelector('#for_emails')===null){
        // Call main func
        main(mailbox);
      }
      else if ((document.querySelector('#emails-view').innerHTML !== `<h3>${last_mailbox}</h3>` ||  document.querySelector('#emails-view').innerHTML === `<h3>${last_mailbox}</h3>`  ) && document.querySelector('#for_emails')!==null) {
          // Delete div 

          document.querySelector('#for_emails').remove();

          // Call again

          main(mailbox);
      }
    }
    
}