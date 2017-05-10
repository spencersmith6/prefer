// adjust swipe settings
$(document).bind("mobileinit", function () {
            $.event.special.swipe.horizontalDistanceThreshold = 100;
        });

// submit user preference then get and load new product
$(document).ready(function(){

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
                $('#link_button').attr("href", newProduct.product_link)
                // wait until image is loaded, then reset image position
                $('#product-img').load(function() {$("#product-container").animate({'right':'0px'}, 0).animate({'opacity': '1.0'}, 100 ) })
                $('#product-img').attr("src", newProduct.product_image)

            }
        })
    }

    // wrapper function for case where user clicks button
    function submitPreferenceClick(event){
        submitPreference($(event.target).text())
    }

    // on click, do the appropriate swipe animation, then call the ajax function
    $('.preference-button').click(function(event) {
        if (this.id == 'like-button'){
            $("#product-container").animate({'right':'-500px', 'opacity': '0.0'}, 500,'swing',
                                    function(){submitPreferenceClick(event)})
        }
        else if (this.id == 'dislike-button'){
            $("#product-container").animate({'right':'500px', 'opacity': '0.0'}, 500,'swing',
                                    function(){submitPreferenceClick(event)})
        }
    })

    // on swipe, do the appropriate swipe animation, then call the ajax function
    $('#product-img').on('dragstart', function(event) {event.preventDefault()}) // prevent browser from dragging image

    $('#product-img').on('swiperight', function(event) {
        $("#product-container").animate({'right':'-500px', 'opacity': '0.0'}, 500,'swing', function(){submitPreference('Like')})
    })

    $('#product-img').on('swipeleft', function(event) {
        $("#product-container").animate({'right':'500px', 'opacity': '0.0'}, 500,'swing', function(){submitPreference('Dislike')})
    })

})
