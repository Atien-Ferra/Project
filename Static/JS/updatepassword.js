$(document).ready(function () {
    // Validate the password fields before submission.
    // Only require current password when that input exists (i.e. logged-in flow).
    $("form").on("submit", function (event) {
      const currentExists = $("#current_password").length > 0;
      const currentPassword = currentExists ? $("#current_password").val() : null;
      const newPassword = $("#new_password").val();
      const confirmPassword = $("#confirm_password").val();

      if ((currentExists && !currentPassword) || !newPassword || !confirmPassword) {
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