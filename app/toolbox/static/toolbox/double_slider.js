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

      slider.on('change', function (event) {
          minLabel.text(event.value.newValue[0] + sliderUnit);
          maxLabel.text(event.value.newValue[1] + sliderUnit);
      });



      // Find the corresponding `.slider-horizontal` generated element and apply width class
      $input.siblings(".slider-horizontal").addClass("w-100");

  });

  document.querySelectorAll('.reset-double-slider').forEach(btn => {
    btn.addEventListener('click', function (e) {
      const target = $(btn.dataset.target);
      console.log('target', target);
      const min = parseFloat(target.data('slider-min'));
      const max = parseFloat(target.data('slider-max'));
      target.slider('setValue', [min, max]);
      const minLabel = document.querySelector(`#${target.attr('id')}-min-label`);
      const maxLabel = document.querySelector(`#${target.attr('id')}-max-label`);
      minLabel.innerText = min + target.data('slider-unit');
      maxLabel.innerText = max + target.data('slider-unit');
    });
  });


};
