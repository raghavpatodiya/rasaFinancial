$(document).ready(function() {
    // Function to fetch and display news related to the entered company
    function searchNews() {
      var companyName = $('#company-name-input').val();
      // Use AJAX to fetch news data from the server
      $.ajax({
        url: '/stock_news', // Endpoint to fetch news data (You need to define this endpoint in your Flask app)
        method: 'POST',
        data: {company_name: companyName},
        success: function(response) {
          // Clear previous news content
          $('#news-content').empty();
          // Append each news article to the news section
          response.forEach(function(newsItem) {
            var newsHtml = '<div class="card news-card">';
            newsHtml += '<div class="card-body news-card-body">';
            newsHtml += '<h5 class="card-title news-card-title">' + newsItem.title + '</h5>';
            newsHtml += '<p class="card-text news-card-text">' + newsItem.publisher + '</p>';
            newsHtml += '<a href="' + newsItem.link + '" class="btn btn-primary news-btn">Read More</a>';
            newsHtml += '</div></div>';
            $('#news-content').append(newsHtml);
          });
        },
        error: function(xhr, status, error) {
          // Handle error
          console.error('Error fetching news:', error);
        }
      });
    }
  
    // Event listener for the search news button
    $('#search-news-button').click(function() {
      searchNews();
    });
  });