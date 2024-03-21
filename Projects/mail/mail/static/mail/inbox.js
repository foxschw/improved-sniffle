document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => {
    // flag that if this button is clicked, email won't be rendered as a reply.
    let reply = false;
    compose_email(reply);
  });
  document.querySelector('#compose-form').addEventListener('submit', submit_email);

  // By default, load the inbox
  load_mailbox('inbox');

});


function compose_email(email_id, reply) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#read-email').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // Check if email is a reply and format if so.
  // Fetch email data from ID passed in.
  if (reply === true) {
    fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
    // Populate recipient
      // When replying to an email you've sent, reply to recipients instead of back to yourself
      if (email.sender === email.user) {
        document.querySelector('#compose-recipients').value = email.recipients;
      // Otherwise, reply to sender
      } else {
        document.querySelector('#compose-recipients').value = email.sender;
      }

      // Add Re: if it isn't there already
      let email_subject = email.subject;
      if (!email_subject.startsWith("Re: ")) {
        email_subject = "Re: " + email_subject;
      }
      document.querySelector('#compose-subject').value = email_subject;
      
      // Prepopulate body
      document.querySelector('#compose-body').value = "\n---\n" +
        `On ${email.timestamp} ${email.sender} wrote:` + "\n" +
        email.body;
    });
  }

}


function submit_email(composition) {
  // Prevent normal form submission
  composition.preventDefault();
  // Load data from form into variable
  const formData = new FormData(composition.target);
  // Convert all paragraph breaks to HTML so they load when viewed later.
  let email_body = formData.get('body');
  email_body = email_body.replace(/\n/g, "<br>");
  // Post email to /emails route
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      // Pull fields from form submission, use the new email_body variable.
      recipients: formData.get('recipients'),
      subject: formData.get('subject'),
      body: email_body
    })
  })
  .then(response => response.json())
  .then(result => {
    // Print result
    console.log(result);
  })
  .then(() => {
    // clear out current view and reload sent to include most recent.
    document.querySelector('#emails-view').innerHTML = '';
    load_mailbox('sent');
  });
}


function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#read-email').style.display = 'none';

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
      user.classList.add('bold-class');
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

      element.addEventListener('click', () => {
        read_email(email.id, mailbox);
      });

    })
  });
}


function read_email(email_id, mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#read-email').style.display = 'block';

  // Clear out the div of anything there already
  document.querySelector('#read-email').innerHTML = '';

  // If we're seeing this email, mark it as read.
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  });
  
  // Assemble the email
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
      // Print email
      console.log(email);
      console.log(email.user); //dbug
      console.log(email.sender); //dbug
      
      // Create div container
      const element = document.createElement('div');
      document.querySelector('#read-email').append(element);

      // Create elements for all component parts of the email
      const from = document.createElement('span');
      from.classList.add('bold-class');
      from.innerHTML = 'From: ';

      const sender = document.createElement('span');
      sender.innerHTML = email.sender;

      const to = document.createElement('span');
      to.classList.add('bold-class');
      to.innerHTML = 'To: ';

      const recipient = document.createElement('span');
      recipient.innerHTML = email.recipients;

      const subject = document.createElement('span');
      subject.classList.add('bold-class');
      subject.innerHTML = 'Subject: ';

      const subj = document.createElement('span');
      subj.innerHTML = email.subject;

      const timestamp = document.createElement('span');
      timestamp.classList.add('bold-class');
      timestamp.innerHTML = 'Timestamp: ';

      const time = document.createElement('span');
      time.innerHTML = email.timestamp;

      const reply_btn = document.createElement('button');
      reply_btn.classList.add('btn');
      reply_btn.classList.add('btn-sm');
      reply_btn.classList.add('btn-outline-primary');
      reply_btn.id = 'reply';
      reply_btn.innerHTML = 'Reply';
      // Send to compose view, passing in the id of the email being viewed.
      reply_btn.addEventListener('click', () => {
        // if this button is clicked, compose email should be formatted as reply
        let reply = true
        compose_email(email.id, reply);
      });


      const archive_btn = document.createElement('button');
      // Only add archive button for received emails, hide if not.
      if (mailbox === 'sent') {
        archive_btn.style.display = 'none'
      } else {
        archive_btn.classList.add('btn');
        archive_btn.classList.add('btn-sm');
        archive_btn.classList.add('btn-outline-primary');
        // Determine what the button should say depending on if archived = true
        archive_btn.innerHTML = email.archived ? 'Unarchive' : 'Archive';
        // Clicking the button will toggle the state of the archived field
        // (and return user to inbox)
        archive_btn.addEventListener('click', () => {
          archive_toggle(email.archived, email.id);
        });
      };
      
      const body = document.createElement('span');
      body.innerHTML = email.body;

      // Combine all the components together
      element.append(from, sender, document.createElement('br'), 
        to, recipient, document.createElement('br'), 
        subject, subj, document.createElement('br'), 
        timestamp, time, document.createElement('br'),
        reply_btn, archive_btn, document.createElement('hr'),
        body);
  });
}


function archive_toggle(current_state, email_id) {
  // Make PUT request to API 
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      // Flip archive state to whatever is opposite.
      archived: !current_state
    })
  })
  .then(() => {
    // Send user to inbox, reloading first to include recent changes.
    // Inbox will load by default on refresh
    location.reload();
  });
}