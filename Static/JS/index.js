$(document).ready(function () {
    // Example: Add a welcome animation
    $(".text-center h1").fadeIn(1000);
  
    // Add a click event for the buttons
    $(".btn").on("click", function () {
      console.log("Button clicked: " + $(this).text());
    });
  });