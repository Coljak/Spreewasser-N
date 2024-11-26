
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


  });
