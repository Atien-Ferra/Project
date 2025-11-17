$(document).ready(function () {
    // Add event listener for the login form submission
    $("form").on("submit", function (event) {
      const email = $("#email").val();
      const password = $("#password").val();
  
      if (!email || !password) {
        event.preventDefault();
        alert("Please fill in both email and password.");
      }
    });
  });