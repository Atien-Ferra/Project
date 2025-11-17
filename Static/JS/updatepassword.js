$(document).ready(function () {
    // Validate the password fields before submission
    $("form").on("submit", function (event) {
      const currentPassword = $("#current_password").val();
      const newPassword = $("#new_password").val();
      const confirmPassword = $("#confirm_password").val();
  
      if (!currentPassword || !newPassword || !confirmPassword) {
        event.preventDefault();
        alert("Please fill in all fields.");
        return;
      }
  
      if (newPassword !== confirmPassword) {
        event.preventDefault();
        alert("New password and confirm password do not match.");
      }
    });
  });