export function initializeSliders() {
  console.log("Initializing sliders...");
    $(".numeric-slider-range").each(function () {
        const parent = $(this).parent();
        const slider = $(this);
        const id = parent.attr("id");
        console.log("Slider setup for:", id, {
            min: parent.data("range_min"),
            max: parent.data("range_max"),
            values: [parent.data("cur_min"), parent.data("cur_max")]
            });
        slider.slider({
          range: true,
          min: parseFloat(parent.data("range_min")),
          max: parseFloat(parent.data("range_max")),
          values: [parent.data("cur_min"), parent.data("cur_max")],

          slide: function (event, ui) {
            $("#" + id + "_min").val(ui.values[0]).trigger("change");
            $("#" + id + "_max").val(ui.values[1]).trigger("change");
            $("#" + id + "_text").text(ui.values[0] + " - " + ui.values[1]);
        }
        });
      
        // Set initial text and hidden field values
        $("#" + id + "_min").val(parent.data("cur_min"));
        $("#" + id + "_max").val(parent.data("cur_max"));
        $("#" + id + "_text").text(parent.data("cur_min") + " - " + parent.data("cur_max"));
      });

      $(".numeric-slider-single").each(function () {
        const parent = $(this).parent(); // div.numeric-slider-single-container
        const slider = $(this);
        
        const input = parent.find("input[type='hidden']");
        const text = parent.find("span");
    
        slider.slider({
            range: "min",
            min: parseFloat(parent.data("range_min")),
            max: parseFloat(parent.data("range_max")),
            value: parseFloat(parent.data("cur_val")),
            slide: function (event, ui) {
                input.val(ui.value).trigger("change");
                text.text(ui.value);
            }
        });
    
        input.val(parent.data("cur_val"));
        text.text(parent.data("cur_val"));
    });
    
      
  };