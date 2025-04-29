export function initializeSliders() {
  console.log("Initializing sliders...");
  $(".double-slider").each(function () {
      let $input = $(this);
      let slider = $input.slider(); // initializes Bootstrap slider

      let sliderUnit = $input.attr("data-slider-unit");
      let sliderId = $input.attr("id");

      let minLabel = $("#" + sliderId + "-min-label");
      let maxLabel = $("#" + sliderId + "-max-label");

      slider.on('slide', function (event) {
          minLabel.text(event.value[0] + sliderUnit);
          maxLabel.text(event.value[1] + sliderUnit);
      });

      // Find the corresponding `.slider-horizontal` generated element and apply width class
      $input.siblings(".slider-horizontal").addClass("w-100");
  });
};
