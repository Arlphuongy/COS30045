// Wait for the DOM to be fully loaded before executing code
window.onload = function() {
    // Load data from CSV file
    d3.csv("lab2_4.csv").then(function(data) {
        console.log(data); // Log the data to verify it's loaded correctly
        
        // Store the data in a variable
        var wombatSightings = data;
        
        // Call the barChart function with our data
        barChart(wombatSightings);
    }).catch(function(error) {
        // Handle any errors that occur during CSV loading
        console.log("Error loading the CSV file:", error);
    });
};

// Function to create the bar chart
function barChart(dataset) {
    // Set up chart dimensions
    var w = 500;
    var h = 300;
    var padding = 1;
    
    // Create SVG element
    var svg = d3.select("#chart")
                .append("svg")
                .attr("width", w)
                .attr("height", h);
    
    // Create the bar chart with the loaded data
    svg.selectAll("rect")
       .data(dataset)
       .enter()
       .append("rect")
       .attr("x", function(d, i) {
           return i * (w / dataset.length);
       })
       .attr("y", function(d) {
           return h - (parseInt(d.wombats) * 4); // Scale height for visibility
       })
       .attr("width", w / dataset.length - padding)
       .attr("height", function(d) {
           return parseInt(d.wombats) * 4; // Scale height for visibility
       })
       .attr("fill", function(d) {
           // Color bars based on data value
           if (parseInt(d.wombats) > 20) {
               return "rgb(0, 0, 255)"; // Blue for high values
           } else if (parseInt(d.wombats) > 10) {
               return "rgb(50, 50, 255)"; // Medium blue for medium values
           } else {
               return "rgb(100, 100, 255)"; // Light blue for low values
           }
       });
}