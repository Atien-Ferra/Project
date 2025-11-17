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
  });