$(document).ready(function(){

    // submit user preference then get and load new product
    function submitPreference(preferenceValue){
        $.ajax({
            method: 'POST',
            url: '/next_prefer',
            data: {
                product_id: $('#product-id').text(),
                preference: preferenceValue
            },
            cache: false,
            success: function(newProduct){
                $('#product-id').text(newProduct.product_id)
                $('#product-name').text(newProduct.product_name)
                $('#product-img').attr("src", newProduct.product_image)
                $("#product-container").animate({'right':'0px'}, 0).animate({'opacity': '1.0'}, 100) // reset image position
            }
        })
    }

    // wrapper function for case where user clicks button
    function submitPreferenceClick(event){
        submitPreference($(event.target).text())
    }

    // wrapper function for case where user swipes
    function submitPreferenceSwipe(event){
        if (event.type == 'swiperight'){
            submitPreference('Like')
        }
        else if (event.type == 'swipeleft'){
            submitPreference('Dislike')
        }
    }


    // on click, do the appropriate swipe animation, then call the ajax function
    $('.preference-button').click(function(event) {
        if ($(this).text() == 'Like'){
            $("#product-container").animate({'right':'-500px', 'opacity': '0.0'}, 500,'swing',
                                    function(){submitPreferenceClick(event)})
        }
        else if ($(this).text() == 'Dislike'){
            $("#product-container").animate({'right':'500px', 'opacity': '0.0'}, 500,'swing',
                                    function(){submitPreferenceClick(event)})
        }
    })

    // on swipe, do the appropriate swipe animation, then call the ajax function
    $('#product-img').on('dragstart', function(event) {event.preventDefault()}) // prevent browser from dragging image

    $('#product-img').on('swiperight', function(event) {
        $("#product-container").animate({'right':'-500px', 'opacity': '0.0'}, 500,'swing', function(){submitPreferenceSwipe(event)})
    })

        $('#product-img').on('swipeleft', function(event) {
        $("#product-container").animate({'right':'500px', 'opacity': '0.0'}, 500,'swing', function(){submitPreferenceSwipe(event)})
    })

})
