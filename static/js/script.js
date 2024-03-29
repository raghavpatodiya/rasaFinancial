function handleVoiceInput() {
    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.onresult = function (event) {
        const userMessage = event.results[0][0].transcript;
        $("#chat-widget-input").val(userMessage);
        $("#chat-widget-input").focus();
    };
    recognition.start();
}

$(document).ready(function () {
    // Logout button click event
    $(".logout-btn").on("click", function () {
        // Redirect to the login page
        window.location.href = "/login";
    });
    $("#chat-widget-button").on("click", function () {
        $("#chat-widget").toggleClass("d-none");
    });
    $("#chat-widget-close-button").on("click", function () {
        $("#chat-widget").addClass("d-none");
    });

    $("#voice-input").on("click", function () {
        handleVoiceInput();
    });

    function resetConversation() {
        $("#chat-widget-messages").empty();
    }

    $("#reset-conversation").on("click", function () {
        resetConversation();
    });

    $("#chat-widget-input").keypress(function (event) {
        if (event.which == 13) {
            let userMessage = $("#chat-widget-input").val();
            $("#chat-widget-input").val("");
            $("#chat-widget-messages").append(
                "<div class='user-message'><strong>You:</strong> " +
                escapeHtml(userMessage) +
                "</div>"
            );
            $("#chat-widget-messages").scrollTop(
                $("#chat-widget-messages")[0].scrollHeight
            );
            $.ajax({
                type: "POST",
                url: "/webhook",
                contentType: "application/json",
                data: JSON.stringify({ message: userMessage }),
                success: function (data) {
                    let botResponse = data.response;
                    $("#chat-widget-messages").append(
                        "<div class='bot-response'><strong>Bot:</strong> " +
                            escapeHtml(botResponse) +
                            "</div>"
                    );
                    $("#chat-widget-messages").scrollTop(
                        $("#chat-widget-messages")[0].scrollHeight
                    );
                },
                error: function () {
                    // Handle error if needed
                },
            });
        }
    });

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function updateLocCounter() {
        $.ajax({
            type: "GET",
            url: "/loc",
            success: function (data) {
                var odometer = new Odometer({
                    el: document.querySelector("#loc-counter"),
                    value: 0,
                    theme: "default",
                    format: "(,ddd)",
                });
                odometer.update(data.loc);
            },
            error: function () {
                $("#loc-counter").text("LOC: Error fetching LOC");
            },
        });
    }
    updateLocCounter();
    setInterval(updateLocCounter, 5000);
});

