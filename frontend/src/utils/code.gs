function updateUserCount() {
  // Reference the spreadsheet and sheet
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName('Sheet1'); // Adjust if needed

  try {
    // Fetch data from the Lambda endpoint
    var response = UrlFetchApp.fetch('https://ivmq71srt0.execute-api.us-east-1.amazonaws.com/user-count');
    var data = JSON.parse(response.getContentText());

    // Extract user count and login activity
    var userCount = data.total_users;
    var loginActivity = data.login_activity || [];

    // Set header and value for user count
    sheet.getRange('A1').setValue('User Count');
    sheet.getRange('A2').setValue(userCount);

    // Clear previous login activity rows
    var existingRows = sheet.getLastRow();
    if (existingRows > 1) {
      sheet.getRange('B2:G' + existingRows).clearContent();
    }

    // Write headers
    var headers = ['User ID', 'Timestamp', 'Success', 'Message', 'IP Address', 'User Agent'];
    sheet.getRange('B1:G1').setValues([headers]);

    // Write all login activity rows
    if (loginActivity.length > 0) {
      var rows = loginActivity.map(function(entry) {
        return [
          entry.user_id || '',
          entry.timestamp || '',
          entry.success !== undefined ? entry.success : false,
          entry.message || '',
          entry.ipAddress || '',
          entry.userAgent || ''
        ];
      });

      // Write rows starting at B2
      sheet.getRange(2, 2, rows.length, 6).setValues(rows);
    }

  } catch (error) {
    Logger.log('Error fetching data: ' + error);
    sheet.getRange('A2').setValue('Error: Unable to fetch data');
  }
}
