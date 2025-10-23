// https://www.geeksforgeeks.org/bootstrap/how-to-create-multi-step-progress-bar-using-bootstrap/?utm_source=chatgpt.com
$(document).ready(function () {
    var currentGfgStep, nextGfgStep, previousGfgStep;
    var opacity;
    var current = 1;
    

    setProgressBar(current);
    

    $(".next-step").click(function () {
        console.log('Next-step clicked')
        currentGfgStep = $(this).parent();
        nextGfgStep = $(this).parent().next();

        $("#progressbar li").eq($(".step-tab").index(nextGfgStep)).addClass("active");

        // nextGfgStep.show();
        currentGfgStep.animate({ opacity: 0 }, {
            step: function (now) {
                opacity = 1 - now;

                currentGfgStep.css({
                    'display': 'none',
                    'position': 'relative'
                });
                nextGfgStep.css({ 'opacity': opacity });
            },
            duration: 500
        });
        setProgressBar(++current);
    });

    $(".previous-step").click(function () {

        currentGfgStep = $(this).parent();
        previousGfgStep = $(this).parent().prev();

        $("#progressbar li").eq($(".step-tab").index(currentGfgStep)).removeClass("active");

        // previousGfgStep.show();

        currentGfgStep.animate({ opacity: 0 }, {
            step: function (now) {
                opacity = 1 - now;

                currentGfgStep.css({
                    'display': 'none',
                    'position': 'relative'
                });
                previousGfgStep.css({ 'opacity': opacity });
            },
            duration: 500
        });
        setProgressBar(--current);
    });

    function setProgressBar(current) {
        console.log('setProgressBar', current);
        const steps = $(".step-list-item").length;
        let percent = parseFloat(100 / steps) * current;
        percent = percent.toFixed();
        $(".progress-bar")
            .css("width", percent + "%")
    }

   
});



// $(function () {
//   const $steps = $(".step-list-item");
//   const $progressbar = $("#progressbar li");

//   function showStep(index) {
//     $steps.hide().eq(index).fadeIn();
//     $progressbar.removeClass("active").slice(0, index + 1).addClass("active");
//     $(".progress-bar").css("width", ((index + 1) / $steps.length * 100) + "%");
//   }

//   $steps.hide().first().show(); // Show first step
//   showStep(0);

//   $(document).on("click", ".next-step", function () {
//     const currentIndex = $steps.index($steps.filter(":visible"));
//     if (currentIndex < $steps.length - 1) showStep(currentIndex + 1);
//   });

//   $(document).on("click", ".previous-step", function () {
//     const currentIndex = $steps.index($steps.filter(":visible"));
//     if (currentIndex > 0) showStep(currentIndex - 1);
//   });
// });
