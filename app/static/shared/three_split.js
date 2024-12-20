
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

    $('#toggleBottomFullscreen').on('click', function () {
      $('.panel-bottom').css('height', '100');
      // $('#reopenBottomPanelButton').removeClass('d-none');
    });
  
    $('#reopenBottomPanelButton').on('click', function () {
      $('.panel-bottom').css('height', '30%').removeClass('d-none');
      $('#reopenBottomPanelButton').addClass('d-none');
    });

  });
