import { initializeSliders } from "./custom_slider.js";

document.addEventListener("DOMContentLoaded", function () {
    // Initialize the sliders when the DOM is fully loaded
    // initializeSliders();
    const setLabel = (lbl, val) => {
        const label = $(`#slider-${lbl}-label`);
        label.text(val);
        const slider = $(`#slider-div .${lbl}-slider-handle`);
        const rect = slider[0].getBoundingClientRect();
        label.offset({
          top: rect.top - 30,
          left: rect.left
        });
      }
      
      const setLabels = (values) => {
        setLabel("min", values[0]);
        setLabel("max", values[1]);
      }
      
      
    //   $('#ex2').slider().on('slide', function(ev) {
    //     setLabels(ev.value);
    //   });
    //   setLabels($('#ex2').attr("data-value").split(","));
});
