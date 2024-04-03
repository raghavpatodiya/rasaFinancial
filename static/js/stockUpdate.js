function fetchStockData() {
    const symbols = ['AAPL', 'GOOGL', 'MSFT']; 
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
function updateTable(symbol, data) {
    const row = `
        <tr>
            <td>${symbol}</td>
            <td>${data.price}</td>
            <td>${data.change}</td>
            <td>${data.changePercent}</td>
        </tr>
    `;
    $('#stock-table tbody').append(row);
}
fetchStockData();
setInterval(fetchStockData, 5000); 
