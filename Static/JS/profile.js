$(document).ready(function () {
    // Example: Highlight the profile card on hover
    $(".card").hover(
      function () {
        $(this).addClass("shadow-lg");
      },
      function () {
        $(this).removeClass("shadow-lg");
      }
    );
  
    // Add a confirmation dialog for updating the password
    $(".btn-primary").on("click", function (event) {
      if (!confirm("Are you sure you want to update your password?")) {
        event.preventDefault();
      }
    });

    // Handle profile update via AJAX
    $("#update-profile-form").on("submit", function (event) {
        event.preventDefault();

        const formData = $(this).serialize();
        $.ajax({
            url: "/profile",
            method: "POST",
            data: formData,
            success: function (response) {
                alert("Profile updated successfully.");
                location.reload();
            },
            error: function () {
                alert("An error occurred while updating the profile.");
            },
        });
    });
});