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
            newsHtml += '<a href="' + newsItem.link + '" class="btn btn-primary news-btn" target="_blank">Read More</a>';
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

  // Function to add a stock to the watchlist
  function addToWatchlist(companyName) {
    $.ajax({
      url: '/add_to_watchlist',
      method: 'POST',
      data: {company_name: companyName},
      success: function(response) {
        // Handle success
        console.log('Stock added to watchlist:', response);
        // Update the watchlist table
        updateWatchlistTable();
      },
      error: function(xhr, status, error) {
        // Handle error
        console.error('Error adding stock to watchlist:', error);
      }
    });
  }

  // Event listener for adding stock to watchlist
  $('#add-watchlist-button').click(function() {
    var companyName = $('#watchlist-input').val();
    addToWatchlist(companyName);
  });

  // Function to update the watchlist table
  function updateWatchlistTable() {
    $.ajax({
      url: '/get_watchlist',
      method: 'GET',
      success: function(response) {
        console.log('Watchlist data:', response); // Log the response
        $('#watchlist-table tbody').empty();
        // Append each stock to the watchlist table
        response.forEach(function(stock) {
          var row = '<tr>';
          row += '<td>' + stock.symbol + '</td>';
          row += '<td><button class="btn btn-danger remove-watchlist-btn" data-symbol="' + stock.symbol + '">Remove</button></td>';
          row += '</tr>';
          $('#watchlist-table tbody').append(row);
        });
      },
      error: function(xhr, status, error) {
        // Handle error
        console.error('Error fetching watchlist:', error);
      }
    });
  }

  // Initial update of the watchlist table
  updateWatchlistTable();
});