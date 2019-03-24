function linechart(gd) {
  console.log(gd.toString())
  var timeFormat = 'YYYY-MM-DD';
  var config = {
      type:    'line',
      data:    {
          datasets: [
              {
                  data: [gd],
                  fill: false,
                  backgroundColor: [
                      'rgba(255, 99, 132, 0.2)',
                      'rgba(54, 162, 235, 0.2)',
                      'rgba(255, 206, 86, 0.2)',
                      'rgba(75, 192, 192, 0.2)',
                      'rgba(153, 102, 255, 0.2)',
                      'rgba(255, 159, 64, 0.2)'
                  ],
                  borderColor: [
                      'rgba(255, 99, 132, 1)',
                      'rgba(54, 162, 235, 1)',
                      'rgba(255, 206, 86, 1)',
                      'rgba(75, 192, 192, 1)',
                      'rgba(153, 102, 255, 1)',
                      'rgba(255, 159, 64, 1)'
                  ]
              }
          ]
      },
      options: {
          legend: { display: false },
          responsive: true,
          title:      {
              display: true,
              text:    'var2'
          },
          scales:     {
              xAxes: [{
                  type:       "time",
                  time:       {
                      format: timeFormat,
                      tooltipFormat: 'll',
                      unit: 'quarter'

                  },
                  scaleLabel: {
                      display:     true,
                      labelString: 'Date'
                  }
              }],
              yAxes: [{
                  scaleLabel: {
                      display:     false
                  }
              }]
          }
      }
  };


   const LINECHART = document.getElementById("grafico-voti").getContext("2d");
   let lineChart = new Chart (LINECHART, config);
}
