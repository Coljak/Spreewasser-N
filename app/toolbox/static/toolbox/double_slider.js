export function initializeSliders() {
    console.log("Initializing sliders...");
      $(".double-slider").each(function () {
        let slider = $(this).slider();
        
        let sliderUnit = $(this).attr("data-slider-unit");
        let sliderId = $(this).attr("id");
        
        let minLabel = $("#" + sliderId + "-min-label");
        let maxLabel = $("#" + sliderId + "-max-label");
        slider.on('slide', function (event) {
            minLabel.text(event.value[0] + sliderUnit) ;//+ $(this).attr('data-slider-unit'));
            maxLabel.text(event.value[1] + sliderUnit) ;//+ $(this).attr('data-slider-unit'));
        });

        $('.slider-horizontal').addClass('w-100');

      });
    };