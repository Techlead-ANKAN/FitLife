
function showChart(chartId, tab) {
  // Remove active class from all tabs
  $('.tab').removeClass('active');

  // Add active class to the current tab
  $(tab).addClass('active');

  // Fade out all charts
  $('.chart-container').fadeOut(300);

  // Animate the selected chart from bottom to up
  setTimeout(() => {
    $('#' + chartId).parent().css('top', '100%').show().animate({
      top: '0%'
    }, 300);
  }, 300);
}

function createChart(chartId, type, labels, data, backgroundColors) {
    new Chart(document.getElementById(chartId), {
              type: type,
              data: {
                  labels: labels,
                  datasets: [{
                      data: data,
                      backgroundColor: backgroundColors,
                      borderWidth: 1
                  }]
              },
              options: {
                  responsive: true,
                  animation: {
                      duration: 3000,
                      easing: 'easeOutBounce',
                      from: 0,
                      onComplete: function(animation) {
                          animation.chart.data.datasets.forEach(dataset => {
                              dataset.data.forEach((value, index) => {
                                  dataset.data[index] = value;
                              });
                          });
                      }
                  },
                  scales: {
                      y: {
                          beginAtZero: true
                      }
                  }
              }
          });
}

function getRandomValue(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

$(document).ready(function () {
  const checkinData = Array(3).fill(0).map(() => getRandomValue(10, 100));
  const popularTimesData = Array(6).fill(0).map(() => getRandomValue(10, 100));
  const classAttendanceData = Array(5).fill(0).map(() => getRandomValue(10, 100));
  const trainerUtilizationData = Array(7).fill(0).map(() => getRandomValue(10, 100));
  const facilityUsageData = Array(4).fill(0).map(() => getRandomValue(10, 100));
  const retentionRateData = Array(6).fill(0).map(() => getRandomValue(10, 100));
  const memberDemographicsData = Array(4).fill(0).map(() => getRandomValue(10, 100));
  const workoutTrendsData = Array(5).fill(0).map(() => getRandomValue(10, 100));

  createChart(
    "checkinChart",
    "bar",
    ["Daily", "Weekly", "Monthly"],
    checkinData,
    ["#3498db", "#2ecc71", "#e74c3c"]
  );
  createChart(
    "popularTimesChart",
    "line",
    ["6AM", "9AM", "12PM", "3PM", "6PM", "9PM"],
    popularTimesData,
    ["#e67e22"]
  );
  createChart(
    "classAttendanceChart",
    "bar",
    ["Yoga", "Zumba", "Pilates", "HIIT", "Spin"],
    classAttendanceData,
    ["#9b59b6"]
  );
  createChart(
    "trainerUtilizationChart",
    "line",
    ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    trainerUtilizationData,
    ["#f1c40f"]
  );
  createChart(
    "facilityUsageChart",
    "pie",
    ["Cardio", "Weight Room", "Pool", "Studio"],
    facilityUsageData,
    ["#1abc9c", "#e74c3c", "#3498db", "#f39c12"]
  );
  createChart(
    "retentionRateChart",
    "line",
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    retentionRateData,
    ["#e67e22"]
  );
  createChart(
    "memberDemographicsChart",
    "doughnut",
    ["18-25", "26-35", "36-45", "46+"],
    memberDemographicsData,
    ["#2980b9", "#16a085", "#8e44ad", "#c0392b"]
  );
  createChart(
    "workoutTrendsChart",
    "bar",
    ["Strength", "Cardio", "Yoga", "HIIT", "CrossFit"],
    workoutTrendsData,
    ["#e74c3c"]
  );
});