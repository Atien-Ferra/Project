$(document).ready(function () {
    const editButton = $("#editButton");
    const saveButton = $("#saveButton");
    const cancelButton = $("#cancelButton");

    const sessionLengthText = $("#sessionLengthText");
    const sessionLengthInput = $("#sessionLengthInput");

    const breakLengthText = $("#breakLengthText");
    const breakLengthInput = $("#breakLengthInput");

    const preferredDifficultyText = $("#preferredDifficultyText");
    const preferredDifficultyInput = $("#preferredDifficultyInput");

    editButton.on("click", function () {
        sessionLengthText.addClass("d-none");
        sessionLengthInput.removeClass("d-none");

        breakLengthText.addClass("d-none");
        breakLengthInput.removeClass("d-none");

        preferredDifficultyText.addClass("d-none");
        preferredDifficultyInput.removeClass("d-none");

        editButton.addClass("d-none");
        saveButton.removeClass("d-none");
        cancelButton.removeClass("d-none");
    });

    cancelButton.on("click", function () {
        sessionLengthInput.addClass("d-none");
        sessionLengthText.removeClass("d-none");

        breakLengthInput.addClass("d-none");
        breakLengthText.removeClass("d-none");

        preferredDifficultyInput.addClass("d-none");
        preferredDifficultyText.removeClass("d-none");

        editButton.removeClass("d-none");
        saveButton.addClass("d-none");
        cancelButton.addClass("d-none");
    });

    $("#update-profile-form").on("submit", function (event) {
        event.preventDefault();

        const formData = $(this).serialize();
        $.ajax({
            url: "/profile",
            method: "POST",
            data: formData,
            success: function () {
                sessionLengthText.text(sessionLengthInput.val()).removeClass("d-none");
                sessionLengthInput.addClass("d-none");

                breakLengthText.text(breakLengthInput.val()).removeClass("d-none");
                breakLengthInput.addClass("d-none");

                preferredDifficultyText.text(preferredDifficultyInput.find(":selected").text()).removeClass("d-none");
                preferredDifficultyInput.addClass("d-none");

                editButton.removeClass("d-none");
                saveButton.addClass("d-none");
                cancelButton.addClass("d-none");
            },
            error: function () {
                alert("An error occurred while updating preferences.");
            },
        });
    });
});