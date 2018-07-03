(function () {
    var init = function (button, menu) {

        var body = document.body,
            button = document.querySelector(button),
            menu = document.querySelector(menu),
            supportClipPath = (function () {
                var s = document.createElement('span'),
                    ss = s.style,
                    circle = 'circle(1px at 1px 1px)',
                    support;
                ss.position = "fixed";
                ss.top = ss.left = "-20px";
                body.appendChild(s);
                support = ["webkitClipPath", "clipPath"].some(function (p) {
                    return ((ss[p] = circle) && (getComputedStyle(s)[p] === circle));
                });
                body.removeChild(s);
                return support;
            })(),
            buildRect = function (box) {
                return 'rect(' + box.top + 'px,' + box.right + 'px,' + box.bottom + 'px,' + box.left + 'px)';
            };

        var bodyClip = buildRect(body.getBoundingClientRect()),
            buttonClip = buildRect(button.getBoundingClientRect());

        if (!supportClipPath) {
            menu.style.clip = buttonClip;
        }

        button.addEventListener("click", function (evt) {
            evt.preventDefault();
            menu.classList.toggle('nav-active');
            if (!supportClipPath) {
                menu.style.clip = menu.classList.contains('nav-active') ? bodyClip : buttonClip;
            }
        }, false);
    }

    init('[nav-reveal-button]', '[nav-reveal-menu]');

    window.navCircleReveal = init;

})();


$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
});


$(document).ready(function () {
    //Initialize tooltips
    $('.nav-tabs > li a[title]').tooltip();

    //Wizard
    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {

        var $target = $(e.target);

        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });

    // $(".next-step").click(function () {
    //     var valid = $("#id_table_form ").valid();
    //     if (!valid) {
    //         return false;
    //     }
    //     else {
    //         $('.step-indicator li.active').addClass('completed');
    //         var $active = $('.wizard .nav-tabs li.active');
    //         $active.next().removeClass('disabled');
    //         nextTab($active);
    //     }
    // });



    //Wizard
    // $tab_toggle.on('show.bs.tab', function(e) {
    //     var $target = $(e.target);

    //     if (!$target.parent().hasClass('active, disabled')) {
    //         $target.parent().prev().addClass('completed');
    //     }
    //     if ($target.parent().hasClass('disabled')) {
    //         return false;
    //     }
    // });


    //End of Doc Ready
});

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}

function prevTab(elem) {
    element = $(elem).prev().find('a[data-toggle="tab"]')
    element.click();
}