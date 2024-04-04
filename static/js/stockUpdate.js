function fetchStockData() {
    const symbols = ['AAPL', 'GOOGL', 'MSFT'];
    symbols.forEach(function(symbol) {
        yfinance.Ticker(symbol).info
        .then(function(data) {
            updateTable(symbol, data);
        })
        .catch(function(error) {
            console.error('Error fetching data for symbol:', symbol, error);
        });
    });
}

function updateTable(symbol, data) {
    const row = `
        <tr>
            <td>${symbol}</td>
            <td>${data.currentPrice}</td>
            <td>${data.previousClose - data.currentPrice}</td>
            <td>${((data.previousClose - data.currentPrice) / data.previousClose     * 100).toFixed(2)}%</td>
        </tr>
    `;
    $('#stock-table tbody').append(row);
}
$(document).ready(function() {
    fetchStockData(); // Fetch initial data
    setInterval(fetchStockData, 5000); // Fetch data every 5 seconds
});