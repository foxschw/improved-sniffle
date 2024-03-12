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
  })
  .then(() => {
    // Send user to Sent mailbox, reloading first to include most recent email.
    location.reload();
    load_mailbox('sent');
  });
}


function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Request email from mailbox that has been passed in.
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Print email
    console.log(emails);

    // Iterate over each email in the mailbox
    emails.forEach((email) => {
      const element = document.createElement('div');
      element.classList.add('sent-mailbox');
      // Apply specific style if email is marked "read"
      if (email.read === true) {
        element.id = 'email-read'
      };
      document.querySelector('#emails-view').append(element);
      
      // Create variable for user
      const user = document.createElement('span');
      user.classList.add('user-class');
      // If viewing the Sent mailbox, show recipient, not sender.
      if (mailbox === 'sent') {
        user.innerHTML = `${email.recipients} - `;
      } else {
        user.innerHTML = `${email.sender} - `;
      }

      // Create variable for subject.
      const text = document.createElement('span');
      text.innerHTML = email.subject;

      // Create variable for time-stamp
      const time = document.createElement('span');
      time.classList.add('time-stamp-class');
      time.innerHTML = email.timestamp;

      // Add these variables to the div.
      element.append(user, text, time);
    })
  });
}