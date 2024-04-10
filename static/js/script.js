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
// Function to speak out text using Web Speech API
function speakText(text) {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    synth.speak(utterance);
}
function reportConversation() {
    // Get the user message and bot response from the previous conversation
    const userMessage = getLastUserMessage();
    const botResponse = getLastBotResponse();

    // Make an AJAX request to report the conversation
    $.ajax({
        type: "POST",
        url: "/report-conversation",
        contentType: "application/json",
        data: JSON.stringify({ user_message: userMessage, bot_response: botResponse }),
        success: function (response) {
            alert(response.message);
        },
        error: function (error) {
            alert("Failed to report conversation. Please try again later.");
        }
    });
}

// Function to get the last user message from the chat history
function getLastUserMessage() {
    return $(".user-message").last().text().replace("You:", "").trim();
}

// Function to get the last bot response from the chat history
function getLastBotResponse() {
    return $(".bot-response").last().text().replace("Bot:", "").trim();
}
$(document).ready(function () {
    // Logout button click event
    $(".logout-btn").on("click", function () {
        // Redirect to the login page
        window.location.href = "/login";
    });
    $(".faq-page-btn").on("click", function () {
        // Redirect to the FAQ page
        window.location.href = "/faq";
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
    $("#report-conversation").on("click", function () {
        reportConversation();
    });

    let utterance = null; // Initialize utterance variable to null

    function handleBotResponse(botResponse) {
        // Cancel any ongoing speech if utterance is not null
        if (utterance && window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
        }
        // console.log(typeof botResponse);
        // blob (image response)
        if (botResponse instanceof Blob) {
            const imageUrl = URL.createObjectURL(botResponse);
            const imgElement = document.createElement('img');
            imgElement.src = imageUrl;
            const botResponseContainer = document.createElement('div');
            botResponseContainer.classList.add('bot-response');
            botResponseContainer.appendChild(imgElement);
            $("#chat-widget-messages").append("<div class='bot-response'><strong><span class='bot-label'>Bot:</span></strong> Here is the requested graph</div>");
            $("#chat-widget-messages").append(botResponseContainer);                  
        } else {
            const botResponseHtml = "<div class='bot-response'><strong><span class='bot-label'>Bot:</span></strong> " +
                escapeHtml(botResponse) +
                "</div>";
            $("#chat-widget-messages").append(botResponseHtml);      
        }

        $("#chat-widget-messages").scrollTop($("#chat-widget-messages")[0].scrollHeight);

        const $botResponseElement = $("#chat-widget-messages").children().last();
        const speakerButtonHtml = "<button class='speak-button'>🔈</button>";
        $botResponseElement.append(speakerButtonHtml);

        // Event handler for toggling speech synthesis
        $botResponseElement.find('.speak-button').on('click', function () {
            if (utterance && window.speechSynthesis.speaking) {
                // If speech is currently speaking, cancel it
                window.speechSynthesis.cancel();
                $(this).text('🔈'); // Change button text to indicate speech synthesis is disabled
            } else {
                // If speech is not currently speaking, create utterance and start speaking
                utterance = new SpeechSynthesisUtterance(botResponse);
                window.speechSynthesis.speak(utterance);
                $(this).text('🔊'); // Change button text to indicate speech synthesis is enabled
            }
        });

        // Immediately start speaking if the button is already clicked
        if (utterance && window.speechSynthesis.speaking) {
            utterance = new SpeechSynthesisUtterance(botResponse);
            window.speechSynthesis.speak(utterance);
        }
    }

    // Event handler for chat widget input
    $("#chat-widget-input").keypress(function (event) {
        if (event.which == 13) {
            let userMessage = $("#chat-widget-input").val();
            $("#chat-widget-input").val("");
            $("#chat-widget-messages").append(
                "<div class='user-message'><strong><span class='bot-label'>You:</span></strong> " +
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
                    // Handle bot response
                    handleBotResponse(botResponse);
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
    

    function updateStockData() {
        // AJAX request to fetch stock data from the server
        $.ajax({
            type: "GET",
            url: "/stock_data",
            success: function (data) {
                // Clear the existing table rows
                $("#stock-table tbody").empty();
                // Loop through the received data and append rows to the table
                data.forEach(function (stock) {
                    let trendSymbol = stock.change > 0 ? "<span style='color: green;'>▲</span>" : "<span style='color: red;'>▼</span>";
                    $("#stock-table tbody").append(
                        `<tr>
                            <td>${stock.symbol}</td>
                            <td>${stock.price}${trendSymbol}</td>
                            <td>${stock.change}</td>
                            <td>${stock.percent_change}</td>
                            <td>${stock.market_cap}</td>
                        </tr>`
                    );
                });
            },
            error: function () {
                // Handle error if needed
            },
        });
    }
    updateStockData();
    setInterval(updateStockData, 5000);
});
