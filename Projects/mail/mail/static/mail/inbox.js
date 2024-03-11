document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  document.querySelector('#compose-form').addEventListener('submit', submit_email);

  // By default, load the inbox
  load_mailbox('inbox');

});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

}

function submit_email(composition) {
  // Prevent normal form submission
  composition.preventDefault();
  // Load data from form into variable
  const formData = new FormData(composition.target);
  // Post email to /emails route
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      // Pull fields from form submission
      recipients: formData.get('recipients'),
      subject: formData.get('subject'),
      body: formData.get('body')
    })
  })
  .then(response => response.json())
  .then(result => {
    // Print result
    console.log(result);
  });
  // Send user to Sent mailbox
  load_mailbox('sent');
}


function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  if (mailbox === 'sent') {
    fetch('/emails/sent')
    .then(response => response.json())
    .then(emails => {
      // Print email
      console.log(emails);

      emails.forEach((email) => {
        const element = document.createElement('div');
        element.innerHTML = email.body;
        document.querySelector('#emails-view').append(element);
      })

    });
  }

}