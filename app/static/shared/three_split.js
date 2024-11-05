
  $(document).ready(function () {
    // Vertical resizable panel (left/right)
    $(".panel-left").resizable({
      handleSelector: ".vertical-splitter",
      resizeHeight: false
    });

    // Horizontal resizable panel (top/bottom)
    $(".panel-top").resizable({
      handleSelector: ".horizontal-splitter",
      resizeWidth: false
    });

    var map = L.map('map').setView([51.505, -0.09], 13);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);
  });
