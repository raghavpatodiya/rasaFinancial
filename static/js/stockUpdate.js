function fetchStockData() {
    // Array of stock symbols
    const symbols = ['AAPL', 'GOOGL', 'MSFT']; // Add more symbols if needed

    // Fetch data for each stock symbol
    symbols.forEach(function(symbol) {
        yfinance.quote({
            symbol: symbol,
            modules: ['price'],
            callback: function(data) {
                updateTable(symbol, data);
            }
        });
    });
}

// Function to update the table with live stock data
function updateTable(symbol, data) {
    // Create a table row
    const row = `
        <tr>
            <td>${symbol}</td>
            <td>${data.price}</td>
            <td>${data.change}</td>
            <td>${data.changePercent}</td>
        </tr>
    `;

    // Append the row to the table body
    $('#stock-table tbody').append(row);
}

// Fetch stock data initially
fetchStockData();

// Fetch stock data periodically (every 30 seconds in this example)
setInterval(fetchStockData, 30000); // Adjust the interval as needed
