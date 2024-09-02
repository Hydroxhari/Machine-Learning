
  function getBHKValue() {
    var uiBHK = document.getElementsByName("uiBHK");
    for(var i in uiBHK) {
      if(uiBHK[i].checked) {
          return parseInt(i)+1;
      }
    }
    return -1; // Invalid Value
  }
  
function onClickedEstimatePrice() {
    console.log("Estimate price button clicked");

    var sqft = document.getElementById("uiSqft").value;
    var bhk = getBHKValue();
    var location = document.getElementById("uiLocations").value;
    var estPrice = document.getElementById("uiEstimatedPrice");

    var url = "/api/predict_home_price";

    // AJAX POST request with CORS headers
    $.ajax({
        url: url,
        type: "POST",
        contentType: "application/json", // Send JSON data
        data: JSON.stringify({
            sqft: parseFloat(sqft),
            bhk: bhk,
            location: location
        }),
        success: function(data, status) {
            console.log("Success: Got response for predict_home_price request", data);
            if (data && data.estimated_price !== undefined) {
                estPrice.innerHTML = "<h2>" + data.estimated_price.toString() + " Lakh</h2>";
            } else {
                console.error("No estimated price data received:", data);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error("Error estimating price:", textStatus, errorThrown);
        }
    });
}

  function onPageLoad() {
    console.log( "document loaded" );
    // var url = "http://127.0.0.1:5000/get_location_names"; // Use this if you are NOT using nginx which is first 7 tutorials
    var url = "/api/get_location_names"; // Use this if  you are using nginx. i.e tutorial 8 and onwards
    $.get(url,function(data, status) {
        console.log("got response for get_location_names request");
        if(data) {
            var locations = data.locations;
            var uiLocations = document.getElementById("uiLocations");
            $('#uiLocations').empty();
            for(var i in locations) {
                var opt = new Option(locations[i]);
                $('#uiLocations').append(opt);
            }
        }
    });
  }
  
  window.onload=onPageLoad;