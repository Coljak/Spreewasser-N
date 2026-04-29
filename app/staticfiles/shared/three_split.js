// import {map} from '/static/shared/map_sidebar_utils.js';


  $(document).ready(function () {
    // Vertical resizable panel (left/right)

      let leafletMap;
      document.addEventListener('leaflet-map-ready', function (e) {
          leafletMap = e.detail;
          console.log('Leaflet map ready event received in three_split.js', e.detail);
      });
      // Corner resizer
      $('#cornerSplitter').on('mousedown', function (e) {
        e.preventDefault();
    
        const startX = e.clientX;
        const startY = e.clientY;
        const startWidthLeft = $('.panel-left').width();
        const startWidthRight = $('.panel-right').width();
        const startHeightTop = $('.panel-top').height();
        const startHeightBottom = $('.panel-bottom').height();
    
        $(document).on('mousemove.cornerResize', function (event) {
          const deltaX = event.clientX - startX;
          const deltaY = event.clientY - startY;
    
          $('.panel-left').css('width', startWidthLeft + deltaX + 'px');
          $('.panel-right').css('width', startWidthRight - deltaX + 'px');
          $('.panel-top').css('height', startHeightTop + deltaY + 'px');
          $('.panel-bottom').css('height', startHeightBottom - deltaY + 'px');

        });
    
        $(document).on('mouseup.cornerResize', function () {
          $(document).off('.cornerResize');
          if (leafletMap && typeof leafletMap.invalidateSize === 'function') {
            console.log('Invalidate map size after corner resize');
              setTimeout(function () {
                  leafletMap.invalidateSize();
              }, 50);
          }
          
        });
      });

    
    $(".panel-left").resizable({
      handleSelector: ".vertical-splitter",
      resizeHeight: false
    });

    // Horizontal resizable panel (top/bottom)
    $(".panel-top").resizable({
      handleSelector: ".horizontal-splitter",
      resizeWidth: false
    });

  
    $('#reopenBottomPanelButton').on('click', function () {
      $('.panel-bottom').css('height', '30%').removeClass('d-none');
      $('#reopenBottomPanelButton').addClass('d-none');
    });

  });
